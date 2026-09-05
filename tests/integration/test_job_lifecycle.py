from datetime import UTC, datetime

from push_kids.agent_processing.contracts import (
    AnalysisProposal,
    EvidenceReference,
    KnowledgeProposal,
)
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.persistence.models import AgentJob
from push_kids.platform.time import utcnow
from sqlalchemy import select


class FailingProvider:
    def analyze(self, _data):
        raise RuntimeError("provider unavailable")


class CapturingProvider:
    def __init__(self) -> None:
        self.received = None

    def analyze(self, data):
        self.received = data
        return AnalysisProposal(
            summary="结合近期记录整理了本次内容",
            subject_name="英语",
            knowledge_points=[
                KnowledgeProposal(
                    name="英语学习",
                    direct_evidence=[
                        EvidenceReference(source="parent_text", detail="今天继续学英语")
                    ],
                )
            ],
        )


def test_cancelled_job_never_runs(client, app, family_headers, child) -> None:
    created = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "英语 animal",
        },
    ).json()
    cancelled = client.post(f"/api/v1/submissions/{created['id']}/cancel", headers=family_headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"
    assert app.state.worker.process_one() is False


def test_parent_can_delete_a_pending_confirmation_draft(client, app, family_headers, child) -> None:
    created = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "语文，阅读《秋天》",
        },
    ).json()
    assert app.state.worker.process_one() is True
    pending = client.get(f"/api/v1/submissions/{created['id']}", headers=family_headers).json()
    assert pending["state"] == "pending_confirmation"

    deleted = client.post(f"/api/v1/submissions/{created['id']}/cancel", headers=family_headers)
    assert deleted.status_code == 200
    assert deleted.json()["state"] == "cancelled"
    assert deleted.json()["proposal"] is None


def test_failed_job_retries_three_times_without_exposing_provider_error(
    client, app, family_headers, child
) -> None:
    created = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "数学进位加法",
        },
    ).json()
    app.state.worker.provider = FailingProvider()
    for _ in range(3):
        assert app.state.worker.process_one() is True
        with app.state.database.session_factory() as db:
            job = db.scalar(select(AgentJob).where(AgentJob.submission_id == created["id"]))
            assert job is not None
            job.available_at = utcnow()
            db.commit()
    detail = client.get(f"/api/v1/submissions/{created['id']}", headers=family_headers)
    assert detail.json()["state"] == "failed"
    assert detail.json()["error_message"] == "分析暂时失败，请重试"
    assert "provider unavailable" not in detail.text

    app.state.worker.provider = DeterministicTestProvider()
    retried = client.post(f"/api/v1/submissions/{created['id']}/retry", headers=family_headers)
    assert retried.status_code == 200
    assert retried.json()["state"] == "queued"
    assert app.state.worker.process_one() is True
    recovered = client.get(f"/api/v1/submissions/{created['id']}", headers=family_headers)
    assert recovered.json()["state"] == "pending_confirmation"
    assert recovered.json()["error_message"] is None


def test_worker_supplies_only_confirmed_recent_context_and_active_subjects(
    client, app, family_headers, child
) -> None:
    first = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "英语单词 school",
        },
    ).json()
    assert app.state.worker.process_one() is True
    first_detail = client.get(f"/api/v1/submissions/{first['id']}", headers=family_headers).json()
    confirmed = client.post(
        f"/api/v1/submissions/{first['id']}/confirm",
        headers=family_headers,
        json={"proposal": first_detail["proposal"]},
    )
    assert confirmed.status_code == 200
    inactive = client.post(
        "/api/v1/subjects",
        headers=family_headers,
        json={"child_id": child["id"], "name": "科学", "kind": "learning"},
    ).json()
    assert (
        client.patch(
            f"/api/v1/subjects/{inactive['id']}",
            headers=family_headers,
            json={"active": False},
        ).status_code
        == 200
    )

    second = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "今天继续学英语",
        },
    ).json()
    provider = CapturingProvider()
    app.state.worker.provider = provider
    assert app.state.worker.process_one() is True
    assert provider.received is not None
    assert "英语" in provider.received.existing_subjects
    assert "科学" not in provider.received.existing_subjects
    assert len(provider.received.recent_learning) == 1
    assert provider.received.recent_learning[0].record_id
    assert "school" in provider.received.recent_learning[0].summary
    detail = client.get(f"/api/v1/submissions/{second['id']}", headers=family_headers)
    assert detail.json()["state"] == "pending_confirmation"
