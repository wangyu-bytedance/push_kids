from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    KnowledgeItem,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
    Subject,
)
from push_kids.planning.domain import DueKnowledge, apply_feedback, group_daily_todos
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import local_date


class PlanningService:
    @classmethod
    def daily_todos(
        cls, db: Session, family_id: str, child_id: str, day: date | None = None
    ) -> list[dict]:
        child = ChildrenService.get_child(db, family_id, child_id)
        target = day or local_date()
        rows = db.execute(
            select(ReviewItem, KnowledgeItem, Subject)
            .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .join(Subject, KnowledgeItem.subject_id == Subject.id)
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                ReviewItem.active.is_(True),
                ReviewItem.due_date <= target,
            )
        ).all()
        items = [
            DueKnowledge(
                review_id=review.id,
                subject_id=subject.id,
                subject_name=subject.name,
                knowledge_name=knowledge.name,
                review_method=knowledge.review_method,
                estimated_minutes=knowledge.estimated_minutes,
                due_date=review.due_date,
            )
            for review, knowledge, subject in rows
        ]
        return group_daily_todos(items, child.daily_budget_minutes or 15)

    @staticmethod
    def feedback(
        db: Session,
        family_id: str,
        review_id: str,
        action: str,
        idempotency_key: str | None = None,
    ) -> dict:
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
        review = db.scalar(
            select(ReviewItem).where(ReviewItem.id == review_id, ReviewItem.family_id == family_id)
        )
        if review is None:
            raise NotFoundError("没有找到这条复习任务")
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
