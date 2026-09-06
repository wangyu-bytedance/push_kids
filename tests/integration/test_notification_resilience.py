"""FEAT-003：通知投递的失败语义。

提醒是尽力而为的：可恢复故障要退避重试，永久拒绝要落到明确终态并同步授权状态，崩溃留下的租约要能回收。
任何情况下都不能把"没发出去"记成"已发送"。
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from push_kids.notifications.domain import RETRY_DELAYS_SECONDS
from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.providers import SendOutcome
from push_kids.notifications.service import NotificationsService
from push_kids.notifications.templates import TemplateBinding
from push_kids.persistence.models import (
    DeliveryState,
    NotificationDelivery,
    NotificationDestination,
)
from push_kids.platform.time import SHANGHAI, local_date
from sqlalchemy import select


class ScriptedSender:
    """Replays a fixed list of provider outcomes so retry and terminal paths stay deterministic."""

    def __init__(self, outcomes: list[SendOutcome]) -> None:
        self._outcomes = list(outcomes)
        self.calls = 0

    @property
    def available(self) -> bool:
        return True

    @property
    def unavailable_reason(self) -> str:
        return ""

    def send(
        self, *, receiver: str, binding: TemplateBinding, values: dict[str, str], deep_link: str
    ) -> SendOutcome:
        self.calls += 1
        if not self._outcomes:
            return SendOutcome("sent", "ok")
        return self._outcomes.pop(0)


@pytest.fixture
def app(notification_app):
    return notification_app


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _family(client: TestClient) -> dict:
    created = client.post(
        "/api/v1/families",
        headers={**_actor("parent-a"), "Idempotency-Key": "resilience-family-001"},
        json={
            "display_name": "小雨的家",
            "relationship_label": "妈妈",
            "child": {"name": "小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
        },
    )
    assert created.status_code == 201, created.text
    return created.json()


def _queued_reminder(client: TestClient, app, at: datetime) -> datetime:
    """Queue one schedule reminder and return the moment it becomes due."""
    child_id = _family(client)["children"][0]["id"]
    day = local_date()
    event = client.post(
        "/api/v1/calendar-events",
        headers={**_actor("parent-a"), "Idempotency-Key": "resilience-event-001"},
        json={
            "child_id": child_id,
            "name": "钢琴课",
            "event_date": day.isoformat(),
            "start_time": at.strftime("%H:%M:%S"),
            "end_time": (at + timedelta(hours=1)).strftime("%H:%M:%S"),
            "kind": "class",
        },
    )
    assert event.status_code == 201, event.text
    granted = client.post(
        "/api/v1/notifications/subscriptions",
        headers=_actor("parent-a"),
        json={"results": [{"type": "schedule_reminder", "accepted": True}]},
    )
    assert granted.status_code == 200, granted.text
    start_at = datetime.combine(day, at.time(), tzinfo=SHANGHAI).astimezone(UTC)
    due = start_at - timedelta(minutes=60)
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=30)).queued == 1
        )
    return due


def _channel_with(app, sender):
    return dataclasses.replace(app.state.notification_channel, sender=sender)


def _row(app) -> NotificationDelivery:
    with app.state.database.session_factory() as db:
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        db.expunge(row)
        return row


def test_transient_transport_error_backs_off_then_gives_up(client: TestClient, app) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    sender = ScriptedSender([SendOutcome("retry", "transport_error")] * 4)
    channel = _channel_with(app, sender)

    with app.state.database.session_factory() as db:
        first = NotificationsService.dispatch_due(db, channel, due)
    assert first == {"sent": 0, "skipped": 0, "retried": 1, "failed": 0, "dropped": 0}
    row = _row(app)
    assert row.state == DeliveryState.pending.value
    assert row.attempts == 1
    assert row.result_code == "transport_error"
    # 退避期内不能再打一次微信。
    assert row.available_at == due + timedelta(seconds=RETRY_DELAYS_SECONDS[0])
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["retried"] == 0
    assert sender.calls == 1

    second_window = due + timedelta(seconds=RETRY_DELAYS_SECONDS[0])
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, second_window)["retried"] == 1
    third_window = second_window + timedelta(seconds=RETRY_DELAYS_SECONDS[1])
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, third_window)["failed"] == 1
    final = _row(app)
    assert final.state == DeliveryState.failed.value
    assert final.attempts == 3
    assert final.sent_at is None
    assert sender.calls == 3


def test_user_refusal_is_permanent_and_revokes_the_grant(client: TestClient, app) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    channel = _channel_with(app, ScriptedSender([SendOutcome("permanent", "user_refused")]))
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["failed"] == 1
    assert _row(app).state == DeliveryState.failed.value

    settings = client.get("/api/v1/notifications/settings", headers=_actor("parent-a")).json()
    schedule = next(item for item in settings["preferences"] if item["type"] == "schedule_reminder")
    # 用户在微信里拒收之后，产品必须承认自己不能再发，而不是继续排队。
    assert schedule["subscription_status"] == "rejected"
    assert schedule["remaining_quota"] == 0
    assert settings["last_sent_at"] is None
    deliveries = client.get("/api/v1/notifications/deliveries", headers=_actor("parent-a")).json()
    assert deliveries[0]["state"] == "failed"
    assert deliveries[0]["result_code"] == "user_refused"


def test_abandoned_lease_is_reclaimed_instead_of_lost(client: TestClient, app) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    with app.state.database.session_factory() as db:
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        row.state = DeliveryState.sending.value
        row.attempts = 1
        row.lease_until = due - timedelta(seconds=1)
        db.commit()
    channel = _channel_with(app, ScriptedSender([]))
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["sent"] == 1
    reclaimed = _row(app)
    assert reclaimed.state == DeliveryState.sent.value
    assert reclaimed.attempts == 2

    # 用尽重试次数的租约不能无限循环，必须落到失败终态。
    with app.state.database.session_factory() as db:
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        row.state = DeliveryState.sending.value
        row.attempts = 3
        row.lease_until = due - timedelta(seconds=1)
        db.commit()
        assert NotificationsService.reclaim_expired(db, due) == 1
    exhausted = _row(app)
    assert exhausted.state == DeliveryState.failed.value
    assert exhausted.result_code == "lease_expired"


def test_unusable_receiver_record_fails_loudly(client: TestClient, app) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    with app.state.database.session_factory() as db:
        destination = db.scalar(select(NotificationDestination))
        assert destination is not None
        destination.ciphertext = "dGFtcGVyZWQtY2lwaGVydGV4dC12YWx1ZQ=="
        db.commit()
    channel = _channel_with(app, ScriptedSender([]))
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["failed"] == 1
    assert _row(app).result_code == "destination_unreadable"


def test_channel_without_templates_skips_instead_of_pretending(client: TestClient, app) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    channel = dataclasses.replace(app.state.notification_channel, bindings={})
    assert channel.available is False
    assert channel.reason
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["skipped"] == 1
    skipped = _row(app)
    assert skipped.state == DeliveryState.skipped.value
    assert skipped.result_code == "channel_unavailable"
    # 通道恢复之后同一条提醒可以重新排队，不需要家长再操作一次。
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=1)).queued == 1
        )
        assert (
            NotificationsService.dispatch_due(db, app.state.notification_channel, due)["sent"] == 1
        )


def test_settings_report_an_unavailable_channel_truthfully(client: TestClient, app) -> None:
    _family(client)
    app.state.notification_channel = dataclasses.replace(
        app.state.notification_channel, bindings={}
    )
    body = client.get("/api/v1/notifications/settings", headers=_actor("parent-a")).json()
    assert body["channel"]["available"] is False
    assert body["channel"]["template_ids"] == []
    assert body["channel"]["reason"]
    # 通道不可用时不能收下一个永远花不掉的授权。
    blocked = client.post(
        "/api/v1/notifications/subscriptions",
        headers=_actor("parent-a"),
        json={"results": [{"type": "review_digest", "accepted": True}]},
    )
    assert blocked.status_code == 404


def test_time_is_never_read_from_the_client(client: TestClient, app) -> None:
    """晚间摘要只按 Asia/Shanghai 的 19:00 判断，不看请求里的任何时间字段。"""
    _family(client)
    day = local_date()
    with app.state.database.session_factory() as db:
        before = datetime.combine(day, time(18, 59), tzinfo=SHANGHAI).astimezone(UTC)
        assert NotificationPlanner.plan_review_digests(db, before).queued == 0
