from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

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
from push_kids.platform.errors import ForbiddenError, NotFoundError

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
