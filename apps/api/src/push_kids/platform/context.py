from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Annotated, cast

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.persistence.models import (
    Family,
    FamilyMember,
    FamilyStatus,
    MemberRole,
    MemberStatus,
    WeChatActorBinding,
)
from push_kids.platform.dependencies import get_db
from push_kids.platform.errors import ForbiddenError, UnauthorizedError


@dataclass(frozen=True)
class RequestContext:
    family_id: str
    subject_hmac: str | None
    app_id: str | None
    openid: str | None
    actor_binding_id: str | None = None
    member_id: str | None = None
    role: str = "manager"


@dataclass(frozen=True)
class TrustedActorContext:
    subject_hmac: str
    app_id: str
    openid: str | None


def subject_hmac(secret: str, app_id: str, openid: str) -> str:
    message = f"v1:{app_id}:{openid}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def _trusted_actor(
    request: Request,
    x_wx_source: str | None,
    x_wx_openid: str | None,
    x_wx_appid: str | None,
    x_wx_env: str | None,
    x_debug_actor: str | None,
) -> TrustedActorContext:
    settings = request.app.state.settings
    if not settings.is_cloud:
        if not x_debug_actor or not 3 <= len(x_debug_actor) <= 80:
            raise UnauthorizedError("本地家庭流程需要 X-Debug-Actor")
        subject = hashlib.sha256(f"local:v1:{x_debug_actor}".encode()).hexdigest()
        return TrustedActorContext(subject, "local-debug", None)
    if not x_wx_source or not x_wx_openid or not x_wx_appid or not x_wx_env:
        raise UnauthorizedError("请从已关联的小程序访问")
    if x_wx_appid != settings.wechat_expected_app_id or x_wx_env != settings.wechat_env_id:
        raise ForbiddenError("当前小程序或云环境无权访问")
    if not settings.actor_hmac_key:
        raise RuntimeError("云身份密钥未配置")
    subject = subject_hmac(settings.actor_hmac_key.get_secret_value(), x_wx_appid, x_wx_openid)
    return TrustedActorContext(subject, x_wx_appid, x_wx_openid)


def trusted_actor_context(
    request: Request,
    x_wx_source: Annotated[str | None, Header(alias="X-WX-SOURCE")] = None,
    x_wx_openid: Annotated[str | None, Header(alias="X-WX-OPENID")] = None,
    x_wx_appid: Annotated[str | None, Header(alias="X-WX-APPID")] = None,
    x_wx_env: Annotated[str | None, Header(alias="X-WX-ENV")] = None,
    x_debug_actor: Annotated[str | None, Header(alias="X-Debug-Actor")] = None,
) -> TrustedActorContext:
    return _trusted_actor(request, x_wx_source, x_wx_openid, x_wx_appid, x_wx_env, x_debug_actor)


def request_context(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_family_id: Annotated[str | None, Header(alias="X-Family-ID")] = None,
    x_wx_source: Annotated[str | None, Header(alias="X-WX-SOURCE")] = None,
    x_wx_openid: Annotated[str | None, Header(alias="X-WX-OPENID")] = None,
    x_wx_appid: Annotated[str | None, Header(alias="X-WX-APPID")] = None,
    x_wx_env: Annotated[str | None, Header(alias="X-WX-ENV")] = None,
    x_debug_actor: Annotated[str | None, Header(alias="X-Debug-Actor")] = None,
) -> RequestContext:
    settings = request.app.state.settings
    if not settings.is_cloud and x_family_id is not None:
        if not 3 <= len(x_family_id) <= 80:
            raise HTTPException(status_code=422, detail="X-Family-ID has invalid length")
        return RequestContext(x_family_id, None, None, None)
    if not settings.is_cloud and x_debug_actor is None:
        raise HTTPException(status_code=422, detail="X-Family-ID is required")

    if x_family_id is not None:
        raise ForbiddenError("云环境不接受客户端家庭标识")
    actor = _trusted_actor(request, x_wx_source, x_wx_openid, x_wx_appid, x_wx_env, x_debug_actor)
    binding = db.scalar(
        select(WeChatActorBinding).where(
            WeChatActorBinding.app_id == actor.app_id,
            WeChatActorBinding.subject_hmac == actor.subject_hmac,
            WeChatActorBinding.status == "active",
        )
    )
    if binding is None:
        raise ForbiddenError("当前微信用户尚未绑定家庭")
    if not binding.family_id:
        raise RuntimeError("微信用户绑定缺少家庭标识")
    member = db.scalar(
        select(FamilyMember).where(
            FamilyMember.actor_binding_id == binding.id,
            FamilyMember.family_id == binding.family_id,
            FamilyMember.status == MemberStatus.active.value,
        )
    )
    family = db.scalar(
        select(Family).where(
            Family.id == binding.family_id,
            Family.status == FamilyStatus.active.value,
        )
    )
    if member is None or family is None:
        raise ForbiddenError("当前微信用户尚未获得家庭权限")
    role = cast(str, member.role)
    if request.method not in {"GET", "HEAD", "OPTIONS"} and role not in {
        "editor",
        "manager",
    }:
        raise ForbiddenError("当前家庭角色只有查看权限")
    return RequestContext(
        binding.family_id,
        actor.subject_hmac,
        actor.app_id,
        actor.openid,
        binding.id,
        member.id,
        role,
    )


def family_id(context: Annotated[RequestContext, Depends(request_context)]) -> str:
    return context.family_id


def manager_context(
    context: Annotated[RequestContext, Depends(request_context)],
) -> RequestContext:
    """Manager-only gate for operations that change what the whole family can see.

    Only the role is checked here. The local `X-Family-ID` path has no membership row, so
    requiring a member id would lock managers out of local flows. Callers that need the
    acting member's identity must resolve and validate it themselves.
    """
    if context.role != MemberRole.manager.value:
        raise ForbiddenError("只有家庭管理员可以执行此操作")
    return context
