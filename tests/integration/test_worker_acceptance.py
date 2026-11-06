import json
from datetime import timedelta

import pytest
from push_kids.agent_processing.decision_contracts import DecisionAnswer
from push_kids.agent_processing.failures import StageFailure
from push_kids.persistence.models import AgentJob, Child, Family, LearningRecord, LearningSubmission
from push_kids.platform.time import utcnow
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from tests.integration.test_worker_resilience import add_jobs


class AcceptanceFake:
    model = "synthetic-acceptance"

    def __init__(self, *, failure=None, reject=False, callback=None):
        self.failure, self.reject, self.callback = failure, reject, callback
        self.calls = 0

    async def evaluate(self, questions, state, images, deadline, trace):
        self.calls += 1
        if self.callback:
            self.callback()
        if self.failure:
            raise self.failure
        return {
            key: DecisionAnswer(type="noul", noul=0.1 if self.reject else 0.999)
            for key in questions
        }


@pytest.mark.parametrize("outcome", ["no_finding", "needs_review", "unavailable"])
def test_acceptance_outcomes_keep_proposal_pending_without_formal_writes(
    client, app, child, family_headers, outcome
):
    checker = AcceptanceFake(
        failure=StageFailure("provider_timeout") if outcome == "unavailable" else None,
        reject=outcome == "needs_review",
    )
    app.state.worker.provider.acceptance_provider = checker
    job_id = add_jobs(app, child, family_headers, texts=("十以内加法",))[0]
    assert app.state.worker.process_one()
    assert checker.calls == 1
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, job_id)
        submission = db.get(LearningSubmission, job.submission_id)
        proposal = json.loads(submission.proposal_json)
        assert job.state == "succeeded" and job.attempts == 1
        assert submission.state == "pending_confirmation"
        assert proposal["knowledge_points"]
        assert proposal["_quality_acceptance"]["outcome"] == outcome
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
        if outcome != "no_finding":
            assert any("核对" in tip for tip in proposal["uncertainties"])
        submission_id = submission.id
    public = client.get(f"/api/v1/submissions/{submission_id}", headers=family_headers)
    assert public.status_code == 200
    assert "_quality_acceptance" not in public.json()["proposal"]
    confirmed = client.post(
        f"/api/v1/submissions/{submission_id}/confirm",
        headers=family_headers,
        json={"proposal": public.json()["proposal"]},
    )
    assert confirmed.status_code == 200
    with app.state.database.session_factory() as db:
        assert db.get(LearningSubmission, submission_id).state == "confirmed"
        assert db.scalar(select(func.count()).select_from(LearningRecord)) > 0


def test_parent_manual_confirmation_during_acceptance_wins(client, app, child, family_headers):
    job_id = add_jobs(app, child, family_headers, texts=("十以内加法",))[0]
    with app.state.database.session_factory() as db:
        submission_id = db.get(AgentJob, job_id).submission_id

    def parent_confirms():
        response = client.post(
            f"/api/v1/submissions/{submission_id}/confirm",
            headers=family_headers,
            json={
                "manual_entry": True,
                "proposal": {
                    "summary": "家长确认的加法练习",
                    "subject_name": "数学",
                    "knowledge_points": [{"name": "家长修改的十以内加法"}],
                },
            },
        )
        assert response.status_code == 200

    checker = AcceptanceFake(callback=parent_confirms)
    app.state.worker.provider.acceptance_provider = checker
    assert app.state.worker.process_one()
    assert checker.calls == 1
    with app.state.database.session_factory() as db:
        submission = db.get(LearningSubmission, submission_id)
        assert submission.state == "confirmed"
        assert (
            json.loads(submission.proposal_json)["knowledge_points"][0]["name"]
            == "家长修改的十以内加法"
        )
        assert db.get(AgentJob, job_id).state == "cancelled"
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 1


@pytest.mark.parametrize("change", ["cancel", "lease", "deleting", "family", "attempt", "expired"])
def test_acceptance_outside_transaction_cannot_overwrite_late_state(
    client, app, child, family_headers, change, monkeypatch
):
    job_id = add_jobs(app, child, family_headers, texts=("十以内加法",))[0]
    active_sessions = set()

    def began(session, transaction):
        if transaction.parent is None:
            active_sessions.add(id(session))

    def ended(session, transaction):
        if transaction.parent is None:
            active_sessions.discard(id(session))

    def change_state():
        assert not active_sessions, "checker must run without an open DB transaction"
        with app.state.database.session_factory() as db:
            job = db.get(AgentJob, job_id)
            if change == "cancel":
                db.get(LearningSubmission, job.submission_id).state = "cancelled"
            elif change == "lease":
                job.lease_until += timedelta(seconds=5)
            elif change == "deleting":
                db.get(Child, child["id"]).deleting = True
            elif change == "family":
                db.add(
                    Family(
                        id=family_headers["X-Family-ID"], display_name="测试家庭", status="deleting"
                    )
                )
            elif change == "attempt":
                job.attempts += 1
            else:
                late_now = utcnow() + timedelta(minutes=6)
                monkeypatch.setattr("push_kids.agent_processing.worker.utcnow", lambda: late_now)
            db.commit()

    checker = AcceptanceFake(callback=change_state)
    app.state.worker.provider.acceptance_provider = checker
    event.listen(Session, "after_transaction_create", began)
    event.listen(Session, "after_transaction_end", ended)
    try:
        assert app.state.worker.process_one()
    finally:
        event.remove(Session, "after_transaction_create", began)
        event.remove(Session, "after_transaction_end", ended)
    assert checker.calls == 1
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, job_id)
        assert job.state != "succeeded"
        assert db.get(LearningSubmission, job.submission_id).proposal_json is None
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0


def test_archived_child_allows_existing_job_to_finish(client, app, child, family_headers):
    job_id = add_jobs(app, child, family_headers, texts=("十以内加法",))[0]

    def archive():
        with app.state.database.session_factory() as db:
            db.get(Child, child["id"]).active = False
            db.commit()

    checker = AcceptanceFake(callback=archive)
    app.state.worker.provider.acceptance_provider = checker
    assert app.state.worker.process_one()
    assert checker.calls == 1
    with app.state.database.session_factory() as db:
        job = db.get(AgentJob, job_id)
        assert job.state == "succeeded"
        assert db.get(LearningSubmission, job.submission_id).state == "pending_confirmation"
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
