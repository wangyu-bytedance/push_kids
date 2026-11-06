from __future__ import annotations

import asyncio
from time import monotonic

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    ExistingKnowledgeContext,
    analysis_failure_disposition,
)
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.stage_contracts import (
    EXTRACT_INSTRUCTIONS,
    MATCH_INSTRUCTIONS,
    MERGE_INSTRUCTIONS,
    PIPELINE_REVISION,
    MatchDecision,
    MatchingResult,
    MergedPoint,
    QualityIssue,
    QualityReviewResult,
)
from push_kids.agent_processing.telemetry import AnalysisTrace

from tests.staged_analysis_fakes import StageFake, audited_consolidation


def run_case(provider, data, seconds=10, search=None):
    return asyncio.run(
        StagedPipeline(provider, AnalysisTrace.disabled()).run(
            data,
            search or (lambda request: []),
            monotonic() + seconds,
        )
    )


@pytest.mark.parametrize("count", [0, 1, 3, 6, 9])
def test_material_coverage_and_concurrency(tmp_path, count):
    images = []
    for i in range(count):
        p = tmp_path / f"{i}.png"
        p.write_bytes(f"synthetic-{i}".encode())
        images.append(p)
    provider = StageFake()
    queries = []
    result = run_case(
        provider,
        AnalysisInput(
            image_paths=images,
            text=None if count else "十以内加法",
            existing_subjects=["数学"],
        ),
        search=lambda r: queries.append(r) or [],
    )
    assert provider.max_active <= 2
    assert len(result.knowledge_points) == 1
    evidence = result.knowledge_points[0].direct_evidence
    assert {e.image_index for e in evidence} == (set(range(1, count + 1)) if count else {None})
    assert len(queries) == 1 and queries[0].candidate_key == "十以内加法"
    assert result.knowledge_points[0].context_used == []


def test_staged_prompt_requires_reusable_knowledge_and_independent_review():
    from push_kids.agent_processing.stage_contracts import (
        KNOWLEDGE_EXAMPLES,
        KNOWLEDGE_RULES,
        REUSE_INSTRUCTIONS,
        REVIEW_INSTRUCTIONS,
    )

    assert PIPELINE_REVISION == "staged-20261101-13"
    for instructions in (
        EXTRACT_INSTRUCTIONS,
        MERGE_INSTRUCTIONS,
        REVIEW_INSTRUCTIONS,
        MATCH_INSTRUCTIONS,
        REUSE_INSTRUCTIONS,
    ):
        assert instructions.count(KNOWLEDGE_RULES) == 1
        assert instructions.endswith(KNOWLEDGE_EXAMPLES)


def test_quality_review_runs_before_history_search():
    provider = StageFake()
    observed = []
    result = run_case(
        provider,
        AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
        search=lambda request: observed.append(provider.calls.copy()) or [],
    )
    assert result.knowledge_points
    assert provider.calls["review", "review"] == 1
    assert observed and observed[0]["review", "review"] == 1


def test_quality_review_can_request_one_merge_correction():
    provider = StageFake(review_failures=1)
    result = run_case(provider, AnalysisInput(text="十以内加法", existing_subjects=["数学"]))
    assert result.knowledge_points
    assert provider.review_calls == 2
    assert provider.calls["merge", "merge"] == 2


def test_all_quality_stages_receive_original_sources_and_complete_proposal(tmp_path):
    class ObservedStages(StageFake):
        def __init__(self):
            super().__init__(review_failures=1)
            self.observed = []

        async def generate_stage(self, stage, instructions, payload, schema, images, *args):
            if stage in {"merge", "review"}:
                self.observed.append((stage, payload, [(a, p.read_bytes()) for a, p in images]))
            return await super().generate_stage(stage, instructions, payload, schema, images, *args)

    image = tmp_path / "page.png"
    image.write_bytes(b"original source bytes")
    text = "家长明确提交的原文字"
    provider = ObservedStages()
    run_case(provider, AnalysisInput(image_paths=[image], text=text, existing_subjects=["数学"]))
    assert [s for s, _, _ in provider.observed] == ["merge", "review", "merge", "review"]
    for stage, payload, images in provider.observed:
        assert images == [("m1", b"original source bytes")]
        assert payload["parent_text"] == text
        assert set(payload["materials"]) == {"m1", "t"}
        assert "数学" in payload["subjects"]
        assert set(payload["excerpts"]) == {"m1", "t"}
        if stage == "review":
            assert payload["summary"] == "练习十以内加法"
            assert payload["uncertainties"] == []


@pytest.mark.parametrize("empty_candidates", [False, True])
def test_final_evidence_and_subject_come_from_audited_source_not_candidate(empty_candidates):
    from pydantic import BaseModel

    class AuditedMerge(BaseModel):
        summary: str
        items: list[dict]
        omissions: list[dict]
        uncertainties: list[str]
        evidence: list[dict]
        source_checks: list[dict]

    class SourceCorrection(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                if empty_candidates:
                    value.status, value.items = "non_learning", []
                else:
                    value.items[0].evidence = "未经核验的数学误读"
            if stage == "merge":
                item = value.items[0].model_dump()
                item.update(
                    members=list(payload["candidates"]),
                    subject="英语",
                    name="英语字母Tt的认读",
                    category="字母",
                    display_kind="word",
                    review_method="主动回忆",
                    evidence_keys=["e0"],
                    confidence="medium",
                )
                return AuditedMerge(
                    summary="认读英语字母Tt",
                    items=[item],
                    omissions=[],
                    uncertainties=["字母笔画需家长核对"],
                    evidence=[{"key": "e0", "material": "t", "detail": "原文字明确给出字母Tt"}],
                    source_checks=[
                        {
                            "material": "t",
                            "disposition": "covered",
                            "item_aliases": ["i0"],
                            "basis": "明确字母对象",
                        }
                    ],
                )
            if stage == "review":
                self.audited = payload
            if stage == "match":
                self.match_payload = payload
            return value

    provider = SourceCorrection()
    result = run_case(
        provider, AnalysisInput(text="英语字母Tt", existing_subjects=["数学", "英语"])
    )
    point = result.knowledge_points[0]
    assert (point.subject_name, point.name, point.confidence) == (
        "英语",
        "英语字母Tt的认读",
        "medium",
    )
    assert [e.detail for e in point.direct_evidence] == ["原文字明确给出字母Tt"]
    assert provider.audited["evidence"][0]["key"] == "e0"
    assert (
        provider.match_payload["candidates"][0]["direct_evidence"][0]["detail"]
        == "原文字明确给出字母Tt"
    )


@pytest.mark.parametrize("cached", [False, True])
def test_consolidated_byte_budget_applies_without_and_with_checkpoints(cached):
    class LargeResult(StageFake):
        async def generate_stage(self, stage, *args, **kwargs):
            value = await super().generate_stage(stage, *args, **kwargs)
            if stage == "merge":
                value.uncertainties = ["界" * 23000]
            return value

    class Store:
        def get(self, *args):
            return None

        def put(self, unit, digest, value, **kwargs):
            assert unit != "merge"

    pipeline = StagedPipeline(LargeResult(), AnalysisTrace.disabled(), Store() if cached else None)
    with pytest.raises(StageFailure) as caught:
        asyncio.run(
            pipeline.run(
                AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
                lambda _: [],
                monotonic() + 10,
            )
        )
    assert caught.value.diagnostics == ("stage.fields:byte_limit",)
    assert caught.value.stage == "merge"


def test_changed_source_bytes_are_rejected_before_proposal(tmp_path):
    class ChangedSource(StageFake):
        async def generate_stage(self, stage, instructions, payload, schema, images, *args):
            value = await super().generate_stage(
                stage, instructions, payload, schema, images, *args
            )
            if stage == "review":
                images[0][1].write_bytes(b"changed original")
            return value

    image = tmp_path / "page.png"
    image.write_bytes(b"original")
    with pytest.raises(StageFailure) as caught:
        run_case(ChangedSource(), AnalysisInput(image_paths=[image], existing_subjects=["数学"]))
    assert caught.value.reason == "input"
    assert caught.value.retryable is False


@pytest.mark.parametrize(
    "invalid",
    [
        "foreign_material",
        "duplicate_evidence",
        "evidence_alias",
        "blank_detail",
        "missing_reference",
        "duplicate_reference",
        "no_reference",
        "missing_check",
        "duplicate_check",
        "foreign_check",
        "wrong_item_alias",
        "non_learning_with_items",
        "blank_check_basis",
        "foreign_subject",
    ],
)
def test_audited_directory_and_source_ledger_reject_invalid_references(invalid):
    class InvalidDirectory(StageFake):
        async def generate_stage(self, stage, *args, **kwargs):
            value = await super().generate_stage(stage, *args, **kwargs)
            if stage == "merge":
                if invalid == "foreign_material":
                    value.evidence[0].material = "m9"
                elif invalid == "duplicate_evidence":
                    value.evidence.append(value.evidence[0])
                elif invalid == "evidence_alias":
                    value.evidence[0].key = "e40"
                elif invalid == "blank_detail":
                    value.evidence[0].detail = " "
                elif invalid == "missing_reference":
                    value.items[0].evidence_keys = ["e39"]
                elif invalid == "duplicate_reference":
                    value.items[0].evidence_keys *= 2
                elif invalid == "no_reference":
                    value.items[0].evidence_keys = []
                elif invalid == "missing_check":
                    value.source_checks = []
                elif invalid == "duplicate_check":
                    value.source_checks *= 2
                elif invalid == "foreign_check":
                    value.source_checks[0].material = "m9"
                elif invalid == "wrong_item_alias":
                    value.source_checks[0].item_aliases = ["i9"]
                elif invalid == "non_learning_with_items":
                    value.source_checks[0].disposition = "non_learning"
                elif invalid == "blank_check_basis":
                    value.source_checks[0].basis = " "
                else:
                    value.items[0].subject = "未知学科"
            return value

    provider = InvalidDirectory()
    with pytest.raises(StageFailure) as caught:
        run_case(provider, AnalysisInput(text="十以内加法", existing_subjects=["数学"]))
    assert caught.value.reason in {"validation", "coverage"}
    assert provider.review_calls == 0


@pytest.mark.parametrize(
    "code,aliases",
    [
        ("should_merge", ["i0"]),
        ("should_merge", ["q", "i0"]),
        ("should_merge", ["t", "i0"]),
        ("over_merged", ["t"]),
    ],
)
def test_granularity_issues_require_real_item_targets(code, aliases):
    class InvalidIssue(StageFake):
        async def generate_stage(self, stage, *args, **kwargs):
            value = await super().generate_stage(stage, *args, **kwargs)
            if stage == "review":
                value = QualityReviewResult(
                    passed=False,
                    issues=[QualityIssue(code=code, items=aliases, basis="合成范围问题")],
                )
            return value

    with pytest.raises(StageFailure) as caught:
        run_case(InvalidIssue(), AnalysisInput(text="十以内加法", existing_subjects=["数学"]))
    assert caught.value.reason == "validation" and caught.value.stage == "review"


def test_quality_review_rejects_after_one_failed_correction():
    provider = StageFake(review_failures=2)
    searched = []
    with pytest.raises(StageFailure, match="quality"):
        run_case(
            provider,
            AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
            search=lambda request: searched.append(request) or [],
        )
    assert provider.review_calls == 2
    assert not searched
    disposition = analysis_failure_disposition(StageFailure("quality"))
    assert (disposition.retryable, disposition.code) == (True, "analysis_output_invalid")


@pytest.mark.parametrize("invalid", ["pass_with_issue", "unknown_alias"])
def test_quality_review_rejects_invalid_contract(invalid):
    class InvalidReview(StageFake):
        async def generate_stage(self, stage, *args, **kwargs):
            if stage == "review":
                self.review_calls += 1
                issue = QualityIssue(
                    code="vague_name",
                    items=["i999" if invalid == "unknown_alias" else "i0"],
                    basis="名称缺少具体范围",
                )
                return QualityReviewResult(passed=invalid == "pass_with_issue", issues=[issue])
            return await super().generate_stage(stage, *args, **kwargs)

    provider = InvalidReview()
    with pytest.raises(StageFailure, match="validation"):
        run_case(provider, AnalysisInput(text="十以内加法", existing_subjects=["数学"]))
    assert provider.review_calls == 1


def test_identical_images_retain_original_first_source(tmp_path):
    paths = [tmp_path / f"{i}.png" for i in range(3)]
    for path in paths:
        path.write_bytes(b"identical synthetic")
    provider = StageFake()
    result = run_case(provider, AnalysisInput(image_paths=paths, existing_subjects=["数学"]))
    assert sum(n for (s, _), n in provider.calls.items() if s == "extract") == 1
    assert result.knowledge_points[0].direct_evidence[0].image_index == 1


@pytest.mark.parametrize("broken", ["source", "coverage", "reference", "summary", "uncertain"])
def test_rejects_foreign_source_missing_member_and_invented_reference(broken):
    with pytest.raises(StageFailure) as exc:
        run_case(
            StageFake(broken=broken), AnalysisInput(text="十以内加法", existing_subjects=["数学"])
        )
    assert exc.value.reason in {"validation", "coverage"}


def test_a_failed_material_does_not_publish_a_partial_result(tmp_path):
    paths = [tmp_path / f"{i}.png" for i in range(2)]
    for i, path in enumerate(paths):
        path.write_bytes(str(i).encode())
    provider = StageFake(fail_unit="m2")
    with pytest.raises(StageFailure, match="provider_timeout"):
        run_case(provider, AnalysisInput(image_paths=paths, existing_subjects=["数学"]))
    assert provider.calls["merge", "merge"] == 0


def test_deadline_does_not_start_a_provider_call():
    provider = StageFake()
    with pytest.raises(StageFailure, match="local_deadline"):
        run_case(provider, AnalysisInput(text="十以内加法", existing_subjects=["数学"]), seconds=-1)
    assert not provider.calls


def test_single_material_schema_failure_has_one_local_correction(tmp_path):
    class RecoveringMaterial(StageFake):
        def __init__(self):
            super().__init__()
            self.inputs = []

        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "extract":
                self.inputs.append(payload)
                if len(self.inputs) == 1:
                    raise StageFailure("validation")
            return await super().generate_stage(stage, instructions, payload, *args)

    image = tmp_path / "page.png"
    image.write_bytes(b"synthetic page with an oversized model name")
    provider = RecoveringMaterial()
    result = run_case(provider, AnalysisInput(image_paths=[image], existing_subjects=["数学"]))
    assert len(result.knowledge_points) == 1
    assert len(provider.inputs) == 2
    assert provider.inputs[1]["materials"] == ["m1"]
    assert "correction" in provider.inputs[1]
    assert result.knowledge_points[0].direct_evidence[0].image_index == 1


def test_pipeline_leaves_request_queue_budget_to_provider(monkeypatch):
    class QueuedRequest(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            deadline = args[2]
            self.deadline = deadline
            if deadline - 25 < 10:
                raise StageFailure("local_deadline")
            return MatchingResult(
                decisions=[MatchDecision(candidate="i0", match=None, uncertain=False)]
            )

    provider = QueuedRequest()
    monkeypatch.setattr("push_kids.agent_processing.pipeline.monotonic", lambda: 0)
    pipeline = StagedPipeline(provider, AnalysisTrace.disabled())
    result = asyncio.run(
        pipeline._call(
            "match", "match", "instructions", {}, MatchingResult, [], 270, lambda _: None
        )
    )
    assert result.decisions[0].match is None
    assert provider.deadline == 270


def test_unsupported_candidate_is_accounted_for_in_reviewed_omissions():
    from push_kids.agent_processing.stage_contracts import (
        ExtractedPoint,
        MaterialResult,
        OmittedCandidates,
    )

    class OmissionProvider(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "extract":
                return MaterialResult(
                    status="content",
                    needs_context=False,
                    excerpt="",
                    items=[
                        ExtractedPoint(
                            subject="数学",
                            name="十以内加法",
                            evidence="两组数量求总数",
                            materials=["t"],
                            confidence="high",
                        ),
                        ExtractedPoint(
                            subject="英语",
                            name="界面操作标题",
                            evidence="仅为页面操作标题",
                            materials=["t"],
                            confidence="high",
                        ),
                    ],
                )
            if stage == "merge":
                return audited_consolidation(
                    payload,
                    summary="整理十以内加法",
                    uncertainties=[],
                    items=[
                        MergedPoint(
                            members=["c1"],
                            subject="数学",
                            name="十以内加法",
                            category="计算",
                            display_kind="arithmetic",
                            review_method="变式练习",
                            estimated_minutes=2,
                            evidence_keys=["e0"],
                            confidence="high",
                        )
                    ],
                    omissions=[
                        OmittedCandidates(
                            members=["c2"],
                            reason="no_learning_evidence",
                            basis="页面操作标题没有英语教学证据",
                        )
                    ],
                )
            if stage == "review":
                self.reviewed_omissions = payload.get("final_omissions", {})
            return await super().generate_stage(stage, instructions, payload, *args)

    provider = OmissionProvider()
    queried = []
    result = run_case(
        provider,
        AnalysisInput(text="数学教学与界面标题", existing_subjects=["数学", "英语"]),
        search=lambda r: queried.append(r) or [],
    )
    assert [point.name for point in result.knowledge_points] == ["十以内加法"]
    assert provider.reviewed_omissions["o0"]["members"] == ["c2"]
    assert len(queried) == 1 and queried[0].subject_name == "数学"


def test_quality_correction_uses_review_alias_and_keeps_unaffected_item():
    class AliasCorrection(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "merge" and "review_issues" in payload:
                previous = payload.get("previous_items", {})
                assert previous.get("i0", {}).get("members") == ["c1"]
                assert payload["review_issues"][0]["items"] == ["i0"]
            return await super().generate_stage(stage, instructions, payload, *args)

    result = run_case(
        AliasCorrection(review_failures=1),
        AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
    )
    assert result.knowledge_points[0].name == "十以内加法"


def test_blocking_history_does_not_delay_loop_shutdown():
    import time

    started = monotonic()
    with pytest.raises(StageFailure, match="local_deadline"):
        run_case(
            StageFake(),
            AnalysisInput(text="加法", existing_subjects=["数学"]),
            seconds=0.08,
            search=lambda _: time.sleep(0.5) or [],
        )
    assert monotonic() - started < 0.3


@pytest.mark.parametrize(
    "reason,retryable,code",
    [
        ("provider_timeout", True, "analysis_failed"),
        ("rate_limited", True, "analysis_failed"),
        ("auth", False, "analysis_failed"),
        ("config", False, "analysis_failed"),
        ("validation", True, "analysis_output_invalid"),
        ("quality", True, "analysis_output_invalid"),
    ],
)
def test_safe_failure_dispositions(reason, retryable, code):
    failure = StageFailure(reason, retryable=retryable)
    disposition = analysis_failure_disposition(failure)
    assert (disposition.retryable, disposition.code, disposition.reason) == (
        retryable,
        code,
        reason,
    )


def test_cross_page_group_is_bounded_and_preserves_evidence(tmp_path):
    paths = [tmp_path / f"{i}.png" for i in range(2)]
    for i, path in enumerate(paths):
        path.write_bytes(str(i).encode())
    provider = StageFake(needs_context=True)
    result = run_case(provider, AnalysisInput(image_paths=paths, existing_subjects=["数学"]))
    assert provider.calls["group", "m1"] == 1
    assert {e.image_index for e in result.knowledge_points[0].direct_evidence} == {1, 2}


@pytest.mark.parametrize("source", ["text", "photo"])
@pytest.mark.parametrize("empty_candidates", [False, True])
def test_single_source_context_gap_is_audited_without_discarding_supported_goal(
    tmp_path, source, empty_candidates
):
    class IncompleteSource(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.needs_context = True
                value.excerpt = "已明确加法关系，部分例题未提供"
                if empty_candidates:
                    value.items = []
            if stage in {"merge", "review"}:
                self.audited_sources.append(payload)
            return value

    provider = IncompleteSource()
    provider.audited_sources = []
    path = tmp_path / "single.png"
    path.write_bytes(b"synthetic-single-source")
    data = AnalysisInput(
        text="练习十以内加法，例题未提供" if source == "text" else None,
        image_paths=[path] if source == "photo" else [],
        existing_subjects=["数学"],
    )
    queries = []
    result = run_case(provider, data, search=lambda r: queries.append(r) or [])

    assert [p.name for p in result.knowledge_points] == ["十以内加法"]
    assert len(queries) == 1
    assert sum(n for (stage, _), n in provider.calls.items() if stage == "group") == 0
    assert len(provider.audited_sources) == 2
    alias = "t" if source == "text" else "m1"
    for payload in provider.audited_sources:
        assert payload["unresolved_materials"] == [alias]
        assert payload["excerpts"][alias] == "已明确加法关系，部分例题未提供"
    evidence = result.knowledge_points[0].direct_evidence
    assert {(e.source, e.image_index) for e in evidence} == {
        ("parent_text", None) if source == "text" else ("image", 1)
    }


def test_unreadable_single_source_is_not_recovered_as_a_context_gap(tmp_path):
    class UnreadableSource(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.status, value.items, value.needs_context = "unreadable", [], False
            return value

    path = tmp_path / "unreadable.png"
    path.write_bytes(b"synthetic-unreadable-source")
    provider = UnreadableSource()
    queries = []
    with pytest.raises(StageFailure, match="unreadable"):
        run_case(
            provider,
            AnalysisInput(image_paths=[path], existing_subjects=["数学"]),
            search=lambda r: queries.append(r) or [],
        )
    assert not queries
    assert not any(stage in {"merge", "review"} for stage, _ in provider.calls)


def test_duplicate_merge_groups_are_rejected_before_source_loss(tmp_path):
    class DuplicateMerge(StageFake):
        async def generate_stage(self, stage, *args, **kwargs):
            value = await super().generate_stage(stage, *args, **kwargs)
            if stage == "merge":
                original = value.items[0]
                value.items = [
                    original.model_copy(update={"members": [member]}) for member in original.members
                ]
            return value

    paths = [tmp_path / "one.png", tmp_path / "two.png"]
    for i, path in enumerate(paths):
        path.write_bytes(str(i).encode())
    with pytest.raises(StageFailure, match="validation"):
        run_case(DuplicateMerge(), AnalysisInput(image_paths=paths, existing_subjects=["数学"]))


def test_cross_page_unknown_first_page_can_be_completed(tmp_path):
    class UnknownFirstPage(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract" and payload["materials"] == ["m1"]:
                value.items = []
                value.needs_context = True
            if stage == "group":
                value.items[0].materials = ["m1", "m2"]
            return value

    paths = [tmp_path / "one.png", tmp_path / "two.png"]
    for i, path in enumerate(paths):
        path.write_bytes(str(i).encode())
    result = run_case(
        UnknownFirstPage(), AnalysisInput(image_paths=paths, existing_subjects=["数学"])
    )
    assert {e.image_index for e in result.knowledge_points[0].direct_evidence} == {1, 2}


def test_group_cannot_discard_an_unresolved_page(tmp_path):
    class MissingPage(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract" and payload["materials"] == ["m1"]:
                value.items = []
                value.needs_context = True
            if stage == "group":
                value.items[0].materials = ["m2"]
            return value

    paths = [tmp_path / "one.png", tmp_path / "two.png"]
    for i, path in enumerate(paths):
        path.write_bytes(str(i).encode())
    with pytest.raises(StageFailure, match="coverage"):
        run_case(MissingPage(), AnalysisInput(image_paths=paths, existing_subjects=["数学"]))


def test_explicit_same_day_review_resolves_scoped_identity_after_term_miss():
    from push_kids.agent_processing.contracts import (
        ExistingKnowledgeContext,
        SameDayKnowledgeContext,
    )

    data = AnalysisInput(
        text="今天再次复习十以内加法",
        existing_subjects=["数学"],
        same_day_learning=[
            SameDayKnowledgeContext(
                knowledge_id="known", subject_name="数学", name="十以内加法", category="计算"
            )
        ],
    )
    queries = []

    def search(request):
        queries.append(request)
        if request.knowledge_id:
            assert request.knowledge_id == "known"
            data.existing_knowledge.append(
                ExistingKnowledgeContext(
                    knowledge_id="known", subject_name="数学", name="十以内加法", category="计算"
                )
            )
        return []

    result = run_case(StageFake(), data, search=search)
    assert len(queries) == 2 and len(result.todo_matches) == 1
    assert result.todo_matches[0].knowledge_id == "known"


def test_semantically_equivalent_candidates_collapse_to_one_historical_identity(tmp_path):
    class EquivalentHistory(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.items[0].name = (
                    "上下车情境中的加减混合运算"
                    if payload["materials"] == ["m1"]
                    else "加减法混合运算应用题"
                )
                value.items[0].evidence = value.items[0].name
            elif stage == "merge":
                value = audited_consolidation(
                    payload,
                    summary="练习加减法混合运算应用题",
                    uncertainties=[],
                    omissions=[],
                    items=[
                        MergedPoint(
                            members=[candidate],
                            subject="数学",
                            name=point["name"],
                            category="应用题",
                            display_kind="arithmetic",
                            review_method="变式练习",
                            estimated_minutes=3,
                            evidence_keys=["e0"],
                            confidence="high",
                        )
                        for candidate, point in payload["candidates"].items()
                    ],
                )
            elif stage == "match":
                value = MatchingResult(
                    decisions=[
                        MatchDecision(candidate=row["candidate"], match="h0", uncertain=False)
                        for row in payload["candidates"]
                    ]
                )
            return value

    paths = [tmp_path / "one.png", tmp_path / "two.png"]
    for index, path in enumerate(paths):
        path.write_bytes(str(index).encode())
    result = run_case(
        EquivalentHistory(),
        AnalysisInput(
            image_paths=paths,
            existing_subjects=["数学"],
            existing_knowledge=[
                ExistingKnowledgeContext(
                    knowledge_id="known",
                    review_id="review",
                    subject_name="数学",
                    name="加减法混合运算应用题",
                    category="应用题",
                )
            ],
        ),
    )
    assert not result.knowledge_points
    assert len(result.todo_matches) == 1
    assert result.todo_matches[0].knowledge_id == "known"
    assert "上下车" in result.todo_matches[0].evidence
    assert "加减法混合运算应用题" in result.todo_matches[0].evidence
