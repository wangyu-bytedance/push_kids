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
