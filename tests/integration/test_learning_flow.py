from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from push_kids.persistence.models import (
    AgentJob,
    DailyReviewPlanItem,
    KnowledgeItem,
    KnowledgeOccurrence,
    KnowledgeSearchTerm,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewFeedbackBatchRequest,
    ReviewFeedbackRequest,
    ReviewItem,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select


def _submit_and_process(
    client: TestClient,
    app,
    headers: dict[str, str],
    child_id: str,
    text: str,
    *,
    days_ago: int = 4,
) -> dict:
    occurred = datetime.now(UTC) - timedelta(days=days_ago)
    response = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={"child_id": child_id, "occurred_at": occurred.isoformat(), "input_text": text},
    )
    assert response.status_code == 202
    submission_id = response.json()["id"]
    assert response.json()["state"] == "queued"
    assert app.state.worker.process_one() is True
    proposal = client.get(f"/api/v1/submissions/{submission_id}", headers=headers)
    assert proposal.status_code == 200
    assert proposal.json()["state"] == "pending_confirmation"
    return proposal.json()


def _confirm(client: TestClient, headers: dict[str, str], submission: dict) -> dict:
    response = client.post(
        f"/api/v1/submissions/{submission['id']}/confirm",
        headers=headers,
        json={"proposal": submission["proposal"]},
    )
    assert response.status_code == 200
    return response.json()


def test_async_confirmation_flow_and_family_isolation(client, app, family_headers, child) -> None:
    submission = _submit_and_process(
        client, app, family_headers, child["id"], "数学，两位数进位加法"
    )
    denied = client.get(
        f"/api/v1/submissions/{submission['id']}", headers={"X-Family-ID": "family-other"}
    )
    assert denied.status_code == 404
    result = _confirm(client, family_headers, submission)
    assert len(result["knowledge_item_ids"]) == 2
    dashboard = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["todo_count"] == 2
    assert dashboard.json()["pending_confirmation_count"] == 0


def test_ai_generation_omits_same_day_duplicate_knowledge(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(client, app, family_headers, child["id"], "英语单词 animal")
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
    _confirm(client, family_headers, first)
    response = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": (datetime.now(UTC) - timedelta(days=4)).isoformat(),
            "input_text": "英语单词 animal",
        },
    )
    second_id = response.json()["id"]
    for _ in range(3):
        assert app.state.worker.process_one() is True
        with app.state.database.session_factory() as db:
            job = db.scalar(select(AgentJob).where(AgentJob.submission_id == second_id))
            job.available_at = utcnow()
            db.commit()
    second = client.get(f"/api/v1/submissions/{second_id}", headers=family_headers).json()
    assert second["state"] == "failed"
    assert second["proposal"] is None
    with app.state.database.session_factory() as db:
        knowledge_count = db.scalar(select(func.count(KnowledgeItem.id)))
        occurrence_count = db.scalar(select(func.count(KnowledgeOccurrence.id)))
    assert knowledge_count == 1
    assert occurrence_count == 1


def test_today_review_classification_updates_review_and_plan_after_confirmation(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(
        client, app, family_headers, child["id"], "数学，进位加法", days_ago=4
    )
    confirmed = _confirm(client, family_headers, first)
    dashboard = client.get(
        f"/api/v1/children/{child['id']}/dashboard", headers=family_headers
    ).json()
    planned = [
        item
        for session in dashboard["review_selection"]["sessions"]
        for item in session["items"]
        if item["knowledge_name"] == "进位加法"
    ]
    assert len(planned) == 1

    second = _submit_and_process(
        client, app, family_headers, child["id"], "今天复习进位加法", days_ago=0
    )
    assert second["proposal"]["todo_matches"][0]["match_kind"] == "today_review"
    review_id = planned[0]["review_id"]
    with app.state.database.session_factory() as db:
        before = db.get(ReviewItem, review_id)
        assert before.review_count == 0 and before.last_reviewed_on is None
    _confirm(client, family_headers, second)
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        plan_item = db.scalar(
            select(DailyReviewPlanItem).where(DailyReviewPlanItem.review_item_id == review_id)
        )
        assert review.review_count == 1
        assert review.last_reviewed_on == local_date()
        assert review.due_date > local_date()
        assert review.policy_revision == "curve_heat_v1"
        assert plan_item.state == "complete"
        assert db.scalar(select(func.count(KnowledgeItem.id))) == len(
            confirmed["knowledge_item_ids"]
        )


def test_plan_outside_history_review_uses_search_tool_and_does_not_duplicate_knowledge(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(
        client, app, family_headers, child["id"], "英语单词 animal", days_ago=0
    )
    confirmed = _confirm(client, family_headers, first)
    knowledge_id = next(
        item_id
        for item_id in confirmed["knowledge_item_ids"]
        if _knowledge_name(app, item_id) == "英语单词 animal"
    )
    with app.state.database.session_factory() as db:
        before_count = int(db.scalar(select(func.count(KnowledgeItem.id))) or 0)
        assert db.scalar(
            select(func.count(KnowledgeSearchTerm.id)).where(
                KnowledgeSearchTerm.knowledge_item_id == knowledge_id
            )
        )

    second = _submit_and_process(
        client,
        app,
        family_headers,
        child["id"],
        "今天复习英语单词 animal",
        days_ago=0,
    )
    match = next(
        item for item in second["proposal"]["todo_matches"] if item["knowledge_id"] == knowledge_id
    )
    assert match["match_kind"] == "history_item"
    _confirm(client, family_headers, second)
    with app.state.database.session_factory() as db:
        review = db.scalar(select(ReviewItem).where(ReviewItem.knowledge_item_id == knowledge_id))
        assert int(db.scalar(select(func.count(KnowledgeItem.id))) or 0) == before_count
        assert review.review_count == 1
        assert review.last_reviewed_on == local_date()


def _knowledge_name(app, knowledge_id: str) -> str:
    with app.state.database.session_factory() as db:
        return str(db.get(KnowledgeItem, knowledge_id).name)


def test_review_feedback_updates_dashboard(client, app, family_headers, child) -> None:
    submission = _submit_and_process(client, app, family_headers, child["id"], "语文，古诗静夜思")
    confirmed = _confirm(client, family_headers, submission)
    review_id = confirmed["review_item_ids"][0]
    response = client.post(
        f"/api/v1/reviews/{review_id}/feedback",
        headers=family_headers,
        json={"action": "reinforce"},
    )
    assert response.status_code == 200
    assert response.json()["action"] == "reinforce"


def test_review_feedback_retry_is_idempotent(client, app, family_headers, child) -> None:
    submission = _submit_and_process(client, app, family_headers, child["id"], "语文，古诗静夜思")
    review_id = _confirm(client, family_headers, submission)["review_item_ids"][0]
    headers = {**family_headers, "Idempotency-Key": "feedback-stable-retry-001"}
    first = client.post(
        f"/api/v1/reviews/{review_id}/feedback", headers=headers, json={"action": "complete"}
    )
    second = client.post(
        f"/api/v1/reviews/{review_id}/feedback", headers=headers, json={"action": "complete"}
    )
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 1
        assert db.scalar(select(func.count(ReviewFeedbackRequest.id))) == 1
    mismatch = client.post(
        f"/api/v1/reviews/{review_id}/feedback", headers=headers, json={"action": "reinforce"}
    )
    assert mismatch.status_code == 409


def test_daily_selection_is_bounded_stable_and_batch_feedback_does_not_refill(
    client, app, family_headers, child
) -> None:
    submission = _submit_and_process(
        client,
        app,
        family_headers,
        child["id"],
        "数学，知识一，知识二，知识三，知识四，知识五",
    )
    _confirm(client, family_headers, submission)

    first = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    repeated = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    selection = first.json()["review_selection"]
    assert selection == repeated.json()["review_selection"]
    assert selection["selected_count"] == 5
    assert selection["selected_minutes"] <= child["daily_budget_minutes"]
    assert len(selection["sessions"]) == 1
    selected_ids = [item["review_id"] for item in selection["sessions"][0]["items"]]

    batch_headers = {**family_headers, "Idempotency-Key": "daily-batch-20260913-001"}
    payload = {
        "child_id": child["id"],
        "items": [{"review_id": review_id, "action": "complete"} for review_id in selected_ids[:2]],
    }
    batch = client.post("/api/v1/review-feedback-batches", headers=batch_headers, json=payload)
    replay = client.post("/api/v1/review-feedback-batches", headers=batch_headers, json=payload)
    assert batch.status_code == replay.status_code == 200
    assert batch.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert replay.json()["items"] == batch.json()["items"]

    refreshed = client.get(
        f"/api/v1/children/{child['id']}/dashboard", headers=family_headers
    ).json()["review_selection"]
    remaining_ids = [
        item["review_id"] for session in refreshed["sessions"] for item in session["items"]
    ]
    assert refreshed["today_feedback_count"] == 2
    assert remaining_ids == selected_ids[2:]
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 2
        assert db.scalar(select(func.count(ReviewFeedbackBatchRequest.id))) == 1

    mismatch = client.post(
        "/api/v1/review-feedback-batches",
        headers=batch_headers,
        json={
            "child_id": child["id"],
            "items": [{"review_id": selected_ids[0], "action": "reinforce"}],
        },
    )
    assert mismatch.status_code == 409


def test_batch_feedback_is_family_scoped_and_rolls_back_all_items_on_conflict(
    client, app, family_headers, child
) -> None:
    submission = _submit_and_process(
        client,
        app,
        family_headers,
        child["id"],
        "数学，知识甲，知识乙",
    )
    review_ids = _confirm(client, family_headers, submission)["review_item_ids"]
    with app.state.database.session_factory() as db:
        db.get(ReviewItem, review_ids[1]).due_date = local_date() + timedelta(days=1)
        db.commit()
    payload = {
        "child_id": child["id"],
        "items": [
            {"review_id": review_ids[0], "action": "complete"},
            {"review_id": review_ids[1], "action": "complete"},
        ],
    }
    headers = {**family_headers, "Idempotency-Key": "atomic-conflict-batch-001"}

    conflict = client.post("/api/v1/review-feedback-batches", headers=headers, json=payload)
    denied = client.post(
        "/api/v1/review-feedback-batches",
        headers={"X-Family-ID": "family-other", "Idempotency-Key": "foreign-batch-001"},
        json=payload,
    )

    assert conflict.status_code == 409
    assert denied.status_code == 404
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(ReviewFeedback.id))) == 0
        assert db.get(ReviewItem, review_ids[0]).step == 0


def test_ai_todo_match_only_completes_after_parent_confirmation(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(
        client, app, family_headers, child["id"], "数学，进位加法", days_ago=0
    )
    confirmed = _confirm(client, family_headers, first)
    with app.state.database.session_factory() as db:
        for review_id in confirmed["review_item_ids"]:
            review = db.get(ReviewItem, review_id)
            knowledge = db.get(KnowledgeItem, review.knowledge_item_id)
            if knowledge.name == "进位加法":
                review.due_date = local_date()
        db.commit()
    second = _submit_and_process(
        client, app, family_headers, child["id"], "今天复习进位加法", days_ago=0
    )
    matches = second["proposal"]["todo_matches"]
    assert [item["knowledge_name"] for item in matches] == ["进位加法"]
    before = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    assert before.json()["todo_count"] == 1
    result = _confirm(client, family_headers, second)
    assert result["records"] == []
    assert len(result["updated_reviews"]) == 1
    after = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    assert after.json()["todo_count"] == 0


def test_practice_materials_are_limited_to_selected_confirmed_reviews(
    client, app, family_headers, child
) -> None:
    submission = _submit_and_process(
        client, app, family_headers, child["id"], "数学，进位加法，退位减法"
    )
    confirmed = _confirm(client, family_headers, submission)
    selected = confirmed["review_item_ids"][0]
    result = client.get(
        f"/api/v1/children/{child['id']}/practice-materials",
        headers=family_headers,
        params={"review_ids": selected},
    )
    assert result.status_code == 200
    assert len(result.json()["items"]) == 1
    assert result.json()["items"][0]["knowledge_name"] in {"数学", "进位加法", "退位减法"}
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/practice-materials",
            headers={"X-Family-ID": "family-other"},
            params={"review_ids": selected},
        ).status_code
        == 404
    )


def test_photo_upload_and_invalid_media(client, app, family_headers, child) -> None:
    fields = {"child_id": child["id"], "occurred_at": datetime.now(UTC).isoformat()}
    invalid = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", ("note.txt", b"not an image", "text/plain"))],
    )
    assert invalid.status_code == 400
    spoofed = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", ("fake.jpg", b"plain text", "image/jpeg"))],
    )
    assert spoofed.status_code == 400
    assert spoofed.json()["error"]["message"] == "图片内容与格式不匹配"
    png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    too_many = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", (f"work-{index}.png", png, "image/png")) for index in range(10)],
    )
    assert too_many.status_code == 400
    assert too_many.json()["error"]["message"] == "一次最多上传 9 张图片"
    valid = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", ("work.png", png, "image/png"))],
    )
    assert valid.status_code == 202
    assert valid.json()["media_count"] == 1
    app.state.worker.process_one()
    detail = client.get(f"/api/v1/submissions/{valid.json()['id']}", headers=family_headers)
    assert detail.json()["state"] == "pending_confirmation"


def test_deferred_photo_batch_creates_one_job_only_after_finalize(
    client, app, family_headers, child
) -> None:
    fields = {
        "child_id": child["id"],
        "occurred_at": datetime.now(UTC).isoformat(),
        "defer_analysis": "true",
    }
    png = b"\x89PNG\r\n\x1a\nvalid-image-content"
    first = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", ("page-1.png", png, "image/png"))],
    )
    assert first.status_code == 202
    submission_id = first.json()["id"]
    assert first.json()["media_count"] == 1
    assert first.json()["can_finalize_upload"] is True
    assert app.state.worker.process_one() is False
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(AgentJob.id))) == 0

    second = client.post(
        f"/api/v1/submissions/{submission_id}/media",
        headers=family_headers,
        files={"file": ("page-2.png", png, "image/png")},
    )
    assert second.status_code == 200
    assert second.json()["media_count"] == 2
    assert (
        client.post(
            f"/api/v1/submissions/{submission_id}/media",
            headers={"X-Family-ID": "family-other"},
            files={"file": ("page-3.png", png, "image/png")},
        ).status_code
        == 404
    )
    finalized = client.post(f"/api/v1/submissions/{submission_id}/finalize", headers=family_headers)
    assert finalized.status_code == 200
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(AgentJob.id))) == 1
    assert app.state.worker.process_one() is True
    detail = client.get(f"/api/v1/submissions/{submission_id}", headers=family_headers)
    assert detail.json()["state"] == "pending_confirmation"
    assert detail.json()["media_count"] == 2


def test_submission_retry_key_is_idempotent_and_rejects_mismatched_payload(
    client, app, family_headers, child
) -> None:
    headers = {**family_headers, "Idempotency-Key": "manual-stable-retry-001"}
    occurred_at = datetime.now(UTC).isoformat()
    payload = {
        "child_id": child["id"],
        "occurred_at": occurred_at,
        "input_text": "数学，进位加法",
    }
    first = client.post("/api/v1/submissions", headers=headers, json=payload)
    second = client.post("/api/v1/submissions", headers=headers, json=payload)
    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(LearningSubmission.id))) == 1
        assert db.scalar(select(func.count(AgentJob.id))) == 1

    mismatch = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={**payload, "input_text": "英语单词 animal"},
    )
    assert mismatch.status_code == 409
    assert mismatch.json()["error"]["message"] == "此提交标识已用于不同内容，请重新提交"


def test_photo_retry_key_does_not_duplicate_media(client, app, family_headers, child) -> None:
    headers = {**family_headers, "Idempotency-Key": "photo-stable-retry-001"}
    fields = {"child_id": child["id"], "occurred_at": datetime.now(UTC).isoformat()}
    png = b"\x89PNG\r\n\x1a\nvalid-image-content"
    first = client.post(
        "/api/v1/submissions/upload",
        headers=headers,
        data=fields,
        files=[("files", ("work.png", png, "image/png"))],
    )
    second = client.post(
        "/api/v1/submissions/upload",
        headers=headers,
        data=fields,
        files=[("files", ("work.png", png, "image/png"))],
    )
    assert first.status_code == second.status_code == 202
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["media_count"] == second.json()["media_count"] == 1
