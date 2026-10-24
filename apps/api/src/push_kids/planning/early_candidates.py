"""Equality-slot index probes keep empty-day work independent of inventory size."""

from datetime import date
from typing import Any

from sqlalchemy import case, select, union_all
from sqlalchemy.orm import Session

from push_kids.persistence.models import (
    KnowledgeItem,
    ReviewEarlySlot,
    ReviewItem,
    ReviewQueueEntry,
    Subject,
)
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


def select_early_reviews(
    db: Session,
    family_id: str,
    child_id: str,
    target: date,
    budget: int,
    *,
    exclude: tuple[str, ...] = (),
    lock: bool = False,
    projected_subject_offers: dict[str, date] | None = None,
) -> list[ReviewSelectionCandidate]:
    q = ReviewEarlySlot
    scope = (
        q.family_id == family_id,
        q.child_id == child_id,
        q.slot_on == target,
        q.review_item_id.not_in(exclude),
    )

    def current(query):
        return query.with_for_update() if lock else query

    first = current(
        select(q.priority_key)
        .where(*scope, q.subject_id == Subject.id)
        .order_by(q.priority_key)
        .limit(1)
        .correlate(Subject)
    ).scalar_subquery()
    historical_offer = current(
        select(ReviewQueueEntry.last_offered_on)
        .where(
            ReviewQueueEntry.family_id == family_id,
            ReviewQueueEntry.child_id == child_id,
            ReviewQueueEntry.subject_id == Subject.id,
        )
        .order_by(ReviewQueueEntry.last_offered_on.desc())
        .limit(1)
        .correlate(Subject)
        .with_hint(ReviewQueueEntry, "FORCE INDEX (ix_review_queue_offer)", dialect_name="mysql")
    ).scalar_subquery()
    groups = (
        select(Subject.id.label("sid"), first.label("anchor"), historical_offer.label("served"))
        .where(Subject.family_id == family_id, Subject.child_id == child_id)
        .subquery()
    )
    offered: Any = groups.c.served
    if projected_subject_offers:
        projected = case(projected_subject_offers, value=groups.c.sid, else_=offered)
        offered = case((offered > projected, offered), else_=projected)
    subject_offers: dict[str, date | None] = {
        sid: last_offered
        for sid, last_offered in db.execute(
            current(
                select(groups.c.sid, offered)
                .where(groups.c.anchor.is_not(None))
                .order_by(offered, groups.c.anchor, groups.c.sid)
                .limit(120)
            )
        ).all()
    }
    probes = []
    for minutes in range(1, 6):
        top = current(
            select(q.review_item_id)
            .where(*scope, q.subject_id == Subject.id, q.minutes == minutes)
            .order_by(q.priority_key)
            .limit(1)
            .correlate(Subject)
        ).scalar_subquery()
        probes.append(
            select(top).where(
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.id.in_(subject_offers),
            )
        )
        bucket = current(
            select(q.review_item_id)
            .where(*scope, q.minutes == minutes)
            .order_by(q.priority_key)
            .limit(min(10, max(0, budget)) // minutes)
        ).subquery()
        probes.append(select(bucket.c.review_item_id))
    ids = {rid for rid in db.scalars(union_all(*probes)) if rid}
    if not ids:
        return []
    rows = db.execute(
        current(
            select(ReviewItem, KnowledgeItem, Subject)
            .join(KnowledgeItem, KnowledgeItem.id == ReviewItem.knowledge_item_id)
            .join(Subject, Subject.id == KnowledgeItem.subject_id)
            .where(
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                ReviewItem.id.in_(ids),
            )
            .limit(1268)
        ).execution_options(populate_existing=True)
    )
    return select_daily_reviews(
        [
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
                review_count=r.review_count,
                state_version=r.state_version,
                subject_last_offered_on=subject_offers.get(s.id),
            )
            for r, k, s in rows
        ],
        budget_minutes=min(10, max(0, budget)),
    )
