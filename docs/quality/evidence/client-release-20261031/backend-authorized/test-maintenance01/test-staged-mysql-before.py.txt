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
from push_kids.agent_processing.worker import AnalysisWorker
from push_kids.learning.schemas import ConfirmSubmission
from push_kids.learning.service import LearningService
from push_kids.media.store import LocalMediaStore
from push_kids.persistence.models import (
    AgentJob,
    AnalysisStageResult,
    Child,
    Family,
    LearningSubmission,
    Subject,
)
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.time import utcnow
from sqlalchemy import event, func, select, text

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
        assert len(rows) == 2
        db.get(AgentJob, store.job_id).available_at = utcnow() - timedelta(days=3650)
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
    assert provider.calls["extract", "t"] == 1 and provider.calls["merge", "merge"] == 1
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
