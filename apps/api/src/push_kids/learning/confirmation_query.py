"""Read-only confirmation contract for recoverable task association."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.persistence.models import LearningRecord, LearningSubmission, SubmissionRequest


def confirmed_submission(
    db: Session, family_id: str, child_id: str, key: str, submission_id: str | None = None
) -> dict | None:
    row = db.execute(
        select(LearningSubmission.id, LearningSubmission.confirmed_at, LearningSubmission.state)
        .join(SubmissionRequest, SubmissionRequest.submission_id == LearningSubmission.id)
        .where(
            SubmissionRequest.family_id == family_id,
            SubmissionRequest.idempotency_key == key,
            LearningSubmission.family_id == family_id,
            LearningSubmission.child_id == child_id,
        )
        .limit(1)
    ).first()
    if row is None or (submission_id and row.id != submission_id) or row.state != "confirmed":
        return None
    ids = list(
        db.scalars(
            select(LearningRecord.id)
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.submission_id == row.id,
            )
            .order_by(LearningRecord.id)
            .limit(30)
        )
    )
    return {"submission_id": row.id, "confirmed_at": row.confirmed_at, "record_ids": ids}


def existing_record_ids(db: Session, family_id: str, child_id: str, ids: list[str]) -> set[str]:
    if len(ids) > 50:
        raise ValueError("Record projection exceeds page cap")
    return set(
        db.scalars(
            select(LearningRecord.id)
            .where(
                LearningRecord.family_id == family_id,
                LearningRecord.child_id == child_id,
                LearningRecord.id.in_(ids),
            )
            .limit(50)
        )
    )
