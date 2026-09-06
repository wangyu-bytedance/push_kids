from datetime import timedelta

import pytest
from push_kids.agent_processing.contracts import AnalysisProposal, KnowledgeProposal
from push_kids.learning.schemas import ConfirmSubmission
from push_kids.learning.service import LearningService
from push_kids.persistence.models import (
    AgentJob,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select


def proposal(**updates):
    return AnalysisProposal(
        **{
            "summary": "本次活动",
            "subject_name": "游泳",
            "subject_kind": "activity",
            "knowledge_points": [KnowledgeProposal(name="换气")],
            **updates,
        }
    )


def pending(db, family, child_id):
    item = LearningSubmission(
        family_id=family, child_id=child_id, occurred_at=utcnow(), state="pending_confirmation"
    )
    db.add(item)
    db.commit()
    return item.id


@pytest.mark.parametrize("mode", ["new", "name", "id"])
def test_activity_confirmation_has_no_writes(client, app, child, family_headers, mode):
    family = family_headers["X-Family-ID"]
    with app.state.database.session_factory() as db:
        subject = None
        if mode != "new":
            subject = Subject(family_id=family, child_id=child["id"], name="游泳", kind="activity")
            db.add(subject)
            db.commit()
        sid = pending(db, family, child["id"])
        models = [
            Subject,
            LearningRecord,
            KnowledgeItem,
            KnowledgeOccurrence,
            ReviewItem,
            ReviewFeedback,
        ]
        before = [db.scalar(select(func.count()).select_from(model)) for model in models]
        body = ConfirmSubmission(
            subject_id=subject.id if mode == "id" else None,
            proposal=proposal(subject_kind="learning" if mode != "new" else "activity"),
        )
    response = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json=body.model_dump(mode="json"),
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_input"
    with app.state.database.session_factory() as db:
        assert [db.scalar(select(func.count()).select_from(model)) for model in models] == before
        assert db.get(LearningSubmission, sid).state == "pending_confirmation"


def test_parent_selected_learning_subject_wins(client, app, child, family_headers):
    family = family_headers["X-Family-ID"]
    with app.state.database.session_factory() as db:
        subject = Subject(family_id=family, child_id=child["id"], name="科学", kind="learning")
        db.add(subject)
        db.commit()
        sid = pending(db, family, child["id"])
        subject_id = subject.id
    response = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={"subject_id": subject_id, "proposal": proposal().model_dump(mode="json")},
    )
    assert response.status_code == 200
    assert response.json()["subject_id"] == subject_id
    assert len(response.json()["review_item_ids"]) == 1


def test_historical_activity_reviews_are_inert(client, app, child, family_headers):
    family = family_headers["X-Family-ID"]
    with app.state.database.session_factory() as db:
        subject = Subject(family_id=family, child_id=child["id"], name="游泳", kind="activity")
        db.add(subject)
        db.flush()
        subject_id = subject.id
        knowledge = KnowledgeItem(
            family_id=family,
            child_id=child["id"],
            subject_id=subject.id,
            name="换气",
            normalized_name="换气",
        )
        db.add(knowledge)
        db.flush()
        sid = pending(db, family, child["id"])
        record = LearningRecord(
            family_id=family,
            child_id=child["id"],
            subject_id=subject.id,
            submission_id=sid,
            summary="历史错误活动学习记录",
            source="manual",
            occurred_at=utcnow(),
        )
        review = ReviewItem(
            family_id=family,
            child_id=child["id"],
            knowledge_item_id=knowledge.id,
            due_date=local_date() - timedelta(days=2),
        )
        db.add_all([record, review])
        db.flush()
        rid = review.id
        db.add_all(
            [
                KnowledgeOccurrence(
                    family_id=family,
                    knowledge_item_id=knowledge.id,
                    learning_record_id=record.id,
                    occurred_at=utcnow(),
                ),
                ReviewFeedback(family_id=family, review_item_id=rid, action="complete"),
                ReviewFeedbackRequest(
                    family_id=family,
                    review_item_id=rid,
                    action="complete",
                    idempotency_key="old-key-123",
                    result_step=1,
                    result_due_date=local_date(),
                    result_active=True,
                ),
            ]
        )
        db.commit()
        original = (review.step, review.due_date, review.active)

    prefix = f"/api/v1/children/{child['id']}"
    assert client.get(prefix + "/todos", headers=family_headers).json()["groups"] == []
    assert client.get(prefix + "/practice-materials", headers=family_headers).json()["items"] == []
    assert (
        client.get(prefix + f"/practice-materials?review_ids={rid}", headers=family_headers).json()[
            "items"
        ]
        == []
    )
    for key in (None, "old-key-123"):
        headers = {**family_headers, **({"Idempotency-Key": key} if key else {})}
        assert (
            client.post(
                f"/api/v1/reviews/{rid}/feedback", headers=headers, json={"action": "complete"}
            ).status_code
            == 404
        )

    with app.state.database.session_factory() as db:
        sid = pending(db, family, child["id"])
        with pytest.raises(ValueError, match="不能添加"):
            LearningService.confirm(
                db,
                family,
                sid,
                ConfirmSubmission(
                    proposal=proposal(
                        subject_name="数学",
                        subject_kind="learning",
                        todo_matches=[{"review_id": rid, "knowledge_name": "换气"}],
                    )
                ),
            )
        db.rollback()
        old = db.get(ReviewItem, rid)
        assert (old.step, old.due_date, old.active) == original
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 1

    response = client.post(
        "/api/v1/activity-records",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject_id,
            "occurred_at": utcnow().isoformat(),
        },
    )
    assert response.status_code == 201
    schedule = client.post(
        "/api/v1/activity-schedules",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "subject_id": subject_id,
            "weekdays": [],
        },
    )
    assert schedule.status_code == 201
    report = client.get(prefix + "/report", headers=family_headers).json()
    assert report["overview"]["review_feedback_count"] == 0
    assert report["overview"]["activity_records"] == 1
    assert sum(day["count"] for day in report["review_activity"]) == 0
    assert sum(day["pending_count"] for day in report["review_urgency"]) == 0
    dashboard = client.get(prefix + "/dashboard", headers=family_headers).json()
    assert dashboard["activity_suggestions"][0]["last_practice_days_ago"] == 0

    class CapturingProvider:
        received = None

        def analyze(self, data):
            self.received = data
            return proposal(subject_name="数学", subject_kind="learning")

    provider = CapturingProvider()
    app.state.worker.provider = provider
    with app.state.database.session_factory() as db:
        submission = LearningSubmission(
            family_id=family, child_id=child["id"], occurred_at=utcnow()
        )
        db.add(submission)
        db.flush()
        db.add(AgentJob(family_id=family, submission_id=submission.id))
        db.commit()
    assert app.state.worker.process_one()
    assert rid not in [item.review_id for item in provider.received.todo_candidates]


@pytest.mark.parametrize("other_family", [False, True])
def test_confirmation_rejects_other_child_subject(client, app, child, family_headers, other_family):
    family = family_headers["X-Family-ID"]
    headers = {"X-Family-ID": "other-family"} if other_family else family_headers
    other = client.post("/api/v1/children", headers=headers, json={"name": "另一个档案"}).json()
    subject = client.post(
        "/api/v1/subjects",
        headers=headers,
        json={
            "child_id": other["id"],
            "name": "游泳",
            "kind": "activity",
        },
    ).json()
    with app.state.database.session_factory() as db:
        sid = pending(db, family, child["id"])
    response = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={
            "subject_id": subject["id"],
            "proposal": proposal().model_dump(mode="json"),
        },
    )
    assert response.status_code == 404
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
