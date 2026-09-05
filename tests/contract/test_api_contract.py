def test_openapi_contains_core_contracts(app) -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/submissions/{submission_id}/confirm" in paths
    assert "/api/v1/children/{child_id}/dashboard" in paths
    assert "/api/v1/reviews/{review_id}/feedback" in paths
    assert "/api/v1/activity-records" in paths


def test_family_header_is_required(client) -> None:
    response = client.get("/api/v1/children")
    assert response.status_code == 422


def test_child_payload_validation(client, family_headers) -> None:
    response = client.post(
        "/api/v1/children",
        headers=family_headers,
        json={"name": "", "daily_budget_minutes": 1000},
    )
    assert response.status_code == 422


def test_subject_view_marks_preset_and_custom_origin(client, family_headers) -> None:
    child_id = client.post(
        "/api/v1/children",
        headers=family_headers,
        json={"name": "小满", "daily_budget_minutes": 15},
    ).json()["id"]
    preset = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child_id, "name": "数学", "kind": "learning"},
    )
    custom = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child_id, "name": "围棋", "kind": "activity"},
    )
    assert preset.status_code == custom.status_code == 201, preset.text
    assert preset.json()["is_custom"] is False
    assert custom.json()["is_custom"] is True
    listed = client.get(f"/api/v1/children/{child_id}/subjects", headers=family_headers)
    assert listed.status_code == 200
    assert {item["name"]: item["is_custom"] for item in listed.json()} == {
        "数学": False,
        "围棋": True,
    }
