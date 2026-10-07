from dataclasses import replace
from datetime import date, timedelta
from random import Random

import pytest
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews

DAY = date(2026, 10, 7)


def item(n, subject="cn", **values):
    return replace(
        ReviewSelectionCandidate(
            str(n),
            str(n),
            subject,
            subject,
            "synthetic",
            "recall",
            3,
            DAY,
        ),
        **values,
    )


def test_subjects_cannot_be_hidden_by_old_language_backlog():
    rows = [item(i, due_date=DAY - timedelta(days=20)) for i in range(200)]
    rows += [item("math", "math"), item("en", "en")]
    chosen = select_daily_reviews(rows, budget_minutes=30)
    assert {r.subject_id for r in chosen} == {"cn", "math", "en"}
    assert len(chosen) == 10


def test_coverage_reserves_affordable_choices_for_remaining_subjects():
    rows = [
        item("a", "a", estimated_minutes=5),
        item("b", "a", estimated_minutes=1),
        item("c", "b", estimated_minutes=4),
    ]
    assert {r.review_id for r in select_daily_reviews(rows, budget_minutes=5)} == {"b", "c"}


def test_first_and_repeat_opportunities_are_balanced_after_coverage():
    rows = [item(n, estimated_minutes=1, review_count=int(n > 19)) for n in range(40)]
    chosen = select_daily_reviews(rows, budget_minutes=15)
    assert sum(r.review_count == 0 for r in chosen) == 8
    assert sum(r.review_count > 0 for r in chosen) == 7


def test_waiting_priority_within_the_same_pool():
    old = item("old", due_date=DAY - timedelta(days=50), missed_plan_days=0)
    waiting = item("waiting", missed_plan_days=3)
    assert select_daily_reviews([old, waiting], budget_minutes=3) == [waiting]


def test_small_budget_rotates_subject_opportunities_without_faking_completion():
    rows = [item(i, str(i), estimated_minutes=5) for i in range(4)]
    seen = set()
    for n in range(4):
        chosen = select_daily_reviews(rows, budget_minutes=5)
        assert len(chosen) == 1
        sid = chosen[0].subject_id
        seen.add(sid)
        rows = [
            replace(r, subject_last_offered_on=DAY + timedelta(days=n))
            if r.subject_id == sid
            else r
            for r in rows
        ]
        assert all(r.review_count == 0 for r in rows)
    assert len(seen) == 4


@pytest.mark.parametrize("budget", [0, 5, 15, 30, 120])
def test_deterministic_budget_and_no_duplicates(budget):
    rows = [
        item(n, str(n % 130), estimated_minutes=n % 7, review_count=n % 2, missed_plan_days=n % 4)
        for n in range(500)
    ]
    expected = select_daily_reviews(rows, budget_minutes=budget)
    Random(42).shuffle(rows)
    actual = select_daily_reviews(rows + rows[:10], budget_minutes=budget)
    assert actual == expected
    assert sum(r.bounded_minutes for r in actual) <= budget
    assert len(actual) <= 120
    assert len({r.review_id for r in actual}) == len(actual)


def test_parent_reservation_can_exceed_budget_but_automatic_items_cannot():
    rows = [
        item("reserved", manually_scheduled=True, estimated_minutes=5),
        item("auto", "other", estimated_minutes=1),
    ]
    assert [r.review_id for r in select_daily_reviews(rows, budget_minutes=3)] == ["reserved"]
