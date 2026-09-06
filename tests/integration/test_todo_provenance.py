"""Structured Todo provenance, stable photo order and stored recognition evidence."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from push_kids.learning.history import LearningHistory
from push_kids.persistence.models import KnowledgeItem, ReviewItem, SubmissionMedia
from push_kids.platform.time import local_date
from sqlalchemy import select

PNG = b"\x89PNG\r\n\x1a\nvalid-image-content"


def _confirmed(
    client: TestClient,
    app,
    headers: dict[str, str],
    child_id: str,
    text: str,
    *,
    days_ago: int = 4,
) -> dict:
    occurred = datetime.now(UTC) - timedelta(days=days_ago)
    submission_id = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={"child_id": child_id, "occurred_at": occurred.isoformat(), "input_text": text},
    ).json()["id"]
    assert app.state.worker.process_one() is True
    proposal = client.get(f"/api/v1/submissions/{submission_id}", headers=headers).json()[
        "proposal"
    ]
    result = client.post(
        f"/api/v1/submissions/{submission_id}/confirm", headers=headers, json={"proposal": proposal}
    )
    assert result.status_code == 200, result.text
    return {"submission_id": submission_id, "occurred_at": occurred, **result.json()}


def _todo_items(client: TestClient, headers: dict[str, str], child_id: str, day=None) -> list[dict]:
    params = {"day": day.isoformat()} if day else None
    response = client.get(f"/api/v1/children/{child_id}/todos", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return [item for group in response.json()["groups"] for item in group["items"]]


def test_todos_expose_source_submission_round_and_interval(
    client, app, family_headers, child
) -> None:
    confirmed = _confirmed(client, app, family_headers, child["id"], "数学，两位数进位加法")
    learned_on = local_date(confirmed["occurred_at"])
    items = _todo_items(client, family_headers, child["id"])
    assert items
    for item in items:
        assert item["source_submission_id"] == confirmed["submission_id"]
        assert item["source_occurred_on"] == learned_on.isoformat()
        assert item["review_round"] == 1
        # First review is due today because the material is four days old.
        assert item["interval_days"] == (local_date() - learned_on).days

    review_id = confirmed["review_item_ids"][0]
    feedback = client.post(
        f"/api/v1/reviews/{review_id}/feedback",
        headers=family_headers,
        json={"action": "complete"},
    )
    assert feedback.status_code == 200
    next_due = datetime.fromisoformat(feedback.json()["due_date"]).date()
    advanced = [
        item
        for item in _todo_items(client, family_headers, child["id"], day=next_due)
        if item["review_id"] == review_id
    ]
    assert len(advanced) == 1
    assert advanced[0]["review_round"] == 2
    assert advanced[0]["interval_days"] == (next_due - local_date()).days
    assert advanced[0]["source_submission_id"] == confirmed["submission_id"]


def test_todos_keep_history_without_source_submission(client, app, family_headers, child) -> None:
    confirmed = _confirmed(client, app, family_headers, child["id"], "语文，古诗静夜思")
    review_id = confirmed["review_item_ids"][0]
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, review_id)
        review.source_submission_id = None
        db.commit()
    items = [
        item
        for item in _todo_items(client, family_headers, child["id"])
        if item["review_id"] == review_id
    ]
    assert len(items) == 1
    assert items[0]["source_submission_id"] is None
    assert items[0]["source_occurred_on"] is None
    assert items[0]["review_round"] == 1
    assert items[0]["interval_days"] is None


def test_appended_photos_get_strictly_increasing_sort_order(
    client, app, family_headers, child
) -> None:
    fields = {
        "child_id": child["id"],
        "occurred_at": datetime.now(UTC).isoformat(),
        "defer_analysis": "true",
    }
    created = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data=fields,
        files=[("files", (f"page-{index}.png", PNG, "image/png")) for index in range(2)],
    )
    assert created.status_code == 202, created.text
    submission_id = created.json()["id"]
    for index in (3, 4):
        appended = client.post(
            f"/api/v1/submissions/{submission_id}/media",
            headers=family_headers,
            files={"file": (f"page-{index}.png", PNG, "image/png")},
        )
        assert appended.status_code == 200, appended.text
    with app.state.database.session_factory() as db:
        orders = list(
            db.scalars(
                select(SubmissionMedia.sort_order)
                .where(SubmissionMedia.submission_id == submission_id)
                .order_by(SubmissionMedia.created_at, SubmissionMedia.id)
            )
        )
        assert orders == [0, 1, 2, 3]
        detail = LearningHistory.detail(
            db, family_headers["X-Family-ID"], child["id"], submission_id
        )
    assert [item["index"] for item in detail["media"]] == [1, 2, 3, 4]


def test_detail_returns_recognition_confidence_and_evidence(
    client, app, family_headers, child
) -> None:
    confirmed = _confirmed(client, app, family_headers, child["id"], "英语单词 animal")
    family = family_headers["X-Family-ID"]
    with app.state.database.session_factory() as db:
        detail = LearningHistory.detail(db, family, child["id"], confirmed["submission_id"])
        stored = db.scalars(select(KnowledgeItem)).all()
    assert detail["knowledge"]
    for entry in detail["knowledge"]:
        assert entry["confidence"] in {"high", "medium", "low"}
        assert entry["evidence"]
        assert all("detail" in item for item in entry["evidence"])
    assert all(json.loads(item.evidence_json) for item in stored)

    with app.state.database.session_factory() as db:
        for item in db.scalars(select(KnowledgeItem)):
            item.evidence_json = "not-json"
        db.commit()
        broken = LearningHistory.detail(db, family, child["id"], confirmed["submission_id"])
    # Historical rows are untrusted input: unreadable evidence degrades, never raises.
    assert all(entry["evidence"] == [] for entry in broken["knowledge"])


def test_confirmation_keeps_first_recognition_provenance(
    client, app, family_headers, child
) -> None:
    first = _confirmed(client, app, family_headers, child["id"], "英语单词 animal")
    with app.state.database.session_factory() as db:
        original = {
            item.id: (item.confidence, item.evidence_json)
            for item in db.scalars(select(KnowledgeItem))
        }
        reviews = {
            item.knowledge_item_id: item.source_submission_id
            for item in db.scalars(select(ReviewItem))
        }
    _confirmed(client, app, family_headers, child["id"], "英语单词 animal", days_ago=3)
    with app.state.database.session_factory() as db:
        assert {
            item.id: (item.confidence, item.evidence_json)
            for item in db.scalars(select(KnowledgeItem))
        } == original
        assert {
            item.knowledge_item_id: item.source_submission_id
            for item in db.scalars(select(ReviewItem))
        } == reviews
    assert all(value == first["submission_id"] for value in reviews.values())
