"""Planning-owned consequences of an already validated knowledge status change."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import ReviewItem, ReviewScheduleOverride
from push_kids.planning.scheduling import refresh_future_due_stats, withdraw_pending
from push_kids.platform.time import local_date


def reconcile_superseded(db: Session, family_id: str, child_id: str, knowledge_id: str) -> None:
    review = db.scalar(
        select(ReviewItem)
        .where(
            ReviewItem.family_id == family_id,
            ReviewItem.child_id == child_id,
            ReviewItem.knowledge_item_id == knowledge_id,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if review:
        manual = db.scalar(
            select(ReviewScheduleOverride.review_item_id).where(
                ReviewScheduleOverride.review_item_id == review.id,
                ReviewScheduleOverride.family_id == family_id,
                ReviewScheduleOverride.child_id == child_id,
            )
        )
        if not manual:
            withdraw_pending(db, family_id, child_id, str(review.id), local_date())
        review.state_version = int(review.state_version or 0) + 1
        db.flush()
        refresh_future_due_stats(db, family_id, child_id, local_date())
    ChildrenService.invalidate_review_inventory(db, family_id, child_id)
