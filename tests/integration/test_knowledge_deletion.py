"""Single-knowledge deletion through real HTTP, persistence and read projections."""

import pytest
from push_kids.persistence.models import (
    Child,
    DailyReviewPlanItem,
    FamilyMember,
    KnowledgeItem,
    KnowledgeOccurrence,
    KnowledgeSearchTerm,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.time import local_date
from sqlalchemy import event, func, select

from tests.integration.test_todo_provenance import _confirmed


def test_deleting_later_intake_does_not_subtract_from_existing_plan(
    client, app, family_headers, child
):
    _confirmed(client, app, family_headers, child["id"], "数学，加法")
    endpoint = f"/api/v1/children/{child['id']}/dashboard"
    before = client.get(endpoint, headers=family_headers).json()["review_selection"]
    later = _confirmed(client, app, family_headers, child["id"], "数学，减法")
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, later["review_item_ids"][0]).knowledge_item_id
    response = client.delete(
        f"/api/v1/children/{child['id']}/knowledge/{kid}", headers=family_headers
    )
    assert response.status_code == 204
    after = client.get(endpoint, headers=family_headers).json()["review_selection"]
    assert after["plan_id"] == before["plan_id"]
    assert after["total_due"] == before["total_due"]
    assert after["all_items"] == before["all_items"]


def test_delete_only_selected_knowledge_and_refresh_all_projections(
    client, app, family_headers, child
):
    confirmed = _confirmed(client, app, family_headers, child["id"], "数学，加法，减法")
    family = family_headers["X-Family-ID"]
    rid = confirmed["review_item_ids"][0]
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, rid).knowledge_item_id
        before_records = db.scalar(select(func.count(LearningRecord.id)))
    dashboard = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    plan_before = dashboard.json()["review_selection"]
    assert (
        client.post(
            f"/api/v1/reviews/{rid}/feedback",
            headers={**family_headers, "Idempotency-Key": "delete-feedback-1"},
            json={"action": "reinforce"},
        ).status_code
        == 200
    )
    with app.state.database.session_factory() as db:
        remaining = set(db.scalars(select(KnowledgeItem.id))) - {kid}
        assert remaining
    path = f"/api/v1/children/{child['id']}/knowledge/{kid}"
    assert client.delete(path, headers=family_headers).status_code == 204
    assert client.delete(path, headers=family_headers).status_code == 204
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid) is None
        assert db.get(ReviewItem, rid) is None
        assert set(db.scalars(select(KnowledgeItem.id))) == remaining
        assert db.scalar(select(func.count(LearningRecord.id))) == before_records
        assert db.get(LearningSubmission, confirmed["submission_id"]) is not None
        for model in (ReviewFeedback, ReviewFeedbackRequest, DailyReviewPlanItem):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.review_item_id == rid)
                )
                == 0
            )
        for model in (KnowledgeOccurrence, KnowledgeSearchTerm):
            assert (
                db.scalar(
                    select(func.count()).select_from(model).where(model.knowledge_item_id == kid)
                )
                == 0
            )
        loads = PlanningService.pending_review_loads(
            db, local_date(), family_id=family, child_ids={child["id"]}
        )
        assert sum(item.pending_count for item in loads) == len(remaining)
    after = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers).json()[
        "review_selection"
    ]
    assert after["planned_count"] == plan_before["planned_count"] - 1
    assert after["planned_minutes"] < plan_before["planned_minutes"]
    history = client.get(
        f"/api/v1/children/{child['id']}/history/{confirmed['submission_id']}",
        headers=family_headers,
    ).json()
    assert {item["id"] for item in history["knowledge"]} == remaining
    assert (
        client.post(
            f"/api/v1/reviews/{rid}/feedback", headers=family_headers, json={"action": "complete"}
        ).status_code
        == 404
    )


def test_delete_is_scoped_and_rejects_unwritable_child(client, app, family_headers, child):
    confirmed = _confirmed(client, app, family_headers, child["id"], "数学，加法")
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, confirmed["review_item_ids"][0]).knowledge_item_id
    path = f"/api/v1/children/{child['id']}/knowledge/{kid}"
    assert client.delete(path, headers={"X-Family-ID": "other-family"}).status_code == 404
    other = client.post(
        "/api/v1/children", headers=family_headers, json={"name": "其他孩子"}
    ).json()
    assert (
        client.delete(
            f"/api/v1/children/{other['id']}/knowledge/{kid}", headers=family_headers
        ).status_code
        == 204
    )
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid) is not None
        db.get(Child, child["id"]).deleting = True
        db.commit()
    assert client.delete(path, headers=family_headers).status_code == 409


def test_delete_rolls_back_every_association_on_failure(client, app, family_headers, child):
    confirmed = _confirmed(client, app, family_headers, child["id"], "数学，加法")
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, confirmed["review_item_ids"][0]).knowledge_item_id
        before = db.scalar(select(func.count(KnowledgeOccurrence.id)))

    def fail(_conn, _cursor, statement, _parameters, _context, _many):
        if statement.startswith("DELETE FROM knowledge_items"):
            raise RuntimeError("injected transaction failure")

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", fail)
    try:
        with pytest.raises(RuntimeError, match="injected"):
            client.delete(f"/api/v1/children/{child['id']}/knowledge/{kid}", headers=family_headers)
    finally:
        event.remove(engine, "before_cursor_execute", fail)
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid) is not None
        assert db.get(ReviewItem, confirmed["review_item_ids"][0]) is not None
        assert db.scalar(select(func.count(KnowledgeOccurrence.id))) == before


def test_viewer_cannot_delete_and_editor_can(client, app):
    headers = {"X-Debug-Actor": "delete-parent", "Idempotency-Key": "delete-family-1"}
    created = client.post(
        "/api/v1/families",
        headers=headers,
        json={
            "display_name": "测试家庭",
            "relationship_label": "家长",
            "child": {"name": "测试孩子"},
        },
    )
    assert created.status_code == 201
    cid = created.json()["children"][0]["id"]
    confirmed = _confirmed(client, app, headers, cid, "数学，加法")
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, confirmed["review_item_ids"][0]).knowledge_item_id
        member = db.get(FamilyMember, created.json()["member"]["id"])
        member.role = "viewer"
        db.commit()
    path = f"/api/v1/children/{cid}/knowledge/{kid}"
    assert client.delete(path, headers=headers).status_code == 403
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid) is not None
        db.get(FamilyMember, created.json()["member"]["id"]).role = "editor"
        db.commit()
    assert client.delete(path, headers=headers).status_code == 204


def test_deleted_batch_feedback_replay_never_resurrects(client, app, family_headers, child):
    confirmed = _confirmed(client, app, family_headers, child["id"], "数学，加法")
    rid = confirmed["review_item_ids"][0]
    body = {"child_id": child["id"], "items": [{"review_id": rid, "action": "complete"}]}
    headers = {**family_headers, "Idempotency-Key": "deleted-batch-001"}
    first = client.post("/api/v1/review-feedback-batches", headers=headers, json=body)
    assert first.status_code == 200
    with app.state.database.session_factory() as db:
        kid = db.get(ReviewItem, rid).knowledge_item_id
    assert (
        client.delete(
            f"/api/v1/children/{child['id']}/knowledge/{kid}", headers=family_headers
        ).status_code
        == 204
    )
    replay = client.post("/api/v1/review-feedback-batches", headers=headers, json=body)
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid) is None
        assert db.get(ReviewItem, rid) is None
