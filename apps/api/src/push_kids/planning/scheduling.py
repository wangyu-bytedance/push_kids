"""Transactional parent arrangements; deliberately separate from review feedback."""

import json
from datetime import date, timedelta
from hashlib import sha256
from typing import Literal

from sqlalchemy import case, func, select, update
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    DailyReviewPlanItem,
    KnowledgeItem,
    ReviewItem,
    ReviewScheduleChange,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.domain import parent_schedule_date
from push_kids.planning.inventory import preview_reviews
from push_kids.planning.queue_state import record_offered, reset_queue
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import local_date


class ScheduleDayChanged(ConflictError):
    code = "day_changed"


def refresh_future_due_stats(db: Session, family_id: str, child_id: str, from_day: date) -> None:
    """Keep materialized due/backlog summaries aligned after a manual date change."""
    due_scope = (
        ReviewItem.family_id == family_id,
        ReviewItem.child_id == child_id,
        ReviewItem.active.is_(True),
        ReviewItem.due_date <= DailyReviewPlan.plan_date,
        Subject.kind == "learning",
        Subject.active.is_(True),
    )
    due_stats = (
        select(func.count(ReviewItem.id), func.min(ReviewItem.due_date))
        .select_from(ReviewItem)
        .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
        .join(Subject, Subject.id == KnowledgeItem.subject_id)
        .where(*due_scope)
        .correlate(DailyReviewPlan)
    )
    db.execute(
        update(DailyReviewPlan)
        .where(
            DailyReviewPlan.family_id == family_id,
            DailyReviewPlan.child_id == child_id,
            DailyReviewPlan.plan_date >= from_day,
        )
        .values(
            due_count=due_stats.with_only_columns(func.count(ReviewItem.id)).scalar_subquery(),
            earliest_due=due_stats.with_only_columns(
                func.min(ReviewItem.due_date)
            ).scalar_subquery(),
        )
        .execution_options(synchronize_session=False)
    )


def withdraw_pending(
    db: Session, family_id: str, child_id: str, review_id: str, from_day: date
) -> None:
    """Remove only this review from affected snapshots, without refilling any slots."""
    link = (
        select(DailyReviewPlanItem.id)
        .where(
            DailyReviewPlanItem.plan_id == DailyReviewPlan.id,
            DailyReviewPlanItem.family_id == family_id,
            DailyReviewPlanItem.child_id == child_id,
            DailyReviewPlanItem.review_item_id == review_id,
            DailyReviewPlanItem.state == "pending",
        )
        .correlate(DailyReviewPlan)
    )
    minutes = (
        select(DailyReviewPlanItem.estimated_minutes)
        .where(
            DailyReviewPlanItem.plan_id == DailyReviewPlan.id,
            DailyReviewPlanItem.family_id == family_id,
            DailyReviewPlanItem.review_item_id == review_id,
        )
        .correlate(DailyReviewPlan)
        .scalar_subquery()
    )
    db.execute(
        update(DailyReviewPlan)
        .where(
            DailyReviewPlan.family_id == family_id,
            DailyReviewPlan.child_id == child_id,
            DailyReviewPlan.plan_date >= from_day,
            link.exists(),
        )
        .values(
            due_count=case((DailyReviewPlan.due_count > 0, DailyReviewPlan.due_count - 1), else_=0),
            total_minutes=case(
                (DailyReviewPlan.total_minutes >= minutes, DailyReviewPlan.total_minutes - minutes),
                else_=0,
            ),
        )
        .execution_options(synchronize_session=False)
    )
    plan_ids = select(DailyReviewPlan.id).where(
        DailyReviewPlan.family_id == family_id,
        DailyReviewPlan.child_id == child_id,
        DailyReviewPlan.plan_date >= from_day,
    )
    db.execute(
        update(DailyReviewPlanItem)
        .where(
            DailyReviewPlanItem.family_id == family_id,
            DailyReviewPlanItem.child_id == child_id,
            DailyReviewPlanItem.review_item_id == review_id,
            DailyReviewPlanItem.state == "pending",
            DailyReviewPlanItem.plan_id.in_(plan_ids),
        )
        .values(state="rescheduled")
        .execution_options(synchronize_session=False)
    )


def consume_arrangement(
    db: Session, family_id: str, review: ReviewItem, reviewed_on: date, action: str
) -> Literal["none", "preserve", "consumed"]:
    """Separate historical/deferred events from actual consumption of a reservation."""
    override = db.scalar(
        select(ReviewScheduleOverride)
        .where(
            ReviewScheduleOverride.family_id == family_id,
            ReviewScheduleOverride.review_item_id == review.id,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if override is None:
        return "none"
    if action == "defer":
        return "preserve"
    if override.requested_on and reviewed_on < override.requested_on:
        return "preserve"
    db.delete(override)
    withdraw_pending(
        db, family_id, str(review.child_id), str(review.id), reviewed_on + timedelta(days=1)
    )
    return "consumed"


def schedule_review(
    db: Session,
    family_id: str,
    child_id: str,
    review_id: str,
    *,
    action: str,
    base_day: date,
    expected_version: int,
    idempotency_key: str,
) -> dict:
    child = db.scalar(
        select(Child)
        .where(Child.id == child_id, Child.family_id == family_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    ChildrenService.require_active_child(db, family_id, child_id)
    if child is None:
        raise NotFoundError("没有找到这个孩子")
    fingerprint = sha256(
        json.dumps([child_id, review_id, action, base_day.isoformat(), expected_version]).encode()
    ).hexdigest()
    prior = db.scalar(
        select(ReviewScheduleChange)
        .where(
            ReviewScheduleChange.family_id == family_id,
            ReviewScheduleChange.idempotency_key == idempotency_key,
        )
        .with_for_update()
    )
    if prior:
        if prior.request_fingerprint != fingerprint:
            raise ConflictError("此操作标识已用于不同安排")
        return json.loads(str(prior.result_json))
    today = local_date()
    if base_day != today:
        raise ScheduleDayChanged("日期已变化，请重新查看明天的安排")
    review = db.scalar(
        select(ReviewItem)
        .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
        .join(Subject, Subject.id == KnowledgeItem.subject_id)
        .where(
            ReviewItem.id == review_id,
            ReviewItem.family_id == family_id,
            ReviewItem.child_id == child_id,
            KnowledgeItem.family_id == family_id,
            KnowledgeItem.child_id == child_id,
            Subject.family_id == family_id,
            Subject.child_id == child_id,
            Subject.kind == "learning",
            Subject.active.is_(True),
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if review is None:
        raise NotFoundError("没有找到这条复习安排")
    if review.state_version != expected_version:
        raise ConflictError("这条安排已发生变化，请重新加载")
    assert review.due_date is not None
    effective_due = review.due_date
    if action == "day_after":
        if review.id not in preview_reviews(db, family_id, child, 1, lock=True):
            raise ConflictError("仅明天计划中的条目可改到后天")
        effective_due = today + timedelta(days=1)
    try:
        target = parent_schedule_date(today, action, effective_due)
    except ValueError as exc:
        raise ConflictError(str(exc)) from exc
    override = db.scalar(
        select(ReviewScheduleOverride)
        .where(
            ReviewScheduleOverride.review_item_id == review_id,
            ReviewScheduleOverride.family_id == family_id,
        )
        .with_for_update()
    )
    before_due, before_version = review.due_date, int(review.state_version)
    changed = not (override and override.scheduled_on == target and review.active)
    if changed:
        reservations = int(
            db.scalar(
                select(func.count())
                .select_from(ReviewScheduleOverride)
                .where(
                    ReviewScheduleOverride.family_id == family_id,
                    ReviewScheduleOverride.child_id == child_id,
                    ReviewScheduleOverride.scheduled_on <= target,
                    ReviewScheduleOverride.review_item_id != review_id,
                )
                .with_for_update()
            )
            or 0
        )
        if reservations >= 120:
            raise ConflictError("手动安排已达120项上限，请先调整已有安排")
        target_plan = db.scalar(
            select(DailyReviewPlan)
            .where(
                DailyReviewPlan.family_id == family_id,
                DailyReviewPlan.child_id == child_id,
                DailyReviewPlan.plan_date == target,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if target_plan:
            used = db.scalar(
                select(func.count())
                .select_from(DailyReviewPlanItem)
                .where(
                    DailyReviewPlanItem.plan_id == target_plan.id,
                    DailyReviewPlanItem.family_id == family_id,
                    DailyReviewPlanItem.state != "rescheduled",
                    DailyReviewPlanItem.review_item_id != review_id,
                )
                .with_for_update()
            )
            if int(used or 0) >= 120:
                raise ConflictError("这一天的计划已达120项上限")
        withdraw_pending(db, family_id, child_id, review_id, today)
        if not review.active:
            review.step = 0
        review.active = True
        review.due_date = target
        reset_queue(review, target)
        review.state_version += 1
        if override is None:
            override = ReviewScheduleOverride(
                review_item_id=review_id,
                family_id=family_id,
                child_id=child_id,
                scheduled_on=target,
                requested_on=today,
            )
            db.add(override)
        else:
            override.scheduled_on, override.requested_on = target, today
        if target_plan:
            knowledge = db.get(KnowledgeItem, review.knowledge_item_id)
            assert knowledge is not None
            minutes = min(5, max(1, int(knowledge.estimated_minutes or 1)))
            item = db.scalar(
                select(DailyReviewPlanItem)
                .where(
                    DailyReviewPlanItem.plan_id == target_plan.id,
                    DailyReviewPlanItem.review_item_id == review_id,
                    DailyReviewPlanItem.family_id == family_id,
                )
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if item is None:
                ordinal = (
                    int(
                        db.scalar(
                            select(func.max(DailyReviewPlanItem.ordinal))
                            .where(DailyReviewPlanItem.plan_id == target_plan.id)
                            .with_for_update()
                        )
                        or 0
                    )
                    + 1
                )
                db.add(
                    DailyReviewPlanItem(
                        family_id=family_id,
                        child_id=child_id,
                        plan_id=target_plan.id,
                        review_item_id=review_id,
                        ordinal=ordinal,
                        estimated_minutes=minutes,
                    )
                )
            else:
                item.state = "pending"
            # Refresh after SQL withdrawal; avoid writing a stale total from the identity map.
            db.refresh(target_plan, with_for_update=True)
            target_plan.total_minutes = int(target_plan.total_minutes or 0) + minutes
            record_offered(db, family_id, child_id, [review_id], target)
        db.flush()
        # A due item may have been outside the plan's minute budget, so removing
        # only selected rows cannot maintain its due/backlog total. Recount every
        # existing future summary while leaving the selected snapshot unchanged.
        refresh_future_due_stats(db, family_id, child_id, today)
        ChildrenService.invalidate_review_inventory(db, family_id, child_id)
        db.flush()
    planned = preview_reviews(db, family_id, child, (target - today).days, lock=True)
    minutes = int(
        db.scalar(
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (KnowledgeItem.estimated_minutes < 1, 1),
                            (KnowledgeItem.estimated_minutes > 5, 5),
                            else_=KnowledgeItem.estimated_minutes,
                        )
                    ),
                    0,
                )
            )
            .select_from(ReviewItem)
            .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                ReviewItem.id.in_(planned),
            )
            .with_for_update()
        )
        or 0
    )
    result = {
        "review_id": review_id,
        "before_due_date": before_due.isoformat(),
        "due_date": target.isoformat(),
        "state_version": int(review.state_version),
        "review_count": int(review.review_count or 0),
        "manually_scheduled": True,
        "planned_minutes": minutes,
        "budget_minutes": int(child.daily_budget_minutes or 0),
        "over_budget_minutes": max(0, minutes - int(child.daily_budget_minutes or 0)),
    }
    db.add(
        ReviewScheduleChange(
            family_id=family_id,
            child_id=child_id,
            review_item_id=review_id,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            action=action,
            before_due_date=before_due,
            after_due_date=target,
            before_version=before_version,
            after_version=review.state_version,
            result_json=json.dumps(result),
        )
    )
    db.commit()
    return result
