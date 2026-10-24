"""Explicit coverage protocol fake; never claims semantic model accuracy."""

from push_kids.agent_processing.coverage import CoverageDecision, CoverageResult


class CoverageFake:
    def __init__(self, accept=True, uncertain=False, fail=False):
        self.accept, self.uncertain, self.fail, self.calls = accept, uncertain, fail, 0

    async def generate_stage(self, stage, instructions, payload, schema, images, deadline, trace):
        assert stage == "coverage"
        assert not images and len(payload["pairs"]) <= 400
        self.calls += 1
        if self.fail:
            raise TimeoutError()
        return CoverageResult(
            decisions=[
                CoverageDecision(
                    pair=p["pair"],
                    fully_covers=self.accept,
                    same_skill=self.accept,
                    uncertain=self.uncertain,
                )
                for p in payload["pairs"]
            ]
        )
