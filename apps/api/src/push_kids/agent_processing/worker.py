from __future__ import annotations

import asyncio
import logging
from contextlib import ExitStack, suppress
from datetime import timedelta
from time import monotonic

from sqlalchemy import or_, select

from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisProvider,
    RecentLearningContext,
    TodoCandidate,
)
from push_kids.media.store import MediaStore, WeChatCloudMediaStore
from push_kids.persistence.models import (
    AgentJob,
    JobState,
    KnowledgeItem,
    LearningRecord,
    LearningSubmission,
    MediaObject,
    MediaState,
    ReviewItem,
    Subject,
    SubmissionMedia,
    SubmissionState,
)
from push_kids.platform.database import Database
from push_kids.platform.time import utcnow

logger = logging.getLogger("push_kids.worker")


class AnalysisWorker:
    def __init__(
        self,
        database: Database,
        provider: AnalysisProvider,
        media_store: MediaStore,
        poll_seconds: float = 0.25,
    ) -> None:
        self.database = database
        self.provider = provider
        self.media_store = media_store
        self.poll_seconds = poll_seconds
        self._stop = asyncio.Event()
        self._last_cleanup = 0.0

    async def run(self) -> None:
        while not self._stop.is_set():
            processed = await asyncio.to_thread(self.process_one)
            if not processed:
                with suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(self._stop.wait(), timeout=self.poll_seconds)

    def stop(self) -> None:
        self._stop.set()

    def process_one(self) -> bool:
        if monotonic() - self._last_cleanup >= 60:
            self._cleanup_expired_media()
            self._last_cleanup = monotonic()
        with self.database.session_factory() as db:
            now = utcnow()
            job = db.scalar(
                select(AgentJob)
                .where(
                    or_(
                        AgentJob.state == JobState.queued.value,
                        (AgentJob.state == JobState.running.value) & (AgentJob.lease_until < now),
                    ),
                    AgentJob.available_at <= now,
                )
                .order_by(AgentJob.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if job is None:
                return False
            submission = db.scalar(
                select(LearningSubmission)
                .where(LearningSubmission.id == job.submission_id)
                .with_for_update()
            )
            if submission is None or submission.state == SubmissionState.cancelled.value:
                job.state = JobState.cancelled.value
                db.commit()
                return True
            job.state = JobState.running.value
            job.attempts = (job.attempts or 0) + 1
            job.lease_until = now + timedelta(minutes=5)
            submission.state = SubmissionState.analyzing.value
            db.commit()
            media = list(
                db.scalars(
                    select(SubmissionMedia).where(SubmissionMedia.submission_id == submission.id)
                )
            )
            candidate_rows = db.execute(
                select(ReviewItem, KnowledgeItem)
                .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
                .where(
                    ReviewItem.family_id == submission.family_id,
                    ReviewItem.child_id == submission.child_id,
                    ReviewItem.active.is_(True),
                )
                .limit(50)
            ).all()
            subject_names = list(
                db.scalars(
                    select(Subject.name)
                    .where(
                        Subject.family_id == submission.family_id,
                        Subject.child_id == submission.child_id,
                        Subject.active.is_(True),
                    )
                    .order_by(Subject.created_at)
                )
            )
            recent_rows = db.execute(
                select(LearningRecord, Subject)
                .join(Subject, LearningRecord.subject_id == Subject.id)
                .where(
                    LearningRecord.family_id == submission.family_id,
                    LearningRecord.child_id == submission.child_id,
                    LearningRecord.occurred_at <= submission.occurred_at,
                )
                .order_by(LearningRecord.occurred_at.desc())
                .limit(20)
            ).all()
            try:
                with ExitStack() as media_stack:
                    image_paths = [
                        media_stack.enter_context(self.media_store.materialize(item.path or ""))
                        for item in media
                    ]
                    proposal = self.provider.analyze(
                        AnalysisInput(
                            text=submission.input_text,
                            image_paths=image_paths,
                            todo_candidates=[
                                TodoCandidate(
                                    review_id=review.id or "", knowledge_name=knowledge.name or ""
                                )
                                for review, knowledge in candidate_rows
                                if review.id and knowledge.name
                            ],
                            existing_subjects=subject_names,
                            recent_learning=[
                                RecentLearningContext(
                                    record_id=record.id or "",
                                    subject_name=subject.name or "",
                                    summary=record.summary or "",
                                    occurred_at=record.occurred_at.isoformat(),
                                )
                                for record, subject in recent_rows
                                if record.id and record.occurred_at and subject.name
                            ],
                        )
                    )
                db.refresh(job)
                db.refresh(submission)
                if submission.state == SubmissionState.cancelled.value:
                    job.state = JobState.cancelled.value
                else:
                    submission.proposal_json = proposal.model_dump_json()
                    submission.state = SubmissionState.pending_confirmation.value
                    submission.error_code = None
                    submission.error_message = None
                    job.state = JobState.succeeded.value
                db.commit()
            except Exception:
                db.rollback()
                job = db.get(AgentJob, job.id)
                submission = db.get(LearningSubmission, submission.id)
                if job is None or submission is None:
                    return True
                logger.warning(
                    "analysis_job_failed job_id=%s attempt=%s",
                    job.id,
                    job.attempts,
                )
                message = "分析暂时失败，请重试"
                job.error_message = message
                if (job.attempts or 0) < (job.max_attempts or 3):
                    job.state = JobState.queued.value
                    job.available_at = utcnow() + timedelta(seconds=job.attempts or 1)
                    submission.state = SubmissionState.queued.value
                else:
                    job.state = JobState.failed.value
                    submission.state = SubmissionState.failed.value
                    submission.error_code = "analysis_failed"
                    submission.error_message = message
                db.commit()
            return True

    def _cleanup_expired_media(self) -> None:
        if not isinstance(self.media_store, WeChatCloudMediaStore):
            return
        with self.database.session_factory() as db:
            cleanup_candidates = list(
                db.scalars(
                    select(MediaObject)
                    .join(LearningSubmission, MediaObject.submission_id == LearningSubmission.id)
                    .where(
                        or_(
                            (
                                (MediaObject.state == MediaState.ticketed.value)
                                & (MediaObject.expires_at <= utcnow())
                            ),
                            (
                                (MediaObject.state == MediaState.claimed.value)
                                & (LearningSubmission.state == SubmissionState.cancelled.value)
                            ),
                        )
                    )
                    .order_by(MediaObject.expires_at)
                    .limit(20)
                    .with_for_update(skip_locked=True)
                )
            )
            for item in cleanup_candidates:
                storage_ref = item.storage_ref or item.storage_path
                if not storage_ref:
                    continue
                try:
                    self.media_store.delete(storage_ref)
                except Exception:
                    logger.warning(
                        "media_cleanup_failed media_id=%s state=%s",
                        item.id,
                        item.state,
                    )
                    continue
                item.state = MediaState.deleted.value
            db.commit()
