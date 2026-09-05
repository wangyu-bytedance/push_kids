from __future__ import annotations

import os
import time

import pytest
from fastapi.testclient import TestClient
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.bootstrap.app import create_app
from push_kids.persistence.models import WeChatActorBinding
from push_kids.platform.config import Settings
from push_kids.platform.context import subject_hmac

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
            WECHAT_STORAGE_BUCKET="bucket-test",
            WECHAT_STORAGE_CLOUD_PREFIX="cloud://mysql-test",
            PUSH_KIDS_ACTOR_HMAC_KEY=hmac_key,
            PUSH_KIDS_RUN_WORKER=True,
        )
    )
    app.state.worker.provider = DeterministicTestProvider()
    with app.state.database.session_factory() as db:
        db.add_all(
            [
                WeChatActorBinding(
                    app_id="wx-mysql-test",
                    subject_hmac=subject_hmac(hmac_key, "wx-mysql-test", "parent-a"),
                    family_id="mysql-family-a",
                ),
                WeChatActorBinding(
                    app_id="wx-mysql-test",
                    subject_hmac=subject_hmac(hmac_key, "wx-mysql-test", "parent-b"),
                    family_id="mysql-family-b",
                ),
            ]
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
