from pathlib import Path

import pytest
from alembic import command
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from sqlalchemy import create_engine, inspect, text

from tests.integration.test_notification_migration import _config, _seed


def assert_grade_schema(engine):
    columns = {column["name"]: column for column in inspect(engine).get_columns("children")}
    assert columns["grade_confirmed_school_year"]["nullable"] is True
    assert columns["grade_revision"]["nullable"] is False
    indexes = {i["name"]: i["column_names"] for i in inspect(engine).get_indexes("children")}
    assert indexes["ix_children_family_active_deleting_created_id"] == [
        "family_id",
        "active",
        "deleting",
        "created_at",
        "id",
    ]


@pytest.mark.parametrize("existing", [False, True])
def test_additive_migration_preserves_grade_and_refuses_confirmation_loss(
    tmp_path, monkeypatch, existing
):
    url = f"sqlite:///{tmp_path / 'grade-migration.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, "20261024_0024")
    if existing:
        _seed(url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    assert_grade_schema(engine)
    if existing:
        with engine.begin() as connection:
            row = connection.execute(
                text("SELECT grade,grade_confirmed_school_year,grade_revision FROM children")
            ).one()
            assert row[1:] == (None, 0)
            original = row[0]
            connection.execute(
                text("UPDATE children SET grade_confirmed_school_year=2026,grade_revision=1")
            )
        with pytest.raises(RuntimeError, match="Cannot discard shared grade"):
            command.downgrade(config, "20261024_0024")
        with engine.begin() as connection:
            assert connection.scalar(text("SELECT grade FROM children")) == original
            connection.execute(
                text("UPDATE children SET grade_confirmed_school_year=NULL,grade_revision=0")
            )
    command.downgrade(config, "20261024_0024")
    assert "grade_revision" not in {c["name"] for c in inspect(engine).get_columns("children")}
    command.upgrade(config, "head")
    assert_grade_schema(engine)
    engine.dispose()


def test_old_local_sqlite_upgrades_once_without_faking_parent_confirmation(
    tmp_path: Path, monkeypatch
):
    path = tmp_path / "local-old.db"
    url = f"sqlite:///{path}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    command.upgrade(_config(url), "20261024_0024")
    _seed(url)
    database = Database(Settings(PUSH_KIDS_DATABASE_URL=url))
    database.create_schema()
    assert_grade_schema(database.engine)
    with database.engine.begin() as connection:
        assert connection.execute(
            text("SELECT grade_confirmed_school_year,grade_revision FROM children")
        ).one() == (None, 0)
        connection.execute(
            text("UPDATE children SET grade_confirmed_school_year=2026,grade_revision=7")
        )
    database.create_schema()
    with database.engine.connect() as connection:
        assert connection.execute(
            text("SELECT grade_confirmed_school_year,grade_revision FROM children")
        ).one() == (2026, 7)
    database.engine.dispose()
