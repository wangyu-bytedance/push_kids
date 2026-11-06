from datetime import timedelta

import pytest
from push_kids.agent_processing.checkpoints import StageCheckpoints, expire_stages, purge_stages
from push_kids.agent_processing.failures import StageFailure
from push_kids.persistence.models import (
    AgentJob,
    AnalysisStageResult,
    Child,
    KnowledgeItem,
    LearningRecord,
    LearningSubmission,
)
from push_kids.platform.time import utcnow
from sqlalchemy import func, select

from tests.staged_analysis_fakes import StageFake, audited_consolidation

DECISION_UNITS = {"classify", "merge", "merge-correction", "review0", "review1", "match", "reuse"}
EXTRACTION_UNITS = {"t", "m1", "m9", "group0", "group1"}


def submit(client, headers, child):
    response = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
            "input_text": "十以内加法",
        },
    )
    assert response.status_code == 202
    return response.json()["id"]


def test_retry_resumes_validated_stages_without_formal_writes(client, app, family_headers, child):
    sid = submit(client, family_headers, child)
    provider = StageFake(fail_stage="match")
    app.state.worker.provider = provider
    assert app.state.worker.process_one()
    database = app.state.database
    with database.session_factory() as db:
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 3
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert job.attempts == 1 and job.state == "queued"
        job.available_at = utcnow()
        db.commit()
    provider.fail_stage = None
    assert app.state.worker.process_one()
    with database.session_factory() as db:
        assert db.get(LearningSubmission, sid).state == "pending_confirmation"
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 0
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 0
    assert provider.calls["extract", "t"] == 1
    assert provider.calls["merge", "merge"] == 1
    assert provider.calls["review", "review"] == 1
    assert provider.calls["match", "match"] == 2


@pytest.mark.parametrize("action", ["retry", "cancel"])
def test_reviewed_empty_source_is_terminal_and_keeps_parent_recovery(
    client, app, family_headers, child, action
):
    class NoSpecificGoal(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            value = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "extract":
                value.items, value.needs_context = [], True
            elif stage == "merge":
                return audited_consolidation(payload, items=[], summary="请补充具体学习对象")
            return value

    sid = submit(client, family_headers, child)
    provider = NoSpecificGoal()
    app.state.worker.provider = provider
    assert app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        submission = db.get(LearningSubmission, sid)
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert submission.state == job.state == "failed"
        assert job.attempts == 1 and submission.proposal_json is None
        assert submission.error_code == "analysis_output_invalid"
        assert "stage=review;unit=empty_proposal" in job.error_message
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 0
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
    assert not app.state.worker.process_one()
    assert not any(stage == "match" for stage, _ in provider.calls)

    response = client.post(f"/api/v1/submissions/{sid}/{action}", headers=family_headers)
    assert response.status_code == 200
    with app.state.database.session_factory() as db:
        keys = stage_keys(db, sid)
        assert keys == ({"t"} if action == "retry" else set())
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert job.state == ("queued" if action == "retry" else "cancelled")


def test_checkpoint_initialization_time_is_deducted_from_provider_budget(
    client, app, family_headers, child, monkeypatch
):
    from push_kids.agent_processing import worker

    sid = submit(client, family_headers, child)
    app.state.worker.provider = StageFake()
    clock = [utcnow()]
    observed = []
    original_store = worker.StageCheckpoints
    original_run = worker.AnalysisAgentRunner.run

    def delayed_store(*args, **kwargs):
        store = original_store(*args, **kwargs)
        clock[0] += timedelta(seconds=75)
        return store

    def observe_budget(self, *args, **kwargs):
        observed.append(kwargs["time_budget_seconds"])
        return original_run(self, *args, **kwargs)

    monkeypatch.setattr(worker, "utcnow", lambda: clock[0])
    monkeypatch.setattr(worker, "StageCheckpoints", delayed_store)
    monkeypatch.setattr(worker.AnalysisAgentRunner, "run", observe_budget)
    assert app.state.worker.process_one()
    assert observed == [195.0]
    with app.state.database.session_factory() as db:
        assert db.get(LearningSubmission, sid).state == "pending_confirmation"


def make_store(client, app, headers, child):
    sid = submit(client, headers, child)
    with app.state.database.session_factory() as db:
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        job.state, job.attempts, job.lease_until = "running", 1, utcnow() + timedelta(minutes=5)
        db.get(LearningSubmission, sid).state = "analyzing"
        db.commit()
        return StageCheckpoints(
            app.state.database, headers["X-Family-ID"], child["id"], sid, job.id, 1, job.lease_until
        )


@pytest.mark.parametrize("change", ["cancel", "lease", "child_deleting"])
def test_late_checkpoint_cannot_resurrect_state(client, app, family_headers, child, change):
    store = make_store(client, app, family_headers, child)
    with app.state.database.session_factory() as db:
        if change == "cancel":
            db.get(LearningSubmission, store.submission_id).state = "cancelled"
        elif change == "lease":
            db.get(AgentJob, store.job_id).attempts = 2
        else:
            db.get(Child, child["id"]).deleting = True
        db.commit()
    with pytest.raises(StageFailure, match="lease_changed"):
        store.put("t", "a" * 64, {"items": []})


def test_stage_ttl_scope_and_capacity(client, app, family_headers, child):
    store = make_store(client, app, family_headers, child)
    store.put("t", "a" * 64, {"items": []})
    assert store.get("t", "b" * 64) is None
    assert store.get("t", "a" * 64) == {"items": []}
    with pytest.raises(StageFailure, match="capacity"):
        store.put("huge", "a" * 64, {"value": "x" * 65536})
    with app.state.database.session_factory() as db:
        purge_stages(db, "foreign-family")
        db.commit()
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 1
        row = db.scalar(select(AnalysisStageResult))
        row.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert expire_stages(app.state.database) == 1
    assert expire_stages(app.state.database) == 0


def test_cancel_purges_stage_results(client, app, family_headers, child):
    store = make_store(client, app, family_headers, child)
    store.put("t", "a" * 64, {"items": []})
    response = client.post(
        f"/api/v1/submissions/{store.submission_id}/cancel", headers=family_headers
    )
    assert response.status_code == 200
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 0


def test_manual_confirmation_purges_stage_results(client, app, family_headers, child):
    from push_kids.agent_processing.contracts import AnalysisProposal, KnowledgeProposal
    from push_kids.learning.schemas import ConfirmSubmission
    from push_kids.learning.service import LearningService

    store = make_store(client, app, family_headers, child)
    store.put("t", "a" * 64, {"items": []})
    with app.state.database.session_factory() as db:
        LearningService.confirm(
            db,
            family_headers["X-Family-ID"],
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
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 0
        assert db.get(AgentJob, store.job_id).state == "cancelled"


def test_all_eighteen_successful_units_fit_and_nineteenth_is_rejected(
    client, app, family_headers, child
):
    store = make_store(client, app, family_headers, child)
    for index in range(18):
        store.put(f"unit{index}", "a" * 64, {"items": []})
    reloaded = StageCheckpoints(
        app.state.database,
        store.family_id,
        store.child_id,
        store.submission_id,
        store.job_id,
        store.attempt,
        store.lease,
    )
    assert len(reloaded.rows) == 18
    assert reloaded.get("unit17", "a" * 64) == {"items": []}
    with pytest.raises(StageFailure, match="capacity"):
        reloaded.put("unit18", "a" * 64, {"items": []})
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 18


def test_checkpoint_aggregate_bytes_and_revision_are_still_bounded(
    client, app, family_headers, child
):
    from push_kids.agent_processing.stage_contracts import PIPELINE_REVISION

    store = make_store(client, app, family_headers, child)
    for index in range(8):
        store.put(f"unit{index}", "a" * 64, {"value": "x" * 64000})
    with pytest.raises(StageFailure, match="capacity"):
        store.put("overflow", "a" * 64, {"value": "x" * 64000})
    with app.state.database.session_factory() as db:
        row = db.scalar(select(AnalysisStageResult).where(AnalysisStageResult.unit_key == "unit0"))
        row.revision = "staged-previous-revision"
        db.commit()
    reloaded = StageCheckpoints(
        app.state.database,
        store.family_id,
        store.child_id,
        store.submission_id,
        store.job_id,
        store.attempt,
        store.lease,
    )
    assert reloaded.get("unit0", "a" * 64) is None
    assert reloaded.rows["unit1"].revision == PIPELINE_REVISION


def test_maximum_recovered_pipeline_stores_eighteen_validated_keys_without_formal_records(
    client, app, family_headers, child, tmp_path
):
    import asyncio
    from time import monotonic

    from push_kids.agent_processing.contracts import AnalysisInput, ExistingKnowledgeContext
    from push_kids.agent_processing.pipeline import StagedPipeline
    from push_kids.agent_processing.telemetry import AnalysisTrace

    from tests.staged_analysis_fakes import MaximumStages

    store = make_store(client, app, family_headers, child)
    images = [tmp_path / f"page{index}.png" for index in range(9)]
    for index, path in enumerate(images):
        path.write_bytes(f"synthetic-{index}".encode())
    data = AnalysisInput(
        text="十以内加法",
        image_paths=images,
        existing_subjects=["数学"],
        existing_knowledge=[
            ExistingKnowledgeContext(
                knowledge_id="synthetic-known",
                subject_name="数学",
                name="十以内加法",
                category="计算",
            )
        ],
    )
    pipeline = StagedPipeline(MaximumStages(recover=True), AnalysisTrace.disabled(), store)
    result = asyncio.run(pipeline.run(data, lambda _: [], monotonic() + 10))
    assert len(result.todo_matches) == 1 and pipeline.calls == 33
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 18
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 0
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
    reused = StagedPipeline(MaximumStages(recover=True), AnalysisTrace.disabled(), store)
    second = asyncio.run(reused.run(data, lambda _: [], monotonic() + 10))
    assert len(second.todo_matches) == 1 and reused.calls == 0


def seed_failed_stages(client, app, headers, child):
    store = make_store(client, app, headers, child)
    for unit in DECISION_UNITS | EXTRACTION_UNITS:
        store.put(unit, "a" * 64, {"items": []})
    with app.state.database.session_factory() as db:
        db.get(AgentJob, store.job_id).state = "failed"
        submission = db.get(LearningSubmission, store.submission_id)
        submission.state = "failed"
        submission.error_code, submission.error_message = "analysis_output_invalid", "safe failure"
        db.commit()
    return store


def stage_keys(db, submission_id):
    return set(
        db.scalars(
            select(AnalysisStageResult.unit_key).where(
                AnalysisStageResult.submission_id == submission_id
            )
        )
    )


def test_explicit_retry_refreshes_only_own_semantic_branch(client, app, family_headers, child):
    store = seed_failed_stages(client, app, family_headers, child)
    sibling = seed_failed_stages(client, app, family_headers, child)
    foreign = seed_failed_stages(
        client,
        app,
        {"X-Family-ID": "foreign-family"},
        {
            "id": client.post(
                "/api/v1/children",
                headers={"X-Family-ID": "foreign-family"},
                json={"name": "合成孩子"},
            ).json()["id"]
        },
    )
    with app.state.database.session_factory() as db:
        for row in db.scalars(
            select(AnalysisStageResult).where(
                AnalysisStageResult.submission_id == store.submission_id,
                AnalysisStageResult.unit_key.in_(DECISION_UNITS),
            )
        ):
            row.revision = "staged-20261031-06"
        db.commit()
    response = client.post(
        f"/api/v1/submissions/{store.submission_id}/retry",
        headers={"X-Family-ID": "foreign-family"},
    )
    assert response.status_code == 404
    response = client.post(
        f"/api/v1/submissions/{store.submission_id}/retry", headers=family_headers
    )
    assert response.status_code == 200 and response.json()["state"] == "queued"
    assert (
        client.post(
            f"/api/v1/submissions/{store.submission_id}/retry", headers=family_headers
        ).status_code
        == 409
    )
    with app.state.database.session_factory() as db:
        assert stage_keys(db, store.submission_id) == EXTRACTION_UNITS
        assert stage_keys(db, sibling.submission_id) == DECISION_UNITS | EXTRACTION_UNITS
        assert stage_keys(db, foreign.submission_id) == DECISION_UNITS | EXTRACTION_UNITS
        job = db.get(AgentJob, store.job_id)
        assert job.state == "queued" and job.attempts == 0 and job.error_message is None
        assert db.get(LearningSubmission, store.submission_id).error_code is None


def test_retry_deletion_and_state_reset_roll_back_together(
    client, app, family_headers, child, monkeypatch
):
    from push_kids.learning.service import LearningService
    from sqlalchemy.exc import OperationalError

    store = seed_failed_stages(client, app, family_headers, child)
    with app.state.database.session_factory() as db:

        def fail_commit():
            raise OperationalError("synthetic commit", None, RuntimeError("synthetic"))

        monkeypatch.setattr(db, "commit", fail_commit)
        with pytest.raises(OperationalError):
            LearningService.retry(db, store.family_id, store.submission_id)
        db.rollback()
    with app.state.database.session_factory() as db:
        assert stage_keys(db, store.submission_id) == DECISION_UNITS | EXTRACTION_UNITS
        assert db.get(AgentJob, store.job_id).state == "failed"
        assert db.get(LearningSubmission, store.submission_id).state == "failed"


@pytest.mark.parametrize("change", ["family", "child_deleting", "archived"])
def test_retry_rechecks_scope_before_purging(client, app, family_headers, child, change):
    from push_kids.persistence.models import Family

    store = seed_failed_stages(client, app, family_headers, child)
    with app.state.database.session_factory() as db:
        if change == "family":
            family = db.get(Family, store.family_id)
            if family is None:
                family = Family(id=store.family_id, display_name="合成家庭")
                db.add(family)
            family.status = "deleting"
        else:
            row = db.get(Child, store.child_id)
            if change == "child_deleting":
                row.deleting = True
            else:
                row.active = False
        db.commit()
    response = client.post(
        f"/api/v1/submissions/{store.submission_id}/retry", headers=family_headers
    )
    assert response.status_code == (200 if change == "archived" else 409)
    with app.state.database.session_factory() as db:
        assert stage_keys(db, store.submission_id) == (
            EXTRACTION_UNITS if change == "archived" else DECISION_UNITS | EXTRACTION_UNITS
        )


def test_final_quality_failure_stops_and_parent_retry_obtains_new_decisions(
    client, app, family_headers, child
):
    sid = submit(client, family_headers, child)
    provider = StageFake(review_failures=99)
    app.state.worker.provider = provider
    assert app.state.worker.process_one()
    assert not app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        jid = job.id
        assert job.state == "failed" and job.attempts == 1
        assert db.get(LearningSubmission, sid).error_code == "analysis_output_invalid"
        assert stage_keys(db, sid) == {"t"}
    response = client.post(f"/api/v1/submissions/{sid}/retry", headers=family_headers)
    assert response.status_code == 200
    provider.review_failures = 0
    assert app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        assert db.get(AgentJob, jid).state == "succeeded"
        assert db.get(LearningSubmission, sid).state == "pending_confirmation"
        assert stage_keys(db, sid) == set()
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
    assert provider.calls["extract", "t"] == 1
    assert provider.calls["merge", "merge"] == 3
    assert provider.review_calls == 3


def test_first_review_refusal_survives_correction_transport_interruption(
    client, app, family_headers, child
):
    class CorrectionTimeout(StageFake):
        interrupted = False

        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "merge" and "review_issues" in payload and not self.interrupted:
                self.interrupted = True
                raise StageFailure("provider_timeout")
            return await super().generate_stage(stage, instructions, payload, *args)

    sid = submit(client, family_headers, child)
    provider = CorrectionTimeout(review_failures=1)
    app.state.worker.provider = provider
    assert app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        assert stage_keys(db, sid) == {"t", "merge", "review0"}
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert job.state == "queued"
        job.available_at = utcnow()
        db.commit()
    assert app.state.worker.process_one()
    assert provider.calls["extract", "t"] == 1 and provider.review_calls == 2
    assert provider.calls["merge", "merge"] == 2
    with app.state.database.session_factory() as db:
        assert db.get(LearningSubmission, sid).state == "pending_confirmation"


@pytest.mark.parametrize("change", ["attempt", "lease", "cancel", "child_deleting"])
def test_final_refusal_cannot_purge_after_lease_or_scope_changes(
    client, app, family_headers, child, change
):
    sid = submit(client, family_headers, child)

    class LateRefusal(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            if stage == "review" and "previous_review" in payload:
                with app.state.database.session_factory() as db:
                    job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
                    if change == "attempt":
                        job.attempts += 1
                    elif change == "lease":
                        job.lease_until = utcnow() - timedelta(seconds=1)
                    elif change == "cancel":
                        db.get(LearningSubmission, sid).state = "cancelled"
                    else:
                        db.get(Child, child["id"]).deleting = True
                    db.commit()
                raise StageFailure("quality", retryable=False, stage="review", unit="review1")
            return await super().generate_stage(stage, instructions, payload, *args)

    app.state.worker.provider = LateRefusal(review_failures=1)
    assert app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        assert stage_keys(db, sid) == {"t", "merge", "review0", "merge-correction"}
        assert db.get(LearningSubmission, sid).state == (
            "cancelled" if change == "cancel" else "analyzing"
        )


def test_terminal_cleanup_commit_failure_preserves_durable_lease_and_cache(
    client, app, family_headers, child, monkeypatch
):
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session

    sid = submit(client, family_headers, child)
    original_commit = Session.commit

    def commit(session):
        if any(
            isinstance(row, AgentJob) and row.state == "failed"
            for row in session.identity_map.values()
        ):
            raise OperationalError("synthetic terminal commit", None, RuntimeError("synthetic"))
        return original_commit(session)

    monkeypatch.setattr(Session, "commit", commit)
    app.state.worker.provider = StageFake(review_failures=99)
    with pytest.raises(OperationalError):
        app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        assert stage_keys(db, sid) == {"t", "merge", "review0", "merge-correction"}
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert job.state == "running" and job.attempts == 1 and job.lease_until is not None
        assert db.get(LearningSubmission, sid).state == "analyzing"


def test_uncertain_reuse_stops_worker_and_cleans_only_semantic_stages(
    client, app, family_headers, child
):
    from push_kids.knowledge.normalization import normalize_knowledge_name
    from push_kids.persistence.models import Subject

    with app.state.database.session_factory() as db:
        subject = Subject(
            family_id=family_headers["X-Family-ID"],
            child_id=child["id"],
            name="数学",
            kind="learning",
        )
        db.add(subject)
        db.flush()
        db.add(
            KnowledgeItem(
                family_id=family_headers["X-Family-ID"],
                child_id=child["id"],
                subject_id=subject.id,
                name="十以内加法",
                normalized_name=normalize_knowledge_name("十以内加法"),
                category="计算",
                review_method="变式练习",
                estimated_minutes=3,
            )
        )
        db.commit()

    class UncertainReuse(StageFake):
        async def generate_stage(self, stage, instructions, payload, *args):
            result = await super().generate_stage(stage, instructions, payload, *args)
            if stage == "reuse":
                for decision in result.decisions:
                    decision.verdict, decision.basis = "uncertain", "复习范围不确定"
            return result

    sid = submit(client, family_headers, child)
    app.state.worker.provider = UncertainReuse()
    assert app.state.worker.process_one()
    assert not app.state.worker.process_one()
    with app.state.database.session_factory() as db:
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == sid))
        assert job.state == "failed" and job.attempts == 1
        assert db.get(LearningSubmission, sid).error_code == "analysis_output_invalid"
        assert stage_keys(db, sid) == {"t"}
        assert db.scalar(select(func.count(KnowledgeItem.id))) == 1
        assert db.scalar(select(func.count(LearningRecord.id))) == 0
