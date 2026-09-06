"""The 20260906_0004 migration must let one submission hold several subject records."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260905_0003"
TARGET_REVISION = "20260906_0004"
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "multi_subject_migration",
    ROOT / "apps" / "api" / "migrations" / "versions" / "20260906_0004_multi_subject_records.py",
)
assert MIGRATION_SPEC is not None and MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
MIGRATION_SPEC.loader.exec_module(MIGRATION)


def _config(url: str) -> Config:
    # Built without the ini file on purpose: `fileConfig` would reset logging for later tests.
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def _seed(url: str) -> None:
    now = datetime(2026, 9, 1, 1, 0, tzinfo=UTC).replace(tzinfo=None)
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO children (id, family_id, name, daily_budget_minutes, created_at) "
                "VALUES ('child-1', 'family-1', '小雨', 15, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO subjects "
                "(id, family_id, child_id, name, kind, color, active, is_custom, created_at) "
                "VALUES ('subject-math', 'family-1', 'child-1', '数学', 'learning', "
                "'#39847A', 1, 0, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO learning_submissions "
                "(id, family_id, child_id, occurred_at, source, state, created_at, updated_at) "
                "VALUES ('submission-1', 'family-1', 'child-1', :now, 'photo', 'confirmed', "
                ":now, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO learning_records (id, family_id, child_id, subject_id, "
                "submission_id, occurred_at, summary, source, created_at) "
                "VALUES ('record-1', 'family-1', 'child-1', 'subject-math', 'submission-1', "
                ":now, '数学：两位数加法', '照片', :now)"
            ),
            {"now": now},
        )


def _insert_second_record(url: str) -> None:
    now = datetime(2026, 9, 1, 1, 0, tzinfo=UTC).replace(tzinfo=None)
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO subjects "
                "(id, family_id, child_id, name, kind, color, active, is_custom, created_at) "
                "VALUES ('subject-chinese', 'family-1', 'child-1', '语文', 'learning', "
                "'#39847A', 1, 0, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO learning_records (id, family_id, child_id, subject_id, "
                "submission_id, occurred_at, summary, source, created_at) "
                "VALUES ('record-2', 'family-1', 'child-1', 'subject-chinese', 'submission-1', "
                ":now, '语文：生字听写', '照片', :now)"
            ),
            {"now": now},
        )


def _submission_is_unique(engine) -> bool:
    """SQLite reports an inline ``UNIQUE`` column as a constraint, not as an index."""
    inspector = inspect(engine)
    unique_indexes = [
        item
        for item in inspector.get_indexes("learning_records")
        if item["unique"] and item["column_names"] == ["submission_id"]
    ]
    unique_constraints = [
        item
        for item in inspector.get_unique_constraints("learning_records")
        if item["column_names"] == ["submission_id"]
    ]
    return bool(unique_indexes or unique_constraints)


def test_multi_subject_migration_keeps_rows_and_guards_downgrade(tmp_path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'multi-subject.db'}"
    # `migrations/env.py` resolves the URL from settings, so the environment selects the target.
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    _seed(url)
    engine = create_engine(url)

    assert _submission_is_unique(engine), "the baseline pins one record per submission"

    command.upgrade(config, TARGET_REVISION)
    indexes = {
        item["name"]: item["unique"] for item in inspect(engine).get_indexes("learning_records")
    }
    assert indexes.get("ix_learning_records_submission_id") == 0
    assert not _submission_is_unique(engine), "no unique rule may survive on submission_id"
    # Existing history survives the table rebuild.
    with engine.begin() as connection:
        assert (
            connection.execute(
                text("SELECT summary FROM learning_records WHERE id = 'record-1'")
            ).scalar()
            == "数学：两位数加法"
        )
        assert connection.execute(text("SELECT COUNT(*) FROM learning_records")).scalar() == 1

    _insert_second_record(url)
    with engine.begin() as connection:
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM learning_records WHERE submission_id = 'submission-1'")
            ).scalar()
            == 2
        )

    with pytest.raises(RuntimeError, match="several subject records"):
        command.downgrade(config, BASE_REVISION)

    with engine.begin() as connection:
        connection.execute(text("DELETE FROM learning_records WHERE id = 'record-2'"))
    command.downgrade(config, BASE_REVISION)
    assert _submission_is_unique(engine), "downgrade restores the single-record rule"
    with engine.begin() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM learning_records")).scalar() == 1


def test_mysql_index_replacement_never_leaves_the_foreign_key_unindexed(monkeypatch) -> None:
    indexes = {MIGRATION.MYSQL_UNIQUE_NAME}
    operations: list[tuple[str, str]] = []

    monkeypatch.setattr(MIGRATION, "_has_index", lambda name: name in indexes)

    def create_index(name, *_args, **_kwargs):
        operations.append(("create", name))
        indexes.add(name)

    def drop_index(name, **_kwargs):
        operations.append(("drop", name))
        indexes.remove(name)

    monkeypatch.setattr(MIGRATION.op, "create_index", create_index)
    monkeypatch.setattr(MIGRATION.op, "drop_index", drop_index)

    MIGRATION._replace_mysql_unique_with_plain_index()
    assert operations == [
        ("create", MIGRATION.INDEX_NAME),
        ("drop", MIGRATION.MYSQL_UNIQUE_NAME),
    ]

    operations.clear()
    MIGRATION._restore_mysql_unique_index()
    assert operations == [
        ("create", MIGRATION.MYSQL_UNIQUE_NAME),
        ("drop", MIGRATION.INDEX_NAME),
    ]
