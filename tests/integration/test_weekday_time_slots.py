from datetime import timedelta

from push_kids.platform.time import local_date

SLOT_CAPABILITY = {"X-Client-Capabilities": "weekly-time-slots-v1"}


def with_slot_capability(headers: dict[str, str]) -> dict[str, str]:
    return {**headers, **SLOT_CAPABILITY}


def test_activity_uses_exact_time_for_each_weekday_and_old_client_fails_closed(
    client, family_headers, child
) -> None:
    today = local_date()
    tomorrow = today + timedelta(days=1)
    headers = with_slot_capability(family_headers)
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "线上英语", "kind": "activity"},
    ).json()

    created = client.post(
        "/api/v1/activity-schedules",
        headers=headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "time_slots": [
                {
                    "weekday": tomorrow.weekday(),
                    "start_time": "19:00:00",
                    "end_time": "20:00:00",
                },
                {
                    "weekday": today.weekday(),
                    "start_time": "18:00:00",
                    "end_time": "19:00:00",
                },
            ],
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert [item["weekday"] for item in payload["time_slots"]] == sorted(
        [today.weekday(), tomorrow.weekday()]
    )
    assert payload["start_time"] is None
    assert payload["end_time"] is None

    for target, expected in ((today, ("18:00", "19:00")), (tomorrow, ("19:00", "20:00"))):
        item = client.get(
            f"/api/v1/children/{child['id']}/schedule",
            headers=family_headers,
            params={"day": target.isoformat()},
        ).json()["items"][0]
        assert (item["start_time"], item["end_time"]) == expected

    suggestion = client.get(
        f"/api/v1/children/{child['id']}/activity-suggestions",
        headers=family_headers,
        params={"day": tomorrow.isoformat()},
    ).json()["items"][0]
    assert (suggestion["start_time"], suggestion["end_time"]) == ("19:00", "20:00")

    stale = client.get(f"/api/v1/children/{child['id']}/activity-schedules", headers=family_headers)
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "client_upgrade_required"


def test_travel_replaces_complete_slot_set_and_projects_conflict_only_on_matching_day(
    client, family_headers, child
) -> None:
    today = local_date()
    tomorrow = today + timedelta(days=1)
    headers = with_slot_capability(family_headers)
    created = client.post(
        "/api/v1/travel-arrangements",
        headers={**headers, "Idempotency-Key": "mixed-travel-key-001"},
        json={
            "child_id": child["id"],
            "name": "接送",
            "time_slots": [
                {
                    "weekday": today.weekday(),
                    "start_time": "17:00:00",
                    "end_time": "18:00:00",
                },
                {
                    "weekday": tomorrow.weekday(),
                    "start_time": "19:00:00",
                    "end_time": "20:00:00",
                },
            ],
        },
    )
    assert created.status_code == 201
    travel_id = created.json()["id"]

    event = client.post(
        "/api/v1/calendar-events",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "晚餐",
            "event_date": tomorrow.isoformat(),
            "start_time": "19:30:00",
            "end_time": "20:30:00",
            "kind": "other",
            "repeat_weekly": False,
        },
    )
    assert event.status_code == 201
    today_items = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": today.isoformat()},
    ).json()["items"]
    assert today_items[0]["has_conflict"] is False
    tomorrow_items = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": tomorrow.isoformat()},
    ).json()["items"]
    assert all(item["has_conflict"] for item in tomorrow_items)

    updated = client.patch(
        f"/api/v1/travel-arrangements/{travel_id}",
        headers=headers,
        json={
            "time_slots": [
                {
                    "weekday": tomorrow.weekday(),
                    "start_time": "20:00:00",
                    "end_time": "21:00:00",
                }
            ]
        },
    )
    assert updated.status_code == 200
    assert updated.json()["weekdays"] == [tomorrow.weekday()]
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/schedule",
            headers=family_headers,
            params={"day": today.isoformat()},
        ).json()["items"]
        == []
    )


def test_invalid_mixed_slot_mutation_is_atomic(client, family_headers, child) -> None:
    headers = with_slot_capability(family_headers)
    created = client.post(
        "/api/v1/travel-arrangements",
        headers={**headers, "Idempotency-Key": "mixed-travel-key-atomic"},
        json={
            "child_id": child["id"],
            "name": "上学",
            "time_slots": [{"weekday": 1, "start_time": "07:30:00", "end_time": "08:10:00"}],
        },
    )
    assert created.status_code == 201
    travel_id = created.json()["id"]
    invalid = client.patch(
        f"/api/v1/travel-arrangements/{travel_id}",
        headers=headers,
        json={
            "time_slots": [
                {"weekday": 1, "start_time": "07:30:00", "end_time": "08:10:00"},
                {"weekday": 1, "start_time": "09:00:00", "end_time": "10:00:00"},
            ]
        },
    )
    assert invalid.status_code == 400
    assert "同一天" in invalid.json()["error"]["message"]
    listed = client.get(
        f"/api/v1/children/{child['id']}/travel-arrangements", headers=headers
    ).json()["items"]
    assert listed[0]["time_slots"] == [
        {"weekday": 1, "start_time": "07:30:00", "end_time": "08:10:00"}
    ]
