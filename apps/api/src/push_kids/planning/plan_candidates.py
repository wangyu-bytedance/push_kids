"""Bounded, subject-aware candidates shared by previews and materialized plans."""

from datetime import date

from sqlalchemy import (
    Date,
    String,
    and_,
    case,
    cast,
    func,
    literal,
    select,
    text,
    type_coerce,
    union_all,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from push_kids.persistence.models import (
    Child,
    KnowledgeItem,
    ReviewItem,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.queue_state import recent_plan_days
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


def subject_offers(family_id: str, child_id: str, *, lock: bool):
    query = (
        select(
            KnowledgeItem.subject_id.label("sid"),
            func.max(ReviewItem.last_offered_on).label("served"),
        )
        .join(
            ReviewItem,
            and_(
                ReviewItem.knowledge_item_id == KnowledgeItem.id,
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
            ),
        )
        .where(KnowledgeItem.family_id == family_id, KnowledgeItem.child_id == child_id)
        .where(ReviewItem.last_offered_on.is_not(None))
        .group_by(KnowledgeItem.subject_id)
    )
    return (query.with_for_update() if lock else query).subquery()


def candidate_projection(
    db: Session,
    family_id: str,
    child_id: str,
    target: date,
    *,
    exclude: tuple[str, ...] = (),
    lock: bool = False,
    projected_days: tuple[date, ...] = (),
    actual_days: tuple[date, ...] = (),
    minutes_filter: int | None = None,
    repeated_filter: int | None = None,
    review_ids: set[str] | None = None,
):
    """SQL keeps the full eligible set; Python receives only bounded winners."""
    days = sorted(
        set(actual_days) | {d for d in projected_days if d < target},
        reverse=True,
    )[:3]
    r, k, s = ReviewItem, KnowledgeItem, Subject
    after_offer = (
        func.date_add(r.last_offered_on, text("INTERVAL 1 DAY"))
        if db.get_bind().dialect.name == "mysql"
        else func.date(r.last_offered_on, "+1 day")
    )
    later = func.greatest if db.get_bind().dialect.name == "mysql" else func.max
    anchor = type_coerce(
        later(
            r.due_date,
            *[
                func.coalesce(value, r.due_date)
                for value in (
                    r.queue_eligible_on,
                    s.review_queue_resumed_on,
                    Child.review_queue_resumed_on,
                    type_coerce(after_offer, Date),
                )
            ],
        ),
        Date,
    )
    score: ColumnElement[int] = literal(0)
    for day in days:
        score = score + case((anchor <= day, 1), else_=0)
    minutes = case(
        (k.estimated_minutes < 1, 1), (k.estimated_minutes > 5, 5), else_=k.estimated_minutes
    )
    # Fixed-width ISO dates and unique ID make MIN(key) a portable total order.
    priority = (
        cast(3 - score, String)
        + cast(anchor, String)
        + cast(r.due_date, String)
        + func.coalesce(cast(r.last_reviewed_on, String), "0001-01-01")
        + r.id
    )
    if db.get_bind().dialect.name == "mysql":
        # MySQL 5.7 date/number casts otherwise inherit incompatible coercibilities.
        priority = cast(priority, CHAR(charset="utf8mb4")).collate("utf8mb4_bin")
    query = (
        select(
            r.id.label("rid"),
            k.subject_id.label("sid"),
            minutes.label("minutes"),
            priority.label("priority"),
            anchor.label("anchor"),
            score.label("missed"),
            case((r.review_count > 0, 1), else_=0).label("repeat"),
            ReviewScheduleOverride.review_item_id.label("manual"),
        )
        .select_from(r)
        .join(k, k.id == r.knowledge_item_id)
        .join(s, s.id == k.subject_id)
        .join(Child, Child.id == r.child_id)
        .outerjoin(
            ReviewScheduleOverride,
            and_(
                ReviewScheduleOverride.review_item_id == r.id,
                ReviewScheduleOverride.family_id == family_id,
                ReviewScheduleOverride.child_id == child_id,
            ),
        )
        .where(
            r.family_id == family_id,
            r.child_id == child_id,
            k.family_id == family_id,
            k.child_id == child_id,
            s.family_id == family_id,
            s.child_id == child_id,
            Child.family_id == family_id,
            Child.active.is_(True),
            Child.deleting.is_(False),
            s.kind == "learning",
            s.active.is_(True),
            r.active.is_(True),
            r.due_date <= target,
            r.id.not_in(exclude),
        )
    )
    if lock:
        query = query.with_for_update()
    if review_ids is not None:
        query = query.where(r.id.in_(review_ids))
    if minutes_filter is not None:
        query = query.where(
            k.estimated_minutes <= 1
            if minutes_filter == 1
            else k.estimated_minutes >= 5
            if minutes_filter == 5
            else k.estimated_minutes == minutes_filter
        )
    if repeated_filter is not None:
        query = query.where(r.review_count == 0 if repeated_filter == 0 else r.review_count > 0)
    return query.subquery()


def load_candidates(
    db: Session,
    family_id: str,
    child_id: str,
    target: date,
    *,
    exclude: tuple[str, ...] = (),
    lock: bool = False,
    projected_days: tuple[date, ...] = (),
    projected_subject_offers: dict[str, date] | None = None,
) -> list[ReviewSelectionCandidate]:
    actual_days = tuple(recent_plan_days(db, family_id, child_id, target, lock=lock))
    base = candidate_projection(
        db,
        family_id,
        child_id,
        target,
        exclude=exclude,
        lock=lock,
        projected_days=projected_days,
        actual_days=actual_days,
    )
    automatic = select(base).where(base.c.manual.is_(None)).subquery()
    served = subject_offers(family_id, child_id, lock=lock)
    offered = served.c.served
    subject_totals = (
        select(
            automatic.c.sid,
            func.max(automatic.c.missed).label("missed"),
            func.min(automatic.c.anchor).label("anchor"),
        )
        .group_by(automatic.c.sid)
        .subquery()
    )
    if projected_subject_offers:
        projected = case(
            projected_subject_offers, value=subject_totals.c.sid, else_=served.c.served
        )
        offered = case((served.c.served > projected, served.c.served), else_=projected)
    groups = (
        select(subject_totals.c.sid)
        .outerjoin(served, served.c.sid == subject_totals.c.sid)
        .order_by(
            offered,
            subject_totals.c.missed.desc(),
            subject_totals.c.anchor,
            subject_totals.c.sid,
        )
        .limit(120)
    )
    subject_ids = list(db.scalars(groups))
    coverage_ids = (
        select(func.substr(func.min(automatic.c.priority), 32))
        .where(automatic.c.sid.in_(subject_ids))
        .group_by(automatic.c.sid, automatic.c.minutes)
        .limit(600)
    )
    ids = set(db.scalars(coverage_ids))
    # One UNION query, not one round-trip per subject. Caps derive from 120 minutes.
    pools = []
    for repeated in (0, 1):
        for minutes in range(1, 6):
            minute_base = candidate_projection(
                db,
                family_id,
                child_id,
                target,
                exclude=exclude,
                lock=lock,
                projected_days=projected_days,
                minutes_filter=minutes,
                actual_days=actual_days,
                repeated_filter=repeated,
            )
            bucket = (
                select(minute_base.c.rid)
                .where(minute_base.c.manual.is_(None))
                .order_by(minute_base.c.priority)
                .limit(120 // minutes)
                .subquery()
            )
            pools.append(select(bucket.c.rid))
    ids.update(db.scalars(union_all(*pools)))
    ids.update(
        db.scalars(
            select(base.c.rid)
            .where(base.c.manual.is_not(None))
            .order_by(base.c.priority)
            .limit(120)
        )
    )
    if not ids:
        return []
    base = candidate_projection(
        db,
        family_id,
        child_id,
        target,
        exclude=exclude,
        lock=lock,
        projected_days=projected_days,
        review_ids=ids,
        actual_days=actual_days,
    )
    query = (
        select(
            ReviewItem,
            KnowledgeItem,
            Subject,
            base.c.anchor,
            base.c.missed,
            served.c.served,
            base.c.manual,
        )
        .join(base, base.c.rid == ReviewItem.id)
        .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
        .join(Subject, Subject.id == KnowledgeItem.subject_id)
        .outerjoin(served, served.c.sid == KnowledgeItem.subject_id)
        .where(ReviewItem.id.in_(ids))
        .limit(1268)
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    return [
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
            manually_scheduled=manual is not None,
            review_count=int(r.review_count or 0),
            missed_plan_days=int(missed),
            waiting_since=anchor,
            subject_last_offered_on=max(
                served or date.min,
                (projected_subject_offers or {}).get(s.id, date.min),
            ),
        )
        for r, k, s, anchor, missed, served, manual in db.execute(query)
    ]


def selected_candidates(
    db: Session,
    family_id: str,
    child_id: str,
    target: date,
    budget: int,
    *,
    exclude: tuple[str, ...] = (),
    lock: bool = False,
    projected_days: tuple[date, ...] = (),
    projected_subject_offers: dict[str, date] | None = None,
) -> list[ReviewSelectionCandidate]:
    return select_daily_reviews(
        load_candidates(
            db,
            family_id,
            child_id,
            target,
            exclude=exclude,
            lock=lock,
            projected_days=projected_days,
            projected_subject_offers=projected_subject_offers,
        ),
        budget_minutes=budget,
    )
