from __future__ import annotations

import asyncio
from time import monotonic

import pytest
from push_kids.agent_processing.contracts import AnalysisInput, analysis_failure_disposition
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.telemetry import AnalysisTrace

from tests.staged_analysis_fakes import StageFake


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
