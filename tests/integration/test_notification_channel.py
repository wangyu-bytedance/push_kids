"""FEAT-003：通知通道端到端行为。

覆盖三类通知的入队条件、去重与取消、成员级开关、微信订阅授权额度，以及调度入口的凭据边界。
`recording` 通道让断言落在"本该发出什么"上，而不需要真的调用微信。
"""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from push_kids.notifications.planner import NotificationPlanner
from push_kids.notifications.service import NotificationsService
from push_kids.platform.time import SHANGHAI, local_date

from tests.conftest import NOTIFICATION_TRIGGER


@pytest.fixture
def app(notification_app):
    return notification_app


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _idempotent(name: str, key: str) -> dict[str, str]:
    return {**_actor(name), "Idempotency-Key": key}


def _plan(app, now: datetime | None = None) -> dict[str, int]:
    with app.state.database.session_factory() as db:
        return NotificationPlanner.plan_all(db, now)


def _dispatch(app, now: datetime | None = None) -> dict[str, int]:
    with app.state.database.session_factory() as db:
        return NotificationsService.dispatch_due(db, app.state.notification_channel, now)


def _sent(app) -> list[dict]:
    return app.state.notification_channel.sender.sent


def _grant(client: TestClient, actor: str, types: list[str]) -> dict:
    response = client.post(
        "/api/v1/notifications/subscriptions",
        headers=_actor(actor),
        json={"results": [{"type": item, "accepted": True} for item in types]},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _create_family(client: TestClient) -> dict:
    created = client.post(
        "/api/v1/families",
        headers=_idempotent("parent-a", "notify-family-001"),
        json={
            "display_name": "小雨的家",
            "relationship_label": "妈妈",
            "child": {"name": "小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
        },
    )
    assert created.status_code == 201, created.text
    return created.json()


def _join(client: TestClient, actor: str, relationship: str) -> str:
    token = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("parent-a", f"notify-invite-{actor}"),
        json={"expires_in_hours": 24},
    ).json()["token"]
    application = client.post(
        "/api/v1/family-requests",
        headers=_idempotent(actor, f"notify-join-{actor}"),
        json={"token": token, "relationship_label": relationship},
    )
    assert application.status_code == 201, application.text
    return application.json()["id"]


def test_settings_expose_channel_state_and_manager_only_types(client: TestClient) -> None:
    _create_family(client)
    settings = client.get("/api/v1/notifications/settings", headers=_actor("parent-a"))
    assert settings.status_code == 200, settings.text
    body = settings.json()
    assert body["channel"]["available"] is True
    assert body["channel"]["long_term"] is False
    assert body["channel"]["template_ids"] == ["tpl-application", "tpl-schedule", "tpl-digest"]
    types = {item["type"]: item for item in body["preferences"]}
    assert set(types) == {"member_application", "schedule_reminder", "review_digest"}
    assert types["member_application"]["managers_only"] is True
    # 默认开启只表示"愿意收"，还没有微信授权，所以额度仍是 0。
    assert types["review_digest"]["enabled"] is True
    assert types["review_digest"]["subscription_status"] == "unknown"
    assert types["review_digest"]["remaining_quota"] == 0
    assert body["last_sent_at"] is None


def test_join_request_notifies_managers_only_after_a_grant(client: TestClient, app) -> None:
    _create_family(client)
    _join(client, "grandparent-b", "奶奶")

    # 没有微信授权时既不入队也不假装发送。
    assert _plan(app)["queued_member_applications"] == 0
    assert _dispatch(app) == {"sent": 0, "skipped": 0, "retried": 0, "failed": 0, "dropped": 0}
    assert _sent(app) == []

    _grant(client, "parent-a", ["member_application"])
    assert _plan(app)["queued_member_applications"] == 1
    report = _dispatch(app)
    assert report["sent"] == 1
    assert len(_sent(app)) == 1
    message = _sent(app)[0]
    assert message["template_id"] == "tpl-application"
    assert message["data"]["thing1"]["value"] == "有家人申请加入家庭"
    assert "奶奶" in message["data"]["thing2"]["value"]
    assert message["deep_link"] == "/pages/family-requests/index"

    # 一次性订阅只买一条消息，用完后必须重新授权。
    after = client.get("/api/v1/notifications/settings", headers=_actor("parent-a")).json()
    application_state = next(
        item for item in after["preferences"] if item["type"] == "member_application"
    )
    assert application_state["subscription_status"] == "expired"
    assert application_state["remaining_quota"] == 0
    assert after["last_sent_at"] is not None

    deliveries = client.get("/api/v1/notifications/deliveries", headers=_actor("parent-a"))
    assert deliveries.status_code == 200
    assert deliveries.json()[0]["state"] == "sent"
    assert deliveries.json()[0]["type"] == "member_application"


def test_approved_request_stops_reminding_and_viewers_are_not_asked(
    client: TestClient, app
) -> None:
    _create_family(client)
    request_id = _join(client, "grandparent-b", "奶奶")
    _grant(client, "parent-a", ["member_application"])
    assert _plan(app)["queued_member_applications"] == 1
    approved = client.post(
        f"/api/v1/family-requests/{request_id}/approve",
        headers=_idempotent("parent-a", "notify-approve-001"),
        json={"role": "viewer"},
    )
    assert approved.status_code == 200, approved.text
    # 申请已经处理完，待办提醒必须撤回而不是继续发送。
    assert _plan(app)["cancelled"] == 1
    assert _dispatch(app) == {"sent": 0, "skipped": 0, "retried": 0, "failed": 0, "dropped": 0}

    viewer = client.get("/api/v1/notifications/settings", headers=_actor("grandparent-b")).json()
    assert [item["type"] for item in viewer["preferences"]] == [
        "schedule_reminder",
        "review_digest",
    ]
    # 只看权限的家人不能接管审批提醒，但必须能管理自己的两类提醒。
    denied = client.patch(
        "/api/v1/notifications/preferences",
        headers=_actor("grandparent-b"),
        json={"type": "member_application", "enabled": True},
    )
    assert denied.status_code == 403
    own = client.patch(
        "/api/v1/notifications/preferences",
        headers=_actor("grandparent-b"),
        json={"type": "schedule_reminder", "enabled": False},
    )
    assert own.status_code == 200, own.text


def test_schedule_reminder_reaches_the_whole_family_one_hour_ahead(client: TestClient, app) -> None:
    family = _create_family(client)
    child_id = family["children"][0]["id"]
    request_id = _join(client, "grandparent-b", "奶奶")
    client.post(
        f"/api/v1/family-requests/{request_id}/approve",
        headers=_idempotent("parent-a", "notify-approve-002"),
        json={"role": "viewer"},
    )
    day = local_date()
    start = time(17, 30)
    event = client.post(
        "/api/v1/calendar-events",
        headers=_idempotent("parent-a", "notify-event-001"),
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
    start_at = datetime.combine(day, start, tzinfo=SHANGHAI).astimezone(UTC)

    _grant(client, "parent-a", ["schedule_reminder"])
    _grant(client, "grandparent-b", ["schedule_reminder"])

    two_hours_before = start_at - timedelta(hours=2)
    assert _plan(app, two_hours_before)["queued_schedule_reminders"] == 2
    # 还没到发送时间，队列必须安静。
    assert _dispatch(app, two_hours_before)["sent"] == 0

    one_hour_before = start_at - timedelta(minutes=60)
    assert _dispatch(app, one_hour_before)["sent"] == 2
    payloads = {item["data"]["thing1"]["value"] for item in _sent(app)}
    assert payloads == {"小雨"}
    times = {item["data"]["time2"]["value"] for item in _sent(app)}
    assert times == {"17:30"}
    headlines = {item["data"]["thing3"]["value"] for item in _sent(app)}
    assert headlines == {"钢琴课"}
    assert {item["deep_link"] for item in _sent(app)} == {"/pages/calendar/index"}


def test_moving_and_deleting_a_schedule_refreshes_instead_of_duplicating(
    client: TestClient, app
) -> None:
    family = _create_family(client)
    child_id = family["children"][0]["id"]
    day = local_date()
    created = client.post(
        "/api/v1/calendar-events",
        headers=_idempotent("parent-a", "notify-event-002"),
        json={
            "child_id": child_id,
            "name": "游泳",
            "event_date": day.isoformat(),
            "start_time": "18:00:00",
            "end_time": "19:00:00",
            "kind": "activity",
        },
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]
    _grant(client, "parent-a", ["schedule_reminder"])
    original_start = datetime.combine(day, time(18, 0), tzinfo=SHANGHAI).astimezone(UTC)
    planning_moment = original_start - timedelta(hours=2)
    assert _plan(app, planning_moment)["queued_schedule_reminders"] == 1

    moved = client.patch(
        f"/api/v1/calendar-events/{event_id}",
        headers=_actor("parent-a"),
        json={"start_time": "18:30:00", "end_time": "19:30:00"},
    )
    assert moved.status_code == 200, moved.text
    replanned = _plan(app, planning_moment)
    # 同一个日程改时间只能刷新原来的那一条，不能再排一条。
    assert replanned["queued_schedule_reminders"] == 0
    assert replanned["refreshed"] == 1
    assert replanned["cancelled"] == 0
    assert _dispatch(app, original_start - timedelta(minutes=60))["sent"] == 0
    new_start = datetime.combine(day, time(18, 30), tzinfo=SHANGHAI).astimezone(UTC)
    assert _dispatch(app, new_start - timedelta(minutes=60))["sent"] == 1
    assert _sent(app)[0]["data"]["time2"]["value"] == "18:30"

    client.delete(f"/api/v1/calendar-events/{event_id}", headers=_actor("parent-a"))
    later = client.post(
        "/api/v1/calendar-events",
        headers=_idempotent("parent-a", "notify-event-003"),
        json={
            "child_id": child_id,
            "name": "围棋",
            "event_date": day.isoformat(),
            "start_time": "20:00:00",
            "end_time": "21:00:00",
            "kind": "activity",
        },
    )
    assert later.status_code == 201, later.text
    later_start = datetime.combine(day, time(20, 0), tzinfo=SHANGHAI).astimezone(UTC)
    planning_moment = later_start - timedelta(hours=2)
    # 一次性订阅已经用掉，家长要重新授权才会有下一条提醒。
    assert _plan(app, planning_moment)["queued_schedule_reminders"] == 0
    _grant(client, "parent-a", ["schedule_reminder"])
    assert _plan(app, planning_moment)["queued_schedule_reminders"] == 1
    client.delete(f"/api/v1/calendar-events/{later.json()['id']}", headers=_actor("parent-a"))
    assert _plan(app, planning_moment)["cancelled"] == 1
    assert _dispatch(app, later_start - timedelta(minutes=60))["sent"] == 0


def test_disabled_member_switch_keeps_the_queue_empty(client: TestClient, app) -> None:
    family = _create_family(client)
    child_id = family["children"][0]["id"]
    day = local_date()
    client.post(
        "/api/v1/calendar-events",
        headers=_idempotent("parent-a", "notify-event-004"),
        json={
            "child_id": child_id,
            "name": "英语课",
            "event_date": day.isoformat(),
            "start_time": "16:00:00",
            "end_time": "17:00:00",
            "kind": "class",
        },
    )
    off = client.patch(
        "/api/v1/notifications/preferences",
        headers=_actor("parent-a"),
        json={"type": "schedule_reminder", "enabled": False},
    )
    assert off.status_code == 200, off.text
    assert (
        next(
            item["enabled"]
            for item in off.json()["preferences"]
            if item["type"] == "schedule_reminder"
        )
        is False
    )
    start_at = datetime.combine(day, time(16, 0), tzinfo=SHANGHAI).astimezone(UTC)
    assert _plan(app, start_at - timedelta(hours=2))["queued_schedule_reminders"] == 0
    assert _dispatch(app, start_at - timedelta(minutes=60))["sent"] == 0


def test_evening_digest_only_reports_real_outstanding_review(client: TestClient, app) -> None:
    family = _create_family(client)
    child_id = family["children"][0]["id"]
    day = local_date()
    morning = datetime.combine(day, time(9, 0), tzinfo=SHANGHAI).astimezone(UTC)
    evening = datetime.combine(day, time(19, 0), tzinfo=SHANGHAI).astimezone(UTC)

    # 没有到期复习时，晚间提醒必须保持沉默。
    assert _plan(app, evening)["queued_review_digests"] == 0

    occurred = datetime.now(UTC) - timedelta(days=4)
    submission = client.post(
        "/api/v1/submissions",
        headers=_actor("parent-a"),
        json={
            "child_id": child_id,
            "occurred_at": occurred.isoformat(),
            "input_text": "数学，两位数进位加法",
        },
    )
    assert submission.status_code == 202, submission.text
    assert app.state.worker.process_one() is True
    proposal = client.get(
        f"/api/v1/submissions/{submission.json()['id']}", headers=_actor("parent-a")
    ).json()
    confirmed = client.post(
        f"/api/v1/submissions/{proposal['id']}/confirm",
        headers=_actor("parent-a"),
        json={"proposal": proposal["proposal"]},
    )
    assert confirmed.status_code == 200, confirmed.text

    _grant(client, "parent-a", ["review_digest"])
    # 19:00 之前不发，避免变成第二个"今天待复习"入口。
    assert _plan(app, morning)["queued_review_digests"] == 0
    assert _plan(app, evening)["queued_review_digests"] == 1
    # 同一天只提醒一次。
    assert _plan(app, evening)["queued_review_digests"] == 0
    assert _dispatch(app, evening)["sent"] == 1
    message = _sent(app)[0]
    assert message["template_id"] == "tpl-digest"
    assert "没复习" in message["data"]["thing1"]["value"]
    assert "小雨" in message["data"]["thing2"]["value"]
    assert message["deep_link"] == "/pages/today/index"


def test_dispatch_entry_point_requires_the_deployment_token(client: TestClient) -> None:
    _create_family(client)
    assert client.post("/api/v1/notifications/dispatch").status_code == 403
    assert (
        client.post(
            "/api/v1/notifications/dispatch", headers={"X-Notification-Trigger": "wrong"}
        ).status_code
        == 403
    )
    accepted = client.post(
        "/api/v1/notifications/dispatch", headers={"X-Notification-Trigger": NOTIFICATION_TRIGGER}
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["sent"] == 0
