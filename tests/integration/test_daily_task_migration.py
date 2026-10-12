from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_daily_task_migration_additive_and_guarded_rollback(tmp_path: Path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "20261007_0018")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO children(id,family_id,name,daily_budget_minutes,active,deleting,"
                "created_at) VALUES('child','family','existing',15,1,0,CURRENT_TIMESTAMP)"
            )
        )
    command.upgrade(config, "head")
    inspector = inspect(engine)
    assert {"daily_tasks", "daily_task_completions"} <= set(inspector.get_table_names())
    assert {index["name"] for index in inspector.get_indexes("daily_tasks")} == {
        "ix_daily_tasks_scope_active_order"
    }
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM children WHERE name='existing'")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM daily_tasks")) == 0
        connection.execute(
            text(
                "INSERT INTO daily_tasks(id,family_id,child_id,name,target_minutes,active,"
                "created_at,updated_at) VALUES('task','family','child','read',20,1,"
                "CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
            )
        )
    with pytest.raises(RuntimeError, match="Cannot discard"):
        command.downgrade(config, "20261007_0018")
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM daily_tasks")) == 1
        connection.execute(text("DELETE FROM daily_tasks"))
    command.downgrade(config, "20261007_0018")
    assert "daily_tasks" not in inspect(engine).get_table_names()
    engine.dispose()
