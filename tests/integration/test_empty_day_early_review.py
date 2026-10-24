"""Real materialization/feedback and trigger contract, including non-refill history."""

from datetime import timedelta

import pytest
from push_kids.persistence.models import (
    DailyReviewPlan,
    KnowledgeItem,
    ReviewEarlySlot,
    ReviewItem,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.early_review import early_eligible
from push_kids.planning.service import PlanningService
from push_kids.platform.time import local_date
from sqlalchemy import func, select


def seed(db, child, *, count=8):
    family, cid = "family-test-a", child["id"]
    subject = db.scalar(select(Subject).where(Subject.child_id == cid, Subject.kind == "learning"))
    if subject is None:
        subject = Subject(family_id=family, child_id=cid, name="数学", kind="learning")
        db.add(subject)
        db.flush()
    today = local_date()
    reviews = []
    for i in range(count):
        k = KnowledgeItem(
            family_id=family,
            child_id=cid,
            subject_id=subject.id,
            name=f"early-{i}",
            normalized_name=f"early-{i}",
            estimated_minutes=3,
        )
        db.add(k)
        db.flush()
        r = ReviewItem(
            family_id=family,
            child_id=cid,
            knowledge_item_id=k.id,
            due_date=today + timedelta(days=1),
            last_reviewed_on=today - timedelta(days=8),
            queue_eligible_on=today + timedelta(days=1),
            review_count=2,
            step=2,
            interval_days=9,
        )
        db.add(r)
        reviews.append(r)
    db.commit()
    db.info["empty_day_early_review_enabled"] = True
    return reviews


def test_early_offer_preserves_dates_budget_and_never_refills(app, client, child):
    with app.state.database.session_factory() as db:
        reviews = seed(db, child)
        before = {r.id: (r.due_date, r.review_count, r.last_reviewed_on) for r in reviews}
        result = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert result["early_count"] == 3
        assert result["selected_minutes"] == 9
        assert result["total_due"] == 0
        assert result["policy_revision"] == "empty-day-v1"
        for item in result["all_items"]:
            review = db.get(ReviewItem, item["review_id"])
            assert (review.due_date, review.review_count, review.last_reviewed_on) == before[
                review.id
            ]
            assert item["selection_kind"] == "early"
            PlanningService.feedback(
                db, "family-test-a", review.id, "defer", f"early-defer-{review.id}"
            )
        again = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert again["selected_count"] == 0
        assert again["planned_count"] == 3
        assert again["early_count"] == 3
        assert db.get(DailyReviewPlan, result["plan_id"]).materialization_state == "fixed_early"


def test_due_blocks_early_and_future_feedback_requires_plan(app, client, child):
    import pytest
    from push_kids.platform.errors import ConflictError

    with app.state.database.session_factory() as db:
        reviews = seed(db, child)
        reviews[0].due_date = local_date()
        db.commit()
        result = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert result["early_count"] == 0 and result["selected_count"] == 1
        with pytest.raises(ConflictError):
            PlanningService.feedback(db, "family-test-a", reviews[-1].id, "complete")
        db.rollback()


def test_projection_matches_policy_and_manual_reservation(app, client, child):
    with app.state.database.session_factory() as db:
        r = seed(db, child, count=1)[0]
        slots = set(
            db.scalars(
                select(ReviewEarlySlot.slot_on).where(ReviewEarlySlot.review_item_id == r.id)
            )
        )
        expected = {
            r.due_date - timedelta(days=n)
            for n in (1, 2, 3)
            if early_eligible(
                target=r.due_date - timedelta(days=n),
                due=r.due_date,
                last_reviewed=r.last_reviewed_on,
                review_count=r.review_count,
                eligible_on=r.queue_eligible_on,
            )
        }
        assert slots == expected and local_date() in slots
        db.add(
            ReviewScheduleOverride(
                review_item_id=r.id,
                family_id=r.family_id,
                child_id=r.child_id,
                scheduled_on=r.due_date,
                requested_on=local_date(),
            )
        )
        db.commit()
        assert db.scalar(select(func.count()).select_from(ReviewEarlySlot)) == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("review_count", 0),
        ("last_reviewed_on", None),
        ("last_offered_on", "yesterday"),
        ("queue_eligible_on", "tomorrow"),
        ("active", False),
    ],
)
def test_projection_rechecks_changed_review(app, client, child, field, value):
    with app.state.database.session_factory() as db:
        r = seed(db, child, count=1)[0]
        if value == "yesterday":
            value = local_date() - timedelta(days=1)
        if value == "tomorrow":
            value = local_date() + timedelta(days=2)
        setattr(r, field, value)
        db.commit()
        assert not db.scalar(
            select(ReviewEarlySlot.review_item_id).where(ReviewEarlySlot.slot_on == local_date())
        )


def test_originally_empty_reopens_only_after_inventory_changes(app, client, child):
    from push_kids.persistence.models import Child

    with app.state.database.session_factory() as db:
        db.info["empty_day_early_review_enabled"] = True
        first = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert first["planned_count"] == 0
        assert (
            db.get(DailyReviewPlan, first["plan_id"]).materialization_state == "provisional_empty"
        )
        seed(db, child, count=1)
        # Direct storage setup alone is not a formal inventory mutation.
        assert (
            PlanningService.daily_review_selection(db, "family-test-a", child["id"])[
                "planned_count"
            ]
            == 0
        )
        row = db.get(Child, child["id"])
        row.review_inventory_revision += 1
        db.commit()
        selected = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert selected["plan_id"] == first["plan_id"] and selected["early_count"] == 1


def test_real_early_feedback_and_stale_version(app, client, child):
    from push_kids.platform.errors import ConflictError

    with app.state.database.session_factory() as db:
        seed(db, child, count=2)
        selected = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        first, second = [db.get(ReviewItem, i["review_id"]) for i in selected["all_items"]]
        old_count = first.review_count
        PlanningService.feedback(db, "family-test-a", first.id, "complete", "true-early-feedback")
        assert first.last_reviewed_on == local_date() and first.review_count == old_count + 1
        assert first.due_date > local_date()
        second.state_version += 1
        db.commit()
        with pytest.raises(ConflictError):
            PlanningService.feedback(
                db, "family-test-a", second.id, "complete", "stale-early-feedback"
            )
        db.rollback()


def test_slot_drift_is_repairable_without_touching_review_facts(app, client, child):
    from push_kids.planning.early_projection import projection_drift, rebuild_projection
    from sqlalchemy import delete

    with app.state.database.session_factory() as db:
        r = seed(db, child, count=1)[0]
        due = r.due_date
        assert projection_drift(db, r.family_id, r.child_id) == 0
        db.execute(delete(ReviewEarlySlot).where(ReviewEarlySlot.review_item_id == r.id))
        assert projection_drift(db, r.family_id, r.child_id) > 0
        rebuild_projection(db, r.family_id, r.child_id)
        assert projection_drift(db, r.family_id, r.child_id) == 0
        assert r.due_date == due and r.review_count == 2


def test_unaffordable_due_item_still_blocks_early_fill(app, client, child):
    from push_kids.persistence.models import Child

    with app.state.database.session_factory() as db:
        due, future = seed(db, child, count=2)
        db.get(Child, child["id"]).daily_budget_minutes = 2
        due.due_date = local_date()
        db.get(KnowledgeItem, due.knowledge_item_id).estimated_minutes = 5
        db.get(KnowledgeItem, future.knowledge_item_id).estimated_minutes = 1
        db.commit()
        result = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert result["total_due"] == 1
        assert result["selected_count"] == 0 and result["early_count"] == 0


def test_early_subject_opportunity_is_not_hidden_by_a_large_single_subject(app, client, child):
    from push_kids.persistence.models import Child

    with app.state.database.session_factory() as db:
        rows = seed(db, child, count=130)
        db.get(Child, child["id"]).daily_budget_minutes = 3
        subject = Subject(
            family_id="family-test-a", child_id=child["id"], name="英语", kind="learning"
        )
        db.add(subject)
        db.flush()
        for row in rows[:-1]:
            row.last_offered_on = local_date() - timedelta(days=3)
        db.get(KnowledgeItem, rows[-1].knowledge_item_id).subject_id = subject.id
        db.commit()
        result = PlanningService.daily_review_selection(db, "family-test-a", child["id"])
        assert [item["review_id"] for item in result["all_items"]] == [rows[-1].id]


def test_two_day_preview_is_read_only_and_does_not_repeat_early_items(app, client, child):
    from push_kids.persistence.models import Child
    from push_kids.planning.inventory import preview_reviews

    with app.state.database.session_factory() as db:
        rows = seed(db, child, count=8)
        for row in rows:
            row.due_date = local_date() + timedelta(days=3)
            row.last_reviewed_on = local_date() - timedelta(days=20)
            row.queue_eligible_on = row.due_date
        db.commit()
        snapshot = [(row.due_date, row.review_count, row.last_offered_on) for row in rows]
        profile = db.get(Child, child["id"])
        tomorrow = preview_reviews(db, "family-test-a", profile, 1)
        day_after = preview_reviews(db, "family-test-a", profile, 2)
        assert len(tomorrow) == len(day_after) == 3
        assert not set(tomorrow) & set(day_after)
        assert db.scalar(select(func.count()).select_from(DailyReviewPlan)) == 0
        assert snapshot == [(row.due_date, row.review_count, row.last_offered_on) for row in rows]
