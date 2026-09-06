from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import (
    ActivitySchedule,
    CalendarEvent,
    Child,
    TravelArrangement,
)
from push_kids.platform.errors import ConflictError, NotFoundError

MAX_ACTIVE_TIMED_ITEMS_PER_CHILD = 20


def _locked_count(db: Session, statements: Iterable[Select[tuple[str | None]]]) -> int:
    """Count only up to the limit using MySQL current/locking reads."""
    total = 0
    for statement in statements:
        remaining = MAX_ACTIVE_TIMED_ITEMS_PER_CHILD - total
        if remaining <= 0:
            break
        total += len(list(db.scalars(statement.limit(remaining).with_for_update())))
    return total


def ensure_timed_item_capacity(db: Session, family_id: str, child_id: str) -> None:
    """Serialize admission and enforce one cross-source calendar item budget."""
    child = db.scalar(
        select(Child)
        .where(
            Child.id == child_id,
            Child.family_id == family_id,
            Child.active.is_(True),
        )
        .with_for_update()
    )
    if child is None:
        raise NotFoundError("没有找到可用的孩子档案")

    total = _locked_count(
        db,
        (
            select(CalendarEvent.id).where(
                CalendarEvent.family_id == family_id,
                CalendarEvent.child_id == child_id,
                CalendarEvent.active.is_(True),
            ),
            select(ActivitySchedule.id).where(
                ActivitySchedule.family_id == family_id,
                ActivitySchedule.child_id == child_id,
                ActivitySchedule.active.is_(True),
                ActivitySchedule.start_time.is_not(None),
                ActivitySchedule.end_time.is_not(None),
            ),
            select(TravelArrangement.id).where(
                TravelArrangement.family_id == family_id,
                TravelArrangement.child_id == child_id,
                TravelArrangement.active.is_(True),
            ),
        ),
    )
    if total >= MAX_ACTIVE_TIMED_ITEMS_PER_CHILD:
        raise ConflictError("每个孩子最多保留 20 项日程安排，请先删除不再需要的事项")
