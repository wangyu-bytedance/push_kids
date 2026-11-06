import asyncio
from time import monotonic

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisProposal,
    KnowledgeProposal,
    TodoCandidate,
)
from push_kids.agent_processing.decision_contracts import DecisionAnswer
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.proposal_acceptance import accept_proposal
from push_kids.agent_processing.telemetry import AnalysisTrace


class AcceptanceFake:
    model = "synthetic"

    def __init__(self, *, failure=None, reject=False):
        self.failure, self.reject, self.calls = failure, reject, 0

    async def evaluate(self, questions, state, images, deadline, trace):
        self.calls += 1
        if self.failure:
            raise self.failure
        return {
            key: DecisionAnswer(type="noul", noul=0.1 if self.reject else 0.999)
            for key in questions
        }


def proposal():
    return AnalysisProposal(
        summary="加法练习",
        subject_name="数学",
        knowledge_points=[KnowledgeProposal(name="十以内加法", review_method="变式练习")],
    )


def run(checker, *, seconds=2, value=None, text="十以内加法", paths=None):
    return asyncio.run(
        accept_proposal(
            AnalysisInput(text=text, image_paths=paths or [], analysis_subjects=["数学"]),
            value or proposal(),
            checker,
            monotonic() + seconds,
            AnalysisTrace.disabled(),
        )
    )


@pytest.mark.parametrize("reject", [True, False])
def test_advisory_only_preserves_all_learning_fields(reject):
    value = proposal()
    before = value.model_dump(exclude={"uncertainties"})
    result, audit = run(AcceptanceFake(reject=reject), value=value)
    assert result.model_dump(exclude={"uncertainties"}) == before
    assert audit.outcome == ("needs_review" if reject else "no_finding")
    assert not reject or result.uncertainties


@pytest.mark.parametrize(
    "criterion,threshold",
    [
        ("source", 0.95),
        ("subject", 0.90),
        ("scope", 0.95),
        ("granularity", 0.90),
        ("action", 0.90),
        ("summary", 0.95),
        ("coverage_t", 0.95),
        ("separate", 0.90),
    ],
)
@pytest.mark.parametrize("delta", [-0.000001, 0.0])
def test_frozen_acceptance_thresholds(criterion, threshold, delta):
    class Boundary(AcceptanceFake):
        async def evaluate(self, questions, *args):
            target = (
                criterion
                if criterion in {"summary", "coverage_t", "separate"}
                else f"i0_{criterion}"
            )
            return {
                key: DecisionAnswer(type="noul", noul=threshold + delta if key == target else 1.0)
                for key in questions
            }

    value = proposal()
    value.knowledge_points.append(KnowledgeProposal(name="二十以内减法"))
    result, audit = run(Boundary(), value=value)
    assert audit.outcome == ("needs_review" if delta < 0 else "no_finding")
    assert len(audit.findings) == (1 if delta < 0 else 0)
    assert result.model_dump(exclude={"uncertainties"}) == value.model_dump(
        exclude={"uncertainties"}
    )


@pytest.mark.parametrize(
    "reason",
    [
        "provider_timeout",
        "queue_deadline",
        "auth",
        "config",
        "rate_limited",
        "provider_error",
        "validation",
        "network",
        "capacity",
    ],
)
def test_dependency_failures_are_advisory(reason):
    checker = AcceptanceFake(failure=StageFailure(reason))
    result, audit = run(checker)
    assert checker.calls == 1 and result.knowledge_points[0].name == "十以内加法"
    assert audit.outcome == ("skipped" if reason == "capacity" else "unavailable")
    assert audit.reason == reason and result.uncertainties


def test_budget_capacity_and_disabled_do_not_call_checker():
    for seconds, text in [(0.1, "正常材料"), (2, "内容" * 50000)]:
        checker = AcceptanceFake()
        result, audit = run(checker, seconds=seconds, text=text)
        assert audit.outcome == "skipped" and checker.calls == 0
        assert result.knowledge_points and result.uncertainties
    value = proposal()
    result, audit = run(None, value=value)
    assert result is value and audit.outcome == "disabled"


def test_twenty_original_hints_are_preserved():
    value = proposal()
    value.uncertainties = [f"原提示{i}" for i in range(20)]
    result, audit = run(AcceptanceFake(reject=True), value=value)
    assert audit.outcome == "needs_review" and len(result.uncertainties) == 20
    assert all(
        any(original in hint for hint in result.uncertainties) for original in value.uncertainties
    )


def test_multiple_findings_for_one_item_share_one_positioned_hint():
    value = proposal()
    value.knowledge_points *= 4
    result, audit = run(AcceptanceFake(reject=True), value=value)
    assert len([f for f in audit.findings if f.target == "i0"]) == 5
    assert len([hint for hint in result.uncertainties if hint.startswith("第1条：")]) == 1
    assert all(
        any(hint.startswith(f"第{i}条：") for hint in result.uncertainties) for i in range(1, 5)
    )


def test_nine_images_twenty_points_fit_question_bound(tmp_path):
    paths = []
    for i in range(9):
        p = tmp_path / f"{i}.png"
        p.write_bytes(b"synthetic-image")
        paths.append(p)
    value = proposal()
    value.knowledge_points *= 20
    checker = AcceptanceFake()
    result, audit = run(checker, value=value, paths=paths)
    assert checker.calls == 1 and audit.outcome == "no_finding"
    assert len(result.knowledge_points) == 20


def test_review_targets_are_in_coverage_without_identity_decisions():
    value = proposal()
    value.todo_matches = [
        TodoCandidate(knowledge_name="十以内加法", knowledge_id="old", subject_name="数学")
    ]
    result, audit = run(AcceptanceFake(), value=value)
    assert audit.outcome == "no_finding" and result.todo_matches == value.todo_matches


def test_checker_hang_is_bounded_and_keeps_output():
    class Hang(AcceptanceFake):
        async def evaluate(self, *args):
            await asyncio.Event().wait()

    start = monotonic()
    result, audit = run(Hang(), seconds=0.55)
    assert monotonic() - start < 1.5
    assert audit.outcome == "unavailable" and result.knowledge_points


def test_missing_answers_and_unknown_errors_are_observable():
    class Missing(AcceptanceFake):
        async def evaluate(self, *args):
            return {}

    for checker in [Missing(), AcceptanceFake(failure=RuntimeError("private-provider-payload"))]:
        result, audit = run(checker)
        assert audit.outcome == "unavailable"
        assert audit.reason == ("validation" if isinstance(checker, Missing) else "internal")
        assert "private-provider-payload" not in audit.model_dump_json()
        assert result.knowledge_points
