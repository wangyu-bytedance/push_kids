from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260911_0011"
TARGET_REVISION = "20260913_0012"
TABLE = "review_feedback_batch_requests"


def config(url: str) -> Config:
    value = Config()
    value.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    value.set_main_option("path_separator", "os")
    value.set_main_option("sqlalchemy.url", url)
    return value


def test_batch_feedback_migration_is_additive_and_reversible(tmp_path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'batch-feedback.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    migration = config(url)
    command.upgrade(migration, BASE_REVISION)
    engine = create_engine(url)
    assert TABLE not in inspect(engine).get_table_names()
    engine.dispose()

    command.upgrade(migration, TARGET_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    assert TABLE in inspector.get_table_names()
    assert {item["name"] for item in inspector.get_unique_constraints(TABLE)} == {
        "uq_review_feedback_batch_key"
    }
    assert {item["name"] for item in inspector.get_indexes(TABLE)} >= {
        "ix_review_feedback_batch_requests_family_id",
        "ix_review_feedback_batch_requests_child_id",
    }
    engine.dispose()

    command.downgrade(migration, BASE_REVISION)
    engine = create_engine(url)
    assert TABLE not in inspect(engine).get_table_names()
    engine.dispose()
