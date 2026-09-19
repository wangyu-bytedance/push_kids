from __future__ import annotations

from datetime import date, timedelta

from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews

TODAY = date(2026, 9, 13)


def candidate(
    index: int,
    *,
    subject: int = 0,
    minutes: int = 2,
    overdue_days: int = 0,
    last_reviewed_days_ago: int | None = None,
) -> ReviewSelectionCandidate:
    return ReviewSelectionCandidate(
        review_id=f"review-{index:02}",
        knowledge_id=f"knowledge-{index}",
        subject_id=f"subject-{subject}",
        subject_name=f"科目{subject}",
        knowledge_name=f"知识{index}",
        review_method="主动回忆",
        estimated_minutes=minutes,
        due_date=TODAY - timedelta(days=overdue_days),
        last_reviewed_on=(
            TODAY - timedelta(days=last_reviewed_days_ago)
            if last_reviewed_days_ago is not None
            else None
        ),
    )


def test_selection_is_stable_and_not_capped_at_six() -> None:
    rows = [candidate(index, subject=index % 3, minutes=1) for index in range(30)]

    first = select_daily_reviews(rows, budget_minutes=15)
    repeated = select_daily_reviews(list(reversed(rows)), budget_minutes=15)

    assert [item.review_id for item in first] == [item.review_id for item in repeated]
    assert len(first) == 15
    assert sum(item.bounded_minutes for item in first) == 15


def test_selection_orders_by_due_then_oldest_actual_review() -> None:
    rows = [
        candidate(1, overdue_days=2, last_reviewed_days_ago=3),
        candidate(2, overdue_days=8, last_reviewed_days_ago=1),
        candidate(3, overdue_days=2, last_reviewed_days_ago=None),
        candidate(4, overdue_days=2, last_reviewed_days_ago=20),
    ]

    selected = select_daily_reviews(rows, budget_minutes=8)

    assert [item.review_id for item in selected] == [
        "review-02",
        "review-03",
        "review-04",
        "review-01",
    ]


def test_selection_respects_minutes_and_clamps_each_item() -> None:
    rows = [candidate(index, minutes=20) for index in range(10)]

    selected = select_daily_reviews(rows, budget_minutes=15)

    assert len(selected) == 3
    assert [item.bounded_minutes for item in selected] == [5, 5, 5]
