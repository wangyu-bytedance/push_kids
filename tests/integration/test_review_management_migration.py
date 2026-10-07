from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_review_management_upgrade_preserves_dates_and_guarded_downgrade(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'review-management.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "20261006_0015")
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(
            text(
                "INSERT INTO children (id,family_id,name,grade,daily_budget_minutes,"
                "active,deleting,created_at) VALUES ('c','f','test',NULL,15,1,0,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO subjects (id,family_id,child_id,name,kind,color,active,"
                "is_custom,created_at) VALUES "
                "('s','f','c','math','learning','#000000',1,1,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO knowledge_items (id,family_id,child_id,subject_id,name,"
                "normalized_name,category,review_method,estimated_minutes,created_at) "
                "VALUES ('k','f','c','s','one','one','knowledge','read',3,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO review_items (id,family_id,child_id,knowledge_item_id,step,"
                "due_date,review_count,interval_days,heat_milli,lapse_count,policy_revision,"
                "state_version,active,updated_at) VALUES "
                "('r','f','c','k',2,'2026-10-09',7,4,0,0,'curve_heat_v1',3,1,CURRENT_TIMESTAMP)"
            )
        )
    command.upgrade(config, "20261006_0016")
    assert "review_schedule_overrides" in inspect(engine).get_table_names()
    assert "ix_review_scope_count_knowledge" in {
        i["name"] for i in inspect(engine).get_indexes("review_items")
    }
    with engine.begin() as db:
        assert tuple(
            db.execute(text("SELECT due_date,review_count,state_version FROM review_items")).one()
        ) == ("2026-10-09", 7, 3)
        assert db.scalar(text("SELECT review_inventory_revision FROM children")) == 0
        db.execute(
            text(
                "INSERT INTO review_schedule_overrides (review_item_id,family_id,child_id,"
                "scheduled_on,requested_on,created_at,updated_at) VALUES "
                "('r','f','c','2026-10-09','2026-10-06',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
            )
        )
    with pytest.raises(RuntimeError, match="Cannot discard"):
        command.downgrade(config, "20261006_0015")
    with engine.begin() as db:
        db.execute(text("DELETE FROM review_schedule_overrides"))
    command.downgrade(config, "20261006_0015")
    assert "review_schedule_overrides" not in inspect(engine).get_table_names()
    with engine.connect() as db:
        assert db.scalar(text("SELECT review_count FROM review_items")) == 7
    engine.dispose()
