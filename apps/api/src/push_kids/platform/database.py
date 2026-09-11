from collections.abc import Generator
from datetime import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from push_kids.persistence.models import Base
from push_kids.platform.config import Settings


class Database:
    expected_cloud_revision = "20260911_0011"

    _local_read_indexes = {
        "ix_learning_submissions_family_child_state_created_id",
        "ix_learning_submissions_family_child_state_occurred_id",
        "ix_learning_records_family_child_occurred_submission",
        "ix_knowledge_items_family_child_created_id",
        "ix_knowledge_occurrences_family_occurred_knowledge",
        "ix_review_items_family_child_active_due_id",
        "ix_review_feedback_family_review_occurred",
        "ix_activity_records_family_child_occurred_id",
    }

    def __init__(self, settings: Settings) -> None:
        database_url = settings.resolved_database_url
        connect_args: dict[str, object] = (
            {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        engine_options: dict[str, object] = {}
        if database_url == "sqlite:///:memory:":
            engine_options["poolclass"] = StaticPool
        elif database_url.startswith("sqlite:///./"):
            Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        elif database_url.startswith("mysql"):
            connect_args.update({"connect_timeout": 10, "read_timeout": 15, "write_timeout": 15})
            engine_options.update(
                {"pool_pre_ping": True, "pool_recycle": 1200, "pool_size": 5, "max_overflow": 5}
            )
        self.engine = create_engine(database_url, connect_args=connect_args, **engine_options)
        if database_url.startswith("sqlite"):
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        self.session_factory = sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=Session
        )

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)
        self._upgrade_local_sqlite()

    def verify_cloud_schema(self) -> None:
        if self.engine.dialect.name != "mysql":
            raise RuntimeError("云环境数据库必须是 MySQL")
        with self.engine.connect() as connection:
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        if revision != self.expected_cloud_revision:
            raise RuntimeError("数据库 Schema 未迁移到当前版本")

    def check_ready(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def _upgrade_local_sqlite(self) -> None:
        """Apply the small pre-release SQLite evolution without hiding production migrations."""
        if self.engine.dialect.name != "sqlite":
            return
        columns = {item["name"] for item in inspect(self.engine).get_columns("activity_schedules")}
        statements = {
            "start_time": "ALTER TABLE activity_schedules ADD COLUMN start_time TIME",
            "end_time": "ALTER TABLE activity_schedules ADD COLUMN end_time TIME",
            "created_at": (
                "ALTER TABLE activity_schedules ADD COLUMN created_at DATETIME "
                "DEFAULT CURRENT_TIMESTAMP"
            ),
            "updated_at": (
                "ALTER TABLE activity_schedules ADD COLUMN updated_at DATETIME "
                "DEFAULT CURRENT_TIMESTAMP"
            ),
        }
        with self.engine.begin() as connection:
            for name, statement in statements.items():
                if name not in columns:
                    connection.execute(text(statement))
        subject_columns = {item["name"] for item in inspect(self.engine).get_columns("subjects")}
        if "active" not in subject_columns:
            with self.engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE subjects ADD COLUMN active BOOLEAN DEFAULT 1 NOT NULL")
                )
        child_columns = {item["name"] for item in inspect(self.engine).get_columns("children")}
        if "active" not in child_columns:
            # An existing local database predates archiving, so its children are all in use.
            with self.engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE children ADD COLUMN active BOOLEAN DEFAULT 1 NOT NULL")
                )
        if "deleting" not in child_columns:
            with self.engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE children ADD COLUMN deleting BOOLEAN DEFAULT 0 NOT NULL")
                )
        self._backfill_local_weekday_slots()
        for table in Base.metadata.tables.values():
            for index in table.indexes:
                if index.name in self._local_read_indexes:
                    index.create(bind=self.engine, checkfirst=True)

    @staticmethod
    def _legacy_days(raw: str | None, parent_id: str) -> list[int]:
        try:
            days = [int(value) for value in (raw or "").split(",") if value != ""]
        except ValueError as exc:
            raise RuntimeError(f"invalid legacy weekdays for parent {parent_id}") from exc
        if len(days) != len(set(days)) or any(day < 0 or day > 6 for day in days):
            raise RuntimeError(f"invalid legacy weekdays for parent {parent_id}")
        return sorted(days)

    @staticmethod
    def _legacy_range(start, end, parent_id: str) -> tuple[time, time]:
        try:
            start_value = start if isinstance(start, time) else time.fromisoformat(str(start))
            end_value = end if isinstance(end, time) else time.fromisoformat(str(end))
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"invalid legacy time range for parent {parent_id}") from exc
        if end_value <= start_value:
            raise RuntimeError(f"invalid legacy time range for parent {parent_id}")
        return start_value, end_value

    def _backfill_local_weekday_slots(self) -> None:
        with self.engine.begin() as connection:
            activity_rows = connection.execute(
                text(
                    "SELECT id, family_id, child_id, weekdays, start_time, end_time "
                    "FROM activity_schedules AS parent "
                    "WHERE NOT EXISTS (SELECT 1 FROM activity_schedule_slots AS slot "
                    "WHERE slot.schedule_id = parent.id)"
                )
            ).mappings()
            activity_values: list[dict[str, object]] = []
            for row in activity_rows:
                days = self._legacy_days(row["weekdays"], row["id"])
                if not days:
                    if row["start_time"] is not None or row["end_time"] is not None:
                        raise RuntimeError(f"invalid flexible activity parent {row['id']}")
                    continue
                start, end = self._legacy_range(row["start_time"], row["end_time"], row["id"])
                activity_values.extend(
                    {
                        "id": str(uuid4()),
                        "family_id": row["family_id"],
                        "child_id": row["child_id"],
                        "parent_id": row["id"],
                        "weekday": day,
                        "start_time": start.isoformat(),
                        "end_time": end.isoformat(),
                    }
                    for day in days
                )
            if activity_values:
                connection.execute(
                    text(
                        "INSERT INTO activity_schedule_slots "
                        "(id, family_id, child_id, schedule_id, weekday, start_time, end_time) "
                        "VALUES (:id, :family_id, :child_id, :parent_id, :weekday, "
                        ":start_time, :end_time)"
                    ),
                    activity_values,
                )

            travel_rows = connection.execute(
                text(
                    "SELECT id, family_id, child_id, weekdays, start_time, end_time "
                    "FROM travel_arrangements AS parent "
                    "WHERE NOT EXISTS (SELECT 1 FROM travel_arrangement_slots AS slot "
                    "WHERE slot.arrangement_id = parent.id)"
                )
            ).mappings()
            travel_values: list[dict[str, object]] = []
            for row in travel_rows:
                days = self._legacy_days(row["weekdays"], row["id"])
                if not days:
                    raise RuntimeError(f"invalid empty travel parent {row['id']}")
                start, end = self._legacy_range(row["start_time"], row["end_time"], row["id"])
                travel_values.extend(
                    {
                        "id": str(uuid4()),
                        "family_id": row["family_id"],
                        "child_id": row["child_id"],
                        "parent_id": row["id"],
                        "weekday": day,
                        "start_time": start.isoformat(),
                        "end_time": end.isoformat(),
                    }
                    for day in days
                )
            if travel_values:
                connection.execute(
                    text(
                        "INSERT INTO travel_arrangement_slots "
                        "(id, family_id, child_id, arrangement_id, weekday, start_time, end_time) "
                        "VALUES (:id, :family_id, :child_id, :parent_id, :weekday, "
                        ":start_time, :end_time)"
                    ),
                    travel_values,
                )

    def session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()
