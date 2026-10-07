"""Planning-owned queue dates; offering a task never records a review."""

from datetime import date, timedelta

from sqlalchemy import case, select, update
from sqlalchemy.orm import Session

from push_kids.persistence.models import DailyReviewPlan, ReviewItem
from push_kids.planning.selection import DAILY_REVIEW_POLICY_REVISION


def initialize_queue(review: ReviewItem, confirmed_on: date) -> None:
    assert review.due_date is not None
    review.queue_eligible_on = max(review.due_date, confirmed_on)


def reset_queue(review: ReviewItem, changed_on: date, *, deferred: bool = False) -> None:
    assert review.due_date is not None
    review.queue_eligible_on = max(review.due_date, changed_on + timedelta(days=int(deferred)))


def record_offered(
    db: Session, family_id: str, child_id: str, review_ids: list[str], offered_on: date
) -> None:
    if not review_ids:
        return
    if len(review_ids) > 120:
        raise ValueError("Plan offer exceeds 120 items")
    db.execute(
        update(ReviewItem)
        .where(
            ReviewItem.family_id == family_id,
            ReviewItem.child_id == child_id,
            ReviewItem.id.in_(review_ids),
        )
        .values(
            last_offered_on=case(
                (ReviewItem.last_offered_on > offered_on, ReviewItem.last_offered_on),
                else_=offered_on,
            )
        )
    )


def recent_plan_days(
    db: Session, family_id: str, child_id: str, before: date, *, lock: bool = False
) -> list[date]:
    query = (
        select(DailyReviewPlan.plan_date)
        .where(
            DailyReviewPlan.family_id == family_id,
            DailyReviewPlan.child_id == child_id,
            DailyReviewPlan.policy_revision == DAILY_REVIEW_POLICY_REVISION,
            DailyReviewPlan.plan_date < before,
        )
        .order_by(DailyReviewPlan.plan_date.desc())
        .limit(3)
    )
    return list(db.scalars(query.with_for_update() if lock else query))


def missed_days(review: ReviewItem, days: list[date], *, resumed_on: date | None = None) -> int:
    assert review.due_date is not None
    anchor = max(
        review.due_date,
        review.queue_eligible_on or review.due_date,
        resumed_on or date.min,
        review.last_offered_on + timedelta(days=1) if review.last_offered_on else date.min,
    )
    return min(3, sum(day >= anchor for day in days))
