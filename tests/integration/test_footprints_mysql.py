"""Explicit isolated MySQL gate. Never creates a live provider or sends child photos."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.platform.config import Settings

from tests.integration.test_footprints import ROOT, confirm, create_batch, get_photo, upload


@pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_URL"), reason="isolated MySQL5.7 not configured"
)
def test_mysql_same_confirm_is_idempotent_under_overlap(tmp_path):
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_DATABASE_URL=os.environ["PUSH_KIDS_TEST_MYSQL_URL"],
            PUSH_KIDS_MEDIA_ROOT=tmp_path,
            PUSH_KIDS_AI_PROVIDER="test",
            PUSH_KIDS_RUN_WORKER=False,
            PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
        )
    )
    with TestClient(app) as client:
        h = {"X-Family-ID": f"footprints-mysql-{uuid4().hex}"}
        cid = client.post("/api/v1/children", headers=h, json={"name": "合成测试"}).json()["id"]
        batch = create_batch(client, h, cid)
        photo = upload(client, h, cid, batch["photos"][0]["id"])
        assert app.state.footprint_worker.process_one()
        photo = get_photo(client, h, cid, photo["id"])
        gate = Barrier(2)

        def run(_):
            gate.wait(timeout=10)
            response = confirm(client, h, cid, batch["id"], [photo])
            assert response.status_code == 200, response.text

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run, range(2)))
        result = client.get(f"{ROOT}/summary?child_id={cid}", headers=h).json()
        assert result["photos"] == 1 and result["visit_days"] == 1
