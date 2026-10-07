"""Owner of validated temporary stage data; all operations are family-scoped."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from hashlib import sha256
from time import monotonic
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.stage_contracts import PIPELINE_REVISION
from push_kids.persistence.models import (
    AgentJob,
    AnalysisStageResult,
    Child,
    Family,
    LearningSubmission,
)
from push_kids.platform.database import Database
from push_kids.platform.time import utcnow


def fingerprint(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class StageCheckpoints:
    def __init__(
        self,
        database: Database,
        family_id: str,
        child_id: str,
        submission_id: str,
        job_id: str,
        attempt: int,
        lease: datetime,
    ):
        self.database = database
        self.family_id, self.child_id = family_id, child_id
        self.submission_id, self.job_id = submission_id, job_id
        self.attempt, self.lease = attempt, lease
        with database.session_factory() as db:
            rows = db.scalars(
                select(AnalysisStageResult)
                .where(
                    AnalysisStageResult.family_id == family_id,
                    AnalysisStageResult.job_id == job_id,
                )
                .limit(15)
            ).all()
            if len(rows) > 14:
                raise StageFailure("capacity", retryable=False)
            self.rows = {r.unit_key: r for r in rows}

    def get(self, unit: str, digest: str) -> dict[str, Any] | None:
        row = self.rows.get(unit)
        if (
            row is None
            or row.expires_at is None
            or row.expires_at <= utcnow()
            or row.fingerprint != digest
        ):
            return None
        if row.revision != PIPELINE_REVISION or row.child_id != self.child_id:
            return None
        try:
            value = json.loads(row.payload or "")
        except (ValueError, TypeError):
            return None
        return value if isinstance(value, dict) else None

    def _guard(self, db: Session) -> None:
        # Same outer lock order as deletion: family -> child -> job -> submission.
        family = db.scalar(select(Family).where(Family.id == self.family_id).with_for_update())
        child = db.scalar(
            select(Child)
            .where(
                Child.id == self.child_id,
                Child.family_id == self.family_id,
            )
            .with_for_update()
        )
        job = db.scalar(
            select(AgentJob)
            .where(
                AgentJob.id == self.job_id,
                AgentJob.family_id == self.family_id,
            )
            .with_for_update()
        )
        submission = db.scalar(
            select(LearningSubmission)
            .where(
                LearningSubmission.id == self.submission_id,
                LearningSubmission.family_id == self.family_id,
            )
            .with_for_update()
        )
        if (
            (family is not None and family.status != "active")
            or child is None
            or child.deleting
            or job is None
            or job.state != "running"
            or job.attempts != self.attempt
            or job.lease_until != self.lease
            or job.submission_id != self.submission_id
            or self.lease <= utcnow()
            or submission is None
            or submission.state != "analyzing"
            or submission.child_id != self.child_id
        ):
            raise StageFailure("lease_changed", retryable=False)

    def put(
        self, unit: str, digest: str, value: dict[str, Any], *, deadline: float | None = None
    ) -> None:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if len(payload.encode()) > 65535:
            raise StageFailure("capacity", retryable=False)
        with self.database.session_factory() as db:
            self._guard(db)
            rows = db.scalars(
                select(AnalysisStageResult)
                .where(
                    AnalysisStageResult.family_id == self.family_id,
                    AnalysisStageResult.job_id == self.job_id,
                )
                .limit(15)
            ).all()
            existing = next((r for r in rows if r.unit_key == unit), None)
            size = sum(len((r.payload or "").encode()) for r in rows if r.unit_key != unit)
            if len(rows) >= 14 and existing is None or size + len(payload.encode()) > 512 * 1024:
                raise StageFailure("capacity", retryable=False)
            row = existing or AnalysisStageResult(
                family_id=self.family_id,
                child_id=self.child_id,
                submission_id=self.submission_id,
                job_id=self.job_id,
                unit_key=unit,
            )
            row.revision, row.fingerprint, row.payload = PIPELINE_REVISION, digest, payload
            row.expires_at = utcnow() + timedelta(hours=24)
            db.add(row)
            if deadline is not None and monotonic() >= deadline:
                raise StageFailure("local_deadline")
            db.commit()
            self.rows[unit] = row


def purge_stages(
    db: Session, family_id: str, child_id: str | None = None, submission_id: str | None = None
) -> None:
    query = delete(AnalysisStageResult).where(AnalysisStageResult.family_id == family_id)
    if child_id is not None:
        query = query.where(AnalysisStageResult.child_id == child_id)
    if submission_id is not None:
        query = query.where(AnalysisStageResult.submission_id == submission_id)
    with db.no_autoflush:
        db.execute(query)


def expire_stages(database: Database) -> int:
    with database.session_factory() as db:
        rows = db.execute(
            select(AnalysisStageResult.id, AnalysisStageResult.family_id)
            .where(
                AnalysisStageResult.expires_at <= utcnow(),
            )
            .order_by(AnalysisStageResult.expires_at, AnalysisStageResult.id)
            .limit(100)
        ).all()
        for row_id, family_id in rows:
            db.execute(
                delete(AnalysisStageResult).where(
                    AnalysisStageResult.id == row_id,
                    AnalysisStageResult.family_id == family_id,
                    AnalysisStageResult.expires_at <= utcnow(),
                )
            )
        db.commit()
        return len(rows)
