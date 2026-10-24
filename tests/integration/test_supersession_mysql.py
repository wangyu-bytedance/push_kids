"""Real MySQL5.7 gate against an explicitly configured disposable test database."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.persistence.models import KnowledgeItem, ReviewItem
from push_kids.platform.config import Settings
from sqlalchemy import create_engine, event, update
from sqlalchemy.engine import make_url

from tests.integration.test_knowledge_supersession import (
    apply,
)
from tests.integration.test_knowledge_supersession import (
    test_background_inventory_restart_retry_and_scope as background_case,
)
from tests.integration.test_knowledge_supersession import (
    test_completed_history_and_existing_parent_reservation_survive_once as manual_case,
)
from tests.integration.test_knowledge_supersession import (
    test_confirmation_uses_only_unchanged_server_proposal as confirm_case,
)
from tests.integration.test_knowledge_supersession import (
    test_current_future_plan_no_refill_history_and_terminal_state as state_case,
)
from tests.integration.test_knowledge_supersession import (
    test_delete_only_selected_target_and_keep_permanent_status as delete_case,
)
from tests.integration.test_review_inventory import path, seed

pytestmark = pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_URL"), reason="isolated MySQL5.7 not configured"
)


@pytest.fixture
def app(tmp_path, monkeypatch):
    base_url = make_url(os.environ["PUSH_KIDS_TEST_MYSQL_URL"])
    name = "coverage_case_" + uuid4().hex[:12]
    server = create_engine(base_url.set(database=None))
    with server.begin() as db:
        db.exec_driver_sql(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
    url = base_url.set(database=name).render_as_string(hide_password=False)
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")
    application = create_app(
        Settings(
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_DATABASE_URL=url,
            PUSH_KIDS_MEDIA_ROOT=tmp_path,
            PUSH_KIDS_AI_PROVIDER="test",
            PUSH_KIDS_RUN_WORKER=False,
            PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
        )
    )

    yield application
    application.state.database.engine.dispose()
    with server.begin() as db:
        db.exec_driver_sql(f"DROP DATABASE `{name}`")
    server.dispose()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def family_headers():
    return {"X-Family-ID": "coverage-mysql-" + uuid4().hex}


def test_real_mysql_version(app):
    from sqlalchemy import text

    with app.state.database.engine.connect() as db:
        assert str(db.scalar(text("SELECT VERSION()"))).startswith("5.7.")


@pytest.mark.parametrize("case", [state_case, delete_case, manual_case, background_case])
def test_mysql_permanent_status_and_planning(case, client, app, family_headers, child):
    case(client, app, family_headers, child)


@pytest.mark.parametrize("change", ["none", "edited", "injected", "old_changed", "manual"])
def test_mysql_confirmation_snapshot(change, client, app, family_headers, child):
    confirm_case(client, app, family_headers, child, change)


def test_overlapping_covering_writes_only_one_transition(client, app, family_headers, child):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=3)
    barrier = Barrier(2)

    def run(target):
        barrier.wait(timeout=10)
        return apply(app, family, cid, ids[0][1], target)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, [ids[1][1], ids[2][1]]))
    assert sorted(results) == [False, True]
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, ids[0][1]).superseded_by_knowledge_id in {ids[1][1], ids[2][1]}
        assert db.get(ReviewItem, ids[0][0]).state_version == 1


def test_mysql_status_inventory_actual_queries_are_bounded_and_indexed(
    client, app, family_headers, child
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=200)
    with app.state.database.session_factory() as db:
        db.execute(
            update(KnowledgeItem)
            .where(
                KnowledgeItem.family_id == family,
                KnowledgeItem.child_id == cid,
                KnowledgeItem.id.in_([kid for _, kid in ids[:100]]),
            )
            .values(review_status="superseded", superseded_by_knowledge_id=ids[-1][1])
        )
        db.commit()
    engine, captured = app.state.database.engine, []

    def capture(_conn, _cursor, statement, params, _context, _many):
        captured.append((statement, params))

    event.listen(engine, "before_cursor_execute", capture)
    try:
        for status in ("normal", "superseded"):
            captured.clear()
            response = client.get(
                path(child),
                headers=family_headers,
                params={"view": "count", "review_status": status, "limit": 50},
            )
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["total"] == 100 and len(data["items"]) == 50
            assert len(response.content) <= 96 * 1024
            assert len(captured) <= 13
            assert all(sql.lstrip().startswith("SELECT") for sql, _ in captured)
            assert all("OVER (" not in sql.upper() for sql, _ in captured)
            with engine.connect() as connection:
                plans = [
                    dict(row)
                    for sql, params in list(captured)
                    for row in connection.exec_driver_sql("EXPLAIN " + sql, params).mappings()
                ]
            knowledge_plans = [
                row for row in plans if str(row["table"]).startswith("knowledge_items")
            ]
            # MySQL may choose an existing tenant-leading covering index instead of
            # the status index at this distribution; require an indexed access path.
            assert knowledge_plans
            assert all(
                row["key"] and row["type"] not in {"ALL", "index"} for row in knowledge_plans
            ), [(row["table"], row["key"], row["type"], row["rows"]) for row in knowledge_plans]
            if status == "superseded":
                assert all(item["superseded_by_name"] == "知识199" for item in data["items"])
    finally:
        event.remove(engine, "before_cursor_execute", capture)


def test_mysql_guarded_downgrade_and_reupgrade(client, app, family_headers, child):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=2)
    assert apply(app, family, cid, ids[0][1], ids[1][1])
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option(
        "sqlalchemy.url",
        app.state.database.engine.url.render_as_string(hide_password=False).replace("%", "%%"),
    )
    with pytest.raises(RuntimeError, match="Cannot discard permanent supersession states"):
        command.downgrade(config, "20261018_0021")
    for _, kid in ids:
        assert (
            client.delete(
                f"/api/v1/children/{cid}/knowledge/{kid}", headers=family_headers
            ).status_code
            == 204
        )
    command.downgrade(config, "20261018_0021")
    command.upgrade(config, "head")
    response = client.get(path(child), headers=family_headers, params={"view": "count"})
    assert response.status_code == 200 and response.json()["total"] == 0
