from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from push_kids.persistence.models import (
    AgentJob,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewFeedbackRequest,
)
from sqlalchemy import func, select


def _submit_and_process(
    client: TestClient, app, headers: dict[str, str], child_id: str, text: str
) -> dict:
    occurred = datetime.now(UTC) - timedelta(days=4)
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


def test_confirmation_is_required_and_duplicate_knowledge_keeps_occurrences(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(client, app, family_headers, child["id"], "英语单词 animal")
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
    _confirm(client, family_headers, first)
    second = _submit_and_process(client, app, family_headers, child["id"], "英语单词 animal")
    _confirm(client, family_headers, second)
    with app.state.database.session_factory() as db:
        knowledge_count = db.scalar(select(func.count(KnowledgeItem.id)))
        occurrence_count = db.scalar(select(func.count(KnowledgeOccurrence.id)))
    assert knowledge_count == 1
    assert occurrence_count == 2


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


def test_ai_todo_match_only_completes_after_parent_confirmation(
    client, app, family_headers, child
) -> None:
    first = _submit_and_process(client, app, family_headers, child["id"], "数学，进位加法")
    _confirm(client, family_headers, first)
    second = _submit_and_process(client, app, family_headers, child["id"], "进位加法")
    matches = second["proposal"]["todo_matches"]
    assert [item["knowledge_name"] for item in matches] == ["进位加法"]
    before = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    assert before.json()["todo_count"] == 2
    _confirm(client, family_headers, second)
    after = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
    assert after.json()["todo_count"] == 1


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
