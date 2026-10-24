"""Permanent scheduling metadata; never merges learning or review facts."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.persistence.models import Child, KnowledgeItem, Subject
from push_kids.platform.time import utcnow

POLICY_REVISION = "single_full_coverage_v1"


def supersede(db: Session, family_id: str, child_id: str, old_id: str, covering_id: str) -> bool:
    """Caller owns transaction and planning reconciliation; child serializes all mutations."""
    child = db.scalar(
        select(Child)
        .where(Child.id == child_id, Child.family_id == family_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if child is None or child.deleting:
        return False
    rows = {
        k.id: k
        for k in db.scalars(
            select(KnowledgeItem)
            .join(Subject, Subject.id == KnowledgeItem.subject_id)
            .where(
                KnowledgeItem.id.in_([old_id, covering_id]),
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.kind == "learning",
            )
            .order_by(KnowledgeItem.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    }
    old, covering = rows.get(old_id), rows.get(covering_id)
    if not old or not covering or old_id == covering_id:
        return False
    if (
        old.review_status != "normal"
        or covering.review_status != "normal"
        or old.subject_id != covering.subject_id
    ):
        return False
    old.review_status = "superseded"
    old.superseded_by_knowledge_id = covering.id
    old.superseded_at = utcnow()
    old.supersession_policy_revision = POLICY_REVISION
    db.flush()
    return True
