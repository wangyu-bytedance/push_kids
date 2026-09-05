from datetime import date, timedelta

import pytest
from push_kids.planning.domain import (
    DueKnowledge,
    apply_feedback,
    group_daily_todos,
    initial_review_date,
    review_interval_days,
)


def test_initial_review_uses_next_day_for_recent_learning() -> None:
    today = date(2026, 8, 30)
    assert initial_review_date(today, today) == date(2026, 8, 31)


def test_old_backfill_creates_current_check_without_historical_debt() -> None:
    assert initial_review_date(date(2026, 1, 1), date(2026, 8, 30)) == date(2026, 8, 30)


@pytest.mark.parametrize(
    ("action", "expected_step", "expected_days", "active"),
    [
        ("complete", 1, 3, True),
        ("reinforce", 0, 1, True),
        ("partial", 1, 1, True),
        ("defer", 0, 1, True),
    ],
)
def test_feedback_transitions(
    action: str, expected_step: int, expected_days: int, active: bool
) -> None:
    today = date(2026, 8, 30)
    result = apply_feedback(0, action, today)  # type: ignore[arg-type]
    assert result.step == expected_step
    assert result.due_date == today + timedelta(days=expected_days)
    assert result.active is active


def test_final_complete_retires_item() -> None:
    result = apply_feedback(5, "complete", date(2026, 8, 30))
    assert result.step == 6
    assert result.active is False


def test_group_daily_todos_respects_budget_and_groups_subject_method() -> None:
    items = [
        DueKnowledge("r1", "math", "数学", "进位加法", "口算", 4, date(2026, 8, 29)),
        DueKnowledge("r2", "math", "数学", "退位减法", "口算", 4, date(2026, 8, 30)),
        DueKnowledge("r3", "en", "英语", "animal", "听说", 5, date(2026, 8, 30)),
    ]
    groups = group_daily_todos(items, budget_minutes=8)
    assert len(groups) == 2
    assert len(groups[0]["items"]) == 2
    assert groups[0]["optional"] is False
    assert groups[1]["optional"] is True


def test_group_daily_todos_passes_through_todo_provenance() -> None:
    items = [
        DueKnowledge(
            "r1",
            "math",
            "数学",
            "进位加法",
            "口算",
            4,
            date(2026, 9, 5),
            source_submission_id="sub-1",
            source_occurred_on=date(2026, 9, 2),
            review_round=2,
            interval_days=3,
        )
    ]
    item = group_daily_todos(items, budget_minutes=15)[0]["items"][0]
    assert item["source_submission_id"] == "sub-1"
    assert item["source_occurred_on"] == "2026-09-02"
    assert item["review_round"] == 2
    assert item["interval_days"] == 3


def test_group_daily_todos_keeps_history_without_provenance() -> None:
    items = [DueKnowledge("r1", "math", "数学", "进位加法", "口算", 4, date(2026, 9, 5))]
    item = group_daily_todos(items, budget_minutes=15)[0]["items"][0]
    assert item["source_submission_id"] is None
    assert item["source_occurred_on"] is None
    assert item["review_round"] == 1
    assert item["interval_days"] is None


def test_interval_days_uses_first_learning_when_never_reviewed() -> None:
    assert review_interval_days(date(2026, 9, 5), None, date(2026, 9, 2)) == 3


def test_interval_days_prefers_last_review_over_first_learning() -> None:
    assert review_interval_days(date(2026, 9, 5), date(2026, 9, 4), date(2026, 9, 2)) == 1


def test_interval_days_is_unknown_without_any_anchor() -> None:
    assert review_interval_days(date(2026, 9, 5), None, None) is None
