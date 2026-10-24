"""Upgrade from production 0022, conservative legacy classification and safe rollback."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_additive_migrations_preserve_legacy_plans(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'today-learning.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "20261020_0022")
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(
            text("""INSERT INTO children
        (id,family_id,name,daily_budget_minutes,active,deleting,created_at)
        VALUES ('c','f','synthetic',15,1,0,CURRENT_TIMESTAMP)""")
        )
        db.execute(
            text("""INSERT INTO daily_review_plans
        (id,family_id,child_id,plan_date,budget_minutes,total_minutes,due_count,
        policy_revision,state,created_at,updated_at)
        VALUES ('legacy','f','c','2026-10-24',15,0,0,'fair-v2','active',
        CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""")
        )
    command.upgrade(config, "20261024_0024")
    with engine.connect() as db:
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "20261024_0024"
        assert (
            db.scalar(text("SELECT materialization_state FROM daily_review_plans"))
            == "legacy_fixed"
        )
        assert db.scalar(text("SELECT observed_since FROM knowledge_input_clocks")) is not None
        assert (
            db.scalar(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type='trigger' AND name LIKE 'ers_v1_%'"
                )
            )
            == 9
        )
    assert {"ix_suggestion_job_claim", "ix_suggestion_job_quota"} <= {
        row["name"] for row in inspect(engine).get_indexes("learning_suggestion_jobs")
    }
    command.downgrade(config, "20261020_0022")
    assert "review_early_slots" not in inspect(engine).get_table_names()
    command.upgrade(config, "20261024_0024")
    engine.dispose()
