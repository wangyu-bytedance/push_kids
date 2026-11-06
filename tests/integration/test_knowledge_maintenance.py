from __future__ import annotations

import pytest
from push_kids.agent_processing.history_search import add_search_terms
from push_kids.knowledge.maintenance import (
    KnowledgeRepairCluster,
    KnowledgeRepairConflict,
    apply_repair_cluster,
)
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeOccurrence,
    KnowledgeSearchTerm,
    LearningRecord,
    ReviewFeedback,
    ReviewItem,
)
from sqlalchemy import func, select

from tests.integration.test_review_inventory import seed


def _cluster(app, family_id, child_id):
    subject_id, ids = seed(app, family_id, child_id, size=3)
    names = ["常见拟声词的认识与运用", "常用拟声词的认识与运用", "其他知识"]
    with app.state.database.session_factory() as db:
        for (_, knowledge_id), name in zip(ids, names, strict=True):
            knowledge = db.get(KnowledgeItem, knowledge_id)
            knowledge.name = name
            knowledge.normalized_name = name
            add_search_terms(db, knowledge)
        canonical_review = db.get(ReviewItem, ids[0][0])
        duplicate_review = db.get(ReviewItem, ids[1][0])
        canonical_review.review_count = 4
        duplicate_review.review_count = 3
        db.commit()
    return (
        KnowledgeRepairCluster(
            family_id=family_id,
            child_id=child_id,
            subject_id=subject_id,
            canonical_id=ids[0][1],
            canonical_old_name=names[0],
            target_name="拟声词的认识与运用",
            duplicate_ids=(ids[1][1],),
            duplicate_old_names=(names[1],),
        ),
        ids,
    )


def _formal_counts(db):
    return tuple(
        int(db.scalar(select(func.count()).select_from(model)) or 0)
        for model in (LearningRecord, KnowledgeOccurrence, ReviewFeedback, KnowledgeItem)
    )


def test_repair_renames_reindexes_and_supersedes_without_review_facts(app, family_headers, child):
    family_id, child_id = family_headers["X-Family-ID"], child["id"]
    cluster, ids = _cluster(app, family_id, child_id)
    with app.state.database.session_factory() as db:
        before = _formal_counts(db)
        apply_repair_cluster(db, cluster)
        after = _formal_counts(db)
        db.commit()
        canonical = db.get(KnowledgeItem, ids[0][1])
        duplicate = db.get(KnowledgeItem, ids[1][1])
        assert canonical.name == "拟声词的认识与运用"
        assert canonical.normalized_name == "拟声词的认识与运用"
        assert duplicate.review_status == "superseded"
        assert duplicate.superseded_by_knowledge_id == canonical.id
        assert db.get(ReviewItem, ids[0][0]).review_count == 4
        assert db.get(ReviewItem, ids[1][0]).review_count == 3
        terms = set(
            db.scalars(
                select(KnowledgeSearchTerm.term).where(
                    KnowledgeSearchTerm.knowledge_item_id == canonical.id
                )
            )
        )
        assert "拟声词的认识与运用" in terms
        assert "常见拟声词的认识与运用" not in terms
        assert before == after


@pytest.mark.parametrize("change", ["canonical_name", "duplicate_status", "wrong_scope"])
def test_repair_conflict_rolls_back_whole_cluster(app, family_headers, child, change):
    family_id, child_id = family_headers["X-Family-ID"], child["id"]
    cluster, ids = _cluster(app, family_id, child_id)
    with app.state.database.session_factory() as db:
        if change == "canonical_name":
            db.get(KnowledgeItem, ids[0][1]).name = "已变化"
        elif change == "duplicate_status":
            db.get(KnowledgeItem, ids[1][1]).review_status = "superseded"
        else:
            cluster = KnowledgeRepairCluster(**{**cluster.__dict__, "family_id": "other-family"})
        db.commit()
    with app.state.database.session_factory() as db:
        with pytest.raises(KnowledgeRepairConflict):
            apply_repair_cluster(db, cluster)
        db.rollback()
    with app.state.database.session_factory() as db:
        assert db.get(KnowledgeItem, ids[0][1]).normalized_name == "常见拟声词的认识与运用"
        expected = "superseded" if change == "duplicate_status" else "normal"
        assert db.get(KnowledgeItem, ids[1][1]).review_status == expected
