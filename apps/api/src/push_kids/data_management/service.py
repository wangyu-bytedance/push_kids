from __future__ import annotations

import hashlib
import hmac

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.data_management.schemas import DeletionRequestView
from push_kids.persistence.models import (
    DeletionRequest,
    DeletionState,
    Family,
    FamilyMember,
    FamilyStatus,
    MemberStatus,
    WeChatActorBinding,
)
from push_kids.platform.context import RequestContext, TrustedActorContext
from push_kids.platform.errors import ConflictError, ForbiddenError, GoneError, NotFoundError
from push_kids.platform.time import utcnow


class DataDeletionService:
    @staticmethod
    def _digest(secret: str, namespace: str, value: str) -> str:
        return hmac.new(
            secret.encode(), f"{namespace}:v1:{value}".encode(), hashlib.sha256
        ).hexdigest()

    @classmethod
    def _identity(
        cls,
        secret: str,
        target_type: str,
        family_id: str,
        target_id: str,
        confirmation_name: str,
        idempotency_key: str,
    ) -> tuple[str, str]:
        key_hash = cls._digest(secret, "deletion-key", idempotency_key)
        fingerprint = cls._digest(
            secret,
            "deletion-request",
            f"{target_type}:{family_id}:{target_id}:{confirmation_name.strip()}",
        )
        return key_hash, fingerprint

    @staticmethod
    def _binding_id(context: RequestContext, actor: TrustedActorContext) -> str:
        if not context.actor_binding_id or context.subject_hmac != actor.subject_hmac:
            raise ForbiddenError("删除配置只能从已验证的家庭账号操作")
        return context.actor_binding_id

    @staticmethod
    def view(item: DeletionRequest) -> DeletionRequestView:
        return DeletionRequestView(
            id=item.id,
            target_type=item.target_type,
            state=item.state,
            attempts=item.attempts or 0,
            retryable=item.state == DeletionState.failed.value,
            error_code=item.error_code,
            created_at=item.created_at,
            updated_at=item.updated_at,
            completed_at=item.completed_at,
        )

    @classmethod
    def _existing(
        cls,
        db: Session,
        actor_binding_id: str,
        key_hash: str,
        fingerprint: str,
    ) -> DeletionRequest | None:
        item = db.scalar(
            select(DeletionRequest)
            .where(
                DeletionRequest.actor_binding_id == actor_binding_id,
                DeletionRequest.idempotency_key_hash == key_hash,
            )
            .with_for_update()
        )
        if item is None:
            return None
        if item.request_fingerprint != fingerprint:
            raise ConflictError("此删除提交标识已用于不同内容，请重新操作")
        if item.state == DeletionState.failed.value:
            item.state = DeletionState.queued.value
            item.attempts = 0
            item.available_at = utcnow()
            item.lease_until = None
            item.error_code = None
            db.commit()
        return item

    @classmethod
    def request_child_deletion(
        cls,
        db: Session,
        context: RequestContext,
        actor: TrustedActorContext,
        child_id: str,
        confirmation_name: str,
        idempotency_key: str,
        secret: str,
    ) -> DeletionRequestView:
        actor_binding_id = cls._binding_id(context, actor)
        key_hash, fingerprint = cls._identity(
            secret,
            "child",
            context.family_id,
            child_id,
            confirmation_name,
            idempotency_key,
        )
        existing = cls._existing(db, actor_binding_id, key_hash, fingerprint)
        if existing is not None:
            return cls.view(existing)
        child = ChildrenService.get_child(db, context.family_id, child_id)
        if confirmation_name.strip() != str(child.name or "").strip():
            raise ConflictError("输入的孩子称呼不一致，请重新确认")
        if child.deleting:
            raise ConflictError("这个孩子的资料正在清理，请稍后查看结果")
        child.deleting = True
        item = DeletionRequest(
            actor_binding_id=actor_binding_id,
            family_id=context.family_id,
            target_type="child",
            target_id=child.id,
            idempotency_key_hash=key_hash,
            request_fingerprint=fingerprint,
        )
        db.add(item)
        db.commit()
        return cls.view(item)

    @classmethod
    def request_family_deletion(
        cls,
        db: Session,
        context: RequestContext,
        actor: TrustedActorContext,
        confirmation_name: str,
        idempotency_key: str,
        secret: str,
    ) -> DeletionRequestView:
        actor_binding_id = cls._binding_id(context, actor)
        key_hash, fingerprint = cls._identity(
            secret,
            "family",
            context.family_id,
            context.family_id,
            confirmation_name,
            idempotency_key,
        )
        existing = cls._existing(db, actor_binding_id, key_hash, fingerprint)
        if existing is not None:
            return cls.view(existing)
        family = db.scalar(
            select(Family)
            .where(Family.id == context.family_id, Family.status == FamilyStatus.active.value)
            .with_for_update()
        )
        if family is None:
            raise NotFoundError("没有找到当前家庭")
        if confirmation_name.strip() != str(family.display_name or "").strip():
            raise ConflictError("输入的家庭名称不一致，请重新确认")
        active_members = db.scalar(
            select(func.count())
            .select_from(FamilyMember)
            .where(
                FamilyMember.family_id == context.family_id,
                FamilyMember.status == MemberStatus.active.value,
            )
        )
        if int(active_members or 0) != 1:
            raise ConflictError("家庭中还有其他成员，请先处理成员关系后再删除当前家庭")
        active_cleanup = db.scalar(
            select(DeletionRequest).where(
                DeletionRequest.family_id == context.family_id,
                DeletionRequest.state != DeletionState.succeeded.value,
            )
        )
        if active_cleanup is not None:
            raise ConflictError("当前家庭还有资料正在清理，请完成后再试")
        family.status = FamilyStatus.deleting.value
        item = DeletionRequest(
            actor_binding_id=actor_binding_id,
            family_id=context.family_id,
            target_type="family",
            target_id=context.family_id,
            idempotency_key_hash=key_hash,
            request_fingerprint=fingerprint,
        )
        db.add(item)
        db.commit()
        return cls.view(item)

    @classmethod
    def get_request(
        cls, db: Session, actor: TrustedActorContext, request_id: str
    ) -> DeletionRequestView:
        binding = db.scalar(
            select(WeChatActorBinding).where(
                WeChatActorBinding.app_id == actor.app_id,
                WeChatActorBinding.subject_hmac == actor.subject_hmac,
            )
        )
        if binding is None:
            raise NotFoundError("没有找到这次清理请求")
        item = db.scalar(
            select(DeletionRequest).where(
                DeletionRequest.id == request_id,
                DeletionRequest.actor_binding_id == binding.id,
            )
        )
        if item is None:
            raise NotFoundError("没有找到这次清理请求")
        if item.expires_at is not None and item.expires_at <= utcnow():
            raise GoneError("这次清理状态已过期")
        return cls.view(item)

    @classmethod
    def retry_request(
        cls, db: Session, actor: TrustedActorContext, request_id: str
    ) -> DeletionRequestView:
        binding = db.scalar(
            select(WeChatActorBinding).where(
                WeChatActorBinding.app_id == actor.app_id,
                WeChatActorBinding.subject_hmac == actor.subject_hmac,
            )
        )
        if binding is None:
            raise NotFoundError("没有找到这次清理请求")
        item = db.scalar(
            select(DeletionRequest)
            .where(
                DeletionRequest.id == request_id,
                DeletionRequest.actor_binding_id == binding.id,
            )
            .with_for_update()
        )
        if item is None:
            raise NotFoundError("没有找到这次清理请求")
        if item.state != DeletionState.failed.value:
            raise ConflictError("只有清理失败后才需要重试")
        if not item.family_id or not item.target_id:
            raise GoneError("这次清理已经完成或过期")
        item.state = DeletionState.queued.value
        item.attempts = 0
        item.available_at = utcnow()
        item.lease_until = None
        item.error_code = None
        db.commit()
        return cls.view(item)
