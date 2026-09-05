"""The 20260905_0003 field migration must backfill provenance, order and subject origin."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = "20260905_0002"
TARGET_REVISION = "20260905_0003"


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
                "INSERT INTO children (id, family_id, name, daily_budget_minutes, created_at) "
                "VALUES ('child-1', 'family-1', '小雨', 15, :now)"
            ),
            {"now": now},
        )
        for subject_id, name, kind, owner in (
            ("subject-math", "数学", "learning", "child-1"),
            ("subject-chinese", "语文", "learning", "child-1"),
            ("subject-science", "科学", "learning", "child-1"),
            ("subject-swim", "游泳", "activity", "child-1"),
            # A preset name under a different kind stays parent-built.
            ("subject-math-club", "数学", "activity", "child-2"),
        ):
            connection.execute(
                text(
                    "INSERT INTO subjects "
                    "(id, family_id, child_id, name, kind, color, active, created_at) "
                    "VALUES (:id, 'family-1', :owner, :name, :kind, '#39847A', 1, :now)"
                ),
                {"id": subject_id, "owner": owner, "name": name, "kind": kind, "now": now},
            )
        for index, (submission_id, occurred) in enumerate(
            (
                ("submission-old", datetime(2026, 8, 20, 2)),
                ("submission-new", datetime(2026, 8, 28, 2)),
            )
        ):
            connection.execute(
                text(
                    "INSERT INTO learning_submissions "
                    "(id, family_id, child_id, occurred_at, source, state, created_at, updated_at) "
                    "VALUES (:id, 'family-1', 'child-1', :occurred, 'photo', 'confirmed', "
                    ":now, :now)"
                ),
                {"id": submission_id, "occurred": occurred, "now": now},
            )
            connection.execute(
                text(
                    "INSERT INTO learning_records "
                    "(id, family_id, child_id, subject_id, submission_id, occurred_at, summary, "
                    "source, created_at) VALUES (:id, 'family-1', 'child-1', 'subject-math', "
                    ":submission_id, :occurred, '进位加法', '课内', :now)"
                ),
                {
                    "id": f"record-{index}",
                    "submission_id": submission_id,
                    "occurred": occurred,
                    "now": now,
                },
            )
            for media_index in range(2):
                connection.execute(
                    text(
                        "INSERT INTO submission_media "
                        "(id, submission_id, path, content_type, byte_size, created_at) "
                        "VALUES (:id, :submission_id, :path, 'image/png', 100, :created_at)"
                    ),
                    {
                        "id": f"media-{index}-{media_index}",
                        "submission_id": submission_id,
                        "path": f"page-{index}-{media_index}.png",
                        "created_at": datetime(2026, 8, 28, 3, media_index),
                    },
                )
        connection.execute(
            text(
                "INSERT INTO knowledge_items (id, family_id, child_id, subject_id, name, "
                "normalized_name, category, review_method, estimated_minutes, created_at) "
                "VALUES ('knowledge-1', 'family-1', 'child-1', 'subject-math', '进位加法', "
                "'进位加法', '知识点', '口头回顾', 3, :now)"
            ),
            {"now": now},
        )
        # The later occurrence is inserted first so ordering, not insertion, picks the source.
        for occurrence_id, record_id, occurred in (
            ("occurrence-new", "record-1", datetime(2026, 8, 28, 2)),
            ("occurrence-old", "record-0", datetime(2026, 8, 20, 2)),
        ):
            connection.execute(
                text(
                    "INSERT INTO knowledge_occurrences (id, family_id, knowledge_item_id, "
                    "learning_record_id, occurred_at, created_at) "
                    "VALUES (:id, 'family-1', 'knowledge-1', :record_id, :occurred, :now)"
                ),
                {"id": occurrence_id, "record_id": record_id, "occurred": occurred, "now": now},
            )
        connection.execute(
            text(
                "INSERT INTO review_items (id, family_id, child_id, knowledge_item_id, step, "
                "due_date, active, updated_at) "
                "VALUES ('review-1', 'family-1', 'child-1', 'knowledge-1', 0, :due, 1, :now)"
            ),
            {"due": date(2026, 9, 5), "now": now},
        )
    engine.dispose()


def test_field_migration_backfills_and_downgrades(tmp_path: Path, monkeypatch) -> None:
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    # `migrations/env.py` resolves the URL from settings, so the environment selects the target.
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, BASE_REVISION)
    _seed(url)
    command.upgrade(config, TARGET_REVISION)

    engine = create_engine(url)
    with engine.connect() as connection:
        assert (
            connection.execute(
                text("SELECT source_submission_id FROM review_items WHERE id = 'review-1'")
            ).scalar()
            == "submission-old"
        )
        media = connection.execute(
            text(
                "SELECT submission_id, sort_order FROM submission_media "
                "ORDER BY submission_id, sort_order"
            )
        ).all()
        assert media == [
            ("submission-new", 0),
            ("submission-new", 1),
            ("submission-old", 0),
            ("submission-old", 1),
        ]
        assert dict(connection.execute(text("SELECT id, is_custom FROM subjects")).all()) == {
            "subject-math": 0,
            "subject-chinese": 0,
            "subject-science": 1,
            "subject-swim": 1,
            "subject-math-club": 1,
        }
        # Recognition evidence cannot be recovered for confirmations made before this revision.
        assert connection.execute(
            text("SELECT confidence, evidence_json FROM knowledge_items")
        ).all() == [(None, None)]
    engine.dispose()

    command.downgrade(config, BASE_REVISION)
    engine = create_engine(url)
    with engine.connect() as connection:
        columns = {
            table: {row[1] for row in connection.execute(text(f"PRAGMA table_info({table})")).all()}
            for table in ("review_items", "submission_media", "knowledge_items", "subjects")
        }
        assert connection.execute(text("SELECT COUNT(*) FROM review_items")).scalar() == 1
    engine.dispose()
    assert "source_submission_id" not in columns["review_items"]
    assert "sort_order" not in columns["submission_media"]
    assert not {"confidence", "evidence_json"} & columns["knowledge_items"]
    assert "is_custom" not in columns["subjects"]
