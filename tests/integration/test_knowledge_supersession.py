"""Feature semantics through real transactions, HTTP and durable derived plans."""

import asyncio
import json
from datetime import timedelta
from time import monotonic

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisProposal,
    ExistingKnowledgeContext,
    KnowledgeProposal,
)
from push_kids.agent_processing.coverage import propose_coverage
from push_kids.agent_processing.history_search import add_search_terms
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.knowledge.supersession import supersede
from push_kids.persistence.models import (
    DailyReviewPlanItem,
    KnowledgeCoverageJob,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    ReviewQueueEntry,
    ReviewScheduleOverride,
)
from push_kids.planning.service import PlanningService
from push_kids.planning.supersession import reconcile_superseded
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select

from tests.coverage_fakes import CoverageFake
from tests.integration.test_review_inventory import path, schedule, seed


def apply(app, family, cid, old, covering):
    with app.state.database.session_factory() as db:
        changed = supersede(db, family, cid, old, covering)
        if changed:
            reconcile_superseded(db, family, cid, old)
        db.commit()
        return changed


def flatten(plan):
    return [i["review_id"] for s in plan["sessions"] for i in s["items"]]


def test_current_future_plan_no_refill_history_and_terminal_state(
    client, app, family_headers, child
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=6)
    oldrid, oldkid = ids[0]
    with app.state.database.session_factory() as db:
        before = PlanningService.daily_review_selection(db, family, cid)
        future = PlanningService.daily_review_selection(
            db, family, cid, day=local_date() + timedelta(days=1)
        )
        old_count = db.get(ReviewItem, oldrid).review_count
    assert oldrid in flatten(before)
    assert apply(app, family, cid, oldkid, ids[-1][1])
    assert not apply(app, family, cid, oldkid, ids[-1][1])
    assert not apply(app, family, cid, ids[-1][1], oldkid)
    with app.state.database.session_factory() as db:
        after = PlanningService.daily_review_selection(db, family, cid)
        assert flatten(after) == [r for r in flatten(before) if r != oldrid]
        after_future = PlanningService.daily_review_selection(
            db, family, cid, day=local_date() + timedelta(days=1)
        )
        assert flatten(after_future) == [r for r in flatten(future) if r != oldrid]
        assert not db.get(ReviewQueueEntry, oldrid).available
        assert db.get(ReviewItem, oldrid).review_count == old_count
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 0
        assert len(list(db.scalars(select(KnowledgeItem)))) == 6
        # Existing curve reactivation cannot clear authoritative knowledge status.
        review = db.get(ReviewItem, oldrid)
        review.active, review.due_date = True, local_date()
        db.commit()
        assert not db.get(ReviewQueueEntry, oldrid).available
        assert all(
            load.pending_count <= 5
            for load in PlanningService.pending_review_loads(db, local_date(), family_id=family)
        )
    normal = client.get(path(child), headers=family_headers, params={"view": "count"}).json()
    assert normal["total"] == 5
    replaced = client.get(
        path(child), headers=family_headers, params={"review_status": "superseded"}
    ).json()
    assert replaced["total"] == 1
    assert replaced["items"][0]["superseded_by_name"] == "知识5"
    assert not replaced["items"][0]["can_schedule"]
    assert schedule(client, family_headers, child, oldrid, version=1).status_code == 409
    assert client.get(path(child), headers={"X-Family-ID": "other"}).status_code == 404


def test_completed_history_and_existing_parent_reservation_survive_once(
    client, app, family_headers, child
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=4)
    rid, kid = ids[0]
    assert schedule(client, family_headers, child, rid).status_code == 200
    assert apply(app, family, cid, kid, ids[-1][1])
    with app.state.database.session_factory() as db:
        assert db.get(ReviewQueueEntry, rid).available
        tomorrow = PlanningService.daily_review_selection(
            db, family, cid, day=local_date() + timedelta(days=1)
        )
        assert rid in flatten(tomorrow)
    response = client.post(
        f"/api/v1/reviews/{rid}/feedback", headers=family_headers, json={"action": "complete"}
    )
    assert response.status_code == 200, response.text
    with app.state.database.session_factory() as db:
        assert db.get(ReviewScheduleOverride, rid) is None
        assert not db.get(ReviewQueueEntry, rid).available
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 1
        assert db.get(KnowledgeItem, kid).review_status == "superseded"
    assert (
        schedule(
            client,
            family_headers,
            child,
            rid,
            version=response.json().get("state_version", 2),
            key="new-schedule-after-cover",
        ).status_code
        == 409
    )


def test_delete_only_selected_target_and_keep_permanent_status(client, app, family_headers, child):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=3)
    for _, old in ids[:-1]:
        assert apply(app, family, cid, old, ids[-1][1])
    response = client.delete(
        f"/api/v1/children/{cid}/knowledge/{ids[-1][1]}", headers=family_headers
    )
    assert response.status_code == 204
    result = client.get(
        path(child), headers=family_headers, params={"view": "count", "review_status": "superseded"}
    ).json()
    assert result["total"] == 2
    assert all(i["superseded_by_name"] is None and not i["can_schedule"] for i in result["items"])
    with app.state.database.session_factory() as db:
        assert all(db.get(KnowledgeItem, k).review_status == "superseded" for _, k in ids[:-1])


def test_scope_rejections_and_status_cursor_isolation(client, app, family_headers, child):
    from push_kids.persistence.models import Subject

    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=3)
    other = client.post(
        "/api/v1/children", headers=family_headers, json={"name": "同家庭另一个孩子"}
    )
    assert other.status_code == 201
    _, other_ids = seed(app, family, other.json()["id"], size=1)
    with app.state.database.session_factory() as db:
        subject = Subject(family_id=family, child_id=cid, name="测试英语", kind="learning")
        db.add(subject)
        db.flush()
        knowledge = KnowledgeItem(
            family_id=family,
            child_id=cid,
            subject_id=subject.id,
            name="英语词汇",
            normalized_name="英语词汇",
        )
        db.add(knowledge)
        db.flush()
        different_subject_id = knowledge.id
        db.commit()
    oldrid, oldkid = ids[0]
    assert not apply(app, family, cid, oldkid, oldkid)
    assert not apply(app, family, cid, oldkid, other_ids[0][1])
    assert not apply(app, family, cid, oldkid, different_subject_id)
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, oldkid).review_status == "normal"
        assert db.get(ReviewItem, oldrid).state_version == 0
    params = {"view": "count", "limit": 1}
    first = client.get(path(child), headers=family_headers, params=params).json()
    params["cursor"] = first["next_cursor"]
    assert (
        client.get(
            path(child), headers=family_headers, params={**params, "review_status": "superseded"}
        ).status_code
        == 400
    )
    assert apply(app, family, cid, oldkid, ids[-1][1])
    assert client.get(path(child), headers=family_headers, params=params).status_code == 409
    subjects = client.get(
        path(child) + "/subjects",
        headers=family_headers,
        params={"review_status": "superseded"},
    ).json()["items"]
    assert sum(item["count"] for item in subjects) == 1


@pytest.mark.parametrize("change", ["none", "edited", "injected", "old_changed", "manual"])
def test_confirmation_uses_only_unchanged_server_proposal(
    client, app, family_headers, child, change
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    sid, ids = seed(app, family, cid, size=1)
    rid, kid = ids[0]
    point = KnowledgeProposal(
        name="20以内加减法",
        subject_name="测试数学",
        review_method="变式练习",
        direct_evidence=[{"source": "parent_text", "detail": "20以内加减法完整范围"}],
    )
    with app.state.database.session_factory() as db:
        old = db.get(KnowledgeItem, kid)
        old.name, old.normalized_name, old.review_method = (
            "10以内加减法",
            "10以内加减法",
            "变式练习",
        )
        old.evidence_json = "[]"
        db.commit()
        context = ExistingKnowledgeContext(
            knowledge_id=kid,
            name=old.name,
            category=old.category,
            subject_name="测试数学",
            review_method=old.review_method,
            evidence=old.evidence_json,
        )
    proposal = AnalysisProposal(
        summary="练习20以内加减法", subject_name="测试数学", knowledge_points=[point]
    )
    asyncio.run(
        propose_coverage(
            CoverageFake(), proposal, [context], monotonic() + 5, AnalysisTrace.disabled()
        )
    )
    assert len(proposal.coverage_matches) == 1
    draft = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={"child_id": cid, "occurred_at": utcnow().isoformat(), "input_text": "完整练习"},
    ).json()["id"]
    with app.state.database.session_factory() as db:
        sub = db.get(LearningSubmission, draft)
        stored = proposal.model_dump()
        if change == "injected":
            stored["coverage_matches"] = []
        sub.proposal_json, sub.state = json.dumps(stored), "pending_confirmation"
        if change == "old_changed":
            db.get(KnowledgeItem, kid).name = "新技能"
        db.commit()
    if change == "edited":
        proposal.knowledge_points[0].name = "20以内进位加法"
    response = client.post(
        f"/api/v1/submissions/{draft}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal.model_dump(),
            "manual_entry": change == "manual",
            "groups": [{"subject_id": sid, "subject_name": "测试数学", "knowledge_indexes": [0]}],
        },
    )
    assert response.status_code == 200, response.text
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid).review_status == (
            "superseded" if change == "none" else "normal"
        )
        assert db.get(ReviewItem, rid).review_count == 0
        assert db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) == 1
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 0


def test_background_inventory_restart_retry_and_scope(client, app, family_headers, child):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=2)
    with app.state.database.session_factory() as db:
        for i, (_, kid) in enumerate(ids):
            k = db.get(KnowledgeItem, kid)
            k.name, k.normalized_name = (
                ("10以内加减法", "10以内加减法") if i == 0 else ("20以内加减法", "20以内加减法")
            )
            add_search_terms(db, k)
        db.commit()
    worker = app.state.coverage_worker
    worker.provider = CoverageFake(fail=True)
    worker.discover()
    with app.state.database.session_factory() as db:
        jobs = list(
            db.scalars(
                select(KnowledgeCoverageJob).order_by(KnowledgeCoverageJob.knowledge_item_id)
            )
        )
        # Process newer covering identity first, independent of global discovery order.
        for job in jobs:
            job.available_at = (
                utcnow() + timedelta(hours=1)
                if job.knowledge_item_id == ids[0][1]
                else utcnow() - timedelta(seconds=1)
            )
        db.commit()
    assert worker.process_one()
    with app.state.database.session_factory() as db:
        job = db.scalar(
            select(KnowledgeCoverageJob).where(KnowledgeCoverageJob.knowledge_item_id == ids[1][1])
        )
        assert job.state == "queued" and job.attempts == 1
        assert db.get(KnowledgeItem, ids[0][1]).review_status == "normal"
        job.available_at = utcnow() - timedelta(seconds=1)
        db.commit()
    worker.provider = CoverageFake()
    assert worker.process_one()
    with app.state.database.session_factory() as db:
        job = db.scalar(
            select(KnowledgeCoverageJob).where(KnowledgeCoverageJob.knowledge_item_id == ids[1][1])
        )
        assert job.state == "completed" and job.attempts == 2
        assert db.get(KnowledgeItem, ids[0][1]).review_status == "superseded"
        assert db.get(KnowledgeItem, ids[1][1]).review_status == "normal"
    assert not apply(app, "other", cid, ids[0][1], ids[1][1])


@pytest.mark.parametrize("missing_review", [False, True])
def test_confirming_old_material_never_restores_even_with_rebuilt_review(
    client, app, family_headers, child, missing_review
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    sid, ids = seed(app, family, cid, size=2)
    rid, kid = ids[0]
    assert apply(app, family, cid, kid, ids[1][1])
    with app.state.database.session_factory() as db:
        old = db.get(KnowledgeItem, kid)
        point = KnowledgeProposal(
            existing_knowledge_id=kid,
            name=old.name,
            subject_name="测试数学",
            category=old.category,
            review_method=old.review_method,
        )
        if missing_review:
            db.delete(db.get(ReviewItem, rid))
        db.commit()
    proposal = AnalysisProposal(
        summary="再次学习旧内容", subject_name="测试数学", knowledge_points=[point]
    )
    draft = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={"child_id": cid, "occurred_at": utcnow().isoformat(), "input_text": "再次学习旧内容"},
    ).json()["id"]
    response = client.post(
        f"/api/v1/submissions/{draft}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal.model_dump(),
            "manual_entry": True,
            "groups": [{"subject_id": sid, "subject_name": "测试数学", "knowledge_indexes": [0]}],
        },
    )
    assert response.status_code == 200, response.text
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid).review_status == "superseded"
        review = db.scalar(select(ReviewItem).where(ReviewItem.knowledge_item_id == kid))
        assert not db.get(ReviewQueueEntry, review.id).available
        assert db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) == 1


def test_completed_row_survives_later_supersession(client, app, family_headers, child):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=2)
    with app.state.database.session_factory() as db:
        PlanningService.daily_review_selection(db, family, cid)
    response = client.post(
        f"/api/v1/reviews/{ids[0][0]}/feedback", headers=family_headers, json={"action": "complete"}
    )
    assert response.status_code == 200
    assert apply(app, family, cid, ids[0][1], ids[1][1])
    with app.state.database.session_factory() as db:
        assert (
            db.scalar(
                select(DailyReviewPlanItem.state).where(
                    DailyReviewPlanItem.review_item_id == ids[0][0]
                )
            )
            == "complete"
        )
        assert db.get(ReviewItem, ids[0][0]).review_count == 1


def test_confirmation_planning_failure_rolls_back_all_new_facts(
    client, app, family_headers, child, monkeypatch
):
    import push_kids.learning.coverage as coverage

    def fail(*args):
        raise RuntimeError("injected_reconciliation_failure")

    monkeypatch.setattr(coverage, "reconcile_superseded", fail)
    with pytest.raises(RuntimeError, match="injected_reconciliation_failure"):
        test_confirmation_uses_only_unchanged_server_proposal(
            client, app, family_headers, child, "none"
        )
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(KnowledgeItem)) == 1
        assert db.scalar(select(KnowledgeItem.review_status)) == "normal"
        assert db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) == 0


def test_discovery_cursor_resumes_without_rescanning_processed_pages(
    client, app, family_headers, child
):
    from push_kids.persistence.models import KnowledgeCoverageScan

    family, cid = family_headers["X-Family-ID"], child["id"]
    seed(app, family, cid, size=51)
    worker = app.state.coverage_worker
    for expected in (20, 40, 51, 51):
        worker.discover()
        with app.state.database.session_factory() as db:
            assert db.scalar(select(func.count()).select_from(KnowledgeCoverageJob)) == expected
            assert db.get(KnowledgeCoverageScan, "inventory").after_id


@pytest.mark.parametrize("exhausted", [False, True])
def test_archived_or_exhausted_work_has_terminal_state_without_model_calls(
    client, app, family_headers, child, exhausted
):
    from push_kids.persistence.models import Child

    family, cid = family_headers["X-Family-ID"], child["id"]
    seed(app, family, cid, size=1)
    worker = app.state.coverage_worker
    worker.provider = CoverageFake()
    worker.discover()
    with app.state.database.session_factory() as db:
        job = db.scalar(select(KnowledgeCoverageJob))
        if exhausted:
            job.state, job.attempts = "running", 3
            job.available_at = utcnow() - timedelta(seconds=1)
        else:
            db.get(Child, cid).active = False
        db.commit()
    assert worker.process_one()
    assert worker.provider.calls == 0
    with app.state.database.session_factory() as db:
        job = db.scalar(select(KnowledgeCoverageJob))
        assert job.state == ("failed" if exhausted else "cancelled")
