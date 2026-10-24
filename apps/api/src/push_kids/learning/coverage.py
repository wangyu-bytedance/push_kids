"""Apply only the server's coverage snapshots after the parent's final confirmation."""

import json

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.agent_processing.contracts import CoverageMatch
from push_kids.knowledge.coverage_snapshot import content_fingerprint, point_fingerprint
from push_kids.knowledge.supersession import supersede
from push_kids.persistence.models import KnowledgeItem
from push_kids.planning.supersession import reconcile_superseded


def apply_confirmed_coverage(
    db: Session, family_id: str, child_id: str, stored: dict, confirmed: list[tuple]
) -> None:
    final = {}
    for point, kid in confirmed:
        covering = db.get(KnowledgeItem, kid)
        # Existing identities retain first provenance and review action. The actual
        # scheduled item must match the content on which the AI based coverage.
        evidence = json.dumps([e.model_dump() for e in point.direct_evidence], ensure_ascii=False)
        if covering and content_fingerprint(
            covering.name, covering.category, covering.review_method, covering.evidence_json or ""
        ) == content_fingerprint(point.name, point.category, point.review_method, evidence):
            final[point_fingerprint(point)] = kid
    matches = stored.get("coverage_matches", [])
    if not isinstance(matches, list):
        return
    for raw in matches[:400]:
        try:
            match = CoverageMatch.model_validate(raw)
        except ValidationError:
            continue
        covering_id = final.get(match.point_fingerprint)
        if not covering_id:
            continue
        old = db.scalar(
            select(KnowledgeItem)
            .where(
                KnowledgeItem.id == match.old_knowledge_id,
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if (
            old is None
            or len(old.evidence_json or "") > 4000
            or content_fingerprint(
                old.name, old.category, old.review_method, (old.evidence_json or "")[:4000]
            )
            != match.old_fingerprint
        ):
            continue
        if supersede(db, family_id, child_id, str(old.id), str(covering_id)):
            reconcile_superseded(db, family_id, child_id, str(old.id))
