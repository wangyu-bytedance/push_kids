import asyncio
from time import monotonic

from push_kids.agent_processing.contracts import AnalysisInput
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.stage_contracts import MatchDecision, MatchingResult
from push_kids.agent_processing.telemetry import AnalysisTrace

from tests.staged_analysis_fakes import StageFake


def test_uncertain_match_cannot_be_reused_from_checkpoint():
    assert not StagedPipeline._checkpoint_reusable(
        "match",
        MatchingResult(decisions=[MatchDecision(candidate="i0", match=None, uncertain=True)]),
    )


def test_acceptance_capability_never_replaces_pro_generation():
    provider = StageFake()
    provider.acceptance_provider = object()
    result = asyncio.run(
        StagedPipeline(provider, AnalysisTrace.disabled()).run(
            AnalysisInput(text="十以内加法", existing_subjects=["数学"]),
            lambda request: [],
            monotonic() + 5,
        )
    )
    assert result.knowledge_points[0].name == "十以内加法"
    assert provider.calls["review", "review"] and provider.calls["match", "match"]
    assert not any(
        stage in {"classify", "decision", "decision_fallback", "disambiguate"}
        for stage, _ in provider.calls
    )
