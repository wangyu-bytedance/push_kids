from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from inspect import signature
from time import monotonic

from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisOutputValidationError,
    AnalysisProposal,
)
from push_kids.agent_processing.history_search import (
    HistorySearchRequest,
    search_history_items,
)
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.platform.database import Database

MAX_AGENT_TURNS = 8
MAX_TOOL_CALLS = 20
MAX_UNIQUE_RESULTS = 100

HistorySearch = Callable[[HistorySearchRequest], list[dict[str, object]]]


@dataclass
class AgentToolLedger:
    tool_calls: int = 0
    unique_result_ids: set[str] = field(default_factory=set)
    searched_candidates: set[tuple[str, str]] = field(default_factory=set)


class AnalysisAgentRunner:
    """Own the bounded tool trust boundary around a model provider."""

    def __init__(self, database: Database, provider) -> None:
        self.database = database
        self.provider = provider

    def run(
        self,
        data: AnalysisInput,
        *,
        family_id: str,
        child_id: str,
        trace: AnalysisTrace | None = None,
        time_budget_seconds: float | None = None,
    ) -> AnalysisProposal:
        trace = trace or AnalysisTrace.disabled()
        tool_aware = getattr(self.provider, "analyze_with_history", None)
        if tool_aware is None:
            # Compatibility for test doubles and a controlled rollback to the old provider.
            return data.validate_proposal(self.provider.analyze(data))

        ledger = AgentToolLedger()

        def execute(request: HistorySearchRequest) -> list[dict[str, object]]:
            if ledger.tool_calls >= MAX_TOOL_CALLS:
                raise AnalysisOutputValidationError(["history_search.tool_budget"])
            ledger.tool_calls += 1
            candidate_name = normalize_knowledge_name(request.candidate_key)
            if not candidate_name:
                raise AnalysisOutputValidationError(["history_search.candidate_key"])
            with self.database.session_factory() as db:
                rows = search_history_items(
                    db,
                    family_id=family_id,
                    child_id=child_id,
                    request=request,
                )
            new_ids = {row.knowledge_id for row in rows} - ledger.unique_result_ids
            if len(ledger.unique_result_ids) + len(new_ids) > MAX_UNIQUE_RESULTS:
                raise AnalysisOutputValidationError(["history_search.result_budget"])
            ledger.unique_result_ids.update(new_ids)
            ledger.searched_candidates.add((request.subject_name, candidate_name))
            known = {row.knowledge_id for row in data.existing_knowledge}
            data.existing_knowledge.extend(row for row in rows if row.knowledge_id not in known)
            return [row.model_dump() for row in rows]

        def validate_final(proposal: AnalysisProposal) -> AnalysisProposal:
            proposal = data.validate_proposal(proposal)
            missing = [
                point
                for point in proposal.knowledge_points
                if (
                    point.subject_name or proposal.subject_name,
                    normalize_knowledge_name(point.name),
                )
                not in ledger.searched_candidates
            ]
            if missing:
                raise AnalysisOutputValidationError(["history_search.incomplete"])
            return proposal

        kwargs: dict[str, object] = {"max_turns": MAX_AGENT_TURNS}
        parameters = signature(tool_aware).parameters
        if "validate_final" in parameters:
            kwargs["validate_final"] = validate_final
        if "trace" in parameters:
            kwargs["trace"] = trace
        if "deadline" in parameters and time_budget_seconds is not None:
            kwargs["deadline"] = monotonic() + max(0.0, time_budget_seconds)
        proposal = tool_aware(data, execute, **kwargs)
        # Compatibility and security fallback for providers that do not accept the callback,
        # and a final defense if a provider forgets to invoke it.
        return validate_final(proposal)
