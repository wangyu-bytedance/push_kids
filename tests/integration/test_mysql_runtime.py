from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.bootstrap.app import create_app
from push_kids.families.schemas import JoinDecision
from push_kids.families.service import FamilyService
from push_kids.persistence.models import Family, FamilyMember, WeChatActorBinding
from push_kids.platform.config import Settings
from push_kids.platform.context import RequestContext, subject_hmac
from sqlalchemy import select

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="PUSH_KIDS_TEST_MYSQL_URL is not configured")


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
