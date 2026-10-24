from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_upgrade_projection_foreign_key_and_guarded_rollback(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'coverage.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "20261018_0021")
    command.upgrade(config, "20261020_0022")
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("PRAGMA foreign_keys=ON"))
        db.execute(
            text(
                "INSERT INTO children "
                "(id,family_id,name,daily_budget_minutes,active,deleting,created_at) VALUES "
                "('c','f','test',15,1,0,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO subjects "
                "(id,family_id,child_id,name,kind,color,active,is_custom,created_at) VALUES "
                "('s','f','c','math','learning','#000000',1,1,CURRENT_TIMESTAMP)"
            )
        )
        for kid in ("old", "new"):
            db.execute(
                text(
                    "INSERT INTO knowledge_items "
                    "(id,family_id,child_id,subject_id,name,normalized_name,category,review_method,estimated"
                    "_minutes,created_at) VALUES "
                    "(:id,'f','c','s',:id,:id,'skill','practice',3,CURRENT_TIMESTAMP)"
                ),
                {"id": kid},
            )
        db.execute(
            text(
                "INSERT INTO review_items "
                "(id,family_id,child_id,knowledge_item_id,step,due_date,review_count,interval_days,heat_"
                "milli,lapse_count,policy_revision,state_version,active,updated_at) VALUES "
                "('r','f','c','old',2,'2026-10-09',7,4,0,0,'curve_heat_v1',3,1,CURRENT_TIMESTAMP)"
            )
        )
        assert (
            db.scalar(text("SELECT available FROM review_queue_entries WHERE review_item_id='r'"))
            == 1
        )
        db.execute(
            text(
                "UPDATE knowledge_items SET review_status='superseded',"
                "superseded_by_knowledge_id='new' "
                "WHERE id='old'"
            )
        )
        assert (
            db.scalar(text("SELECT available FROM review_queue_entries WHERE review_item_id='r'"))
            == 0
        )
        db.execute(text("DELETE FROM knowledge_items WHERE id='new'"))
        assert tuple(
            db.execute(
                text("SELECT review_status,superseded_by_knowledge_id FROM knowledge_items")
            ).one()
        ) == ("superseded", None)
        assert tuple(
            db.execute(text("SELECT review_count,state_version,due_date FROM review_items")).one()
        ) == (7, 3, "2026-10-09")
    assert "knowledge_coverage_jobs" in inspect(engine).get_table_names()
    with pytest.raises(RuntimeError, match="Cannot discard permanent"):
        command.downgrade(config, "20261018_0021")
    with engine.begin() as db:
        db.execute(text("DELETE FROM review_items"))
        db.execute(text("DELETE FROM knowledge_items"))
    command.downgrade(config, "20261018_0021")
    assert "knowledge_coverage_jobs" not in inspect(engine).get_table_names()
    assert "review_status" not in {
        c["name"] for c in inspect(engine).get_columns("knowledge_items")
    }
    command.upgrade(config, "head")
    engine.dispose()
