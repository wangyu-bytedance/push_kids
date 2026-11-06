from alembic import command
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from sqlalchemy import create_engine, inspect, text

from tests.integration.test_notification_migration import _config, _seed


def old_database(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'workday.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, "20261024_0025")
    _seed(url)
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(
            text(
                "INSERT INTO subjects (id,family_id,child_id,name,kind,color,active,created_at) "
                "VALUES ('subject','family-1','child-1','课','activity',"
                "'#1F5B45',1,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO activity_schedules "
                "(id,family_id,child_id,subject_id,weekdays,active,created_at,updated_at) "
                "VALUES ('activity','family-1','child-1','subject','',1,"
                "CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
            )
        )
        db.execute(
            text(
                "INSERT INTO calendar_events "
                "(id,family_id,child_id,name,event_date,start_time,end_time,kind,repeat_weekly,"
                "active,created_at,updated_at) VALUES ('event','family-1','child-1','课',"
                "'2026-01-01','18:00','19:00','class',1,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
            )
        )
    engine.dispose()
    return url, config


def test_migration_preserves_legacy_and_blocks_loss_of_workday(tmp_path, monkeypatch):
    import pytest

    url, config = old_database(tmp_path, monkeypatch)
    command.upgrade(config, "head")
    engine = create_engine(url)
    with engine.begin() as db:
        for table in ["activity_schedules", "calendar_events"]:
            assert db.scalar(text(f"SELECT workday_only FROM {table}")) == 0
            column = next(c for c in inspect(db).get_columns(table) if c["name"] == "workday_only")
            assert column["nullable"] is False and str(column["default"]) == "0"
        assert db.scalar(text("SELECT repeat_weekly FROM calendar_events")) == 1
        db.execute(text("UPDATE calendar_events SET workday_only=1,repeat_weekly=0"))
    with pytest.raises(RuntimeError, match="Cannot discard workday"):
        command.downgrade(config, "20261024_0025")
    with engine.begin() as db:
        db.execute(text("UPDATE calendar_events SET workday_only=0"))
    command.downgrade(config, "20261024_0025")
    command.upgrade(config, "head")
    engine.dispose()


def test_old_local_sqlite_bootstraps_and_restarts_workday_rows(tmp_path, monkeypatch):
    url, _ = old_database(tmp_path, monkeypatch)
    database = Database(Settings(PUSH_KIDS_DATABASE_URL=url))
    database.create_schema()
    with database.engine.begin() as db:
        db.execute(
            text("UPDATE activity_schedules SET workday_only=1,start_time='18:00',end_time='19:00'")
        )
    # The old weekly-slot backfill must not treat this timed, empty-weekday row as flexible.
    database.create_schema()
    with database.engine.connect() as db:
        assert db.scalar(text("SELECT workday_only FROM activity_schedules")) == 1
        assert db.scalar(text("SELECT count(*) FROM activity_schedule_slots")) == 0
    database.engine.dispose()
