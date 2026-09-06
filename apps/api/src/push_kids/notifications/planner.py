"""Turns family facts into queued notifications.

The planner is idempotent by construction: every tick re-derives the set of messages that *should*
exist in a bounded window, refreshes the matching pending rows and cancels the pending rows that no
longer describe reality. Nothing here decides schedules or review dates; it only reads them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from push_kids.activities.service import ActivitiesService
from push_kids.families.service import AudienceMember, FamilyService
from push_kids.notifications.domain import (
    MEMBER_APPLICATION,
    REVIEW_DIGEST,
    SCHEDULE_REMINDER,
    ChildReviewLoad,
    local_datetime_text,
    member_application_content,
    member_application_key,
    review_digest_content,
    review_digest_key,
    schedule_reminder_content,
    schedule_reminder_key,
)
from push_kids.notifications.outbox import EnqueueOutcome, NotificationOutbox
from push_kids.planning.service import PlanningService
from push_kids.platform.time import SHANGHAI, local_date, utcnow

# A reminder is planned only shortly before it is needed: a wider horizon would keep rows for
# schedules that are still likely to be edited.
SCHEDULE_LOOKAHEAD = timedelta(hours=3)
SCHEDULE_LEAD = timedelta(minutes=60)
DIGEST_HOUR = 19
# Pending join requests are cancelled by their own lifecycle, so the sweep window only has to be
# wide enough to cover any row this planner could have created earlier.
APPLICATION_SWEEP = timedelta(days=365)


@dataclass(frozen=True)
class PlanResult:
    queued: int = 0
    refreshed: int = 0
    cancelled: int = 0


# A re-armed row is a message that is being queued for its first real attempt, so it counts as
# queued; a refreshed row was already waiting and only moved.
_QUEUED_OUTCOMES = {EnqueueOutcome.created, EnqueueOutcome.rearmed}


def _tally(outcomes: list[EnqueueOutcome], cancelled: int = 0) -> PlanResult:
    return PlanResult(
        queued=sum(1 for item in outcomes if item in _QUEUED_OUTCOMES),
        refreshed=sum(1 for item in outcomes if item is EnqueueOutcome.refreshed),
        cancelled=cancelled,
    )


class NotificationPlanner:
    @classmethod
    def plan_member_applications(cls, db: Session, now: datetime | None = None) -> PlanResult:
        """Ask every manager of the family to review a still-pending join request."""
        current = now or utcnow()
        outcomes: list[EnqueueOutcome] = []
        keep: set[str] = set()
        for application in FamilyService.pending_applications(db):
            managers = FamilyService.notification_audience(
                db, application.family_id, managers_only=True
            )
            content = member_application_content(
                application.relationship_label,
                application.request_code,
                local_datetime_text(application.created_at.astimezone(SHANGHAI)),
            )
            for manager in managers:
                key = member_application_key(application.request_id, manager.member_id)
                keep.add(key)
                outcomes.append(
                    NotificationOutbox.enqueue(
                        db,
                        family_id=application.family_id,
                        type_name=MEMBER_APPLICATION.type,
                        member_id=manager.member_id,
                        dedupe_key=key,
                        content=content,
                        scheduled_at=current,
                    )
                )
        cancelled = NotificationOutbox.cancel_pending_outside(
            db,
            type_name=MEMBER_APPLICATION.type,
            window_start=current - APPLICATION_SWEEP,
            window_end=current + timedelta(hours=1),
            keep_keys=keep,
        )
        db.commit()
        return _tally(outcomes, cancelled)

    @classmethod
    def plan_schedule_reminders(cls, db: Session, now: datetime | None = None) -> PlanResult:
        """Tell the whole family which child has what, and when, one hour ahead."""
        current = now or utcnow()
        window_end = current + SCHEDULE_LOOKAHEAD
        occurrences = ActivitiesService.occurrences_in_window(db, current, window_end)
        audiences: dict[str, list[AudienceMember]] = {}
        outcomes: list[EnqueueOutcome] = []
        keep: set[str] = set()
        for occurrence in occurrences:
            # A schedule starting in less than an hour is still worth one prompt, so the send time
            # is clamped to now instead of silently dropping the reminder.
            send_at = max(occurrence.start_at - SCHEDULE_LEAD, current)
            lead_minutes = max(0, int((occurrence.start_at - send_at).total_seconds() // 60))
            content = schedule_reminder_content(
                occurrence.child_name,
                occurrence.name,
                occurrence.start_time_text,
                lead_minutes,
                start_datetime_text=local_datetime_text(occurrence.start_at.astimezone(SHANGHAI)),
                duration_minutes=occurrence.duration_minutes,
                notified_at_text=local_datetime_text(send_at.astimezone(SHANGHAI)),
            )
            if occurrence.family_id not in audiences:
                audiences[occurrence.family_id] = FamilyService.notification_audience(
                    db, occurrence.family_id
                )
            for member in audiences[occurrence.family_id]:
                key = schedule_reminder_key(
                    occurrence.occurrence_id, occurrence.local_day, member.member_id
                )
                keep.add(key)
                outcomes.append(
                    NotificationOutbox.enqueue(
                        db,
                        family_id=occurrence.family_id,
                        type_name=SCHEDULE_REMINDER.type,
                        member_id=member.member_id,
                        dedupe_key=key,
                        content=content,
                        scheduled_at=send_at,
                    )
                )
        cancelled = NotificationOutbox.cancel_pending_outside(
            db,
            type_name=SCHEDULE_REMINDER.type,
            window_start=current,
            window_end=window_end - SCHEDULE_LEAD,
            keep_keys=keep,
        )
        db.commit()
        return _tally(outcomes, cancelled)

    @classmethod
    def plan_review_digests(cls, db: Session, now: datetime | None = None) -> PlanResult:
        """At 19:00 Asia/Shanghai, report what is still not reviewed. Silent when nothing is due."""
        current = now or utcnow()
        local = current.astimezone(SHANGHAI)
        if local.hour < DIGEST_HOUR:
            return PlanResult()
        day = local_date(current)
        by_family: dict[str, list[ChildReviewLoad]] = {}
        for load in PlanningService.pending_review_loads(db, day):
            by_family.setdefault(load.family_id, []).append(
                ChildReviewLoad(
                    child_name=load.child_name,
                    pending_count=load.pending_count,
                    subject_names=load.subject_names,
                )
            )
        outcomes: list[EnqueueOutcome] = []
        for family_id, loads in by_family.items():
            content = review_digest_content(loads)
            if content is None:
                continue
            for member in FamilyService.notification_audience(db, family_id):
                outcomes.append(
                    NotificationOutbox.enqueue(
                        db,
                        family_id=family_id,
                        type_name=REVIEW_DIGEST.type,
                        member_id=member.member_id,
                        dedupe_key=review_digest_key(day, member.member_id),
                        content=content,
                        scheduled_at=current,
                    )
                )
        db.commit()
        return _tally(outcomes)

    @classmethod
    def plan_all(cls, db: Session, now: datetime | None = None) -> dict[str, int]:
        current = now or utcnow()
        applications = cls.plan_member_applications(db, current)
        schedules = cls.plan_schedule_reminders(db, current)
        digests = cls.plan_review_digests(db, current)
        return {
            "queued_member_applications": applications.queued,
            "queued_schedule_reminders": schedules.queued,
            "queued_review_digests": digests.queued,
            "refreshed": applications.refreshed + schedules.refreshed + digests.refreshed,
            "cancelled": applications.cancelled + schedules.cancelled,
        }
