from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    Child,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
    Subject,
)
from push_kids.planning.domain import (
    DueKnowledge,
    apply_feedback,
    group_daily_todos,
    review_interval_days,
)
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import local_date


@dataclass(frozen=True)
class PendingReviewLoad:
    """How much review one child still owes as of a local day.

    The count is the number of outstanding knowledge points, using exactly the same rule as the
    Today list: a review that has been given feedback is no longer due, so this stays a read of
    planning policy and never advances a schedule.
    """

    family_id: str
    child_id: str
    child_name: str
    pending_count: int
    subject_names: tuple[str, ...]


class PlanningService:
    @staticmethod
    def purge_data(db: Session, family_id: str, child_id: str | None) -> None:
        review_query = select(ReviewItem.id).where(ReviewItem.family_id == family_id)
        knowledge_query = select(KnowledgeItem.id).where(KnowledgeItem.family_id == family_id)
        if child_id is not None:
            review_query = review_query.where(ReviewItem.child_id == child_id)
            knowledge_query = knowledge_query.where(KnowledgeItem.child_id == child_id)
        review_ids = list(db.scalars(review_query))
        knowledge_ids = list(db.scalars(knowledge_query))
        record_query = select(LearningRecord.id).where(LearningRecord.family_id == family_id)
        if child_id is not None:
            record_query = record_query.where(LearningRecord.child_id == child_id)
        record_ids = list(db.scalars(record_query))
        db.execute(
            delete(ReviewFeedbackRequest).where(
                ReviewFeedbackRequest.family_id == family_id,
                ReviewFeedbackRequest.review_item_id.in_(review_ids),
            )
        )
        db.execute(
            delete(ReviewFeedback).where(
                ReviewFeedback.family_id == family_id,
                ReviewFeedback.review_item_id.in_(review_ids),
            )
        )
        db.execute(
            delete(KnowledgeOccurrence).where(
                KnowledgeOccurrence.family_id == family_id,
                or_(
                    KnowledgeOccurrence.knowledge_item_id.in_(knowledge_ids),
                    KnowledgeOccurrence.learning_record_id.in_(record_ids),
                ),
            )
        )
        db.execute(delete(ReviewItem).where(ReviewItem.id.in_(review_ids)))
        db.execute(delete(KnowledgeItem).where(KnowledgeItem.id.in_(knowledge_ids)))

    @staticmethod
    def history_for_knowledge(
        db: Session,
        family_id: str,
        child_id: str,
        knowledge_ids: list[str],
        review_id: str | None = None,
        before: str | None = None,
    ) -> dict:
        ChildrenService.get_child(db, family_id, child_id)
        query = (
            select(ReviewItem, KnowledgeItem)
            .join(
                KnowledgeItem,
                ReviewItem.knowledge_item_id == KnowledgeItem.id,
            )
            .join(Subject, Subject.id == KnowledgeItem.subject_id)
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.id.in_(knowledge_ids),
                Subject.kind == "learning",
            )
        )
        if review_id:
            query = query.where(ReviewItem.id == review_id)
        rows = db.execute(query.order_by(KnowledgeItem.name, KnowledgeItem.id)).all()
        if review_id and not rows:
            raise NotFoundError("没有找到这条记录关联的复习")
        ids = [r.id for r, _ in rows]
        feedback_query = select(
            ReviewFeedback.id,
            ReviewFeedback.review_item_id,
            ReviewFeedback.action,
            ReviewFeedback.occurred_at,
            func.row_number()
            .over(
                partition_by=ReviewFeedback.review_item_id,
                order_by=(ReviewFeedback.occurred_at.desc(), ReviewFeedback.id.desc()),
            )
            .label("rank"),
        ).where(ReviewFeedback.family_id == family_id, ReviewFeedback.review_item_id.in_(ids))
        if before:
            anchor = (
                db.scalar(
                    select(ReviewFeedback).where(
                        ReviewFeedback.id == before,
                        ReviewFeedback.family_id == family_id,
                        ReviewFeedback.review_item_id == review_id,
                    )
                )
                if review_id
                else None
            )
            if anchor is None:
                raise ValueError("反馈分页已失效，请重新展开")
            feedback_query = feedback_query.where(
                or_(
                    ReviewFeedback.occurred_at < anchor.occurred_at,
                    and_(
                        ReviewFeedback.occurred_at == anchor.occurred_at,
                        ReviewFeedback.id < anchor.id,
                    ),
                )
            )
        ranked = feedback_query.subquery()
        feedbacks = (
            db.execute(select(ranked).where(ranked.c.rank <= 4).order_by(ranked.c.rank))
            .mappings()
            .all()
        )
        grouped: dict[str, list] = {}
        for f in feedbacks:
            grouped.setdefault(f["review_item_id"], []).append(
                {
                    "id": f["id"],
                    "action": f["action"],
                    "occurred_at": f["occurred_at"].isoformat(),
                }
            )
        return {
            "items": [
                {
                    "review_id": r.id,
                    "knowledge_id": k.id,
                    "name": k.name,
                    "active": r.active,
                    "due_date": r.due_date.isoformat(),
                    "is_due": r.active and r.due_date <= local_date(),
                    "feedback": grouped.get(r.id, [])[:3],
                    "next_before": grouped[r.id][2]["id"]
                    if len(grouped.get(r.id, [])) > 3
                    else None,
                }
                for r, k in rows
            ]
        }

    @classmethod
    def daily_todos(
        cls, db: Session, family_id: str, child_id: str, day: date | None = None
    ) -> list[dict]:
        child = ChildrenService.get_child(db, family_id, child_id)
        target = day or local_date()
        rows = db.execute(
            select(ReviewItem, KnowledgeItem, Subject, LearningSubmission.occurred_at)
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .outerjoin(
                LearningSubmission,
                and_(
                    LearningSubmission.id == ReviewItem.source_submission_id,
                    LearningSubmission.family_id == family_id,
                    LearningSubmission.child_id == child_id,
                ),
            )
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                ReviewItem.active.is_(True),
                ReviewItem.due_date <= target,
                Subject.kind == "learning",
            )
        ).all()
        review_ids = [review.id for review, _, _, _ in rows]
        last_reviewed: dict[str, date] = {}
        if review_ids:
            for item_id, occurred_at in (
                db.execute(
                    select(
                        ReviewFeedback.review_item_id,
                        func.max(ReviewFeedback.occurred_at),
                    )
                    .where(
                        ReviewFeedback.family_id == family_id,
                        ReviewFeedback.review_item_id.in_(review_ids),
                    )
                    .group_by(ReviewFeedback.review_item_id)
                )
                .tuples()
                .all()
            ):
                if item_id is not None and occurred_at is not None:
                    last_reviewed[item_id] = local_date(occurred_at)
        items = []
        for review, knowledge, subject, source_occurred_at in rows:
            source_occurred_on = (
                local_date(source_occurred_at) if source_occurred_at is not None else None
            )
            items.append(
                DueKnowledge(
                    review_id=review.id,
                    subject_id=subject.id,
                    subject_name=subject.name,
                    knowledge_name=knowledge.name,
                    review_method=knowledge.review_method,
                    estimated_minutes=knowledge.estimated_minutes,
                    due_date=review.due_date,
                    source_submission_id=review.source_submission_id,
                    source_occurred_on=source_occurred_on,
                    review_round=(review.step or 0) + 1,
                    interval_days=review_interval_days(
                        review.due_date, last_reviewed.get(review.id), source_occurred_on
                    ),
                )
            )
        return group_daily_todos(items, child.daily_budget_minutes or 15)

    @classmethod
    def pending_review_loads(cls, db: Session, target: date) -> list[PendingReviewLoad]:
        """Outstanding review per active child across families, for the evening digest.

        Only learning subjects count, matching `daily_todos`; activities never create review debt.
        """
        rows = db.execute(
            select(
                ReviewItem.family_id,
                ReviewItem.child_id,
                Child.name,
                Subject.name,
                func.count(ReviewItem.id),
            )
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .join(Child, ReviewItem.child_id == Child.id)
            .where(
                ReviewItem.active.is_(True),
                ReviewItem.due_date <= target,
                Subject.kind == "learning",
                Child.active.is_(True),
                Child.deleting.is_(False),
            )
            .group_by(ReviewItem.family_id, ReviewItem.child_id, Child.name, Subject.name)
            .order_by(func.count(ReviewItem.id).desc(), Subject.name)
        ).all()
        totals: dict[tuple[str, str], PendingReviewLoad] = {}
        for family_id, child_id, child_name, subject_name, count in rows:
            key = (str(family_id), str(child_id))
            current = totals.get(key)
            if current is None:
                totals[key] = PendingReviewLoad(
                    family_id=str(family_id),
                    child_id=str(child_id),
                    child_name=str(child_name),
                    pending_count=int(count or 0),
                    subject_names=(str(subject_name),),
                )
                continue
            totals[key] = PendingReviewLoad(
                family_id=current.family_id,
                child_id=current.child_id,
                child_name=current.child_name,
                pending_count=current.pending_count + int(count or 0),
                subject_names=(*current.subject_names, str(subject_name)),
            )
        return list(totals.values())

    @staticmethod
    def feedback(
        db: Session,
        family_id: str,
        review_id: str,
        action: str,
        idempotency_key: str | None = None,
    ) -> dict:
        # Feedback closes a review item that already exists, so it is scoped by review id and
        # family only. An archived profile keeps accepting feedback on purpose (`BHV-025`);
        # the deterministic planner never creates new review items here.
        review = db.scalar(
            select(ReviewItem)
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .where(
                ReviewItem.id == review_id,
                ReviewItem.family_id == family_id,
                Subject.kind == "learning",
            )
            .with_for_update()
        )
        if review is None:
            raise NotFoundError("没有找到这条复习任务")
        if idempotency_key:
            existing = db.scalar(
                select(ReviewFeedbackRequest).where(
                    ReviewFeedbackRequest.family_id == family_id,
                    ReviewFeedbackRequest.idempotency_key == idempotency_key,
                )
            )
            if existing is not None:
                if existing.review_item_id != review_id or existing.action != action:
                    raise ConflictError("此反馈标识已用于不同操作，请重新操作")
                return PlanningService._feedback_result(existing)
        if not review.active:
            raise ConflictError("这条复习已结束，请刷新列表后再操作")
        transition = apply_feedback(review.step, action, local_date())  # type: ignore[arg-type]
        review.step = transition.step
        review.due_date = transition.due_date
        review.active = transition.active
        review.last_feedback = action
        db.add(ReviewFeedback(family_id=family_id, review_item_id=review.id, action=action))
        if idempotency_key:
            db.add(
                ReviewFeedbackRequest(
                    family_id=family_id,
                    idempotency_key=idempotency_key,
                    review_item_id=review.id,
                    action=action,
                    result_step=review.step,
                    result_due_date=review.due_date,
                    result_active=review.active,
                )
            )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if not idempotency_key:
                raise
            existing = db.scalar(
                select(ReviewFeedbackRequest).where(
                    ReviewFeedbackRequest.family_id == family_id,
                    ReviewFeedbackRequest.idempotency_key == idempotency_key,
                )
            )
            if existing is None:
                raise
            if existing.review_item_id != review_id or existing.action != action:
                raise ConflictError("此反馈标识已用于不同操作，请重新操作") from None
            return PlanningService._feedback_result(existing)
        return {
            "review_id": review.id,
            "action": action,
            "step": review.step,
            "due_date": review.due_date.isoformat(),
            "active": review.active,
        }

    @staticmethod
    def _feedback_result(request: ReviewFeedbackRequest) -> dict:
        if request.result_due_date is None:
            raise RuntimeError("feedback request has no stored due date")
        return {
            "review_id": request.review_item_id,
            "action": request.action,
            "step": request.result_step,
            "due_date": request.result_due_date.isoformat(),
            "active": request.result_active,
        }

    @staticmethod
    def practice_materials(
        db: Session,
        family_id: str,
        child_id: str,
        limit: int = 5,
        review_ids: list[str] | None = None,
    ) -> dict:
        ChildrenService.get_child(db, family_id, child_id)
        query = (
            select(KnowledgeItem, Subject)
            .join(ReviewItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .where(
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                ReviewItem.active.is_(True),
                Subject.kind == "learning",
            )
            .order_by(ReviewItem.due_date)
            .limit(limit)
        )
        if review_ids:
            query = query.where(ReviewItem.id.in_(review_ids))
        rows = db.execute(query).all()
        prompts = []
        for knowledge, subject in rows:
            prompt = {
                "数学": f"请孩子不用看答案，讲一讲“{knowledge.name}”，再做一道同类例题。",
                "英语": f"请孩子听、说、读、拼“{knowledge.name}”，家长只提示不代答。",
                "语文": f"请孩子认读或听写“{knowledge.name}”，再用自己的话解释。",
            }.get(subject.name, f"请孩子用自己的话回顾“{knowledge.name}”。")
            prompts.append(
                {"subject_name": subject.name, "knowledge_name": knowledge.name, "prompt": prompt}
            )
        return {
            "title": "今天的家长带练清单",
            "items": prompts,
            "disclaimer": "用于提示复习，不自动判分。",
        }
