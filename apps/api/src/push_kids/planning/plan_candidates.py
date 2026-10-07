"""Bounded database candidates shared by read-only previews and materialized plans."""

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import KnowledgeItem, ReviewItem, ReviewScheduleOverride, Subject
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


def selected_candidates(
    db: Session,
    family_id: str,
    child_id: str,
    target: date,
    budget: int,
    *,
    exclude: tuple[str, ...] = (),
    lock: bool = False,
) -> list[ReviewSelectionCandidate]:
    query = (
        select(ReviewItem, KnowledgeItem, Subject, ReviewScheduleOverride.review_item_id)
        .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
        .join(Subject, Subject.id == KnowledgeItem.subject_id)
        .outerjoin(
            ReviewScheduleOverride,
            and_(
                ReviewScheduleOverride.review_item_id == ReviewItem.id,
                ReviewScheduleOverride.family_id == family_id,
                ReviewScheduleOverride.child_id == child_id,
            ),
        )
        .where(
            ReviewItem.family_id == family_id,
            ReviewItem.child_id == child_id,
            KnowledgeItem.family_id == family_id,
            KnowledgeItem.child_id == child_id,
            Subject.family_id == family_id,
            Subject.child_id == child_id,
            Subject.kind == "learning",
            Subject.active.is_(True),
            ReviewItem.active.is_(True),
            ReviewItem.due_date <= target,
            ReviewItem.id.not_in(exclude),
        )
        .order_by(
            ReviewItem.due_date,
            ReviewItem.last_reviewed_on,
            ReviewItem.id,
        )
        .limit(120)
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    # Separate bounded queries ensure old automatic backlog cannot hide parent reservations.
    manual_ids = select(ReviewScheduleOverride.review_item_id).where(
        ReviewScheduleOverride.family_id == family_id,
        ReviewScheduleOverride.child_id == child_id,
        ReviewScheduleOverride.scheduled_on <= target,
    )
    if lock:
        manual_ids = manual_ids.with_for_update()
    rows = list(db.execute(query.where(ReviewItem.id.in_(manual_ids))))
    rows += list(db.execute(query.where(ReviewScheduleOverride.review_item_id.is_(None))))
    candidates = [
        ReviewSelectionCandidate(
            review_id=r.id,
            knowledge_id=k.id,
            subject_id=s.id,
            subject_name=s.name,
            knowledge_name=k.name,
            review_method=k.review_method,
            estimated_minutes=k.estimated_minutes,
            due_date=r.due_date,
            last_reviewed_on=r.last_reviewed_on,
            review_step=r.step,
            last_feedback=r.last_feedback,
            source_submission_id=r.source_submission_id,
            manually_scheduled=override_id is not None,
        )
        for r, k, s, override_id in rows
    ]
    return select_daily_reviews(candidates, budget_minutes=budget)
