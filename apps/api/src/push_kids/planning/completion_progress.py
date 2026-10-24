"""Actor completion facts owned by planning, shared only through its public service."""

from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import (
    ReviewMemberCompletionProgress,
    ReviewMemberCompletionReceipt,
)
from push_kids.platform.time import utcnow


def completion_cursor(db: Session, family_id: str, member_id: str, *, current: bool = False) -> int:
    statement = select(ReviewMemberCompletionProgress.total_completed).where(
        ReviewMemberCompletionProgress.family_id == family_id,
        ReviewMemberCompletionProgress.member_id == member_id,
    )
    value = db.scalar(statement.with_for_update() if current else statement)
    return int(value or 0)


def record_completion(
    db: Session, family_id: str, member_id: str, review_id: str, child_id: str, day: date
) -> None:
    """Called in the feedback transaction after the family and child locks, before commit.

    Authenticated mutations hold the family lock, including different children/devices.
    The composite receipt also rejects duplicate task/day writes with a different request key.
    """
    progress = db.scalar(
        select(ReviewMemberCompletionProgress)
        .where(
            ReviewMemberCompletionProgress.family_id == family_id,
            ReviewMemberCompletionProgress.member_id == member_id,
        )
        .with_for_update()
    )
    if db.get(ReviewMemberCompletionReceipt, (family_id, member_id, review_id, day)):
        return
    db.add(
        ReviewMemberCompletionReceipt(
            family_id=family_id,
            member_id=member_id,
            review_id=review_id,
            child_id=child_id,
            day=day,
        )
    )
    if progress is None:
        db.add(
            ReviewMemberCompletionProgress(
                family_id=family_id, member_id=member_id, total_completed=1
            )
        )
    else:
        progress.total_completed = int(progress.total_completed or 0) + 1
        progress.updated_at = utcnow()


def purge_completion_data(db: Session, family_id: str, child_id: str | None) -> None:
    scope = [ReviewMemberCompletionReceipt.family_id == family_id]
    if child_id is not None:
        scope.append(ReviewMemberCompletionReceipt.child_id == child_id)
    db.execute(delete(ReviewMemberCompletionReceipt).where(*scope))
    if child_id is None:
        db.execute(
            delete(ReviewMemberCompletionProgress).where(
                ReviewMemberCompletionProgress.family_id == family_id
            )
        )


def prune_completion_receipts(db: Session, before: date) -> None:
    """Expiry removes only old dedupe facts, never the monotonic member cursor."""
    db.execute(
        delete(ReviewMemberCompletionReceipt).where(ReviewMemberCompletionReceipt.day < before)
    )
