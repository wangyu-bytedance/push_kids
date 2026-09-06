from __future__ import annotations

from datetime import date, time

from fastapi.testclient import TestClient
from push_kids.persistence.models import (
    ActivityRecord,
    ActivitySchedule,
    AgentJob,
    CalendarEvent,
    CalendarEventRequest,
    Child,
    DeletionRequest,
    Family,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    MediaObject,
    ReviewFeedback,
    ReviewFeedbackRequest,
    ReviewItem,
    Subject,
    SubmissionMedia,
    SubmissionRequest,
    TravelArrangement,
    TravelArrangementRequest,
)
from push_kids.platform.time import utcnow
from sqlalchemy import select


def _actor(name: str, key: str | None = None) -> dict[str, str]:
    headers = {"X-Debug-Actor": name}
    if key:
        headers["Idempotency-Key"] = key
    return headers


def _family(client: TestClient, actor: str, name: str = "小芽的家") -> dict:
    response = client.post(
        "/api/v1/families",
        headers=_actor(actor, f"family-{actor}"),
        json={"display_name": name, "relationship_label": "家长"},
    )
    assert response.status_code == 201
    assert response.json()["children"] == []
    return response.json()


def _child(client: TestClient, actor: str, name: str) -> dict:
    response = client.post(
        "/api/v1/children",
        headers=_actor(actor),
        json={"name": name, "daily_budget_minutes": 15, "subject_names": ["语文"]},
    )
    assert response.status_code == 201
    return response.json()


def _seed_child_owned_rows(app, family_id: str, child_id: str) -> tuple[dict, object]:
    media_path = app.state.settings.media_root / "fixture" / "child-photo.jpg"
    media_path.parent.mkdir(parents=True, exist_ok=True)
    media_path.write_bytes(b"child-private-media")
    with app.state.database.session_factory() as db:
        subject = db.scalar(select(Subject).where(Subject.child_id == child_id))
        assert subject is not None
        submission = LearningSubmission(
            family_id=family_id,
            child_id=child_id,
            occurred_at=utcnow(),
            source="manual",
            state="confirmed",
        )
        db.add(submission)
        db.flush()
        media = MediaObject(
            family_id=family_id,
            submission_id=submission.id,
            backend="local",
            storage_path=str(media_path),
            storage_ref=str(media_path),
            uploader_subject_hmac="fixture",
            idempotency_key="fixture-media",
            state="claimed",
            expires_at=utcnow(),
        )
        db.add(media)
        db.flush()
        submission_media = SubmissionMedia(
            submission_id=submission.id,
            media_object_id=media.id,
            path=str(media_path),
            content_type="image/jpeg",
            byte_size=10,
        )
        job = AgentJob(family_id=family_id, submission_id=submission.id, state="succeeded")
        submission_request = SubmissionRequest(
            family_id=family_id,
            idempotency_key="fixture-submission",
            request_fingerprint="a" * 64,
            submission_id=submission.id,
        )
        record = LearningRecord(
            family_id=family_id,
            child_id=child_id,
            subject_id=subject.id,
            submission_id=submission.id,
            occurred_at=utcnow(),
            summary="学习记录",
            source="manual",
        )
        knowledge = KnowledgeItem(
            family_id=family_id,
            child_id=child_id,
            subject_id=subject.id,
            name="字词",
            normalized_name="字词",
        )
        db.add_all([submission_media, job, submission_request, record, knowledge])
        db.flush()
        occurrence = KnowledgeOccurrence(
            family_id=family_id,
            knowledge_item_id=knowledge.id,
            learning_record_id=record.id,
            occurred_at=utcnow(),
        )
        review = ReviewItem(
            family_id=family_id,
            child_id=child_id,
            knowledge_item_id=knowledge.id,
            source_submission_id=submission.id,
            due_date=date.today(),
        )
        schedule = ActivitySchedule(family_id=family_id, child_id=child_id, subject_id=subject.id)
        activity = ActivityRecord(
            family_id=family_id,
            child_id=child_id,
            subject_id=subject.id,
            occurred_at=utcnow(),
        )
        event = CalendarEvent(
            family_id=family_id,
            child_id=child_id,
            name="家长会",
            event_date=date.today(),
            start_time=time(18),
            end_time=time(19),
        )
        travel = TravelArrangement(
            family_id=family_id,
            child_id=child_id,
            name="上学",
            weekdays="0,1",
            start_time=time(7, 30),
            end_time=time(8),
        )
        db.add_all([occurrence, review, schedule, activity, event, travel])
        db.flush()
        feedback = ReviewFeedback(
            family_id=family_id, review_item_id=review.id, action="remembered"
        )
        feedback_request = ReviewFeedbackRequest(
            family_id=family_id,
            idempotency_key="fixture-feedback",
            review_item_id=review.id,
            action="remembered",
            result_step=1,
            result_due_date=date.today(),
            result_active=True,
        )
        event_request = CalendarEventRequest(
            family_id=family_id,
            idempotency_key="fixture-event",
            request_fingerprint="b" * 64,
            event_id=event.id,
        )
        travel_request = TravelArrangementRequest(
            family_id=family_id,
            idempotency_key="fixture-travel",
            request_fingerprint="c" * 64,
            arrangement_id=travel.id,
        )
        db.add_all([feedback, feedback_request, event_request, travel_request])
        db.commit()
        owned = {
            type(item): item.id
            for item in (
                submission,
                media,
                submission_media,
                job,
                submission_request,
                record,
                knowledge,
                occurrence,
                review,
                feedback,
                feedback_request,
                schedule,
                activity,
                event,
                event_request,
                travel,
                travel_request,
            )
        }
    return owned, media_path


def test_child_deletion_is_idempotent_freezes_writes_and_purges_owned_rows(
    client: TestClient, app
) -> None:
    actor = "delete-child-manager"
    _family(client, actor)
    child = _child(client, actor, "小芽")
    sibling = _child(client, actor, "小树")
    family_id = client.get("/api/v1/me", headers=_actor(actor)).json()["family"]["id"]
    owned_ids, media_path = _seed_child_owned_rows(app, family_id, child["id"])

    wrong = client.post(
        f"/api/v1/children/{child['id']}/deletion-requests",
        headers=_actor(actor, "delete-child-wrong"),
        json={"confirmation_name": "别的名字"},
    )
    assert wrong.status_code == 409

    accepted = client.post(
        f"/api/v1/children/{child['id']}/deletion-requests",
        headers=_actor(actor, "delete-child-001"),
        json={"confirmation_name": "小芽"},
    )
    assert accepted.status_code == 202
    replay = client.post(
        f"/api/v1/children/{child['id']}/deletion-requests",
        headers=_actor(actor, "delete-child-001"),
        json={"confirmation_name": "小芽"},
    )
    assert replay.status_code == 202
    assert replay.json()["id"] == accepted.json()["id"]

    visible = client.get("/api/v1/children?include_archived=true", headers=_actor(actor))
    assert [item["id"] for item in visible.json()] == [sibling["id"]]
    blocked = client.post(
        "/api/v1/subjects",
        headers=_actor(actor),
        json={"child_id": child["id"], "name": "数学", "kind": "learning"},
    )
    assert blocked.status_code == 409

    assert app.state.deletion_worker.process_one() is True
    assert not media_path.exists()
    status = client.get(f"/api/v1/deletion-requests/{accepted.json()['id']}", headers=_actor(actor))
    assert status.status_code == 200
    assert status.json()["state"] == "succeeded"

    with app.state.database.session_factory() as db:
        assert db.get(Child, child["id"]) is None
        assert db.get(Child, sibling["id"]) is not None
        assert db.scalar(select(Subject).where(Subject.child_id == child["id"])) is None
        for model, item_id in owned_ids.items():
            assert db.get(model, item_id) is None, model.__name__
        tombstone = db.get(DeletionRequest, accepted.json()["id"])
        assert tombstone is not None
        assert tombstone.family_id is None
        assert tombstone.target_id is None
        assert tombstone.expires_at is not None


def test_family_deletion_requires_sole_manager_and_unbinds_actor(client: TestClient, app) -> None:
    manager = "delete-family-manager"
    created = _family(client, manager, "星星之家")
    _child(client, manager, "星星")
    invite = client.post(
        "/api/v1/families/current/invites",
        headers=_actor(manager, "delete-family-invite"),
        json={},
    ).json()
    joined = client.post(
        "/api/v1/family-requests",
        headers=_actor("delete-family-relative", "delete-family-join"),
        json={"token": invite["token"], "relationship_label": "家人"},
    ).json()
    client.post(
        f"/api/v1/family-requests/{joined['id']}/approve",
        headers=_actor(manager, "delete-family-approve"),
        json={"role": "viewer"},
    )

    refused = client.post(
        "/api/v1/families/current/deletion-requests",
        headers=_actor(manager, "delete-family-refused"),
        json={"confirmation_name": "星星之家"},
    )
    assert refused.status_code == 409

    member = next(
        item
        for item in client.get("/api/v1/families/current/members", headers=_actor(manager)).json()
        if not item["is_self"]
    )
    client.delete(f"/api/v1/families/current/members/{member['id']}", headers=_actor(manager))
    accepted = client.post(
        "/api/v1/families/current/deletion-requests",
        headers=_actor(manager, "delete-family-accepted"),
        json={"confirmation_name": "星星之家"},
    )
    assert accepted.status_code == 202
    assert client.get("/api/v1/children", headers=_actor(manager)).status_code == 403

    assert app.state.deletion_worker.process_one() is True
    bootstrap = client.get("/api/v1/me", headers=_actor(manager))
    assert bootstrap.status_code == 200
    assert bootstrap.json()["state"] == "unbound"
    assert bootstrap.json()["children"] == []
    with app.state.database.session_factory() as db:
        assert db.get(Family, created["family"]["id"]) is None


def test_deletion_status_is_private_to_the_verified_actor(client: TestClient) -> None:
    actor = "delete-private-manager"
    _family(client, actor)
    child = _child(client, actor, "小禾")
    accepted = client.post(
        f"/api/v1/children/{child['id']}/deletion-requests",
        headers=_actor(actor, "delete-private-request"),
        json={"confirmation_name": "小禾"},
    ).json()

    hidden = client.get(
        f"/api/v1/deletion-requests/{accepted['id']}", headers=_actor("unrelated-actor")
    )
    assert hidden.status_code == 404


def test_failed_cleanup_is_durable_and_can_be_retried(client: TestClient, app, monkeypatch) -> None:
    actor = "delete-retry-manager"
    _family(client, actor)
    child = _child(client, actor, "小松")
    accepted = client.post(
        f"/api/v1/children/{child['id']}/deletion-requests",
        headers=_actor(actor, "delete-retry-request"),
        json={"confirmation_name": "小松"},
    ).json()
    with app.state.database.session_factory() as db:
        item = db.get(DeletionRequest, accepted["id"])
        assert item is not None
        item.max_attempts = 1
        db.commit()

    original = app.state.deletion_worker._delete_media

    def unavailable(*_args) -> None:
        raise RuntimeError("storage unavailable")

    monkeypatch.setattr(app.state.deletion_worker, "_delete_media", unavailable)
    assert app.state.deletion_worker.process_one() is True
    status = client.get(f"/api/v1/deletion-requests/{accepted['id']}", headers=_actor(actor)).json()
    assert status["state"] == "failed"
    assert status["retryable"] is True

    monkeypatch.setattr(app.state.deletion_worker, "_delete_media", original)
    retried = client.post(
        f"/api/v1/deletion-requests/{accepted['id']}/retry", headers=_actor(actor)
    )
    assert retried.status_code == 200
    assert retried.json()["state"] == "queued"
    assert app.state.deletion_worker.process_one() is True
    assert (
        client.get(f"/api/v1/deletion-requests/{accepted['id']}", headers=_actor(actor)).json()[
            "state"
        ]
        == "succeeded"
    )
