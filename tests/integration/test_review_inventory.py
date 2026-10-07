"""Inventory and parent scheduling through HTTP with deterministic synthetic records."""

from datetime import timedelta

import pytest
from push_kids.persistence.models import (
    Child,
    DailyReviewPlan,
    DailyReviewPlanItem,
    FamilyMember,
    KnowledgeItem,
    ReviewFeedback,
    ReviewItem,
    ReviewScheduleChange,
    ReviewScheduleOverride,
    Subject,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.time import local_date
from sqlalchemy import event, func, select


def seed(app, family, child_id, size=6):
    with app.state.database.session_factory() as db:
        subject = Subject(family_id=family, child_id=child_id, name="测试数学", kind="learning")
        db.add(subject)
        db.flush()
        sid = subject.id
        ids = []
        for i in range(size):
            k = KnowledgeItem(
                family_id=family,
                child_id=child_id,
                subject_id=sid,
                name=f"知识{i}",
                normalized_name=f"知识{i}",
                estimated_minutes=5,
            )
            db.add(k)
            db.flush()
            r = ReviewItem(
                family_id=family,
                child_id=child_id,
                knowledge_item_id=k.id,
                due_date=local_date(),
                review_count=i % 4,
            )
            db.add(r)
            db.flush()
            ids.append((r.id, k.id))
        db.commit()
    return sid, ids


def path(child):
    return f"/api/v1/children/{child['id']}/review-inventory"


def schedule(
    client, headers, child, rid, *, action="tomorrow", version=0, key="schedule-test-1", day=None
):
    return client.post(
        f"/api/v1/children/{child['id']}/reviews/{rid}/schedule",
        headers={**headers, "Idempotency-Key": key},
        json={
            "action": action,
            "expected_version": version,
            "base_day": (day or local_date()).isoformat(),
        },
    )


def test_filters_paging_and_readonly_preview(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    sid, ids = seed(app, family, child["id"])
    empty = client.post(
        "/api/v1/subjects", headers=family_headers, json={"child_id": child["id"], "name": "空科目"}
    ).json()
    activity = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "跑步", "kind": "activity"},
    ).json()
    subjects = client.get(path(child) + "/subjects", headers=family_headers).json()["items"]
    assert {s["id"] for s in subjects} == {sid, empty["id"]}
    assert any(s["count"] == 0 for s in subjects)
    assert (
        client.get(path(child), headers=family_headers, params={"view": "subject"}).status_code
        == 400
    )
    assert (
        client.get(
            path(child),
            headers=family_headers,
            params={"view": "subject", "subject_id": activity["id"]},
        ).status_code
        == 404
    )
    first = client.get(
        path(child), headers=family_headers, params={"view": "count", "limit": 2}
    ).json()
    second = client.get(
        path(child),
        headers=family_headers,
        params={"view": "count", "limit": 2, "cursor": first["next_cursor"]},
    ).json()
    assert [i["review_count"] for i in first["items"] + second["items"]] == [0, 0, 1, 1]
    assert first["total"] == 6
    for count, expected in [(0, 2), (1, 2), (6, 0), (2147483647, 0)]:
        result = client.get(
            path(child), headers=family_headers, params={"view": "count", "review_count": count}
        ).json()
        assert result["total"] == expected
        assert all(i["review_count"] == count for i in result["items"])
    for count in [-1, "1.5", 2147483648, "null"]:
        assert (
            client.get(
                path(child), headers=family_headers, params={"view": "count", "review_count": count}
            ).status_code
            == 422
        )
    tomorrow = client.get(path(child), headers=family_headers).json()
    after = client.get(path(child), headers=family_headers, params={"offset": 2}).json()
    assert tomorrow["total"] == after["total"] == 3
    assert {i["review_id"] for i in tomorrow["items"]}.isdisjoint(
        i["review_id"] for i in after["items"]
    )
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(DailyReviewPlan)) == 0
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 0
    rid = ids[0][0]
    assert schedule(client, family_headers, child, rid).status_code == 200
    stale = client.get(
        path(child),
        headers=family_headers,
        params={"view": "count", "limit": 2, "cursor": first["next_cursor"]},
    )
    assert stale.status_code == 409


def test_manual_priority_over_budget_and_version_idempotency(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 125)
    chosen = ids[-4:]
    for n, (rid, _) in enumerate(chosen):
        response = schedule(client, family_headers, child, rid, key=f"schedule-reserve-{n}")
        assert response.status_code == 200, response.text
    assert response.json()["over_budget_minutes"] == 5
    preview = client.get(path(child), headers=family_headers).json()
    assert {i["review_id"] for i in preview["items"]} == {rid for rid, _ in chosen}
    rid = chosen[-1][0]
    replay = schedule(client, family_headers, child, rid, key="schedule-reserve-3")
    assert replay.json() == response.json()
    assert schedule(client, family_headers, child, rid, key="schedule-stale-1").status_code == 409
    assert (
        schedule(
            client, family_headers, child, rid, version=1, key="schedule-reserve-3"
        ).status_code
        == 409
    )
    lowered = schedule(
        client, family_headers, child, rid, action="day_after", version=1, key="schedule-lower-1"
    )
    assert lowered.status_code == 200, lowered.text
    assert lowered.json()["due_date"] == (local_date() + timedelta(days=2)).isoformat()
    assert (
        schedule(
            client,
            family_headers,
            child,
            rid,
            action="day_after",
            version=2,
            key="schedule-lower-2",
        ).status_code
        == 409
    )
    raised = schedule(client, family_headers, child, rid, version=2, key="schedule-raise-1")
    assert raised.status_code == 200
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 0
        assert db.get(ReviewItem, rid).review_count == 0
        assert db.get(ReviewItem, rid).last_reviewed_on is None
        assert db.get(ReviewItem, rid).step == 0
        assert db.scalar(select(func.count()).select_from(ReviewScheduleOverride)) == 4
        assert db.scalar(select(func.count()).select_from(ReviewScheduleChange)) == 6


def test_reschedule_withdraws_today_without_feedback_or_refill(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 10)
    endpoint = f"/api/v1/children/{child['id']}/dashboard"
    before = client.get(endpoint, headers=family_headers).json()["review_selection"]
    rid = before["all_items"][0]["review_id"]
    assert schedule(client, family_headers, child, rid).status_code == 200
    after = client.get(endpoint, headers=family_headers).json()["review_selection"]
    assert after["plan_id"] == before["plan_id"]
    assert after["planned_count"] == before["planned_count"] - 1
    assert after["total_due"] == before["total_due"] - 1
    assert after["planned_minutes"] == before["planned_minutes"] - 5
    assert after["today_feedback_count"] == 0
    assert {i["review_id"] for i in after["all_items"]} == {
        i["review_id"] for i in before["all_items"]
    } - {rid}
    with app.state.database.session_factory() as db:
        item = db.scalar(
            select(DailyReviewPlanItem).where(DailyReviewPlanItem.review_item_id == rid)
        )
        assert item.state == "rescheduled"
    kid = next(kid for review_id, kid in ids if review_id == rid)
    assert (
        client.delete(
            f"/api/v1/children/{child['id']}/knowledge/{kid}", headers=family_headers
        ).status_code
        == 204
    )
    remaining = client.get(endpoint, headers=family_headers).json()["review_selection"]
    assert remaining["total_due"] == after["total_due"]
    assert remaining["planned_minutes"] == after["planned_minutes"]


def test_manual_add_of_budget_backlog_keeps_future_due_total(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 5)
    tomorrow = local_date() + timedelta(days=1)
    with app.state.database.session_factory() as db:
        today_before = PlanningService.daily_review_selection(db, family, child["id"])
        before = PlanningService.daily_review_selection(db, family, child["id"], day=tomorrow)
    assert today_before["total_due"] == 5
    assert before["planned_count"] == 3
    assert before["total_due"] == 5
    selected = {item["review_id"] for item in before["all_items"]}
    backlog_id = next(rid for rid, _ in ids if rid not in selected)

    response = schedule(client, family_headers, child, backlog_id, key="budget-backlog")
    assert response.status_code == 200, response.text
    with app.state.database.session_factory() as db:
        today_after = PlanningService.daily_review_selection(db, family, child["id"])
        after = PlanningService.daily_review_selection(db, family, child["id"], day=tomorrow)
    assert today_after["total_due"] == 4
    assert today_after["backlog_count"] == 1
    assert after["planned_count"] == 4
    assert after["total_due"] == 5
    assert after["backlog_count"] == 1
    assert backlog_id in {item["review_id"] for item in after["all_items"]}


def test_schedule_consumed_only_by_current_real_feedback_and_delete_cleans(
    client, app, family_headers, child
):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 1)
    rid, kid = ids[0]
    assert schedule(client, family_headers, child, rid).status_code == 200
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, rid)
        due = review.due_date
        PlanningService.record_review_event(
            db,
            family_id=family,
            review=review,
            action="observed",
            reviewed_on=local_date() - timedelta(days=2),
            source="test",
        )
        db.commit()
        assert review.review_count == 1
        assert review.due_date == due
        assert review.last_reviewed_on is None
        assert db.get(ReviewScheduleOverride, rid) is not None
    result = client.post(
        f"/api/v1/reviews/{rid}/feedback", headers=family_headers, json={"action": "complete"}
    )
    assert result.status_code == 200, result.text
    with app.state.database.session_factory() as db:
        assert db.get(ReviewScheduleOverride, rid) is None
        assert db.get(ReviewItem, rid).review_count == 2
        version = db.get(ReviewItem, rid).state_version
    assert (
        schedule(
            client, family_headers, child, rid, version=version, key="schedule-again-1"
        ).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/v1/children/{child['id']}/knowledge/{kid}", headers=family_headers
        ).status_code
        == 204
    )
    with app.state.database.session_factory() as db:
        assert db.get(ReviewScheduleOverride, rid) is None
        assert db.scalar(select(func.count()).select_from(ReviewScheduleChange)) == 0


def test_tenant_midnight_inactive_and_atomic_rollback(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 1)
    rid, _ = ids[0]
    assert client.get(path(child), headers={"X-Family-ID": "another"}).status_code == 404
    assert schedule(client, {"X-Family-ID": "another"}, child, rid).status_code == 404
    assert (
        schedule(
            client, family_headers, child, rid, day=local_date() - timedelta(days=1)
        ).status_code
        == 409
    )

    with app.state.database.session_factory() as db:
        r = db.get(ReviewItem, rid)
        r.active, r.step, r.review_count = False, 4, 8
        db.commit()

    def fail(_conn, _cursor, statement, _parameters, _context, _many):
        if statement.startswith("INSERT INTO review_schedule_changes"):
            raise RuntimeError("schedule failure")

    event.listen(app.state.database.engine, "before_cursor_execute", fail)
    try:
        with pytest.raises(RuntimeError, match="schedule failure"):
            schedule(client, family_headers, child, rid)
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", fail)
    with app.state.database.session_factory() as db:
        assert db.get(ReviewItem, rid).active is False
        assert db.get(ReviewScheduleOverride, rid) is None
    assert schedule(client, family_headers, child, rid).status_code == 200
    with app.state.database.session_factory() as db:
        r = db.get(ReviewItem, rid)
        assert r.active and r.step == 0 and r.review_count == 8
        db.get(Child, child["id"]).active = False
        db.commit()
    assert (
        schedule(client, family_headers, child, rid, version=1, key="archived-test-1").status_code
        == 409
    )


@pytest.mark.parametrize("action", ["complete", "observed", "partial", "reinforce"])
def test_same_day_feedback_restores_automatic_curve_before_consuming_arrangement(
    client, app, family_headers, child, action
):
    from push_kids.planning.policies import ReviewState, apply_review_event

    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 1)
    rid, _ = ids[0]
    with app.state.database.session_factory() as db:
        r = db.get(ReviewItem, rid)
        first = PlanningService.record_review_event(
            db,
            family_id=family,
            review=r,
            action="complete",
            reviewed_on=local_date(),
            source="test",
        )
        db.commit()
        original = ReviewState(**{k: v for k, v in first.__dict__.items() if k != "advanced"})
    assert schedule(client, family_headers, child, rid, version=1).status_code == 200
    with app.state.database.session_factory() as db:
        r = db.get(ReviewItem, rid)
        second = PlanningService.record_review_event(
            db, family_id=family, review=r, action=action, reviewed_on=local_date(), source="test"
        )
        db.commit()
        expected = apply_review_event(original, action, local_date())
        assert second.due_date == expected.due_date
        assert second.interval_days == expected.interval_days
        assert second.review_count == 2
        assert db.get(ReviewScheduleOverride, rid) is None
    if action in {"complete", "observed"}:
        assert client.get(path(child), headers=family_headers).json()["items"] == []


def test_viewer_reads_inventory_but_cannot_schedule(client, app):
    headers = {"X-Debug-Actor": "inventory-parent", "Idempotency-Key": "inventory-family-1"}
    created = client.post(
        "/api/v1/families",
        headers=headers,
        json={
            "display_name": "测试家庭",
            "relationship_label": "家长",
            "child": {"name": "测试孩子"},
        },
    ).json()
    child = created["children"][0]
    _, ids = seed(app, created["family"]["id"], child["id"], 1)
    with app.state.database.session_factory() as db:
        db.get(FamilyMember, created["member"]["id"]).role = "viewer"
        db.commit()
    assert client.get(path(child), headers=headers, params={"view": "count"}).status_code == 200
    assert schedule(client, headers, child, ids[0][0]).status_code == 403
    with app.state.database.session_factory() as db:
        assert db.get(ReviewScheduleOverride, ids[0][0]) is None


def test_purge_removes_arrangements_only_for_target_child(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    other = client.post(
        "/api/v1/children", headers=family_headers, json={"name": "另一个孩子"}
    ).json()
    _, ids = seed(app, family, child["id"], 1)
    _, other_ids = seed(app, family, other["id"], 1)
    assert schedule(client, family_headers, child, ids[0][0]).status_code == 200
    assert (
        schedule(
            client, family_headers, other, other_ids[0][0], key="schedule-sibling-1"
        ).status_code
        == 200
    )
    with app.state.database.session_factory() as db:
        PlanningService.purge_data(db, family, child["id"])
        db.commit()
        assert db.get(ReviewScheduleOverride, ids[0][0]) is None
        assert db.get(ReviewScheduleOverride, other_ids[0][0]) is not None
        assert db.scalar(select(func.count()).select_from(ReviewScheduleChange)) == 1


def test_preview_honors_existing_future_snapshot_without_refill(client, app, family_headers, child):
    family = family_headers["X-Family-ID"]
    _, ids = seed(app, family, child["id"], 6)
    tomorrow = local_date() + timedelta(days=1)
    with app.state.database.session_factory() as db:
        plan = PlanningService.daily_review_selection(db, family, child["id"], day=tomorrow)
    original = {i["review_id"] for i in plan["all_items"]}
    moved = next(iter(original))
    assert schedule(client, family_headers, child, moved, action="day_after").status_code == 200
    current = client.get(path(child), headers=family_headers).json()
    assert {i["review_id"] for i in current["items"]} == original - {moved}
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(DailyReviewPlan)) == 1
    left_out = next(rid for rid, _ in ids if rid not in original)
    assert (
        schedule(client, family_headers, child, left_out, key="join-materialized-1").status_code
        == 200
    )
    current = client.get(path(child), headers=family_headers).json()
    assert {i["review_id"] for i in current["items"]} == original - {moved} | {left_out}
