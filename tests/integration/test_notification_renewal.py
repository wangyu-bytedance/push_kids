"""FEAT-011 real HTTP/feedback transactions, never a real WeChat call."""

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest
from push_kids.persistence.models import (
    FamilyMember,
    KnowledgeItem,
    NotificationGrantAttempt,
    NotificationRenewalPreference,
    NotificationRenewalState,
    NotificationSubscription,
    ReviewItem,
    ReviewMemberCompletionReceipt,
    Subject,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select

from tests.integration.test_notification_channel import _actor, _create_family, _grant, _join


@pytest.fixture
def app(notification_app):
    return notification_app


@pytest.fixture
def family(client):
    return _create_family(client)


def read(client, actor="parent-a"):
    response = client.get("/api/v1/notifications/renewal", headers=_actor(actor))
    assert response.status_code == 200, response.text
    return response.json()


def prepare(
    client,
    *,
    mode="manual",
    types=None,
    remembered=None,
    version=None,
    key=None,
    actor="parent-a",
    main=True,
):
    response = client.post(
        "/api/v1/notifications/grant-attempts",
        headers={**_actor(actor), "Idempotency-Key": key or str(uuid4())},
        json={
            "mode": mode,
            "types": types or ["review_digest"],
            "expected_version": read(client, actor)["version"] if version is None else version,
            "main_switch": main,
            "remembered": remembered or {},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["attempt"]


def result(client, attempt, decision="accept", *, enable=False, actor="parent-a"):
    return client.post(
        f"/api/v1/notifications/grant-attempts/{attempt['attempt_id']}/result",
        headers=_actor(actor),
        json={
            "results": [
                {"type": entry["type"], "decision": decision} for entry in attempt["bindings"]
            ],
            "enable_renewal": enable,
        },
    )


def choice(client, value, version=None, key=None):
    return client.patch(
        "/api/v1/notifications/renewal",
        headers={**_actor("parent-a"), "Idempotency-Key": key or str(uuid4())},
        json={
            "choice": value,
            "expected_version": read(client)["version"] if version is None else version,
        },
    )


def spend(app):
    # Consumption itself has separate dispatcher regression tests.
    with app.state.database.session_factory() as db:
        for row in db.scalars(select(NotificationSubscription)):
            row.remaining_quota = 0
            row.status = "expired"
        db.commit()


def reviews(app, family, count):
    child_id = family["children"][0]["id"]
    with app.state.database.session_factory() as db:
        subject = db.scalar(
            select(Subject).where(Subject.child_id == child_id, Subject.kind == "learning")
        )
        if subject is None:
            subject = Subject(
                family_id=family["family"]["id"], child_id=child_id, name="数学", kind="learning"
            )
            db.add(subject)
            db.flush()
        ids = []
        for _ in range(count):
            name = str(uuid4())
            item = KnowledgeItem(
                family_id=family["family"]["id"],
                child_id=child_id,
                subject_id=subject.id,
                name=name,
                normalized_name=name,
            )
            db.add(item)
            db.flush()
            review = ReviewItem(
                family_id=family["family"]["id"],
                child_id=child_id,
                knowledge_item_id=item.id,
                due_date=local_date(),
            )
            db.add(review)
            db.flush()
            ids.append(str(review.id))
        db.commit()
        return ids


def complete(client, rid, key=None, action="complete", actor="parent-a"):
    return client.post(
        f"/api/v1/reviews/{rid}/feedback",
        headers={**_actor(actor), "Idempotency-Key": key or str(uuid4())},
        json={"action": action},
    )


def initialize(client, app):
    assert result(client, prepare(client)).status_code == 200
    spend(app)
    assert choice(client, "enabled").status_code == 200


def test_grant_registration_replay_conflict_and_no_quota_hoarding(client, app, family):
    attempt = prepare(client)
    assert read(client)["settings"]["preferences"][-1]["remaining_quota"] == 0
    first = result(client, attempt)
    assert first.status_code == 200, first.text
    assert result(client, attempt).json() == first.json()
    assert result(client, attempt, "reject").status_code == 409
    assert read(client)["settings"]["preferences"][-1]["remaining_quota"] == 1
    assert prepare(client) is None
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(NotificationGrantAttempt.id))) == 1


def test_ten_successful_own_reviews_then_next_click_per_type(client, app, family):
    initialize(client, app)
    ids = reviews(app, family, 11)
    assert prepare(client, mode="auto") is None
    for index, rid in enumerate(ids[:10]):
        assert complete(client, rid).status_code == 200
        assert read(client)["completion_cursor"] == index + 1
        if index < 9:
            assert prepare(client, mode="auto") is None
    attempt = prepare(client, mode="auto")
    assert attempt
    assert complete(client, ids[10]).status_code == 200
    assert result(client, attempt, "reject").status_code == 200
    state = read(client)
    assert state["completion_cursor"] == 11
    assert state["types"][-1]["cooldown_remaining"] == 10
    assert prepare(client, mode="auto") is None
    # Remembered allow may bypass only ordinary cooldown, never explicit opt-out.
    assert prepare(client, mode="auto", remembered={"review_digest": "accept"})


def test_feedback_dedupe_failed_actions_and_atomic_rollback(client, app, family):
    rid, rid2 = reviews(app, family, 2)
    assert complete(client, rid, "same-feedback-001").status_code == 200
    assert complete(client, rid, "same-feedback-001").status_code == 200
    assert complete(client, rid).status_code == 200
    assert read(client)["completion_cursor"] == 1
    assert complete(client, rid2, action="defer").status_code == 200
    assert complete(client, "missing-review").status_code == 404
    assert read(client)["completion_cursor"] == 1
    assert complete(client, rid2, "same-feedback-001").status_code == 409
    assert read(client)["completion_cursor"] == 1
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ReviewMemberCompletionReceipt)) == 1


@pytest.mark.parametrize("decision", ["cancel", "technical", "unknown", "ban", "filter"])
def test_non_accept_never_grants_and_classifies_outcome(client, app, family, decision):
    initialize(client, app)
    attempt = prepare(client, mode="auto", remembered={"review_digest": "accept"})
    assert result(client, attempt, decision).status_code == 200
    assert read(client)["settings"]["preferences"][-1]["remaining_quota"] == 0
    if decision in {"ban", "filter"}:
        assert read(client)["types"][-1]["status"] == decision
    if decision != "cancel":
        assert prepare(client, mode="auto", remembered={"review_digest": "accept"}) is None


def test_opt_out_cas_replay_and_late_onboarding_does_not_reenable(client, app, family):
    _grant(client, "parent-a", ["review_digest"])
    spend(app)
    assert read(client)["types"][-1]["consented"] is False
    attempt = prepare(client, mode="onboarding")
    assert attempt
    assert choice(client, "disabled", version=0, key="decline-event-001").status_code == 200
    assert choice(client, "disabled", version=0, key="decline-event-001").status_code == 200
    assert choice(client, "enabled", version=0).status_code == 409
    assert result(client, attempt, enable=True).status_code == 200
    state = read(client)
    assert state["choice"] == "disabled"
    assert state["version"] == 1
    assert state["settings"]["preferences"][-1]["remaining_quota"] == 1
    spend(app)
    assert prepare(client, mode="auto", remembered={"review_digest": "accept"}) is None


@pytest.mark.parametrize(
    "main,remembered,reason",
    [(False, {}, "main_switch_off"), (True, {"review_digest": "reject"}, "remembered_reject")],
)
def test_explicit_device_stop_survives_next_device_allow(
    client, app, family, main, remembered, reason
):
    initialize(client, app)
    assert prepare(client, mode="auto", main=main, remembered=remembered) is None
    assert read(client)["types"][-1]["status"] == reason
    assert prepare(client, mode="auto", remembered={"review_digest": "accept"}) is None
    # Explicit manual restoration can establish a new grant and clear the stop.
    assert result(client, prepare(client)).status_code == 200
    assert read(client)["types"][-1]["status"] == "has_quota"


def test_unknown_attempt_never_reopens_automatically_and_template_change_requires_consent(
    client, app, family
):
    initialize(client, app)
    attempt = prepare(
        client, mode="auto", remembered={"review_digest": "accept"}, key="prepare-replay-001"
    )
    same = prepare(
        client, mode="auto", remembered={"review_digest": "accept"}, key="prepare-replay-001"
    )
    assert same["attempt_id"] == attempt["attempt_id"]
    with app.state.database.session_factory() as db:
        row = db.get(NotificationGrantAttempt, attempt["attempt_id"])
        row.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert prepare(client, mode="auto", remembered={"review_digest": "accept"}) is None
    assert read(client)["types"][-1]["status"] == "pending"
    app.state.notification_channel.bindings["review_digest"] = replace(
        app.state.notification_channel.bindings["review_digest"], template_id="tpl-new"
    )
    assert read(client)["types"][-1]["consented"] is False
    assert result(client, attempt).status_code == 409
    assert prepare(client, mode="auto", remembered={"review_digest": "accept"}) is None


def test_family_member_and_viewer_boundaries(client, app, family):
    attempt = prepare(client)
    application = _join(client, "parent-b", "爸爸")
    response = client.post(
        f"/api/v1/family-requests/{application}/approve",
        headers={**_actor("parent-a"), "Idempotency-Key": "approve-renewal-viewer"},
        json={"role": "viewer"},
    )
    assert response.status_code == 200, response.text
    assert result(client, attempt, actor="parent-b").status_code == 404
    assert read(client, "parent-b")["completion_cursor"] == 0
    assert len(read(client, "parent-b")["types"]) == 2
    rid = reviews(app, family, 1)[0]
    assert complete(client, rid, actor="parent-b").status_code == 403
    assert prepare(client, actor="parent-b")
    with app.state.database.session_factory() as db:
        member = db.scalar(select(FamilyMember).where(FamilyMember.relationship_label == "爸爸"))
        member.status = "removed"
        db.commit()
    assert (
        client.get("/api/v1/notifications/renewal", headers=_actor("parent-b")).status_code == 403
    )


def test_failed_feedback_rolls_back_completion_fact_with_review(client, app, family, monkeypatch):
    from push_kids.planning import service as planning

    rid = reviews(app, family, 1)[0]
    original = planning.record_completion

    def fail_after_fact(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("injected feedback transaction failure")

    monkeypatch.setattr(planning, "record_completion", fail_after_fact)
    with pytest.raises(RuntimeError, match="injected feedback"):
        complete(client, rid, key="rollback-feedback-001")
    assert read(client)["completion_cursor"] == 0
    with app.state.database.session_factory() as db:
        assert db.get(ReviewItem, rid).review_count == 0
        assert db.scalar(select(func.count()).select_from(ReviewMemberCompletionReceipt)) == 0
    monkeypatch.setattr(planning, "record_completion", original)
    assert complete(client, rid, key="rollback-feedback-001").status_code == 200
    assert read(client)["completion_cursor"] == 1


def test_mixed_types_have_independent_cooldown_and_no_payload_key_reuse(client, app, family):
    types = ["review_digest", "schedule_reminder"]
    assert result(client, prepare(client, types=types)).status_code == 200
    spend(app)
    assert choice(client, "enabled", key="choice-fixed-payload").status_code == 200
    assert choice(client, "disabled", version=1, key="choice-fixed-payload").status_code == 409
    for rid in reviews(app, family, 10):
        assert complete(client, rid).status_code == 200
    attempt = prepare(client, types=types, mode="auto")
    response = client.post(
        f"/api/v1/notifications/grant-attempts/{attempt['attempt_id']}/result",
        headers=_actor("parent-a"),
        json={
            "results": [
                {"type": "review_digest", "decision": "accept"},
                {"type": "schedule_reminder", "decision": "cancel"},
            ]
        },
    )
    assert response.status_code == 200, response.text
    snapshot = {item["type"]: item for item in read(client)["types"]}
    assert snapshot["review_digest"]["status"] == "has_quota"
    assert snapshot["schedule_reminder"]["status"] == "cooldown"
    assert prepare(client, types=types, mode="auto") is None


def test_departure_stops_renewal_and_receipt_retention_never_rewinds_cursor(client, app, family):
    from push_kids.notifications.service import NotificationsService

    initialize(client, app)
    rid = reviews(app, family, 1)[0]
    assert complete(client, rid).status_code == 200
    attempt = prepare(client, mode="auto", remembered={"review_digest": "accept"})
    fid, mid = family["family"]["id"], family["member"]["id"]
    with app.state.database.session_factory() as db:
        receipt = db.scalar(select(ReviewMemberCompletionReceipt))
        receipt.day = local_date() - timedelta(days=31)
        db.commit()
        NotificationsService.prune_history(db)
        assert db.scalar(select(func.count()).select_from(ReviewMemberCompletionReceipt)) == 0
    assert read(client)["completion_cursor"] == 1
    with app.state.database.session_factory() as db:
        db.get(FamilyMember, mid).status = "removed"
        db.commit()
        assert NotificationsService.revoke_departed(db) == 1
        assert db.get(NotificationRenewalPreference, (fid, mid)).choice == "disabled"
        assert (
            db.get(NotificationRenewalState, (fid, mid, "review_digest")).active_attempt_id is None
        )
        assert db.get(NotificationGrantAttempt, attempt["attempt_id"]).state == "unknown"
