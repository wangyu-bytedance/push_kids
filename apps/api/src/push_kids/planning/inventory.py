"""Scoped, cursor-paged review inventory. Reading previews never creates a daily plan."""

from datetime import timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    DailyReviewPlanItem,
    KnowledgeItem,
    ReviewItem,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.early_candidates import select_early_reviews
from push_kids.planning.eligibility import scheduling_eligible
from push_kids.planning.plan_candidates import selected_candidates
from push_kids.planning.queue_state import missed_days, recent_plan_days
from push_kids.platform.errors import AppError, ConflictError, NotFoundError
from push_kids.platform.pagination import decode_cursor, encode_cursor
from push_kids.platform.time import local_date


class InventoryChanged(ConflictError):
    code = "cursor_stale"


def cursor_anchor(cursor: str | None, scope: list, revision: int) -> dict:
    if not cursor:
        return {}
    try:
        anchor = decode_cursor(cursor, scope)
        if not isinstance(anchor.get("revision"), int):
            raise ValueError
    except ValueError as exc:
        raise AppError("分页参数无效，请重新加载") from exc
    if anchor["revision"] != revision:
        raise InventoryChanged("条目已有变化，请重新加载")
    return anchor


def preview_reviews(
    db: Session, family_id: str, child: Child, offset: int, *, lock: bool = False
) -> list[str]:
    """Two sequential dry runs; tomorrow's projected selection is not duplicated on day two."""
    previous: tuple[str, ...] = ()
    selected: list[str] = []
    projected_days: list = []
    projected_subject_offers = {}
    for day_offset in range(1, offset + 1):
        target = local_date() + timedelta(days=day_offset)
        plan_query = select(DailyReviewPlan.id).where(
            DailyReviewPlan.family_id == family_id,
            DailyReviewPlan.child_id == child.id,
            DailyReviewPlan.plan_date == target,
        )
        plan = db.scalar(plan_query.with_for_update() if lock else plan_query)
        if plan:
            item_query = (
                select(DailyReviewPlanItem.review_item_id, KnowledgeItem.subject_id)
                .join(ReviewItem, ReviewItem.id == DailyReviewPlanItem.review_item_id)
                .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
                .where(
                    DailyReviewPlanItem.family_id == family_id,
                    DailyReviewPlanItem.child_id == child.id,
                    DailyReviewPlanItem.plan_id == plan,
                    DailyReviewPlanItem.state == "pending",
                    ReviewItem.family_id == family_id,
                    ReviewItem.child_id == child.id,
                    KnowledgeItem.family_id == family_id,
                    KnowledgeItem.child_id == child.id,
                    scheduling_eligible(),
                )
                .order_by(DailyReviewPlanItem.ordinal, DailyReviewPlanItem.id)
                .limit(120)
            )
            rows = list(db.execute(item_query.with_for_update() if lock else item_query))
            selected = [rid for rid, _ in rows]
            projected_subject_offers.update({sid: target for _, sid in rows})
        else:
            candidates = selected_candidates(
                db,
                family_id,
                str(child.id),
                target,
                int(child.daily_budget_minutes or 0),
                exclude=previous,
                lock=lock,
                projected_days=tuple(projected_days),
                projected_subject_offers=projected_subject_offers,
            )
            if not candidates and db.info.get("empty_day_early_review_enabled", False):
                due_exists = db.scalar(
                    select(ReviewItem.id)
                    .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
                    .join(Subject, Subject.id == KnowledgeItem.subject_id)
                    .where(
                        ReviewItem.family_id == family_id,
                        ReviewItem.child_id == child.id,
                        ReviewItem.active.is_(True),
                        ReviewItem.id.not_in(previous),
                        ReviewItem.due_date <= target,
                        Subject.active.is_(True),
                        Subject.kind == "learning",
                        scheduling_eligible(),
                    )
                    .limit(1)
                )
                if not due_exists:
                    candidates = select_early_reviews(
                        db,
                        family_id,
                        str(child.id),
                        target,
                        int(child.daily_budget_minutes or 0),
                        exclude=previous,
                        lock=lock,
                        projected_subject_offers=projected_subject_offers,
                    )
            selected = [c.review_id for c in candidates]
            projected_subject_offers.update({c.subject_id: target for c in candidates})
        previous = tuple(selected)
        projected_days.append(target)
    return selected


def subjects_page(
    db: Session,
    family_id: str,
    child_id: str,
    *,
    cursor: str | None = None,
    limit: int = 20,
    review_status: str = "normal",
) -> dict:
    child = ChildrenService.get_child(db, family_id, child_id)
    revision = int(child.review_inventory_revision or 0)
    limit = max(1, min(50, limit))
    scope = ["review-subjects", family_id, child_id, review_status]
    anchor = cursor_anchor(cursor, scope, revision)
    query = select(Subject).where(
        Subject.family_id == family_id, Subject.child_id == child_id, Subject.kind == "learning"
    )
    if anchor:
        if not isinstance(anchor.get("id"), str):
            raise AppError("分页参数无效")
        query = query.where(Subject.id > anchor["id"])
    rows = list(db.scalars(query.order_by(Subject.id).limit(min(50, limit) + 1)))
    page = rows[:limit]
    counts = {
        subject: count
        for subject, count in db.execute(
            select(KnowledgeItem.subject_id, func.count())
            .where(
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                KnowledgeItem.subject_id.in_([s.id for s in page]),
                KnowledgeItem.review_status == review_status,
            )
            .group_by(KnowledgeItem.subject_id)
        ).all()
    }
    return {
        "items": [
            {"id": s.id, "name": s.name, "active": bool(s.active), "count": counts.get(s.id, 0)}
            for s in page
        ],
        "revision": revision,
        "next_cursor": encode_cursor(
            scope,
            {
                "revision": revision,
                "id": page[-1].id,
            },
        )
        if len(rows) > limit
        else None,
    }


def inventory_page(
    db: Session,
    family_id: str,
    child_id: str,
    *,
    view: str = "time",
    review_status: str = "normal",
    offset: int = 1,
    subject_id: str | None = None,
    review_count: int | None = None,
    cursor: str | None = None,
    limit: int = 20,
) -> dict:
    child = ChildrenService.get_child(db, family_id, child_id)
    if review_status not in {"normal", "superseded"}:
        raise AppError("无效的词条状态")
    if review_status == "superseded" and view == "time":
        view = "count"
    if view == "subject" and not subject_id:
        raise AppError("请选择一个科目")
    if review_count is not None and view != "count":
        raise AppError("次数条件仅用于按次数查看")
    if subject_id and (
        view != "subject"
        or not db.scalar(
            select(Subject.id).where(
                Subject.id == subject_id,
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.kind == "learning",
            )
        )
    ):
        raise NotFoundError("没有找到这个科目")
    today = local_date()
    revision = int(child.review_inventory_revision or 0)
    limit = max(1, min(50, limit))
    scope = [
        "review-inventory",
        family_id,
        child_id,
        view,
        offset,
        subject_id,
        review_count,
        today,
        review_status,
    ]
    anchor = cursor_anchor(cursor, scope, revision)
    conditions = [
        KnowledgeItem.family_id == family_id,
        KnowledgeItem.child_id == child_id,
        KnowledgeItem.review_status == review_status,
        Subject.family_id == family_id,
        Subject.child_id == child_id,
        Subject.kind == "learning",
    ]
    if subject_id:
        conditions.append(KnowledgeItem.subject_id == subject_id)
    if review_count is not None:
        conditions.append(ReviewItem.review_count == review_count)
    ids = preview_reviews(db, family_id, child, offset) if view == "time" else []
    if view == "time":
        conditions.append(ReviewItem.id.in_(ids))
    # Missing legacy Review is explicitly unknown, sorted after known counts.
    count_key = func.coalesce(ReviewItem.review_count, 2147483648)
    query = (
        select(KnowledgeItem, ReviewItem, Subject, ReviewScheduleOverride.scheduled_on)
        .join(Subject, Subject.id == KnowledgeItem.subject_id)
        .outerjoin(
            ReviewItem,
            and_(
                ReviewItem.knowledge_item_id == KnowledgeItem.id,
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
            ),
        )
        .outerjoin(
            ReviewScheduleOverride,
            and_(
                ReviewScheduleOverride.review_item_id == ReviewItem.id,
                ReviewScheduleOverride.family_id == family_id,
                ReviewScheduleOverride.child_id == child_id,
            ),
        )
        .where(*conditions)
    )
    total = int(db.scalar(select(func.count()).select_from(query.subquery())) or 0)
    summary = {}
    if view == "time":
        # The plan is domain-capped at 120; reuse its order and exact bounded totals.
        all_rows = list(db.execute(query.limit(120)))
        order = {rid: index for index, rid in enumerate(ids)}
        all_rows.sort(key=lambda row: order[row[1].id])
        start = anchor.get("position", 0)
        if not isinstance(start, int) or not 0 <= start <= 120:
            raise AppError("分页参数无效")
        rows = all_rows[start : start + limit + 1]
        budget = int(child.daily_budget_minutes or 0)
        minutes = sum(min(5, max(1, k.estimated_minutes)) for k, _, _, _ in all_rows)
        summary = {
            "planned_minutes": minutes,
            "budget_minutes": budget,
            "over_budget_minutes": max(0, minutes - budget),
            "manual_minutes": sum(
                min(5, max(1, k.estimated_minutes)) for k, _, _, m in all_rows if m
            ),
            "plan_date": (today + timedelta(days=offset)).isoformat(),
        }
        next_anchor = {"revision": revision, "position": start + limit}
    else:
        if anchor:
            if not isinstance(anchor.get("count"), int) or not isinstance(anchor.get("id"), str):
                raise AppError("分页参数无效")
            query = query.where(
                or_(
                    count_key > anchor["count"],
                    and_(count_key == anchor["count"], KnowledgeItem.id > anchor["id"]),
                )
            )
        rows = list(db.execute(query.order_by(count_key, KnowledgeItem.id).limit(limit + 1)))
        next_anchor = {"revision": revision}
        if rows[:limit]:
            k, r, _, _ = rows[:limit][-1]
            next_anchor.update(count=int(r.review_count) if r else 2147483648, id=k.id)
    tomorrow = (
        set(ids if view == "time" and offset == 1 else preview_reviews(db, family_id, child, 1))
        if review_status == "normal"
        else set()
    )
    today_plan = (
        db.scalar(
            select(DailyReviewPlan.id).where(
                DailyReviewPlan.family_id == family_id,
                DailyReviewPlan.child_id == child_id,
                DailyReviewPlan.plan_date == today,
            )
        )
        if review_status == "normal"
        else None
    )
    today_states = (
        {
            str(rid): (str(state), kind, original)
            for rid, state, kind, original in db.execute(
                select(
                    DailyReviewPlanItem.review_item_id,
                    DailyReviewPlanItem.state,
                    DailyReviewPlanItem.selection_kind,
                    DailyReviewPlanItem.original_due_date,
                )
                .where(
                    DailyReviewPlanItem.family_id == family_id,
                    DailyReviewPlanItem.child_id == child_id,
                    DailyReviewPlanItem.plan_id == today_plan,
                    DailyReviewPlanItem.state != "rescheduled",
                )
                .limit(120)
            ).all()
        }
        if today_plan
        else {}
    )
    days = (
        recent_plan_days(db, family_id, child_id, today + timedelta(days=1))
        if review_status == "normal"
        else []
    )

    def arrangement(r, s, manual):
        if not r or not child.active or child.deleting or not s.active:
            return "unavailable"
        state = today_states.get(r.id, (None, None, None))[0]
        if state in {"complete", "partial", "reinforce"}:
            return "reviewed_today"
        if state == "deferred":
            return "deferred_today"
        if state == "pending":
            return "scheduled_today"
        if not r.active:
            return "unavailable"
        if manual:
            return "reserved"
        if r.due_date > today:
            return "not_due"
        return "waiting" if today_plan else "awaiting_daily_plan"

    covering = aliased(KnowledgeItem)
    covering_ids = [
        k.superseded_by_knowledge_id for k, _, _, _ in rows[:limit] if k.superseded_by_knowledge_id
    ]
    covering_names = (
        {
            str(kid): str(name)
            for kid, name in db.execute(
                select(covering.id, covering.name)
                .where(
                    covering.family_id == family_id,
                    covering.child_id == child_id,
                    covering.id.in_(covering_ids),
                )
                .limit(limit)
            ).tuples()
        }
        if covering_ids
        else {}
    )
    items = [
        {
            "knowledge_id": k.id,
            "review_status": k.review_status,
            "superseded_by_knowledge_id": k.superseded_by_knowledge_id,
            "superseded_by_name": covering_names.get(k.superseded_by_knowledge_id),
            "source_submission_id": r.source_submission_id if r else None,
            "knowledge_name": k.name,
            "subject_id": s.id,
            "subject_name": s.name,
            "review_id": r.id if r else None,
            "review_count": int(r.review_count) if r else None,
            "selection_kind": (
                today_states[r.id][1]
                if r and r.id in today_states
                else (
                    "early"
                    if r and view == "time" and r.due_date > today + timedelta(days=offset)
                    else "due"
                )
            ),
            "original_due_date": (
                today_states[r.id][2].isoformat()
                if r and r.id in today_states and today_states[r.id][2]
                else (
                    r.due_date.isoformat()
                    if r and view == "time" and r.due_date > today + timedelta(days=offset)
                    else None
                )
            ),
            "last_reviewed_on": r.last_reviewed_on.isoformat()
            if r and r.last_reviewed_on
            else None,
            "due_date": r.due_date.isoformat() if r and r.active else None,
            "suggested_review_on": r.due_date.isoformat() if r and r.active and m is None else None,
            "scheduled_on": m.isoformat() if m else None,
            "arrangement_state": "superseded"
            if k.review_status == "superseded"
            else arrangement(r, s, m),
            "missed_plan_days": missed_days(
                r,
                days,
                resumed_on=max(
                    child.review_queue_resumed_on or today.min,
                    s.review_queue_resumed_on or today.min,
                ),
            )
            if k.review_status == "normal"
            and r
            and r.active
            and s.active
            and child.active
            and not m
            else 0,
            "active": bool(r.active) if r else False,
            "state_version": int(r.state_version) if r else None,
            "manually_scheduled": m is not None,
            "in_tomorrow_plan": bool(r and r.id in tomorrow),
            "can_schedule": bool(
                k.review_status == "normal"
                and r
                and s.active
                and child.active
                and not child.deleting
            ),
            "estimated_minutes": min(5, max(1, k.estimated_minutes)),
        }
        for k, r, s, m in rows[:limit]
    ]
    return {
        "as_of_day": today.isoformat(),
        "revision": revision,
        "items": items,
        "total": total,
        "sort": "review_count_asc" if view != "time" else "plan_order",
        "child_writable": bool(child.active and not child.deleting),
        "next_cursor": encode_cursor(scope, next_anchor) if len(rows) > limit else None,
        **summary,
    }
