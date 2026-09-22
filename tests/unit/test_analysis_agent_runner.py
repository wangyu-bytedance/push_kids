from __future__ import annotations

import push_kids.agent_processing.runner as runner_module
import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisOutputValidationError,
    AnalysisProposal,
    EvidenceReference,
    KnowledgeProposal,
)
from push_kids.agent_processing.history_search import HistorySearchRequest
from push_kids.agent_processing.runner import AnalysisAgentRunner


def _new_proposal(name: str = "进位加法") -> AnalysisProposal:
    return AnalysisProposal(
        summary="识别到数学学习内容",
        subject_name="数学",
        source="家长文字",
        knowledge_points=[
            KnowledgeProposal(
                name=name,
                subject_name="数学",
                category="计算",
                review_method="变式练习",
                estimated_minutes=3,
                direct_evidence=[
                    EvidenceReference(source="parent_text", detail="家长文字中明确出现")
                ],
            )
        ],
    )


class _NoSearchProvider:
    def analyze_with_history(self, data, search_history, *, max_turns):
        del data, search_history, max_turns
        return _new_proposal()


class _SearchedNewProvider:
    def analyze_with_history(self, data, search_history, *, max_turns):
        del data
        assert max_turns == 8
        assert (
            search_history(
                HistorySearchRequest(
                    candidate_key="进位加法",
                    subject_name="数学",
                    keywords=("进位加法",),
                )
            )
            == []
        )
        return _new_proposal()


class _ToolBudgetProvider:
    def analyze_with_history(self, data, search_history, *, max_turns):
        del data, max_turns
        for index in range(21):
            search_history(
                HistorySearchRequest(
                    candidate_key=f"候选{index}",
                    subject_name="数学",
                    keywords=(f"候选{index}",),
                )
            )
        return _new_proposal()


class _DeadlineProvider:
    deadline: float | None = None

    def analyze_with_history(self, data, search_history, *, max_turns, deadline):
        del data, max_turns
        self.deadline = deadline
        search_history(
            HistorySearchRequest(
                candidate_key="进位加法",
                subject_name="数学",
                keywords=("进位加法",),
            )
        )
        return _new_proposal()


class _CorrectableFinalProvider:
    validation_codes: list[str] = []

    def analyze_with_history(
        self,
        data,
        search_history,
        *,
        max_turns,
        validate_final,
    ):
        del data
        assert max_turns == 8
        search_history(
            HistorySearchRequest(
                candidate_key="加法",
                subject_name="数学",
                keywords=("加法",),
            )
        )
        try:
            validate_final(_new_proposal("两位数进位加法"))
        except AnalysisOutputValidationError as exc:
            self.validation_codes = exc.codes
        search_history(
            HistorySearchRequest(
                candidate_key="两位数进位加法",
                subject_name="数学",
                keywords=("进位加法",),
            )
        )
        return validate_final(_new_proposal("两位数进位加法"))


def test_runner_refuses_to_label_new_without_a_completed_history_search(app, client) -> None:
    del client
    runner = AnalysisAgentRunner(app.state.database, _NoSearchProvider())

    with pytest.raises(AnalysisOutputValidationError) as error:
        runner.run(
            AnalysisInput(text="进位加法", existing_subjects=["数学"]),
            family_id="family-a",
            child_id="child-a",
        )

    assert error.value.codes == ["history_search.incomplete"]


def test_runner_allows_new_after_scoped_search_returns_no_history(app, client) -> None:
    del client
    runner = AnalysisAgentRunner(app.state.database, _SearchedNewProvider())

    proposal = runner.run(
        AnalysisInput(text="进位加法", existing_subjects=["数学"]),
        family_id="family-a",
        child_id="child-a",
    )

    assert [point.name for point in proposal.knowledge_points] == ["进位加法"]


def test_runner_exposes_final_ledger_validation_inside_provider_loop(app, client) -> None:
    del client
    provider = _CorrectableFinalProvider()
    runner = AnalysisAgentRunner(app.state.database, provider)

    proposal = runner.run(
        AnalysisInput(text="两位数进位加法", existing_subjects=["数学"]),
        family_id="family-a",
        child_id="child-a",
    )

    assert provider.validation_codes == ["history_search.incomplete"]
    assert [point.name for point in proposal.knowledge_points] == ["两位数进位加法"]


def test_runner_enforces_the_global_history_tool_call_budget(app, client) -> None:
    del client
    runner = AnalysisAgentRunner(app.state.database, _ToolBudgetProvider())

    with pytest.raises(AnalysisOutputValidationError) as error:
        runner.run(
            AnalysisInput(text="进位加法", existing_subjects=["数学"]),
            family_id="family-a",
            child_id="child-a",
        )

    assert error.value.codes == ["history_search.tool_budget"]


def test_runner_derives_provider_deadline_from_worker_supplied_lease_budget(
    app, client, monkeypatch
) -> None:
    del client
    provider = _DeadlineProvider()
    monkeypatch.setattr(runner_module, "monotonic", lambda: 1000.0)

    AnalysisAgentRunner(app.state.database, provider).run(
        AnalysisInput(text="进位加法", existing_subjects=["数学"]),
        family_id="family-a",
        child_id="child-a",
        time_budget_seconds=42.0,
    )

    assert provider.deadline == 1042.0
