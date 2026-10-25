"""Opt-in real MySQL5.7 gate; creates only task-owned disposable databases."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from time import monotonic, sleep
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.platform.config import Settings
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from tests.integration.test_learning_suggestions import (
    approve,
    suggestion_scope,  # noqa: F401 - shared domain fixture
)

MYSQL_URL = os.getenv("PUSH_KIDS_TODAY_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="task-owned MySQL5.7 not configured")


@pytest.fixture
def app(tmp_path, monkeypatch):
    base = make_url(MYSQL_URL)
    assert (base.database or "").startswith("today_learning_test"), "isolated test URL required"
    server = create_engine(base.set(database=None))
    name = "today_learning_test_" + uuid4().hex[:12]
    with server.begin() as db:
        assert str(db.scalar(text("SELECT VERSION()"))).startswith("5.7.")
        db.exec_driver_sql(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
    url = base.set(database=name).render_as_string(hide_password=False)
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "20261020_0022")
    engine = create_engine(url)
    try:
        with engine.begin() as db:
            db.execute(
                text("""INSERT INTO children
                (id,family_id,name,daily_budget_minutes,active,deleting,created_at)
                VALUES ('legacy-child','legacy-family','synthetic',15,1,0,UTC_TIMESTAMP())""")
            )
            db.execute(
                text("""INSERT INTO daily_review_plans
                (id,family_id,child_id,plan_date,budget_minutes,total_minutes,due_count,
                policy_revision,state,created_at,updated_at)
                VALUES ('legacy-plan','legacy-family','legacy-child','2026-10-24',15,0,0,
                'fair-v2','active',UTC_TIMESTAMP(),UTC_TIMESTAMP())""")
            )
        command.upgrade(config, "20261024_0024")
        with engine.connect() as db:
            assert (
                db.scalar(text("SELECT materialization_state FROM daily_review_plans"))
                == "legacy_fixed"
            )
            assert db.scalar(text("SELECT observed_since FROM knowledge_input_clocks")) is not None
            assert (
                db.scalar(
                    text(
                        "SELECT COUNT(*) FROM information_schema.TRIGGERS "
                        "WHERE TRIGGER_SCHEMA=DATABASE() AND TRIGGER_NAME LIKE 'ers_v1_%'"
                    )
                )
                == 9
            )
        command.downgrade(config, "20261020_0022")
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
    finally:
        engine.dispose()
        with server.begin() as db:
            db.exec_driver_sql(f"DROP DATABASE `{name}`")
        server.dispose()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


def test_mysql57_shared_prompt_and_approval_races(
    app,
    client,
    child,
    family_headers,
    suggestion_scope,  # noqa: F811 - imported pytest fixture
):
    root, _ = suggestion_scope
    gate = Barrier(2)

    def claim(index):
        gate.wait(timeout=10)
        return client.post(
            root + "/automatic-prompt",
            headers=family_headers,
            json={"request_id": f"race-parent-{index:03}"},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(claim, range(2)))
    assert all(r.status_code == 200 for r in responses)
    assert sum(r.json()["can_auto_open"] for r in responses) == 1
    # MySQL5.7 DATETIME rounds available_at to whole seconds. Match the
    # production worker's polling contract instead of requiring an immediate claim.
    deadline = monotonic() + 2
    while not app.state.suggestion_worker.process_one():
        assert monotonic() < deadline, "suggestion job was not claimed within two seconds"
        sleep(0.05)
    proposal = client.get(root + "/current", headers=family_headers).json()["proposal"]
    gate = Barrier(2)

    def accept(_index):
        gate.wait(timeout=10)
        return approve(client, root, family_headers, proposal)

    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = list(pool.map(accept, range(2)))
    assert tasks[0]["id"] == tasks[1]["id"]
    with app.state.database.engine.connect() as db:
        assert db.scalar(text("SELECT COUNT(*) FROM study_tasks")) == 1
        assert db.scalar(text("SELECT COUNT(*) FROM learning_records")) == 0
