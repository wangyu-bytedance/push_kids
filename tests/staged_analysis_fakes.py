"""Deterministic stage adapter for protocol and durable recovery tests."""

import asyncio
from collections import Counter

from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.stage_contracts import (
    ConsolidatedResult,
    ExtractedPoint,
    MatchDecision,
    MatchingResult,
    MaterialResult,
    MergedPoint,
)


class StageFake:
    concurrency = 2
    parameter_revision = "test-1"

    def __init__(self, *, fail_unit=None, fail_stage=None, broken=None, needs_context=False):
        self.calls = Counter()
        self.fail_unit, self.fail_stage = fail_unit, fail_stage
        self.broken, self.needs_context = broken, needs_context
        self.active = self.max_active = 0

    async def generate_stage(self, stage, instructions, payload, schema, images, deadline, trace):
        unit = payload.get("materials", [stage])[0]
        self.calls[stage, unit] += 1
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(0.005)
            if stage == self.fail_stage or unit == self.fail_unit:
                raise StageFailure("provider_timeout")
            if stage in {"extract", "group"}:
                return MaterialResult(
                    status="content",
                    needs_context=self.needs_context and stage == "extract",
                    excerpt="续页" if self.needs_context else "",
                    items=[
                        ExtractedPoint(
                            subject="数学",
                            name="十以内加法",
                            evidence="根据两组数量求总数",
                            materials=["m9"] if self.broken == "source" else payload["materials"],
                            confidence="high",
                        )
                    ],
                )
            if stage == "merge":
                members = list(payload["candidates"])
                if self.broken == "coverage":
                    members = members[:-1]
                return ConsolidatedResult(
                    summary="未涉及语文内容" if self.broken == "summary" else "练习十以内加法",
                    uncertainties=[],
                    items=[
                        MergedPoint(
                            members=members or ["invented"],
                            subject="数学",
                            name="十以内加法",
                            category="计算",
                            display_kind="arithmetic",
                            review_method="变式练习",
                            estimated_minutes=3,
                        )
                    ],
                )
            return MatchingResult(
                decisions=[
                    MatchDecision(
                        candidate=row["candidate"],
                        match="h999"
                        if self.broken == "reference"
                        else next(
                            (o["id"] for o in row["options"] if o["name"] == row["name"]), None
                        ),
                        uncertain=self.broken == "uncertain",
                    )
                    for row in payload["candidates"]
                ]
            )
        finally:
            self.active -= 1
