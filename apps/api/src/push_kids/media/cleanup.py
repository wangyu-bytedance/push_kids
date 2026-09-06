from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from push_kids.persistence.models import MediaObject, SubmissionMedia


class MediaCleanup:
    @staticmethod
    def inventory(
        db: Session, family_id: str, submission_ids: list[str]
    ) -> tuple[set[str], list[str]]:
        attached = set(
            db.scalars(
                select(SubmissionMedia.path).where(
                    SubmissionMedia.submission_id.in_(submission_ids)
                )
            )
        )
        objects = list(
            db.scalars(
                select(MediaObject).where(
                    MediaObject.family_id == family_id,
                    MediaObject.submission_id.in_(submission_ids),
                )
            )
        )
        refs = {str(item) for item in attached if item}
        refs.update(str(item.storage_ref) for item in objects if item.storage_ref)
        paths = [
            str(item.storage_path) for item in objects if not item.storage_ref and item.storage_path
        ]
        return refs, paths

    @staticmethod
    def purge_rows(db: Session, submission_ids: list[str]) -> None:
        db.execute(delete(SubmissionMedia).where(SubmissionMedia.submission_id.in_(submission_ids)))
        db.execute(delete(MediaObject).where(MediaObject.submission_id.in_(submission_ids)))
