from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from push_kids.daily_tasks.schemas import DailyTaskCreate
from push_kids.daily_tasks.service import DailyTasksService
from push_kids.persistence.models import (
    ActivityRecord,
    CalendarEvent,
    Child,
    DailyTask,
    DailyTaskCompletion,
    FamilyMember,
    Subject,
)
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.errors import ConflictError
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import event, func, select, text


def _path(child):
    return f"/api/v1/children/{child['id']}/daily-tasks"


def _create(client, headers, child, name="阅读", minutes=20):
    response = client.post(
        _path(child), headers=headers, json={"name": name, "target_minutes": minutes}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_daily_task_crud_completion_snapshot_and_dashboard(client, app, family_headers, child):
    path = _path(child)
    assert client.get(path, headers=family_headers).json() == []
    task = _create(client, family_headers, child, " 阅读 ")
    jump = _create(client, family_headers, child, "跳绳", 10)
    assert task["name"] == "阅读"
    assert client.get(path, headers=family_headers).json()[0]["id"] == task["id"]
    endpoint = f"{path}/{task['id']}/today-completion"
    result = client.put(endpoint, headers=family_headers, json={"completed": True})
    assert result.status_code == 200
    assert result.json()["remaining_count"] == 1
    assert [item["id"] for item in result.json()["items"]] == [jump["id"], task["id"]]
    original_at = result.json()["items"][1]["occurred_at"]
    repeated = client.put(endpoint, headers=family_headers, json={"completed": True}).json()
    assert repeated["items"][1]["occurred_at"] == original_at
    assert (
        client.patch(
            f"{path}/{task['id']}",
            headers=family_headers,
            json={"name": "亲子阅读", "target_minutes": 30},
        ).status_code
        == 200
    )
    with app.state.database.session_factory() as db:
        completion = db.scalar(select(DailyTaskCompletion))
        assert completion.name_snapshot == "阅读"
        assert completion.minutes_snapshot == 20
        assert completion.occurred_at == completion.created_at
        assert db.scalar(select(func.count(DailyTaskCompletion.id))) == 1
    dashboard = client.get(
        f"/api/v1/children/{child['id']}/dashboard", headers=family_headers
    ).json()
    assert dashboard["daily_tasks"]["items"][1]["name"] == "亲子阅读"
    assert dashboard["daily_tasks"]["remaining_count"] == 1
    assert dashboard["todo_count"] == 0
    assert dashboard["daily_summary"]["record_count"] == 0
    assert dashboard["child"]["daily_budget_minutes"] == 15
    assert (
        client.put(endpoint, headers=family_headers, json={"completed": False}).json()[
            "remaining_count"
        ]
        == 2
    )
    client.put(endpoint, headers=family_headers, json={"completed": True})
    assert client.delete(f"{path}/{task['id']}", headers=family_headers).status_code == 204
    assert client.delete(f"{path}/{task['id']}", headers=family_headers).status_code == 204
    assert client.get(f"{path}/today", headers=family_headers).json()["total_count"] == 1
    assert client.put(endpoint, headers=family_headers, json={"completed": True}).status_code == 404
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(DailyTaskCompletion.id))) == 1


@pytest.mark.parametrize("minutes", [0, -1, 181, 1.5, "20", True, None])
def test_daily_task_rejects_invalid_minutes(client, family_headers, child, minutes):
    response = client.post(
        _path(child), headers=family_headers, json={"name": "阅读", "target_minutes": minutes}
    )
    assert response.status_code == 422
    assert client.get(_path(child), headers=family_headers).json() == []


def test_daily_task_name_patch_limit_and_duplicate(client, family_headers, child):
    path = _path(child)
    for name in ["", "   ", "字" * 31, 12, None]:
        assert (
            client.post(
                path, headers=family_headers, json={"name": name, "target_minutes": 20}
            ).status_code
            == 422
        )
    task = _create(client, family_headers, child, "字" * 30, 1)
    endpoint = f"{path}/{task['id']}"
    assert (
        client.patch(endpoint, headers=family_headers, json={"target_minutes": 180}).json()["name"]
        == "字" * 30
    )
    for body in [{"name": None}, {"target_minutes": None}, {"active": False}]:
        assert client.patch(endpoint, headers=family_headers, json=body).status_code == 422
    assert client.patch(endpoint, headers=family_headers, json={}).status_code == 200
    assert (
        client.post(
            path, headers=family_headers, json={"name": "字" * 30, "target_minutes": 20}
        ).status_code
        == 409
    )
    for index in range(19):
        _create(client, family_headers, child, f"任务{index}")
    assert (
        client.post(
            path, headers=family_headers, json={"name": "超过上限", "target_minutes": 20}
        ).status_code
        == 409
    )
    assert len(client.get(path, headers=family_headers).json()) == 20
    client.delete(endpoint, headers=family_headers)
    _create(client, family_headers, child, "字" * 30)


def test_shanghai_midnight_reset_and_no_past_debt(client, app, family_headers, child, monkeypatch):
    import push_kids.daily_tasks.service as module

    now = datetime(2026, 10, 12, 15, 59, 59, tzinfo=UTC)
    monkeypatch.setattr(module, "utcnow", lambda: now)
    monkeypatch.setattr(module, "local_date", lambda value=None: local_date(value or now))
    task = _create(client, family_headers, child)
    endpoint = f"{_path(child)}/{task['id']}/today-completion"
    assert (
        client.put(endpoint, headers=family_headers, json={"completed": True}).json()["day"]
        == "2026-10-12"
    )
    now += timedelta(seconds=1)
    today = client.get(f"{_path(child)}/today", headers=family_headers).json()
    assert today["day"] == "2026-10-13"
    assert today["remaining_count"] == 1
    assert today["items"][0]["occurred_at"] is None
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(DailyTaskCompletion.id))) == 1
        assert (
            DailyTasksService.today(
                db, family_headers["X-Family-ID"], child["id"], date(2026, 10, 12)
            )["remaining_count"]
            == 0
        )
    now += timedelta(days=5)
    assert client.get(f"{_path(child)}/today", headers=family_headers).json()["total_count"] == 1


def test_task_isolation_archiving_and_strict_completion(client, app, family_headers, child):
    task = _create(client, family_headers, child)
    path = _path(child)
    other_headers = {"X-Family-ID": "other-family"}
    other = client.post(
        "/api/v1/children", headers=other_headers, json={"name": "另一个孩子"}
    ).json()
    sibling = client.post("/api/v1/children", headers=family_headers, json={"name": "弟弟"}).json()
    for method, suffix, body in [
        ("GET", "", None),
        ("POST", "", {"name": "跳绳", "target_minutes": 10}),
        ("PATCH", f"/{task['id']}", {"name": "改名"}),
        ("DELETE", f"/{task['id']}", None),
        ("PUT", f"/{task['id']}/today-completion", {"completed": True}),
    ]:
        assert (
            client.request(method, path + suffix, headers=other_headers, json=body).status_code
            == 404
        )
    for wrong_child in [sibling, other]:
        assert (
            client.put(
                f"{_path(wrong_child)}/{task['id']}/today-completion",
                headers=family_headers,
                json={"completed": True},
            ).status_code
            == 404
        )
    for body in [
        {},
        {"completed": "true"},
        {"completed": 1},
        {"completed": None},
        {"completed": True, "day": "2026-01-01"},
    ]:
        assert (
            client.put(
                f"{path}/{task['id']}/today-completion", headers=family_headers, json=body
            ).status_code
            == 422
        )
    assert (
        client.post(f"/api/v1/children/{child['id']}/archive", headers=family_headers).status_code
        == 200
    )
    assert client.get(path, headers=family_headers).status_code == 200
    for method, suffix, body in [
        ("POST", "", {"name": "跳绳", "target_minutes": 10}),
        ("PATCH", f"/{task['id']}", {"name": "改名"}),
        ("DELETE", f"/{task['id']}", None),
        ("PUT", f"/{task['id']}/today-completion", {"completed": True}),
    ]:
        assert (
            client.request(method, path + suffix, headers=family_headers, json=body).status_code
            == 403
        )


def test_real_member_viewer_and_editor_permissions(client, app):
    from tests.integration.test_data_deletion import _actor, _child, _family

    _family(client, "task-manager")
    child = _child(client, "task-manager", "小朋友")
    manager = _actor("task-manager")
    invite = client.post(
        "/api/v1/families/current/invites",
        headers={**manager, "Idempotency-Key": "tasks-invite"},
        json={"expires_in_hours": 24},
    ).json()
    viewer = _actor("task-viewer")
    application = client.post(
        "/api/v1/family-requests",
        headers={**viewer, "Idempotency-Key": "tasks-join"},
        json={"token": invite["token"], "relationship_label": "家人"},
    ).json()
    member = client.post(
        f"/api/v1/family-requests/{application['id']}/approve",
        headers={**manager, "Idempotency-Key": "tasks-approve"},
        json={"role": "viewer"},
    ).json()
    task = _create(client, manager, child)
    path = _path(child)
    assert client.get(path, headers=viewer).status_code == 200
    assert client.get(f"{path}/today", headers=viewer).status_code == 200
    for method, suffix, body in [
        ("POST", "", {"name": "跳绳", "target_minutes": 10}),
        ("PATCH", f"/{task['id']}", {"name": "改名"}),
        ("DELETE", f"/{task['id']}", None),
        ("PUT", f"/{task['id']}/today-completion", {"completed": True}),
    ]:
        assert client.request(method, path + suffix, headers=viewer, json=body).status_code == 403
    with app.state.database.session_factory() as db:
        db.get(FamilyMember, member["id"]).role = "editor"
        db.commit()
    assert (
        client.put(
            f"{path}/{task['id']}/today-completion", headers=viewer, json={"completed": True}
        ).status_code
        == 200
    )


@pytest.mark.parametrize("target", ["child", "family"])
def test_daily_tasks_are_purged_by_real_deletion_worker(client, app, target):
    from tests.integration.test_data_deletion import _actor, _child, _family

    family = _family(client, "task-delete", "每日任务之家")
    child = _child(client, "task-delete", "小朋友")
    sibling = _child(client, "task-delete", "弟弟")
    headers = _actor("task-delete")
    task = _create(client, headers, child)
    _create(client, headers, sibling)
    client.put(
        f"{_path(child)}/{task['id']}/today-completion", headers=headers, json={"completed": True}
    )
    endpoint = (
        f"/api/v1/children/{child['id']}/deletion-requests"
        if target == "child"
        else "/api/v1/families/current/deletion-requests"
    )
    response = client.post(
        endpoint,
        headers={**headers, "Idempotency-Key": "tasks-delete"},
        json={"confirmation_name": "小朋友" if target == "child" else "每日任务之家"},
    )
    assert response.status_code == 202, response.text
    assert app.state.deletion_worker.process_one() is True
    assert (
        client.get(f"/api/v1/deletion-requests/{response.json()['id']}", headers=headers).json()[
            "state"
        ]
        == "succeeded"
    )
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(DailyTaskCompletion.id))) == 0
        assert db.scalar(select(func.count(DailyTask.id))) == (1 if target == "child" else 0)
        if target == "child":
            assert db.scalar(select(DailyTask.child_id)) == sibling["id"]
        assert family["family"]["id"]


def test_activity_fold_uses_recorded_facts_not_past_time(client, app, family_headers, child):
    with app.state.database.session_factory() as db:
        subject = Subject(
            family_id=family_headers["X-Family-ID"],
            child_id=child["id"],
            name="游泳",
            kind="activity",
        )
        db.add(subject)
        db.flush()
        subject_id = subject.id
        db.add(
            CalendarEvent(
                family_id=family_headers["X-Family-ID"],
                child_id=child["id"],
                name="游泳",
                event_date=local_date(),
                start_time=datetime.min.time(),
                end_time=datetime.min.time(),
                kind="activity",
            )
        )
        db.commit()
    endpoint = f"/api/v1/children/{child['id']}/dashboard"
    initial = client.get(endpoint, headers=family_headers).json()
    assert initial["activity_remaining_count"] == 1
    with app.state.database.session_factory() as db:
        db.add(
            ActivityRecord(
                family_id=family_headers["X-Family-ID"],
                child_id=child["id"],
                subject_id=subject_id,
                occurred_at=utcnow(),
                duration_minutes=10,
            )
        )
        db.commit()
    result = client.get(endpoint, headers=family_headers).json()
    assert result["activity_remaining_count"] == 0
    assert result["schedule_items"][0]["completed"] is True


@pytest.mark.parametrize("duplicate", [False, True])
def test_concurrent_admission_preserves_cap_and_name(tmp_path, duplicate):
    database = Database(
        Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=f"sqlite:///{tmp_path / 'tasks.db'}")
    )
    database.create_schema()
    family_id, child_id = str(uuid4()), str(uuid4())
    with database.session_factory() as db:
        db.add(Child(id=child_id, family_id=family_id, name="并发孩子"))
        db.commit()
        for index in range(19):
            DailyTasksService.create(
                db, family_id, child_id, DailyTaskCreate(name=f"任务{index}", target_minutes=20)
            )
    barrier = Barrier(2)

    def attempt(index):
        with database.session_factory() as db:
            db.scalar(select(func.count(DailyTask.id)))
            barrier.wait(timeout=5)
            try:
                task = DailyTasksService.create(
                    db,
                    family_id,
                    child_id,
                    DailyTaskCreate(
                        name="同名" if duplicate else f"并发{index}", target_minutes=20
                    ),
                )
                return task.id
            except ConflictError:
                return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sum(result is not None for result in results) == 1
    with database.session_factory() as db:
        assert len(DailyTasksService.list_tasks(db, family_id, child_id)) == 20
    database.engine.dispose()


@pytest.mark.parametrize("commands", [(True, True), (True, False), (False, True)])
def test_concurrent_completion_is_serialized_and_idempotent(tmp_path, commands):
    database = Database(
        Settings(
            PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=f"sqlite:///{tmp_path / 'complete.db'}"
        )
    )
    database.create_schema()
    family_id, child_id = str(uuid4()), str(uuid4())
    with database.session_factory() as db:
        db.add(Child(id=child_id, family_id=family_id, name="并发孩子"))
        db.commit()
        task_id = DailyTasksService.create(
            db, family_id, child_id, DailyTaskCreate(name="阅读", target_minutes=20)
        ).id
    barrier = Barrier(2)

    def attempt(completed):
        with database.session_factory() as db:
            db.scalar(select(func.count(DailyTaskCompletion.id)))
            barrier.wait(timeout=5)
            return DailyTasksService.complete(db, family_id, child_id, task_id, completed)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, commands))
    assert all(result["total_count"] == 1 for result in results)
    with database.session_factory() as db:
        count = db.scalar(select(func.count(DailyTaskCompletion.id)))
        assert count in (0, 1)
        assert DailyTasksService.today(db, family_id, child_id)["remaining_count"] == 1 - count
        if all(commands):
            assert count == 1
    database.engine.dispose()


def test_today_query_is_constant_and_indexed_with_large_history(client, app, family_headers, child):
    task = _create(client, family_headers, child)
    for index in range(19):
        _create(client, family_headers, child, f"任务{index}")
    with app.state.database.session_factory() as db:
        now = utcnow()
        db.execute(
            DailyTaskCompletion.__table__.insert(),
            [
                {
                    "id": str(uuid4()),
                    "family_id": family_headers["X-Family-ID"],
                    "child_id": child["id"],
                    "task_id": task["id"],
                    "day": local_date() - timedelta(days=index + 1),
                    "name_snapshot": "阅读",
                    "minutes_snapshot": 20,
                    "occurred_at": now,
                    "created_at": now,
                }
                for index in range(10_000)
            ],
        )
        db.commit()
    queries = []

    def capture(_conn, _cursor, statement, _params, *_args):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        response = client.get(f"{_path(child)}/today", headers=family_headers)
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert response.json()["remaining_count"] == 20
    assert len(queries) == 2
    assert len(response.content) <= 16 * 1024
    with engine.connect() as connection:
        plan = connection.execute(
            text(
                "EXPLAIN QUERY PLAN SELECT t.id, c.occurred_at FROM daily_tasks t "
                "LEFT JOIN daily_task_completions c ON c.family_id=t.family_id "
                "AND c.child_id=t.child_id AND c.task_id=t.id AND c.day=:day "
                "WHERE t.family_id=:family AND t.child_id=:child AND t.active=1 "
                "ORDER BY t.created_at,t.id LIMIT 20"
            ),
            {
                "day": str(local_date()),
                "family": family_headers["X-Family-ID"],
                "child": child["id"],
            },
        ).all()
    detail = " ".join(str(row) for row in plan)
    assert "ix_daily_tasks_scope_active_order" in detail
    assert (
        "uq_daily_task_completion_day" in detail
        or "sqlite_autoindex_daily_task_completions" in detail
    )
