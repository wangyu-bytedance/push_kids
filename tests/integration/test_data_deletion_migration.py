from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260906_0006"
TARGET_REVISION = "20260906_0007"


def _config(url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_data_deletion_migration_upgrades_and_downgrades(tmp_path: Path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'deletion.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, TARGET_REVISION)

    engine = create_engine(url)
    inspector = inspect(engine)
    assert "deletion_requests" in inspector.get_table_names()
    assert "deleting" in {column["name"] for column in inspector.get_columns("children")}
    assert {
        "actor_binding_id",
        "target_type",
        "target_id",
        "state",
        "attempts",
        "expires_at",
    }.issubset({column["name"] for column in inspector.get_columns("deletion_requests")})
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    assert "deletion_requests" not in inspector.get_table_names()
    assert "deleting" not in {column["name"] for column in inspector.get_columns("children")}
    engine.dispose()
