"""Background notification tick.

Planning and sending are folded into one loop on purpose: both must run on wall-clock time and both
are idempotent, so a restart in the middle of a tick can only repeat work, never lose or duplicate a
message. Every iteration is fully re-derived from current facts.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.service import NotificationChannel, NotificationsService
from push_kids.platform.database import Database

logger = logging.getLogger("push_kids.notifications")

MAX_BACKOFF_SECONDS = 300


class NotificationScheduler:
    def __init__(
        self,
        database: Database,
        channel: NotificationChannel,
        tick_seconds: float = 30.0,
    ) -> None:
        self.database = database
        self.channel = channel
        self.tick_seconds = tick_seconds
        self._stop = asyncio.Event()
        self._running = False
        self._healthy = False
        self._consecutive_failures = 0

    @property
    def is_ready(self) -> bool:
        return self._running and self._healthy and not self._stop.is_set()

    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        self._running = True
        logger.info("notification_scheduler_started tick_seconds=%s", self.tick_seconds)
        try:
            while not self._stop.is_set():
                try:
                    await asyncio.to_thread(self.tick)
                except Exception as exc:
                    self._healthy = False
                    self._consecutive_failures += 1
                    delay = min(MAX_BACKOFF_SECONDS, 2 ** min(self._consecutive_failures, 8))
                    logger.warning(
                        "notification_tick_failed error_type=%s consecutive_failures=%s",
                        type(exc).__name__,
                        self._consecutive_failures,
                    )
                    await self._wait(delay)
                    continue
                self._healthy = True
                self._consecutive_failures = 0
                await self._wait(self.tick_seconds)
        finally:
            self._running = False
            self._healthy = False
            logger.info("notification_scheduler_stopped")

    async def _wait(self, delay: float) -> None:
        with suppress(TimeoutError, asyncio.TimeoutError):
            await asyncio.wait_for(self._stop.wait(), timeout=delay)

    def tick(self) -> dict[str, int]:
        with self.database.session_factory() as db:
            swept = NotificationsService.sweep(db)
            planned = NotificationPlanner.plan_all(db)
            dispatched = NotificationsService.dispatch_due(db, self.channel)
        report = {**swept, **planned, **dispatched}
        if any(report.values()):
            logger.info(
                "notification_tick queued=%s cancelled=%s sent=%s skipped=%s retried=%s "
                "failed=%s dropped=%s revoked=%s pruned=%s",
                planned["queued_member_applications"]
                + planned["queued_schedule_reminders"]
                + planned["queued_review_digests"],
                planned["cancelled"],
                dispatched["sent"],
                dispatched["skipped"],
                dispatched["retried"],
                dispatched["failed"],
                dispatched["dropped"],
                swept["revoked"],
                swept["pruned"],
            )
        return report
