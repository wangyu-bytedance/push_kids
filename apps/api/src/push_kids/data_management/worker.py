from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import timedelta

from sqlalchemy import delete, or_, select
from sqlalchemy.exc import SQLAlchemyError

from push_kids.activities.service import ActivitiesService
from push_kids.children.service import ChildrenService
from push_kids.families.service import FamilyService
from push_kids.learning.service import LearningService
from push_kids.media.cleanup import MediaCleanup
from push_kids.media.store import MediaStore, WeChatCloudMediaStore
from push_kids.persistence.models import (
    Child,
    DeletionRequest,
    DeletionState,
    Family,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.database import Database
from push_kids.platform.time import utcnow
from push_kids.travel.service import TravelService

logger = logging.getLogger("push_kids.data_deletion")


class DataDeletionWorker:
    def __init__(self, database: Database, media_store: MediaStore, poll_seconds: float = 0.25):
        self.database = database
        self.media_store = media_store
        self.poll_seconds = poll_seconds
        self._stop = asyncio.Event()
        self._running = False
        self._healthy = False

    @property
    def is_ready(self) -> bool:
        return self._running and self._healthy and not self._stop.is_set()

    def stop(self) -> None:
        self._stop.set()

    async def _wait(self, delay: float) -> None:
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._stop.wait(), timeout=delay)

    async def run(self) -> None:
        self._running = True
        self._healthy = False
        logger.info("data_deletion_worker_started")
        try:
            while not self._stop.is_set():
                try:
                    processed = await asyncio.to_thread(self.process_one)
                    self._healthy = True
                except Exception as exc:
                    self._healthy = False
                    logger.warning(
                        "data_deletion_worker_iteration_failed error_type=%s",
                        type(exc).__name__,
                    )
                    await self._wait(1)
                    continue
                if not processed:
                    await self._wait(self.poll_seconds)
        finally:
            self._running = False
            self._healthy = False
            logger.info("data_deletion_worker_stopped")

    def process_one(self) -> bool:
        self._remove_expired_tombstones()
        leased = self._lease_one()
        if leased is None:
            return False
        request_id, attempt = leased
        try:
            target_type, family_id, target_id = self._target(request_id, attempt)
            self._delete_media(target_type, family_id, target_id)
            self._purge_database(request_id, attempt, target_type, family_id, target_id)
            logger.info(
                "data_deletion_completed request_id=%s target_type=%s attempt=%s",
                request_id,
                target_type,
                attempt,
            )
        except SQLAlchemyError:
            self._record_failure(request_id, attempt, retryable=True)
            raise
        except Exception as exc:
            self._record_failure(request_id, attempt, retryable=True)
            logger.warning(
                "data_deletion_attempt_failed request_id=%s attempt=%s error_type=%s",
                request_id,
                attempt,
                type(exc).__name__,
            )
        return True

    def _remove_expired_tombstones(self) -> None:
        with self.database.session_factory() as db:
            db.execute(
                delete(DeletionRequest).where(
                    DeletionRequest.state == DeletionState.succeeded.value,
                    DeletionRequest.expires_at.is_not(None),
                    DeletionRequest.expires_at < utcnow(),
                )
            )
            db.commit()

    def _lease_one(self) -> tuple[str, int] | None:
        with self.database.session_factory() as db:
            now = utcnow()
            item = db.scalar(
                select(DeletionRequest)
                .where(
                    or_(
                        DeletionRequest.state == DeletionState.queued.value,
                        (DeletionRequest.state == DeletionState.running.value)
                        & (DeletionRequest.lease_until < now),
                    ),
                    DeletionRequest.available_at <= now,
                )
                .order_by(DeletionRequest.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if item is None:
                return None
            if not item.id:
                raise RuntimeError("deletion request is missing its id")
            if (item.attempts or 0) >= (item.max_attempts or 3):
                item.state = DeletionState.failed.value
                item.error_code = "cleanup_failed"
                item.lease_until = None
                db.commit()
                return None
            item.state = DeletionState.running.value
            item.attempts = (item.attempts or 0) + 1
            item.lease_until = now + timedelta(minutes=5)
            item.error_code = None
            db.commit()
            return item.id, item.attempts

    def _target(self, request_id: str, attempt: int) -> tuple[str, str, str]:
        with self.database.session_factory() as db:
            item = db.scalar(select(DeletionRequest).where(DeletionRequest.id == request_id))
            if (
                item is None
                or item.state != DeletionState.running.value
                or item.attempts != attempt
                or not item.target_type
                or not item.family_id
                or not item.target_id
            ):
                raise RuntimeError("deletion lease changed")
            return item.target_type, item.family_id, item.target_id

    def _delete_media(self, target_type: str, family_id: str, target_id: str) -> None:
        child_id = target_id if target_type == "child" else None
        with self.database.session_factory() as db:
            submission_ids = LearningService.deletion_submission_ids(db, family_id, child_id)
            refs, paths = MediaCleanup.inventory(db, family_id, submission_ids)
        for ref in refs:
            self.media_store.delete(ref)
        if isinstance(self.media_store, WeChatCloudMediaStore):
            for path in paths:
                self.media_store.delete_path(path)

    def _purge_owned_rows(self, db, family_id: str, child_id: str | None) -> None:
        submission_ids = LearningService.deletion_submission_ids(db, family_id, child_id)
        PlanningService.purge_data(db, family_id, child_id)
        ActivitiesService.purge_data(db, family_id, child_id)
        TravelService.purge_data(db, family_id, child_id)
        MediaCleanup.purge_rows(db, submission_ids)
        LearningService.purge_data(db, family_id, child_id)
        ChildrenService.purge_data(db, family_id, child_id)

    def _purge_database(
        self,
        request_id: str,
        attempt: int,
        target_type: str,
        family_id: str,
        target_id: str,
    ) -> None:
        with self.database.session_factory() as db:
            item = db.scalar(
                select(DeletionRequest).where(DeletionRequest.id == request_id).with_for_update()
            )
            if (
                item is None
                or item.state != DeletionState.running.value
                or item.attempts != attempt
            ):
                db.rollback()
                return
            if target_type == "child":
                child = db.scalar(
                    select(Child)
                    .where(
                        Child.id == target_id,
                        Child.family_id == family_id,
                        Child.deleting.is_(True),
                    )
                    .with_for_update()
                )
                if child is None:
                    raise RuntimeError("deleting child is missing")
                self._purge_owned_rows(db, family_id, target_id)
            elif target_type == "family":
                family = db.scalar(
                    select(Family)
                    .where(Family.id == family_id, Family.status == "deleting")
                    .with_for_update()
                )
                if family is None:
                    raise RuntimeError("deleting family is missing")
                self._purge_owned_rows(db, family_id, None)
                FamilyService.purge_data(db, family_id)
            else:
                raise RuntimeError("unsupported deletion target")
            now = utcnow()
            item.state = DeletionState.succeeded.value
            item.target_id = None
            item.family_id = None
            item.error_code = None
            item.lease_until = None
            item.completed_at = now
            item.expires_at = now + timedelta(days=30)
            db.commit()

    def _record_failure(self, request_id: str, attempt: int, retryable: bool) -> None:
        with self.database.session_factory() as db:
            item = db.scalar(
                select(DeletionRequest)
                .where(DeletionRequest.id == request_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if (
                item is None
                or item.state != DeletionState.running.value
                or item.attempts != attempt
            ):
                db.rollback()
                return
            if retryable and item.attempts < (item.max_attempts or 3):
                item.state = DeletionState.queued.value
                item.available_at = utcnow() + timedelta(seconds=item.attempts or 1)
            else:
                item.state = DeletionState.failed.value
            item.error_code = "cleanup_failed"
            item.lease_until = None
            db.commit()
