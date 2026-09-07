"""The single place that turns a notification intent into a durable row.

The planner is a *reader* of other domains: `families`, `activities` and `planning` never import
notifications, so the package graph stays acyclic while this module owns queue semantics —
per-member opt-in, WeChat grant balance, dedupe, in-place refresh and cancellation of superseded
reminders.
"""

from __future__ import annotations

import enum
import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.families.service import FamilyService
from push_kids.notifications.domain import NotificationContent, kind_for
from push_kids.persistence.models import (
    DeliveryState,
    NotificationDelivery,
    NotificationDeliveryChild,
    NotificationPreference,
    NotificationSubscription,
    SubscriptionStatus,
)
from push_kids.platform.time import utcnow

UNLIMITED_QUOTA = -1
# A message skipped for a condition the member can still fix may be re-armed once that condition
# changes. `sent`, `failed` and `cancelled` are never resurrected.
RE_ARMABLE_RESULT_CODES = {
    "channel_unavailable",
    "member_disabled",
    "not_authorized",
    # A template whose slots do not match the content is a deployment mistake, so the reminder is
    # allowed to go out once the mapping is corrected.
    "template_field_missing",
}


class EnqueueOutcome(enum.StrEnum):
    created = "created"
    refreshed = "refreshed"
    rearmed = "rearmed"
    skipped = "skipped"


class NotificationOutbox:
    @staticmethod
    def _sync_child_scope(db: Session, delivery_id: str, child_ids: tuple[str, ...]) -> None:
        target = set(child_ids)
        rows = list(
            db.scalars(
                select(NotificationDeliveryChild).where(
                    NotificationDeliveryChild.delivery_id == delivery_id
                )
            )
        )
        existing = {str(row.child_id): row for row in rows}
        for child_id, row in existing.items():
            if child_id not in target:
                db.delete(row)
        for child_id in target - existing.keys():
            db.add(NotificationDeliveryChild(delivery_id=delivery_id, child_id=child_id))

    @staticmethod
    def is_enabled(db: Session, member_id: str, type_name: str) -> bool:
        kind = kind_for(type_name)
        row = db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.member_id == member_id,
                NotificationPreference.type == type_name,
            )
        )
        if row is None:
            return kind.default_enabled
        return bool(row.enabled)

    @staticmethod
    def is_authorized(db: Session, member_id: str, type_name: str) -> bool:
        """True only while WeChat still allows one more message of this type to this member.

        Queueing without a grant would create rows that can only ever be skipped, so the check
        belongs here rather than only in the dispatcher.
        """
        row = db.scalar(
            select(NotificationSubscription).where(
                NotificationSubscription.member_id == member_id,
                NotificationSubscription.type == type_name,
            )
        )
        if row is None or row.status != SubscriptionStatus.accepted.value:
            return False
        quota = int(row.remaining_quota or 0)
        return quota == UNLIMITED_QUOTA or quota > 0

    @classmethod
    def can_receive(cls, db: Session, member_id: str, type_name: str) -> bool:
        return cls.is_enabled(db, member_id, type_name) and cls.is_authorized(
            db, member_id, type_name
        )

    @classmethod
    def enqueue(
        cls,
        db: Session,
        *,
        family_id: str,
        type_name: str,
        member_id: str,
        dedupe_key: str,
        content: NotificationContent,
        scheduled_at: datetime,
        child_ids: tuple[str, ...] = (),
    ) -> EnqueueOutcome:
        """Queue, refresh or re-arm exactly one message.

        A pending row is updated in place so an edited schedule moves instead of producing a second
        reminder. A row that already reached a terminal state is only revived when that state was a
        recoverable skip.
        """
        # Validates the type early; audience filtering stays with the caller that owns membership.
        kind_for(type_name)
        if not FamilyService.notification_member_is_active(db, family_id, member_id):
            return EnqueueOutcome.skipped
        if child_ids and not ChildrenService.notification_scope_is_active(
            db, family_id, set(child_ids)
        ):
            return EnqueueOutcome.skipped
        if not cls.can_receive(db, member_id, type_name):
            return EnqueueOutcome.skipped
        existing = db.scalar(
            select(NotificationDelivery).where(NotificationDelivery.dedupe_key == dedupe_key)
        )
        payload = json.dumps(content.as_payload(), ensure_ascii=False)
        if existing is not None:
            if existing.state == DeliveryState.pending.value:
                existing.scheduled_at = scheduled_at
                existing.payload_json = payload
                existing.available_at = scheduled_at
                cls._sync_child_scope(db, str(existing.id), child_ids)
                return EnqueueOutcome.refreshed
            if (
                existing.state == DeliveryState.skipped.value
                and existing.result_code in RE_ARMABLE_RESULT_CODES
            ):
                existing.state = DeliveryState.pending.value
                existing.scheduled_at = scheduled_at
                existing.available_at = scheduled_at
                existing.payload_json = payload
                existing.attempts = 0
                existing.lease_until = None
                existing.result_code = None
                existing.updated_at = utcnow()
                cls._sync_child_scope(db, str(existing.id), child_ids)
                return EnqueueOutcome.rearmed
            return EnqueueOutcome.skipped
        row = NotificationDelivery(
            family_id=family_id,
            member_id=member_id,
            type=type_name,
            dedupe_key=dedupe_key,
            payload_json=payload,
            scheduled_at=scheduled_at,
            available_at=scheduled_at,
            state=DeliveryState.pending.value,
        )
        db.add(row)
        try:
            db.flush()
        except IntegrityError:
            # A concurrent tick queued the same message first; that row is authoritative.
            db.rollback()
            return EnqueueOutcome.skipped
        cls._sync_child_scope(db, str(row.id), child_ids)
        return EnqueueOutcome.created

    @staticmethod
    def cancel_pending_outside(
        db: Session,
        *,
        type_name: str,
        window_start: datetime,
        window_end: datetime,
        keep_keys: set[str],
    ) -> int:
        """Cancel pending rows in the window that no longer match a real occurrence.

        This is how a deleted or moved schedule stops reminding: the recomputed desired set wins.
        """
        rows = list(
            db.scalars(
                select(NotificationDelivery).where(
                    NotificationDelivery.type == type_name,
                    NotificationDelivery.state == DeliveryState.pending.value,
                    NotificationDelivery.scheduled_at >= window_start,
                    NotificationDelivery.scheduled_at <= window_end,
                )
            )
        )
        cancelled = 0
        for row in rows:
            if row.dedupe_key in keep_keys:
                continue
            row.state = DeliveryState.cancelled.value
            row.result_code = "source_changed"
            row.updated_at = utcnow()
            cancelled += 1
        return cancelled
