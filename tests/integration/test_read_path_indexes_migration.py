from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260911_0010"
TARGET_REVISION = "20260911_0011"
EXPECTED = {
    "learning_submissions": {
        "ix_learning_submissions_family_child_state_created_id",
        "ix_learning_submissions_family_child_state_occurred_id",
    },
    "learning_records": {"ix_learning_records_family_child_occurred_submission"},
    "knowledge_items": {"ix_knowledge_items_family_child_created_id"},
    "knowledge_occurrences": {"ix_knowledge_occurrences_family_occurred_knowledge"},
    "review_items": {"ix_review_items_family_child_active_due_id"},
    "review_feedback": {"ix_review_feedback_family_review_occurred"},
    "activity_records": {"ix_activity_records_family_child_occurred_id"},
}


def _config(url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def _index_names(url: str, table: str) -> set[str]:
    engine = create_engine(url)
    try:
        return {str(item["name"]) for item in inspect(engine).get_indexes(table)}
    finally:
        engine.dispose()


def test_read_path_index_migration_upgrades_and_downgrades(tmp_path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'read-indexes.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    for table, expected in EXPECTED.items():
        assert _index_names(url, table).isdisjoint(expected)

    command.upgrade(config, TARGET_REVISION)
    for table, expected in EXPECTED.items():
        assert expected <= _index_names(url, table)

    engine = create_engine(url)
    try:
        indexes = {
            item["name"]: item["column_names"]
            for item in inspect(engine).get_indexes("learning_records")
        }
    finally:
        engine.dispose()
    assert indexes["ix_learning_records_family_child_occurred_submission"] == [
        "family_id",
        "child_id",
        "occurred_at",
        "submission_id",
        "id",
    ]

    command.downgrade(config, BASE_REVISION)
    for table, expected in EXPECTED.items():
        assert _index_names(url, table).isdisjoint(expected)
