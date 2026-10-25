"""Real MySQL5.7 privilege boundary; only task-owned local databases and users."""

import json
import os
import secrets
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from push_kids.persistence import early_review_slots_v1
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from tools.verify_cloud_schema import main

pytestmark = pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_URL"), reason="isolated local MySQL5.7 not configured"
)


@pytest.fixture(scope="module")
def readiness_databases():
    base = make_url(os.environ["PUSH_KIDS_TEST_MYSQL_URL"])
    assert base.host in {"127.0.0.1", "localhost"}, "local disposable MySQL only"
    name = "schema_readiness_" + uuid4().hex[:12]
    username, password = "schema_app_" + uuid4().hex[:12], secrets.token_urlsafe(24)
    server = create_engine(base._replace(database=None), hide_parameters=True)
    admin_url = base.set(database=name).render_as_string(hide_password=False)
    crud_url = base.set(database=name, username=username, password=password).render_as_string(
        hide_password=False
    )
    admin = crud = None
    try:
        with server.begin() as db:
            assert str(db.scalar(text("SELECT VERSION()"))).startswith("5.7.")
            db.exec_driver_sql(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4")
            db.execute(
                text("CREATE USER :username IDENTIFIED BY :password"),
                {"username": username, "password": password},
            )
            db.execute(
                text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{name}`.* TO :username"),
                {"username": username},
            )
        config = Config()
        config.set_main_option(
            "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
        )
        with pytest.MonkeyPatch.context() as patch:
            patch.setenv("PUSH_KIDS_DATABASE_URL", admin_url)
            command.upgrade(config, "head")
        admin = Database(Settings(PUSH_KIDS_DATABASE_URL=admin_url))
        crud = Database(Settings(PUSH_KIDS_DATABASE_URL=crud_url))
        yield admin, crud, admin_url, crud_url
    finally:
        for database in (admin, crud):
            if database is not None:
                database.engine.dispose()
        with server.begin() as db:
            db.exec_driver_sql(f"DROP DATABASE IF EXISTS `{name}`")
            db.execute(text("DROP USER IF EXISTS :username"), {"username": username})
        server.dispose()


def test_runtime_uses_crud_visible_structure_without_ddl_privileges(readiness_databases):
    admin, crud, _, _ = readiness_databases
    admin.verify_cloud_schema(verify_triggers=True)
    with crud.engine.connect() as db:
        assert (
            db.scalar(
                text(
                    "SELECT COUNT(*) FROM information_schema.TRIGGERS "
                    "WHERE TRIGGER_SCHEMA=DATABASE()"
                )
            )
            == 0
        )
    queries = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        queries.append(statement)

    event.listen(crud.engine, "before_cursor_execute", capture)
    try:
        crud.verify_cloud_schema()
        crud.check_ready()
        assert not any("TRIGGERS" in query.upper() for query in queries)
    finally:
        event.remove(crud.engine, "before_cursor_execute", capture)
    with pytest.raises(RuntimeError, match="触发器不完整"):
        crud.verify_cloud_schema(verify_triggers=True)
    for ddl in (
        "CREATE TABLE forbidden_probe (id INT)",
        "ALTER TABLE children ADD COLUMN forbidden_probe INT",
        "CREATE TRIGGER forbidden_probe BEFORE INSERT ON children "
        "FOR EACH ROW SET NEW.grade_revision=0",
    ):
        with crud.engine.connect() as db, pytest.raises(DBAPIError) as error:
            db.exec_driver_sql(ddl)
        assert error.value.orig.args[0] == 1142


def test_runtime_still_rejects_wrong_revision(readiness_databases):
    admin, crud, _, _ = readiness_databases
    try:
        with admin.engine.begin() as db:
            db.execute(text("UPDATE alembic_version SET version_num='20261020_0022'"))
        with pytest.raises(RuntimeError, match="未迁移到当前版本"):
            crud.verify_cloud_schema()
    finally:
        with admin.engine.begin() as db:
            db.execute(text("UPDATE alembic_version SET version_num='20261024_0025'"))


@pytest.mark.parametrize("missing", ["table", "column", "index"])
def test_runtime_still_rejects_incomplete_structure(missing, readiness_databases):
    admin, crud, _, _ = readiness_databases
    statements = {
        "table": (
            "RENAME TABLE learning_suggestion_prompt_days TO readiness_saved_table",
            "RENAME TABLE readiness_saved_table TO learning_suggestion_prompt_days",
        ),
        "column": (
            "ALTER TABLE learning_suggestions CHANGE validated_content_json "
            "readiness_saved_column TEXT NOT NULL",
            "ALTER TABLE learning_suggestions CHANGE readiness_saved_column "
            "validated_content_json TEXT NOT NULL",
        ),
        "index": (
            "DROP INDEX ix_study_intent_recovery ON study_task_record_intents",
            "CREATE INDEX ix_study_intent_recovery "
            "ON study_task_record_intents (state,recovery_after,id)",
        ),
    }
    remove, restore = statements[missing]
    with admin.engine.begin() as db:
        db.exec_driver_sql(remove)
    try:
        with pytest.raises(RuntimeError, match="不完整"):
            crud.verify_cloud_schema()
    finally:
        with admin.engine.begin() as db:
            db.exec_driver_sql(restore)
    crud.verify_cloud_schema()


def test_release_gate_rejects_missing_trigger_and_keeps_output_safe(
    readiness_databases, monkeypatch, capsys
):
    admin, crud, admin_url, crud_url = readiness_databases
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", admin_url)
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PASS"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", crud_url)
    assert main() == 1
    assert json.loads(capsys.readouterr().out) == {
        "status": "FAIL",
        "error_category": "RuntimeError",
    }
    name, create = next(iter(early_review_slots_v1.trigger_statements("mysql")))
    with admin.engine.begin() as db:
        db.exec_driver_sql(f"DROP TRIGGER `{name}`")
    try:
        crud.verify_cloud_schema()
        with pytest.raises(RuntimeError, match="触发器不完整"):
            admin.verify_cloud_schema(verify_triggers=True)
        monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", admin_url)
        assert main() == 1
        assert json.loads(capsys.readouterr().out) == {
            "status": "FAIL",
            "error_category": "RuntimeError",
        }
    finally:
        with admin.engine.begin() as db:
            db.exec_driver_sql(create)
    admin.verify_cloud_schema(verify_triggers=True)
