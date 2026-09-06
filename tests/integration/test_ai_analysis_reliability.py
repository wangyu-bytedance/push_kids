import json
from datetime import timedelta

import pytest
from push_kids.agent_processing.context import build_analysis_input
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.learning.schemas import ConfirmSubmission
from push_kids.learning.service import LearningService
from push_kids.persistence.models import (
    AgentJob,
    Child,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select


def proposal(name="两位数进位加法"):
    return {
        "summary": "完成进位加法练习",
        "subject_name": "数学",
        "knowledge_points": [
            {
                "name": name,
                "category": "计算",
                "direct_evidence": [{"source": "parent_text", "detail": "家长记录进位加法"}],
            }
        ],
        "todo_matches": [],
    }


def draft(client, app, headers, child_id, state="pending_confirmation", body=None, text="练习"):
    response = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={
            "child_id": child_id,
            "occurred_at": utcnow().isoformat(),
            "input_text": text,
        },
    )
    assert response.status_code == 202
    key = response.json()["id"]
    with app.state.database.session_factory() as db:
        row = db.get(LearningSubmission, key)
        row.state = state
        row.proposal_json = (
            json.dumps(body or proposal()) if state == "pending_confirmation" else None
        )
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == key))
        job.state = {"pending_confirmation": "succeeded", "analyzing": "running"}.get(state, state)
        db.commit()
    return key


def confirm(client, headers, key, body=None, manual=False):
    return client.post(
        f"/api/v1/submissions/{key}/confirm",
        headers=headers,
        json={"proposal": body or proposal(), "manual_entry": manual},
    )


@pytest.mark.parametrize("step,active", [(3, True), (6, False)])
def test_repeat_learning_preserves_review_and_deduplicates_occurrence(
    client,
    app,
    child,
    family_headers,
    step,
    active,
):
    first = draft(client, app, family_headers, child["id"])
    result = confirm(client, family_headers, first).json()
    review_id = result["review_item_ids"][0]
    due = local_date() + timedelta(days=21)
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        review.step, review.active, review.due_date, review.last_feedback = (
            step,
            active,
            due,
            "complete",
        )
        db.commit()
    body = proposal()
    body["knowledge_points"] *= 3
    second = draft(client, app, family_headers, child["id"], body=body)
    assert confirm(client, family_headers, second, body).status_code == 200
    assert confirm(client, family_headers, second, body).status_code == 409
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        assert (review.step, review.active, review.due_date, review.last_feedback) == (
            step,
            active,
            due,
            "complete",
        )
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 1
        assert db.scalar(select(func.count(KnowledgeOccurrence.id))) == 2
        assert db.scalar(select(func.count(LearningRecord.id))) == 2


def test_duplicate_matches_advance_once_and_stale_proposal_cannot_advance_again(
    client,
    app,
    child,
    family_headers,
):
    first = draft(client, app, family_headers, child["id"])
    review_id = confirm(client, family_headers, first).json()["review_item_ids"][0]
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        review.due_date = local_date()
        db.commit()
        match = {
            "review_id": review_id,
            "knowledge_name": "两位数进位加法",
            "step": review.step,
            "due_date": review.due_date.isoformat(),
            "evidence": "本次练习",
        }
    body = proposal()
    body["knowledge_points"] = []
    body["todo_matches"] = [match] * 6
    keys = [draft(client, app, family_headers, child["id"], body=body) for _ in range(2)]
    first_result = confirm(client, family_headers, keys[0], body)
    assert first_result.status_code == 200
    assert first_result.json()["records"] == []
    assert len(first_result.json()["updated_reviews"]) == 1
    stale = confirm(client, family_headers, keys[1], body)
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "review_state_changed"
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        assert review.step == 1 and review.active
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 1
        assert db.scalar(select(func.count(LearningRecord.id))) == 1
        assert db.get(LearningSubmission, keys[1]).state == "pending_confirmation"


@pytest.mark.parametrize("state", ["queued", "analyzing", "failed", "pending_confirmation"])
def test_manual_confirmation_requires_no_provider_and_cancels_job(
    client,
    app,
    child,
    family_headers,
    state,
):
    key = draft(client, app, family_headers, child["id"], state)
    assert confirm(client, family_headers, key, manual=True).status_code == 200
    assert confirm(client, family_headers, key, manual=True).status_code == 409
    with app.state.database.session_factory() as db:
        record = db.scalar(select(LearningRecord).where(LearningRecord.submission_id == key))
        assert record.source == "人工录入"
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == key))
        assert job.state in {"cancelled", "succeeded"}
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 0
    assert not app.state.worker.process_one()


@pytest.mark.parametrize(
    "invalid", ["cancelled", "activity", "todo", "empty", "foreign", "ordinary"]
)
def test_manual_invalid_input_is_atomic(client, app, child, family_headers, invalid):
    state = "cancelled" if invalid == "cancelled" else "queued"
    key = draft(client, app, family_headers, child["id"], state)
    body = proposal()
    if invalid == "activity":
        body["subject_kind"] = "activity"
    elif invalid == "todo":
        body["todo_matches"] = [{"review_id": "unknown", "knowledge_name": "x"}]
    elif invalid == "empty":
        body["knowledge_points"] = [{"name": "   "}]
    headers = {"X-Family-ID": "other"} if invalid == "foreign" else family_headers
    assert confirm(client, headers, key, body, manual=invalid != "ordinary").status_code >= 400
    with app.state.database.session_factory() as db:
        assert db.get(LearningSubmission, key).state == state
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
        assert db.scalar(select(func.count(Subject.id))) == 0


@pytest.mark.parametrize("outcome", ["success", "failure"])
@pytest.mark.parametrize("action", ["manual", "cancel", "new_lease"])
def test_worker_discards_late_results(client, app, child, family_headers, outcome, action):
    key = draft(client, app, family_headers, child["id"], "queued", text="进位加法")

    class RacingProvider:
        def analyze(self, data):
            with app.state.database.session_factory() as db:
                if action == "manual":
                    LearningService.confirm(
                        db,
                        family_headers["X-Family-ID"],
                        key,
                        ConfirmSubmission(manual_entry=True, proposal=proposal()),
                    )
                elif action == "cancel":
                    LearningService.cancel(
                        db, app.state.worker.media_store, family_headers["X-Family-ID"], key
                    )
                else:
                    job = db.scalar(select(AgentJob).where(AgentJob.submission_id == key))
                    job.attempts += 1
                    job.lease_until += timedelta(minutes=1)
                    db.commit()
            if outcome == "failure":
                raise RuntimeError("synthetic failure")
            return DeterministicTestProvider().analyze(data)

    app.state.worker.provider = RacingProvider()
    assert app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        expected = {"manual": "confirmed", "cancel": "cancelled", "new_lease": "analyzing"}[action]
        assert db.get(LearningSubmission, key).state == expected
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == key))
        assert job.state == ("running" if action == "new_lease" else "cancelled")


def test_repeated_material_warns_and_never_auto_completes(client, app, child, family_headers):
    for index in range(2):
        key = draft(client, app, family_headers, child["id"], "queued", text="进位加法")
        assert app.state.worker.process_one()
        body = client.get(f"/api/v1/submissions/{key}", headers=family_headers).json()["proposal"]
        if index:
            assert any("完全相同" in message for message in body["uncertainties"])
            assert not body["todo_matches"]
            assert not body["knowledge_points"]
            assert confirm(client, family_headers, key, body).status_code == 400
        else:
            assert confirm(client, family_headers, key, body).status_code == 200
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 1
        assert db.scalar(select(func.count(LearningRecord.id))) == 1
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 0


def test_submission_view_adds_structured_groups_without_changing_confirm_payload(
    client, app, child, family_headers
):
    body = proposal("20 以内加法")
    body["knowledge_points"].extend(
        [
            {
                "name": "春",
                "category": "汉字",
                "display_kind": "hanzi",
                "direct_evidence": [{"source": "parent_text", "detail": "家长记录春"}],
            },
            {
                "name": "晓",
                "category": "汉字",
                "display_kind": "hanzi",
                "direct_evidence": [{"source": "parent_text", "detail": "家长记录晓"}],
            },
        ]
    )
    key = draft(client, app, family_headers, child["id"], body=body)

    view = client.get(f"/api/v1/submissions/{key}", headers=family_headers)

    assert view.status_code == 200
    assert view.json()["display_groups"] == [
        {"kind": "hanzi", "label": "汉字", "items": ["春", "晓"]},
        {"kind": "arithmetic", "label": "运算", "items": ["20 以内加法"]},
    ]
    assert confirm(client, family_headers, key, view.json()["proposal"]).status_code == 200


def test_existing_knowledge_reference_is_scoped_and_consistent(client, app, child, family_headers):
    first = draft(client, app, family_headers, child["id"])
    known = confirm(client, family_headers, first).json()["knowledge_item_ids"][0]
    body = proposal()
    body["knowledge_points"][0]["existing_knowledge_id"] = known
    key = draft(client, app, family_headers, child["id"], body=body)
    assert confirm(client, family_headers, key, body).status_code == 200
    other_child = client.post(
        "/api/v1/children", headers=family_headers, json={"name": "另一档案"}
    ).json()
    key = draft(client, app, family_headers, other_child["id"], body=body)
    assert confirm(client, family_headers, key, body).status_code == 400
    body["knowledge_points"][0]["name"] = "除法"
    key = draft(client, app, family_headers, child["id"], body=body)
    assert confirm(client, family_headers, key, body).status_code == 400


def test_context_balances_subjects_and_excludes_future_foreign_and_unconfirmed(
    client,
    app,
    child,
    family_headers,
):
    now = utcnow()
    with app.state.database.session_factory() as db:
        family = family_headers["X-Family-ID"]
        foreign_child = Child(family_id="other", name="foreign")
        db.add(foreign_child)
        db.flush()
        for name, count, owner, child_id in [
            ("数学", 35, family, child["id"]),
            ("语文", 1, family, child["id"]),
            ("other", 1, "other", foreign_child.id),
        ]:
            subject = Subject(family_id=owner, child_id=child_id, name=name, kind="learning")
            db.add(subject)
            db.flush()
            for index in range(count):
                row = LearningSubmission(
                    family_id=owner,
                    child_id=child_id,
                    state="confirmed",
                    occurred_at=now - timedelta(days=1, seconds=index),
                )
                db.add(row)
                db.flush()
                db.add(
                    LearningRecord(
                        family_id=owner,
                        child_id=child_id,
                        subject_id=subject.id,
                        submission_id=row.id,
                        occurred_at=row.occurred_at,
                        summary=name,
                        source="课内",
                    )
                )
            if owner == family:
                future = LearningSubmission(
                    family_id=owner,
                    child_id=child_id,
                    state="confirmed",
                    occurred_at=now + timedelta(days=1),
                )
                db.add(future)
                db.flush()
                db.add(
                    LearningRecord(
                        family_id=owner,
                        child_id=child_id,
                        subject_id=subject.id,
                        submission_id=future.id,
                        occurred_at=future.occurred_at,
                        summary="future",
                        source="课内",
                    )
                )
        current = LearningSubmission(
            family_id=family, child_id=child["id"], occurred_at=now, input_text="未确认输入"
        )
        db.add(current)
        db.flush()
        result = build_analysis_input(db, current, [])
        assert result.grade == "小学二年级" and result.occurred_at == now.isoformat()
        assert {item.subject_name for item in result.recent_learning} == {"数学", "语文"}
        assert len(result.recent_learning) == 11
        assert all(
            item.summary not in {"future", "other", "未确认输入"} for item in result.recent_learning
        )
        db.rollback()
