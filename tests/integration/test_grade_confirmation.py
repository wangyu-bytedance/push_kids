from datetime import date
from uuid import uuid4

import pytest
from push_kids.children import grade_confirmation
from push_kids.persistence.models import Child
from sqlalchemy import event, select, text

API = "/api/v1"


@pytest.fixture
def app(app):
    # A configured reminder channel must not run unrelated jobs on the shared in-memory DB.
    app.state.settings.run_notification_scheduler = False
    return app


@pytest.fixture
def grade_clock(monkeypatch):
    clock = [date(2026, 10, 24)]
    monkeypatch.setattr(grade_confirmation, "local_date", lambda: clock[0])
    return clock


def seed(app, *, family="family-test-a", grade="小学二年级", year=None, **extra):
    with app.state.database.session_factory() as db:
        child = Child(
            family_id=family,
            name="合成" + uuid4().hex[:8],
            grade=grade,
            grade_confirmed_school_year=year,
            **extra,
        )
        db.add(child)
        db.commit()
        return child.id


def pending(client, headers):
    response = client.get(f"{API}/children/grade-confirmations", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def confirm(client, headers, cid, *, grade="小学三年级", year=2026, revision=0):
    return client.post(
        f"{API}/children/{cid}/grade-confirmation",
        headers=headers,
        json={
            "school_year": year,
            "expected_grade_revision": revision,
            "grade": grade,
        },
    )


def test_initial_read_has_no_writes_and_confirmation_does_not_touch_learning(
    client, app, family_headers, grade_clock
):
    cid = seed(app)
    statements = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        statements.append(statement)

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        view = pending(client, family_headers)
        assert view["items"][0]["suggested_grade"] == "小学二年级"
        assert view["items"][0]["reason"] == "initial_check"
        writes = [
            sql
            for sql in statements
            if sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
        ]
        assert not writes, writes
        statements.clear()
        result = confirm(client, family_headers, cid, grade="二年级")
        assert result.status_code == 200, result.text
        assert result.json()["child"]["grade_confirmed_school_year"] == 2026
        assert result.json()["child"]["grade_revision"] == 1
        assert all(
            "UPDATE children" in sql
            or not sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for sql in statements
        )
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert pending(client, family_headers)["items"] == []


def test_new_profiles_manual_save_and_august_semantics(client, app, family_headers, grade_clock):
    grade_clock[0] = date(2026, 8, 30)
    created = client.post(
        f"{API}/children", headers=family_headers, json={"name": "新建孩子", "grade": "一年级"}
    ).json()
    assert created["grade"] == "小学一年级"
    assert created["grade_confirmed_school_year"] == 2025
    assert pending(client, family_headers)["items"] == []
    grade_clock[0] = date(2026, 9, 1)
    assert pending(client, family_headers)["items"][0]["suggested_grade"] == "小学二年级"
    kept = confirm(client, family_headers, created["id"], grade="一年级", revision=1)
    assert kept.status_code == 200
    assert kept.json()["child"]["grade"] == "小学一年级"
    grade_clock[0] = date(2027, 1, 1)
    assert pending(client, family_headers)["items"] == []


def test_shared_once_retry_conflict_and_independent_children(
    client, app, family_headers, grade_clock
):
    first, second = seed(app), seed(app, grade="学前-中班")
    assert len(pending(client, family_headers)["items"]) == 2
    saved = confirm(client, family_headers, first)
    assert saved.status_code == 200
    assert confirm(client, family_headers, first).json()["outcome"] == "already_confirmed"
    rejected = confirm(client, family_headers, first, grade="小学四年级")
    assert rejected.status_code == 409
    assert rejected.json()["error"]["code"] == "grade_confirmation_conflict"
    assert [item["id"] for item in pending(client, family_headers)["items"]] == [second]
    grade_clock[0] = date(2027, 9, 1)
    old = confirm(client, family_headers, first, year=2026, revision=1)
    assert old.status_code == 409
    assert old.json()["error"]["code"] == "grade_school_year_changed"
    assert (
        next(i for i in pending(client, family_headers)["items"] if i["id"] == first)[
            "suggested_grade"
        ]
        == "小学四年级"
    )


def test_only_explicit_grade_edits_confirm_and_stale_edits_never_overwrite(
    client, app, family_headers, grade_clock
):
    cid = seed(app)
    url = f"{API}/children/{cid}"
    for payload in [{"name": "改名字"}, {"daily_budget_minutes": 20}, {"grade": "小学二年级"}]:
        response = client.patch(url, headers=family_headers, json=payload)
        assert response.status_code == 200
        assert response.json()["grade_confirmed_school_year"] is None
        assert response.json()["grade_revision"] == 0
    assert (
        client.patch(url, headers=family_headers, json={"grade": "小学三年级"}).json()["error"][
            "code"
        ]
        == "client_upgrade_required"
    )
    assert (
        client.patch(
            url, headers=family_headers, json={"grade": "二年级", "confirm_grade": True}
        ).status_code
        == 422
    )
    saved = client.patch(
        url,
        headers=family_headers,
        json={
            "grade": "二年级",
            "confirm_grade": True,
            "expected_grade_revision": 0,
        },
    )
    assert saved.status_code == 200
    assert saved.json()["grade_revision"] == 1
    assert pending(client, family_headers)["items"] == []
    stale = client.patch(
        url,
        headers=family_headers,
        json={
            "name": "不能一起保存",
            "grade": "四年级",
            "confirm_grade": True,
            "expected_grade_revision": 0,
        },
    )
    assert stale.status_code == 409
    with app.state.database.session_factory() as db:
        child = db.get(Child, cid)
        assert child.name == "改名字" and child.grade == "小学二年级"
    for version, grade in [(1, None), (2, "国际学校"), (3, "学前-小班")]:
        response = client.patch(
            url,
            headers=family_headers,
            json={
                "grade": grade,
                "confirm_grade": True,
                "expected_grade_revision": version,
            },
        )
        assert response.status_code == 200
        assert response.json()["grade_confirmed_school_year"] == (2026 if version == 3 else None)


def test_restore_accumulates_and_unknown_terminal_deleting_are_excluded(
    client, app, family_headers, grade_clock
):
    cid = seed(app, grade="小学一年级", year=2024, active=False)
    seed(app, grade="其他")
    seed(app, grade="初中三年级", year=2024)
    seed(app, grade="小学二年级", deleting=True)
    seed(app, family="another-family", grade="小学二年级")
    assert pending(client, family_headers)["items"] == []
    assert confirm(client, family_headers, cid).status_code == 409
    assert client.post(f"{API}/children/{cid}/restore", headers=family_headers).status_code == 200
    item = pending(client, family_headers)["items"][0]
    assert item["suggested_grade"] == "小学三年级"
    assert confirm(client, {"X-Family-ID": "another-family"}, cid).status_code == 404
    for grade in ["其他", "学前", "", "高一"]:
        assert confirm(client, family_headers, cid, grade=grade).status_code == 422


def test_too_many_active_profiles_and_future_metadata_fail_closed(
    client, app, family_headers, grade_clock
):
    cid = seed(app, year=2027)
    assert (
        client.get(f"{API}/children/grade-confirmations", headers=family_headers).status_code == 409
    )
    assert confirm(client, family_headers, cid).status_code == 409
    for _ in range(5):
        seed(app)
    assert (
        client.get(f"{API}/children/grade-confirmations", headers=family_headers).status_code == 409
    )


def test_conditional_update_rejects_stale_snapshot(client, app, grade_clock):
    from push_kids.children.grade_confirmation import (
        GradeConfirmationConflict,
        GradeConfirmationService,
    )

    cid = seed(app)
    with (
        app.state.database.session_factory() as first,
        app.state.database.session_factory() as second,
    ):
        a = first.get(Child, cid)
        b = second.get(Child, cid)
        GradeConfirmationService.save_manual_grade(second, b, "三年级", 0)
        second.commit()
        with pytest.raises(GradeConfirmationConflict):
            GradeConfirmationService.save_manual_grade(first, a, "四年级", 0)
        first.rollback()
    with app.state.database.session_factory() as db:
        assert db.get(Child, cid).grade == "小学三年级"


def test_actual_manager_editor_viewer_share_server_state(client, app, grade_clock):
    from tests.integration.test_multi_child_profiles import _actor, _idempotent, _open_family

    family = _open_family(client, "grade-manager", "grade-family", "合成孩子")
    cid = family["children"][0]["id"]
    for actor, role in [("grade-editor", "editor"), ("grade-viewer", "viewer")]:
        invite = client.post(
            f"{API}/families/current/invites", headers=_idempotent("grade-manager", actor), json={}
        ).json()
        request = client.post(
            f"{API}/family-requests",
            headers=_idempotent(actor, actor + "-join"),
            json={"token": invite["token"], "relationship_label": "家长"},
        )
        assert request.status_code == 201, request.text
        approved = client.post(
            f"{API}/family-requests/{request.json()['id']}/approve",
            headers=_idempotent("grade-manager", actor + "-approve"),
            json={"role": role},
        )
        assert approved.status_code == 200, approved.text
    with app.state.database.session_factory() as db:
        child = db.scalar(select(Child).where(Child.id == cid))
        child.grade = "小学二年级"
        db.commit()
    assert pending(client, _actor("grade-viewer")) == {
        "school_year": 2026,
        "can_confirm": False,
        "items": [],
    }
    assert confirm(client, _actor("grade-viewer"), cid).status_code == 403
    assert confirm(client, _actor("grade-editor"), cid).status_code == 200
    assert pending(client, _actor("grade-manager"))["items"] == []


def test_failed_commit_rolls_back_all_grade_fields(client, app, grade_clock):
    from push_kids.children.grade_confirmation import GradeConfirmationService
    from push_kids.children.schemas import GradeConfirmation

    cid = seed(app)
    with app.state.database.session_factory() as db:

        def fail(_session):
            raise RuntimeError("synthetic transaction failure")

        event.listen(db, "before_commit", fail)
        with pytest.raises(RuntimeError, match="synthetic transaction failure"):
            GradeConfirmationService.confirm(
                db,
                "family-test-a",
                cid,
                GradeConfirmation(school_year=2026, expected_grade_revision=0, grade="三年级"),
            )
        event.remove(db, "before_commit", fail)
        db.rollback()
    with app.state.database.session_factory() as db:
        row = db.execute(
            text(
                "SELECT grade,grade_revision,grade_confirmed_school_year FROM children WHERE id=:id"
            ),
            {"id": cid},
        ).one()
        assert tuple(row) == ("小学二年级", 0, None)
