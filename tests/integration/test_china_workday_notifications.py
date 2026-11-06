from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from push_kids.notifications.planner import NotificationPlanner
from push_kids.persistence.models import NotificationDelivery
from sqlalchemy import select

from tests.integration.test_notification_channel import _actor, _create_family, _grant


def test_workday_planner_queues_adjusted_day_only_and_keeps_idempotence(notification_app):
    with TestClient(notification_app) as client:
        family = _create_family(client)
        child_id = family["children"][0]["id"]
        headers = _actor("parent-a")
        response = client.post(
            "/api/v1/calendar-events",
            headers=headers,
            json={
                "child_id": child_id,
                "name": "工作日课",
                "event_date": "2026-01-01",
                "start_time": "18:00",
                "end_time": "19:00",
                "workday_only": True,
            },
        )
        assert response.status_code == 201, response.text
        _grant(client, "parent-a", ["schedule_reminder"])
        for day, count in [("2026-01-01", 0), ("2026-01-04", 1), ("2027-01-04", 0)]:
            now = datetime.fromisoformat(day).replace(hour=8, tzinfo=UTC)
            with notification_app.state.database.session_factory() as db:
                result = NotificationPlanner.plan_schedule_reminders(db, now)
                assert result.queued == count
                repeated = NotificationPlanner.plan_schedule_reminders(db, now)
                assert repeated.queued == 0
                deliveries = list(
                    db.scalars(
                        select(NotificationDelivery).where(
                            NotificationDelivery.scheduled_at >= now,
                            NotificationDelivery.scheduled_at <= now + timedelta(hours=3),
                        )
                    )
                )
                assert len(deliveries) == count
