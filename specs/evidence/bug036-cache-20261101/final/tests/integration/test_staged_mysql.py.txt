"""Run only against the explicitly configured isolated MySQL runtime fixture."""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from push_kids.agent_processing.checkpoints import StageCheckpoints
from push_kids.agent_processing.contracts import AnalysisProposal, KnowledgeProposal
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.worker import AnalysisWorker
from push_kids.learning.schemas import ConfirmSubmission
from push_kids.learning.service import LearningService
from push_kids.media.store import LocalMediaStore
from push_kids.persistence.models import (
    AgentJob,
    AnalysisStageResult,
    Child,
    Family,
    LearningRecord,
    LearningSubmission,
    Subject,
)
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import utcnow
from sqlalchemy import event, func, select, text, update

from tests.staged_analysis_fakes import StageFake

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="isolated MySQL URL not configured")


def seed():
    database = Database(Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=MYSQL_URL))
    family, child, submission, job = (str(uuid4()) for _ in range(4))
    with database.session_factory() as db:
        db.add(Family(id=family, display_name="synthetic"))
        db.flush()
        db.add(Child(id=child, family_id=family, name="合成测试"))
        db.flush()
        db.add(Subject(family_id=family, child_id=child, name="数学", kind="learning"))
        db.add(
            LearningSubmission(
                id=submission,
                family_id=family,
                child_id=child,
                occurred_at=utcnow(),
                input_text="十以内加法",
                state="analyzing",
            )
        )
        db.flush()
        db.add(
            AgentJob(
                id=job,
                family_id=family,
                submission_id=submission,
                state="running",
                attempts=1,
                lease_until=utcnow() + timedelta(minutes=5),
                available_at=utcnow(),
            )
        )
        db.commit()
        db.expire_all()
        lease = db.get(AgentJob, job).lease_until
    return database, StageCheckpoints(database, family, child, submission, job, 1, lease)


def test_manual_confirm_and_checkpoint_have_consistent_lock_order():
    database, store = seed()
    at_job, continue_job = threading.Event(), threading.Event()

    def before_cursor(conn, cursor, statement, parameters, context, executemany):
        if (
            threading.current_thread().name == "checkpoint-lock-test"
            and statement.startswith("SELECT")
            and "FROM agent_jobs" in statement
            and "FOR UPDATE" in statement
        ):
            at_job.set()
            assert continue_job.wait(3)

    event.listen(database.engine, "before_cursor_execute", before_cursor)

    def checkpoint():
        threading.current_thread().name = "checkpoint-lock-test"
        store.put("t", "a" * 64, {"items": []})

    def confirm():
        with database.session_factory() as db:
            LearningService.confirm(
                db,
                store.family_id,
                store.submission_id,
                ConfirmSubmission(
                    manual_entry=True,
                    proposal=AnalysisProposal(
                        subject_name="数学",
                        summary="练习加法",
                        source="人工录入",
                        knowledge_points=[
                            KnowledgeProposal(
                                name="加法",
                                category="计算",
                                review_method="口头回顾",
                                estimated_minutes=2,
                            )
                        ],
                    ),
                ),
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            saved = pool.submit(checkpoint)
            assert at_job.wait(3)
            confirmed = pool.submit(confirm)
            time.sleep(0.05)
            continue_job.set()
            saved.result(timeout=5)
            confirmed.result(timeout=5)
        with database.session_factory() as db:
            assert db.get(LearningSubmission, store.submission_id).state == "confirmed"
            assert db.get(AgentJob, store.job_id).state == "cancelled"
            assert (
                db.scalar(
                    select(func.count(AnalysisStageResult.id)).where(
                        AnalysisStageResult.family_id == store.family_id
                    )
                )
                == 0
            )
    finally:
        continue_job.set()
        event.remove(database.engine, "before_cursor_execute", before_cursor)
        database.engine.dispose()


def test_mysql_stage_recovery_and_indexes(tmp_path):
    database, store = seed()
    with database.session_factory() as db:
        job = db.get(AgentJob, store.job_id)
        job.state = "queued"
        job.attempts = 0
        job.available_at = utcnow() - timedelta(days=3650)
        db.get(LearningSubmission, store.submission_id).state = "queued"
        db.commit()
    provider = StageFake(fail_stage="match")
    worker = AnalysisWorker(database, provider, LocalMediaStore(tmp_path, 10 * 1024 * 1024))
    assert worker.process_one()
    with database.session_factory() as db:
        rows = db.scalars(
            select(AnalysisStageResult).where(AnalysisStageResult.family_id == store.family_id)
        ).all()
        assert len(rows) == 3
        assert {row.unit_key for row in rows} == {"t", "merge", "review0"}
        assert {(row.family_id, row.child_id, row.submission_id, row.job_id) for row in rows} == {
            (store.family_id, store.child_id, store.submission_id, store.job_id)
        }
        job = db.get(AgentJob, store.job_id)
        assert job.state == "queued" and job.attempts == 1
        assert db.get(LearningSubmission, store.submission_id).state == "queued"
        job.available_at = utcnow() - timedelta(days=3650)
        db.commit()
        plan = (
            db.execute(
                text(
                    "EXPLAIN SELECT id FROM analysis_stage_results "
                    "WHERE family_id=:family AND job_id=:job LIMIT 15"
                ),
                {"family": store.family_id, "job": store.job_id},
            )
            .mappings()
            .one()
        )
        assert "uq_analysis_stage_unit" in (plan["possible_keys"] or "")
    provider.fail_stage = None
    assert worker.process_one()
    assert provider.calls["extract", "t"] == 1
    assert provider.calls["merge", "merge"] == 1
    assert provider.calls["review", "review"] == 1
    assert provider.calls["match", "match"] == 2
    with database.session_factory() as db:
        assert db.get(LearningSubmission, store.submission_id).state == "pending_confirmation"
        assert (
            db.scalar(
                select(func.count(AnalysisStageResult.id)).where(
                    AnalysisStageResult.family_id == store.family_id
                )
            )
            == 0
        )
    database.engine.dispose()


def failed_stage_store():
    database, store = seed()
    for unit in (
        "t",
        "group0",
        "merge",
        "merge-correction",
        "review0",
        "review1",
        "match",
        "reuse",
    ):
        store.put(unit, "a" * 64, {"items": []})
    with database.session_factory() as db:
        db.get(AgentJob, store.job_id).state = "failed"
        db.get(LearningSubmission, store.submission_id).state = "failed"
        db.commit()
    return database, store


def dispose_stage_fixture(database, store):
    # Worker claims across families: do not leave this test's queued jobs for the next case.
    with database.session_factory() as db:
        db.execute(
            update(AgentJob).where(AgentJob.family_id == store.family_id).values(state="cancelled")
        )
        db.commit()
    database.engine.dispose()


@pytest.mark.parametrize("missing_job", [False, True])
def test_concurrent_explicit_retry_has_one_transition_and_preserves_extraction(missing_job):
    database, store = failed_stage_store()
    if missing_job:
        # A legacy submission without a job retains the existing repair path.
        with database.session_factory() as db:
            db.query(AnalysisStageResult).filter(
                AnalysisStageResult.job_id == store.job_id
            ).delete()
            db.delete(db.get(AgentJob, store.job_id))
            db.commit()
    together = threading.Barrier(2)
    lock_order = {}

    def before_cursor(conn, cursor, statement, parameters, context, executemany):
        thread = threading.current_thread().name
        if (
            thread.startswith("retry-concurrency-")
            and statement.startswith("SELECT")
            and "FOR UPDATE" in statement
        ):
            for table in ("families", "children", "agent_jobs", "learning_submissions"):
                if f"FROM {table}" in statement:
                    lock_order.setdefault(thread, []).append(table)
            if "FROM families" in statement:
                together.wait(timeout=5)

    def retry(index):
        threading.current_thread().name = f"retry-concurrency-{index}"
        with database.session_factory() as db:
            try:
                return LearningService.retry(db, store.family_id, store.submission_id).state
            except ConflictError:
                db.rollback()
                return "conflict"

    event.listen(database.engine, "before_cursor_execute", before_cursor)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(retry, [0, 1]))
        assert sorted(outcomes) == ["conflict", "queued"]
        assert all(
            order == ["families", "children", "agent_jobs", "learning_submissions"]
            for order in lock_order.values()
        )
        assert len(lock_order) == 2
        with database.session_factory() as db:
            jobs = db.scalars(
                select(AgentJob).where(
                    AgentJob.family_id == store.family_id,
                    AgentJob.submission_id == store.submission_id,
                )
            ).all()
            assert len(jobs) == 1 and jobs[0].state == "queued" and jobs[0].attempts == 0
            keys = set(
                db.scalars(
                    select(AnalysisStageResult.unit_key).where(
                        AnalysisStageResult.family_id == store.family_id,
                        AnalysisStageResult.submission_id == store.submission_id,
                    )
                )
            )
            assert keys == (set() if missing_job else {"t", "group0"})
    finally:
        event.remove(database.engine, "before_cursor_execute", before_cursor)
        dispose_stage_fixture(database, store)


def test_retry_and_late_checkpoint_use_same_locks_without_resurrecting_cache():
    database, store = failed_stage_store()
    at_job, continue_job, at_checkpoint = threading.Event(), threading.Event(), threading.Event()
    lock_order = {}

    def before_cursor(conn, cursor, statement, parameters, context, executemany):
        thread = threading.current_thread().name
        if thread in {"retry-lock-test", "late-checkpoint-test"} and "FOR UPDATE" in statement:
            for table in ("families", "children", "agent_jobs", "learning_submissions"):
                if f"FROM {table}" in statement:
                    lock_order.setdefault(thread, []).append(table)
            if thread == "retry-lock-test" and "FROM agent_jobs" in statement:
                at_job.set()
                assert continue_job.wait(5)
            if thread == "late-checkpoint-test" and "FROM families" in statement:
                at_checkpoint.set()

    def retry():
        threading.current_thread().name = "retry-lock-test"
        with database.session_factory() as db:
            return LearningService.retry(db, store.family_id, store.submission_id).state

    def checkpoint():
        threading.current_thread().name = "late-checkpoint-test"
        with pytest.raises(StageFailure, match="lease_changed"):
            store.put("review1", "b" * 64, {"passed": True, "issues": []})

    event.listen(database.engine, "before_cursor_execute", before_cursor)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            retried = pool.submit(retry)
            assert at_job.wait(5)
            late = pool.submit(checkpoint)
            assert at_checkpoint.wait(5)
            continue_job.set()
            assert retried.result(timeout=5) == "queued"
            late.result(timeout=5)
        assert all(
            order == ["families", "children", "agent_jobs", "learning_submissions"]
            for order in lock_order.values()
        )
        with database.session_factory() as db:
            assert set(
                db.scalars(
                    select(AnalysisStageResult.unit_key).where(
                        AnalysisStageResult.submission_id == store.submission_id
                    )
                )
            ) == {"t", "group0"}
    finally:
        continue_job.set()
        event.remove(database.engine, "before_cursor_execute", before_cursor)
        dispose_stage_fixture(database, store)


def test_retry_purge_and_state_reset_rollback_on_mysql(monkeypatch):
    from sqlalchemy.exc import OperationalError

    database, store = failed_stage_store()
    try:
        with database.session_factory() as db:

            def fail_commit():
                assert db.get(LearningSubmission, store.submission_id).state == "queued"
                assert set(
                    db.scalars(
                        select(AnalysisStageResult.unit_key).where(
                            AnalysisStageResult.submission_id == store.submission_id
                        )
                    )
                ) == {"t", "group0"}
                raise OperationalError("synthetic commit", None, RuntimeError("synthetic"))

            monkeypatch.setattr(db, "commit", fail_commit)
            with pytest.raises(OperationalError):
                LearningService.retry(db, store.family_id, store.submission_id)
            db.rollback()
        with database.session_factory() as db:
            assert db.get(AgentJob, store.job_id).state == "failed"
            assert db.get(LearningSubmission, store.submission_id).state == "failed"
            assert (
                db.scalar(
                    select(func.count(AnalysisStageResult.id)).where(
                        AnalysisStageResult.submission_id == store.submission_id
                    )
                )
                == 8
            )
    finally:
        dispose_stage_fixture(database, store)


def test_retry_cannot_delete_other_family_or_submission_stages():
    database, store = failed_stage_store()
    foreign_database, foreign = failed_stage_store()
    try:
        with database.session_factory() as db:
            with pytest.raises(NotFoundError):
                LearningService.retry(db, foreign.family_id, store.submission_id)
            db.rollback()
            assert LearningService.retry(db, store.family_id, store.submission_id).state == "queued"
        with database.session_factory() as db:
            assert (
                db.scalar(
                    select(func.count(AnalysisStageResult.id)).where(
                        AnalysisStageResult.submission_id == foreign.submission_id
                    )
                )
                == 8
            )
            assert db.get(LearningSubmission, foreign.submission_id).state == "failed"
            assert (
                db.scalar(
                    select(func.count(AnalysisStageResult.id)).where(
                        AnalysisStageResult.submission_id == store.submission_id
                    )
                )
                == 2
            )
    finally:
        dispose_stage_fixture(database, store)
        dispose_stage_fixture(foreign_database, foreign)


def test_mysql_final_refusal_stops_and_explicit_retry_reuses_extraction(tmp_path):
    database, store = seed()
    provider = StageFake(review_failures=99)
    worker = AnalysisWorker(database, provider, LocalMediaStore(tmp_path, 10 * 1024 * 1024))
    try:
        with database.session_factory() as db:
            job = db.get(AgentJob, store.job_id)
            job.state, job.attempts = "queued", 0
            job.available_at = utcnow() - timedelta(days=3650)
            db.get(LearningSubmission, store.submission_id).state = "queued"
            db.commit()
        assert worker.process_one()
        assert not worker.process_one()
        with database.session_factory() as db:
            job = db.get(AgentJob, store.job_id)
            assert job.state == "failed" and job.attempts == 1
            assert (
                db.get(LearningSubmission, store.submission_id).error_code
                == "analysis_output_invalid"
            )
            assert set(
                db.scalars(
                    select(AnalysisStageResult.unit_key).where(
                        AnalysisStageResult.submission_id == store.submission_id
                    )
                )
            ) == {"t"}
            LearningService.retry(db, store.family_id, store.submission_id)
            job.available_at = utcnow() - timedelta(days=3650)
            db.commit()
        provider.review_failures = 0
        assert worker.process_one()
        assert provider.calls["extract", "t"] == 1 and provider.review_calls == 3
        with database.session_factory() as db:
            assert db.get(AgentJob, store.job_id).state == "succeeded"
            assert db.get(LearningSubmission, store.submission_id).state == "pending_confirmation"
            assert (
                db.scalar(
                    select(func.count(LearningRecord.id)).where(
                        LearningRecord.family_id == store.family_id
                    )
                )
                == 0
            )
    finally:
        database.engine.dispose()
