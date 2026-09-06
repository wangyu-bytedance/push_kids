from push_kids.platform.time import local_date


def create_travel(client, headers, child_id, **overrides):
    payload = {
        "child_id": child_id,
        "name": "上学",
        "weekdays": [local_date().weekday()],
        "start_time": "07:30:00",
        "end_time": "08:10:00",
        **overrides,
    }
    return client.post(
        "/api/v1/travel-arrangements",
        headers={**headers, "Idempotency-Key": "travel-stable-key-001"},
        json=payload,
    )


def test_travel_crud_projects_only_to_calendar(client, family_headers, child) -> None:
    target = local_date()
    created = create_travel(client, family_headers, child["id"])
    assert created.status_code == 201
    travel = created.json()
    assert travel["name"] == "上学"
    assert travel["weekdays"] == [target.weekday()]

    listed = client.get(
        f"/api/v1/children/{child['id']}/travel-arrangements", headers=family_headers
    ).json()["items"]
    assert [item["id"] for item in listed] == [travel["id"]]

    calendar = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["items"]
    assert calendar[0]["source"] == "travel_arrangement"
    assert calendar[0]["kind"] == "travel"
    dashboard = client.get(
        f"/api/v1/children/{child['id']}/dashboard",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()
    assert all(item["source"] != "travel_arrangement" for item in dashboard["schedule_items"])
    report = client.get(f"/api/v1/children/{child['id']}/report", headers=family_headers).json()
    assert report["overview"]["activity_records"] == 0

    updated = client.patch(
        f"/api/v1/travel-arrangements/{travel['id']}",
        headers=family_headers,
        json={"name": "去学校", "start_time": "07:20:00"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "去学校"
    assert updated.json()["start_time"] == "07:20:00"

    deleted = client.delete(f"/api/v1/travel-arrangements/{travel['id']}", headers=family_headers)
    assert deleted.status_code == 204
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/travel-arrangements", headers=family_headers
        ).json()["items"]
        == []
    )


def test_calendar_conflicts_cover_travel_and_existing_sources(
    client, family_headers, child
) -> None:
    target = local_date()
    travel = create_travel(client, family_headers, child["id"])
    assert travel.status_code == 201
    event = client.post(
        "/api/v1/calendar-events",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "早读",
            "event_date": target.isoformat(),
            "start_time": "07:50:00",
            "end_time": "08:20:00",
            "kind": "other",
            "repeat_weekly": False,
        },
    )
    assert event.status_code == 201
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "晨练", "kind": "activity"},
    ).json()
    schedule = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "weekdays": [target.weekday()],
            "start_time": "08:00:00",
            "end_time": "08:30:00",
        },
    )
    assert schedule.status_code == 201

    items = client.get(
        f"/api/v1/children/{child['id']}/schedule",
        headers=family_headers,
        params={"day": target.isoformat()},
    ).json()["items"]
    by_name = {item["name"]: item for item in items}
    assert by_name["上学"]["has_conflict"] is True
    assert by_name["早读"]["has_conflict"] is True
    assert by_name["晨练"]["has_conflict"] is True
    assert [conflict["name"] for conflict in by_name["上学"]["conflicts"]] == [
        "早读",
        "晨练",
    ]
    assert [conflict["overlap_minutes"] for conflict in by_name["上学"]["conflicts"]] == [20, 10]


def test_travel_validation_scope_and_idempotency(client, family_headers, child) -> None:
    first = create_travel(client, family_headers, child["id"])
    second = create_travel(client, family_headers, child["id"])
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    mismatch = create_travel(client, family_headers, child["id"], name="放学")
    assert mismatch.status_code == 409

    invalid = client.post(
        "/api/v1/travel-arrangements",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "上学",
            "weekdays": [],
            "start_time": "08:00:00",
            "end_time": "08:00:00",
        },
    )
    assert invalid.status_code == 422
    invalid_patch = client.patch(
        f"/api/v1/travel-arrangements/{first.json()['id']}",
        headers=family_headers,
        json={"start_time": "09:00:00"},
    )
    assert invalid_patch.status_code == 400
    unchanged = client.get(
        f"/api/v1/children/{child['id']}/travel-arrangements", headers=family_headers
    ).json()["items"][0]
    assert unchanged["start_time"] == "07:30:00"
    assert (
        client.patch(
            f"/api/v1/travel-arrangements/{first.json()['id']}",
            headers={"X-Family-ID": "other-family"},
            json={"name": "越权"},
        ).status_code
        == 404
    )


def test_cross_source_calendar_capacity_is_twenty_and_delete_releases_a_slot(
    client, family_headers, child
) -> None:
    target = local_date()
    travel = create_travel(client, family_headers, child["id"])
    assert travel.status_code == 201
    subject = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "体能", "kind": "activity"},
    ).json()
    schedule = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject["id"],
            "weekdays": [target.weekday()],
            "start_time": "10:00:00",
            "end_time": "10:30:00",
        },
    )
    assert schedule.status_code == 201

    for index in range(18):
        created = client.post(
            "/api/v1/calendar-events",
            headers=family_headers,
            json={
                "child_id": child["id"],
                "name": f"事项 {index + 1}",
                "event_date": target.isoformat(),
                "start_time": "12:00:00",
                "end_time": "12:30:00",
                "kind": "other",
                "repeat_weekly": False,
            },
        )
        assert created.status_code == 201

    rejected = client.post(
        "/api/v1/calendar-events",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "第 21 项",
            "event_date": target.isoformat(),
            "start_time": "13:00:00",
            "end_time": "13:30:00",
            "kind": "other",
            "repeat_weekly": False,
        },
    )
    assert rejected.status_code == 409
    assert "最多保留 20 项" in rejected.json()["error"]["message"]

    assert (
        client.delete(
            f"/api/v1/travel-arrangements/{travel.json()['id']}", headers=family_headers
        ).status_code
        == 204
    )
    accepted = client.post(
        "/api/v1/calendar-events",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "name": "补位事项",
            "event_date": target.isoformat(),
            "start_time": "13:00:00",
            "end_time": "13:30:00",
            "kind": "other",
            "repeat_weekly": False,
        },
    )
    assert accepted.status_code == 201
