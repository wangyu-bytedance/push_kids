"""Knowledge-owned confirmation clock and bounded context, independent of its consumers."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, delete, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import Base, Child, KnowledgeItem, Subject
from push_kids.platform.time import local_date


class KnowledgeInputClock(Base):
    __tablename__ = "knowledge_input_clocks"
    family_id = Column(String(80), primary_key=True)
    child_id = Column(String(36), ForeignKey("children.id"), primary_key=True)
    observed_since = Column(Date, nullable=False)
    last_new_confirmed_on = Column(Date, nullable=True)
    input_revision = Column(Integer, nullable=False, default=0)


def record_confirmation(db: Session, family_id: str, child_id: str, *, new_knowledge: bool) -> None:
    """Called under the caller's Child lock, in the same confirmation transaction."""
    clock = db.get(KnowledgeInputClock, (family_id, child_id))
    today = local_date()
    if clock is None:
        clock = KnowledgeInputClock(
            family_id=family_id, child_id=child_id, observed_since=today, input_revision=0
        )
        db.add(clock)
    clock.input_revision = int(clock.input_revision or 0) + 1
    if new_knowledge:
        clock.last_new_confirmed_on = today


def invalidate_input(db: Session, family_id: str, child_id: str) -> None:
    record_confirmation(db, family_id, child_id, new_knowledge=False)


def get_context(db: Session, family_id: str, child_id: str, *, child: Child | None = None) -> dict:
    """Reuse a caller's locked child snapshot, validating its scope before reading context."""
    if child is None:
        child = db.scalar(select(Child).where(Child.family_id == family_id, Child.id == child_id))
    if child is None or child.family_id != family_id or child.id != child_id:
        return {}
    clock = db.get(KnowledgeInputClock, (family_id, child_id))
    subjects = list(
        db.execute(
            select(Subject.id, Subject.name)
            .where(
                Subject.family_id == family_id,
                Subject.child_id == child_id,
                Subject.active.is_(True),
                Subject.kind == "learning",
            )
            .order_by(Subject.id)
            .limit(30)
        )
    )
    rows = list(
        db.execute(
            select(
                KnowledgeItem.id,
                KnowledgeItem.subject_id,
                KnowledgeItem.name,
                KnowledgeItem.category,
                KnowledgeItem.created_at,
            )
            .where(
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                KnowledgeItem.review_status == "normal",
                KnowledgeItem.subject_id.in_([s.id for s in subjects]),
            )
            .order_by(KnowledgeItem.created_at.desc(), KnowledgeItem.id.desc())
            .limit(20)
        )
    )
    return {
        "grade": child.grade,
        "active": bool(child.active and not child.deleting),
        "observed_since": clock.observed_since.isoformat()
        if clock and clock.observed_since
        else None,
        "last_new_confirmed_on": clock.last_new_confirmed_on.isoformat()
        if clock and clock.last_new_confirmed_on
        else None,
        "input_revision": int(clock.input_revision or 0) if clock else 0,
        "subjects": [{"id": s.id, "name": s.name} for s in subjects],
        "knowledge": [
            {
                "alias": f"K{i + 1}",
                "id": k.id,
                "subject_id": k.subject_id,
                "name": k.name,
                "category": k.category,
                "confirmed_at": k.created_at.isoformat(),
            }
            for i, k in enumerate(rows)
        ],
        "coverage": "recent_confirmed_max20",
        "truncated": len(rows) == 20,
    }


def purge_context(db: Session, family_id: str, child_id: str | None = None) -> None:
    query = delete(KnowledgeInputClock).where(KnowledgeInputClock.family_id == family_id)
    if child_id:
        query = query.where(KnowledgeInputClock.child_id == child_id)
    db.execute(query)
