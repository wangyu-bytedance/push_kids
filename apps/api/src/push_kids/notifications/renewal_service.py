"""Member opt-in, short-lived grant preparation and exactly-once local grant registration.

Preparation cannot prove an external WeChat grant. Unresolved calls stay blocked until their
original result is registered or the member explicitly starts a new manual authorization.
"""

from __future__ import annotations

import json
from datetime import timedelta
from hashlib import sha256

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from push_kids.families.service import FamilyService
from push_kids.notifications.renewal_policy import (
    COOLDOWN_COMPLETIONS,
    LEASE_SECONDS,
    auto_eligible,
    renewal_status,
)
from push_kids.notifications.schemas import (
    GrantAttemptView,
    GrantPreparationView,
    GrantPrepare,
    GrantRegister,
    RenewalTypeView,
    RenewalUpdate,
    RenewalView,
    SubscriptionRegister,
    SubscriptionResult,
)
from push_kids.notifications.service import NotificationChannel, NotificationsService
from push_kids.notifications.templates import TemplateBinding
from push_kids.persistence.models import (
    NotificationGrantAttempt,
    NotificationRenewalPreference,
    NotificationRenewalState,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.context import RequestContext
from push_kids.platform.errors import ConflictError, ForbiddenError, NotFoundError
from push_kids.platform.time import utcnow


def fingerprint(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def template_fingerprint(binding: TemplateBinding) -> str:
    return fingerprint([binding.template_id, binding.long_term, binding.fields])


class NotificationRenewalService:
    @staticmethod
    def _lock(db: Session, context: RequestContext) -> str:
        member = NotificationsService._require_member(context)
        if db.get_bind().dialect.name == "sqlite":
            # SQLite has no row-level FOR UPDATE; an owner-scoped no-op obtains its write lock.
            db.execute(
                update(NotificationRenewalPreference)
                .where(
                    NotificationRenewalPreference.family_id == context.family_id,
                    NotificationRenewalPreference.member_id == member,
                )
                .values(version=NotificationRenewalPreference.version)
            )
        if not FamilyService.notification_member_is_active(
            db, context.family_id, member, expected_role=context.role
        ):
            raise ForbiddenError("当前家庭成员身份已失效")
        return member

    @staticmethod
    def _preference(db: Session, context: RequestContext, *, locked: bool = False):
        statement = select(NotificationRenewalPreference).where(
            NotificationRenewalPreference.family_id == context.family_id,
            NotificationRenewalPreference.member_id == context.member_id,
        )
        return db.scalar(statement.with_for_update() if locked else statement)

    @staticmethod
    def _states(db: Session, context: RequestContext, *, locked: bool = False):
        statement = (
            select(NotificationRenewalState)
            .where(
                NotificationRenewalState.family_id == context.family_id,
                NotificationRenewalState.member_id == context.member_id,
            )
            .order_by(NotificationRenewalState.type)
            .limit(3)
        )
        return {
            str(row.type): row
            for row in db.scalars(statement.with_for_update() if locked else statement)
        }

    @classmethod
    def view(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        *,
        locked: bool = False,
    ) -> RenewalView:
        member = NotificationsService._require_member(context)
        settings = NotificationsService.settings_view(db, context, channel, locked=locked)
        preference = cls._preference(db, context, locked=locked)
        states = cls._states(db, context, locked=locked)
        cursor = PlanningService.completion_cursor(db, context.family_id, member, current=locked)
        choice = str(preference.choice) if preference else "unseen"
        types = []
        for item in settings.preferences:
            row = states.get(item.type)
            binding = channel.binding(item.type)
            matches = bool(
                row and binding and row.template_fingerprint == template_fingerprint(binding)
            )
            consented = bool(matches and row.consented)
            last_prompt = int(row.last_prompt_cursor) if matches else cursor
            pending = bool(matches and row.active_attempt_id)
            types.append(
                RenewalTypeView(
                    type=item.type,
                    status=renewal_status(
                        available=settings.channel.available and binding is not None,
                        enabled=item.enabled,
                        quota=item.remaining_quota,
                        consented=consented,
                        choice=choice,
                        completed=cursor,
                        last_prompt=last_prompt,
                        stop_reason=str(row.stop_reason) if matches and row.stop_reason else None,
                        pending=pending,
                    ),
                    consented=consented,
                    cooldown_remaining=max(0, COOLDOWN_COMPLETIONS - (cursor - last_prompt)),
                    active_attempt_id=str(row.active_attempt_id) if pending else None,
                )
            )
        return RenewalView(
            settings=settings,
            choice=choice,
            version=int(preference.version) if preference else 0,
            completion_cursor=cursor,
            types=types,
            server_time=utcnow(),
        )

    @classmethod
    def update(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        body: RenewalUpdate,
        key: str,
    ) -> RenewalView:
        member = cls._lock(db, context)
        row = cls._preference(db, context, locked=True)
        if row is None:
            row = NotificationRenewalPreference(
                family_id=context.family_id, member_id=member, choice="unseen", version=0
            )
            db.add(row)
        if (
            row.last_request_key == key
            and row.choice == body.choice
            and row.version == body.expected_version + 1
        ):
            return cls.view(db, context, channel, locked=True)
        if row.last_request_key == key:
            raise ConflictError("此设置标识已用于其他操作")
        if row.version != body.expected_version:
            raise ConflictError("提醒设置已在其他设备更新，请刷新后再试")
        row.choice = body.choice
        row.version += 1
        row.last_request_key = key
        row.updated_at = utcnow()
        db.commit()
        return cls.view(db, context, channel)

    @staticmethod
    def _attempt_view(row: NotificationGrantAttempt) -> GrantAttemptView:
        assert row.expires_at is not None and row.bindings_json is not None
        state = str(row.state)
        if state in {"prepared", "started"} and row.expires_at <= utcnow():
            state = "unknown"
        return GrantAttemptView(
            attempt_id=row.id,
            mode=row.mode,
            state=state,
            expires_at=row.expires_at,
            bindings=json.loads(row.bindings_json),
            result=GrantRegister.model_validate_json(row.result_json) if row.result_json else None,
        )

    @classmethod
    def _attempt(
        cls, db: Session, context: RequestContext, attempt_id: str
    ) -> NotificationGrantAttempt:
        row = db.scalar(
            select(NotificationGrantAttempt)
            .where(
                NotificationGrantAttempt.id == attempt_id,
                NotificationGrantAttempt.family_id == context.family_id,
                NotificationGrantAttempt.member_id == context.member_id,
            )
            .with_for_update()
        )
        if row is None:
            raise NotFoundError("没有找到这次授权记录")
        return row

    @classmethod
    def read_attempt(
        cls, db: Session, context: RequestContext, attempt_id: str
    ) -> GrantAttemptView:
        NotificationsService._require_member(context)
        return cls._attempt_view(cls._attempt(db, context, attempt_id))

    @classmethod
    def prepare(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        body: GrantPrepare,
        key: str,
    ) -> GrantPreparationView:
        member = cls._lock(db, context)
        request_hash = fingerprint(body.model_dump())
        existing = db.scalar(
            select(NotificationGrantAttempt)
            .where(
                NotificationGrantAttempt.family_id == context.family_id,
                NotificationGrantAttempt.member_id == member,
                NotificationGrantAttempt.request_key == key,
            )
            .with_for_update()
        )
        if existing:
            if existing.request_fingerprint != request_hash:
                raise ConflictError("此授权标识已用于其他操作")
            return GrantPreparationView(
                attempt=cls._attempt_view(existing),
                renewal=cls.view(db, context, channel, locked=True),
            )
        view = cls.view(db, context, channel, locked=True)
        if view.version != body.expected_version:
            raise ConflictError("提醒设置已更新，请刷新后再试")
        if len(set(body.types)) != len(body.types):
            raise ConflictError("提醒类型不可重复")
        visible = {item.type: item for item in view.settings.preferences}
        if any(name not in visible for name in body.types):
            raise ForbiddenError("无权管理这类提醒")
        states = cls._states(db, context, locked=True)
        statuses = {item.type: item.status for item in view.types}
        now = utcnow()
        bindings = []
        for name in sorted(body.types):
            item = visible[name]
            binding = channel.binding(name)
            if (
                not channel.available
                or not binding
                or not item.enabled
                or item.remaining_quota != 0
            ):
                continue
            row = states.get(name)
            template_hash = template_fingerprint(binding)
            if row is None:
                row = NotificationRenewalState(
                    family_id=context.family_id,
                    member_id=member,
                    type=name,
                    template_fingerprint=template_hash,
                    consented=False,
                    last_prompt_cursor=view.completion_cursor,
                )
                db.add(row)
                states[name] = row
            elif row.template_fingerprint != template_hash:
                row.template_fingerprint = template_hash
                row.consented = False
                row.last_prompt_cursor = view.completion_cursor
                row.active_attempt_id = None
                row.stop_reason = None
                row.retry_after = None
            remembered = body.remembered.get(name)
            if body.main_switch is False or remembered == "reject":
                row.stop_reason = (
                    "main_switch_off" if body.main_switch is False else "remembered_reject"
                )
                continue
            if row.active_attempt_id:
                old = cls._attempt(db, context, row.active_attempt_id)
                assert old.expires_at is not None
                if body.mode != "manual" or old.expires_at > now:
                    continue
                old.state = "unknown"
                row.active_attempt_id = None
            if body.mode == "auto":
                if (
                    not row.consented
                    or view.choice != "enabled"
                    or not auto_eligible(
                        status=statuses[name],
                        remembered=remembered,
                        main_switch=body.main_switch,
                        retry_ready=row.retry_after is None or row.retry_after <= now,
                    )
                ):
                    continue
            elif body.mode == "onboarding" and (
                view.choice != "unseen" or not item.previously_granted
            ):
                continue
            bindings.append(
                {"type": name, "template_id": binding.template_id, "fingerprint": template_hash}
            )
        attempt = None
        if bindings:
            attempt = NotificationGrantAttempt(
                family_id=context.family_id,
                member_id=member,
                request_key=key,
                request_fingerprint=request_hash,
                mode=body.mode,
                choice_version=view.version,
                bindings_json=json.dumps(bindings),
                state="prepared",
                expires_at=now + timedelta(seconds=LEASE_SECONDS),
            )
            db.add(attempt)
            db.flush()
            for entry in bindings:
                states[entry["type"]].active_attempt_id = attempt.id
        db.commit()
        return GrantPreparationView(
            attempt=cls._attempt_view(attempt) if attempt else None,
            renewal=cls.view(db, context, channel),
        )

    @classmethod
    def started(cls, db: Session, context: RequestContext, attempt_id: str) -> GrantAttemptView:
        cls._lock(db, context)
        row = cls._attempt(db, context, attempt_id)
        assert row.expires_at is not None
        if row.state == "prepared":
            row.state = "started" if row.expires_at > utcnow() else "unknown"
            db.commit()
        return cls._attempt_view(row)

    @classmethod
    def register(
        cls,
        db: Session,
        context: RequestContext,
        channel: NotificationChannel,
        attempt_id: str,
        body: GrantRegister,
    ) -> GrantAttemptView:
        member = cls._lock(db, context)
        row = cls._attempt(db, context, attempt_id)
        # Order-independent canonical outcomes; duplicates are never folded into an extra grant.
        payload = body.model_dump()
        payload["results"] = sorted(payload["results"], key=lambda item: item["type"])
        result_hash = fingerprint(payload)
        if row.result_fingerprint:
            if row.result_fingerprint != result_hash:
                raise ConflictError("这次授权已登记了不同结果")
            return cls._attempt_view(row)
        assert row.bindings_json is not None
        bindings = {item["type"]: item for item in json.loads(row.bindings_json)}
        if len({item.type for item in body.results}) != len(body.results) or {
            item.type for item in body.results
        } != set(bindings):
            raise ConflictError("授权结果必须与本次模板逐项对应")
        if body.enable_renewal and row.mode != "onboarding":
            raise ConflictError("本次授权不包含首次开启选择")
        view = cls.view(db, context, channel, locked=True)
        visible = {item.type: item for item in view.settings.preferences}
        states = cls._states(db, context, locked=True)
        grants = []
        now = utcnow()
        for outcome in body.results:
            binding = channel.binding(outcome.type)
            item = visible.get(outcome.type)
            state = states.get(outcome.type)
            if (
                not binding
                or not item
                or not item.enabled
                or not channel.available
                or not state
                or template_fingerprint(binding) != bindings[outcome.type]["fingerprint"]
            ):
                raise ConflictError("提醒模板或权限已变化，请在提醒设置重新确认")
            decision = outcome.decision
            if decision in {"accept", "reject"}:
                grants.append(SubscriptionResult(type=outcome.type, accepted=decision == "accept"))
            if decision == "accept":
                state.consented = True
                state.stop_reason = None
                state.retry_after = None
            elif decision in {"ban", "filter"}:
                state.stop_reason = decision
            elif decision in {"technical", "unknown"}:
                state.retry_after = now + timedelta(seconds=LEASE_SECONDS)
            if decision in {"accept", "reject", "cancel"}:
                state.last_prompt_cursor = view.completion_cursor
            if state.active_attempt_id == row.id:
                state.active_attempt_id = None
            state.updated_at = now
        if grants:
            NotificationsService.apply_subscription(
                db, context, channel, SubscriptionRegister(results=grants)
            )
        if body.enable_renewal:
            preference = cls._preference(db, context, locked=True)
            if preference is None:
                preference = NotificationRenewalPreference(
                    family_id=context.family_id, member_id=member, choice="unseen", version=0
                )
                db.add(preference)
            # Preserve a later explicit choice on another device, while recording the real grant.
            if preference.version == row.choice_version:
                preference.choice = "enabled"
                preference.version += 1
        row.state = "registered"
        row.result_fingerprint = result_hash
        row.result_json = json.dumps(payload)
        row.updated_at = now
        db.commit()
        return cls._attempt_view(row)
