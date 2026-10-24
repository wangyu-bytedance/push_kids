"""Durable, bounded inventory coverage; provider calls never hold a transaction."""

import asyncio
import json
import logging
from datetime import timedelta
from time import monotonic
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError

from push_kids.agent_processing.contracts import (
    AnalysisProposal,
    EvidenceReference,
    KnowledgeProposal,
)
from push_kids.agent_processing.coverage import propose_coverage
from push_kids.agent_processing.coverage_jobs import ensure_coverage_job
from push_kids.agent_processing.history_search import HistorySearchRequest, search_history_items
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.knowledge.coverage_snapshot import content_fingerprint
from push_kids.knowledge.supersession import supersede
from push_kids.persistence.models import (
    Child,
    Family,
    KnowledgeCoverageJob,
    KnowledgeCoverageScan,
    KnowledgeItem,
    Subject,
)
from push_kids.planning.supersession import reconcile_superseded
from push_kids.platform.time import utcnow

logger = logging.getLogger("push_kids.coverage")


class CoverageWorker:
    def __init__(self, database, provider, poll_seconds=5):
        self.database, self.provider = database, provider
        self.poll_seconds, self.stopped = max(1, poll_seconds), False

    def stop(self):
        self.stopped = True

    async def run(self):
        while not self.stopped:
            try:
                worked = await asyncio.to_thread(self.process_one)
            except Exception:
                logger.warning("coverage_worker_failed reason=database")
                worked = False
            if not worked:
                await asyncio.sleep(self.poll_seconds)

    def discover(self):
        """Monotonic persisted scan: inspect only twenty identities, never rescan old pages."""
        with self.database.session_factory() as db:
            query = (
                select(KnowledgeCoverageScan)
                .where(KnowledgeCoverageScan.id == "inventory")
                .with_for_update()
            )
            scan = db.scalar(query)
            if scan is None:
                try:
                    with db.begin_nested():
                        db.add(KnowledgeCoverageScan(id="inventory", after_id=""))
                        db.flush()
                except IntegrityError:
                    pass
                scan = db.scalar(query.execution_options(populate_existing=True))
            assert scan is not None
            items = (
                select(KnowledgeItem).order_by(KnowledgeItem.created_at, KnowledgeItem.id).limit(20)
            )
            if scan.after_created_at is not None:
                items = items.where(
                    or_(
                        KnowledgeItem.created_at > scan.after_created_at,
                        and_(
                            KnowledgeItem.created_at == scan.after_created_at,
                            KnowledgeItem.id > scan.after_id,
                        ),
                    )
                )
            rows = list(db.scalars(items))
            for knowledge in rows:
                try:
                    with db.begin_nested():
                        ensure_coverage_job(db, knowledge)
                        db.flush()
                except IntegrityError:
                    pass
            if rows:
                scan.after_created_at, scan.after_id = rows[-1].created_at, rows[-1].id
            db.commit()

    def process_one(self) -> bool:
        if not getattr(self.provider, "coverage_enabled", True) or not callable(
            getattr(self.provider, "generate_stage", None)
        ):
            return False
        self.discover()
        now, token = utcnow(), str(uuid4())
        with self.database.session_factory() as db:
            job = db.scalar(
                select(KnowledgeCoverageJob)
                .where(
                    KnowledgeCoverageJob.state.in_(["queued", "running"]),
                    KnowledgeCoverageJob.available_at <= now,
                )
                .order_by(KnowledgeCoverageJob.available_at, KnowledgeCoverageJob.id)
                .limit(1)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if job is None:
                return False
            if job.attempts >= 3:
                job.state, job.error_code = "failed", "lease_exhausted"
                db.commit()
                return True
            job.state, job.lease_token = "running", token
            job.attempts += 1
            job.available_at = now + timedelta(seconds=90)
            job_id, family_id, child_id, kid = (
                job.id,
                job.family_id,
                job.child_id,
                job.knowledge_item_id,
            )
            db.commit()
        try:
            with self.database.session_factory() as db:
                k = db.scalar(
                    select(KnowledgeItem).where(
                        KnowledgeItem.id == kid,
                        KnowledgeItem.family_id == family_id,
                        KnowledgeItem.child_id == child_id,
                    )
                )
                child = db.get(Child, child_id)
                family = db.get(Family, family_id)
                if (
                    k is None
                    or k.review_status != "normal"
                    or child is None
                    or not child.active
                    or child.deleting
                    or (family and family.status != "active")
                ):
                    self._finish(job_id, token, "cancelled")
                    return True
                subject = db.get(Subject, k.subject_id)
                if subject is None or subject.kind != "learning" or not subject.active:
                    self._finish(job_id, token, "cancelled")
                    return True
                point = KnowledgeProposal(
                    name=k.name,
                    subject_name=subject.name,
                    category=k.category,
                    review_method=k.review_method,
                    direct_evidence=[
                        EvidenceReference.model_validate(e)
                        for e in json.loads(k.evidence_json or "[]")
                    ][:20],
                )
                cover_fingerprint = content_fingerprint(
                    k.name, k.category, k.review_method, (k.evidence_json or "")
                )
                contexts = search_history_items(
                    db,
                    family_id=family_id,
                    child_id=child_id,
                    request=HistorySearchRequest(
                        candidate_key=k.name, subject_name=subject.name, keywords=(k.name[:40],)
                    ),
                )
                contexts = [old for old in contexts if old.knowledge_id != kid]
            proposal = AnalysisProposal(
                summary="已确认知识整理", subject_name=point.subject_name, knowledge_points=[point]
            )
            ok = asyncio.run(
                propose_coverage(
                    self.provider, proposal, contexts, monotonic() + 30, AnalysisTrace.disabled()
                )
            )
            if not ok:
                self._finish(job_id, token, "retry")
                return True
            with self.database.session_factory() as db:
                # Same lock order as confirmation and deletion.
                family = db.scalar(select(Family).where(Family.id == family_id).with_for_update())
                child = db.scalar(
                    select(Child)
                    .where(Child.id == child_id, Child.family_id == family_id)
                    .with_for_update()
                )
                job = db.scalar(
                    select(KnowledgeCoverageJob)
                    .where(
                        KnowledgeCoverageJob.id == job_id,
                        KnowledgeCoverageJob.lease_token == token,
                        KnowledgeCoverageJob.state == "running",
                    )
                    .with_for_update()
                )
                if job is None:
                    return True
                k = db.get(KnowledgeItem, kid)
                if (
                    k is None
                    or child is None
                    or not child.active
                    or child.deleting
                    or (family and family.status != "active")
                ):
                    job.state = "cancelled"
                elif cover_fingerprint != content_fingerprint(
                    k.name, k.category, k.review_method, (k.evidence_json or "")
                ):
                    job.state, job.error_code = "cancelled", "content_changed"
                else:
                    for match in proposal.coverage_matches:
                        old = db.scalar(
                            select(KnowledgeItem)
                            .where(
                                KnowledgeItem.id == match.old_knowledge_id,
                                KnowledgeItem.family_id == family_id,
                                KnowledgeItem.child_id == child_id,
                            )
                            .with_for_update()
                        )
                        if (
                            old
                            and len(old.evidence_json or "") <= 4000
                            and match.old_fingerprint
                            == content_fingerprint(
                                old.name,
                                old.category,
                                old.review_method,
                                (old.evidence_json or "")[:4000],
                            )
                            and supersede(db, family_id, child_id, str(old.id), str(kid))
                        ):
                            reconcile_superseded(db, family_id, child_id, str(old.id))
                    job.state, job.error_code = "completed", None
                job.lease_token = None
                db.commit()
        except Exception:
            self._finish(job_id, token, "retry")
        return True

    def _finish(self, job_id, token, outcome):
        with self.database.session_factory() as db:
            job = db.scalar(
                select(KnowledgeCoverageJob)
                .where(
                    KnowledgeCoverageJob.id == job_id,
                    KnowledgeCoverageJob.lease_token == token,
                    KnowledgeCoverageJob.state == "running",
                )
                .with_for_update()
            )
            if job:
                job.state = (
                    ("failed" if job.attempts >= 3 else "queued") if outcome == "retry" else outcome
                )
                job.error_code = "unavailable" if outcome == "retry" else None
                job.lease_token = None
                job.available_at = utcnow() + timedelta(seconds=2 ** int(job.attempts))
                db.commit()
