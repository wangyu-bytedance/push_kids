"""FEAT-003：通知投递的失败语义。

提醒是尽力而为的：可恢复故障要退避重试，永久拒绝要落到明确终态并同步授权状态，崩溃留下的租约要能回收。
任何情况下都不能把"没发出去"记成"已发送"。
"""

from __future__ import annotations

import dataclasses
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from threading import Event, get_ident
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.notifications import service as notification_service
from push_kids.notifications.domain import RETRY_DELAYS_SECONDS, NotificationContent
from push_kids.notifications.outbox import EnqueueOutcome, NotificationOutbox
from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.providers import SendOutcome
from push_kids.notifications.service import LEASE_SECONDS, NotificationsService
from push_kids.notifications.templates import TemplateBinding
from push_kids.persistence.models import (
    DeliveryState,
    NotificationDelivery,
    NotificationDeliveryChild,
    NotificationDestination,
    NotificationSubscription,
)
from push_kids.platform.config import Settings
from push_kids.platform.time import SHANGHAI, local_date
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import make_url

from tests.conftest import NOTIFICATION_TEMPLATES


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


@pytest.fixture
def mysql_notification_app(tmp_path, monkeypatch):
    configured = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
    if not configured:
        pytest.skip("isolated MySQL 5.7 not configured")
    server_url = make_url(configured)
    assert server_url.host in {"127.0.0.1", "localhost"}
    server = create_engine(server_url.set(database=None))
    database_name = "notification_lease_" + uuid4().hex[:12]
    with server.begin() as db:
        assert db.exec_driver_sql("SELECT VERSION()").scalar_one().startswith("5.7.")
        db.exec_driver_sql(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4")
    url = server_url.set(database=database_name).render_as_string(hide_password=False)
    try:
        monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
        config = Config()
        config.set_main_option(
            "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
        )
        command.upgrade(config, "head")
        app = create_app(
            Settings(
                PUSH_KIDS_ENV="test",
                PUSH_KIDS_DATABASE_URL=url,
                PUSH_KIDS_MEDIA_ROOT=tmp_path,
                PUSH_KIDS_AI_PROVIDER="test",
                PUSH_KIDS_RUN_WORKER=False,
                PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
                PUSH_KIDS_NOTIFICATION_CHANNEL="recording",
                PUSH_KIDS_NOTIFICATION_TEMPLATES=NOTIFICATION_TEMPLATES,
            )
        )
        try:
            yield app
        finally:
            app.state.database.engine.dispose()
    finally:
        with server.begin() as db:
            db.exec_driver_sql(f"DROP DATABASE `{database_name}`")
        server.dispose()


def test_mysql_reclaim_cannot_replace_a_committed_send(mysql_notification_app) -> None:
    app = mysql_notification_app
    database = app.state.database
    entered_sender, resume_sender, reclaim_update = Event(), Event(), Event()
    reclaimer_thread = None

    class PausedSender(ScriptedSender):
        def send(self, **kwargs):
            entered_sender.set()
            assert resume_sender.wait(timeout=8)
            return super().send(**kwargs)

    def observe_reclaimer(_conn, _cursor, statement, _params, _ctx, _many):
        if get_ident() == reclaimer_thread and statement.startswith(
            "UPDATE notification_deliveries"
        ):
            reclaim_update.set()

    with TestClient(app) as client:
        due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
        delivery = _row(app)
        sender = PausedSender([])

        def send():
            with database.session_factory() as db:
                return NotificationsService.dispatch_due(db, _channel_with(app, sender), due)

        def reclaim():
            nonlocal reclaimer_thread
            reclaimer_thread = get_ident()
            with database.session_factory() as db:
                return NotificationsService.reclaim_expired(db, due + timedelta(seconds=121))

        event.listen(database.engine, "before_cursor_execute", observe_reclaimer)
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                sending = pool.submit(send)
                try:
                    assert entered_sender.wait(timeout=5)
                    recovering = pool.submit(reclaim)
                    assert reclaim_update.wait(timeout=5)
                    assert not recovering.done()
                finally:
                    resume_sender.set()
                assert sending.result(timeout=8)["sent"] == 1
                assert recovering.result(timeout=8) == 0
        finally:
            event.remove(database.engine, "before_cursor_execute", observe_reclaimer)

        with database.session_factory() as db:
            saved = db.get(NotificationDelivery, delivery.id)
            assert saved.state == DeliveryState.sent.value
            quota = db.scalar(
                select(NotificationSubscription.remaining_quota).where(
                    NotificationSubscription.member_id == delivery.member_id,
                    NotificationSubscription.type == delivery.type,
                )
            )
            assert quota == 0
        assert sender.calls == 1


def test_mysql_planner_cannot_cancel_a_delivery_from_an_old_pending_snapshot(
    mysql_notification_app,
) -> None:
    app = mysql_notification_app
    database = app.state.database
    with TestClient(app) as client:
        due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
        delivery = _row(app)
        with database.session_factory() as planner:
            assert (
                planner.scalar(
                    select(NotificationDelivery.state).where(NotificationDelivery.id == delivery.id)
                )
                == DeliveryState.pending.value
            )
            with database.session_factory() as dispatcher:
                sent = NotificationsService.dispatch_due(
                    dispatcher, _channel_with(app, ScriptedSender([])), due
                )
                assert sent["sent"] == 1
            cancelled = NotificationOutbox.cancel_pending_outside(
                planner,
                type_name=str(delivery.type),
                window_start=due - timedelta(minutes=1),
                window_end=due + timedelta(minutes=1),
                keep_keys=set(),
            )
            planner.commit()
        assert cancelled == 0
        assert _row(app).state == DeliveryState.sent.value


def test_mysql_planner_cannot_rearm_a_delivery_from_an_old_skipped_snapshot(
    mysql_notification_app,
) -> None:
    app = mysql_notification_app
    database = app.state.database
    with TestClient(app) as client:
        due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
        unavailable = dataclasses.replace(app.state.notification_channel, bindings={})
        with database.session_factory() as initial:
            assert NotificationsService.dispatch_due(initial, unavailable, due)["skipped"] == 1
            delivery = _row(app)
            child_id = initial.scalar(select(NotificationDeliveryChild.child_id))
        content = NotificationContent("活动", "合成提醒", "合成提醒", "/")
        with database.session_factory() as stale_planner:
            assert (
                stale_planner.scalar(
                    select(NotificationDelivery.state).where(NotificationDelivery.id == delivery.id)
                )
                == DeliveryState.skipped.value
            )
            with database.session_factory() as dispatcher:
                current = dispatcher.get(NotificationDelivery, delivery.id)
                current.state = DeliveryState.pending.value
                dispatcher.commit()
                sent = NotificationsService.dispatch_due(
                    dispatcher, _channel_with(app, ScriptedSender([])), due
                )
                assert sent["sent"] == 1
            outcome = NotificationOutbox.enqueue(
                stale_planner,
                family_id=str(delivery.family_id),
                type_name=str(delivery.type),
                member_id=str(delivery.member_id),
                dedupe_key=str(delivery.dedupe_key),
                content=content,
                scheduled_at=due,
                child_ids=(child_id,),
            )
            stale_planner.commit()
        assert outcome is EnqueueOutcome.skipped
        assert _row(app).state == DeliveryState.sent.value


def test_old_dispatcher_cannot_send_under_replacement_lease(client, app, monkeypatch):
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    replacement_time = due + timedelta(seconds=LEASE_SECONDS + 1)
    sender = ScriptedSender([])
    original_claim = NotificationsService._claim

    def replace_after_claim(db, *args, **kwargs):
        claimed = original_claim(db, *args, **kwargs)
        if claimed:
            with app.state.database.session_factory() as other:
                assert NotificationsService.reclaim_expired(other, replacement_time) == 1
                row = other.scalar(select(NotificationDelivery))
                assert row.state == DeliveryState.pending.value
                row.state = DeliveryState.sending.value
                row.attempts += 1
                row.lease_until = replacement_time + timedelta(seconds=LEASE_SECONDS)
                other.commit()
        return claimed

    monkeypatch.setattr(NotificationsService, "_claim", staticmethod(replace_after_claim))
    with app.state.database.session_factory() as db:
        report = NotificationsService.dispatch_due(db, _channel_with(app, sender), due)
    row = _row(app)
    assert report["dropped"] == 1
    assert sender.calls == 0
    assert (row.state, row.attempts, row.lease_until) == (
        DeliveryState.sending.value,
        2,
        replacement_time + timedelta(seconds=LEASE_SECONDS),
    )


def test_dispatch_does_not_lease_queue_tail_before_it_can_send(client, app, monkeypatch):
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    current = due
    monkeypatch.setattr(notification_service, "utcnow", lambda: current)
    with app.state.database.session_factory() as db:
        head = db.scalar(select(NotificationDelivery))
        child_id = db.scalar(select(NotificationDeliveryChild.child_id))
        tail = NotificationDelivery(
            family_id=head.family_id,
            member_id=head.member_id,
            type=head.type,
            dedupe_key="resilience-queue-tail",
            payload_json=head.payload_json,
            scheduled_at=due,
            available_at=due,
        )
        head.scheduled_at = due - timedelta(seconds=1)
        db.add(tail)
        db.flush()
        db.add(NotificationDeliveryChild(delivery_id=tail.id, child_id=child_id))
        subscription = db.scalar(select(NotificationSubscription))
        subscription.remaining_quota = 2
        db.commit()

        class SlowFirstSender(ScriptedSender):
            def send(self, **kwargs):
                nonlocal current
                if not self.calls:
                    current += timedelta(seconds=LEASE_SECONDS + 1)
                    assert (
                        db.scalar(
                            select(NotificationDelivery.state).where(
                                NotificationDelivery.id == tail.id
                            )
                        )
                        == DeliveryState.pending.value
                    )
                else:
                    expiry = db.scalar(
                        select(NotificationDelivery.lease_until).where(
                            NotificationDelivery.id == tail.id
                        )
                    )
                    assert expiry > current
                return super().send(**kwargs)

        sender = SlowFirstSender([])
        report = NotificationsService.dispatch_due(db, _channel_with(app, sender))
        assert report["sent"] == 2
        assert sender.calls == 2
        assert db.scalars(select(NotificationDelivery.state)).all() == [
            DeliveryState.sent.value,
            DeliveryState.sent.value,
        ]


@pytest.mark.parametrize("storage", ["sqlite", "mysql"])
def test_dispatch_refreshes_quota_between_claims(storage, request, tmp_path, monkeypatch):
    if storage == "mysql":
        app = request.getfixturevalue("mysql_notification_app")
    else:
        app = create_app(
            Settings(
                PUSH_KIDS_ENV="test",
                PUSH_KIDS_DATABASE_URL=f"sqlite:///{tmp_path / 'notification-lease.db'}",
                PUSH_KIDS_MEDIA_ROOT=tmp_path / "uploads",
                PUSH_KIDS_AI_PROVIDER="test",
                PUSH_KIDS_RUN_WORKER=False,
                PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
                PUSH_KIDS_NOTIFICATION_CHANNEL="recording",
                PUSH_KIDS_NOTIFICATION_TEMPLATES=NOTIFICATION_TEMPLATES,
            )
        )
    with TestClient(app) as client:
        due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    database = app.state.database
    with database.session_factory() as db:
        first = db.scalar(select(NotificationDelivery))
        child_id = db.scalar(select(NotificationDeliveryChild.child_id))
        for seconds in (1, 2):
            reminder = NotificationDelivery(
                family_id=first.family_id,
                member_id=first.member_id,
                type=first.type,
                dedupe_key=f"resilience-quota-race-{seconds}",
                payload_json=first.payload_json,
                scheduled_at=due + timedelta(seconds=seconds),
                available_at=due,
            )
            db.add(reminder)
            db.flush()
            db.add(NotificationDeliveryChild(delivery_id=reminder.id, child_id=child_id))
        subscription = db.scalar(select(NotificationSubscription))
        subscription.remaining_quota = 2
        db.commit()

    sender = ScriptedSender([])
    channel = _channel_with(app, sender)
    tick = due + timedelta(seconds=2)
    claim_next = NotificationsService._claim
    intervened = False

    with database.session_factory() as outer:

        def dispatch_between_claims(db, *args, **kwargs):
            nonlocal intervened
            if db is outer and sender.calls == 1 and not intervened:
                intervened = True
                with database.session_factory() as inner:
                    assert (
                        NotificationsService.dispatch_due(inner, channel, tick, limit=1)["sent"]
                        == 1
                    )
            return claim_next(db, *args, **kwargs)

        monkeypatch.setattr(NotificationsService, "_claim", staticmethod(dispatch_between_claims))
        report = NotificationsService.dispatch_due(outer, channel, tick)
    assert intervened
    assert report == {"sent": 1, "skipped": 1, "retried": 0, "failed": 0, "dropped": 0}
    assert sender.calls == 2
    with database.session_factory() as db:
        states = db.execute(
            select(NotificationDelivery.state, NotificationDelivery.result_code).order_by(
                NotificationDelivery.scheduled_at
            )
        ).all()
        assert states == [("sent", "ok"), ("sent", "ok"), ("skipped", "not_authorized")]
        subscription = db.scalar(select(NotificationSubscription))
        assert (subscription.status, subscription.remaining_quota) == ("expired", 0)


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


def test_template_slot_without_content_is_skipped_before_calling_wechat(
    client: TestClient, app
) -> None:
    due = _queued_reminder(client, app, datetime(2026, 1, 1, 17, 30))
    # 运维配了一个本项目产不出内容的槽位（这里用申请码），微信会整条拒发并吃掉一次授权额度。
    broken = TemplateBinding(
        type="schedule_reminder",
        template_id="tpl-schedule",
        fields={"thing1": "headline", "character_string9": "code"},
    )
    sender = ScriptedSender([])
    channel = dataclasses.replace(
        _channel_with(app, sender),
        bindings={**app.state.notification_channel.bindings, "schedule_reminder": broken},
    )
    with app.state.database.session_factory() as db:
        assert NotificationsService.dispatch_due(db, channel, due)["skipped"] == 1
    # 没有真的调用发送，额度也就没有被浪费。
    assert sender.calls == 0
    row = _row(app)
    assert row.state == DeliveryState.skipped.value
    assert row.result_code == "template_field_missing"
    settings = client.get("/api/v1/notifications/settings", headers=_actor("parent-a")).json()
    reminder = next(item for item in settings["preferences"] if item["type"] == "schedule_reminder")
    assert reminder["subscription_status"] == "accepted"
    assert reminder["remaining_quota"] == 1
    # 换回字段完整的模板，同一条提醒重新排队后就能发出去。
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
