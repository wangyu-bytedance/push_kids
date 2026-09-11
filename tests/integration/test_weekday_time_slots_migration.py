from __future__ import annotations

from datetime import UTC, datetime, time
from pathlib import Path

from alembic import command
from alembic.config import Config
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from sqlalchemy import MetaData, create_engine, inspect, select

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260907_0009"
TARGET_REVISION = "20260911_0010"


def _config(url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_weekday_slot_migration_backfills_uniform_parents_and_downgrades(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'weekday-slots.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    engine = create_engine(url)
    metadata = MetaData()
    metadata.reflect(engine)
    now = datetime.now(UTC)
    with engine.begin() as connection:
        connection.execute(
            metadata.tables["children"].insert(),
            {
                "id": "child-1",
                "family_id": "family-1",
                "name": "小雨",
                "grade": "二年级",
                "daily_budget_minutes": 15,
                "active": True,
                "deleting": False,
                "created_at": now,
            },
        )
        connection.execute(
            metadata.tables["subjects"].insert(),
            {
                "id": "subject-1",
                "family_id": "family-1",
                "child_id": "child-1",
                "name": "英语",
                "kind": "activity",
                "color": "#39847A",
                "active": True,
                "is_custom": True,
                "created_at": now,
            },
        )
        connection.execute(
            metadata.tables["activity_schedules"].insert(),
            {
                "id": "activity-1",
                "family_id": "family-1",
                "child_id": "child-1",
                "subject_id": "subject-1",
                "weekdays": "1,2",
                "time_text": None,
                "start_time": time(18),
                "end_time": time(19),
                "target_per_week": None,
                "note": None,
                "active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
        connection.execute(
            metadata.tables["travel_arrangements"].insert(),
            {
                "id": "travel-1",
                "family_id": "family-1",
                "child_id": "child-1",
                "name": "上学",
                "weekdays": "0,1,2,3,4",
                "start_time": time(7, 30),
                "end_time": time(8, 10),
                "active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
    engine.dispose()

    command.upgrade(config, TARGET_REVISION)
    engine = create_engine(url)
    metadata = MetaData()
    metadata.reflect(engine)
    inspector = inspect(engine)
    assert "activity_schedule_slots" in inspector.get_table_names()
    assert "travel_arrangement_slots" in inspector.get_table_names()
    with engine.connect() as connection:
        activity_slots = (
            connection.execute(
                select(metadata.tables["activity_schedule_slots"]).order_by(
                    metadata.tables["activity_schedule_slots"].c.weekday
                )
            )
            .mappings()
            .all()
        )
        travel_slots = (
            connection.execute(select(metadata.tables["travel_arrangement_slots"])).mappings().all()
        )
    assert [row["weekday"] for row in activity_slots] == [1, 2]
    assert {(row["start_time"], row["end_time"]) for row in activity_slots} == {
        (time(18), time(19))
    }
    assert len(travel_slots) == 5
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    assert "activity_schedule_slots" not in inspector.get_table_names()
    assert "travel_arrangement_slots" not in inspector.get_table_names()
    engine.dispose()


def test_local_schema_upgrade_backfills_existing_activity_slots(tmp_path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'local-weekday-slots.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    command.upgrade(_config(url), BASE_REVISION)
    engine = create_engine(url)
    metadata = MetaData()
    metadata.reflect(engine)
    now = datetime.now(UTC)
    with engine.begin() as connection:
        connection.execute(
            metadata.tables["children"].insert(),
            {
                "id": "local-child",
                "family_id": "local-family",
                "name": "小雨",
                "grade": "二年级",
                "daily_budget_minutes": 15,
                "active": True,
                "deleting": False,
                "created_at": now,
            },
        )
        connection.execute(
            metadata.tables["subjects"].insert(),
            {
                "id": "local-subject",
                "family_id": "local-family",
                "child_id": "local-child",
                "name": "英语",
                "kind": "activity",
                "color": "#39847A",
                "active": True,
                "is_custom": True,
                "created_at": now,
            },
        )
        connection.execute(
            metadata.tables["activity_schedules"].insert(),
            {
                "id": "local-activity",
                "family_id": "local-family",
                "child_id": "local-child",
                "subject_id": "local-subject",
                "weekdays": "1,2",
                "time_text": None,
                "start_time": time(18),
                "end_time": time(19),
                "target_per_week": None,
                "note": None,
                "active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
    engine.dispose()

    database = Database(
        Settings(
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_DATABASE_URL=url,
            PUSH_KIDS_MEDIA_ROOT=tmp_path / "uploads",
            PUSH_KIDS_AI_PROVIDER="test",
            PUSH_KIDS_RUN_WORKER=False,
        )
    )
    database.create_schema()
    database.create_schema()
    metadata = MetaData()
    metadata.reflect(database.engine)
    with database.engine.connect() as connection:
        rows = (
            connection.execute(
                select(metadata.tables["activity_schedule_slots"]).order_by(
                    metadata.tables["activity_schedule_slots"].c.weekday
                )
            )
            .mappings()
            .all()
        )
    assert [row["weekday"] for row in rows] == [1, 2]
    database.engine.dispose()
