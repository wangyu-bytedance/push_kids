"""Subject order follows the original daily plan through real feedback and reads."""

import pytest
from push_kids.persistence.models import (
    DailyReviewPlan,
    DailyReviewPlanItem,
    KnowledgeItem,
    ReviewItem,
    Subject,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.time import local_date


def seed_plan(app, family, child_id, names=("语文", "数学", "英语")):
    with app.state.database.session_factory() as db:
        subjects = [
            Subject(family_id=family, child_id=child_id, name=name, kind="learning")
            for name in names
        ]
        db.add_all(subjects)
        db.flush()
        plan = DailyReviewPlan(
            family_id=family,
            child_id=child_id,
            plan_date=local_date(),
            budget_minutes=15,
            total_minutes=12,
            due_count=6,
        )
        db.add(plan)
        db.flush()
        review_ids = {name: [] for name in names}
        for round_number in range(2):
            for index, subject in enumerate(subjects):
                knowledge = KnowledgeItem(
                    family_id=family,
                    child_id=child_id,
                    subject_id=subject.id,
                    name=f"synthetic-{index}-{round_number}",
                    normalized_name=f"synthetic-{index}-{round_number}",
                    estimated_minutes=index + 1,
                )
                db.add(knowledge)
                db.flush()
                review = ReviewItem(
                    family_id=family,
                    child_id=child_id,
                    knowledge_item_id=knowledge.id,
                    due_date=local_date(),
                )
                db.add(review)
                db.flush()
                db.add(
                    DailyReviewPlanItem(
                        family_id=family,
                        child_id=child_id,
                        plan_id=plan.id,
                        review_item_id=review.id,
                        ordinal=round_number * len(subjects) + index,
                        estimated_minutes=index + 1,
                    )
                )
                review_ids[subject.name].append(review.id)
        db.commit()
    return review_ids


def read_plan(app, family, child_id):
    with app.state.database.session_factory() as db:
        return PlanningService.daily_review_selection(db, family, child_id)


@pytest.mark.parametrize("action", ["complete", "partial", "reinforce", "defer"])
def test_feedback_preserves_subject_and_remaining_item_order(app, child, family_headers, action):
    family = family_headers["X-Family-ID"]
    ids = seed_plan(app, family, child["id"])
    before = read_plan(app, family, child["id"])
    rid = ids["语文"][0]
    with app.state.database.session_factory() as db:
        PlanningService.feedback(db, family, rid, action)
    after = read_plan(app, family, child["id"])

    assert [g["subject_name"] for g in after["sessions"]] == ["语文", "数学", "英语"]
    assert [g["id"] for g in after["sessions"]] == [g["id"] for g in before["sessions"]]
    for group in after["sessions"]:
        assert [item["review_id"] for item in group["items"]] == [
            item for item in ids[group["subject_name"]] if item != rid
        ]
        assert group["estimated_minutes"] == sum(
            item["estimated_minutes"] for item in group["items"]
        )
    assert after["plan_id"] == before["plan_id"]
    assert after["planned_count"] == before["planned_count"] == 6
    assert after["planned_minutes"] == before["planned_minutes"] == 12
    assert after["selected_count"] == 5
    assert after["selected_minutes"] == 11
    assert after["today_feedback_count"] == after["today_feedback_minutes"] == 1
    assert [item["review_id"] for item in after["all_items"]] == [
        item["review_id"] for item in before["all_items"]
    ]
    completed = next(item for item in after["all_items"] if item["review_id"] == rid)
    assert completed["state"] == ("deferred" if action == "defer" else action)
    assert completed["review_count"] == (0 if action == "defer" else 1)
    assert after == read_plan(app, family, child["id"])


def test_only_empty_subjects_disappear_and_all_complete_has_no_empty_cards(
    app, child, family_headers
):
    family = family_headers["X-Family-ID"]
    ids = seed_plan(app, family, child["id"])
    for name in ("数学", "语文", "英语"):
        for rid in ids[name]:
            with app.state.database.session_factory() as db:
                PlanningService.feedback(db, family, rid, "complete")
        current = read_plan(app, family, child["id"])
        assert all(group["items"] for group in current["sessions"])
        assert [group["subject_name"] for group in current["sessions"]] == {
            "数学": ["语文", "英语"],
            "语文": ["英语"],
            "英语": [],
        }[name]
    assert current["selected_count"] == current["selected_minutes"] == 0
    assert current["today_feedback_count"] == current["planned_count"] == 6
    assert current["today_feedback_minutes"] == current["planned_minutes"] == 12


def test_empty_plan_has_no_subject_cards(app, child, family_headers):
    current = read_plan(app, family_headers["X-Family-ID"], child["id"])
    assert current["sessions"] == []
    assert current["planned_count"] == current["selected_count"] == 0


def test_dashboard_feedback_and_idempotent_replay_keep_custom_plan_order(
    app, client, child, family_headers
):
    family = family_headers["X-Family-ID"]
    names = ("阅读", "英语", "数学")
    ids = seed_plan(app, family, child["id"], names)
    dashboard_path = f"/api/v1/children/{child['id']}/dashboard"
    before = client.get(dashboard_path, headers=family_headers)
    assert before.status_code == 200
    original = before.json()["review_selection"]
    assert [g["subject_name"] for g in original["sessions"]] == list(names)

    feedback_path = f"/api/v1/reviews/{ids[names[0]][0]}/feedback"
    headers = {**family_headers, "Idempotency-Key": "synthetic-order-complete"}
    first = client.post(feedback_path, headers=headers, json={"action": "complete"})
    replay = client.post(feedback_path, headers=headers, json={"action": "complete"})
    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()
    for _ in range(3):
        response = client.get(dashboard_path, headers=family_headers)
        assert response.status_code == 200
        current = response.json()["review_selection"]
        assert [g["subject_name"] for g in current["sessions"]] == list(names)
        assert current["plan_id"] == original["plan_id"]
        assert current["selected_count"] == 5
        assert current["today_feedback_count"] == 1


def test_other_family_cannot_change_order_and_sibling_plan_is_unchanged(
    app, client, child, family_headers
):
    family = family_headers["X-Family-ID"]
    ids = seed_plan(app, family, child["id"])
    sibling = client.post(
        "/api/v1/children", headers=family_headers, json={"name": "synthetic-sibling"}
    )
    assert sibling.status_code == 201
    sibling_id = sibling.json()["id"]
    seed_plan(app, family, sibling_id, ("科学", "数学", "英语"))
    sibling_before = read_plan(app, family, sibling_id)
    before = read_plan(app, family, child["id"])
    rid = ids["语文"][0]
    denied = client.post(
        f"/api/v1/reviews/{rid}/feedback",
        headers={"X-Family-ID": "synthetic-other-family"},
        json={"action": "complete"},
    )
    assert denied.status_code == 404
    assert read_plan(app, family, child["id"]) == before
    denied_read = client.get(
        f"/api/v1/children/{child['id']}/dashboard",
        headers={"X-Family-ID": "synthetic-other-family"},
    )
    assert denied_read.status_code == 404
    with app.state.database.session_factory() as db:
        PlanningService.feedback(db, family, rid, "complete")
    assert read_plan(app, family, sibling_id) == sibling_before
