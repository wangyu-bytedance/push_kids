from datetime import UTC, datetime, timedelta

import pytest
from push_kids.activities.service import ActivitiesService


def create_workday(client, headers, child):
    response = client.post(
        "/api/v1/calendar-events",
        headers=headers,
        json={
            "child_id": child["id"],
            "name": "工作日安排",
            "event_date": "2026-01-01",
            "start_time": "18:00",
            "end_time": "19:00",
            "workday_only": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def schedule(client, headers, child, day):
    response = client.get(f"/api/v1/children/{child['id']}/schedule?day={day}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_workday_event_holiday_adjusted_day_start_and_isolation(client, family_headers, child):
    item = create_workday(client, family_headers, child)
    assert item["workday_only"] is True
    assert schedule(client, family_headers, child, "2026-01-01")["items"] == []
    assert schedule(client, family_headers, child, "2025-12-31")["items"] == []
    adjusted = schedule(client, family_headers, child, "2026-01-04")["items"]
    assert len(adjusted) == 1 and adjusted[0]["workday_only"] is True
    assert adjusted[0]["repeat_weekly"] is False
    assert adjusted[0]["event_date"] == "2026-01-01"
    assert schedule(client, family_headers, child, "2026-01-05")["items"]
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/schedule?day=2026-01-04",
            headers={"X-Family-ID": "other-family"},
        ).status_code
        == 404
    )


def test_workday_event_patch_validates_merged_mode_atomically(client, family_headers, child):
    item = create_workday(client, family_headers, child)
    url = f"/api/v1/calendar-events/{item['id']}"
    assert (
        client.patch(url, headers=family_headers, json={"repeat_weekly": True}).status_code == 422
    )
    assert client.patch(url, headers=family_headers, json={"workday_only": None}).status_code == 422
    renamed = client.patch(url, headers=family_headers, json={"name": "新名称"})
    assert renamed.json()["workday_only"] is True
    assert renamed.json()["repeat_weekly"] is False
    assert (
        client.patch(url, headers=family_headers, json={"start_time": "20:00"}).status_code == 422
    )
    converted = client.patch(
        url, headers=family_headers, json={"workday_only": False, "repeat_weekly": True}
    )
    assert converted.status_code == 200
    assert converted.json()["start_time"] == "18:00:00"


def test_workday_idempotency_mode_and_invalid_create(client, family_headers, child):
    payload = {
        "child_id": child["id"],
        "name": "课",
        "event_date": "2026-01-01",
        "start_time": "18:00",
        "end_time": "19:00",
        "workday_only": True,
    }
    headers = {**family_headers, "Idempotency-Key": "workday-key-2026"}
    first = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    again = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    assert first.json()["id"] == again.json()["id"]
    assert (
        client.post(
            "/api/v1/calendar-events", headers=headers, json={**payload, "workday_only": False}
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/v1/calendar-events",
            headers=family_headers,
            json={**payload, "repeat_weekly": True},
        ).status_code
        == 422
    )


def activity(client, headers, child):
    subject = client.post(
        "/api/v1/subjects",
        headers=headers,
        json={"child_id": child["id"], "name": "合成辅导课", "kind": "activity"},
    )
    assert subject.status_code == 201, subject.text
    return {
        "child_id": child["id"],
        "subject_id": subject.json()["id"],
        "workday_only": True,
        "start_time": "18:00",
        "end_time": "19:00",
    }


def test_workday_activity_projection_suggestion_patch_and_conflict(client, family_headers, child):
    payload = activity(client, family_headers, child)
    response = client.post("/api/v1/activity-schedules", headers=family_headers, json=payload)
    assert response.status_code == 201, response.text
    row = response.json()
    assert row["workday_only"] and row["time_slots"] == [] and row["weekdays"] == []
    assert row["start_time"] == "18:00:00"
    assert schedule(client, family_headers, child, "2026-01-01")["items"] == []
    create_workday(client, family_headers, child)
    items = schedule(client, family_headers, child, "2026-01-04")["items"]
    assert len(items) == 2 and all(item["conflicts"] for item in items)
    url = f"/api/v1/activity-schedules/{row['id']}"
    assert client.patch(url, headers=family_headers, json={"time_slots": []}).status_code == 422
    assert client.patch(url, headers=family_headers, json={"weekdays": [0]}).status_code == 422
    updated = client.patch(url, headers=family_headers, json={"note": "只改备注"})
    assert updated.json()["workday_only"] and updated.json()["start_time"] == "18:00:00"
    for day, expected in [("2026-01-01", False), ("2026-01-04", True), ("2027-01-04", False)]:
        response = client.get(
            f"/api/v1/children/{child['id']}/activity-suggestions?day={day}", headers=family_headers
        )
        suggestion = response.json()["items"][0]
        assert suggestion["scheduled_today"] is expected
        assert suggestion["suggested"] is expected
    converted = client.patch(
        url, headers=family_headers, json={"workday_only": False, "time_slots": []}
    )
    assert converted.status_code == 200 and not converted.json()["workday_only"]
    assert converted.json()["start_time"] is None


@pytest.mark.parametrize(
    "extra", [{"weekdays": [0]}, {"time_slots": []}, {"end_time": None}, {"end_time": "17:00"}]
)
def test_workday_activity_rejects_mixed_or_incomplete(client, family_headers, child, extra):
    payload = activity(client, family_headers, child)
    assert (
        client.post(
            "/api/v1/activity-schedules", headers=family_headers, json={**payload, **extra}
        ).status_code
        == 422
    )


def test_workday_window_and_coverage_warning(client, family_headers, child, app, caplog):
    create_workday(client, family_headers, child)
    payload = activity(client, family_headers, child)
    assert (
        client.post("/api/v1/activity-schedules", headers=family_headers, json=payload).status_code
        == 201
    )
    for day, count in [("2026-01-01", 0), ("2026-01-04", 2), ("2027-01-04", 0)]:
        start = datetime.fromisoformat(day).replace(tzinfo=UTC)
        with app.state.database.session_factory() as db:
            rows = ActivitiesService.occurrences_in_window(db, start, start + timedelta(hours=23))
        assert len(rows) == count
    assert "workday_calendar_coverage_missing" in caplog.text
    result = schedule(client, family_headers, child, "2027-01-04")
    assert result["items"] == []
    assert result["workday_calendar_warning"] == {
        "code": "workday_calendar_coverage_missing",
        "coverage_end": "2026-12-31",
    }
    assert (
        schedule(client, family_headers, child, "2026-01-04").get("workday_calendar_warning")
        is None
    )


def test_legacy_idempotency_fingerprint_survives_additive_mode(client, family_headers, child, app):
    import json
    from hashlib import sha256

    from push_kids.activities.schemas import CalendarEventWrite
    from push_kids.persistence.models import CalendarEventRequest
    from sqlalchemy import select

    payload = {
        "child_id": child["id"],
        "name": "旧客户端",
        "event_date": "2026-01-04",
        "start_time": "18:00",
        "end_time": "19:00",
    }
    headers = {**family_headers, "Idempotency-Key": "legacy-workday-migration"}
    created = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    with app.state.database.session_factory() as db:
        row = db.scalar(
            select(CalendarEventRequest).where(
                CalendarEventRequest.idempotency_key == headers["Idempotency-Key"]
            )
        )
        legacy = CalendarEventWrite(**payload).model_dump(mode="json", exclude={"workday_only"})
        row.request_fingerprint = sha256(
            json.dumps(legacy, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        db.commit()
    replay = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    assert replay.status_code == 201 and replay.json()["id"] == created.json()["id"]
    assert (
        client.post(
            "/api/v1/calendar-events", headers=headers, json={**payload, "workday_only": True}
        ).status_code
        == 409
    )


def test_hidden_activity_does_not_claim_calendar_coverage_is_missing(client, family_headers, child):
    payload = activity(client, family_headers, child)
    assert (
        client.post("/api/v1/activity-schedules", headers=family_headers, json=payload).status_code
        == 201
    )
    assert schedule(client, family_headers, child, "2027-01-04")["workday_calendar_warning"]
    assert (
        client.patch(
            f"/api/v1/subjects/{payload['subject_id']}",
            headers=family_headers,
            json={"active": False},
        ).status_code
        == 200
    )
    result = schedule(client, family_headers, child, "2027-01-04")
    assert result["items"] == []
    assert result["workday_calendar_warning"] is None
