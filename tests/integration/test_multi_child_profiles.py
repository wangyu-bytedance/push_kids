"""FEAT-005 一家庭多孩子档案：数量上限、重名、归档语义、权限与跨档案隔离。

这些用例针对 SPEC-20260906-MULTI-CHILD-01 的 AC-001~AC-005。改造前会失败的用例已在
docstring 中标注，用来证明它们真的依赖新行为，而不是恒真断言。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from push_kids.persistence.models import FamilyAuditEvent
from sqlalchemy import select

API = "/api/v1"


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _idempotent(actor: str, key: str) -> dict[str, str]:
    return {**_actor(actor), "Idempotency-Key": key}


def _create_child(client: TestClient, headers: dict[str, str], name: str, **extra: object) -> dict:
    payload: dict[str, object] = {"name": name, "daily_budget_minutes": 15}
    payload.update(extra)
    return client.post(f"{API}/children", headers=headers, json=payload).json()


def _open_family(client: TestClient, actor: str, key: str, child_name: str | None) -> dict:
    body: dict[str, object] = {"display_name": f"{actor}的家", "relationship_label": "妈妈"}
    if child_name is not None:
        body["child"] = {"name": child_name, "daily_budget_minutes": 15}
    response = client.post(f"{API}/families", headers=_idempotent(actor, key), json=body)
    assert response.status_code == 201, response.text
    return response.json()


def _submit_and_process(
    client: TestClient, app, headers: dict[str, str], child_id: str, text: str
) -> dict:
    occurred = datetime.now(UTC) - timedelta(days=4)
    created = client.post(
        f"{API}/submissions",
        headers=headers,
        json={"child_id": child_id, "occurred_at": occurred.isoformat(), "input_text": text},
    )
    assert created.status_code == 202, created.text
    assert app.state.worker.process_one() is True
    pending = client.get(f"{API}/submissions/{created.json()['id']}", headers=headers)
    assert pending.json()["state"] == "pending_confirmation"
    return pending.json()


def test_family_can_hold_several_children_with_separate_data(
    client: TestClient, app, family_headers: dict[str, str]
) -> None:
    """AC-001：两个档案并存，科目、提交与确认结果互不可见。"""
    first = _create_child(client, family_headers, "小雨", grade="小学二年级")
    second = _create_child(client, family_headers, "小星", grade="小学四年级")
    assert first["active"] is True
    assert second["active"] is True

    listed = client.get(f"{API}/children", headers=family_headers)
    assert listed.status_code == 200
    # 创建顺序稳定，切换列表才不会每次刷新都跳动。
    assert [item["name"] for item in listed.json()] == ["小雨", "小星"]

    subject = client.post(
        f"{API}/subjects",
        headers=family_headers,
        json={"child_id": first["id"], "name": "语文", "kind": "learning"},
    )
    assert subject.status_code == 201

    first_subjects = client.get(
        f"{API}/children/{first['id']}/subjects", headers=family_headers
    ).json()
    assert [item["name"] for item in first_subjects] == ["语文"]
    assert (
        client.get(f"{API}/children/{second['id']}/subjects", headers=family_headers).json() == []
    )

    mine = _submit_and_process(client, app, family_headers, first["id"], "语文，背了古诗")
    theirs = _submit_and_process(client, app, family_headers, second["id"], "数学，两位数加法")

    # 第二个孩子不能借用第一个孩子的科目，否则确认会把记录写到错误的档案下。
    borrowed = client.post(
        f"{API}/submissions/{theirs['id']}/confirm",
        headers=family_headers,
        json={
            "manual_entry": True,
            "subject_id": subject.json()["id"],
            "proposal": theirs["proposal"],
        },
    )
    assert borrowed.status_code == 404

    assert (
        client.post(
            f"{API}/submissions/{mine['id']}/confirm",
            headers=family_headers,
            json={"proposal": mine["proposal"]},
        ).status_code
        == 200
    )

    first_ids = [
        item["id"]
        for item in client.get(
            f"{API}/submissions?child_id={first['id']}", headers=family_headers
        ).json()
    ]
    second_ids = [
        item["id"]
        for item in client.get(
            f"{API}/submissions?child_id={second['id']}", headers=family_headers
        ).json()
    ]
    assert first_ids == [mine["id"]]
    assert second_ids == [theirs["id"]]

    # 确认只影响自己的看板，不给另一个孩子造复习债。
    assert (
        client.get(f"{API}/children/{second['id']}/dashboard", headers=family_headers).json()[
            "todo_count"
        ]
        == 0
    )
    assert (
        client.get(f"{API}/children/{first['id']}/dashboard", headers=family_headers).json()[
            "todo_count"
        ]
        > 0
    )


def test_active_child_limit_is_enforced(client: TestClient, family_headers: dict[str, str]) -> None:
    """AC-002：在用档案上限 5。改造前无上限，第 6 个会返回 201，本用例会失败。"""
    for index in range(5):
        created = client.post(
            f"{API}/children",
            headers=family_headers,
            json={"name": f"孩子{index}", "daily_budget_minutes": 15},
        )
        assert created.status_code == 201

    overflow = client.post(
        f"{API}/children",
        headers=family_headers,
        json={"name": "第六个", "daily_budget_minutes": 15},
    )
    assert overflow.status_code == 409
    assert "5" in overflow.json()["error"]["message"]
    # 被拒之后不能留下半条记录。
    assert len(client.get(f"{API}/children", headers=family_headers).json()) == 5

    first_id = client.get(f"{API}/children", headers=family_headers).json()[0]["id"]
    archived = client.post(
        f"{API}/children/{first_id}/archive",
        headers=family_headers,
    )
    assert archived.status_code == 200
    # 归档腾出名额，家长不必删除历史就能建新档案。
    assert (
        client.post(
            f"{API}/children",
            headers=family_headers,
            json={"name": "第六个", "daily_budget_minutes": 15},
        ).status_code
        == 201
    )


def test_duplicate_active_child_name_is_rejected_but_archived_name_is_reusable(
    client: TestClient, family_headers: dict[str, str]
) -> None:
    """AC-002：在用档案不许重名。改造前重名可建，本用例会失败。"""
    first = _create_child(client, family_headers, "小雨")
    duplicate = client.post(
        f"{API}/children",
        headers=family_headers,
        json={"name": " 小雨 ", "daily_budget_minutes": 15},
    )
    assert duplicate.status_code == 409
    assert len(client.get(f"{API}/children", headers=family_headers).json()) == 1

    second = _create_child(client, family_headers, "小星")
    rename = client.patch(
        f"{API}/children/{second['id']}", headers=family_headers, json={"name": "小雨"}
    )
    assert rename.status_code == 409
    assert (
        client.patch(
            f"{API}/children/{second['id']}", headers=family_headers, json={"name": "小星"}
        ).status_code
        == 200
    )

    assert (
        client.post(f"{API}/children/{first['id']}/archive", headers=family_headers).status_code
        == 200
    )
    # 归档后名字释放，家长可以重新启用同一个称呼。
    assert (
        client.post(
            f"{API}/children",
            headers=family_headers,
            json={"name": "小雨", "daily_budget_minutes": 15},
        ).status_code
        == 201
    )
    # 但恢复已归档档案不能撞上现在在用的同名档案。
    restore = client.post(f"{API}/children/{first['id']}/restore", headers=family_headers)
    assert restore.status_code == 409


def test_archiving_stops_new_writes_but_keeps_history_readable(
    client: TestClient, app, family_headers: dict[str, str]
) -> None:
    """AC-003：归档只停新增，不丢历史。改造前无 active 概念，本用例会失败。"""
    child = _create_child(client, family_headers, "小雨")
    submission = _submit_and_process(client, app, family_headers, child["id"], "数学，口算练习")
    confirmed = client.post(
        f"{API}/submissions/{submission['id']}/confirm",
        headers=family_headers,
        json={"proposal": submission["proposal"]},
    )
    assert confirmed.status_code == 200

    archive = client.post(f"{API}/children/{child['id']}/archive", headers=family_headers)
    assert archive.status_code == 200
    assert archive.json()["active"] is False
    # 重复归档保持幂等，网络重试不该报错。
    assert (
        client.post(f"{API}/children/{child['id']}/archive", headers=family_headers).status_code
        == 200
    )

    assert client.get(f"{API}/children", headers=family_headers).json() == []
    everything = client.get(f"{API}/children?include_archived=true", headers=family_headers)
    assert [item["id"] for item in everything.json()] == [child["id"]]

    # 新增写入被拒。
    blocked_learning = client.post(
        f"{API}/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": "2026-09-06T03:00:00Z",
            "input_text": "还想再记一条",
            "source": "manual",
        },
    )
    assert blocked_learning.status_code == 409
    assert "归档" in blocked_learning.json()["error"]["message"]
    assert (
        client.post(
            f"{API}/subjects",
            headers=family_headers,
            json={"child_id": child["id"], "name": "英语", "kind": "learning"},
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"{API}/calendar-events",
            headers=family_headers,
            json={
                "child_id": child["id"],
                "name": "游泳课",
                "event_date": "2026-09-07",
                "start_time": "18:00",
                "end_time": "19:00",
                "kind": "class",
            },
        ).status_code
        == 409
    )

    # 历史仍可读：报表、看板、历史列表都不受归档影响。
    assert (
        client.get(f"{API}/children/{child['id']}/dashboard", headers=family_headers).status_code
        == 200
    )
    assert (
        client.get(
            f"{API}/children/{child['id']}/report?days=7", headers=family_headers
        ).status_code
        == 200
    )
    history = client.get(f"{API}/children/{child['id']}/history", headers=family_headers)
    assert history.status_code == 200
    assert history.json()["items"]

    restored = client.post(f"{API}/children/{child['id']}/restore", headers=family_headers)
    assert restored.status_code == 200
    assert restored.json()["active"] is True
    assert (
        client.post(
            f"{API}/subjects",
            headers=family_headers,
            json={"child_id": child["id"], "name": "英语", "kind": "learning"},
        ).status_code
        == 201
    )


def test_creating_a_child_can_seed_the_subjects_the_parent_picked(
    client: TestClient, family_headers: dict[str, str]
) -> None:
    """新档案不该是空科目死态；重复与空白名字会被折叠。"""
    child = _create_child(
        client, family_headers, "小雨", subject_names=["语文", "数学", " 数学 ", "  ", "围棋"]
    )
    subjects = client.get(f"{API}/children/{child['id']}/subjects", headers=family_headers).json()
    assert sorted(item["name"] for item in subjects) == ["围棋", "数学", "语文"]
    # 预置三科不算自定义，家长自己加的才算。
    by_name = {item["name"]: item for item in subjects}
    assert by_name["语文"]["is_custom"] is False
    assert by_name["围棋"]["is_custom"] is True

    plain = _create_child(client, family_headers, "小星")
    assert client.get(f"{API}/children/{plain['id']}/subjects", headers=family_headers).json() == []


def test_family_can_be_opened_without_a_child_and_get_one_later(client: TestClient) -> None:
    """AC-001：开通家庭与建立档案解耦。改造前 child 必填，无 child 会 422，本用例会失败。"""
    opened = _open_family(client, "solo-parent", "family-no-child", None)
    assert opened["state"] == "bound"
    assert opened["children"] == []

    added = client.post(
        f"{API}/children",
        headers=_actor("solo-parent"),
        json={"name": "后来才建档", "daily_budget_minutes": 20},
    )
    assert added.status_code == 201
    assert [
        item["name"]
        for item in client.get(f"{API}/me", headers=_actor("solo-parent")).json()["children"]
    ] == ["后来才建档"]


def test_child_profiles_are_scoped_to_their_own_family(client: TestClient) -> None:
    """AC-001/安全：跨家庭不可见，也不能被跨家庭归档。"""
    first = _open_family(client, "family-one", "family-one-key", "甲家孩子")
    second = _open_family(client, "family-two", "family-two-key", "乙家孩子")
    first_child = first["children"][0]["id"]
    second_child = second["children"][0]["id"]
    assert first_child != second_child

    assert [
        item["id"] for item in client.get(f"{API}/children", headers=_actor("family-one")).json()
    ] == [first_child]
    assert (
        client.get(
            f"{API}/children/{second_child}/subjects", headers=_actor("family-one")
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"{API}/children/{second_child}/archive", headers=_actor("family-one")
        ).status_code
        == 404
    )
    # 同名不同家庭互不干扰。
    assert (
        client.post(
            f"{API}/children",
            headers=_actor("family-one"),
            json={"name": "乙家孩子", "daily_budget_minutes": 15},
        ).status_code
        == 201
    )


def test_role_boundaries_for_profile_management(client: TestClient) -> None:
    """AC-004：viewer 不能建档案，editor 不能归档，只有 manager 能归档。"""
    manager = _open_family(client, "role-manager", "role-family", "小雨")
    child_id = manager["children"][0]["id"]

    def _join(actor: str, role: str) -> None:
        token = client.post(
            f"{API}/families/current/invites",
            headers=_idempotent("role-manager", f"invite-{actor}"),
            json={"expires_in_hours": 24},
        ).json()["token"]
        request_id = client.post(
            f"{API}/family-requests",
            headers=_idempotent(actor, f"join-{actor}"),
            json={"token": token, "relationship_label": "家人"},
        ).json()["id"]
        approved = client.post(
            f"{API}/family-requests/{request_id}/approve",
            headers=_idempotent("role-manager", f"approve-{actor}"),
            json={"role": role},
        )
        assert approved.status_code == 200
        assert approved.json()["role"] == role

    _join("role-viewer", "viewer")
    _join("role-editor", "editor")

    assert (
        client.post(
            f"{API}/children",
            headers=_actor("role-viewer"),
            json={"name": "越权", "daily_budget_minutes": 15},
        ).status_code
        == 403
    )
    assert (
        client.post(f"{API}/children/{child_id}/archive", headers=_actor("role-viewer")).status_code
        == 403
    )

    # editor 可以建档案（属于日常记录工作），但不能改变全家可见范围。
    assert (
        client.post(
            f"{API}/children",
            headers=_actor("role-editor"),
            json={"name": "编辑建的", "daily_budget_minutes": 15},
        ).status_code
        == 201
    )
    editor_archive = client.post(
        f"{API}/children/{child_id}/archive", headers=_actor("role-editor")
    )
    assert editor_archive.status_code == 403
    assert "管理员" in editor_archive.json()["error"]["message"]
    # 被拒之后档案仍在用。
    still_active = [
        item["id"] for item in client.get(f"{API}/children", headers=_actor("role-manager")).json()
    ]
    assert child_id in still_active
    assert (
        client.post(
            f"{API}/children/{child_id}/archive", headers=_actor("role-manager")
        ).status_code
        == 200
    )


def test_archive_and_restore_are_recorded_in_the_family_audit_trail(
    client: TestClient, app
) -> None:
    """AC-004/安全：改变全家可见范围的操作必须留痕，谁归档的可以查。"""
    opened = _open_family(client, "audit-parent", "audit-family", "小雨")
    child_id = opened["children"][0]["id"]
    family_id = opened["family"]["id"]

    def _lifecycle(action: str) -> int:
        return client.post(
            f"{API}/children/{child_id}/{action}", headers=_actor("audit-parent")
        ).status_code

    assert _lifecycle("archive") == 200
    # 幂等重放不该重复留痕，否则审计日志会被网络重试灌水。
    assert _lifecycle("archive") == 200
    assert _lifecycle("restore") == 200

    session = app.state.database.session_factory()
    try:
        events = session.scalars(
            select(FamilyAuditEvent)
            .where(
                FamilyAuditEvent.family_id == family_id,
                FamilyAuditEvent.resource_type == "child",
            )
            .order_by(FamilyAuditEvent.created_at)
        ).all()
    finally:
        session.close()
    assert [event.action for event in events] == ["child.archived", "child.restored"]
    assert {event.resource_id for event in events} == {child_id}
    # 每条留痕都要指向真实操作人，不能是空账户。
    assert all(event.actor_binding_id for event in events)


def test_invite_preview_only_lists_profiles_in_use(client: TestClient) -> None:
    """归档档案不该出现在邀请预览里，否则受邀家人会看到已经退场的孩子。"""
    opened = _open_family(client, "preview-parent", "preview-family", "小雨")
    child_id = opened["children"][0]["id"]
    _create_child(client, _actor("preview-parent"), "小星")

    token = client.post(
        f"{API}/families/current/invites",
        headers=_idempotent("preview-parent", "preview-invite"),
        json={"expires_in_hours": 24},
    ).json()["token"]
    before = client.post(
        f"{API}/family-invites/preview", headers=_actor("outsider"), json={"token": token}
    )
    assert before.json()["child_names"] == ["小雨", "小星"]

    assert (
        client.post(
            f"{API}/children/{child_id}/archive", headers=_actor("preview-parent")
        ).status_code
        == 200
    )
    after = client.post(
        f"{API}/family-invites/preview", headers=_actor("outsider"), json={"token": token}
    )
    assert after.json()["child_names"] == ["小星"]
