from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from push_kids.persistence.models import Base
from push_kids.platform.config import Settings


class Database:
    expected_cloud_revision = "20260906_0005"

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

    def session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()
