"""Fairness through real services; opt-in runs use the isolated MySQL 5.7 database."""

import os
from datetime import timedelta
from uuid import uuid4

import pytest
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    DailyReviewPlanItem,
    Family,
    KnowledgeItem,
    ReviewFeedback,
    ReviewItem,
    ReviewQueueEntry,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.inventory import inventory_page, preview_reviews
from push_kids.planning.plan_candidates import load_candidates
from push_kids.planning.selection import select_daily_reviews
from push_kids.planning.service import PlanningService
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.time import local_date
from sqlalchemy import delete, func, insert, select, update


@pytest.fixture(params=["sqlite", "mysql"])
def scope(request):
    url = (
        "sqlite:///:memory:" if request.param == "sqlite" else os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
    )
    if not url:
        pytest.skip("isolated MySQL URL not configured")
    database = Database(Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=url))
    if request.param == "sqlite":
        database.create_schema()
    else:
        database.verify_cloud_schema()
    family, cid = str(uuid4()), str(uuid4())
    with database.session_factory() as db:
        db.add(Family(id=family, display_name="synthetic"))
        db.flush()
        db.add(Child(id=cid, family_id=family, name="synthetic", daily_budget_minutes=30))
        db.commit()
    yield database, family, cid
    with database.session_factory() as db:
        for model in (
            DailyReviewPlanItem,
            DailyReviewPlan,
            ReviewFeedback,
            ReviewScheduleOverride,
            ReviewQueueEntry,
            ReviewItem,
            KnowledgeItem,
            Subject,
            Child,
        ):
            db.execute(delete(model).where(model.family_id == family))
        db.execute(delete(Family).where(Family.id == family))
        db.commit()
    database.engine.dispose()


def seed(db, family, cid, counts=(140, 3, 3), *, prefix="subject"):
    ids = []
    for n, count in enumerate(counts):
        sid = str(uuid4())
        db.add(Subject(id=sid, family_id=family, child_id=cid, name=f"{prefix}-{n}"))
        db.flush()
        keys = [str(uuid4()) for _ in range(count)]
        db.execute(
            insert(KnowledgeItem),
            [
                dict(
                    id=k,
                    family_id=family,
                    child_id=cid,
                    subject_id=sid,
                    name=f"synthetic-{i}",
                    normalized_name=f"synthetic-{i}",
                    estimated_minutes=3,
                )
                for i, k in enumerate(keys)
            ],
        )
        db.execute(
            insert(ReviewItem),
            [
                dict(
                    id=k,
                    family_id=family,
                    child_id=cid,
                    knowledge_item_id=k,
                    due_date=local_date() - timedelta(days=10 - n),
                    queue_eligible_on=local_date() - timedelta(days=10 - n),
                    review_count=i % 2,
                )
                for i, k in enumerate(keys)
            ],
        )
        ids.extend(keys)
    db.commit()
    return ids


def test_real_candidates_cover_subjects_beyond_global_120_and_are_stable(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        ids = seed(db, family, cid)
        candidates = load_candidates(db, family, cid, local_date())
        assert len(candidates) <= 1268
        for budget in (1, 5, 30, 120):
            bounded = load_candidates(db, family, cid, local_date(), candidate_budget=budget)
            assert select_daily_reviews(bounded, budget_minutes=budget) == select_daily_reviews(
                candidates, budget_minutes=budget
            )
        first = PlanningService.daily_review_selection(db, family, cid)
        assert len(first["sessions"]) == 3
        assert first["planned_minutes"] == 30
        assert first["coverage_limited"] is False
        chosen = {r["review_id"] for r in first["all_items"]}
        for _ in range(3):
            assert PlanningService.daily_review_selection(db, family, cid) == first
        assert (
            db.scalar(
                select(func.count())
                .select_from(DailyReviewPlan)
                .where(DailyReviewPlan.family_id == family)
            )
            == 1
        )
        assert db.scalar(
            select(func.count())
            .select_from(ReviewItem)
            .where(ReviewItem.family_id == family, ReviewItem.last_offered_on == local_date())
        ) == len(chosen)
        assert all(db.get(ReviewItem, rid).last_offered_on is None for rid in set(ids) - chosen)
        assert (
            db.scalar(
                select(func.count())
                .select_from(ReviewFeedback)
                .where(ReviewFeedback.family_id == family)
            )
            == 0
        )


def test_readonly_preview_and_inventory_do_not_advance_queue(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        seed(db, family, cid, (8, 4, 4))
        child = db.get(Child, cid)
        tomorrow = preview_reviews(db, family, child, 1)
        after = preview_reviews(db, family, child, 2)
        assert set(tomorrow).isdisjoint(after)
        result = inventory_page(db, family, cid, view="count")
        assert all(r["arrangement_state"] == "awaiting_daily_plan" for r in result["items"])
        assert all(r["missed_plan_days"] == 0 for r in result["items"])
        assert (
            db.scalar(
                select(func.count())
                .select_from(DailyReviewPlan)
                .where(DailyReviewPlan.family_id == family)
            )
            == 0
        )
        plan = PlanningService.daily_review_selection(
            db, family, cid, day=local_date() + timedelta(days=1)
        )
        assert tomorrow == [r["review_id"] for r in plan["all_items"]]


def test_missed_days_count_generated_days_not_refreshes_or_calendar_gap(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        ids = seed(db, family, cid, (8,))
        for offset in (7, 4, 1):
            db.add(
                DailyReviewPlan(
                    family_id=family,
                    child_id=cid,
                    plan_date=local_date() - timedelta(days=offset),
                    budget_minutes=30,
                    policy_revision="daily-plan-fair-v2",
                )
            )
        db.commit()
        candidates = load_candidates(db, family, cid, local_date())
        assert all(r.missed_plan_days == 3 for r in candidates)
        child = db.get(Child, cid)
        child.review_queue_resumed_on = local_date()
        db.commit()
        assert all(r.missed_plan_days == 0 for r in load_candidates(db, family, cid, local_date()))
        assert db.get(ReviewItem, ids[0]).review_count == 0


def test_feedback_defer_and_materialization_are_distinct(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        seed(db, family, cid, (3,))
        plan = PlanningService.daily_review_selection(db, family, cid)
        rid = plan["all_items"][0]["review_id"]
        before = db.get(ReviewItem, rid).review_count
        PlanningService.feedback(db, family, rid, "defer")
        review = db.get(ReviewItem, rid)
        assert review.review_count == before
        assert review.queue_eligible_on >= local_date() + timedelta(days=1)
        row = next(
            r
            for r in inventory_page(db, family, cid, view="count")["items"]
            if r["review_id"] == rid
        )
        assert row["arrangement_state"] == "deferred_today"
        assert row["missed_plan_days"] == 0


def test_second_preview_simulates_scarce_subject_rotation(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        seed(db, family, cid, (3, 3, 3))
        child = db.get(Child, cid)
        child.daily_budget_minutes = 5
        db.commit()
        first = preview_reviews(db, family, child, 1)
        second = preview_reviews(db, family, child, 2)
        assert (
            db.get(KnowledgeItem, first[0]).subject_id
            != db.get(KnowledgeItem, second[0]).subject_id
        )
        PlanningService.daily_review_selection(
            db, family, cid, day=local_date() + timedelta(days=1)
        )
        actual = preview_reviews(db, family, child, 2)
        assert second == actual


def test_projection_syncs_core_writes_lifecycle_and_transaction_rollback(scope):
    database, family, cid = scope
    with database.session_factory() as db:
        rid = seed(db, family, cid, (2,))[0]
        sid = db.get(KnowledgeItem, rid).subject_id

        def projection():
            assert PlanningService.review_queue_drift(db, family, cid) == 0
            return (
                db.execute(
                    select(ReviewQueueEntry.__table__).where(ReviewQueueEntry.review_item_id == rid)
                )
                .mappings()
                .one()
            )

        assert projection()["minutes"] == 3
        db.execute(update(KnowledgeItem).where(KnowledgeItem.id == rid).values(estimated_minutes=9))
        assert projection()["minutes"] == 5
        db.rollback()
        assert projection()["minutes"] == 3
        db.execute(update(Subject).where(Subject.id == sid).values(active=False))
        assert not projection()["available"]
        db.execute(
            update(Subject)
            .where(Subject.id == sid)
            .values(active=True, review_queue_resumed_on=local_date())
        )
        assert projection()["available"] and projection()["anchor_on"] == local_date()
        db.execute(update(Child).where(Child.id == cid).values(active=False))
        assert not projection()["available"]
        db.execute(
            update(Child)
            .where(Child.id == cid)
            .values(active=True, review_queue_resumed_on=local_date())
        )
        assert projection()["available"]
        db.add(
            ReviewScheduleOverride(
                review_item_id=rid,
                family_id=family,
                child_id=cid,
                scheduled_on=local_date(),
                requested_on=local_date(),
            )
        )
        db.flush()
        assert projection()["manual"]
        db.execute(
            delete(ReviewScheduleOverride).where(ReviewScheduleOverride.review_item_id == rid)
        )
        assert not projection()["manual"]
        db.execute(
            update(ReviewItem)
            .where(ReviewItem.id == rid)
            .values(review_count=2, due_date=local_date() + timedelta(days=3))
        )
        assert projection()["repeated"] and projection()["anchor_on"] == local_date() + timedelta(
            days=3
        )
        db.execute(delete(ReviewQueueEntry).where(ReviewQueueEntry.review_item_id == rid))
        assert PlanningService.review_queue_drift(db, family, cid) == 1
        PlanningService.rebuild_review_queue(db, family, cid)
        assert projection()["repeated"]
        db.execute(delete(ReviewItem).where(ReviewItem.id == rid))
        assert (
            db.scalar(
                select(ReviewQueueEntry.review_item_id).where(
                    ReviewQueueEntry.review_item_id == rid
                )
            )
            is None
        )
        db.rollback()
        assert projection()["available"]


def test_current_read_discovers_subject_created_after_reader_snapshot(scope):
    database, family, cid = scope
    if database.engine.dialect.name != "mysql":
        pytest.skip("requires MySQL repeatable-read isolation")
    with database.session_factory() as writer:
        seed(writer, family, cid, (300,))
        writer.execute(
            update(ReviewItem).where(ReviewItem.family_id == family).values(review_count=0)
        )
        writer.execute(
            update(KnowledgeItem)
            .where(KnowledgeItem.family_id == family)
            .values(estimated_minutes=1)
        )
        writer.commit()
    with database.session_factory() as reader, database.session_factory() as writer:
        reader.scalar(select(Child).where(Child.id == cid))
        new_review = seed(writer, family, cid, (1,), prefix="new-subject")[0]
        writer.execute(
            update(ReviewItem)
            .where(ReviewItem.id == new_review)
            .values(due_date=local_date(), queue_eligible_on=local_date())
        )
        writer.execute(
            update(KnowledgeItem).where(KnowledgeItem.id == new_review).values(estimated_minutes=1)
        )
        writer.commit()
        reader.scalar(select(Child).where(Child.id == cid).with_for_update())
        candidates = load_candidates(reader, family, cid, local_date(), lock=True)
        assert new_review in {candidate.review_id for candidate in candidates}
        reader.rollback()
