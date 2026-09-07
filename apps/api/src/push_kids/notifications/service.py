"""Notification use cases: member-facing preferences plus the outbox dispatcher.

The dispatcher is deliberately request-free. It claims durable rows, resolves the recipient from
notification-owned tables only, sends best-effort and records a safe result code. It never invents a
success: an unconfigured channel, a missing grant or a refused user all end in an explicit terminal
state that the interface can show truthfully.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.families.service import FamilyService
from push_kids.notifications.destinations import DestinationCipher, DestinationCipherError
from push_kids.notifications.domain import KINDS, kind_for, retry_delay_seconds
from push_kids.notifications.outbox import NotificationOutbox
from push_kids.notifications.providers import NotificationSender, build_sender
from push_kids.notifications.schemas import (
    ChannelView,
    DeliveryView,
    NotificationSettingsView,
    PreferenceView,
    SubscriptionRegister,
)
from push_kids.notifications.templates import TemplateBinding, parse_templates
from push_kids.persistence.models import (
    DeliveryState,
    MemberRole,
    NotificationDelivery,
    NotificationDestination,
    NotificationPreference,
    NotificationSubscription,
    SubscriptionStatus,
)
from push_kids.platform.config import Settings
from push_kids.platform.context import RequestContext
from push_kids.platform.errors import ForbiddenError, NotFoundError
from push_kids.platform.time import utcnow

logger = logging.getLogger("push_kids")

LEASE_SECONDS = 120
DISPATCH_BATCH = 50
UNLIMITED_QUOTA = -1
# Terminal delivery rows are kept only long enough to explain recent behaviour in the interface.
RETENTION_DAYS = 30
TERMINAL_STATES = (
    DeliveryState.sent.value,
    DeliveryState.skipped.value,
    DeliveryState.failed.value,
    DeliveryState.cancelled.value,
)


@dataclass(frozen=True)
class NotificationChannel:
    """Runtime channel state assembled once at startup from deployment configuration."""

    sender: NotificationSender
    bindings: dict[str, TemplateBinding]
    cipher: DestinationCipher | None
    # Local and test deployments have no WeChat OpenID. They may bind a non-routable receiver so
    # the whole flow stays testable; a cloud deployment must never accept one.
    local_receiver_allowed: bool = False

    @property
    def available(self) -> bool:
        return self.sender.available and self.cipher is not None and bool(self.bindings)

    @property
    def reason(self) -> str:
        if not self.sender.available:
            return self.sender.unavailable_reason
        if self.cipher is None:
            return "缺少通知加密密钥，无法安全保存接收标识"
        if not self.bindings:
            return "尚未配置微信订阅消息模板"
        return ""

    def binding(self, type_name: str) -> TemplateBinding | None:
        return self.bindings.get(type_name)


def build_channel(settings: Settings) -> NotificationChannel:
    """Assemble the channel once at startup from deployment configuration.

    A misconfigured channel must not take the API down, and it must not pretend to work either: the
    result reports itself unavailable and every queued message ends as `skipped`.
    """
    secret = settings.notification_secret_value
    cipher: DestinationCipher | None = None
    if len(secret) >= 32:
        cipher = DestinationCipher(secret)
    elif settings.notification_channel == "recording":
        # Deterministic local key: the recording sender never leaves the process.
        cipher = DestinationCipher("push-kids-local-recording-destination-key")
    try:
        bindings = parse_templates(settings.notification_templates)
    except ValueError as exc:
        # A broken template map disables reminders; it must not take the whole API down.
        logger.warning("notification_templates_invalid reason=%s", exc)
        bindings = {}
    return NotificationChannel(
        sender=build_sender(settings),
        bindings=bindings,
        cipher=cipher,
        local_receiver_allowed=not settings.is_cloud,
    )


class NotificationsService:
    @staticmethod
    def _require_member(context: RequestContext) -> str:
        if not context.member_id:
            raise ForbiddenError("当前环境没有家庭成员身份，无法管理提醒")
        return context.member_id

    @classmethod
    def _preference_rows(cls, db: Session, member_id: str) -> dict[str, NotificationPreference]:
        rows = db.scalars(
            select(NotificationPreference).where(NotificationPreference.member_id == member_id)
        )
        return {str(row.type): row for row in rows}

    @classmethod
    def _subscription_rows(cls, db: Session, member_id: str) -> dict[str, NotificationSubscription]:
        rows = db.scalars(
            select(NotificationSubscription).where(NotificationSubscription.member_id == member_id)
        )
        return {str(row.type): row for row in rows}

    @classmethod
    def settings_view(
        cls, db: Session, context: RequestContext, channel: NotificationChannel
    ) -> NotificationSettingsView:
        member_id = cls._require_member(context)
        preferences = cls._preference_rows(db, member_id)
        subscriptions = cls._subscription_rows(db, member_id)
        is_manager = context.role == MemberRole.manager.value
        views: list[PreferenceView] = []
        template_ids: list[str] = []
        long_term = False
        for kind in KINDS:
            if kind.managers_only and not is_manager:
                continue
            binding = channel.binding(kind.type)
            if binding is not None:
                template_ids.append(binding.template_id)
                long_term = long_term or binding.long_term
            stored = preferences.get(kind.type)
            subscription = subscriptions.get(kind.type)
            views.append(
                PreferenceView(
                    type=kind.type,
                    label=kind.label,
                    description=kind.description,
                    enabled=bool(stored.enabled) if stored is not None else kind.default_enabled,
                    managers_only=kind.managers_only,
                    template_id=binding.template_id if binding else None,
                    subscription_status=(
                        subscription.status if subscription else SubscriptionStatus.unknown.value
                    ),
                    remaining_quota=subscription.remaining_quota if subscription else 0,
                )
            )
        last_sent_at = db.scalar(
            select(NotificationDelivery.sent_at)
            .where(
                NotificationDelivery.member_id == member_id,
                NotificationDelivery.state == DeliveryState.sent.value,
            )
            .order_by(NotificationDelivery.sent_at.desc())
            .limit(1)
        )
        return NotificationSettingsView(
            channel=ChannelView(
                available=channel.available,
                reason=channel.reason,
                template_ids=template_ids,
                long_term=long_term,
            ),
            preferences=views,
            last_sent_at=last_sent_at,
        )

    @classmethod
    def update_preference(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        type_name: str,
        enabled: bool,
    ) -> NotificationSettingsView:
        member_id = cls._require_member(context)
        kind = kind_for(type_name)
        if kind.managers_only and context.role != MemberRole.manager.value:
            raise ForbiddenError("只有家庭管理员可以管理审批提醒")
        row = db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.member_id == member_id,
                NotificationPreference.type == type_name,
            )
        )
        if row is None:
            row = NotificationPreference(
                family_id=context.family_id,
                member_id=member_id,
                type=type_name,
                enabled=enabled,
            )
            db.add(row)
        else:
            row.enabled = enabled
            row.updated_at = utcnow()
        db.commit()
        return cls.settings_view(db, context, channel)

    @classmethod
    def register_subscription(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        body: SubscriptionRegister,
    ) -> NotificationSettingsView:
        """Record a WeChat grant. Without a usable channel this stores nothing and stays honest."""
        member_id = cls._require_member(context)
        if not channel.available or channel.cipher is None:
            # Storing a grant that can never be spent would show a switched-on reminder that
            # never arrives, so the request is refused instead.
            raise NotFoundError("当前部署未开启微信提醒")
        receiver = context.openid
        if not receiver and channel.local_receiver_allowed and context.subject_hmac:
            receiver = f"local:{context.subject_hmac}"
        if not receiver:
            raise ForbiddenError("只有在微信小程序内才能开启微信提醒")
        existing = db.scalar(
            select(NotificationDestination).where(NotificationDestination.member_id == member_id)
        )
        ciphertext = channel.cipher.encrypt(receiver)
        if existing is None:
            db.add(
                NotificationDestination(
                    family_id=context.family_id,
                    member_id=member_id,
                    actor_binding_id=context.actor_binding_id,
                    app_id=context.app_id or "unknown",
                    key_version=channel.cipher.version,
                    ciphertext=ciphertext,
                    status="active",
                )
            )
        else:
            existing.ciphertext = ciphertext
            existing.key_version = channel.cipher.version
            existing.actor_binding_id = context.actor_binding_id
            existing.app_id = context.app_id or existing.app_id
            existing.status = "active"
            existing.updated_at = utcnow()
        subscriptions = cls._subscription_rows(db, member_id)
        now = utcnow()
        for result in body.results:
            kind = kind_for(result.type)
            if kind.managers_only and context.role != MemberRole.manager.value:
                continue
            binding = channel.binding(kind.type)
            # A long-term template keeps sending; a one-off grant pays for exactly one message.
            quota = UNLIMITED_QUOTA if binding and binding.long_term else 1
            row = subscriptions.get(result.type)
            status = (
                SubscriptionStatus.accepted.value
                if result.accepted
                else SubscriptionStatus.rejected.value
            )
            if row is None:
                db.add(
                    NotificationSubscription(
                        family_id=context.family_id,
                        member_id=member_id,
                        type=result.type,
                        status=status,
                        remaining_quota=quota if result.accepted else 0,
                        granted_at=now if result.accepted else None,
                    )
                )
                continue
            row.status = status
            row.updated_at = now
            if result.accepted:
                row.granted_at = now
                stored_quota = int(row.remaining_quota or 0)
                row.remaining_quota = (
                    UNLIMITED_QUOTA if quota == UNLIMITED_QUOTA else max(0, stored_quota) + 1
                )
            else:
                row.remaining_quota = 0
        db.commit()
        return cls.settings_view(db, context, channel)

    @classmethod
    def recent_deliveries(
        cls, db: Session, context: RequestContext, limit: int = 10
    ) -> list[DeliveryView]:
        member_id = cls._require_member(context)
        rows = db.scalars(
            select(NotificationDelivery)
            .where(NotificationDelivery.member_id == member_id)
            .order_by(NotificationDelivery.scheduled_at.desc())
            .limit(limit)
        )
        views: list[DeliveryView] = []
        for row in rows:
            payload = json.loads(row.payload_json or "{}")
            views.append(
                DeliveryView(
                    type=row.type,
                    state=row.state,
                    headline=str(payload.get("headline") or ""),
                    detail=str(payload.get("detail") or ""),
                    scheduled_at=row.scheduled_at,
                    sent_at=row.sent_at,
                    result_code=row.result_code,
                )
            )
        return views

    @staticmethod
    def _claim(
        db: Session, now: datetime, limit: int
    ) -> list[NotificationDelivery]:  # pragma: no cover - exercised through dispatch_due
        statement = (
            select(NotificationDelivery)
            .where(
                NotificationDelivery.state == DeliveryState.pending.value,
                NotificationDelivery.scheduled_at <= now,
                NotificationDelivery.available_at <= now,
            )
            .order_by(NotificationDelivery.scheduled_at)
            .limit(limit)
        )
        if db.bind is not None and db.bind.dialect.name == "mysql":
            statement = statement.with_for_update(skip_locked=True)
        rows = list(db.scalars(statement))
        for row in rows:
            row.state = DeliveryState.sending.value
            row.attempts = int(row.attempts or 0) + 1
            row.lease_until = now + timedelta(seconds=LEASE_SECONDS)
            row.updated_at = now
        db.commit()
        return rows

    @classmethod
    def _terminate(
        cls, db: Session, row: NotificationDelivery, state: DeliveryState, code: str
    ) -> None:
        row.state = state.value
        row.result_code = code
        row.updated_at = utcnow()
        if state is DeliveryState.sent:
            row.sent_at = utcnow()
        db.commit()

    @classmethod
    def reclaim_expired(cls, db: Session, now: datetime | None = None) -> int:
        """Return leases abandoned by a crashed dispatcher so a message is not silently lost."""
        current = now or utcnow()
        rows = list(
            db.scalars(
                select(NotificationDelivery).where(
                    NotificationDelivery.state == DeliveryState.sending.value,
                    NotificationDelivery.lease_until.is_not(None),
                    NotificationDelivery.lease_until < current,
                )
            )
        )
        for row in rows:
            if int(row.attempts or 0) >= int(row.max_attempts or 3):
                row.state = DeliveryState.failed.value
                row.result_code = "lease_expired"
            else:
                row.state = DeliveryState.pending.value
                row.available_at = current
            row.lease_until = None
            row.updated_at = current
        if rows:
            db.commit()
        return len(rows)

    @classmethod
    def revoke_departed(cls, db: Session) -> int:
        """Cut the channel for members who no longer belong to the family.

        Leaving a family must stop delivery, not only future planning: the stored receiver is
        deactivated, the WeChat grant is dropped and queued messages are cancelled. Without this a
        removed member would keep receiving another family's child names.
        """
        holders: set[str] = set()
        holders.update(
            str(value)
            for value in db.scalars(
                select(NotificationDestination.member_id).where(
                    NotificationDestination.status == "active"
                )
            )
        )
        holders.update(
            str(value)
            for value in db.scalars(
                select(NotificationSubscription.member_id).where(
                    NotificationSubscription.status == SubscriptionStatus.accepted.value
                )
            )
        )
        holders.update(
            str(value)
            for value in db.scalars(
                select(NotificationDelivery.member_id).where(
                    NotificationDelivery.state.in_(
                        (DeliveryState.pending.value, DeliveryState.sending.value)
                    )
                )
            )
        )
        departed = holders - FamilyService.active_member_ids(db, holders)
        if not departed:
            return 0
        now = utcnow()
        for destination in db.scalars(
            select(NotificationDestination).where(
                NotificationDestination.member_id.in_(departed),
                NotificationDestination.status == "active",
            )
        ):
            destination.status = "revoked"
            destination.updated_at = now
        for subscription in db.scalars(
            select(NotificationSubscription).where(NotificationSubscription.member_id.in_(departed))
        ):
            subscription.status = SubscriptionStatus.revoked.value
            subscription.remaining_quota = 0
            subscription.updated_at = now
        for delivery in db.scalars(
            select(NotificationDelivery).where(
                NotificationDelivery.member_id.in_(departed),
                NotificationDelivery.state.in_(
                    (DeliveryState.pending.value, DeliveryState.sending.value)
                ),
            )
        ):
            delivery.state = DeliveryState.cancelled.value
            delivery.result_code = "member_departed"
            delivery.lease_until = None
            delivery.updated_at = now
        db.commit()
        logger.info("notification_channel_revoked members=%s", len(departed))
        return len(departed)

    @classmethod
    def prune_history(cls, db: Session, now: datetime | None = None) -> int:
        """Drop delivery history past the retention window so the outbox stays bounded."""
        cutoff = (now or utcnow()) - timedelta(days=RETENTION_DAYS)
        rows = list(
            db.scalars(
                select(NotificationDelivery).where(
                    NotificationDelivery.state.in_(TERMINAL_STATES),
                    NotificationDelivery.updated_at < cutoff,
                )
            )
        )
        for row in rows:
            db.delete(row)
        if rows:
            db.commit()
        return len(rows)

    @classmethod
    def sweep(cls, db: Session, now: datetime | None = None) -> dict[str, int]:
        """Channel maintenance that must run on every tick, before anything is sent."""
        return {
            "revoked": cls.revoke_departed(db),
            "pruned": cls.prune_history(db, now),
        }

    @classmethod
    def dispatch_due(
        cls,
        db: Session,
        channel: NotificationChannel,
        now: datetime | None = None,
        limit: int = DISPATCH_BATCH,
    ) -> dict[str, int]:
        current = now or utcnow()
        counts = {"sent": 0, "skipped": 0, "retried": 0, "failed": 0, "dropped": 0}
        cls.reclaim_expired(db, current)
        claimed = cls._claim(db, current, limit)
        # Membership is re-checked at send time: a row may have been queued before the member left.
        active_members = FamilyService.active_member_ids(
            db, {str(row.member_id) for row in claimed}
        )
        for row in claimed:
            type_name = str(row.type)
            member_id = str(row.member_id)
            if member_id not in active_members:
                cls._terminate(db, row, DeliveryState.cancelled, "member_departed")
                counts["dropped"] += 1
                continue
            binding = channel.binding(type_name)
            if not channel.available or binding is None:
                cls._terminate(db, row, DeliveryState.skipped, "channel_unavailable")
                counts["skipped"] += 1
                continue
            if not NotificationOutbox.is_enabled(db, member_id, type_name):
                cls._terminate(db, row, DeliveryState.skipped, "member_disabled")
                counts["skipped"] += 1
                continue
            subscription = db.scalar(
                select(NotificationSubscription).where(
                    NotificationSubscription.member_id == member_id,
                    NotificationSubscription.type == type_name,
                )
            )
            quota = int(subscription.remaining_quota or 0) if subscription is not None else 0
            authorised = (
                subscription is not None
                and subscription.status == SubscriptionStatus.accepted.value
                and (quota == UNLIMITED_QUOTA or quota > 0)
            )
            if not authorised:
                cls._terminate(db, row, DeliveryState.skipped, "not_authorized")
                counts["skipped"] += 1
                continue
            destination = db.scalar(
                select(NotificationDestination).where(
                    NotificationDestination.member_id == member_id,
                    NotificationDestination.status == "active",
                )
            )
            if destination is None or channel.cipher is None:
                cls._terminate(db, row, DeliveryState.skipped, "no_destination")
                counts["skipped"] += 1
                continue
            try:
                receiver = channel.cipher.decrypt(str(destination.ciphertext))
            except DestinationCipherError:
                logger.warning("notification_destination_undecryptable type=%s", type_name)
                cls._terminate(db, row, DeliveryState.failed, "destination_unreadable")
                counts["failed"] += 1
                continue
            payload = json.loads(row.payload_json or "{}")
            values = {str(k): str(v) for k, v in (payload.get("fields") or {}).items()}
            missing = binding.missing_fields(values)
            if missing:
                # WeChat rejects the whole message when a mapped slot is empty, and a rejected
                # one-off message still costs the member's grant, so the mismatch is reported as a
                # diagnosable skip. Only field keys are logged, never their values.
                logger.warning(
                    "notification_template_field_missing type=%s fields=%s",
                    type_name,
                    ",".join(missing),
                )
                cls._terminate(db, row, DeliveryState.skipped, "template_field_missing")
                counts["skipped"] += 1
                continue
            outcome = channel.sender.send(
                receiver=receiver,
                binding=binding,
                values=values,
                deep_link=str(payload.get("deep_link") or ""),
            )
            if outcome.status == "sent":
                if subscription is not None and quota > 0:
                    subscription.remaining_quota = quota - 1
                    if quota - 1 == 0:
                        # A spent one-off grant must be re-requested by the member.
                        subscription.status = SubscriptionStatus.expired.value
                cls._terminate(db, row, DeliveryState.sent, outcome.code)
                counts["sent"] += 1
                continue
            if outcome.status == "retry" and int(row.attempts or 0) < int(row.max_attempts or 3):
                row.state = DeliveryState.pending.value
                row.available_at = current + timedelta(
                    seconds=retry_delay_seconds(int(row.attempts or 1))
                )
                row.lease_until = None
                row.result_code = outcome.code
                row.updated_at = current
                db.commit()
                counts["retried"] += 1
                continue
            if outcome.code == "user_refused" and subscription is not None:
                subscription.status = SubscriptionStatus.rejected.value
                subscription.remaining_quota = 0
            cls._terminate(db, row, DeliveryState.failed, outcome.code)
            counts["failed"] += 1
        return counts
