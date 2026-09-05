import asyncio
from threading import Event
from unittest.mock import Mock

import httpx
import pytest
from push_kids.platform.time import utcnow
from sqlalchemy import event
from sqlalchemy.exc import OperationalError


@pytest.mark.asyncio
async def test_readiness_tracks_running_backoff_and_recovery(app, monkeypatch):
    app.state.settings.run_worker = True
    worker = app.state.worker
    waiting = asyncio.Event()
    resume = asyncio.Event()
    broken = False

    def process():
        if broken:
            raise RuntimeError("private-provider-message")
        return False

    async def wait(delay):
        waiting.set()
        await resume.wait()
        resume.clear()

    monkeypatch.setattr(worker, "process_one", process)
    monkeypatch.setattr(worker, "_wait", wait, raising=False)
    async with app.router.lifespan_context(app):
        try:
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app), base_url="http://test"
            ) as client:
                await asyncio.wait_for(waiting.wait(), 2)
                assert (await client.get("/health/ready")).status_code == 200
                broken = True
                waiting.clear()
                resume.set()
                await asyncio.wait_for(waiting.wait(), 2)
                response = await client.get("/health/ready")
                assert response.status_code == 503
                assert response.json()["error"]["code"] == "worker_unavailable"
                assert "private-provider-message" not in response.text
                assert (await client.get("/health/live")).status_code == 200
                broken = False
                waiting.clear()
                resume.set()
                await asyncio.wait_for(waiting.wait(), 2)
                assert (await client.get("/health/ready")).json() == {"status": "ready"}
        finally:
            resume.set()


@pytest.mark.asyncio
async def test_busy_worker_stays_ready_after_healthy_poll(app, monkeypatch):
    app.state.settings.run_worker = True
    worker = app.state.worker
    analyzing = asyncio.Event()
    release = Event()
    loop = asyncio.get_running_loop()
    calls = 0

    def process():
        nonlocal calls
        calls += 1
        if calls == 1:
            return False
        loop.call_soon_threadsafe(analyzing.set)
        if not release.wait(timeout=5):
            raise TimeoutError("test analysis was not released")
        return True

    monkeypatch.setattr(worker, "process_one", process)
    async with app.router.lifespan_context(app):
        try:
            await asyncio.wait_for(analyzing.wait(), 2)
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app), base_url="http://test"
            ) as client:
                assert (await client.get("/health/ready")).status_code == 200
                worker.stop()
                assert (await client.get("/health/ready")).status_code == 503
        finally:
            release.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("recovering", [False, True])
async def test_first_claimed_task_is_ready_during_analysis(
    client, app, child, family_headers, monkeypatch, recovering
):
    response = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
            "input_text": "数学分数",
        },
    )
    assert response.status_code == 202
    app.state.settings.run_worker = True
    worker = app.state.worker
    analyzing = asyncio.Event()
    release = Event()
    loop = asyncio.get_running_loop()
    original = worker.provider.analyze
    failed = False

    def analyze(data):
        loop.call_soon_threadsafe(analyzing.set)
        if not release.wait(timeout=5):
            raise TimeoutError("test analysis was not released")
        return original(data)

    def inject(conn, cursor, statement, parameters, context, executemany):
        nonlocal failed
        if recovering and not failed and statement.startswith("SELECT agent_jobs"):
            failed = True
            raise OperationalError("synthetic claim failure", None, RuntimeError("private"))

    async def fast_wait(delay):
        await asyncio.sleep(0)

    monkeypatch.setattr(worker.provider, "analyze", analyze)
    monkeypatch.setattr(worker, "_wait", fast_wait)
    event.listen(app.state.database.engine, "before_cursor_execute", inject)
    try:
        async with app.router.lifespan_context(app):
            try:
                await asyncio.wait_for(analyzing.wait(), 2)
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app), base_url="http://test"
                ) as probe:
                    assert (await probe.get("/health/ready")).status_code == 200
                assert failed == recovering
            finally:
                worker.stop()
                release.set()
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", inject)


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_dead_worker_not_ready_and_database_disposed(app, monkeypatch, caplog, cancel):
    app.state.settings.run_worker = True
    entered = asyncio.Event()
    dispose = Mock(wraps=app.state.database.engine.dispose)
    monkeypatch.setattr(app.state.database.engine, "dispose", dispose)

    async def exit_worker():
        entered.set()
        if cancel:
            raise asyncio.CancelledError
        raise RuntimeError("secret-never-log-this")

    monkeypatch.setattr(app.state.worker, "run", exit_worker)
    async with app.router.lifespan_context(app):
        await entered.wait()
        await asyncio.sleep(0)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app), base_url="http://test"
        ) as client:
            assert (await client.get("/health/ready")).status_code == 503
            assert (await client.get("/health/live")).status_code == 200
    dispose.assert_called_once()
    assert "secret-never-log-this" not in caplog.text


def test_disabled_worker_keeps_readiness(client):
    assert client.get("/health/ready").json() == {"status": "ready"}


@pytest.mark.asyncio
async def test_enabled_worker_not_started_is_not_ready(app):
    app.state.database.create_schema()
    app.state.settings.run_worker = True
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app), base_url="http://test"
        ) as client:
            assert (await client.get("/health/ready")).status_code == 503
    finally:
        app.state.database.engine.dispose()
