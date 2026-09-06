from __future__ import annotations

import asyncio
import json
import logging
from contextlib import ExitStack, suppress
from datetime import timedelta
from time import monotonic

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

from push_kids.agent_processing.context import (
    build_analysis_input,
    material_fingerprint,
    repeated_material,
)
from push_kids.agent_processing.contracts import MATERIAL_FINGERPRINT_KEY, AnalysisProvider
from push_kids.media.store import MediaStore, WeChatCloudMediaStore
from push_kids.persistence.models import (
    AgentJob,
    JobState,
    LearningSubmission,
    MediaObject,
    MediaState,
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
        self._healthy = False
        self._running = False
        self._consecutive_failures = 0

    @property
    def is_ready(self) -> bool:
        return self._running and self._healthy and not self._stop.is_set()

    async def run(self) -> None:
        self._running = True
        self._healthy = False
        logger.info("worker_runtime_started")
        try:
            while not self._stop.is_set():
                try:
                    processed = await asyncio.to_thread(self.process_one)
                except Exception as exc:
                    self._healthy = False
                    self._consecutive_failures += 1
                    delay = min(30, 2 ** min(self._consecutive_failures - 1, 5))
                    logger.warning(
                        "worker_iteration_failed error_type=%s consecutive_failures=%s",
                        type(exc).__name__,
                        self._consecutive_failures,
                    )
                    await self._wait(delay)
                    continue
                self._healthy = True
                self._consecutive_failures = 0
                if not processed:
                    await self._wait(self.poll_seconds)
        finally:
            self._running = False
            self._healthy = False
            logger.info("worker_runtime_stopped")

    async def _wait(self, delay: float) -> None:
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._stop.wait(), timeout=delay)

    def stop(self) -> None:
        self._stop.set()

    def process_one(self) -> bool:
        if monotonic() - self._last_cleanup >= 60:
            self._last_cleanup = monotonic()
            try:
                self._cleanup_expired_media()
            except Exception as exc:
                logger.warning("media_cleanup_iteration_failed error_type=%s", type(exc).__name__)
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
            if submission is None or submission.state not in (
                SubmissionState.queued.value,
                SubmissionState.analyzing.value,
            ):
                job.state = JobState.cancelled.value
                db.commit()
                return True
            max_attempts = job.max_attempts or 3
            if (job.attempts or 0) >= max_attempts:
                job.state = JobState.failed.value
                job.error_message = "分析暂时失败，请重试"
                submission.state = SubmissionState.failed.value
                submission.error_code = "analysis_failed"
                submission.error_message = "分析暂时失败，请重试"
                db.commit()
                logger.warning(
                    "analysis_job_terminal_failed "
                    "job_id=%s attempt=%s max_attempts=%s stage=lease_recovery_exhausted",
                    job.id,
                    job.attempts,
                    max_attempts,
                )
                return True
            lease_recovery = job.state == JobState.running.value
            job.state = JobState.running.value
            job.attempts = (job.attempts or 0) + 1
            job.lease_until = now + timedelta(minutes=5)
            submission.state = SubmissionState.analyzing.value
            db.commit()
            # MySQL DATETIME can persist less precision than the Python value. Reload the
            # durable lease before keeping it as the late-result comparison token.
            db.refresh(job, attribute_names=["state", "attempts", "lease_until"])
            # The queue round trip succeeded; provider latency is not worker failure.
            self._healthy = True
            job_id, submission_id = job.id, submission.id
            attempt, lease = job.attempts, job.lease_until
            logger.info(
                "analysis_attempt_started job_id=%s attempt=%s max_attempts=%s lease_recovery=%s",
                job_id,
                attempt,
                max_attempts,
                int(lease_recovery),
            )
            stage = "media_query"
            try:
                stage_started = monotonic()
                logger.info(
                    "analysis_media_query_started job_id=%s attempt=%s",
                    job_id,
                    attempt,
                )
                media = list(
                    db.scalars(
                        select(SubmissionMedia)
                        .where(SubmissionMedia.submission_id == submission.id)
                        .order_by(
                            SubmissionMedia.sort_order,
                            SubmissionMedia.created_at,
                            SubmissionMedia.id,
                        )
                    )
                )
                logger.info(
                    "analysis_media_query_completed "
                    "job_id=%s attempt=%s object_count=%s duration_ms=%s",
                    job_id,
                    attempt,
                    len(media),
                    int((monotonic() - stage_started) * 1000),
                )
                with ExitStack() as media_stack:
                    stage = "media_materialize"
                    stage_started = monotonic()
                    logger.info(
                        "analysis_media_materialize_started job_id=%s attempt=%s object_count=%s",
                        job_id,
                        attempt,
                        len(media),
                    )
                    image_paths = []
                    for item in media:
                        image_paths.append(
                            media_stack.enter_context(self.media_store.materialize(item.path or ""))
                        )
                    logger.info(
                        "analysis_media_materialize_completed "
                        "job_id=%s attempt=%s object_count=%s duration_ms=%s",
                        job_id,
                        attempt,
                        len(media),
                        int((monotonic() - stage_started) * 1000),
                    )

                    stage = "context_build"
                    stage_started = monotonic()
                    logger.info(
                        "analysis_context_build_started job_id=%s attempt=%s",
                        job_id,
                        attempt,
                    )
                    data = build_analysis_input(db, submission, image_paths)
                    fingerprint = material_fingerprint(data.text, image_paths)
                    repeated = repeated_material(db, submission, fingerprint)
                    logger.info(
                        "analysis_context_build_completed job_id=%s attempt=%s duration_ms=%s",
                        job_id,
                        attempt,
                        int((monotonic() - stage_started) * 1000),
                    )
                    # End the read transaction before the external provider call.
                    db.rollback()

                    stage = "provider"
                    stage_started = monotonic()
                    logger.info(
                        "analysis_provider_started job_id=%s attempt=%s",
                        job_id,
                        attempt,
                    )
                    proposal = data.validate_proposal(self.provider.analyze(data))
                    logger.info(
                        "analysis_provider_completed job_id=%s attempt=%s duration_ms=%s",
                        job_id,
                        attempt,
                        int((monotonic() - stage_started) * 1000),
                    )

                stage = "writeback"
                stage_started = monotonic()
                logger.info(
                    "analysis_writeback_started job_id=%s attempt=%s",
                    job_id,
                    attempt,
                )
                job = db.scalar(
                    select(AgentJob)
                    .where(AgentJob.id == job_id)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )
                submission = db.scalar(
                    select(LearningSubmission)
                    .where(LearningSubmission.id == submission_id)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )
                if (
                    job is None
                    or submission is None
                    or job.state != JobState.running.value
                    or job.attempts != attempt
                    or job.lease_until != lease
                    or submission.state != SubmissionState.analyzing.value
                ):
                    db.rollback()
                    logger.warning(
                        "analysis_writeback_skipped job_id=%s attempt=%s reason=lease_changed",
                        job_id,
                        attempt,
                    )
                    return True
                if repeated:
                    proposal.uncertainties = [
                        "这份材料与近期提交完全相同，请核对是否为新的学习记录；本次不自动标记Todo完成。"
                    ] + proposal.uncertainties[:19]
                    proposal.todo_matches = []
                if not data.grade or not data.recent_learning:
                    proposal.uncertainties = (
                        proposal.uncertainties
                        + ["年级或已确认历史不完整，请核对知识点粒度；未推断学习阶段。"]
                    )[-20:]
                stored = proposal.model_dump()
                stored[MATERIAL_FINGERPRINT_KEY] = fingerprint
                submission.proposal_json = json.dumps(stored, ensure_ascii=False)
                submission.state = SubmissionState.pending_confirmation.value
                submission.error_code = None
                submission.error_message = None
                job.state = JobState.succeeded.value
                db.commit()
                logger.info(
                    "analysis_writeback_completed job_id=%s attempt=%s duration_ms=%s",
                    job_id,
                    attempt,
                    int((monotonic() - stage_started) * 1000),
                )
            except SQLAlchemyError as exc:
                # A failed commit can have an unknown outcome. Preserve the durable lease
                # and let a fresh session recover it instead of overwriting the job state.
                db.rollback()
                logger.warning(
                    "analysis_job_failed "
                    "job_id=%s attempt=%s max_attempts=%s stage=%s error_type=%s",
                    job_id,
                    attempt,
                    max_attempts,
                    stage,
                    type(exc).__name__,
                )
                raise
            except Exception as exc:
                db.rollback()
                job = db.scalar(
                    select(AgentJob)
                    .where(AgentJob.id == job_id)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )
                submission = db.scalar(
                    select(LearningSubmission)
                    .where(LearningSubmission.id == submission_id)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )
                if (
                    job is None
                    or submission is None
                    or job.state != JobState.running.value
                    or job.attempts != attempt
                    or job.lease_until != lease
                    or submission.state != SubmissionState.analyzing.value
                ):
                    db.rollback()
                    logger.warning(
                        "analysis_failure_writeback_skipped "
                        "job_id=%s attempt=%s stage=%s reason=lease_changed",
                        job_id,
                        attempt,
                        stage,
                    )
                    return True
                logger.warning(
                    "analysis_job_failed "
                    "job_id=%s attempt=%s max_attempts=%s stage=%s error_type=%s",
                    job.id,
                    job.attempts,
                    job.max_attempts or 3,
                    stage,
                    type(exc).__name__,
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
                outcome = job.state
                db.commit()
                event = (
                    "analysis_job_requeued"
                    if outcome == JobState.queued.value
                    else "analysis_job_terminal_failed"
                )
                logger.warning(
                    "%s job_id=%s attempt=%s max_attempts=%s stage=%s",
                    event,
                    job_id,
                    attempt,
                    max_attempts,
                    stage,
                )
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
