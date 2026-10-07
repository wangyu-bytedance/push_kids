"""Scoped maintenance contract for planning's reconstructible storage projection."""

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from push_kids.persistence.models import Child, ReviewQueueEntry
from push_kids.persistence.review_queue_v1 import COLUMNS, projection_select, upsert_sql
from push_kids.platform.errors import NotFoundError


def projection_drift(db: Session, family_id: str, child_id: str, *, lock: bool = False) -> int:
    """Count mismatches in SQL without materializing a family's full review inventory."""
    dialect = db.get_bind().dialect.name
    expected = projection_select(dialect, "r.family_id=:family AND r.child_id=:child")
    locking = " FOR UPDATE" if lock and dialect == "mysql" else ""
    expected += locking
    equal = "<=>" if dialect == "mysql" else "IS"
    mismatches = " OR ".join(f"NOT (q.{c} {equal} e.{c})" for c in COLUMNS[1:])
    query = f"""SELECT COUNT(*) FROM ({expected}) e LEFT JOIN review_queue_entries q
        ON q.review_item_id=e.review_item_id
        WHERE q.review_item_id IS NULL OR {mismatches}{locking}"""
    params = {"family": family_id, "child": child_id}
    extra = f"""SELECT COUNT(*) FROM review_queue_entries q LEFT JOIN ({expected}) e
        ON q.review_item_id=e.review_item_id WHERE q.family_id=:family AND q.child_id=:child
        AND e.review_item_id IS NULL{locking}"""
    return int(db.scalar(text(query), params) or 0) + int(db.scalar(text(extra), params) or 0)


def rebuild_projection(db: Session, family_id: str, child_id: str) -> None:
    """Explicit repair in caller's transaction; normal reads never call this function."""
    child = db.scalar(
        select(Child.id).where(Child.family_id == family_id, Child.id == child_id).with_for_update()
    )
    if child is None:
        raise NotFoundError("没有找到这个孩子")
    db.execute(
        delete(ReviewQueueEntry).where(
            ReviewQueueEntry.family_id == family_id, ReviewQueueEntry.child_id == child_id
        )
    )
    db.execute(
        text(upsert_sql(db.get_bind().dialect.name, "r.family_id=:family AND r.child_id=:child")),
        {"family": family_id, "child": child_id},
    )
    if projection_drift(db, family_id, child_id, lock=True):
        raise RuntimeError("review_queue_rebuild_mismatch")
