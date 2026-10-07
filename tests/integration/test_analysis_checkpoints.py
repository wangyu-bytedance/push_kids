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

from tests.staged_analysis_fakes import StageFake


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
        assert db.scalar(select(func.count(AnalysisStageResult.id))) == 2
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
    assert provider.calls["match", "match"] == 2


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
