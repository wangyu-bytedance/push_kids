from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.platform.config import Settings


@pytest.fixture
def app(tmp_path: Path):
    settings = Settings(
        PUSH_KIDS_ENV="test",
        PUSH_KIDS_DATABASE_URL="sqlite:///:memory:",
        PUSH_KIDS_MEDIA_ROOT=tmp_path / "uploads",
        PUSH_KIDS_AI_PROVIDER="test",
        PUSH_KIDS_RUN_WORKER=False,
    )
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def family_headers():
    return {"X-Family-ID": "family-test-a"}


@pytest.fixture
def child(client: TestClient, family_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/children",
        headers=family_headers,
        json={"name": "小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
    )
    assert response.status_code == 201
    return response.json()


# 通知通道需要真实的模板映射和凭据才算"可用"，这里用 recording 通道让断言落在"本该发出什么"上。
NOTIFICATION_TEMPLATES = json.dumps(
    {
        "member_application": {
            "template_id": "tpl-application",
            "fields": {"thing1": "headline", "thing2": "detail", "character_string3": "code"},
        },
        "schedule_reminder": {
            "template_id": "tpl-schedule",
            "fields": {"thing1": "child", "time2": "time", "thing3": "headline"},
        },
        "review_digest": {
            "template_id": "tpl-digest",
            "fields": {"thing1": "headline", "thing2": "detail"},
        },
    },
    ensure_ascii=False,
)
NOTIFICATION_TRIGGER = "notification-trigger-token-for-tests"


@pytest.fixture
def notification_app(tmp_path: Path):
    settings = Settings(
        PUSH_KIDS_ENV="test",
        PUSH_KIDS_DATABASE_URL="sqlite:///:memory:",
        PUSH_KIDS_MEDIA_ROOT=tmp_path / "uploads",
        PUSH_KIDS_AI_PROVIDER="test",
        PUSH_KIDS_RUN_WORKER=False,
        PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
        PUSH_KIDS_NOTIFICATION_CHANNEL="recording",
        PUSH_KIDS_NOTIFICATION_TEMPLATES=NOTIFICATION_TEMPLATES,
        PUSH_KIDS_NOTIFICATION_TRIGGER_TOKEN=NOTIFICATION_TRIGGER,
    )
    return create_app(settings)
