from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from push_kids.notifications.inbound import (
    MAX_BODY_BYTES,
    InboundEventError,
    parse_event,
    verify_signature,
)
from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.schemas import (
    DeliveryView,
    DispatchReport,
    NotificationSettingsView,
    PreferenceUpdate,
    SubscriptionRegister,
)
from push_kids.notifications.service import NotificationChannel, NotificationsService
from push_kids.platform.context import RequestContext, request_context, self_service_context
from push_kids.platform.dependencies import get_db
from push_kids.platform.errors import AppError, ForbiddenError, NotFoundError

router = APIRouter(tags=["notifications"])


def notification_channel(request: Request) -> NotificationChannel:
    return request.app.state.notification_channel


ChannelDep = Annotated[NotificationChannel, Depends(notification_channel)]
ContextDep = Annotated[RequestContext, Depends(request_context)]
# Reminder settings are per member, so even a viewer may change their own.
SelfContextDep = Annotated[RequestContext, Depends(self_service_context)]
DbDep = Annotated[Session, Depends(get_db)]


@router.get("/notifications/settings", response_model=NotificationSettingsView)
def read_settings(context: ContextDep, db: DbDep, channel: ChannelDep):
    return NotificationsService.settings_view(db, context, channel)


@router.patch("/notifications/preferences", response_model=NotificationSettingsView)
def update_preference(
    body: PreferenceUpdate, context: SelfContextDep, db: DbDep, channel: ChannelDep
):
    return NotificationsService.update_preference(db, context, channel, body.type, body.enabled)


@router.post("/notifications/subscriptions", response_model=NotificationSettingsView)
def register_subscription(
    body: SubscriptionRegister, context: SelfContextDep, db: DbDep, channel: ChannelDep
):
    return NotificationsService.register_subscription(db, context, channel, body)


@router.get("/notifications/deliveries", response_model=list[DeliveryView])
def list_deliveries(context: ContextDep, db: DbDep):
    return NotificationsService.recent_deliveries(db, context)


@router.post("/notifications/dispatch", response_model=DispatchReport)
def dispatch(
    request: Request,
    db: DbDep,
    channel: ChannelDep,
    x_notification_trigger: Annotated[
        str | None, Header(alias="X-Notification-Trigger", max_length=200)
    ] = None,
):
    """Operator/cron entry point for one planning + dispatch tick.

    This route carries no family scope, so it is gated by a deployment-owned shared token instead
    of by member identity, and it stays absent unless that token is configured.
    """
    expected = request.app.state.settings.notification_trigger_value
    if not expected:
        raise NotFoundError("当前部署未开启通知调度入口")
    if not x_notification_trigger or not secrets.compare_digest(x_notification_trigger, expected):
        raise ForbiddenError("通知调度凭据无效")
    swept = NotificationsService.sweep(db)
    planned = NotificationPlanner.plan_all(db)
    dispatched = NotificationsService.dispatch_due(db, channel)
    return DispatchReport(**swept, **planned, **dispatched)


def _message_token(request: Request) -> str:
    """The WeChat message-push token. Without it the callback must not exist at all."""
    token = request.app.state.settings.wechat_message_token_value
    if not token:
        raise NotFoundError("当前部署未开启微信消息推送回调")
    return token


@router.get("/notifications/wechat/events", response_class=PlainTextResponse)
def verify_event_url(
    request: Request,
    signature: str = "",
    timestamp: str = "",
    nonce: str = "",
    echostr: str = "",
):
    """WeChat's one-off URL check: echo the challenge only when the signature matches."""
    token = _message_token(request)
    if not verify_signature(token, timestamp, nonce, signature):
        raise ForbiddenError("消息推送签名无效")
    return PlainTextResponse(echostr[:512])


@router.post("/notifications/wechat/events", response_class=PlainTextResponse)
async def receive_event(
    request: Request,
    db: DbDep,
    channel: ChannelDep,
    signature: str = "",
    timestamp: str = "",
    nonce: str = "",
):
    """Apply one subscription event pushed by WeChat.

    This route carries no family scope and no member identity, so it trusts nothing but the signed
    token plus a stored active destination. It always answers `success` for an accepted body: WeChat
    retries otherwise, and a retry cannot make an unknown receiver known.
    """
    token = _message_token(request)
    if not verify_signature(token, timestamp, nonce, signature):
        raise ForbiddenError("消息推送签名无效")
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        raise AppError("消息推送内容过大")
    try:
        event = parse_event(await request.body())
    except InboundEventError as exc:
        raise AppError(str(exc)) from exc
    if event is not None:
        NotificationsService.ingest_event(db, channel, event)
    return PlainTextResponse("success")
