"""FEAT-005 TP-010：`20260906_0004` 迁移必须让存量档案落为在用，并且可以回滚。"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from push_kids.children.service import ChildrenService
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260905_0003"
TARGET_REVISION = "20260906_0004"


def _config(url: str) -> Config:
    # Built without the ini file on purpose: `fileConfig` would reset logging for later tests.
    config = Config()
    config.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("sqlalchemy.url", url)
    return config


def _seed(url: str) -> None:
    now = datetime(2026, 9, 1, 1, 0, tzinfo=UTC).replace(tzinfo=None)
    engine = create_engine(url)
    with engine.begin() as connection:
        for child_id, name in (("child-1", "小雨"), ("child-2", "小星")):
            connection.execute(
                text(
                    "INSERT INTO children (id, family_id, name, daily_budget_minutes, created_at) "
                    "VALUES (:id, 'family-1', :name, 15, :now)"
                ),
                {"id": child_id, "name": name, "now": now},
            )
    engine.dispose()


def test_child_lifecycle_migration_defaults_to_active_and_downgrades(
    tmp_path: Path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'lifecycle.db'}"
    # `migrations/env.py` resolves the URL from settings, so the environment selects the target.
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    _seed(url)
    command.upgrade(config, TARGET_REVISION)

    engine = create_engine(url)
    with engine.connect() as connection:
        # 存量档案在迁移前不存在归档概念，升级后必须全部处于在用状态。
        assert dict(connection.execute(text("SELECT id, active FROM children")).all()) == {
            "child-1": 1,
            "child-2": 1,
        }
        # 旧写入路径不写 active 列，迁移后仍要能插入，否则新后端会拒绝旧客户端的写入。
        with engine.begin() as write:
            write.execute(
                text(
                    "INSERT INTO children (id, family_id, name, daily_budget_minutes, created_at) "
                    "VALUES ('child-3', 'family-1', '后来的', 15, :now)"
                ),
                {"now": datetime(2026, 9, 6, 1, 0)},
            )
        assert (
            connection.execute(text("SELECT active FROM children WHERE id = 'child-3'")).scalar()
            == 1
        )
        indexes = {row[1] for row in connection.execute(text("PRAGMA index_list(children)")).all()}
        assert "ix_children_active" in indexes
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    with engine.connect() as connection:
        columns = {row[1] for row in connection.execute(text("PRAGMA table_info(children)")).all()}
        # 回滚只丢归档信息，档案本体必须保留。
        assert connection.execute(text("SELECT COUNT(*) FROM children")).scalar() == 3
    engine.dispose()
    assert "active" not in columns


def test_cloud_schema_guard_tracks_the_current_head() -> None:
    """应用启动时的云 Schema 校验必须跟随最新 head，否则迁移完成后服务仍会拒绝启动。"""
    config = _config("sqlite:///:memory:")
    heads = ScriptDirectory.from_config(config).get_heads()
    assert heads == [Database.expected_cloud_revision]


def test_existing_local_sqlite_database_gains_the_lifecycle_column(
    tmp_path: Path, monkeypatch
) -> None:
    """本地开发库不跑 Alembic，缺列会让首页直接 500，所以启动时必须自愈。"""
    database_path = tmp_path / "local.db"
    url = f"sqlite:///{database_path}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    command.upgrade(_config(url), BASE_REVISION)
    _seed(url)

    settings = Settings(
        PUSH_KIDS_ENV="test",
        PUSH_KIDS_DATABASE_URL=url,
        PUSH_KIDS_MEDIA_ROOT=tmp_path / "uploads",
        PUSH_KIDS_AI_PROVIDER="test",
        PUSH_KIDS_RUN_WORKER=False,
    )
    database = Database(settings)
    database.create_schema()
    session = database.session_factory()
    try:
        names = sorted(child.name for child in ChildrenService.list_children(session, "family-1"))
    finally:
        session.close()
    # 存量档案自愈成在用状态，家长不会突然看不到自己的孩子。
    assert names == ["小星", "小雨"]
    database.engine.dispose()
