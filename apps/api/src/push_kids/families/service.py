from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.children.schemas import ChildView
from push_kids.children.service import ChildrenService
from push_kids.families.domain import requires_last_manager_protection
from push_kids.families.repository import FamilyRepository
from push_kids.families.schemas import (
    BootstrapView,
    FamilyCreate,
    FamilySummary,
    InviteCreate,
    InviteListItem,
    InvitePreview,
    InviteView,
    JoinDecision,
    JoinRejection,
    JoinRequestCreate,
    JoinRequestSummary,
    JoinRequestView,
    MemberUpdate,
    MemberView,
)
from push_kids.persistence.models import (
    Child,
    Family,
    FamilyAuditEvent,
    FamilyInvite,
    FamilyJoinRequest,
    FamilyMember,
    FamilyStatus,
    InviteStatus,
    JoinRequestStatus,
    MemberRole,
    MemberStatus,
    WeChatActorBinding,
)
from push_kids.platform.context import RequestContext, TrustedActorContext
from push_kids.platform.errors import ConflictError, ForbiddenError, GoneError, NotFoundError
from push_kids.platform.time import utcnow


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _invite_token(secret: str, family_id: str, idempotency_key: str) -> str:
    digest = hmac.new(
        secret.encode(), f"invite:v1:{family_id}:{idempotency_key}".encode(), hashlib.sha256
    ).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def _expired(value: datetime) -> bool:
    now = utcnow()
    if value.tzinfo is None:
        now = now.replace(tzinfo=None)
    return value <= now


def _request_code(request_id: str) -> str:
    return request_id.replace("-", "").upper()[:6]


class FamilyService:
    @staticmethod
    def purge_data(db: Session, family_id: str) -> None:
        db.execute(
            update(WeChatActorBinding)
            .where(WeChatActorBinding.family_id == family_id)
            .values(family_id=None, status="unbound")
        )
        db.execute(delete(FamilyJoinRequest).where(FamilyJoinRequest.family_id == family_id))
        db.execute(delete(FamilyInvite).where(FamilyInvite.family_id == family_id))
        db.execute(delete(FamilyAuditEvent).where(FamilyAuditEvent.family_id == family_id))
        db.execute(delete(FamilyMember).where(FamilyMember.family_id == family_id))
        db.execute(delete(Family).where(Family.id == family_id))

    @staticmethod
    def _member_view(member: FamilyMember, own_member_id: str | None) -> MemberView:
        return MemberView(
            id=member.id,
            role=member.role,
            relationship_label=member.relationship_label,
            is_self=member.id == own_member_id,
            created_at=member.created_at,
        )

    @staticmethod
    def _request_view(item: FamilyJoinRequest) -> JoinRequestView:
        assert item.id
        return JoinRequestView(
            id=item.id,
            request_code=_request_code(item.id),
            status=item.status,
            relationship_label=item.relationship_label,
            role=item.decided_role,
            created_at=item.created_at,
            decided_at=item.decided_at,
        )

    @staticmethod
    def _audit(
        db: Session,
        family_id: str,
        actor_binding_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None,
    ) -> None:
        db.add(
            FamilyAuditEvent(
                family_id=family_id,
                actor_binding_id=actor_binding_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
            )
        )

    @staticmethod
    def _require_manager(context: RequestContext) -> None:
        if context.role != MemberRole.manager.value or not context.member_id:
            raise ForbiddenError("只有家庭管理员可以执行此操作")

    @classmethod
    def bootstrap(cls, db: Session, actor: TrustedActorContext) -> BootstrapView:
        binding = FamilyRepository.actor_binding(db, actor.app_id, actor.subject_hmac)
        if binding is None:
            return BootstrapView(state="unbound")
        if binding.status == "active":
            member = FamilyRepository.active_member(db, binding.id)
            family = db.get(Family, binding.family_id) if binding.family_id else None
            if member and family and family.status == FamilyStatus.active.value:
                # Bootstrap drives the child switcher, so it must only offer profiles in use.
                children = ChildrenService.list_children(db, str(family.id))
                return BootstrapView(
                    state="bound",
                    family=FamilySummary.model_validate(family),
                    member=cls._member_view(member, member.id),
                    children=[ChildView.model_validate(child) for child in children],
                )
        request = FamilyRepository.pending_request(db, binding.id)
        if request:
            return BootstrapView(
                state="pending",
                request=JoinRequestSummary(
                    id=request.id,
                    request_code=_request_code(request.id),
                    family_id=request.family_id,
                    status=request.status,
                    relationship_label=request.relationship_label,
                    created_at=request.created_at,
                ),
            )
        return BootstrapView(state="unbound")

    @classmethod
    def create_family(
        cls,
        db: Session,
        actor: TrustedActorContext,
        body: FamilyCreate,
        idempotency_key: str,
    ) -> BootstrapView:
        binding = FamilyRepository.actor_binding(db, actor.app_id, actor.subject_hmac, lock=True)
        if binding and binding.status == "active":
            return cls.bootstrap(db, actor)
        if binding and FamilyRepository.pending_request(db, binding.id, lock=True):
            raise ConflictError("你已有待处理的加入申请，请先取消申请")

        family = Family(display_name=body.display_name.strip())
        db.add(family)
        db.flush()
        assert family.id
        if binding is None:
            binding = WeChatActorBinding(
                app_id=actor.app_id,
                subject_hmac=actor.subject_hmac,
                family_id=family.id,
                status="active",
            )
            db.add(binding)
            try:
                db.flush()
            except IntegrityError:
                db.rollback()
                result = cls.bootstrap(db, actor)
                if result.state == "bound":
                    return result
                raise ConflictError("家庭创建请求发生冲突，请重试") from None
        else:
            binding.family_id = family.id
            binding.status = "active"
        member = FamilyMember(
            family_id=family.id,
            actor_binding_id=binding.id,
            active_actor_binding_id=binding.id,
            role=MemberRole.manager.value,
            relationship_label=body.relationship_label.strip(),
        )
        db.add(member)
        db.flush()
        assert binding.id
        if body.child is not None:
            ChildrenService.create_child_in_transaction(db, family.id, body.child)
        cls._audit(db, family.id, binding.id, "family.created", "family", family.id)
        db.commit()
        return cls.bootstrap(db, actor)

    @classmethod
    def list_members(cls, db: Session, context: RequestContext) -> list[MemberView]:
        items = list(
            db.scalars(
                select(FamilyMember)
                .where(
                    FamilyMember.family_id == context.family_id,
                    FamilyMember.status == MemberStatus.active.value,
                )
                .order_by(FamilyMember.created_at)
            )
        )
        return [cls._member_view(item, context.member_id) for item in items]

    @classmethod
    def update_member(
        cls, db: Session, context: RequestContext, member_id: str, body: MemberUpdate
    ) -> MemberView:
        cls._require_manager(context)
        member = db.scalar(
            select(FamilyMember)
            .where(
                FamilyMember.id == member_id,
                FamilyMember.family_id == context.family_id,
                FamilyMember.status == MemberStatus.active.value,
            )
            .with_for_update()
        )
        if member is None:
            raise NotFoundError("没有找到这个家庭成员")
        if member.id == context.member_id:
            raise ConflictError("不能在成员管理中移除自己")
        next_role = body.role or member.role
        manager_count = db.scalar(
            select(func.count())
            .select_from(FamilyMember)
            .where(
                FamilyMember.family_id == context.family_id,
                FamilyMember.status == MemberStatus.active.value,
                FamilyMember.role == MemberRole.manager.value,
            )
            .with_for_update()
        )
        if requires_last_manager_protection(str(member.role), next_role, int(manager_count or 0)):
            raise ConflictError("家庭至少需要一位管理员")
        member.role = next_role
        if body.relationship_label is not None:
            member.relationship_label = body.relationship_label.strip()
        assert context.actor_binding_id
        cls._audit(
            db, context.family_id, context.actor_binding_id, "member.updated", "member", member.id
        )
        db.commit()
        return cls._member_view(member, context.member_id)

    @classmethod
    def remove_member(cls, db: Session, context: RequestContext, member_id: str) -> None:
        cls._require_manager(context)
        member = db.scalar(
            select(FamilyMember)
            .where(
                FamilyMember.id == member_id,
                FamilyMember.family_id == context.family_id,
                FamilyMember.status == MemberStatus.active.value,
            )
            .with_for_update()
        )
        if member is None:
            raise NotFoundError("没有找到这个家庭成员")
        manager_count = db.scalar(
            select(func.count())
            .select_from(FamilyMember)
            .where(
                FamilyMember.family_id == context.family_id,
                FamilyMember.status == MemberStatus.active.value,
                FamilyMember.role == MemberRole.manager.value,
            )
            .with_for_update()
        )
        if requires_last_manager_protection(str(member.role), None, int(manager_count or 0)):
            raise ConflictError("家庭至少需要一位管理员")
        member.status = MemberStatus.removed.value
        member.removed_at = utcnow()
        member.active_actor_binding_id = None
        binding = db.get(WeChatActorBinding, member.actor_binding_id)
        if binding:
            binding.status = "unbound"
            binding.family_id = None
        assert context.actor_binding_id
        cls._audit(
            db, context.family_id, context.actor_binding_id, "member.removed", "member", member.id
        )
        db.commit()

    @classmethod
    def create_invite(
        cls,
        db: Session,
        context: RequestContext,
        body: InviteCreate,
        idempotency_key: str,
        secret: str,
    ) -> InviteView:
        cls._require_manager(context)
        token = _invite_token(secret, context.family_id, idempotency_key)
        token_hash = _token_hash(token)
        invite = db.scalar(
            select(FamilyInvite).where(
                FamilyInvite.family_id == context.family_id,
                FamilyInvite.idempotency_key == idempotency_key,
            )
        )
        if invite is None:
            invite = FamilyInvite(
                family_id=context.family_id,
                token_hash=token_hash,
                idempotency_key=idempotency_key,
                expires_at=utcnow() + timedelta(hours=body.expires_in_hours),
                created_by_member_id=context.member_id,
            )
            db.add(invite)
            try:
                db.flush()
            except IntegrityError:
                db.rollback()
                invite = db.scalar(
                    select(FamilyInvite).where(
                        FamilyInvite.family_id == context.family_id,
                        FamilyInvite.idempotency_key == idempotency_key,
                    )
                )
                if invite is None:
                    raise ConflictError("邀请创建请求发生冲突，请重试") from None
                return InviteView(
                    id=invite.id,
                    token=token,
                    share_path=f"/pages/family-join/index?token={token}",
                    status=invite.status,
                    expires_at=invite.expires_at,
                )
            assert context.actor_binding_id
            cls._audit(
                db,
                context.family_id,
                context.actor_binding_id,
                "invite.created",
                "invite",
                invite.id,
            )
            db.commit()
        return InviteView(
            id=invite.id,
            token=token,
            share_path=f"/pages/family-join/index?token={token}",
            status=invite.status,
            expires_at=invite.expires_at,
        )

    @classmethod
    def _expire_pending_requests_for_invite(
        cls,
        db: Session,
        invite_id: str,
        *,
        exclude_request_id: str | None = None,
    ) -> None:
        statement = select(FamilyJoinRequest).where(
            FamilyJoinRequest.invite_id == invite_id,
            FamilyJoinRequest.status == JoinRequestStatus.pending.value,
        )
        if exclude_request_id:
            statement = statement.where(FamilyJoinRequest.id != exclude_request_id)
        for item in db.scalars(statement.with_for_update()):
            item.status = JoinRequestStatus.expired.value
            item.decided_at = utcnow()
            binding = db.get(WeChatActorBinding, item.applicant_binding_id)
            if binding and binding.status == "pending" and binding.family_id == item.family_id:
                binding.status = "unbound"
                binding.family_id = None

    @classmethod
    def list_invites(cls, db: Session, context: RequestContext) -> list[InviteListItem]:
        cls._require_manager(context)
        items = FamilyRepository.active_invites(db, context.family_id)
        changed = False
        active: list[InviteListItem] = []
        for item in items:
            assert item.id
            assert item.expires_at
            if _expired(item.expires_at):
                item.status = InviteStatus.expired.value
                cls._expire_pending_requests_for_invite(db, item.id)
                changed = True
                continue
            active.append(
                InviteListItem(id=item.id, status=item.status, expires_at=item.expires_at)
            )
        if changed:
            db.commit()
        return active

    @classmethod
    def _active_invite(cls, db: Session, token: str, *, lock: bool = False) -> FamilyInvite:
        invite = FamilyRepository.invite_by_hash(db, _token_hash(token), lock=lock)
        if invite is None:
            raise NotFoundError("邀请不存在")
        if invite.status != InviteStatus.active.value:
            raise GoneError("邀请已失效")
        if _expired(invite.expires_at):
            invite.status = InviteStatus.expired.value
            cls._expire_pending_requests_for_invite(db, invite.id)
            db.commit()
            raise GoneError("邀请已过期")
        return invite

    @classmethod
    def preview_invite(cls, db: Session, token: str) -> InvitePreview:
        invite = cls._active_invite(db, token)
        family = db.get(Family, invite.family_id)
        if family is None or family.status != FamilyStatus.active.value:
            raise GoneError("邀请已失效")
        names = list(
            db.scalars(
                select(Child.name)
                .where(Child.family_id == family.id, Child.active.is_(True))
                .order_by(Child.created_at)
            )
        )
        return InvitePreview(
            family_name=family.display_name,
            child_names=names,
            expires_at=invite.expires_at,
        )

    @classmethod
    def apply(
        cls,
        db: Session,
        actor: TrustedActorContext,
        token: str,
        body: JoinRequestCreate,
        idempotency_key: str,
    ) -> JoinRequestView:
        invite = cls._active_invite(db, token, lock=True)
        assert invite.family_id
        binding = FamilyRepository.actor_binding(db, actor.app_id, actor.subject_hmac, lock=True)
        if binding and binding.status == "active":
            raise ConflictError("你已经加入一个家庭")
        if binding is None:
            binding = WeChatActorBinding(
                app_id=actor.app_id,
                subject_hmac=actor.subject_hmac,
                family_id=invite.family_id,
                status="pending",
            )
            db.add(binding)
            try:
                db.flush()
            except IntegrityError:
                db.rollback()
                binding = FamilyRepository.actor_binding(db, actor.app_id, actor.subject_hmac)
                if binding is None:
                    raise ConflictError("加入申请发生冲突，请重试") from None
        assert binding.id
        existing = db.scalar(
            select(FamilyJoinRequest).where(
                FamilyJoinRequest.applicant_binding_id == binding.id,
                FamilyJoinRequest.status == JoinRequestStatus.pending.value,
            )
        )
        if existing:
            if existing.family_id != invite.family_id:
                raise ConflictError("你已有其他待处理的加入申请")
            return cls._request_view(existing)
        binding.family_id = invite.family_id
        binding.status = "pending"
        item = FamilyJoinRequest(
            family_id=invite.family_id,
            invite_id=invite.id,
            applicant_binding_id=binding.id,
            idempotency_key=idempotency_key,
            relationship_label=body.relationship_label.strip(),
        )
        db.add(item)
        db.flush()
        cls._audit(db, invite.family_id, binding.id, "request.created", "join_request", item.id)
        db.commit()
        return cls._request_view(item)

    @classmethod
    def cancel_current_request(cls, db: Session, actor: TrustedActorContext) -> None:
        binding = FamilyRepository.actor_binding(db, actor.app_id, actor.subject_hmac, lock=True)
        if binding is None:
            raise NotFoundError("没有待处理的加入申请")
        item = FamilyRepository.pending_request(db, binding.id, lock=True)
        if item is None:
            raise NotFoundError("没有待处理的加入申请")
        item.status = JoinRequestStatus.cancelled.value
        item.decided_at = utcnow()
        binding.status = "unbound"
        binding.family_id = None
        cls._audit(db, item.family_id, binding.id, "request.cancelled", "join_request", item.id)
        db.commit()

    @classmethod
    def list_requests(cls, db: Session, context: RequestContext) -> list[JoinRequestView]:
        cls._require_manager(context)
        items = list(
            db.scalars(
                select(FamilyJoinRequest)
                .where(
                    FamilyJoinRequest.family_id == context.family_id,
                    FamilyJoinRequest.status == JoinRequestStatus.pending.value,
                )
                .order_by(FamilyJoinRequest.created_at)
            )
        )
        return [cls._request_view(item) for item in items]

    @classmethod
    def approve(
        cls,
        db: Session,
        context: RequestContext,
        request_id: str,
        body: JoinDecision,
        idempotency_key: str,
    ) -> MemberView:
        cls._require_manager(context)
        item = db.scalar(
            select(FamilyJoinRequest)
            .where(
                FamilyJoinRequest.id == request_id,
                FamilyJoinRequest.family_id == context.family_id,
            )
            .with_for_update()
        )
        if item is None:
            raise NotFoundError("没有找到这个加入申请")
        binding = db.scalar(
            select(WeChatActorBinding)
            .where(WeChatActorBinding.id == item.applicant_binding_id)
            .with_for_update()
        )
        if binding is None:
            raise ConflictError("申请人的身份记录不存在")
        assert binding.id
        existing = FamilyRepository.active_member(db, binding.id, lock=True)
        if item.status == JoinRequestStatus.approved.value:
            if item.decision_idempotency_key == idempotency_key and existing:
                return cls._member_view(existing, context.member_id)
            raise ConflictError("该申请已处理")
        if item.status != JoinRequestStatus.pending.value:
            terminal_invite = db.get(FamilyInvite, item.invite_id)
            if (
                item.status == JoinRequestStatus.expired.value
                and terminal_invite
                and (
                    terminal_invite.status != InviteStatus.active.value
                    or terminal_invite.expires_at is None
                    or _expired(terminal_invite.expires_at)
                )
            ):
                raise GoneError("邀请已失效")
            raise ConflictError("该申请已处理")
        invite = db.get(FamilyInvite, item.invite_id)
        if (
            invite is None
            or invite.status != InviteStatus.active.value
            or invite.expires_at is None
            or _expired(invite.expires_at)
        ):
            if invite is not None:
                if invite.status == InviteStatus.active.value:
                    invite.status = InviteStatus.expired.value
                assert invite.id
                cls._expire_pending_requests_for_invite(db, invite.id)
            else:
                item.status = JoinRequestStatus.expired.value
                item.decided_at = utcnow()
                if binding.status == "pending" and binding.family_id == item.family_id:
                    binding.status = "unbound"
                    binding.family_id = None
            db.commit()
            raise GoneError("邀请已过期或被撤销")
        if binding.status == "active" and binding.family_id != context.family_id:
            raise ConflictError("申请人已经加入其他家庭")
        member = FamilyMember(
            family_id=context.family_id,
            actor_binding_id=binding.id,
            active_actor_binding_id=binding.id,
            role=body.role,
            relationship_label=item.relationship_label,
        )
        db.add(member)
        db.flush()
        binding.family_id = context.family_id
        binding.status = "active"
        item.status = JoinRequestStatus.approved.value
        item.decided_role = body.role
        item.decision_reason = body.reason
        item.decision_idempotency_key = idempotency_key
        item.decided_by_member_id = context.member_id
        item.decided_at = utcnow()
        invite.status = InviteStatus.exhausted.value
        assert invite.id
        assert item.id
        cls._expire_pending_requests_for_invite(db, invite.id, exclude_request_id=item.id)
        assert context.actor_binding_id
        cls._audit(
            db,
            context.family_id,
            context.actor_binding_id,
            "request.approved",
            "join_request",
            item.id,
        )
        db.commit()
        return cls._member_view(member, context.member_id)

    @classmethod
    def reject(
        cls,
        db: Session,
        context: RequestContext,
        request_id: str,
        body: JoinRejection,
        idempotency_key: str,
    ) -> JoinRequestView:
        cls._require_manager(context)
        item = db.scalar(
            select(FamilyJoinRequest)
            .where(
                FamilyJoinRequest.id == request_id,
                FamilyJoinRequest.family_id == context.family_id,
            )
            .with_for_update()
        )
        if item is None:
            raise NotFoundError("没有找到这个加入申请")
        if (
            item.status == JoinRequestStatus.rejected.value
            and item.decision_idempotency_key == idempotency_key
        ):
            return cls._request_view(item)
        if item.status != JoinRequestStatus.pending.value:
            raise ConflictError("该申请已处理")
        item.status = JoinRequestStatus.rejected.value
        item.decision_reason = body.reason
        item.decision_idempotency_key = idempotency_key
        item.decided_by_member_id = context.member_id
        item.decided_at = utcnow()
        binding = db.get(WeChatActorBinding, item.applicant_binding_id)
        if binding:
            binding.status = "unbound"
            binding.family_id = None
        assert context.actor_binding_id
        cls._audit(
            db,
            context.family_id,
            context.actor_binding_id,
            "request.rejected",
            "join_request",
            item.id,
        )
        db.commit()
        return cls._request_view(item)

    @classmethod
    def revoke_invite(cls, db: Session, context: RequestContext, invite_id: str) -> None:
        cls._require_manager(context)
        invite = db.scalar(
            select(FamilyInvite)
            .where(
                FamilyInvite.id == invite_id,
                FamilyInvite.family_id == context.family_id,
            )
            .with_for_update()
        )
        if invite is None:
            raise NotFoundError("没有找到这个邀请")
        if invite.status != InviteStatus.active.value:
            return
        invite.status = InviteStatus.revoked.value
        assert invite.id
        cls._expire_pending_requests_for_invite(db, invite.id)
        assert context.actor_binding_id
        cls._audit(
            db, context.family_id, context.actor_binding_id, "invite.revoked", "invite", invite.id
        )
        db.commit()
