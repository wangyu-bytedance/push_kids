"""Bounded, family-scoped inputs for one analysis; no model-generated learning state."""

import json
from hashlib import sha256
from itertools import zip_longest
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.agent_processing.contracts import (
    MATERIAL_FINGERPRINT_KEY,
    AnalysisInput,
    ExistingKnowledgeContext,
    RecentLearningContext,
    TodoCandidate,
)
from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewItem,
    Subject,
)


def material_fingerprint(text: str | None, paths: list[Path]) -> str:
    # Order, identical pages and occurrence date do not change material identity.
    hashes = sorted({sha256(path.read_bytes()).hexdigest() for path in paths})
    return sha256(json.dumps([text or "", hashes], ensure_ascii=False).encode()).hexdigest()


def repeated_material(db: Session, submission: LearningSubmission, fingerprint: str) -> bool:
    previous = db.scalars(
        select(LearningSubmission.proposal_json)
        .where(
            LearningSubmission.family_id == submission.family_id,
            LearningSubmission.child_id == submission.child_id,
            LearningSubmission.id != submission.id,
            LearningSubmission.state.in_(["confirmed", "pending_confirmation"]),
        )
        .order_by(LearningSubmission.created_at.desc(), LearningSubmission.id)
        .limit(100)
    )
    return any(
        value and json.loads(value).get(MATERIAL_FINGERPRINT_KEY) == fingerprint
        for value in previous
    )


def build_analysis_input(
    db: Session, submission: LearningSubmission, paths: list[Path]
) -> AnalysisInput:
    if not submission.family_id or not submission.child_id or not submission.occurred_at:
        raise ValueError("submission context is incomplete")
    child = ChildrenService.get_child(db, submission.family_id, submission.child_id)
    subjects = list(
        db.scalars(
            select(Subject)
            .where(
                Subject.family_id == submission.family_id,
                Subject.child_id == submission.child_id,
                Subject.active.is_(True),
                Subject.kind == "learning",
            )
            .order_by(Subject.created_at, Subject.id)
            .limit(30)
        )
    )
    history_groups: list[list[RecentLearningContext]] = []
    knowledge_groups: list[list[ExistingKnowledgeContext]] = []
    for subject in subjects:
        records = list(
            db.scalars(
                select(LearningRecord)
                .where(
                    LearningRecord.family_id == submission.family_id,
                    LearningRecord.child_id == submission.child_id,
                    LearningRecord.subject_id == subject.id,
                    LearningRecord.occurred_at <= submission.occurred_at,
                )
                .order_by(LearningRecord.occurred_at.desc(), LearningRecord.id)
                .limit(20)
            )
        )
        # Parent-supplied subject/focus raises relevant records within each bounded subject pool.
        text = submission.input_text or ""
        records.sort(key=lambda row: relevance(text, row.summary or ""), reverse=True)
        history_groups.append(
            [
                RecentLearningContext(
                    record_id=row.id,
                    subject_name=subject.name,
                    summary=row.summary,
                    occurred_at=row.occurred_at.isoformat(),
                )
                for row in records[:10]
                if row.occurred_at is not None
            ]
        )
        rows = db.execute(
            select(KnowledgeItem, ReviewItem)
            .outerjoin(ReviewItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
            .where(
                KnowledgeItem.family_id == submission.family_id,
                KnowledgeItem.child_id == submission.child_id,
                KnowledgeItem.subject_id == subject.id,
                select(KnowledgeOccurrence.id)
                .where(
                    KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id,
                    KnowledgeOccurrence.family_id == submission.family_id,
                    KnowledgeOccurrence.occurred_at <= submission.occurred_at,
                )
                .exists(),
            )
            .order_by(KnowledgeItem.created_at.desc(), KnowledgeItem.id)
            .limit(30)
        ).all()
        rows = sorted(rows, key=lambda row: relevance(text, row[0].name), reverse=True)
        knowledge_groups.append(
            [
                ExistingKnowledgeContext(
                    knowledge_id=knowledge.id,
                    subject_name=subject.name,
                    name=knowledge.name,
                    category=knowledge.category,
                    review_step=review.step if review else None,
                    review_due_date=review.due_date.isoformat() if review else None,
                    review_active=review.active if review else None,
                )
                for knowledge, review in rows
            ]
        )
    histories = [row for group in zip_longest(*history_groups) for row in group if row is not None][
        :30
    ]
    knowledge = [
        row for group in zip_longest(*knowledge_groups) for row in group if row is not None
    ][:100]
    reviews = db.execute(
        select(ReviewItem, KnowledgeItem)
        .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
        .join(Subject, KnowledgeItem.subject_id == Subject.id)
        .where(
            ReviewItem.family_id == submission.family_id,
            ReviewItem.child_id == submission.child_id,
            ReviewItem.active.is_(True),
            Subject.kind == "learning",
            Subject.active.is_(True),
            select(KnowledgeOccurrence.id)
            .where(
                KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id,
                KnowledgeOccurrence.family_id == submission.family_id,
                KnowledgeOccurrence.occurred_at <= submission.occurred_at,
            )
            .exists(),
        )
        .order_by(ReviewItem.due_date, ReviewItem.id)
        .limit(50)
    ).all()
    return AnalysisInput(
        text=submission.input_text,
        occurred_at=submission.occurred_at.isoformat(),
        grade=child.grade,
        image_paths=paths,
        existing_subjects=[subject.name for subject in subjects],
        recent_learning=histories,
        existing_knowledge=knowledge,
        todo_candidates=[
            TodoCandidate(
                review_id=review.id,
                knowledge_name=item.name,
                step=review.step,
                due_date=review.due_date.isoformat(),
            )
            for review, item in reviews
        ],
    )


def relevance(text: str, value: str) -> int:
    """Lexical tie-break only; images are interpreted later by the provider."""
    return sum(text[index : index + 2] in value for index in range(max(0, len(text) - 1)))
