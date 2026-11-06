import json
from datetime import timedelta

import pytest
from push_kids.agent_processing.contracts import AnalysisProposal, CoverageMatch, KnowledgeProposal
from push_kids.agent_processing.decision_contracts import DECISION_REVISION
from push_kids.knowledge.coverage_snapshot import content_fingerprint, point_fingerprint
from push_kids.learning.coverage import apply_confirmed_coverage
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select

from tests.integration.test_review_inventory import seed


@pytest.mark.parametrize("change", ["none", "edited", "injected", "manual", "stale", "backfill"])
def test_new_coverage_through_parent_confirmation_route(client, app, child, family_headers, change):
    family, cid = family_headers["X-Family-ID"], child["id"]
    sid, ids = seed(app, family, cid, size=1)
    rid, kid = ids[0]
    point = KnowledgeProposal(name="合成扩展范围", subject_name="测试数学")
    with app.state.database.session_factory() as db:
        old, review = db.get(KnowledgeItem, kid), db.get(ReviewItem, rid)
        snapshot = CoverageMatch(
            point_fingerprint=point_fingerprint(point),
            old_knowledge_id=kid,
            old_fingerprint=content_fingerprint(
                old.name, old.category, old.review_method, old.evidence_json or ""
            ),
            decision_revision=DECISION_REVISION,
            review_state_version=review.state_version,
        )
    proposal = AnalysisProposal(
        summary="合成完整范围",
        subject_name="测试数学",
        knowledge_points=[point],
        coverage_matches=[snapshot],
    )
    occurred_at = utcnow() - timedelta(days=30) if change == "backfill" else utcnow()
    submission = client.post(
        "/api/v1/submissions",
        headers=family_headers,
        json={"child_id": cid, "occurred_at": occurred_at.isoformat(), "input_text": "合成来源"},
    ).json()["id"]
    with app.state.database.session_factory() as db:
        row = db.get(LearningSubmission, submission)
        stored = proposal.model_dump()
        if change == "injected":
            stored["coverage_matches"] = []
        if change == "stale":
            db.get(ReviewItem, rid).state_version += 1
        row.proposal_json, row.state = json.dumps(stored), "pending_confirmation"
        db.commit()
        assert db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) == 0
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == 0
    if change == "edited":
        proposal.knowledge_points[0].name = "家长修改的范围"
    response = client.post(
        f"/api/v1/submissions/{submission}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal.model_dump(),
            "manual_entry": change == "manual",
            "groups": [{"subject_id": sid, "subject_name": "测试数学", "knowledge_indexes": [0]}],
        },
    )
    assert response.status_code == 200, response.text
    covered = change in {"none", "backfill"}
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, kid).review_status == ("superseded" if covered else "normal")
        review = db.get(ReviewItem, rid)
        assert review.review_count == int(covered)
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == int(covered)
        assert db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) == 1
        if covered:
            assert review.last_reviewed_on == local_date(occurred_at)


@pytest.mark.parametrize("stale,same_day", [(False, False), (True, False), (False, True)])
def test_new_coverage_records_observed_before_supersession_and_skips_stale(
    app,
    child,
    family_headers,
    stale,
    same_day,
):
    family, cid = family_headers["X-Family-ID"], child["id"]
    _, ids = seed(app, family, cid, size=2)
    with app.state.database.session_factory() as db:
        old, covering = (db.get(KnowledgeItem, kid) for _, kid in ids)
        review = db.get(ReviewItem, ids[0][0])
        point = KnowledgeProposal(name=covering.name, subject_name="测试数学")
        covering.category, covering.review_method = point.category, point.review_method
        covering.evidence_json = json.dumps(
            [e.model_dump() for e in point.direct_evidence], ensure_ascii=False
        )
        if same_day:
            review.last_reviewed_on, review.review_count, review.step = local_date(), 1, 1
        snapshot = CoverageMatch(
            point_fingerprint=point_fingerprint(point),
            old_knowledge_id=old.id,
            old_fingerprint=content_fingerprint(
                old.name, old.category, old.review_method, old.evidence_json or ""
            ),
            decision_revision=DECISION_REVISION,
            review_state_version=review.state_version,
        )
        if stale:
            review.state_version += 1
        db.flush()
        apply_confirmed_coverage(
            db,
            family,
            cid,
            {"coverage_matches": [snapshot.model_dump()]},
            [(point, covering.id)],
            reviewed_on=local_date(),
        )
        db.flush()
        assert old.review_status == ("normal" if stale else "superseded")
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == (
            0 if stale or same_day else 1
        )
        assert review.review_count == (0 if stale else 1)
        if not stale:
            assert review.last_reviewed_on == local_date()
        # The identical server snapshot cannot repeat its side effects.
        apply_confirmed_coverage(
            db,
            family,
            cid,
            {"coverage_matches": [snapshot.model_dump()]},
            [(point, covering.id)],
            reviewed_on=local_date(),
        )
        assert db.scalar(select(func.count()).select_from(ReviewFeedback)) == (
            0 if stale or same_day else 1
        )
