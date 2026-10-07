"""Atomic removal of one confirmed knowledge identity and its planning-owned associations."""

from sqlalchemy import case, delete, func, or_, select, update
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    DailyReviewPlanItem,
    KnowledgeItem,
    KnowledgeOccurrence,
    KnowledgeSearchTerm,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import local_date


def delete_knowledge(db: Session, family_id: str, child_id: str, knowledge_id: str) -> None:
    """Keep submissions/media intact; an absent scoped knowledge id is an idempotent no-op."""
    db.scalar(
        select(Child)
        .where(Child.id == child_id, Child.family_id == family_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    ChildrenService.require_active_child(db, family_id, child_id)
    scope = (
        KnowledgeItem.id == knowledge_id,
        KnowledgeItem.family_id == family_id,
        KnowledgeItem.child_id == child_id,
    )
    review = db.scalar(
        select(ReviewItem)
        .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
        .where(*scope, ReviewItem.family_id == family_id, ReviewItem.child_id == child_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    knowledge = db.scalar(select(KnowledgeItem).where(*scope).with_for_update())
    if knowledge is None:
        db.commit()
        return
    if review is not None:
        plan_link = (
            select(DailyReviewPlanItem.id)
            .where(
                DailyReviewPlanItem.family_id == family_id,
                DailyReviewPlanItem.child_id == child_id,
                DailyReviewPlanItem.review_item_id == review.id,
                DailyReviewPlanItem.plan_id == DailyReviewPlan.id,
            )
            .correlate(DailyReviewPlan)
        )
        minutes = (
            select(func.coalesce(func.sum(DailyReviewPlanItem.estimated_minutes), 0))
            .where(
                DailyReviewPlanItem.family_id == family_id,
                DailyReviewPlanItem.review_item_id == review.id,
                DailyReviewPlanItem.plan_id == DailyReviewPlan.id,
            )
            .correlate(DailyReviewPlan)
            .scalar_subquery()
        )
        earliest = (
            select(func.min(ReviewItem.due_date))
            .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
            .join(Subject, Subject.id == KnowledgeItem.subject_id)
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                ReviewItem.id != review.id,
                ReviewItem.active.is_(True),
                ReviewItem.due_date <= DailyReviewPlan.plan_date,
                Subject.kind == "learning",
                Subject.active.is_(True),
            )
            .correlate(DailyReviewPlan)
            .scalar_subquery()
        )
        # Adjust only affected snapshots; never recreate a plan or refill its remaining slots.
        db.execute(
            update(DailyReviewPlan)
            .where(
                DailyReviewPlan.family_id == family_id,
                DailyReviewPlan.child_id == child_id,
                or_(
                    plan_link.exists(),
                    (DailyReviewPlan.plan_date >= local_date())
                    & (DailyReviewPlan.plan_date >= review.due_date)
                    & (DailyReviewPlan.created_at >= knowledge.created_at)
                    & bool(review.active),
                ),
            )
            .values(
                total_minutes=case(
                    (
                        DailyReviewPlan.total_minutes >= minutes,
                        DailyReviewPlan.total_minutes - minutes,
                    ),
                    else_=0,
                ),
                due_count=case(
                    (DailyReviewPlan.due_count > 0, DailyReviewPlan.due_count - 1), else_=0
                ),
                earliest_due=earliest,
            )
            .execution_options(synchronize_session=False)
        )
        for model in (DailyReviewPlanItem, ReviewFeedbackRequest, ReviewFeedback):
            db.execute(
                delete(model).where(model.family_id == family_id, model.review_item_id == review.id)
            )
        db.delete(review)
        db.flush()
    for association in (KnowledgeOccurrence, KnowledgeSearchTerm):
        db.execute(
            delete(association).where(
                association.family_id == family_id, association.knowledge_item_id == knowledge_id
            )
        )
    db.delete(knowledge)
    db.commit()
