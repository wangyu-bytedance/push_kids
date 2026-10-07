"""Queue migration adds projections without fabricating history or changing stable plans."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    Family,
    KnowledgeItem,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import local_date
from sqlalchemy import create_engine, inspect, select, text


def test_queue_upgrade_and_guarded_downgrade(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'fair-migration.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "apps/api/migrations")
    )
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "20261006_0016")
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(Family.__table__.insert().values(id="f", display_name="synthetic"))
        db.execute(Child.__table__.insert().values(id="c", family_id="f", name="synthetic"))
        db.execute(
            Subject.__table__.insert().values(id="s", family_id="f", child_id="c", name="math")
        )
        db.execute(
            KnowledgeItem.__table__.insert().values(
                id="k",
                family_id="f",
                child_id="c",
                subject_id="s",
                name="synthetic",
                normalized_name="synthetic",
            )
        )
        db.execute(
            ReviewItem.__table__.insert().values(
                id="r",
                family_id="f",
                child_id="c",
                knowledge_item_id="k",
                due_date=local_date().replace(year=2025),
                review_count=7,
                state_version=3,
            )
        )
        db.execute(
            DailyReviewPlan.__table__.insert().values(
                id="p",
                family_id="f",
                child_id="c",
                plan_date=local_date(),
                budget_minutes=30,
                policy_revision="daily-plan-v1",
            )
        )
    command.upgrade(config, "20261007_0017")
    with engine.connect() as db:
        row = db.execute(select(ReviewItem.__table__)).mappings().one()
        assert row["review_count"] == 7 and row["state_version"] == 3
        assert row["due_date"].year == 2025
        assert row["queue_eligible_on"] == local_date()
        assert row["last_offered_on"] is None
        assert db.scalar(text("SELECT policy_revision FROM daily_review_plans")) == "daily-plan-v1"
    with engine.begin() as db:
        db.execute(text("UPDATE review_items SET last_offered_on=:day"), {"day": local_date()})
    command.upgrade(config, "20261007_0018")
    with engine.connect() as db:
        projection = db.execute(text("SELECT * FROM review_queue_entries")).mappings().one()
        assert projection["review_item_id"] == "r" and projection["repeated"]
        assert projection["last_offered_on"] == local_date().isoformat()
        assert len(inspect(db).get_indexes("review_queue_entries")) == 5
    with engine.begin() as db:
        db.execute(text("UPDATE knowledge_items SET estimated_minutes=2"))
        assert db.scalar(text("SELECT minutes FROM review_queue_entries")) == 2
    command.downgrade(config, "20261007_0017")
    with engine.connect() as db:
        assert db.scalar(text("SELECT review_count FROM review_items")) == 7
        assert (
            db.scalar(text("SELECT last_offered_on FROM review_items")) == local_date().isoformat()
        )
    with engine.begin() as db:
        db.execute(text("UPDATE daily_review_plans SET policy_revision='daily-plan-fair-v2'"))
    with pytest.raises(RuntimeError, match="Retain fair-review"):
        command.downgrade(config, "20261006_0016")
    with engine.begin() as db:
        db.execute(text("UPDATE daily_review_plans SET policy_revision='daily-plan-v1'"))
    command.downgrade(config, "20261006_0016")
    assert "queue_eligible_on" not in {
        c["name"] for c in inspect(engine).get_columns("review_items")
    }
    with engine.connect() as db:
        assert db.scalar(text("SELECT review_count FROM review_items")) == 7
    engine.dispose()
