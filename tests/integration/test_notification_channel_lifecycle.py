"""FEAT-003：通道的生命周期与边界。

离开家庭必须立刻切断通道——已排队的消息要作废、微信授权要收回、接收标识要停用，否则前成员还会继续收到
另一个家庭的孩子姓名。投递历史也不能无限增长，超过保留窗口的终态记录要清理，但在途消息一条都不能被清掉。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.service import RETENTION_DAYS, NotificationsService
from push_kids.persistence.models import (
    DeliveryState,
    NotificationDelivery,
    NotificationDestination,
    NotificationSubscription,
)
from push_kids.platform.time import SHANGHAI, local_date, utcnow
from sqlalchemy import select


@pytest.fixture
def app(notification_app):
    return notification_app


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _idempotent(name: str, key: str) -> dict[str, str]:
    return {**_actor(name), "Idempotency-Key": key}


def _create_family(client: TestClient) -> dict:
    created = client.post(
        "/api/v1/families",
        headers=_idempotent("parent-a", "lifecycle-family-001"),
        json={
            "display_name": "小雨的家",
            "relationship_label": "妈妈",
            "child": {"name": "小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
        },
    )
    assert created.status_code == 201, created.text
    return created.json()


def _add_member(client: TestClient, actor: str, relationship: str) -> str:
    token = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("parent-a", f"lifecycle-invite-{actor}"),
        json={"expires_in_hours": 24},
    ).json()["token"]
    application = client.post(
        "/api/v1/family-requests",
        headers=_idempotent(actor, f"lifecycle-join-{actor}"),
        json={"token": token, "relationship_label": relationship},
    )
    assert application.status_code == 201, application.text
    approved = client.post(
        f"/api/v1/family-requests/{application.json()['id']}/approve",
        headers=_idempotent("parent-a", f"lifecycle-approve-{actor}"),
        json={"role": "viewer"},
    )
    assert approved.status_code == 200, approved.text
    return approved.json()["id"]


def _grant(client: TestClient, actor: str) -> None:
    response = client.post(
        "/api/v1/notifications/subscriptions",
        headers=_actor(actor),
        json={"results": [{"type": "schedule_reminder", "accepted": True}]},
    )
    assert response.status_code == 200, response.text


def _queue_reminder(client: TestClient, app) -> datetime:
    """Queue one schedule reminder for the whole family and return when it becomes due."""
    child_id = _create_family(client)["children"][0]["id"]
    day = local_date()
    event = client.post(
        "/api/v1/calendar-events",
        headers=_idempotent("parent-a", "lifecycle-event-001"),
        json={
            "child_id": child_id,
            "name": "钢琴课",
            "event_date": day.isoformat(),
            "start_time": "17:30:00",
            "end_time": "18:30:00",
            "kind": "class",
        },
    )
    assert event.status_code == 201, event.text
    start_at = datetime.combine(day, datetime(2026, 1, 1, 17, 30).time(), tzinfo=SHANGHAI)
    return start_at.astimezone(UTC) - timedelta(minutes=60)


def _delivery_states(app) -> dict[str, tuple[str, str | None]]:
    with app.state.database.session_factory() as db:
        return {
            str(row.member_id): (str(row.state), row.result_code)
            for row in db.scalars(select(NotificationDelivery))
        }


def test_leaving_the_family_cuts_the_channel(client: TestClient, app) -> None:
    due = _queue_reminder(client, app)
    grandparent_id = _add_member(client, "grandparent-b", "奶奶")
    _grant(client, "parent-a")
    _grant(client, "grandparent-b")
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=1)).queued == 2
        )

    removed = client.delete(
        f"/api/v1/families/current/members/{grandparent_id}", headers=_actor("parent-a")
    )
    assert removed.status_code == 204, removed.text

    with app.state.database.session_factory() as db:
        assert NotificationsService.sweep(db)["revoked"] == 1
    states = _delivery_states(app)
    assert states[grandparent_id] == (DeliveryState.cancelled.value, "member_departed")

    with app.state.database.session_factory() as db:
        destination = db.scalar(
            select(NotificationDestination).where(
                NotificationDestination.member_id == grandparent_id
            )
        )
        assert destination is not None
        assert destination.status == "revoked"
        subscription = db.scalar(
            select(NotificationSubscription).where(
                NotificationSubscription.member_id == grandparent_id
            )
        )
        assert subscription is not None
        assert subscription.status == "revoked"
        assert subscription.remaining_quota == 0

    # 剩下的家人照常收到提醒，被移出的成员一条都收不到。
    with app.state.database.session_factory() as db:
        report = NotificationsService.dispatch_due(db, app.state.notification_channel, due)
    assert report["sent"] == 1
    assert len(app.state.notification_channel.sender.sent) == 1
    # 重新计划也不会把前成员加回受众。
    with app.state.database.session_factory() as db:
        assert NotificationPlanner.plan_schedule_reminders(db, due).queued == 0


def test_a_row_queued_before_departure_is_dropped_at_send_time(client: TestClient, app) -> None:
    due = _queue_reminder(client, app)
    grandparent_id = _add_member(client, "grandparent-b", "奶奶")
    _grant(client, "grandparent-b")
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=1)).queued == 1
        )
    removed = client.delete(
        f"/api/v1/families/current/members/{grandparent_id}", headers=_actor("parent-a")
    )
    assert removed.status_code == 204, removed.text

    # 没有跑清理直接投递：发送前的成员身份复核必须挡住这条消息。
    with app.state.database.session_factory() as db:
        report = NotificationsService.dispatch_due(db, app.state.notification_channel, due)
    assert report == {"sent": 0, "skipped": 0, "retried": 0, "failed": 0, "dropped": 1}
    assert app.state.notification_channel.sender.sent == []
    assert _delivery_states(app)[grandparent_id] == (
        DeliveryState.cancelled.value,
        "member_departed",
    )


def test_history_is_pruned_only_past_the_retention_window(client: TestClient, app) -> None:
    due = _queue_reminder(client, app)
    _grant(client, "parent-a")
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=1)).queued == 1
        )
        assert (
            NotificationsService.dispatch_due(db, app.state.notification_channel, due)["sent"] == 1
        )

    with app.state.database.session_factory() as db:
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        row.updated_at = utcnow() - timedelta(days=RETENTION_DAYS - 1)
        db.commit()
        # 保留窗口之内的记录要留着，家长还要靠它解释"上次发了什么"。
        assert NotificationsService.prune_history(db) == 0

    with app.state.database.session_factory() as db:
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        row.updated_at = utcnow() - timedelta(days=RETENTION_DAYS + 1)
        db.commit()
        assert NotificationsService.prune_history(db) == 1
        assert db.scalar(select(NotificationDelivery)) is None


def test_in_flight_rows_are_never_pruned(client: TestClient, app) -> None:
    due = _queue_reminder(client, app)
    _grant(client, "parent-a")
    with app.state.database.session_factory() as db:
        assert (
            NotificationPlanner.plan_schedule_reminders(db, due - timedelta(minutes=1)).queued == 1
        )
        row = db.scalar(select(NotificationDelivery))
        assert row is not None
        row.updated_at = utcnow() - timedelta(days=RETENTION_DAYS * 3)
        db.commit()
        assert NotificationsService.prune_history(db) == 0
        assert db.scalar(select(NotificationDelivery)) is not None
