import asyncio
import logging
from datetime import timedelta

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisCapabilityError,
    AnalysisDeadlineExceededError,
    AnalysisInputError,
    AnalysisOutputExhaustedError,
)
from push_kids.agent_processing.runner import AnalysisAgentRunner
from push_kids.agent_processing.worker import (
    JOB_LEASE_DURATION,
    JOB_LEASE_WRITEBACK_RESERVE_SECONDS,
)
from push_kids.persistence.models import AgentJob, LearningRecord, LearningSubmission
from push_kids.platform.errors import DependencyError
from push_kids.platform.time import utcnow
from sqlalchemy import event, func, select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def add_jobs(app, child, family_headers, texts=("bad", "good")):
    ids = []
    with app.state.database.session_factory() as db:
        for index, text in enumerate(texts):
            submission = LearningSubmission(
                family_id=family_headers["X-Family-ID"],
                child_id=child["id"],
                occurred_at=utcnow(),
                input_text=text,
            )
            db.add(submission)
            db.flush()
            job = AgentJob(
                family_id=submission.family_id,
                submission_id=submission.id,
                created_at=utcnow() + timedelta(seconds=index),
            )
            db.add(job)
            db.flush()
            ids.append(job.id)
        db.commit()
    return ids


def test_analysis_stage_logs_are_complete_and_safe(client, app, child, family_headers, caplog):
    ids = add_jobs(app, child, family_headers, texts=("private-child-content",))
    caplog.set_level(logging.INFO, logger="push_kids.worker")

    assert app.state.worker.process_one()

    expected = [
        "analysis_attempt_started",
        "analysis_media_query_started",
        "analysis_media_query_completed",
        "analysis_media_materialize_started",
        "analysis_media_materialize_completed",
        "analysis_context_build_started",
        "analysis_context_build_completed",
        "analysis_provider_started",
        "analysis_provider_completed",
        "analysis_writeback_started",
        "analysis_writeback_completed",
    ]
    positions = [caplog.text.index(event_name) for event_name in expected]
    assert positions == sorted(positions)
    assert "duration_ms=" in caplog.text
    assert ids[0] in caplog.text
    assert "private-child-content" not in caplog.text


def test_worker_derives_provider_budget_from_remaining_job_lease(
    client, app, child, family_headers, monkeypatch
):
    add_jobs(app, child, family_headers, texts=("lease budget",))
    original_run = AnalysisAgentRunner.run
    captured: dict[str, float] = {}

    def capture_budget(self, data, **kwargs):
        captured["seconds"] = kwargs["time_budget_seconds"]
        return original_run(self, data, **kwargs)

    monkeypatch.setattr(AnalysisAgentRunner, "run", capture_budget)

    assert app.state.worker.process_one()

    full_budget = JOB_LEASE_DURATION.total_seconds() - JOB_LEASE_WRITEBACK_RESERVE_SECONDS
    assert full_budget - 5 <= captured["seconds"] <= full_budget


def test_failed_stage_log_contains_only_safe_diagnostics(
    client, app, child, family_headers, monkeypatch, caplog
):
    ids = add_jobs(app, child, family_headers, texts=("private-child-content",))
    caplog.set_level(logging.INFO, logger="push_kids.worker")

    def fail_provider(_data, _search_history, *, max_turns):
        del max_turns
        raise RuntimeError("private-provider-response")

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", fail_provider)
    assert app.state.worker.process_one()

    assert "analysis_provider_started" in caplog.text
    assert "analysis_provider_completed" not in caplog.text
    assert (
        f"analysis_job_failed job_id={ids[0]} attempt=1 max_attempts=3 "
        "stage=provider error_type=RuntimeError"
    ) in caplog.text
    assert "analysis_job_requeued" in caplog.text
    assert "private-child-content" not in caplog.text
    assert "private-provider-response" not in caplog.text


@pytest.mark.asyncio
async def test_sql_failure_does_not_stop_next_tasks(
    client, app, child, family_headers, monkeypatch, caplog
):
    ids = add_jobs(app, child, family_headers)
    worker = app.state.worker
    failed = False
    completed = 0
    loop = asyncio.get_running_loop()

    def inject(conn, cursor, statement, parameters, context, executemany):
        nonlocal failed
        if not failed and statement.startswith("SELECT agent_jobs"):
            failed = True
            raise OperationalError(
                "private SQL", {"secret": "never-log-me"}, RuntimeError("child-content")
            )

    original = worker.process_one

    def process():
        nonlocal completed
        result = original()
        if result:
            completed += 1
            if completed == 2:
                loop.call_soon_threadsafe(worker.stop)
        return result

    async def fast_wait(delay):
        await asyncio.sleep(0)

    monkeypatch.setattr(worker, "process_one", process)
    monkeypatch.setattr(worker, "_wait", fast_wait, raising=False)
    event.listen(app.state.database.engine, "before_cursor_execute", inject)
    try:
        await asyncio.wait_for(worker.run(), 5)
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", inject)
    assert failed and completed == 2
    with app.state.database.session_factory() as db:
        assert [db.get(AgentJob, key).state for key in ids] == ["succeeded", "succeeded"]
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
    assert "worker_iteration_failed" in caplog.text
    assert "private SQL" not in caplog.text and "never-log-me" not in caplog.text
    assert "child-content" not in caplog.text


@pytest.mark.asyncio
async def test_backoff_caps_and_resets_after_healthy_poll(app, monkeypatch):
    worker = app.state.worker
    outcomes = iter([True] * 7 + [False, True, False])
    delays = []

    def process():
        if next(outcomes):
            raise RuntimeError("synthetic")
        if len(delays) == 9:
            worker.stop()
        return False

    async def wait(delay):
        delays.append(delay)

    monkeypatch.setattr(worker, "process_one", process)
    monkeypatch.setattr(worker, "_wait", wait, raising=False)
    await asyncio.wait_for(worker.run(), 5)
    assert delays == [1, 2, 4, 8, 16, 30, 30, worker.poll_seconds, 1, worker.poll_seconds]
    assert not worker.is_ready


@pytest.mark.parametrize("phase", ["query", "commit"])
def test_cleanup_failure_is_isolated_and_throttled(
    client, app, child, family_headers, monkeypatch, phase
):
    ids = add_jobs(app, child, family_headers)
    worker = app.state.worker
    attempts = 0

    def cleanup():
        nonlocal attempts
        attempts += 1
        # An exception at either boundary must release the cleanup session.
        with app.state.database.session_factory() as db:
            if phase == "query":
                raise OperationalError("synthetic query", None, RuntimeError("private"))
            db.flush()
            raise OperationalError("synthetic commit", None, RuntimeError("private"))

    monkeypatch.setattr(worker, "_cleanup_expired_media", cleanup)
    assert worker.process_one()
    assert worker.process_one()
    assert attempts == 1
    with app.state.database.session_factory() as db:
        assert [db.get(AgentJob, key).state for key in ids] == ["succeeded", "succeeded"]


def test_preparation_error_is_bounded_and_next_job_runs(client, app, child, family_headers):
    ids = add_jobs(app, child, family_headers)
    with app.state.database.session_factory() as db:
        bad_submission = db.get(AgentJob, ids[0]).submission_id

    def fail_context_read(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("SELECT submission_media") and bad_submission in parameters:
            raise ValueError("invalid context")

    worker = app.state.worker
    event.listen(app.state.database.engine, "before_cursor_execute", fail_context_read)
    try:
        assert worker.process_one()
        assert worker.process_one()
        for _ in range(2):
            with app.state.database.session_factory() as db:
                db.get(AgentJob, ids[0]).available_at = utcnow()
                db.commit()
            assert worker.process_one()
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", fail_context_read)
    with app.state.database.session_factory() as db:
        assert db.get(AgentJob, ids[0]).state == "failed"
        assert db.get(AgentJob, ids[0]).attempts == 3
        assert db.get(AgentJob, ids[1]).state == "succeeded"


def test_invalid_structured_output_retries_three_times_before_terminal_failure(
    client, app, child, family_headers, monkeypatch
):
    ids = add_jobs(app, child, family_headers, texts=("private-invalid-output",))

    def fail_validation(_data, _search_history, *, max_turns):
        del max_turns
        raise AnalysisOutputExhaustedError()

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", fail_validation)
    for attempt in range(1, 4):
        assert app.state.worker.process_one()
        with app.state.database.session_factory() as db:
            job = db.get(AgentJob, ids[0])
            assert job.attempts == attempt
            if attempt < 3:
                assert job.state == "queued"
                db.execute(
                    update(AgentJob).where(AgentJob.id == job.id).values(available_at=utcnow())
                )
                db.commit()
    assert not app.state.worker.process_one()

    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        assert job.state == "failed"
        assert job.attempts == 3
        assert submission.state == "failed"
        assert submission.error_code == "analysis_output_invalid"
        assert submission.proposal_json is None
        assert job.error_message == (
            "code=analysis_output_invalid;reason=turn_budget;validation=none"
        )


def test_worker_persists_only_safe_internal_validation_diagnostic(
    client, app, child, family_headers, monkeypatch
):
    ids = add_jobs(app, child, family_headers, texts=("private-invalid-output",))

    def fail_validation(_data, _search_history, *, max_turns):
        del max_turns
        raise AnalysisOutputExhaustedError(
            reason="output_validation",
            codes=["history_search.incomplete", "SECRET_PRIVATE_CODE"],
        )

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", fail_validation)
    assert app.state.worker.process_one()

    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        assert job.error_message == (
            "code=analysis_output_invalid;reason=output_validation;"
            "validation=history_search.incomplete,validation.other"
        )
        assert "SECRET" not in job.error_message
        assert submission.error_message is None


def test_fresh_ready_job_precedes_an_older_requeued_job(client, app, child, family_headers):
    old_job_id, fresh_job_id = add_jobs(
        app,
        child,
        family_headers,
        texts=("old retry", "fresh ready"),
    )
    now = utcnow()
    with app.state.database.session_factory() as db:
        old_job = db.get(AgentJob, old_job_id)
        fresh_job = db.get(AgentJob, fresh_job_id)
        old_job.attempts = 1
        old_job.available_at = now - timedelta(seconds=1)
        fresh_job.available_at = now - timedelta(seconds=2)
        db.commit()

    assert app.state.worker.process_one()

    with app.state.database.session_factory() as db:
        assert db.get(AgentJob, fresh_job_id).state == "succeeded"
        assert db.get(AgentJob, old_job_id).state == "queued"


@pytest.mark.parametrize(
    ("failure", "error_code"),
    [
        (AnalysisCapabilityError(), "analysis_schema_unsupported"),
        (AnalysisInputError("deterministic"), "analysis_failed"),
    ],
)
def test_non_retryable_analysis_failure_stops_after_first_attempt(
    client, app, child, family_headers, monkeypatch, failure, error_code
):
    ids = add_jobs(app, child, family_headers, texts=("private-invalid-input",))

    def fail_provider(_data, _search_history, *, max_turns):
        del max_turns
        raise failure

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", fail_provider)
    assert app.state.worker.process_one()
    assert not app.state.worker.process_one()

    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        assert job.state == "failed"
        assert job.attempts == 1
        assert submission.state == "failed"
        assert submission.error_code == error_code


@pytest.mark.parametrize(
    "failure",
    [AnalysisDeadlineExceededError(), DependencyError("private-provider-detail")],
)
def test_timeout_and_transport_failures_retry_three_times_with_generic_final_code(
    client, app, child, family_headers, monkeypatch, failure
):
    ids = add_jobs(app, child, family_headers, texts=("private-retryable-input",))

    def fail_provider(_data, _search_history, *, max_turns):
        del max_turns
        raise failure

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", fail_provider)
    for attempt in range(1, 4):
        assert app.state.worker.process_one()
        with app.state.database.session_factory() as db:
            job = db.get(AgentJob, ids[0])
            assert job.attempts == attempt
            if attempt < 3:
                assert job.state == "queued"
                db.execute(
                    update(AgentJob).where(AgentJob.id == job.id).values(available_at=utcnow())
                )
                db.commit()

    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        assert job.state == "failed"
        assert submission.state == "failed"
        assert submission.error_code == "analysis_failed"
        assert "private" not in (submission.error_message or "")


def test_persisted_second_precision_lease_is_used_for_writeback(
    client, app, child, family_headers, monkeypatch
):
    ids = add_jobs(app, child, family_headers, texts=("precision regression",))
    original_commit = Session.commit
    truncated = False

    def commit_with_mysql_precision(session):
        nonlocal truncated
        original_commit(session)
        if truncated:
            return
        running = next(
            (
                item
                for item in session.identity_map.values()
                if isinstance(item, AgentJob)
                and item.state == "running"
                and item.lease_until is not None
            ),
            None,
        )
        if running is None:
            return
        persisted = running.lease_until.replace(microsecond=0)
        with app.state.database.engine.begin() as connection:
            connection.execute(
                update(AgentJob)
                .where(AgentJob.id == running.id)
                .values(lease_until=persisted)
                .execution_options(synchronize_session=False)
            )
        truncated = True

    monkeypatch.setattr(Session, "commit", commit_with_mysql_precision)

    assert app.state.worker.process_one()
    assert truncated
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        assert job.state == "succeeded"
        assert job.attempts == 1
        assert db.get(LearningSubmission, job.submission_id).state == "pending_confirmation"


def test_expired_job_at_attempt_limit_becomes_terminal_without_provider_call(
    client, app, child, family_headers, monkeypatch, caplog
):
    ids = add_jobs(app, child, family_headers, texts=("exhausted",))
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        job.state = "running"
        job.attempts = job.max_attempts
        job.lease_until = utcnow() - timedelta(seconds=1)
        submission.state = "analyzing"
        db.commit()

    def unexpected_provider_call(_data, _search_history, *, max_turns):
        del max_turns
        raise AssertionError("provider must not run for an exhausted job")

    monkeypatch.setattr(app.state.worker.provider, "analyze_with_history", unexpected_provider_call)
    caplog.set_level(logging.WARNING, logger="push_kids.worker")

    assert app.state.worker.process_one()
    assert not app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, ids[0])
        submission = db.get(LearningSubmission, job.submission_id)
        assert job.state == "failed"
        assert job.attempts == job.max_attempts == 3
        assert submission.state == "failed"
        assert submission.error_code == "analysis_failed"
    assert "stage=lease_recovery_exhausted" in caplog.text


@pytest.mark.asyncio
async def test_writeback_failure_keeps_lease_and_recovers(
    client, app, child, family_headers, monkeypatch
):
    ids = add_jobs(app, child, family_headers)
    worker = app.state.worker
    failed = False
    original = worker.process_one
    iterations = 0
    loop = asyncio.get_running_loop()

    def fail_commit(session):
        nonlocal failed
        if not failed and any(
            isinstance(item, AgentJob) and item.state == "succeeded" for item in session.dirty
        ):
            failed = True
            raise OperationalError("synthetic commit", None, RuntimeError("private"))

    def process():
        nonlocal iterations
        result = original()
        iterations += 1
        if iterations == 1:
            with app.state.database.session_factory() as db:
                assert db.get(AgentJob, ids[0]).state == "running"
                assert db.get(AgentJob, ids[1]).state == "succeeded"
                db.get(AgentJob, ids[0]).lease_until = utcnow() - timedelta(seconds=1)
                db.commit()
        elif iterations == 2:
            loop.call_soon_threadsafe(worker.stop)
        return result

    async def fast_wait(delay):
        await asyncio.sleep(0)

    monkeypatch.setattr(worker, "process_one", process)
    monkeypatch.setattr(worker, "_wait", fast_wait, raising=False)
    event.listen(Session, "before_commit", fail_commit)
    try:
        await asyncio.wait_for(worker.run(), 5)
    finally:
        event.remove(Session, "before_commit", fail_commit)
    with app.state.database.session_factory() as db:
        assert [db.get(AgentJob, key).state for key in ids] == ["succeeded", "succeeded"]
        assert db.get(AgentJob, ids[0]).attempts == 2
        assert db.scalar(select(func.count()).select_from(AgentJob)) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_stop_or_cancel_interrupts_backoff(app, monkeypatch, cancel):
    worker = app.state.worker

    def fail():
        raise RuntimeError("synthetic")

    monkeypatch.setattr(worker, "process_one", fail)
    task = asyncio.create_task(worker.run())
    try:
        # Wait until the run loop has observed the failure and entered its real wait.
        for _ in range(100):
            await asyncio.sleep(0.001)
            if getattr(worker, "_consecutive_failures", 0):
                break
        assert not task.done()
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            worker.stop()
            await asyncio.wait_for(task, 0.2)
        assert not worker.is_ready
    finally:
        if not task.done():
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
