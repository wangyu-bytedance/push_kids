"""Durable bounded leases, external generation, and recovery of actual record links."""

import asyncio
import json
import logging
from contextlib import suppress
from datetime import timedelta
from time import monotonic
from uuid import uuid4

from sqlalchemy import delete, or_, select

from push_kids.knowledge.learning_context import get_context
from push_kids.learning.confirmation_query import confirmed_submission
from push_kids.learning_suggestions import generation, queries
from push_kids.learning_suggestions.models import PromptDay, RecordIntent, Suggestion, SuggestionJob
from push_kids.learning_suggestions.recording import link_records
from push_kids.learning_suggestions.service import lock_state
from push_kids.platform.errors import AppError
from push_kids.platform.time import local_date, utcnow

logger = logging.getLogger(__name__)


class SuggestionWorker:
    def __init__(self, database, provider, poll_seconds=1):
        self.database, self.provider, self.poll_seconds = database, provider, poll_seconds
        self._stop = asyncio.Event()
        self._maintenance_at = 0.0

    def stop(self):
        self._stop.set()

    async def run(self):
        while not self._stop.is_set():
            try:
                processed = await asyncio.to_thread(self.process_one)
            except Exception as exc:
                logger.error("suggestion_worker_iteration_failed type=%s", type(exc).__name__)
                processed = False
            if not processed:
                with suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(self._stop.wait(), timeout=self.poll_seconds)

    def process_one(self):
        if monotonic() >= self._maintenance_at:
            self.maintenance()
            self._maintenance_at = monotonic() + 30
        with self.database.session_factory() as db:
            # Only bounded discovery is global; every subsequent read/write is scoped.
            found = db.execute(
                select(SuggestionJob.id, SuggestionJob.family_id, SuggestionJob.child_id)
                .where(
                    SuggestionJob.available_at <= utcnow(),
                    or_(
                        SuggestionJob.state == "queued",
                        (SuggestionJob.state == "running") & (SuggestionJob.lease_until < utcnow()),
                    ),
                )
                .order_by(SuggestionJob.available_at, SuggestionJob.id)
                .limit(1)
            ).first()
        if found is None:
            return False
        job_id, family_id, child_id = found
        with self.database.session_factory() as db:
            try:
                shared = lock_state(db, family_id, child_id)
            except AppError:
                job = queries.scoped(db, SuggestionJob, family_id, child_id, job_id, lock=True)
                if job:
                    job.state, job.safe_error_code = "cancelled", "child_unavailable"
                    job.lease_until, job.lease_token = None, None
                    db.commit()
                return True
            job = queries.scoped(db, SuggestionJob, family_id, child_id, job_id, lock=True)
            if (
                job is None
                or job.state not in {"queued", "running"}
                or (job.state == "running" and job.lease_until >= utcnow())
            ):
                return False
            if job.attempts >= 3:
                job.state, job.safe_error_code = "failed", "attempts_exhausted"
                job.lease_until, job.lease_token = None, None
                db.commit()
                return True
            if (
                not db.info.get("learning_suggestions_enabled", False)
                or shared.active_job_id != job.id
                or shared.pending_task_id
                or queries.fingerprint(get_context(db, family_id, child_id))
                != job.input_fingerprint
            ):
                job.state, job.safe_error_code = "cancelled", "generation_disabled"
                db.commit()
                return True
            token = str(uuid4())
            job.updated_at = utcnow()
            db.flush()
            try:
                generation.check_quota(
                    db, family_id, child_id, claiming=True, retrying=job.attempts > 0
                )
            except AppError:
                job.state, job.safe_error_code = "failed", "resource_limit"
                job.lease_until, job.lease_token = None, None
                db.commit()
                return True
            job.state, job.lease_token, job.lease_until = (
                "running",
                token,
                utcnow() + timedelta(seconds=90),
            )
            job.attempts += 1
            context = json.loads(job.bounded_context_json)
            db.commit()
        try:
            content = self.provider.suggest(context)
            with self.database.session_factory() as db:
                shared = lock_state(db, family_id, child_id)
                job = queries.scoped(db, SuggestionJob, family_id, child_id, job_id, lock=True)
                if job:
                    generation.commit_result(db, family_id, child_id, shared, job, token, content)
                db.commit()
        except Exception:
            with self.database.session_factory() as db:
                job = queries.scoped(db, SuggestionJob, family_id, child_id, job_id, lock=True)
                if job and job.state == "running" and job.lease_token == token:
                    job.state = "failed" if job.attempts >= 3 else "queued"
                    job.safe_error_code = "generation_unavailable"
                    job.available_at = utcnow() + timedelta(seconds=10 if job.attempts == 1 else 60)
                    job.lease_until, job.lease_token = None, None
                    db.commit()
        return True

    def maintenance(self):
        with self.database.session_factory() as db:
            intents = list(
                db.execute(
                    select(
                        RecordIntent.id,
                        RecordIntent.family_id,
                        RecordIntent.child_id,
                        RecordIntent.task_id,
                    )
                    .where(RecordIntent.state == "draft", RecordIntent.recovery_after <= utcnow())
                    .order_by(RecordIntent.recovery_after, RecordIntent.id)
                    .limit(50)
                )
            )
        for intent_id, family_id, child_id, task_id in intents:
            with self.database.session_factory() as db:
                try:
                    link_records(db, family_id, child_id, task_id, intent_id, recovery=True)
                except AppError:
                    db.rollback()
        # Delete only bounded terminal IDs; accepted proposals/tasks/audits remain parent-owned.
        with self.database.session_factory() as db:
            jobs = list(
                db.execute(
                    select(SuggestionJob.id, SuggestionJob.family_id, SuggestionJob.child_id)
                    .where(
                        SuggestionJob.state.in_(["succeeded", "failed", "cancelled"]),
                        SuggestionJob.updated_at < utcnow() - timedelta(days=7),
                    )
                    .order_by(SuggestionJob.updated_at, SuggestionJob.id)
                    .limit(100)
                )
            )
            for jid, family_id, child_id in jobs:
                db.execute(
                    delete(SuggestionJob).where(
                        SuggestionJob.id == jid,
                        SuggestionJob.family_id == family_id,
                        SuggestionJob.child_id == child_id,
                    )
                )
            drafts = list(
                db.execute(
                    select(RecordIntent.id, RecordIntent.family_id, RecordIntent.child_id)
                    .where(
                        RecordIntent.state == "draft",
                        RecordIntent.created_at < utcnow() - timedelta(days=7),
                    )
                    .order_by(RecordIntent.created_at, RecordIntent.id)
                    .limit(100)
                )
            )
            for iid, family_id, child_id in drafts:
                intent = queries.scoped(db, RecordIntent, family_id, child_id, iid, lock=True)
                if (
                    intent
                    and intent.state == "draft"
                    and confirmed_submission(db, family_id, child_id, f"study:{iid}") is None
                ):
                    db.delete(intent)
            prompts = list(
                db.execute(
                    select(PromptDay.family_id, PromptDay.child_id, PromptDay.prompt_on)
                    .where(PromptDay.prompt_on < local_date() - timedelta(days=7))
                    .order_by(PromptDay.prompt_on, PromptDay.family_id, PromptDay.child_id)
                    .limit(100)
                )
            )
            for family_id, child_id, day in prompts:
                db.execute(
                    delete(PromptDay).where(
                        PromptDay.family_id == family_id,
                        PromptDay.child_id == child_id,
                        PromptDay.prompt_on == day,
                    )
                )
            expired = list(
                db.execute(
                    select(Suggestion.id, Suggestion.family_id, Suggestion.child_id)
                    .where(
                        Suggestion.status != "approved",
                        Suggestion.expires_at < utcnow() - timedelta(days=30),
                    )
                    .order_by(Suggestion.expires_at, Suggestion.id)
                    .limit(100)
                )
            )
            for sid, family_id, child_id in expired:
                db.execute(
                    delete(Suggestion).where(
                        Suggestion.id == sid,
                        Suggestion.family_id == family_id,
                        Suggestion.child_id == child_id,
                        Suggestion.status != "approved",
                    )
                )
            db.commit()
