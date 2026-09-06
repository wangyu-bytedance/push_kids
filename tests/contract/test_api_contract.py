def test_openapi_contains_core_contracts(app) -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/submissions/{submission_id}/confirm" in paths
    assert "/api/v1/children/{child_id}/dashboard" in paths
    assert "/api/v1/reviews/{review_id}/feedback" in paths
    assert "/api/v1/activity-records" in paths
    submission = app.openapi()["components"]["schemas"]["SubmissionView"]
    assert submission["properties"]["display_groups"]["type"] == "array"


def test_child_profile_lifecycle_is_part_of_the_contract(app) -> None:
    """多孩子切换依赖档案生命周期与 active 标记，客户端要能据此渲染切换列表。"""
    document = app.openapi()
    paths = document["paths"]
    assert "/api/v1/children/{child_id}/archive" in paths
    assert "/api/v1/children/{child_id}/restore" in paths
    parameters = {item["name"] for item in paths["/api/v1/children"]["get"].get("parameters", [])}
    assert "include_archived" in parameters
    child_view = document["components"]["schemas"]["ChildView"]
    assert child_view["properties"]["active"]["type"] == "boolean"
    assert "active" in child_view["required"]
    # 开通家庭时孩子信息可选，家长可以先建家庭再建档案。
    family_create = document["components"]["schemas"]["FamilyCreate"]
    assert "child" not in family_create.get("required", [])


def test_durable_data_deletion_is_part_of_the_contract(app) -> None:
    document = app.openapi()
    paths = document["paths"]
    assert "/api/v1/children/{child_id}/deletion-requests" in paths
    assert "/api/v1/families/current/deletion-requests" in paths
    assert "/api/v1/deletion-requests/{request_id}" in paths
    assert "/api/v1/deletion-requests/{request_id}/retry" in paths
    status = document["components"]["schemas"]["DeletionRequestView"]
    assert {"id", "target_type", "state", "retryable"}.issubset(status["properties"])
    assert "target_id" not in status["properties"]
    assert "confirmation_name" not in status["properties"]


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


def test_notification_channel_is_part_of_the_contract(app) -> None:
    """小程序要靠这些字段决定是否弹订阅授权、弹哪些模板，所以它们是契约而不是内部细节。"""
    document = app.openapi()
    paths = document["paths"]
    assert "/api/v1/notifications/settings" in paths
    assert "/api/v1/notifications/preferences" in paths
    assert "/api/v1/notifications/subscriptions" in paths
    assert "/api/v1/notifications/deliveries" in paths
    assert "/api/v1/notifications/dispatch" in paths
    channel = document["components"]["schemas"]["ChannelView"]
    assert channel["properties"]["available"]["type"] == "boolean"
    assert channel["properties"]["template_ids"]["type"] == "array"
    preference = document["components"]["schemas"]["PreferenceView"]
    for field in ("type", "label", "enabled", "managers_only", "subscription_status"):
        assert field in preference["required"], field
    # 投递结果只暴露安全的分类码，绝不返回微信原始响应或接收标识。
    delivery = document["components"]["schemas"]["DeliveryView"]
    assert set(delivery["properties"]) == {
        "type",
        "state",
        "headline",
        "detail",
        "scheduled_at",
        "sent_at",
        "result_code",
    }


def test_notification_endpoints_require_a_member_identity(client) -> None:
    """本地 X-Family-ID 通道没有成员身份，不能用来改别人的提醒开关。"""
    assert client.get("/api/v1/notifications/settings").status_code == 422
    denied = client.get("/api/v1/notifications/settings", headers={"X-Family-ID": "family-test-a"})
    assert denied.status_code == 403
