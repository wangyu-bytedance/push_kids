"""FEAT-003 TP：`20260906_0006` 迁移必须是纯新增，并且可以回滚。

提醒能力上线时既有数据不能被改动，回滚时也只应丢掉提醒队列本身。
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260906_0005"
TARGET_REVISION = "20260906_0006"
NOTIFICATION_TABLES = {
    "notification_preferences",
    "notification_destinations",
    "notification_subscriptions",
    "notification_deliveries",
}


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
        connection.execute(
            text(
                "INSERT INTO families (id, display_name, status, created_at, updated_at) "
                "VALUES ('family-1', '小雨的家', 'active', :now, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO wechat_actor_bindings "
                "(id, app_id, subject_hmac, family_id, status, created_at, updated_at) "
                "VALUES ('binding-1', 'wx-test', 'hmac-1', 'family-1', 'active', :now, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO family_members (id, family_id, actor_binding_id, role, "
                "relationship_label, status, created_at, updated_at) "
                "VALUES ('member-1', 'family-1', 'binding-1', 'manager', '妈妈', 'active', "
                ":now, :now)"
            ),
            {"now": now},
        )
        connection.execute(
            text(
                "INSERT INTO children (id, family_id, name, daily_budget_minutes, created_at) "
                "VALUES ('child-1', 'family-1', '小雨', 15, :now)"
            ),
            {"now": now},
        )
    engine.dispose()


def test_notification_migration_is_additive_and_reversible(tmp_path: Path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'notifications.db'}"
    # `migrations/env.py` resolves the URL from settings, so the environment selects the target.
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    _seed(url)
    before = set(inspect(create_engine(url)).get_table_names())
    assert NOTIFICATION_TABLES & before == set()

    command.upgrade(config, TARGET_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    after = set(inspector.get_table_names())
    assert after >= NOTIFICATION_TABLES
    # 迁移只增表，既有数据与既有表结构都不能被触碰。
    assert before <= after
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM children")).scalar() == 1
        assert connection.execute(text("SELECT COUNT(*) FROM family_members")).scalar() == 1
    indexes = {item["name"] for item in inspector.get_indexes("notification_deliveries")}
    # 调度按 (state, available_at, scheduled_at) 取任务，缺这个索引会随历史增长退化为全表扫描。
    assert "ix_notification_deliveries_claim" in indexes
    delivery_columns = {
        item["name"]: item for item in inspector.get_columns("notification_deliveries")
    }
    assert delivery_columns["dedupe_key"]["nullable"] is False
    unique = {item["name"] for item in inspector.get_unique_constraints("notification_deliveries")}
    assert "uq_notification_delivery_dedupe" in unique
    # 接收标识只以密文列存在，不能出现任何以 openid 命名的可检索字段。
    destination_columns = {
        item["name"] for item in inspector.get_columns("notification_destinations")
    }
    assert "ciphertext" in destination_columns
    assert not any("openid" in name for name in destination_columns)
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    rolled_back = set(inspector.get_table_names())
    assert NOTIFICATION_TABLES & rolled_back == set()
    with engine.connect() as connection:
        # 回滚只丢提醒队列，家庭与孩子数据必须保留。
        assert connection.execute(text("SELECT COUNT(*) FROM children")).scalar() == 1
    engine.dispose()
