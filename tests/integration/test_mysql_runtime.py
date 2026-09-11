from __future__ import annotations

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from push_kids.activities.service import ActivitiesService
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.bootstrap.app import create_app
from push_kids.families.schemas import JoinDecision
from push_kids.families.service import FamilyService
from push_kids.learning.service import LearningService
from push_kids.persistence.models import (
    ActivityRecord,
    AgentJob,
    Child,
    Family,
    FamilyMember,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
    SubmissionMedia,
    SubmissionRequest,
    WeChatActorBinding,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.config import Settings
from push_kids.platform.context import RequestContext, subject_hmac
from push_kids.platform.time import local_date, utcnow
from push_kids.reporting.service import ReportingService
from sqlalchemy import event, select

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="PUSH_KIDS_TEST_MYSQL_URL is not configured")


@pytest.fixture(autouse=True)
def _restore_application_logger() -> None:
    """A cloud app installs a process-wide handler; keep the isolated DB suite hermetic."""
    application_logger = logging.getLogger("push_kids")
    original_handlers = list(application_logger.handlers)
    original_level = application_logger.level
    original_propagate = application_logger.propagate
    try:
        yield
    finally:
        for handler in application_logger.handlers:
            if handler not in original_handlers:
                handler.close()
        application_logger.handlers[:] = original_handlers
        application_logger.setLevel(original_level)
        application_logger.propagate = original_propagate


def _headers(openid: str) -> dict[str, str]:
    return {
        "X-WX-SOURCE": "wx_client",
        "X-WX-OPENID": openid,
        "X-WX-APPID": "wx-mysql-test",
        "X-WX-ENV": "mysql-test",
    }


def test_mysql_cloud_identity_job_idempotency_and_confirmation() -> None:
    assert MYSQL_URL
    hmac_key = "mysql-test-hmac-key-that-is-long-enough"
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="cloud",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_BACKEND="wechat_cloud",
            CBR_ENV_ID="mysql-test",
            WECHAT_APP_ID="wx-mysql-test",
            COS_BUCKET="bucket-test",
            PUSH_KIDS_ACTOR_HMAC_KEY=hmac_key,
            PUSH_KIDS_RUN_WORKER=True,
            ARK_API_KEY="synthetic-mysql-test-key",
        )
    )
    app.state.worker.provider = DeterministicTestProvider()
    with app.state.database.session_factory() as db:
        for openid, family_id in (("parent-a", "mysql-family-a"), ("parent-b", "mysql-family-b")):
            family = Family(id=family_id, display_name=f"{openid} family")
            binding = WeChatActorBinding(
                app_id="wx-mysql-test",
                subject_hmac=subject_hmac(hmac_key, "wx-mysql-test", openid),
                family_id=family_id,
            )
            db.add_all([family, binding])
            db.flush()
            db.add(
                FamilyMember(
                    family_id=family_id,
                    actor_binding_id=binding.id,
                    active_actor_binding_id=binding.id,
                    role="manager",
                    relationship_label="parent",
                )
            )
        db.commit()

    with TestClient(app) as client:
        child = client.post(
            "/api/v1/children",
            headers=_headers("parent-a"),
            json={"name": "MySQL test child", "grade": "2", "daily_budget_minutes": 15},
        )
        assert child.status_code == 201
        payload = {
            "child_id": child.json()["id"],
            "occurred_at": "2026-09-03T08:00:00Z",
            "input_text": "learned multiplication",
            "source": "manual",
        }
        headers = {**_headers("parent-a"), "Idempotency-Key": "mysql-submission-001"}
        created = client.post("/api/v1/submissions", headers=headers, json=payload)
        duplicate = client.post("/api/v1/submissions", headers=headers, json=payload)
        assert created.status_code == 202
        assert duplicate.status_code == 202
        assert duplicate.json()["id"] == created.json()["id"]
        assert (
            client.get(
                f"/api/v1/submissions/{created.json()['id']}", headers=_headers("parent-b")
            ).status_code
            == 404
        )

        deadline = time.monotonic() + 5
        detail = created
        while time.monotonic() < deadline:
            detail = client.get(
                f"/api/v1/submissions/{created.json()['id']}", headers=_headers("parent-a")
            )
            if detail.json()["state"] == "pending_confirmation":
                break
            time.sleep(0.05)
        assert detail.json()["state"] == "pending_confirmation"
        confirmed = client.post(
            f"/api/v1/submissions/{created.json()['id']}/confirm",
            headers=_headers("parent-a"),
            json={"proposal": detail.json()["proposal"]},
        )
        assert confirmed.status_code == 200
        assert len(confirmed.json()["knowledge_item_ids"]) >= 1


def test_mysql_family_onboarding_invite_and_approval() -> None:
    assert MYSQL_URL
    hmac_key = "mysql-test-hmac-key-that-is-long-enough"
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="cloud",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_BACKEND="wechat_cloud",
            CBR_ENV_ID="mysql-test",
            WECHAT_APP_ID="wx-mysql-test",
            COS_BUCKET="bucket-test",
            PUSH_KIDS_ACTOR_HMAC_KEY=hmac_key,
            PUSH_KIDS_RUN_WORKER=True,
            ARK_API_KEY="synthetic-mysql-test-key",
        )
    )
    with TestClient(app) as client:
        manager = _headers("onboarding-manager")
        applicant = _headers("onboarding-applicant")
        assert client.get("/api/v1/me", headers=manager).json()["state"] == "unbound"
        created = client.post(
            "/api/v1/families",
            headers={**manager, "Idempotency-Key": "mysql-family-create-001"},
            json={
                "display_name": "MySQL onboarding family",
                "relationship_label": "parent",
                "child": {"name": "MySQL child", "daily_budget_minutes": 15},
            },
        )
        assert created.status_code == 201
        invite = client.post(
            "/api/v1/families/current/invites",
            headers={**manager, "Idempotency-Key": "mysql-family-invite-001"},
            json={},
        )
        assert invite.status_code == 201
        request = client.post(
            "/api/v1/family-requests",
            headers={**applicant, "Idempotency-Key": "mysql-family-join-001"},
            json={"token": invite.json()["token"], "relationship_label": "grandparent"},
        )
        assert request.status_code == 201
        with app.state.database.session_factory() as db:
            manager_binding = db.scalar(
                select(WeChatActorBinding).where(
                    WeChatActorBinding.subject_hmac
                    == subject_hmac(hmac_key, "wx-mysql-test", "onboarding-manager")
                )
            )
            manager_member = db.scalar(
                select(FamilyMember).where(FamilyMember.actor_binding_id == manager_binding.id)
            )
            context = RequestContext(
                family_id=manager_binding.family_id,
                subject_hmac=manager_binding.subject_hmac,
                app_id=manager_binding.app_id,
                openid=None,
                actor_binding_id=manager_binding.id,
                member_id=manager_member.id,
                role="manager",
            )

        def approve_once() -> str:
            with app.state.database.session_factory() as db:
                result = FamilyService.approve(
                    db,
                    context,
                    request.json()["id"],
                    JoinDecision(role="editor"),
                    "mysql-family-approve-001",
                )
                return result.id

        with ThreadPoolExecutor(max_workers=2) as executor:
            member_ids = list(executor.map(lambda _index: approve_once(), range(2)))
        assert member_ids[0] == member_ids[1]
        assert client.get("/api/v1/me", headers=applicant).json()["state"] == "bound"

        removed = client.delete(
            f"/api/v1/families/current/members/{member_ids[0]}", headers=manager
        )
        assert removed.status_code == 204
        assert client.get("/api/v1/me", headers=applicant).json()["state"] == "unbound"
        second_invite = client.post(
            "/api/v1/families/current/invites",
            headers={**manager, "Idempotency-Key": "mysql-family-invite-002"},
            json={},
        )
        second_request = client.post(
            "/api/v1/family-requests",
            headers={**applicant, "Idempotency-Key": "mysql-family-join-002"},
            json={"token": second_invite.json()["token"], "relationship_label": "grandparent"},
        )
        second_approval_headers = {
            **manager,
            "Idempotency-Key": "mysql-family-approve-002",
        }
        second_approval = client.post(
            f"/api/v1/family-requests/{second_request.json()['id']}/approve",
            headers=second_approval_headers,
            json={"role": "viewer"},
        )
        replayed_approval = client.post(
            f"/api/v1/family-requests/{second_request.json()['id']}/approve",
            headers=second_approval_headers,
            json={"role": "viewer"},
        )
        assert second_approval.status_code == 200
        assert replayed_approval.status_code == 200
        assert second_approval.json()["id"] == replayed_approval.json()["id"]
        assert second_approval.json()["id"] != member_ids[0]


def test_mysql_history_reviews_supports_empty_feedback_and_stable_pagination() -> None:
    """Exercise the record-detail query against the same dialect used in cloud hosting."""
    assert MYSQL_URL
    token = uuid4().hex[:12]
    openid = f"history-parent-{token}"
    family_id = f"mysql-history-{token}"
    hmac_key = "mysql-test-hmac-key-that-is-long-enough"
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="cloud",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_BACKEND="wechat_cloud",
            CBR_ENV_ID="mysql-test",
            WECHAT_APP_ID="wx-mysql-test",
            COS_BUCKET="bucket-test",
            PUSH_KIDS_ACTOR_HMAC_KEY=hmac_key,
            PUSH_KIDS_RUN_WORKER=True,
            ARK_API_KEY="synthetic-mysql-test-key",
        )
    )
    app.state.worker.provider = DeterministicTestProvider()
    with app.state.database.session_factory() as db:
        family = Family(id=family_id, display_name="MySQL history family")
        binding = WeChatActorBinding(
            app_id="wx-mysql-test",
            subject_hmac=subject_hmac(hmac_key, "wx-mysql-test", openid),
            family_id=family_id,
        )
        db.add_all([family, binding])
        db.flush()
        db.add(
            FamilyMember(
                family_id=family_id,
                actor_binding_id=binding.id,
                active_actor_binding_id=binding.id,
                role="manager",
                relationship_label="parent",
            )
        )
        db.commit()

    headers = _headers(openid)
    with TestClient(app) as client:
        child = client.post(
            "/api/v1/children",
            headers=headers,
            json={"name": "MySQL history child", "grade": "1", "daily_budget_minutes": 15},
        )
        assert child.status_code == 201, child.text
        child_id = child.json()["id"]
        created = client.post(
            "/api/v1/submissions",
            headers={**headers, "Idempotency-Key": f"mysql-history-submission-{token}"},
            json={
                "child_id": child_id,
                "occurred_at": "2026-09-11T11:32:00Z",
                "input_text": "数学：集合分组，寻找规则",
                "source": "manual",
            },
        )
        assert created.status_code == 202, created.text
        submission_id = created.json()["id"]

        deadline = time.monotonic() + 5
        detail = created
        while time.monotonic() < deadline:
            detail = client.get(f"/api/v1/submissions/{submission_id}", headers=headers)
            if detail.json()["state"] == "pending_confirmation":
                break
            time.sleep(0.05)
        assert detail.json()["state"] == "pending_confirmation"
        confirmed = client.post(
            f"/api/v1/submissions/{submission_id}/confirm",
            headers=headers,
            json={"proposal": detail.json()["proposal"]},
        )
        assert confirmed.status_code == 200, confirmed.text
        review_id = confirmed.json()["review_item_ids"][0]
        endpoint = f"/api/v1/children/{child_id}/history/{submission_id}/reviews"

        empty = client.get(endpoint, headers=headers)
        assert empty.status_code == 200, empty.text
        empty_item = next(item for item in empty.json()["items"] if item["review_id"] == review_id)
        assert empty_item["feedback"] == []
        assert empty_item["next_before"] is None

        with app.state.database.session_factory() as db:
            review = db.get(ReviewItem, review_id)
            review.due_date = utcnow().date() - timedelta(days=1)
            for offset in range(7):
                db.add(
                    ReviewFeedback(
                        family_id=family_id,
                        review_item_id=review_id,
                        action="complete",
                        occurred_at=utcnow() - timedelta(days=offset),
                    )
                )
            db.commit()

        first_response = client.get(endpoint, headers=headers)
        assert first_response.status_code == 200, first_response.text
        first = next(
            item for item in first_response.json()["items"] if item["review_id"] == review_id
        )
        assert first["is_due"] is True
        assert len(first["feedback"]) == 3
        assert first["next_before"]

        second_response = client.get(
            endpoint,
            headers=headers,
            params={"review_id": review_id, "before": first["next_before"]},
        )
        assert second_response.status_code == 200, second_response.text
        second = second_response.json()["items"][0]
        assert len(second["feedback"]) == 3
        assert not {item["id"] for item in first["feedback"]} & {
            item["id"] for item in second["feedback"]
        }
        unrelated = client.get(
            endpoint,
            headers=headers,
            params={"review_id": f"unrelated-{token}"},
        )
        assert unrelated.status_code == 404
        expired_cursor = client.get(
            endpoint,
            headers=headers,
            params={"review_id": review_id, "before": f"missing-{token}"},
        )
        assert expired_cursor.status_code == 400


def test_mysql_bounded_read_paths_have_indexed_query_plans() -> None:
    assert MYSQL_URL
    token = uuid4().hex[:12]
    family_id = f"mysql-read-plan-{token}"
    child_id = f"child-{token}"
    learning_subject_id = f"learning-{token}"
    activity_subject_id = f"activity-{token}"
    confirmed_submission_id = f"confirmed-{token}"
    pending_submission_id = f"pending-{token}"
    record_id = f"record-{token}"
    knowledge_id = f"knowledge-{token}"
    review_id = f"review-{token}"
    activity_id = f"activity-record-{token}"
    now = utcnow()
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="cloud",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_BACKEND="wechat_cloud",
            CBR_ENV_ID="mysql-test",
            WECHAT_APP_ID="wx-mysql-test",
            COS_BUCKET="bucket-test",
            PUSH_KIDS_ACTOR_HMAC_KEY="mysql-test-hmac-key-that-is-long-enough",
            PUSH_KIDS_RUN_WORKER=True,
            ARK_API_KEY="synthetic-mysql-test-key",
        )
    )
    with app.state.database.session_factory() as db:
        db.add(Family(id=family_id, display_name="MySQL read plan family"))
        db.add(
            Child(
                id=child_id,
                family_id=family_id,
                name="MySQL read plan child",
                daily_budget_minutes=15,
            )
        )
        db.add_all(
            [
                Subject(
                    id=learning_subject_id,
                    family_id=family_id,
                    child_id=child_id,
                    name="数学",
                    kind="learning",
                ),
                Subject(
                    id=activity_subject_id,
                    family_id=family_id,
                    child_id=child_id,
                    name="游泳",
                    kind="activity",
                ),
            ]
        )
        db.add_all(
            [
                LearningSubmission(
                    id=confirmed_submission_id,
                    family_id=family_id,
                    child_id=child_id,
                    occurred_at=now,
                    input_text="已确认记录",
                    source="manual",
                    state="confirmed",
                    confirmed_at=now,
                ),
                LearningSubmission(
                    id=pending_submission_id,
                    family_id=family_id,
                    child_id=child_id,
                    occurred_at=now,
                    input_text="待处理记录",
                    source="photo",
                    state="queued",
                ),
            ]
        )
        db.flush()
        db.add(
            LearningRecord(
                id=record_id,
                family_id=family_id,
                child_id=child_id,
                subject_id=learning_subject_id,
                submission_id=confirmed_submission_id,
                occurred_at=now,
                summary="执行计划记录",
                source="manual",
            )
        )
        db.add(
            KnowledgeItem(
                id=knowledge_id,
                family_id=family_id,
                child_id=child_id,
                subject_id=learning_subject_id,
                name="执行计划知识",
                normalized_name="执行计划知识",
                category="知识点",
                review_method="口头回顾",
                estimated_minutes=1,
            )
        )
        db.flush()
        db.add_all(
            [
                KnowledgeOccurrence(
                    family_id=family_id,
                    knowledge_item_id=knowledge_id,
                    learning_record_id=record_id,
                    occurred_at=now,
                ),
                ReviewItem(
                    id=review_id,
                    family_id=family_id,
                    child_id=child_id,
                    knowledge_item_id=knowledge_id,
                    source_submission_id=confirmed_submission_id,
                    due_date=local_date(now),
                    active=True,
                ),
                ActivityRecord(
                    id=activity_id,
                    family_id=family_id,
                    child_id=child_id,
                    subject_id=activity_subject_id,
                    occurred_at=now,
                    duration_minutes=30,
                ),
                AgentJob(
                    family_id=family_id,
                    submission_id=pending_submission_id,
                ),
                SubmissionMedia(
                    submission_id=pending_submission_id,
                    path=f"test/{token}.jpg",
                    content_type="image/jpeg",
                    byte_size=10,
                ),
                SubmissionRequest(
                    family_id=family_id,
                    idempotency_key=f"mysql-read-plan-{token}",
                    request_fingerprint="0" * 64,
                    submission_id=pending_submission_id,
                ),
            ]
        )
        db.flush()
        db.add(
            ReviewFeedback(
                family_id=family_id,
                review_item_id=review_id,
                action="complete",
                occurred_at=now,
            )
        )
        db.commit()

    captured = []

    def capture_select(_conn, _cursor, statement, parameters, *_args) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            captured.append((statement, parameters))

    event.listen(app.state.database.engine, "before_cursor_execute", capture_select)
    try:
        with app.state.database.session_factory() as db:
            PlanningService.daily_todo_page(db, family_id, child_id, local_date(now), limit=20)
            ReportingService.report(db, family_id, child_id, 7)
            LearningService.list_page(db, family_id, child_id, pending_only=True, limit=100)
            ActivitiesService.record_page(db, family_id, child_id, limit=100)
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", capture_select)

    plans = []
    with app.state.database.engine.connect() as connection:
        for statement, parameters in captured:
            plans.extend(
                connection.exec_driver_sql(f"EXPLAIN {statement}", parameters).mappings().all()
            )
    base_rows = [row for row in plans if not str(row.get("table") or "").startswith("<")]
    assert base_rows
    assert all(row.get("type") != "ALL" and row.get("key") for row in base_rows)
    possible_keys = ",".join(str(row.get("possible_keys") or "") for row in plans)
    for index_name in (
        "ix_learning_submissions_family_child_state_created_id",
        "ix_learning_records_family_child_occurred_submission",
        "ix_knowledge_items_family_child_created_id",
        "ix_knowledge_occurrences_family_occurred_knowledge",
        "ix_review_items_family_child_active_due_id",
        "ix_review_feedback_family_review_occurred",
        "ix_activity_records_family_child_occurred_id",
    ):
        assert index_name in possible_keys
