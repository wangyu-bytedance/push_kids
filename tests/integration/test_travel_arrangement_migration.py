from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260906_0005"
TARGET_REVISION = "20260906_0006"


def _config(url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_travel_migration_upgrades_and_downgrades(tmp_path: Path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'travel.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, TARGET_REVISION)

    engine = create_engine(url)
    inspector = inspect(engine)
    assert "travel_arrangements" in inspector.get_table_names()
    assert "travel_arrangement_requests" in inspector.get_table_names()
    assert {column["name"] for column in inspector.get_columns("travel_arrangements")} >= {
        "family_id",
        "child_id",
        "name",
        "weekdays",
        "start_time",
        "end_time",
        "active",
    }
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    assert "travel_arrangements" not in inspect(engine).get_table_names()
    assert "travel_arrangement_requests" not in inspect(engine).get_table_names()
    engine.dispose()
