"""Closed, deterministic policy for conservative empty-day opportunities."""

from datetime import date

EARLY_REVIEW_POLICY_REVISION = "empty-day-v1"


def early_eligible(
    *,
    target: date,
    due: date,
    last_reviewed: date | None,
    review_count: int,
    last_offered: date | None = None,
    eligible_on: date | None = None,
) -> bool:
    if last_reviewed is None or review_count < 1:
        return False
    elapsed = (target - last_reviewed).days
    interval = (due - last_reviewed).days
    return (
        1 <= (due - target).days <= 3
        and interval > 0
        and elapsed >= 2
        and 5 * elapsed >= 4 * interval
        and (last_offered is None or (target - last_offered).days >= 2)
        # Equal-to-due is the old automatic queue anchor, not a parent's reservation.
        and (eligible_on is None or eligible_on == due or target >= eligible_on)
    )
