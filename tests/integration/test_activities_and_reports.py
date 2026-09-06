from datetime import UTC, datetime, time, timedelta

from push_kids.persistence.models import ActivityRecord, ReviewFeedback
from push_kids.platform.time import SHANGHAI, local_date


def test_activity_schedule_record_and_report(client, family_headers, child) -> None:
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "游泳", "kind": "activity"},
    ).json()
    schedule = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "weekdays": [5],
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "target_per_week": 2,
        },
    )
    assert schedule.status_code == 201
    record = client.post(
        "/api/v1/activity-records",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "duration_minutes": 45,
            "note": "练习换气",
        },
    )
    assert record.status_code == 201
    suggestions = client.get(
        f"/api/v1/children/{child['id']}/activity-suggestions", headers=family_headers
    ).json()["items"]
    assert suggestions[0]["optional"] is True
    assert suggestions[0]["last_practice_days_ago"] == 0
    report = client.get(f"/api/v1/children/{child['id']}/report", headers=family_headers).json()
    assert report["overview"]["activity_records"] == 1
    trends = report["overview_trends"]
    assert trends["timezone"] == "Asia/Shanghai"
    assert trends["aggregation"] == "equal_time_sum"
    assert len(trends["buckets"]) == 7
    assert sum(item["activity_records"] for item in trends["buckets"]) == 1
    assert "notice" not in report
    assert len(report["review_activity"]) == 7


def test_fixed_activity_is_one_source_for_settings_calendar_and_today(
    client, family_headers, child
) -> None:
    target = local_date()
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "乒乓球", "kind": "activity"},
    ).json()
    schedule = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "weekdays": [target.weekday()],
            "start_time": "10:00:00",
            "end_time": "11:00:00",
        },
    )
    assert schedule.status_code == 201
    settings_item = schedule.json()
    calendar_items = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["items"]
    dashboard_items = client.get(
        f"/api/v1/children/{child['id']}/dashboard",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["schedule_items"]
    assert len(calendar_items) == len(dashboard_items) == 1
    projected = calendar_items[0]
    assert projected == dashboard_items[0]
    assert projected["id"] == settings_item["id"]
    assert projected["subject_id"] == subject["id"]
    assert projected["start_time"] == "10:00"
    assert projected["end_time"] == "11:00"
    assert projected["source"] == "activity_schedule"
    removed = client.delete(
        f"/api/v1/activity-schedules/{settings_item['id']}", headers=family_headers
    )
    assert removed.status_code == 204
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/schedule",
            headers=family_headers,
            params={"day": target.isoformat()},
        ).json()["items"]
        == []
    )
    assert (
        client.delete(
            f"/api/v1/activity-schedules/{settings_item['id']}",
            headers={"X-Family-ID": "other-family"},
        ).status_code
        == 404
    )


def test_fixed_activity_requires_complete_time_range(client, family_headers, child) -> None:
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "篮球", "kind": "activity"},
    ).json()
    response = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={"child_id": child["id"], "subject_id": subject["id"], "weekdays": [2]},
    )
    assert response.status_code == 422


def test_calendar_event_crud_and_report_ranges(client, family_headers, child) -> None:
    target = local_date()
    created = client.post(
        "/api/v1/calendar-events",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "英语辅导班",
            "event_date": target.isoformat(),
            "start_time": "19:00:00",
            "end_time": "20:00:00",
            "kind": "class",
            "repeat_weekly": True,
        },
    )
    assert created.status_code == 201
    event_id = created.json()["id"]
    updated = client.patch(
        f"/api/v1/calendar-events/{event_id}",
        headers=family_headers,
        json={"name": "英语阅读班", "end_time": "20:30:00"},
    )
    assert updated.status_code == 200
    items = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["items"]
    assert items[0]["name"] == "英语阅读班"
    assert items[0]["end_time"] == "20:30"
    assert (
        client.patch(
            f"/api/v1/calendar-events/{event_id}",
            headers={"X-Family-ID": "other-family"},
            json={"name": "越权修改"},
        ).status_code
        == 404
    )
    assert (
        client.delete(f"/api/v1/calendar-events/{event_id}", headers=family_headers).status_code
        == 204
    )
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/schedule",
            headers=family_headers,
            params={"day": target.isoformat()},
        ).json()["items"]
        == []
    )

    for days in (7, 30, 100):
        report = client.get(
            f"/api/v1/children/{child['id']}/report",
            headers=family_headers,
            params={"days": days},
        )
        assert report.status_code == 200
        payload = report.json()
        assert payload["range_days"] == days
        assert len(payload["review_urgency"]) == days
        assert len(payload["review_activity"]) == days
        assert len(payload["overview_trends"]["buckets"]) == 7
        assert payload["overview_trends"]["timezone"] == "Asia/Shanghai"
        assert payload["overview_trends"]["aggregation"] == "equal_time_sum"
        for key, total in payload["overview"].items():
            assert total == 0
            assert sum(item[key] for item in payload["overview_trends"]["buckets"]) == total
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/report",
            headers=family_headers,
            params={"days": 14},
        ).status_code
        == 400
    )


def test_report_trends_end_at_today_and_remain_family_scoped(
    client, app, family_headers, child
) -> None:
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "轮滑", "kind": "activity"},
    ).json()
    today_at = datetime.combine(local_date(), time(12), tzinfo=SHANGHAI).astimezone(UTC)
    future_at = datetime.combine(
        local_date() + timedelta(days=1), time(0, 30), tzinfo=SHANGHAI
    ).astimezone(UTC)
    with app.state.database.session_factory() as db:
        db.add_all(
            [
                ActivityRecord(
                    family_id=family_headers["X-Family-ID"],
                    child_id=child["id"],
                    subject_id=subject["id"],
                    occurred_at=today_at,
                ),
                ActivityRecord(
                    family_id=family_headers["X-Family-ID"],
                    child_id=child["id"],
                    subject_id=subject["id"],
                    occurred_at=future_at,
                ),
            ]
        )
        db.commit()

    report = client.get(
        f"/api/v1/children/{child['id']}/report?days=7", headers=family_headers
    ).json()

    assert report["overview"]["activity_records"] == 1
    assert sum(item["activity_records"] for item in report["overview_trends"]["buckets"]) == 1
    assert report["overview_trends"]["buckets"][-1]["end_day"] == local_date().isoformat()
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/report?days=7",
            headers={"X-Family-ID": "other-family"},
        ).status_code
        == 404
    )


def test_calendar_creation_retry_is_idempotent(client, app, family_headers, child) -> None:
    headers = {**family_headers, "Idempotency-Key": "calendar-stable-retry-001"}
    payload = {
        "child_id": child["id"],
        "name": "英语辅导班",
        "event_date": local_date().isoformat(),
        "start_time": "19:00:00",
        "end_time": "20:00:00",
        "kind": "class",
        "repeat_weekly": True,
    }
    first = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    second = client.post("/api/v1/calendar-events", headers=headers, json=payload)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    mismatch = client.post(
        "/api/v1/calendar-events", headers=headers, json={**payload, "name": "不同日程"}
    )
    assert mismatch.status_code == 409


def test_report_activity_groups_by_shanghai_day(client, app, family_headers, child) -> None:
    submission = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "数学，进位加法",
        },
    ).json()
    assert app.state.worker.process_one() is True
    draft = client.get(f"/api/v1/submissions/{submission['id']}", headers=family_headers).json()
    confirmed = client.post(
        f"/api/v1/submissions/{submission['id']}/confirm",
        headers=family_headers,
        json={"proposal": draft["proposal"]},
    ).json()
    today = local_date()
    early = datetime.combine(today, time(0, 30), tzinfo=SHANGHAI).astimezone(UTC)
    late = datetime.combine(today, time(23, 30), tzinfo=SHANGHAI).astimezone(UTC)
    with app.state.database.session_factory() as db:
        db.add_all(
            [
                ReviewFeedback(
                    family_id=family_headers["X-Family-ID"],
                    review_item_id=confirmed["review_item_ids"][0],
                    action="complete",
                    occurred_at=early,
                ),
                ReviewFeedback(
                    family_id=family_headers["X-Family-ID"],
                    review_item_id=confirmed["review_item_ids"][0],
                    action="complete",
                    occurred_at=late,
                ),
            ]
        )
        db.commit()
    report = client.get(
        f"/api/v1/children/{child['id']}/report?days=7", headers=family_headers
    ).json()
    assert report["review_activity"][-1]["day"] == today.isoformat()
    assert report["review_activity"][-1]["count"] == 2


def test_historical_activity_suggestion_uses_target_week(
    client, app, family_headers, child
) -> None:
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "武术", "kind": "activity"},
    ).json()
    created = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "weekdays": [],
            "target_per_week": 2,
        },
    )
    assert created.status_code == 201
    target = local_date() - timedelta(days=14)
    target_at = datetime.combine(target, time(12), tzinfo=SHANGHAI).astimezone(UTC)
    current_at = datetime.combine(local_date(), time(12), tzinfo=SHANGHAI).astimezone(UTC)
    with app.state.database.session_factory() as db:
        db.add_all(
            [
                ActivityRecord(
                    family_id=family_headers["X-Family-ID"],
                    child_id=child["id"],
                    subject_id=subject["id"],
                    occurred_at=target_at,
                ),
                ActivityRecord(
                    family_id=family_headers["X-Family-ID"],
                    child_id=child["id"],
                    subject_id=subject["id"],
                    occurred_at=current_at,
                ),
            ]
        )
        db.commit()
    item = client.get(
        f"/api/v1/children/{child['id']}/activity-suggestions",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["items"][0]
    assert item["completed_this_week"] == 1
