"""Opt-in MySQL test: stale RR snapshots must not bypass parent reservation capacity."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    Family,
    KnowledgeItem,
    ReviewItem,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.scheduling import schedule_review
from push_kids.planning.service import PlanningService
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.errors import ConflictError
from push_kids.platform.time import local_date
from sqlalchemy import delete, func, select, text

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="PUSH_KIDS_TEST_MYSQL_URL is not configured")


@pytest.mark.parametrize("materialized", [False, True])
def test_mysql_competing_reservations_with_preexisting_repeatable_read_snapshots(materialized):
    assert MYSQL_URL
    database = Database(Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=MYSQL_URL))
    database.verify_cloud_schema()
    family, cid, sid = (str(uuid4()) for _ in range(3))
    rids = [str(uuid4()) for _ in range(121)]
    tomorrow = local_date() + timedelta(days=1)
    try:
        with database.session_factory() as db:
            db.add(Family(id=family, display_name="isolated scheduling fixture"))
            db.flush()
            db.add(Child(id=cid, family_id=family, name="合成孩子", daily_budget_minutes=15))
            db.flush()
            db.add(
                Subject(id=sid, family_id=family, child_id=cid, name="合成数学", kind="learning")
            )
            db.flush()
            for index, rid in enumerate(rids):
                kid = str(uuid4())
                db.add(
                    KnowledgeItem(
                        id=kid,
                        family_id=family,
                        child_id=cid,
                        subject_id=sid,
                        name=f"合成{index}",
                        normalized_name=f"合成{index}",
                    )
                )
                db.flush()
                db.add(
                    ReviewItem(
                        id=rid,
                        family_id=family,
                        child_id=cid,
                        knowledge_item_id=kid,
                        due_date=tomorrow
                        if not materialized or index == 0
                        else tomorrow + timedelta(days=7),
                    )
                )
                db.flush()
                if index < 119 and not materialized:
                    db.add(
                        ReviewScheduleOverride(
                            review_item_id=rid,
                            family_id=family,
                            child_id=cid,
                            scheduled_on=tomorrow,
                            requested_on=local_date(),
                        )
                    )
            db.commit()
            if materialized:
                plan = PlanningService.daily_review_selection(db, family, cid, day=tomorrow)
                assert plan["planned_count"] == 1
        barrier = Barrier(2)

        def reserve(rid):
            with database.session_factory() as db:
                assert db.scalar(text("SELECT @@tx_isolation")) == "REPEATABLE-READ"
                assert db.scalar(
                    select(func.count())
                    .select_from(ReviewScheduleOverride)
                    .where(ReviewScheduleOverride.family_id == family)
                ) == (0 if materialized else 119)
                barrier.wait(timeout=10)
                try:
                    schedule_review(
                        db,
                        family,
                        cid,
                        rid,
                        action="tomorrow",
                        base_day=local_date(),
                        expected_version=0,
                        idempotency_key=str(uuid4()),
                    )
                    return "success"
                except ConflictError:
                    db.rollback()
                    return "capacity"

        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(reserve, rids[-2:])) == (
                ["success", "success"] if materialized else ["capacity", "success"]
            )
        with database.session_factory() as db:
            assert db.scalar(
                select(func.count())
                .select_from(ReviewScheduleOverride)
                .where(ReviewScheduleOverride.family_id == family)
            ) == (2 if materialized else 120)
            if materialized:
                plan = db.scalar(select(DailyReviewPlan).where(DailyReviewPlan.family_id == family))
                assert plan.total_minutes == 9
                assert plan.due_count == 3
    finally:
        with database.session_factory() as db:
            PlanningService.purge_data(db, family, cid)
            db.execute(delete(Subject).where(Subject.family_id == family))
            db.execute(delete(Child).where(Child.family_id == family))
            db.execute(delete(Family).where(Family.id == family))
            db.commit()
        database.engine.dispose()
