from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260913_0012"
TARGET_REVISION = "20260913_0013"


def _config(url: str) -> Config:
    value = Config()
    value.set_main_option("script_location", str(ROOT / "apps" / "api" / "migrations"))
    value.set_main_option("path_separator", "os")
    value.set_main_option("sqlalchemy.url", url)
    return value


def test_unified_review_migration_backfills_projection_and_search_index(
    tmp_path, monkeypatch
) -> None:
    url = f"sqlite:///{tmp_path / 'unified-review.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    migration = _config(url)
    command.upgrade(migration, BASE_REVISION)
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO children "
                "(id, family_id, name, grade, daily_budget_minutes, created_at) "
                "VALUES ('child-a', 'family-a', '小雨', '小学二年级', 15, "
                "'2026-09-01 00:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO subjects "
                "(id, family_id, child_id, name, kind, color, active, created_at) "
                "VALUES ('subject-a', 'family-a', 'child-a', '数学', 'learning', "
                "'#000000', 1, '2026-09-01 00:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO knowledge_items "
                "(id, family_id, child_id, subject_id, name, normalized_name, category, "
                "review_method, estimated_minutes, created_at) VALUES "
                "('knowledge-a', 'family-a', 'child-a', 'subject-a', '两位数进位加法', "
                "'两位数进位加法', '计算', '变式练习', 3, '2026-09-01 00:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO review_items "
                "(id, family_id, child_id, knowledge_item_id, step, due_date, last_feedback, "
                "active, updated_at) VALUES ('review-a', 'family-a', 'child-a', 'knowledge-a', "
                "2, '2026-09-13', 'complete', 1, '2026-09-12 00:00:00')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO review_feedback "
                "(id, family_id, review_item_id, action, occurred_at) VALUES "
                "('feedback-a', 'family-a', 'review-a', 'complete', '2026-09-05 02:00:00'), "
                "('feedback-b', 'family-a', 'review-a', 'complete', '2026-09-12 02:00:00'), "
                "('feedback-c', 'family-a', 'review-a', 'defer', '2026-09-13 02:00:00')"
            )
        )
    engine.dispose()

    command.upgrade(migration, TARGET_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    assert {column["name"] for column in inspector.get_columns("review_items")} >= {
        "last_reviewed_on",
        "review_count",
        "interval_days",
        "heat_milli",
        "lapse_count",
        "policy_revision",
        "state_version",
    }
    assert {"knowledge_search_terms", "daily_review_plans", "daily_review_plan_items"} <= set(
        inspector.get_table_names()
    )
    assert {item["name"] for item in inspector.get_indexes("review_items")} >= {
        "ix_review_items_family_child_active_due_last_id"
    }
    assert {item["name"] for item in inspector.get_indexes("knowledge_search_terms")} >= {
        "ix_knowledge_search_terms_scope_term_item"
    }
    with engine.connect() as connection:
        projection = connection.execute(
            text(
                "SELECT review_count, last_reviewed_on, interval_days, policy_revision "
                "FROM review_items WHERE id = 'review-a'"
            )
        ).one()
        assert tuple(projection) == (2, "2026-09-12", 1, "fixed_v1")
        indexed = connection.execute(
            text(
                "SELECT COUNT(*), MAX(LENGTH(term)) FROM knowledge_search_terms "
                "WHERE knowledge_item_id = 'knowledge-a'"
            )
        ).one()
        assert 1 <= indexed[0] <= 32
        assert indexed[1] <= 40
        reviewed_dates = connection.execute(
            text("SELECT id, reviewed_on FROM review_feedback ORDER BY id")
        ).all()
        assert reviewed_dates == [
            ("feedback-a", "2026-09-05"),
            ("feedback-b", "2026-09-12"),
            ("feedback-c", None),
        ]
    engine.dispose()

    command.downgrade(migration, BASE_REVISION)
    engine = create_engine(url)
    inspector = inspect(engine)
    assert "knowledge_search_terms" not in inspector.get_table_names()
    assert "daily_review_plans" not in inspector.get_table_names()
    assert "last_reviewed_on" not in {
        column["name"] for column in inspector.get_columns("review_items")
    }
    engine.dispose()
