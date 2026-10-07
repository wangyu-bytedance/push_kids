from datetime import date, timedelta

import pytest
from push_kids.planning.domain import parent_schedule_date
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


@pytest.mark.parametrize("today", [date(2026, 12, 31), date(2024, 2, 28), date(2026, 2, 28)])
def test_parent_date_is_deterministic_across_calendar_boundaries(today):
    tomorrow = parent_schedule_date(today, "tomorrow", today)
    assert tomorrow == today + timedelta(days=1)
    assert parent_schedule_date(today, "day_after", tomorrow) == today + timedelta(days=2)
    with pytest.raises(ValueError):
        parent_schedule_date(today, "day_after", today + timedelta(days=5))


def test_manual_budget_exception_never_breaks_120_item_cap():
    candidates = [
        ReviewSelectionCandidate(
            str(i), str(i), "s", "math", "one", "read", 5, date(2026, 1, 1), manually_scheduled=True
        )
        for i in range(121)
    ]
    chosen = select_daily_reviews(candidates, budget_minutes=5)
    assert len(chosen) == 120
    assert sum(c.bounded_minutes for c in chosen) == 600
