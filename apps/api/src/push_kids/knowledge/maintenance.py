"""Controlled knowledge-name repair while preserving confirmed learning and review facts."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from push_kids.agent_processing.history_search import add_search_terms
from push_kids.children.service import ChildrenService
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.knowledge.supersession import supersede
from push_kids.persistence.models import Child, KnowledgeItem, KnowledgeSearchTerm, Subject
from push_kids.planning.supersession import reconcile_superseded


class KnowledgeRepairConflict(RuntimeError):
    """The locked database state no longer matches the approved dry-run."""


@dataclass(frozen=True)
class KnowledgeRepairCluster:
    family_id: str
    child_id: str
    subject_id: str
    canonical_id: str
    canonical_old_name: str
    target_name: str
    duplicate_ids: tuple[str, ...]
    duplicate_old_names: tuple[str, ...]


def apply_repair_cluster(db: Session, cluster: KnowledgeRepairCluster) -> None:
    """Apply one exact, pre-approved cluster inside the caller-owned transaction."""
    child = db.scalar(
        select(Child)
        .where(Child.id == cluster.child_id, Child.family_id == cluster.family_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if child is None or child.deleting:
        raise KnowledgeRepairConflict("child_state_changed")
    subject = db.scalar(
        select(Subject).where(
            Subject.id == cluster.subject_id,
            Subject.family_id == cluster.family_id,
            Subject.child_id == cluster.child_id,
            Subject.kind == "learning",
        )
    )
    if subject is None:
        raise KnowledgeRepairConflict("subject_state_changed")
    expected_ids = (cluster.canonical_id, *cluster.duplicate_ids)
    rows = list(
        db.scalars(
            select(KnowledgeItem)
            .where(
                KnowledgeItem.id.in_(expected_ids),
                KnowledgeItem.family_id == cluster.family_id,
                KnowledgeItem.child_id == cluster.child_id,
                KnowledgeItem.subject_id == cluster.subject_id,
            )
            .order_by(KnowledgeItem.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    )
    by_id = {row.id: row for row in rows}
    canonical = by_id.get(cluster.canonical_id)
    duplicates = [by_id.get(item_id) for item_id in cluster.duplicate_ids]
    if (
        len(rows) != len(expected_ids)
        or canonical is None
        or canonical.review_status != "normal"
        or canonical.name != cluster.canonical_old_name
        or any(item is None or item.review_status != "normal" for item in duplicates)
        or tuple(item.name for item in duplicates if item is not None)
        != cluster.duplicate_old_names
    ):
        raise KnowledgeRepairConflict("knowledge_state_changed")
    normalized_target = normalize_knowledge_name(cluster.target_name)
    if not normalized_target:
        raise KnowledgeRepairConflict("target_name_invalid")
    collision = db.scalar(
        select(KnowledgeItem.id).where(
            KnowledgeItem.family_id == cluster.family_id,
            KnowledgeItem.child_id == cluster.child_id,
            KnowledgeItem.subject_id == cluster.subject_id,
            KnowledgeItem.normalized_name == normalized_target,
            KnowledgeItem.category == canonical.category,
            KnowledgeItem.id.not_in(expected_ids),
        )
    )
    if collision is not None:
        raise KnowledgeRepairConflict("target_identity_exists")

    for duplicate_id, duplicate in zip(cluster.duplicate_ids, duplicates, strict=True):
        assert duplicate is not None
        if not supersede(
            db,
            cluster.family_id,
            cluster.child_id,
            duplicate_id,
            cluster.canonical_id,
        ):
            raise KnowledgeRepairConflict("supersession_rejected")
        reconcile_superseded(db, cluster.family_id, cluster.child_id, duplicate_id)

    db.execute(
        delete(KnowledgeSearchTerm).where(
            KnowledgeSearchTerm.family_id == cluster.family_id,
            KnowledgeSearchTerm.child_id == cluster.child_id,
            KnowledgeSearchTerm.subject_id == cluster.subject_id,
            KnowledgeSearchTerm.knowledge_item_id == canonical.id,
        )
    )
    canonical.name = cluster.target_name
    canonical.normalized_name = normalized_target
    db.flush()
    add_search_terms(db, canonical)
    ChildrenService.invalidate_review_inventory(db, cluster.family_id, cluster.child_id)
