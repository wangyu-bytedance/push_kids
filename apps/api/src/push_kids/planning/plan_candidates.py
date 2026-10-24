"""Bounded index reads over the transactionally maintained planning queue."""

from datetime import date

from sqlalchemy import and_, case, func, select, union_all
from sqlalchemy.orm import Session

from push_kids.persistence.models import KnowledgeItem, ReviewItem, ReviewQueueEntry, Subject
from push_kids.planning.queue_state import recent_plan_days
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


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
    candidate_budget: int = 120,
) -> list[ReviewSelectionCandidate]:
    q = ReviewQueueEntry
    days = sorted(
        set(recent_plan_days(db, family_id, child_id, target, lock=lock))
        | {d for d in projected_days if d < target},
        reverse=True,
    )[:3]
    scope = (q.family_id == family_id, q.child_id == child_id)
    # MySQL 5.7 needs equality to continue through these composite index columns.
    eligible = (*scope, q.available == 1, q.due_on <= target, q.review_item_id.not_in(exclude))

    def current(query):
        return query.with_for_update() if lock else query

    # All historical offers participate, including reviews currently outside the due set.
    historical_offer = current(
        select(q.last_offered_on)
        .where(*scope, q.subject_id == Subject.id)
        .order_by(q.subject_id.desc(), q.last_offered_on.desc())
        .limit(1)
        .correlate(Subject)
        .with_hint(q, "FORCE INDEX (ix_review_queue_offer)", dialect_name="mysql")
    ).scalar_subquery()
    served = current(
        select(Subject.id.label("sid"), historical_offer.label("served")).where(
            Subject.family_id == family_id, Subject.child_id == child_id
        )
    ).subquery()
    oldest = current(
        select(q.priority_key)
        .where(*eligible, q.manual == 0, q.subject_id == Subject.id)
        .order_by(q.subject_id, q.priority_key)
        .with_hint(q, "FORCE INDEX (ix_review_queue_subject_first)", dialect_name="mysql")
        .limit(1)
        .correlate(Subject)
    ).scalar_subquery()
    subject_totals = current(
        select(Subject.id.label("sid"), func.substr(oldest, 1, 10).label("anchor")).where(
            Subject.family_id == family_id, Subject.child_id == child_id
        )
    ).subquery()
    offered = served.c.served
    if projected_subject_offers:
        projected = case(projected_subject_offers, value=subject_totals.c.sid, else_=offered)
        offered = case((offered > projected, offered), else_=projected)
    # Missed-plan count is monotone in anchor: (-missed, anchor) has exactly this order.
    groups = current(
        select(subject_totals.c.sid)
        .outerjoin(served, served.c.sid == subject_totals.c.sid)
        .where(subject_totals.c.anchor.is_not(None))
        .order_by(offered, subject_totals.c.anchor, subject_totals.c.sid)
        .limit(120)
    )
    subject_ids = list(db.scalars(groups))
    # One bounded statement: at most 120 subjects × five indexed top-1 probes.
    coverage = []
    for minutes in range(1, 6):
        first = current(
            select(q.review_item_id)
            .where(*eligible, q.manual == 0, q.subject_id == Subject.id, q.minutes == minutes)
            .order_by(q.subject_id, q.minutes, q.priority_key)
            .with_hint(q, "FORCE INDEX (ix_review_queue_subject)", dialect_name="mysql")
            .limit(1)
            .correlate(Subject)
        ).scalar_subquery()
        coverage.append(
            current(
                select(first).where(
                    Subject.family_id == family_id,
                    Subject.child_id == child_id,
                    Subject.id.in_(subject_ids),
                )
            )
        )
    ids = {rid for rid in db.scalars(union_all(*coverage)) if rid is not None}
    pools = []
    for repeated in (False, True):
        for minutes in range(1, 6):
            bucket = current(
                select(q.review_item_id)
                .where(*eligible, q.manual == 0, q.repeated == repeated, q.minutes == minutes)
                .order_by(q.priority_key)
                .limit(min(120, max(0, candidate_budget)) // minutes)
            ).subquery()
            pools.append(select(bucket.c.review_item_id))
    ids.update(db.scalars(union_all(*pools)))
    ids.update(
        db.scalars(
            current(
                select(q.review_item_id)
                .where(*eligible, q.manual == 1)
                .order_by(q.due_on, q.review_item_id)
                .limit(120)
            )
        )
    )
    if not ids:
        return []
    query = (
        select(
            ReviewItem.id.label("review_id"),
            KnowledgeItem.id.label("knowledge_id"),
            Subject.id.label("subject_id"),
            Subject.name.label("subject_name"),
            KnowledgeItem.name.label("knowledge_name"),
            KnowledgeItem.review_method,
            KnowledgeItem.estimated_minutes,
            ReviewItem.due_date,
            ReviewItem.last_reviewed_on,
            ReviewItem.step.label("review_step"),
            ReviewItem.last_feedback,
            ReviewItem.source_submission_id,
            ReviewItem.review_count,
            ReviewItem.state_version,
            q.anchor_on,
            q.manual,
            served.c.served,
        )
        .select_from(q)
        .join(
            ReviewItem,
            and_(
                ReviewItem.id == q.review_item_id,
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
            ),
        )
        .join(
            KnowledgeItem,
            and_(
                KnowledgeItem.id == ReviewItem.knowledge_item_id,
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
            ),
        )
        .join(
            Subject,
            and_(
                Subject.id == q.subject_id,
                Subject.family_id == family_id,
                Subject.child_id == child_id,
            ),
        )
        .outerjoin(served, served.c.sid == q.subject_id)
        .where(*scope, q.review_item_id.in_(ids))
        .limit(1268)
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    result = []
    for row in db.execute(query).mappings():
        fields = dict(row)
        anchor = fields.pop("anchor_on")
        fields["manually_scheduled"] = bool(fields.pop("manual"))
        fields["subject_last_offered_on"] = max(
            fields.pop("served") or date.min,
            (projected_subject_offers or {}).get(fields["subject_id"], date.min),
        )
        result.append(
            ReviewSelectionCandidate(
                **fields,
                missed_plan_days=sum(d >= anchor for d in days),
                waiting_since=anchor,
            )
        )
    return result


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
            candidate_budget=budget,
        ),
        budget_minutes=budget,
    )
