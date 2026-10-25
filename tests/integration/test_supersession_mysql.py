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
from sqlalchemy import create_engine, event, inspect, text, update
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


def test_mysql_guarded_downgrade_and_reupgrade(monkeypatch):
    # Exercise the historical contract without current API/ORM-created grade facts.
    base_url = make_url(os.environ["PUSH_KIDS_TEST_MYSQL_URL"])
    name = "coverage_migration_" + uuid4().hex[:12]
    server = create_engine(base_url._replace(database=None))
    with server.begin() as db:
        db.exec_driver_sql(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
    url = base_url.set(database=name).render_as_string(hide_password=False)
    engine = create_engine(url)
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    try:
        command.upgrade(config, "20261020_0022")
        with engine.begin() as db:
            db.execute(
                text(
                    "INSERT INTO children "
                    "(id,family_id,name,daily_budget_minutes,active,deleting,created_at) VALUES "
                    "('c','f','test',15,1,0,CURRENT_TIMESTAMP)"
                )
            )
            db.execute(
                text(
                    "INSERT INTO subjects "
                    "(id,family_id,child_id,name,kind,color,active,is_custom,created_at) VALUES "
                    "('s','f','c','math','learning','#000000',1,1,CURRENT_TIMESTAMP)"
                )
            )
            for kid in ("old", "new"):
                db.execute(
                    text(
                        "INSERT INTO knowledge_items "
                        "(id,family_id,child_id,subject_id,name,normalized_name,category,"
                        "review_method,estimated_minutes,created_at) VALUES "
                        "(:id,'f','c','s',:id,:id,'skill','practice',3,CURRENT_TIMESTAMP)"
                    ),
                    {"id": kid},
                )
            db.execute(
                text(
                    "INSERT INTO review_items "
                    "(id,family_id,child_id,knowledge_item_id,step,due_date,review_count,"
                    "interval_days,heat_milli,lapse_count,policy_revision,state_version,"
                    "active,updated_at) VALUES "
                    "('r','f','c','old',2,'2026-10-09',7,4,0,0,'curve_heat_v1',3,1,"
                    "CURRENT_TIMESTAMP)"
                )
            )
            available = text("SELECT available FROM review_queue_entries WHERE review_item_id='r'")
            assert db.scalar(available) == 1
            db.execute(
                text(
                    "UPDATE knowledge_items SET review_status='superseded',"
                    "superseded_by_knowledge_id='new' WHERE id='old'"
                )
            )
            assert db.scalar(available) == 0
            facts = tuple(
                db.execute(
                    text(
                        "SELECT review_count,state_version,due_date FROM review_items WHERE id='r'"
                    )
                ).one()
            )
        with pytest.raises(RuntimeError, match="Cannot discard permanent supersession states"):
            command.downgrade(config, "20261018_0021")
        with engine.begin() as db:
            assert db.scalar(text("SELECT version_num FROM alembic_version")) == "20261020_0022"
            assert tuple(
                db.execute(
                    text(
                        "SELECT review_status,superseded_by_knowledge_id FROM knowledge_items "
                        "WHERE id='old'"
                    )
                ).one()
            ) == ("superseded", "new")
            assert db.scalar(available) == 0
            assert (
                tuple(
                    db.execute(
                        text(
                            "SELECT review_count,state_version,due_date FROM review_items "
                            "WHERE id='r'"
                        )
                    ).one()
                )
                == facts
            )
            db.execute(text("DELETE FROM review_items"))
            db.execute(text("DELETE FROM knowledge_items"))
        command.downgrade(config, "20261018_0021")
        assert "knowledge_coverage_jobs" not in inspect(engine).get_table_names()
        assert "review_status" not in {
            column["name"] for column in inspect(engine).get_columns("knowledge_items")
        }
        command.upgrade(config, "head")
        with engine.connect() as db:
            assert db.scalar(text("SELECT version_num FROM alembic_version")) == "20261024_0025"
            assert db.scalar(text("SELECT COUNT(*) FROM knowledge_items")) == 0
        assert "review_status" in {
            column["name"] for column in inspect(engine).get_columns("knowledge_items")
        }
        command.check(config)
    finally:
        engine.dispose()
        with server.begin() as db:
            db.exec_driver_sql(f"DROP DATABASE `{name}`")
        server.dispose()
