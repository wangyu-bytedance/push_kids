from __future__ import annotations

from fastapi.testclient import TestClient


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _idempotent(actor: str, key: str) -> dict[str, str]:
    return {**_actor(actor), "Idempotency-Key": key}


def test_create_join_approve_and_role_boundaries(client: TestClient) -> None:
    assert client.get("/api/v1/me").status_code == 401
    assert client.get("/api/v1/me", headers=_actor("parent-a")).json() == {
        "state": "unbound",
        "family": None,
        "member": None,
        "children": [],
        "request": None,
    }

    created = client.post(
        "/api/v1/families",
        headers=_idempotent("parent-a", "family-create-001"),
        json={
            "display_name": "小雨的家",
            "relationship_label": "妈妈",
            "child": {
                "name": "小雨",
                "grade": "小学二年级",
                "daily_budget_minutes": 15,
            },
        },
    )
    assert created.status_code == 201
    assert created.json()["state"] == "bound"
    assert created.json()["member"]["role"] == "manager"
    child_id = created.json()["children"][0]["id"]
    duplicate = client.post(
        "/api/v1/families",
        headers=_idempotent("parent-a", "family-create-001"),
        json={
            "display_name": "不会重复创建",
            "relationship_label": "妈妈",
            "child": {"name": "不会重复创建", "daily_budget_minutes": 15},
        },
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["family"]["id"] == created.json()["family"]["id"]
    assert [item["id"] for item in duplicate.json()["children"]] == [child_id]

    invite = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("parent-a", "invite-create-001"),
        json={"expires_in_hours": 24},
    )
    assert invite.status_code == 201
    token = invite.json()["token"]
    assert token not in str(invite.json()["id"])
    preview = client.post(
        "/api/v1/family-invites/preview",
        headers=_actor("grandparent-b"),
        json={"token": token},
    )
    assert preview.status_code == 200
    assert preview.json()["family_name"] == "小雨的家"
    assert preview.json()["child_names"] == ["小雨"]

    application = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("grandparent-b", "join-request-001"),
        json={"token": token, "relationship_label": "奶奶"},
    )
    assert application.status_code == 201
    assert application.json()["status"] == "pending"
    repeated = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("grandparent-b", "join-request-002"),
        json={"token": token, "relationship_label": "奶奶"},
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == application.json()["id"]
    assert client.get("/api/v1/me", headers=_actor("grandparent-b")).json()["state"] == "pending"

    requests = client.get("/api/v1/families/current/requests", headers=_actor("parent-a"))
    assert requests.status_code == 200
    assert [item["id"] for item in requests.json()] == [application.json()["id"]]
    approved = client.post(
        f"/api/v1/family-requests/{application.json()['id']}/approve",
        headers=_idempotent("parent-a", "join-approve-001"),
        json={"role": "viewer"},
    )
    assert approved.status_code == 200
    assert approved.json()["role"] == "viewer"
    approval_replay = client.post(
        f"/api/v1/family-requests/{application.json()['id']}/approve",
        headers=_idempotent("parent-a", "join-approve-001"),
        json={"role": "viewer"},
    )
    assert approval_replay.status_code == 200
    assert approval_replay.json()["id"] == approved.json()["id"]
    assert (
        client.post(
            f"/api/v1/family-requests/{application.json()['id']}/approve",
            headers=_idempotent("parent-a", "join-approve-different"),
            json={"role": "editor"},
        ).status_code
        == 409
    )
    assert client.get("/api/v1/me", headers=_actor("grandparent-b")).json()["state"] == "bound"
    assert client.get("/api/v1/children", headers=_actor("grandparent-b")).status_code == 200
    denied_write = client.post(
        "/api/v1/children",
        headers=_actor("grandparent-b"),
        json={"name": "不能创建", "daily_budget_minutes": 15},
    )
    assert denied_write.status_code == 403

    members = client.get("/api/v1/families/current/members", headers=_actor("parent-a"))
    assert members.status_code == 200
    assert {item["relationship_label"] for item in members.json()} == {"妈妈", "奶奶"}
    own_manager = next(item for item in members.json() if item["is_self"])
    last_manager = client.patch(
        f"/api/v1/families/current/members/{own_manager['id']}",
        headers=_actor("parent-a"),
        json={"role": "editor"},
    )
    assert last_manager.status_code == 409


def test_revoke_reject_and_cancel_are_terminal(client: TestClient) -> None:
    client.post(
        "/api/v1/families",
        headers=_idempotent("manager-a", "family-create-002"),
        json={
            "display_name": "星星的家",
            "relationship_label": "爸爸",
            "child": {"name": "星星", "daily_budget_minutes": 15},
        },
    )
    invite = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("manager-a", "invite-create-002"),
        json={},
    ).json()
    request = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("applicant-b", "join-request-003"),
        json={"token": invite["token"], "relationship_label": "爷爷"},
    ).json()
    rejected = client.post(
        f"/api/v1/family-requests/{request['id']}/reject",
        headers=_idempotent("manager-a", "join-reject-001"),
        json={"reason": "请重新确认邀请"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"
    replayed_rejection = client.post(
        f"/api/v1/family-requests/{request['id']}/reject",
        headers=_idempotent("manager-a", "join-reject-001"),
        json={"reason": "请重新确认邀请"},
    )
    assert replayed_rejection.status_code == 200
    assert replayed_rejection.json()["id"] == request["id"]
    assert (
        client.post(
            f"/api/v1/family-requests/{request['id']}/reject",
            headers=_idempotent("manager-a", "join-reject-different"),
            json={},
        ).status_code
        == 409
    )
    assert client.get("/api/v1/me", headers=_actor("applicant-b")).json()["state"] == "unbound"

    revoked = client.delete(
        f"/api/v1/families/current/invites/{invite['id']}", headers=_actor("manager-a")
    )
    assert revoked.status_code == 204
    assert (
        client.post(
            "/api/v1/family-invites/preview",
            headers=_actor("applicant-c"),
            json={"token": invite["token"]},
        ).status_code
        == 410
    )

    active_invite = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("manager-a", "invite-create-003"),
        json={},
    ).json()
    client.post(
        "/api/v1/family-requests",
        headers=_idempotent("applicant-c", "join-request-004"),
        json={"token": active_invite["token"], "relationship_label": "外公"},
    )
    cancelled = client.delete("/api/v1/family-requests/current", headers=_actor("applicant-c"))
    assert cancelled.status_code == 204
    assert client.get("/api/v1/me", headers=_actor("applicant-c")).json()["state"] == "unbound"


def test_removed_members_can_rejoin_or_create_their_own_family(client: TestClient) -> None:
    manager = "manager-rejoin"
    client.post(
        "/api/v1/families",
        headers=_idempotent(manager, "family-create-rejoin"),
        json={
            "display_name": "重新加入测试家庭",
            "relationship_label": "家长",
            "child": {"name": "小树", "daily_budget_minutes": 15},
        },
    )

    def join_and_approve(actor: str, suffix: str) -> str:
        invite = client.post(
            "/api/v1/families/current/invites",
            headers=_idempotent(manager, f"invite-{suffix}"),
            json={},
        ).json()
        request = client.post(
            "/api/v1/family-requests",
            headers=_idempotent(actor, f"request-{suffix}"),
            json={"token": invite["token"], "relationship_label": "家人"},
        ).json()
        approved = client.post(
            f"/api/v1/family-requests/{request['id']}/approve",
            headers=_idempotent(manager, f"approve-{suffix}"),
            json={"role": "viewer"},
        )
        assert approved.status_code == 200
        return approved.json()["id"]

    first_member_id = join_and_approve("relative-rejoin", "rejoin-first")
    assert (
        client.delete(
            f"/api/v1/families/current/members/{first_member_id}", headers=_actor(manager)
        ).status_code
        == 204
    )
    second_member_id = join_and_approve("relative-rejoin", "rejoin-second")
    assert second_member_id != first_member_id
    assert client.get("/api/v1/me", headers=_actor("relative-rejoin")).json()["state"] == "bound"

    removed_then_creator_id = join_and_approve("relative-creator", "creator-first")
    client.delete(
        f"/api/v1/families/current/members/{removed_then_creator_id}", headers=_actor(manager)
    )
    own_family = client.post(
        "/api/v1/families",
        headers=_idempotent("relative-creator", "family-create-after-removal"),
        json={
            "display_name": "新的家庭",
            "relationship_label": "家长",
            "child": {"name": "小芽", "daily_budget_minutes": 15},
        },
    )
    assert own_family.status_code == 201
    assert own_family.json()["state"] == "bound"
    assert own_family.json()["family"]["display_name"] == "新的家庭"


def test_invite_is_single_use_and_self_removal_is_forbidden(client: TestClient) -> None:
    created = client.post(
        "/api/v1/families",
        headers=_idempotent("single-use-manager", "family-single-use"),
        json={
            "display_name": "单次邀请家庭",
            "relationship_label": "妈妈",
            "child": {"name": "小禾", "daily_budget_minutes": 15},
        },
    ).json()
    own_member_id = created["member"]["id"]
    assert (
        client.delete(
            f"/api/v1/families/current/members/{own_member_id}",
            headers=_actor("single-use-manager"),
        ).status_code
        == 409
    )

    invite = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("single-use-manager", "invite-single-use"),
        json={},
    ).json()
    listed = client.get("/api/v1/families/current/invites", headers=_actor("single-use-manager"))
    assert listed.status_code == 200
    assert listed.json() == [
        {"id": invite["id"], "status": "active", "expires_at": invite["expires_at"]}
    ]
    assert "token" not in listed.text

    first = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("single-use-first", "request-single-use-first"),
        json={"token": invite["token"], "relationship_label": "爸爸"},
    ).json()
    second = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("single-use-second", "request-single-use-second"),
        json={"token": invite["token"], "relationship_label": "奶奶"},
    ).json()
    assert len(first["request_code"]) == 6
    assert len(second["request_code"]) == 6

    approved = client.post(
        f"/api/v1/family-requests/{first['id']}/approve",
        headers=_idempotent("single-use-manager", "approve-single-use"),
        json={"role": "editor"},
    )
    assert approved.status_code == 200
    assert client.get("/api/v1/me", headers=_actor("single-use-first")).json()["state"] == "bound"
    second_state = client.get("/api/v1/me", headers=_actor("single-use-second")).json()["state"]
    assert second_state == "unbound"
    assert (
        client.get("/api/v1/families/current/requests", headers=_actor("single-use-manager")).json()
        == []
    )
    assert (
        client.get("/api/v1/families/current/invites", headers=_actor("single-use-manager")).json()
        == []
    )
    assert (
        client.post(
            f"/api/v1/family-requests/{second['id']}/approve",
            headers=_idempotent("single-use-manager", "approve-exhausted-invite"),
            json={"role": "viewer"},
        ).status_code
        == 410
    )
    assert (
        client.post(
            "/api/v1/family-invites/preview",
            headers=_actor("single-use-third"),
            json={"token": invite["token"]},
        ).status_code
        == 410
    )


def test_revoking_invite_unbinds_pending_applicant(client: TestClient) -> None:
    client.post(
        "/api/v1/families",
        headers=_idempotent("revoke-manager", "family-revoke-cascade"),
        json={
            "display_name": "撤销邀请家庭",
            "relationship_label": "爸爸",
            "child": {"name": "小满", "daily_budget_minutes": 15},
        },
    )
    invite = client.post(
        "/api/v1/families/current/invites",
        headers=_idempotent("revoke-manager", "invite-revoke-cascade"),
        json={},
    ).json()
    request = client.post(
        "/api/v1/family-requests",
        headers=_idempotent("revoke-applicant", "request-revoke-cascade"),
        json={"token": invite["token"], "relationship_label": "外婆"},
    )
    assert request.status_code == 201
    assert client.get("/api/v1/me", headers=_actor("revoke-applicant")).json()["state"] == "pending"
    assert (
        client.delete(
            f"/api/v1/families/current/invites/{invite['id']}",
            headers=_actor("revoke-manager"),
        ).status_code
        == 204
    )
    assert client.get("/api/v1/me", headers=_actor("revoke-applicant")).json()["state"] == "unbound"


def test_invite_preview_rate_limit_and_sqlite_foreign_keys(client: TestClient, app) -> None:
    with app.state.database.engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
    for _ in range(20):
        response = client.post(
            "/api/v1/family-invites/preview",
            headers=_actor("preview-rate-limit"),
            json={"token": "x" * 32},
        )
        assert response.status_code == 404
    limited = client.post(
        "/api/v1/family-invites/preview",
        headers=_actor("preview-rate-limit"),
        json={"token": "x" * 32},
    )
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "rate_limited"
