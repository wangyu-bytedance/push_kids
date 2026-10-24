import asyncio
from time import monotonic

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisProposal,
    ExistingKnowledgeContext,
    KnowledgeProposal,
)
from push_kids.agent_processing.coverage import (
    CoverageDecision,
    CoverageResult,
    accepted_pairs,
    propose_coverage,
)
from push_kids.agent_processing.pipeline import StagedPipeline
from push_kids.agent_processing.telemetry import AnalysisTrace

from tests.coverage_fakes import CoverageFake
from tests.staged_analysis_fakes import StageFake


@pytest.mark.parametrize(
    "flags, expected",
    [
        ((True, True, False), {"p0"}),
        ((True, False, False), set()),
        ((False, True, False), set()),
        ((True, True, True), set()),
    ],
)
def test_complete_same_skill_and_certain_are_all_required(flags, expected):
    result = CoverageResult(
        decisions=[
            CoverageDecision(
                pair="p0", fully_covers=flags[0], same_skill=flags[1], uncertain=flags[2]
            )
        ]
    )
    assert accepted_pairs(result, {"p0"}) == expected


@pytest.mark.parametrize("ids", [[], ["foreign"], ["p0", "p0"], ["p0", "foreign"]])
def test_missing_duplicate_or_invented_alias_rejects_entire_optional_result(ids):
    assert not accepted_pairs(
        CoverageResult(
            decisions=[
                CoverageDecision(pair=a, fully_covers=True, same_skill=True, uncertain=False)
                for a in ids
            ]
        ),
        {"p0"},
    )


@pytest.mark.parametrize(
    "fail, uncertain, expected_ok, expected_matches",
    [(True, False, False, 0), (False, True, True, 0), (False, False, True, 1)],
)
def test_optional_provider_failure_and_uncertainty_keep_independent_review(
    fail, uncertain, expected_ok, expected_matches
):
    proposal = AnalysisProposal(
        summary="练习",
        subject_name="英语",
        knowledge_points=[
            KnowledgeProposal(
                name="cat dog bird拼写", subject_name="英语", review_method="主动回忆"
            )
        ],
    )
    contexts = [
        ExistingKnowledgeContext(
            knowledge_id="old", name="cat dog拼写", subject_name="英语", category="词汇"
        )
    ]
    ok = asyncio.run(
        propose_coverage(
            CoverageFake(fail=fail, uncertain=uncertain),
            proposal,
            contexts,
            monotonic() + 3,
            AnalysisTrace.disabled(),
        )
    )
    assert ok == expected_ok
    assert len(proposal.coverage_matches) == expected_matches


def test_other_subject_low_confidence_and_superseded_candidates_are_never_sent():
    provider = CoverageFake()
    proposal = AnalysisProposal(
        summary="练习",
        subject_name="科学",
        knowledge_points=[KnowledgeProposal(name="水循环", subject_name="科学", confidence="low")],
    )
    ctx = ExistingKnowledgeContext(
        knowledge_id="k", name="蒸发", subject_name="科学", category="概念"
    )
    asyncio.run(
        propose_coverage(provider, proposal, [ctx], monotonic() + 3, AnalysisTrace.disabled())
    )
    assert provider.calls == 0
    proposal.knowledge_points[0].confidence = "high"
    ctx.subject_name = "数学"
    asyncio.run(
        propose_coverage(provider, proposal, [ctx], monotonic() + 3, AnalysisTrace.disabled())
    )
    assert provider.calls == 0
    ctx.subject_name, ctx.review_status = "科学", "superseded"
    asyncio.run(
        propose_coverage(provider, proposal, [ctx], monotonic() + 3, AnalysisTrace.disabled())
    )
    assert provider.calls == 0
    ctx.review_status = "normal"
    ctx.coverage_evidence_complete = False
    asyncio.run(
        propose_coverage(provider, proposal, [ctx], monotonic() + 3, AnalysisTrace.disabled())
    )
    assert provider.calls == 0


@pytest.mark.parametrize("coverage_unavailable", [False, True])
def test_real_pipeline_keeps_learning_proposal_when_optional_coverage_is_unavailable(
    coverage_unavailable,
):
    class PipelineProvider(StageFake):
        def __init__(self):
            super().__init__()
            self.coverage = CoverageFake(fail=coverage_unavailable)

        async def generate_stage(self, stage, *args):
            if stage == "coverage":
                return await self.coverage.generate_stage(stage, *args)
            return await super().generate_stage(stage, *args)

    provider = PipelineProvider()
    old = ExistingKnowledgeContext(
        knowledge_id="old",
        name="五以内加法",
        subject_name="数学",
        category="计算",
        review_method="变式练习",
    )
    data = AnalysisInput(text="十以内加法", existing_subjects=["数学"])

    def search(_):
        # The runner's scoped search publishes validated contexts on AnalysisInput.
        data.existing_knowledge.append(old)
        return []

    result = asyncio.run(
        StagedPipeline(provider, AnalysisTrace.disabled()).run(
            data,
            search,
            monotonic() + 3,
        )
    )
    assert provider.coverage.calls == 1
    assert result.knowledge_points[0].name == "十以内加法"
    assert [m.old_knowledge_id for m in result.coverage_matches] == (
        [] if coverage_unavailable else ["old"]
    )
