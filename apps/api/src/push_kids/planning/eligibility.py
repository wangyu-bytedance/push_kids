"""SQL scheduling qualification shared by bounded planning reads."""

from sqlalchemy import exists, or_

from push_kids.persistence.models import KnowledgeItem, ReviewItem, ReviewScheduleOverride


def scheduling_eligible():
    manual = (
        exists()
        .where(
            ReviewScheduleOverride.review_item_id == ReviewItem.id,
            ReviewScheduleOverride.family_id == ReviewItem.family_id,
            ReviewScheduleOverride.child_id == ReviewItem.child_id,
        )
        .correlate(ReviewItem)
    )
    return or_(KnowledgeItem.review_status == "normal", manual)
