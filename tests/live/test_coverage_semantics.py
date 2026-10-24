"""Opt-in, synthetic-only independent semantic acceptance corpus."""

import asyncio
import json
import os
from pathlib import Path
from time import monotonic

import pytest
from push_kids.agent_processing.coverage import INSTRUCTIONS, CoverageResult, accepted_pairs
from push_kids.agent_processing.stage_provider import StagedArkProvider
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings


@pytest.mark.live
@pytest.mark.skipif(os.getenv("PUSH_KIDS_RUN_COVERAGE_LIVE") != "1", reason="live coverage opt-in")
def test_live_independently_labelled_full_vs_partial_and_different_skills():
    cases = json.loads((Path(__file__).parents[1] / "fixtures/coverage_semantics.json").read_text())
    provider = StagedArkProvider(Settings())
    assert provider.settings.ark_api_key
    pairs = [
        {
            "pair": str(i),
            "subject": c["subject"],
            "old": {"name": c["old"], "evidence": c["old"]},
            "new": {"name": c["new"], "evidence": c["new"]},
        }
        for i, c in enumerate(cases)
    ]

    async def run():
        async with asyncio.timeout(35):
            return await provider.generate_stage(
                "coverage",
                INSTRUCTIONS,
                {"pairs": pairs},
                CoverageResult,
                [],
                monotonic() + 30,
                AnalysisTrace.disabled(),
            )

    result = asyncio.run(run())
    actual = accepted_pairs(result, {str(i) for i in range(len(cases))})
    expected = {str(i) for i, c in enumerate(cases) if c["expected"]}
    assert actual == expected, {
        "false_positive": [cases[int(i)]["id"] for i in sorted(actual - expected)],
        "false_negative": [cases[int(i)]["id"] for i in sorted(expected - actual)],
    }
