"""Explicit scoped repair contract; daily reads never scan/rebuild the slot projection."""

from sqlalchemy import delete, select, text

from push_kids.persistence.early_review_slots_v1 import COLUMNS, projection_select, refresh_sql
from push_kids.persistence.models import Child, ReviewEarlySlot
from push_kids.platform.errors import NotFoundError


def projection_drift(db, family_id, child_id) -> int:
    dialect = db.get_bind().dialect.name
    expected = projection_select(dialect, "r.family_id=:family AND r.child_id=:child")
    equal = "<=>" if dialect == "mysql" else "IS"
    mismatches = " OR ".join(
        f"NOT (q.{column} {equal} e.{column})" for column in COLUMNS.split(",")[2:]
    )
    keys = "q.review_item_id=e.review_item_id AND q.slot_on=e.slot_on"
    params = {"family": family_id, "child": child_id}
    missing = f"""SELECT COUNT(*) FROM ({expected}) e
        LEFT JOIN review_early_slots q ON {keys}
        WHERE q.review_item_id IS NULL OR {mismatches}"""
    extra = f"""SELECT COUNT(*) FROM review_early_slots q
        LEFT JOIN ({expected}) e ON {keys}
        WHERE q.family_id=:family AND q.child_id=:child AND e.review_item_id IS NULL"""
    return int(db.scalar(text(missing), params) or 0) + int(db.scalar(text(extra), params) or 0)


def rebuild_projection(db, family_id, child_id):
    if (
        db.scalar(
            select(Child.id)
            .where(Child.family_id == family_id, Child.id == child_id)
            .with_for_update()
        )
        is None
    ):
        raise NotFoundError("没有找到这个孩子")
    db.execute(
        delete(ReviewEarlySlot).where(
            ReviewEarlySlot.family_id == family_id, ReviewEarlySlot.child_id == child_id
        )
    )
    db.execute(
        text(refresh_sql(db.get_bind().dialect.name, "r.family_id=:family AND r.child_id=:child")),
        {"family": family_id, "child": child_id},
    )
    if projection_drift(db, family_id, child_id):
        raise RuntimeError("early_review_rebuild_mismatch")
