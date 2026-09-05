from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.persistence.models import WeChatActorBinding
from push_kids.platform.dependencies import get_db
from push_kids.platform.errors import ForbiddenError, UnauthorizedError


@dataclass(frozen=True)
class RequestContext:
    family_id: str
    subject_hmac: str | None
    app_id: str | None
    openid: str | None


def subject_hmac(secret: str, app_id: str, openid: str) -> str:
    message = f"v1:{app_id}:{openid}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def request_context(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    x_family_id: Annotated[str | None, Header(alias="X-Family-ID")] = None,
    x_wx_source: Annotated[str | None, Header(alias="X-WX-SOURCE")] = None,
    x_wx_openid: Annotated[str | None, Header(alias="X-WX-OPENID")] = None,
    x_wx_appid: Annotated[str | None, Header(alias="X-WX-APPID")] = None,
    x_wx_env: Annotated[str | None, Header(alias="X-WX-ENV")] = None,
) -> RequestContext:
    settings = request.app.state.settings
    if not settings.is_cloud:
        if x_family_id is None:
            raise HTTPException(status_code=422, detail="X-Family-ID is required")
        if not 3 <= len(x_family_id) <= 80:
            raise HTTPException(status_code=422, detail="X-Family-ID has invalid length")
        return RequestContext(x_family_id, None, None, None)

    if x_family_id is not None:
        raise ForbiddenError("云环境不接受客户端家庭标识")
    if not x_wx_source or not x_wx_openid or not x_wx_appid or not x_wx_env:
        raise UnauthorizedError("请从已关联的小程序访问")
    if x_wx_appid != settings.wechat_expected_app_id or x_wx_env != settings.wechat_env_id:
        raise ForbiddenError("当前小程序或云环境无权访问")
    if not settings.actor_hmac_key:
        raise RuntimeError("云身份密钥未配置")
    subject = subject_hmac(settings.actor_hmac_key.get_secret_value(), x_wx_appid, x_wx_openid)
    binding = db.scalar(
        select(WeChatActorBinding).where(
            WeChatActorBinding.app_id == x_wx_appid,
            WeChatActorBinding.subject_hmac == subject,
            WeChatActorBinding.status == "active",
        )
    )
    if binding is None:
        raise ForbiddenError("当前微信用户尚未绑定家庭")
    if not binding.family_id:
        raise RuntimeError("微信用户绑定缺少家庭标识")
    return RequestContext(binding.family_id, subject, x_wx_appid, x_wx_openid)


def family_id(context: Annotated[RequestContext, Depends(request_context)]) -> str:
    return context.family_id
