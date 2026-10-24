"""Real isolated MySQL5.7 migration, API races and 50k read-plan evidence."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.children import grade_confirmation
from push_kids.platform.config import Settings
from sqlalchemy import create_engine, text

from tests.integration.test_grade_confirmation import seed
from tests.integration.test_grade_confirmation_migration import assert_grade_schema
from tests.integration.test_notification_migration import _config, _seed
from tests.performance.test_grade_confirmation_reads import assert_bounded_grade_reads

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="isolated MySQL5.7 not configured")


@pytest.fixture
def mysql_app(tmp_path, monkeypatch):
    engine = create_engine(MYSQL_URL)
    assert engine.url.database.startswith("grade_"), "Task-owned isolated database required"
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT VERSION()")).startswith("5.7.")
    engine.dispose()
    monkeypatch.setattr(grade_confirmation, "local_date", lambda: date(2026, 10, 24))
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_ROOT=tmp_path,
            PUSH_KIDS_AI_PROVIDER="test",
            PUSH_KIDS_RUN_WORKER=False,
            PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
        )
    )
    with TestClient(app) as client:
        yield app, client


@pytest.mark.parametrize("same_grade", [True, False])
def test_mysql57_two_parents_confirm_one_fact_without_overwrite(mysql_app, same_grade):
    app, client = mysql_app
    family = "grade-race-" + uuid4().hex
    cid = seed(app, family=family)
    gate = Barrier(2)

    def run(index):
        gate.wait(timeout=10)
        return client.post(
            f"/api/v1/children/{cid}/grade-confirmation",
            headers={"X-Family-ID": family},
            json={
                "school_year": 2026,
                "expected_grade_revision": 0,
                "grade": "小学三年级" if same_grade or index == 0 else "小学四年级",
            },
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(run, range(2)))
    assert sorted(r.status_code for r in responses) == ([200, 200] if same_grade else [200, 409])
    if same_grade:
        assert {r.json()["outcome"] for r in responses} == {"confirmed", "already_confirmed"}
    with app.state.database.engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT grade,grade_revision,grade_confirmed_school_year "
                "FROM children WHERE family_id=:family AND id=:id"
            ),
            {"family": family, "id": cid},
        ).one()
        assert row[1:] == (1, 2026)
    assert (
        client.get("/api/v1/children/grade-confirmations", headers={"X-Family-ID": family}).json()[
            "items"
        ]
        == []
    )


def test_mysql57_50k_archived_plus_five_active_uses_tenant_index(mysql_app):
    app, _client = mysql_app
    assert_bounded_grade_reads(app.state.database.engine, app.state.database.session_factory)


@pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_MIGRATION_URL"),
    reason="isolated migration database not configured",
)
def test_mysql57_additive_migration_and_safe_downgrade(monkeypatch):
    url = os.environ["PUSH_KIDS_TEST_MYSQL_MIGRATION_URL"]
    engine = create_engine(url)
    assert engine.url.database.startswith("grade_"), "Task-owned isolated database required"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, "20261024_0024")
    _seed(url)
    with engine.connect() as connection:
        before = connection.scalar(text("SELECT grade FROM children"))
    command.upgrade(config, "head")
    assert_grade_schema(engine)
    with engine.begin() as connection:
        row = connection.execute(
            text("SELECT grade,grade_confirmed_school_year,grade_revision FROM children")
        ).one()
        assert tuple(row) == (before, None, 0)
        connection.execute(
            text("UPDATE children SET grade_confirmed_school_year=2026,grade_revision=1")
        )
    with pytest.raises(RuntimeError, match="Cannot discard shared grade"):
        command.downgrade(config, "20261024_0024")
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE children SET grade_confirmed_school_year=NULL,grade_revision=0")
        )
    command.downgrade(config, "20261024_0024")
    command.upgrade(config, "head")
    assert_grade_schema(engine)
    engine.dispose()
