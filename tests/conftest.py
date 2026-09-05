from __future__ import annotations

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
