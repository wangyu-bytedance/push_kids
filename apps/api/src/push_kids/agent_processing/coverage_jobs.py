"""AI coverage job enqueue contract for confirmed content; no model or planning dependency."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.persistence.models import KnowledgeCoverageJob, KnowledgeItem


def ensure_coverage_job(db: Session, knowledge: KnowledgeItem) -> None:
    if (
        db.scalar(
            select(KnowledgeCoverageJob.id).where(
                KnowledgeCoverageJob.knowledge_item_id == knowledge.id,
                KnowledgeCoverageJob.family_id == knowledge.family_id,
                KnowledgeCoverageJob.child_id == knowledge.child_id,
            )
        )
        is None
    ):
        db.add(
            KnowledgeCoverageJob(
                knowledge_item_id=knowledge.id,
                family_id=knowledge.family_id,
                child_id=knowledge.child_id,
            )
        )
