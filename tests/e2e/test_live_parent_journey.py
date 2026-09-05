from __future__ import annotations

import base64
import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


@contextmanager
def _live_api(tmp_path: Path) -> Iterator[tuple[httpx.Client, Path, Path]]:
    port = _free_port()
    database_path = tmp_path / "e2e.sqlite3"
    media_root = tmp_path / "media"
    log_path = tmp_path / "uvicorn.log"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(Path.cwd() / "apps/api/src"),
            "PUSH_KIDS_ENV": "e2e",
            "PUSH_KIDS_DATABASE_URL": f"sqlite:///{database_path}",
            "PUSH_KIDS_MEDIA_ROOT": str(media_root),
            "PUSH_KIDS_AI_PROVIDER": "test",
            "PUSH_KIDS_RUN_WORKER": "true",
        }
    )
    env.pop("ARK_API_KEY", None)
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "push_kids.bootstrap.app:create_app",
                "--factory",
                "--app-dir",
                str(Path.cwd() / "apps/api/src"),
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=Path.cwd(),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise AssertionError(f"E2E API exited early; see {log_path}")
                try:
                    health = client.get("/health")
                    if health.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.05)
            else:
                raise AssertionError(f"E2E API did not become healthy; see {log_path}")
            yield client, database_path, media_root
        finally:
            client.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _json(response: httpx.Response, status: int) -> Any:
    assert response.status_code == status, response.text
    return response.json()


def _wait_for_proposal(client: httpx.Client, headers: dict[str, str], submission_id: str) -> dict:
    deadline = time.monotonic() + 10
    seen_states: set[str] = set()
    while time.monotonic() < deadline:
        payload = _json(client.get(f"/api/v1/submissions/{submission_id}", headers=headers), 200)
        seen_states.add(payload["state"])
        if payload["state"] == "pending_confirmation":
            assert payload["proposal"] is not None
            return payload
        assert payload["state"] in {"queued", "analyzing"}, (payload, seen_states)
        time.sleep(0.05)
    raise AssertionError(f"analysis did not finish; observed states={sorted(seen_states)}")


def _replace_points(proposal: dict, names: list[str], subject_name: str) -> dict:
    proposal["summary"] = f"家长确认：学习了{'、'.join(names)}"
    proposal["subject_name"] = subject_name
    proposal["knowledge_points"] = [
        {
            "name": name,
            "category": "计算与概念" if subject_name == "数学" else "字词与阅读",
            "review_method": "口算与讲解" if subject_name == "数学" else "认读与听写",
            "estimated_minutes": 3,
        }
        for name in names
    ]
    return proposal


def _flatten_todos(payload: dict) -> list[dict]:
    return [item for group in payload["groups"] for item in group["items"]]


def test_complete_parent_journey_over_live_http(tmp_path: Path) -> None:
    family = {"X-Family-ID": "e2e-family-a"}
    other_family = {"X-Family-ID": "e2e-family-b"}
    now = datetime.now(UTC)

    with _live_api(tmp_path) as (client, database_path, media_root):
        assert _json(client.get("/health"), 200) == {"status": "ok", "ai_provider": "test"}
        assert client.get("/api/v1/children").status_code == 422

        child = _json(
            client.post(
                "/api/v1/children",
                headers=family,
                json={"name": "端到端小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
            ),
            201,
        )
        child_id = child["id"]
        updated_child = _json(
            client.patch(
                f"/api/v1/children/{child_id}",
                headers=family,
                json={"daily_budget_minutes": 20},
            ),
            200,
        )
        assert updated_child["daily_budget_minutes"] == 20
        assert (
            client.get(f"/api/v1/children/{child_id}/dashboard", headers=other_family).status_code
            == 404
        )
        assert client.get("/api/v1/children", headers=other_family).json() == []

        concurrent_child = _json(
            client.post(
                "/api/v1/children",
                headers=family,
                json={"name": "并发验证", "grade": "小学", "daily_budget_minutes": 10},
            ),
            201,
        )
        concurrent_headers = {**family, "Idempotency-Key": "e2e-concurrent-retry-001"}
        concurrent_payload = {
            "child_id": concurrent_child["id"],
            "occurred_at": now.isoformat(),
            "input_text": "数学，并发重试验证",
        }

        def create_concurrently() -> tuple[int, str]:
            response = client.post(
                "/api/v1/submissions", headers=concurrent_headers, json=concurrent_payload
            )
            return response.status_code, response.json().get("id", response.text)

        with ThreadPoolExecutor(max_workers=2) as executor:
            concurrent_results = list(executor.map(lambda _index: create_concurrently(), range(2)))
        assert {status for status, _item_id in concurrent_results} == {202}
        assert len({item_id for _status, item_id in concurrent_results}) == 1

        math = _json(
            client.post(
                "/api/v1/subjects",
                headers=family,
                json={"child_id": child_id, "name": "数学", "kind": "learning"},
            ),
            201,
        )
        swimming = _json(
            client.post(
                "/api/v1/subjects",
                headers=family,
                json={"child_id": child_id, "name": "游泳", "kind": "activity"},
            ),
            201,
        )
        _json(
            client.post(
                "/api/v1/activity-schedules",
                headers=family,
                json={
                    "child_id": child_id,
                    "subject_id": swimming["id"],
                    "weekdays": [now.astimezone().weekday()],
                    "start_time": "18:30:00",
                    "end_time": "19:30:00",
                    "target_per_week": 2,
                },
            ),
            201,
        )

        first_headers = {**family, "Idempotency-Key": "e2e-manual-first-001"}
        first_payload = {
            "child_id": child_id,
            "occurred_at": (now - timedelta(days=4)).isoformat(),
            "input_text": "数学，进位加法，退位减法，乘法口诀，除法概念，长度单位",
        }
        first_submission = _json(
            client.post(
                "/api/v1/submissions",
                headers=first_headers,
                json=first_payload,
            ),
            202,
        )
        assert first_submission["state"] == "queued"
        first_retry = _json(
            client.post("/api/v1/submissions", headers=first_headers, json=first_payload), 202
        )
        assert first_retry["id"] == first_submission["id"]
        assert (
            _json(client.get(f"/api/v1/children/{child_id}/history", headers=family), 200)["items"]
            == []
        )
        assert (
            client.get(
                f"/api/v1/submissions/{first_submission['id']}", headers=other_family
            ).status_code
            == 404
        )

        first_draft = _wait_for_proposal(client, family, first_submission["id"])
        names = ["进位加法", "退位减法", "乘法口诀", "除法概念", "长度单位"]
        first_proposal = _replace_points(first_draft["proposal"], names, "数学")
        first_proposal["todo_matches"] = []
        first_confirmed = _json(
            client.post(
                f"/api/v1/submissions/{first_submission['id']}/confirm",
                headers=family,
                json={"subject_id": math["id"], "proposal": first_proposal},
            ),
            200,
        )
        assert len(first_confirmed["knowledge_item_ids"]) == 5
        assert len(first_confirmed["review_item_ids"]) == 5
        assert (
            client.post(
                f"/api/v1/submissions/{first_submission['id']}/confirm",
                headers=family,
                json={"subject_id": math["id"], "proposal": first_proposal},
            ).status_code
            == 409
        )

        repeated = _json(
            client.post(
                "/api/v1/submissions",
                headers=family,
                json={
                    "child_id": child_id,
                    "occurred_at": (now - timedelta(days=1)).isoformat(),
                    "input_text": "数学，进位加法",
                },
            ),
            202,
        )
        repeated_draft = _wait_for_proposal(client, family, repeated["id"])
        matches = repeated_draft["proposal"]["todo_matches"]
        assert [item["knowledge_name"] for item in matches] == ["进位加法"]
        repeated_proposal = _replace_points(repeated_draft["proposal"], ["进位加法"], "数学")
        repeated_confirmed = _json(
            client.post(
                f"/api/v1/submissions/{repeated['id']}/confirm",
                headers=family,
                json={"subject_id": math["id"], "proposal": repeated_proposal},
            ),
            200,
        )
        assert repeated_confirmed["knowledge_item_ids"] == [
            first_confirmed["knowledge_item_ids"][0]
        ]

        todo_payload = _json(client.get(f"/api/v1/children/{child_id}/todos", headers=family), 200)
        todos = _flatten_todos(todo_payload)
        assert {item["knowledge_name"] for item in todos} == set(names[1:])
        actions = ["complete", "reinforce", "partial", "defer"]
        for item, action in zip(todos, actions, strict=True):
            result = _json(
                client.post(
                    f"/api/v1/reviews/{item['review_id']}/feedback",
                    headers=family,
                    json={"action": action},
                ),
                200,
            )
            assert result["action"] == action
            assert result["due_date"] > todo_payload["day"]
        assert (
            client.post(
                f"/api/v1/reviews/{todos[0]['review_id']}/feedback",
                headers=other_family,
                json={"action": "complete"},
            ).status_code
            == 404
        )

        backfill = _json(
            client.post(
                "/api/v1/submissions",
                headers=family,
                json={
                    "child_id": child_id,
                    "occurred_at": (now - timedelta(days=120)).isoformat(),
                    "input_text": "语文，古诗静夜思",
                },
            ),
            202,
        )
        backfill_draft = _wait_for_proposal(client, family, backfill["id"])
        backfill_proposal = _replace_points(backfill_draft["proposal"], ["古诗《静夜思》"], "语文")
        backfill_proposal["todo_matches"] = []
        _json(
            client.post(
                f"/api/v1/submissions/{backfill['id']}/confirm",
                headers=family,
                json={"proposal": backfill_proposal},
            ),
            200,
        )
        current_todos = _flatten_todos(
            _json(client.get(f"/api/v1/children/{child_id}/todos", headers=family), 200)
        )
        backfill_todo = next(
            item for item in current_todos if item["knowledge_name"] == "古诗《静夜思》"
        )
        assert backfill_todo["due_date"] == datetime.now().astimezone().date().isoformat()

        invalid_media = client.post(
            "/api/v1/submissions/upload",
            headers=family,
            data={"child_id": child_id, "occurred_at": now.isoformat()},
            files={"files": ("notes.txt", b"not an image", "text/plain")},
        )
        assert invalid_media.status_code == 400
        photo_headers = {**family, "Idempotency-Key": "e2e-photo-first-001"}
        photo_data = {
            "child_id": child_id,
            "occurred_at": now.isoformat(),
            "input_text": "英语单词 animal",
            "defer_analysis": "true",
        }
        photo_files = {"files": ("homework.png", PNG_1X1, "image/png")}
        photo = _json(
            client.post(
                "/api/v1/submissions/upload",
                headers=photo_headers,
                data=photo_data,
                files=photo_files,
            ),
            202,
        )
        assert photo["media_count"] == 1
        assert photo["state"] == "queued"
        assert photo["proposal"] is None
        photo_retry = _json(
            client.post(
                "/api/v1/submissions/upload",
                headers=photo_headers,
                data=photo_data,
                files=photo_files,
            ),
            202,
        )
        assert photo_retry["id"] == photo["id"]
        assert photo_retry["media_count"] == 1
        appended = _json(
            client.post(
                f"/api/v1/submissions/{photo['id']}/media",
                headers=family,
                files={"file": ("homework-2.png", PNG_1X1, "image/png")},
            ),
            200,
        )
        assert appended["media_count"] == 2
        assert appended["state"] == "queued"
        finalized = _json(
            client.post(f"/api/v1/submissions/{photo['id']}/finalize", headers=family), 200
        )
        assert finalized["state"] == "queued"
        finalized_retry = _json(
            client.post(f"/api/v1/submissions/{photo['id']}/finalize", headers=family), 200
        )
        assert finalized_retry["id"] == photo["id"]
        photo_draft = _wait_for_proposal(client, family, photo["id"])
        photo_proposal = photo_draft["proposal"]
        photo_proposal["summary"] = "家长确认：英语单词 animal"
        photo_proposal["knowledge_points"] = [
            {
                "name": "animal",
                "category": "词汇与表达",
                "review_method": "听说与拼写",
                "estimated_minutes": 3,
            }
        ]
        photo_proposal["todo_matches"] = []
        _json(
            client.post(
                f"/api/v1/submissions/{photo['id']}/confirm",
                headers=family,
                json={"proposal": photo_proposal},
            ),
            200,
        )
        stored_files = [path for path in media_root.rglob("*") if path.is_file()]
        assert len(stored_files) == 1
        assert stored_files[0].read_bytes() == PNG_1X1

        activity = _json(
            client.post(
                "/api/v1/activity-records",
                headers=family,
                json={
                    "child_id": child_id,
                    "subject_id": swimming["id"],
                    "occurred_at": now.isoformat(),
                    "duration_minutes": 45,
                    "note": "练习换气与漂浮",
                },
            ),
            201,
        )
        assert activity["duration_minutes"] == 45
        suggestions = _json(
            client.get(f"/api/v1/children/{child_id}/activity-suggestions", headers=family), 200
        )["items"]
        assert suggestions[0]["optional"] is True
        assert suggestions[0]["last_practice_days_ago"] == 0

        dashboard = _json(client.get(f"/api/v1/children/{child_id}/dashboard", headers=family), 200)
        assert dashboard["pending_confirmation_count"] == 0
        assert dashboard["analyzing_count"] == 0
        assert dashboard["failed_count"] == 0
        assert dashboard["todo_count"] == 1
        assert dashboard["activity_suggestions"][0]["optional"] is True

        history = _json(client.get(f"/api/v1/children/{child_id}/history", headers=family), 200)[
            "items"
        ]
        assert len(history) == 4
        assert history[0]["summary"] == "家长确认：英语单词 animal"
        calendar = _json(
            client.get(
                f"/api/v1/children/{child_id}/calendar",
                headers=family,
                params={"month": datetime.now().astimezone().strftime("%Y-%m")},
            ),
            200,
        )
        today_row = next(
            item
            for item in calendar["days"]
            if item["day"] == datetime.now().astimezone().date().isoformat()
        )
        assert today_row == {"day": today_row["day"], "learning": 1, "activity": 1}
        report = _json(
            client.get(f"/api/v1/children/{child_id}/report", headers=family, params={"days": 30}),
            200,
        )
        assert report["overview"] == {
            "learning_records": 3,
            "new_knowledge_items": 7,
            "review_feedback_count": 5,
            "activity_records": 1,
        }
        assert "notice" not in report
        assert "future_load" not in report
        assert len(report["review_urgency"]) == 30
        assert len(report["review_activity"]) == 30
        materials = _json(
            client.get(f"/api/v1/children/{child_id}/practice-materials", headers=family), 200
        )
        assert materials["items"]
        assert materials["disclaimer"] == "用于提示复习，不自动判分。"
        assert (
            _json(
                client.get(
                    "/api/v1/submissions",
                    headers=family,
                    params={"child_id": child_id, "state": "pending_confirmation"},
                ),
                200,
            )
            == []
        )

        assert database_path.is_file()
