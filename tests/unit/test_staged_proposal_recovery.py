"""Observable proposal outcomes and privacy boundaries for BUG-036."""

import asyncio
import json
from time import monotonic

import pytest
from push_kids.agent_processing.checkpoints import fingerprint
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    ExistingKnowledgeContext,
    SameDayKnowledgeContext,
    TodoCandidate,
)
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.stage_contracts import (
    ExtractedPoint,
    MatchDecision,
    MatchingResult,
    MaterialResult,
    MergedPoint,
    OmittedCandidates,
    QualityIssue,
    QualityReviewResult,
    ReuseDecision,
    ReuseReviewResult,
)
from push_kids.agent_processing.telemetry import AnalysisTrace

from tests.staged_analysis_fakes import MaximumStages, StageFake, audited_consolidation


def run(provider, data=None, search=None):
    return asyncio.run(
        StagedPipeline(provider, AnalysisTrace.disabled()).run(
            data or AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
            search or (lambda _: []),
            monotonic() + 10,
        )
    )


class HistoryReview(StageFake):
    def __init__(self, verdict="reject", *, choose=True, corrupt=None):
        super().__init__()
        self.verdict, self.choose, self.corrupt = verdict, choose, corrupt
        self.reuse_count = 0

    async def generate_stage(self, stage, instructions, payload, *args):
        if stage == "match":
            self.match_payload = payload
            decisions = []
            for row in payload["candidates"]:
                option = row["options"][0] if row["options"] and self.choose else None
                # The baseline replay uses the original option representation.
                alias = option["id"] if isinstance(option, dict) else option
                decisions.append(
                    MatchDecision(candidate=row["candidate"], match=alias, uncertain=False)
                )
            return MatchingResult(decisions=decisions)
        if stage == "reuse":
            self.reuse_count += 1
            self.reuse_payload = payload
            return ReuseReviewResult(
                decisions=[
                    ReuseDecision(
                        candidate="i99" if self.corrupt == "candidate" else row["candidate"],
                        match="h99" if self.corrupt == "match" else row["match"],
                        verdict=self.verdict,
                        basis=""
                        if self.verdict == "accept" or self.corrupt == "basis"
                        else "历史范围或复习技能不同，或旧名称不符合规则",
                    )
                    for row in payload["matches"]
                ]
            )
        return await super().generate_stage(stage, instructions, payload, *args)


def history_input(name="三十以内加法", method="变式练习", evidence="三十以内求和"):
    return AnalysisInput(
        text="十以内加法",
        existing_subjects=["数学"],
        existing_knowledge=[
            ExistingKnowledgeContext(
                knowledge_id="history-sentinel",
                subject_name="数学",
                name=name,
                category="计算",
                review_method=method,
                evidence=evidence,
            )
        ],
    )


@pytest.mark.parametrize("old_name", ["三十以内加法", "按图填空", "数的学习"])
def test_final_history_rejection_preserves_reviewed_scope(old_name):
    provider = HistoryReview("reject")
    result = run(provider, history_input(old_name))
    assert [p.name for p in result.knowledge_points] == ["十以内加法"]
    assert result.todo_matches == []
    assert provider.reuse_count == 1


def test_equal_history_is_reused_with_its_identity():
    provider = HistoryReview("accept")
    result = run(provider, history_input("十以内加法", evidence="十以内两个加数求和"))
    assert result.knowledge_points == []
    assert [m.knowledge_id for m in result.todo_matches] == ["history-sentinel"]
    assert provider.reuse_count == 1


def test_history_matching_receives_both_learning_skill_and_evidence():
    provider = HistoryReview("reject")
    run(provider, history_input(method="主动回忆", evidence="较宽运算范围的口述"))
    candidate = provider.match_payload["candidates"][0]
    assert candidate["review_method"] == "变式练习"
    assert candidate["direct_evidence"][0]["detail"] == "根据两组数量求总数"
    option = provider.match_payload["options"][candidate["options"][0]]
    assert option["review_method"] == "主动回忆"
    assert option["evidence"] == "较宽运算范围的口述"
    assert option["evidence_complete"] is True
    assert "history-sentinel" not in json.dumps(provider.match_payload)


def test_uncertain_reuse_never_falls_back_to_new():
    provider = HistoryReview("uncertain")
    with pytest.raises(StageFailure) as caught:
        run(provider, history_input())
    assert (caught.value.stage, caught.value.unit) == ("reuse", "reuse")
    assert caught.value.retryable is False
    assert provider.reuse_count == 1


@pytest.mark.parametrize("corrupt", ["candidate", "match", "basis"])
def test_reuse_contract_cannot_invent_or_omit_selected_identity(corrupt):
    provider = HistoryReview("reject", corrupt=corrupt)
    with pytest.raises(StageFailure) as caught:
        run(provider, history_input())
    assert caught.value.reason in {"coverage", "validation"}
    assert caught.value.stage == "reuse" and provider.reuse_count == 1


def test_same_name_does_not_override_a_null_match():
    provider = HistoryReview(choose=False)
    result = run(provider, history_input("十以内加法"))
    assert [p.name for p in result.knowledge_points] == ["十以内加法"]
    assert result.todo_matches == []
    assert provider.reuse_count == 0


def test_explicit_reject_with_same_name_preserves_reviewed_target():
    provider = HistoryReview("reject")
    result = run(provider, history_input("十以内加法", method="主动回忆", evidence="不同复习技能"))
    assert [p.name for p in result.knowledge_points] == ["十以内加法"]
    assert result.todo_matches == [] and provider.reuse_count == 1


def test_same_day_id_resolution_is_checked_before_name_substitution():
    provider = HistoryReview("reject")
    data = AnalysisInput(
        text="今天再次复习十以内加法",
        existing_subjects=["数学"],
        same_day_learning=[
            SameDayKnowledgeContext(
                knowledge_id="same-day-sentinel",
                subject_name="数学",
                name="10以内加法",
                category="计算",
            )
        ],
    )
    queried = []

    def search(request):
        queried.append(request)
        if request.knowledge_id:
            data.existing_knowledge.append(
                ExistingKnowledgeContext(
                    knowledge_id="same-day-sentinel",
                    subject_name="数学",
                    name="按图填空",
                    category="计算",
                    evidence="十以内加法",
                )
            )
        return []

    result = run(provider, data, search)
    assert len(queried) == 2
    assert provider.reuse_payload["matches"][0]["selected"]["name"] == "按图填空"
    assert [p.name for p in result.knowledge_points] == ["十以内加法"]
    assert result.todo_matches == []


class TwoTargets(StageFake):
    def __init__(self, *, drift=False, omit=False, all_omitted=False, invalid_members=False):
        super().__init__()
        self.drift, self.omit = drift, omit
        self.all_omitted, self.invalid_members = all_omitted, invalid_members
        self.merge_calls = 0

    async def generate_stage(self, stage, instructions, payload, *args):
        if stage == "extract":
            return MaterialResult(
                status="content",
                needs_context=False,
                excerpt="",
                items=[
                    ExtractedPoint(
                        subject="数学",
                        name=name,
                        evidence=name + "的规则",
                        materials=["t"],
                        confidence="high",
                    )
                    for name in ("十以内加法", "十以内减法")
                ],
            )
        if stage == "merge":
            self.merge_calls += 1
            items = [
                MergedPoint(
                    members=[alias],
                    subject=point["subject"],
                    name=point["name"],
                    category="计算",
                    display_kind="arithmetic",
                    review_method="变式练习",
                    estimated_minutes=2,
                    evidence_keys=["e0"],
                    confidence="high",
                )
                for alias, point in payload["candidates"].items()
            ]
            omissions = []
            if self.omit or self.all_omitted:
                omissions = [
                    OmittedCandidates(
                        members=["c1", "c2"] if self.all_omitted else ["c2"],
                        reason="indeterminate_object",
                        basis="示意性的错误省略理由",
                    )
                ]
                items = [] if self.all_omitted else items[:1]
            if self.invalid_members:
                omissions = [
                    OmittedCandidates(
                        members=["c1"], reason="no_learning_evidence", basis="重复成员"
                    )
                ]
            if self.drift and "review_issues" in payload:
                items[0].name = "一百以内加法"
            return audited_consolidation(
                payload, summary="整理加减法", items=items, omissions=omissions, uncertainties=[]
            )
        if stage == "review":
            self.review_calls += 1
            self.review_payload = payload
            if self.all_omitted:
                return QualityReviewResult(passed=True, issues=[])
            if self.omit or self.review_calls == 1:
                return QualityReviewResult(
                    passed=False,
                    issues=[
                        QualityIssue(
                            code="unsupported_by_evidence" if self.omit else "vague_name",
                            items=["o0"] if self.omit else ["i1"],
                            basis="省略了有直接学习证据的对象"
                            if self.omit
                            else "需修正第二项规则表达",
                        )
                    ],
                )
            return QualityReviewResult(passed=True, issues=[])
        return await super().generate_stage(stage, instructions, payload, *args)


def test_correction_rejects_changes_to_an_unaffected_target():
    provider = TwoTargets(drift=True)
    queried = []
    with pytest.raises(StageFailure) as caught:
        run(provider, search=lambda r: queried.append(r) or [])
    assert caught.value.stage == "merge" and caught.value.reason == "validation"
    assert queried == [] and provider.merge_calls == 3


class ScopedCorrection(TwoTargets):
    def __init__(self, *, target="q", drift=None):
        super().__init__()
        self.target, self.scope_drift = target, drift

    async def generate_stage(self, stage, instructions, payload, *args):
        if stage == "extract" and payload["materials"] != ["t"]:
            value = await StageFake.generate_stage(self, stage, instructions, payload, *args)
            value.items[0].name = "十以内加法" if payload["materials"] == ["m1"] else "十以内减法"
            return value
        value = await super().generate_stage(stage, instructions, payload, *args)
        if stage == "review" and self.review_calls == 1:
            value.issues[0].items = [self.target]
        if stage == "merge" and "review_issues" in payload:
            value.summary = "练习加减法规则"
            if self.scope_drift == "item":
                value.items[0].name = "一百以内加法"
            if self.scope_drift == "evidence":
                value.evidence[0].detail = "把已通过的来源改为未经核验的内容"
        return value


def test_metadata_correction_changes_only_summary_and_uncertainties():
    result = run(ScopedCorrection(target="q"))
    assert result.summary == "练习加减法规则"
    assert [p.name for p in result.knowledge_points] == ["十以内加法", "十以内减法"]


@pytest.mark.parametrize("target", ["q", "i1"])
@pytest.mark.parametrize("drift", ["item", "evidence"])
def test_correction_preserves_unaffected_items_and_evidence(target, drift):
    with pytest.raises(StageFailure) as caught:
        run(ScopedCorrection(target=target, drift=drift))
    assert caught.value.stage == "merge" and caught.value.reason == "validation"


@pytest.mark.parametrize("drift", [None, "item", "evidence"])
def test_material_issue_cannot_change_another_sources_target(tmp_path, drift):
    images = [tmp_path / "one.png", tmp_path / "two.png"]
    for index, path in enumerate(images):
        path.write_bytes(f"source-{index}".encode())
    data = AnalysisInput(image_paths=images, existing_subjects=["数学"])
    provider = ScopedCorrection(target="m2", drift=drift)
    if drift:
        with pytest.raises(StageFailure) as caught:
            run(provider, data)
        assert caught.value.reason == "validation" and caught.value.stage == "merge"
    else:
        assert len(run(provider, data).knowledge_points) == 2


@pytest.mark.parametrize("drift", [False, True])
def test_material_correction_uses_audited_source_after_candidate_attribution_changes(
    tmp_path, drift
):
    from push_kids.agent_processing.stage_contracts import ConsolidatedResult

    class CorrectedSource(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "extract":
                value = await super().generate_stage(stage, instructions, payload, *args)
                if payload["materials"] == ["m2"]:
                    value.items = []
                return value
            if stage == "merge":
                corrected = "review_issues" in payload
                return ConsolidatedResult.model_validate(
                    {
                        "summary": "练习十以内加法",
                        "uncertainties": [],
                        "omissions": [],
                        "items": [
                            {
                                "members": ["c1"],
                                "subject": "数学",
                                "name": "十以内减法" if corrected and drift else "十以内加法",
                                "category": "计算",
                                "display_kind": "arithmetic",
                                "review_method": "变式练习",
                                "estimated_minutes": 2,
                                "evidence_keys": ["e0"],
                                "confidence": "high",
                            }
                        ],
                        "evidence": [{"key": "e0", "material": "m2", "detail": "第二页的加法教学"}],
                        "source_checks": [
                            {
                                "material": "m1",
                                "disposition": "non_learning" if corrected else "indeterminate",
                                "item_aliases": [],
                                "basis": "页脚备注" if corrected else "待核对教学角色",
                            },
                            {
                                "material": "m2",
                                "disposition": "covered",
                                "item_aliases": ["i0"],
                                "basis": "第二页加法教学",
                            },
                        ],
                    }
                )
            if stage == "review":
                self.review_calls += 1
                return QualityReviewResult(
                    passed=self.review_calls > 1,
                    issues=[]
                    if self.review_calls > 1
                    else [
                        QualityIssue(
                            code="unsupported_by_evidence",
                            items=["m1"],
                            basis="第一页仅为备注",
                        )
                    ],
                )
            return await super().generate_stage(stage, instructions, payload, *args)

    images = [tmp_path / "one.png", tmp_path / "two.png"]
    for index, path in enumerate(images):
        path.write_bytes(f"source-{index}".encode())
    provider, queried = CorrectedSource(), []
    data = AnalysisInput(image_paths=images, existing_subjects=["数学"])
    if drift:
        with pytest.raises(StageFailure) as caught:
            run(provider, data, lambda request: queried.append(request) or [])
        assert caught.value.reason == "validation" and caught.value.stage == "merge"
        assert provider.review_calls == 1 and queried == []
    else:
        result = run(provider, data)
        assert [point.name for point in result.knowledge_points] == ["十以内加法"]
        assert result.knowledge_points[0].direct_evidence[0].image_index == 2
        assert provider.review_calls == 2


def test_final_review_has_previous_alias_members_and_issue_basis():
    provider = TwoTargets()
    result = run(provider)
    assert [p.name for p in result.knowledge_points] == ["十以内加法", "十以内减法"]
    previous = provider.review_payload["previous_review"]
    assert previous["previous_items"]["i1"]["members"] == ["c2"]
    assert previous["issues"][0]["basis"] == "需修正第二项规则表达"
    assert provider.review_calls == 2


def test_review_cannot_hide_supported_knowledge_in_omissions():
    provider = TwoTargets(omit=True)
    queried = []
    with pytest.raises(StageFailure, match="quality") as caught:
        run(provider, search=lambda r: queried.append(r) or [])
    assert caught.value.retryable is False
    assert provider.review_calls == 2 and queried == []
    assert provider.review_payload["final_omissions"]["o0"]["members"] == ["c2"]


def test_all_omitted_never_publishes_an_empty_proposal():
    provider = TwoTargets(all_omitted=True)
    queried = []
    with pytest.raises(StageFailure, match="coverage") as caught:
        run(provider, search=lambda r: queried.append(r) or [])
    assert caught.value.retryable is False
    assert (caught.value.stage, caught.value.unit) == ("review", "empty_proposal")
    assert provider.review_calls == 1 and queried == []


def test_candidate_cannot_be_both_published_and_omitted():
    provider = TwoTargets(invalid_members=True)
    with pytest.raises(StageFailure, match="coverage"):
        run(provider)
    assert provider.merge_calls == 2 and provider.review_calls == 0


def test_second_material_schema_failure_is_terminal_and_does_not_merge():
    class InvalidMaterial(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.items[0].name = "x" * 121
            return value

    provider = InvalidMaterial()
    with pytest.raises(StageFailure) as caught:
        run(provider)
    assert provider.calls["extract", "t"] == 2
    assert provider.calls["merge", "merge"] == 0
    assert caught.value.diagnostics == ("stage.items.0.name:string_too_long",)
    assert (caught.value.stage, caught.value.unit) == ("extract", "t")


def test_history_unique_result_limit_is_enforced_at_pipeline_boundary():
    data = AnalysisInput(text="十以内加法", existing_subjects=["数学"])

    def search(_):
        data.existing_knowledge.extend(
            ExistingKnowledgeContext(
                knowledge_id=str(index),
                subject_name="数学",
                name=f"历史{index}",
                category="计算",
            )
            for index in range(101)
        )
        return []

    with pytest.raises(StageFailure) as caught:
        run(StageFake(), data, search)
    assert caught.value.unit == "history_results" and caught.value.reason == "capacity"


def test_history_evidence_is_bounded_deduplicated_and_marked_incomplete():
    class TwentyTargets(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.items = [
                    value.items[0].model_copy(update={"name": f"目标{index}"})
                    for index in range(20)
                ]
            if stage == "merge":
                value.items = [
                    value.items[0].model_copy(update={"members": [alias], "name": point["name"]})
                    for alias, point in payload["candidates"].items()
                ]
                value = audited_consolidation(
                    payload,
                    **{
                        key: getattr(value, key)
                        for key in ("summary", "items", "omissions", "uncertainties")
                    },
                )
            if stage == "match":
                self.match_payload = payload
            return value

    data = AnalysisInput(
        text="多目标学习",
        existing_subjects=["数学"],
        existing_knowledge=[
            ExistingKnowledgeContext(
                knowledge_id=f"history-{index}",
                subject_name="数学",
                name=f"历史{index}",
                category="计算",
                evidence="字" * 4000,
            )
            for index in range(100)
        ],
    )
    provider = TwentyTargets()
    queried = []
    result = run(provider, data, lambda r: queried.append(r) or [])
    assert len(result.knowledge_points) == 20 and len(queried) == 20
    payload = provider.match_payload
    assert len(payload["options"]) == 100
    assert len(json.dumps(payload, ensure_ascii=False).encode()) <= 512 * 1024
    assert any(not row["evidence_complete"] for row in payload["options"].values())
    assert all(len(row["direct_evidence"]) == 1 for row in payload["candidates"])
    assert "history-99" not in json.dumps(payload)


def test_history_name_overflow_cannot_be_fixed_by_truncating_current_target():
    data = history_input(name="x" * (512 * 1024))
    with pytest.raises(StageFailure) as caught:
        run(StageFake(), data)
    assert caught.value.unit == "history_payload" and caught.value.reason == "capacity"


def test_valid_cross_subject_history_context_does_not_hit_a_new_global_option_cap():
    class CrossSubjectTargets(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.items.append(
                    value.items[0].model_copy(
                        update={
                            "subject": "英语",
                            "name": "英语词汇table、chair的认读",
                            "evidence": "table与chair词表",
                        }
                    )
                )
            if stage == "merge":
                value.items = [
                    value.items[0].model_copy(
                        update={
                            "members": [alias],
                            "subject": point["subject"],
                            "name": point["name"],
                        }
                    )
                    for alias, point in payload["candidates"].items()
                ]
                value = audited_consolidation(
                    payload,
                    **{
                        key: getattr(value, key)
                        for key in ("summary", "items", "omissions", "uncertainties")
                    },
                )
            if stage == "match":
                self.options_count = len(payload["options"])
                self.per_candidate = [len(row["options"]) for row in payload["candidates"]]
            return value

    data = AnalysisInput(
        text="数学与英语教学",
        existing_subjects=["数学", "英语"],
        same_day_learning=[
            SameDayKnowledgeContext(
                knowledge_id=f"same-{index}",
                subject_name="数学" if index < 100 else "英语",
                name=f"当天知识{index}",
                category="知识点",
            )
            for index in range(200)
        ],
        todo_candidates=[
            TodoCandidate(
                knowledge_id=f"today-{index}",
                review_id=f"review-{index}",
                subject_name="数学" if index < 60 else "英语",
                knowledge_name=f"计划知识{index}",
            )
            for index in range(120)
        ],
    )
    queried = []

    def search(request):
        queried.append(request)
        data.existing_knowledge.extend(
            ExistingKnowledgeContext(
                knowledge_id=f"history-{request.subject_name}-{index}",
                subject_name=request.subject_name,
                name=f"历史知识{index}",
                category="知识点",
            )
            for index in range(20)
        )
        return []

    provider = CrossSubjectTargets()
    result = run(provider, data, search)
    assert len(result.knowledge_points) == 2 and len(queried) == 2
    assert len(data.existing_knowledge) == 40
    assert provider.options_count == 360 and provider.per_candidate == [180, 180]


@pytest.mark.parametrize("recover,expected_calls", [(False, 18), (True, 33)])
def test_maximum_pipeline_stage_positions_and_recovery_budget(tmp_path, recover, expected_calls):
    images = [tmp_path / f"page{index}.png" for index in range(9)]
    for index, path in enumerate(images):
        path.write_bytes(f"synthetic-{index}".encode())
    provider = MaximumStages(recover=recover)
    data = history_input("十以内加法")
    data.image_paths = images
    pipeline = StagedPipeline(provider, AnalysisTrace.disabled())
    result = asyncio.run(pipeline.run(data, lambda _: [], monotonic() + 10))
    assert pipeline.calls == expected_calls == sum(provider.calls.values())
    assert len(result.todo_matches) == 1 and result.knowledge_points == []
    assert provider.review_calls == 2
    assert sum(count for (stage, _), count in provider.calls.items() if stage == "group") == (
        4 if recover else 2
    )
    assert sum(count for (stage, _), count in provider.calls.items() if stage == "reuse") == 1


@pytest.mark.parametrize("seeded", [False, True])
@pytest.mark.parametrize(
    "unit,verdict,reusable",
    [
        ("review0", False, True),
        ("review1", False, False),
        ("review1", True, True),
        ("reuse", "uncertain", False),
        ("reuse", "accept", True),
        ("reuse", "reject", True),
    ],
)
def test_stage_cache_distinguishes_recoverable_results_from_final_refusals(
    seeded, unit, verdict, reusable
):
    from push_kids.agent_processing.stage_contracts import PIPELINE_REVISION

    if unit == "reuse":
        value = ReuseReviewResult(
            decisions=[ReuseDecision(candidate="i0", match="h0", verdict=verdict, basis="范围不同")]
        )
        stage = "reuse"
    else:
        value = QualityReviewResult(
            passed=verdict,
            issues=[]
            if verdict
            else [QualityIssue(code="vague_name", items=["i0"], basis="范围不明")],
        )
        stage = "review"

    class Checkpoints:
        def __init__(self):
            self.digest = fingerprint(
                {
                    "revision": PIPELINE_REVISION,
                    "parameters": "test-1",
                    "payload": {},
                    "context": None,
                    "images": [],
                }
            )
            self.value = value.model_dump() if seeded else None
            self.writes = []

        def get(self, requested_unit, digest):
            assert (requested_unit, digest) == (unit, self.digest)
            return self.value

        def put(self, requested_unit, digest, result, **kwargs):
            assert (requested_unit, digest) == (unit, self.digest)
            self.writes.append(result)
            self.value = result

    class Provider(StageFake):
        async def generate_stage(self, *args):
            self.calls["stage"] += 1
            return value

    store, provider = Checkpoints(), Provider()
    pipeline = StagedPipeline(provider, AnalysisTrace.disabled(), store)
    result = asyncio.run(
        pipeline._call(stage, unit, "", {}, type(value), [], monotonic() + 10, lambda _: None)
    )
    assert result == value
    assert provider.calls["stage"] == (0 if seeded and reusable else 1)
    assert len(store.writes) == (1 if reusable and not seeded else 0)
    second = asyncio.run(
        pipeline._call(stage, unit, "", {}, type(value), [], monotonic() + 10, lambda _: None)
    )
    assert second == value
    assert provider.calls["stage"] == (0 if seeded and reusable else 1) + (not reusable)
    assert len(store.writes) == (1 if reusable and not seeded else 0)
