from datetime import UTC, datetime, timedelta

import pytest
from push_kids.learning.schemas import MediaUploadTicketRequest
from push_kids.learning.service import LearningService
from push_kids.persistence.models import (
    AgentJob,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    SubmissionMedia,
)
from push_kids.platform.context import RequestContext
from push_kids.platform.time import utcnow
from sqlalchemy import func, select


def test_empty_photo_draft_can_resume_or_cancel(client, app, child, family_headers):
    draft = client.post(
        "/api/v1/submissions/photo-drafts",
        headers={**family_headers, "Idempotency-Key": "original-photo-batch"},
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
        },
    ).json()
    assert draft["awaiting_upload"] and not draft["can_finalize_upload"]
    assert draft["upload_batch_key"] == "original-photo-batch"
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(AgentJob)) == 0
    result = client.post(f"/api/v1/submissions/{draft['id']}/cancel", headers=family_headers)
    assert result.status_code == 200
    assert result.json()["state"] == "cancelled"
    assert not result.json()["awaiting_upload"]


def test_ninth_photo_ticket_is_reused_after_upload_failure(client, app, child, family_headers):
    draft = client.post(
        "/api/v1/submissions/photo-drafts",
        headers={
            **family_headers,
            "Idempotency-Key": "original-batch-nine",
        },
        json={"child_id": child["id"], "occurred_at": utcnow().isoformat()},
    ).json()
    family = family_headers["X-Family-ID"]
    with app.state.database.session_factory() as db:
        db.add_all(
            [
                SubmissionMedia(
                    submission_id=draft["id"],
                    path=f"synthetic-{index}",
                    content_type="image/png",
                    byte_size=100,
                )
                for index in range(8)
            ]
        )
        db.commit()
        view = LearningService.get_view(db, family, draft["id"])
        context = RequestContext(
            family_id=family, subject_hmac="synthetic-hmac", openid="synthetic", app_id="synthetic"
        )
        request = MediaUploadTicketRequest(
            submission_id=draft["id"], content_type="image/png", byte_size=100
        )
        key = f"{view.upload_batch_key}-media-{view.media_count}"
        first = LearningService.issue_media_ticket(db, context, request, key, 1024, 300)
    # Simulate leaving/reopening after upload failure. No new ticket should consume a slot.
    with app.state.database.session_factory() as db:
        view = LearningService.get_view(db, family, draft["id"])
        retry = LearningService.issue_media_ticket(
            db, context, request, f"{view.upload_batch_key}-media-{view.media_count}", 1024, 300
        )
        assert retry.ticket_id == first.ticket_id


@pytest.mark.parametrize("occurred", ["2026-09-05T00:30:00+08:00", "2026-09-04T16:30:00Z"])
def test_timestamp_roundtrip_keeps_instant(client, app, child, family_headers, occurred):
    created = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": occurred,
            "input_text": "数学分数",
        },
    ).json()
    result = client.get(f"/api/v1/submissions/{created['id']}", headers=family_headers).json()
    expected = datetime(2026, 9, 4, 16, 30, tzinfo=UTC)
    assert datetime.fromisoformat(result["occurred_at"].replace("Z", "+00:00")) == expected
    assert datetime.fromisoformat(result["created_at"].replace("Z", "+00:00")).tzinfo is not None
    with app.state.database.session_factory() as db:
        stored = db.get(LearningSubmission, created["id"])
        assert stored.occurred_at == expected
    assert app.state.worker.process_one()
    draft = client.get(f"/api/v1/submissions/{created['id']}", headers=family_headers).json()
    assert (
        client.post(
            f"/api/v1/submissions/{created['id']}/confirm",
            headers=family_headers,
            json={"proposal": draft["proposal"]},
        ).status_code
        == 200
    )
    history = client.get(f"/api/v1/children/{child['id']}/history", headers=family_headers).json()
    assert datetime.fromisoformat(history["items"][0]["occurred_at"]) == expected
    calendar = client.get(
        f"/api/v1/children/{child['id']}/calendar?month=2026-09", headers=family_headers
    ).json()
    assert calendar["days"][0]["day"] == "2026-09-05"


def test_pending_filter_precedes_pagination(client, app, child, family_headers):
    with app.state.database.session_factory() as db:
        for state, count, age in [("confirmed", 100, 0), ("pending_confirmation", 101, 20)]:
            db.add_all(
                [
                    LearningSubmission(
                        family_id=family_headers["X-Family-ID"],
                        child_id=child["id"],
                        occurred_at=utcnow(),
                        created_at=utcnow() - timedelta(days=age),
                        state=state,
                    )
                    for _ in range(count)
                ]
            )
        db.add(
            LearningSubmission(
                family_id="other-family",
                child_id=child["id"],
                occurred_at=utcnow(),
                state="pending_confirmation",
            )
        )
        db.commit()
    url = f"/api/v1/submissions?child_id={child['id']}&pending_only=true"
    first = client.get(url, headers=family_headers).json()
    second = client.get(url + "&offset=100", headers=family_headers).json()
    assert len(first) == 100 and len(second) == 1
    assert len({row["id"] for row in first + second}) == 101
    assert {row["state"] for row in first + second} == {"pending_confirmation"}
    assert client.get(url + "&offset=-1", headers=family_headers).status_code == 422


def test_closed_review_rejects_new_feedback_but_replays_success(client, app, child, family_headers):
    sid = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
            "input_text": "数学分数",
        },
    ).json()["id"]
    app.state.worker.process_one()
    draft = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()
    rid = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={"proposal": draft["proposal"]},
    ).json()["review_item_ids"][0]
    with app.state.database.session_factory() as db:
        db.get(ReviewItem, rid).step = 5
        db.commit()
    url = f"/api/v1/reviews/{rid}/feedback"
    headers = {**family_headers, "Idempotency-Key": "last-complete-123"}
    result = client.post(url, headers=headers, json={"action": "complete"})
    assert result.status_code == 200 and not result.json()["active"]
    assert client.post(url, headers=headers, json={"action": "complete"}).json() == result.json()
    for action in ["complete", "defer", "partial", "reinforce"]:
        assert client.post(url, headers=family_headers, json={"action": action}).status_code == 409
    with app.state.database.session_factory() as db:
        assert not db.get(ReviewItem, rid).active
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 1
