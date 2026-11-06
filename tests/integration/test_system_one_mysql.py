"""Spec05 gates against explicitly configured disposable MySQL5.7 databases."""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from tests.integration.test_supersession_mysql import app as mysql_app
from tests.integration.test_system_one_confirmation import (
    test_new_coverage_records_observed_before_supersession_and_skips_stale as confirmation_case,
)

pytestmark = pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_URL"), reason="isolated MySQL5.7 not configured"
)


@pytest.fixture
def app(tmp_path, monkeypatch):
    yield from mysql_app.__wrapped__(tmp_path, monkeypatch)


@pytest.mark.parametrize("stale,same_day", [(False, False), (True, False), (False, True)])
def test_mysql_system_one_confirmation(app, child, family_headers, stale, same_day):
    confirmation_case(app, child, family_headers, stale, same_day)


def test_mysql_recent_index_upgrade_downgrade(app, monkeypatch):
    from pathlib import Path

    engine = app.state.database.engine
    url = engine.url.render_as_string(hide_password=False)
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.downgrade(config, "20261105_0026")
    assert "ix_knowledge_recent_subject" not in {
        item["name"] for item in inspect(engine).get_indexes("knowledge_items")
    }
    command.upgrade(config, "20261105_0027")
    indexes = {
        item["name"]: item["column_names"]
        for item in inspect(engine).get_indexes("knowledge_items")
    }
    assert indexes["ix_knowledge_recent_subject"] == [
        "family_id",
        "child_id",
        "subject_id",
        "review_status",
        "created_at",
        "id",
    ]
