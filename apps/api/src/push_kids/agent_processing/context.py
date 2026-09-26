"""Bounded, family-scoped inputs for one analysis; no model-generated learning state."""

import json
from hashlib import sha256
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.agent_processing.contracts import (
    MATERIAL_FINGERPRINT_KEY,
    AnalysisInput,
    AnalysisInputError,
    SameDayKnowledgeContext,
    TodoCandidate,
)
from push_kids.children.service import PRESET_LEARNING_SUBJECTS, ChildrenService
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningSubmission,
    Subject,
)
from push_kids.planning.service import PlanningService
from push_kids.platform.time import local_date, local_day_bounds


def material_fingerprint(text: str | None, paths: list[Path]) -> str:
    # Order, identical pages and occurrence date do not change material identity.
    hashes = sorted({sha256(path.read_bytes()).hexdigest() for path in paths})
    return sha256(json.dumps([text or "", hashes], ensure_ascii=False).encode()).hexdigest()


def repeated_material(db: Session, submission: LearningSubmission, fingerprint: str) -> bool:
    if submission.occurred_at is None:
        return False
    day_start, day_end = local_day_bounds(local_date(submission.occurred_at))
    previous = db.scalars(
        select(LearningSubmission.proposal_json)
        .where(
            LearningSubmission.family_id == submission.family_id,
            LearningSubmission.child_id == submission.child_id,
            LearningSubmission.id != submission.id,
            LearningSubmission.state.in_(["confirmed", "pending_confirmation"]),
            LearningSubmission.occurred_at >= day_start,
            LearningSubmission.occurred_at <= day_end,
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
        raise AnalysisInputError("submission context is incomplete")
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
    occurrence_day = local_date(submission.occurred_at)
    day_start, day_end = local_day_bounds(occurrence_day)
    same_day_rows = db.execute(
        select(KnowledgeItem, Subject)
        .join(
            KnowledgeOccurrence,
            KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id,
        )
        .join(Subject, KnowledgeItem.subject_id == Subject.id)
        .where(
            KnowledgeItem.family_id == submission.family_id,
            KnowledgeItem.child_id == submission.child_id,
            KnowledgeOccurrence.family_id == submission.family_id,
            KnowledgeOccurrence.occurred_at >= day_start,
            KnowledgeOccurrence.occurred_at <= day_end,
            Subject.active.is_(True),
            Subject.kind == "learning",
        )
        .distinct()
        .limit(201)
    ).all()
    if len(same_day_rows) > 200:
        raise AnalysisInputError("too many same-day learning items for bounded analysis")

    today = local_date()
    today_plan: list[dict] = []
    if occurrence_day == today:
        selection = PlanningService.daily_review_selection(
            db,
            submission.family_id,
            submission.child_id,
            today,
            known_child=child,
        )
        today_plan = selection["all_items"]
    configured_subjects = [subject.name for subject in subjects]
    analysis_subjects = list(dict.fromkeys([*configured_subjects, *PRESET_LEARNING_SUBJECTS]))
    return AnalysisInput(
        text=submission.input_text,
        occurred_at=submission.occurred_at.isoformat(),
        grade=child.grade,
        image_paths=paths,
        existing_subjects=configured_subjects,
        analysis_subjects=analysis_subjects,
        recent_learning=[],
        existing_knowledge=[],
        same_day_learning=[
            SameDayKnowledgeContext(
                knowledge_id=item.id,
                subject_name=subject.name,
                name=item.name,
                category=item.category,
            )
            for item, subject in same_day_rows
        ],
        todo_candidates=[
            TodoCandidate(
                review_id=item["review_id"],
                knowledge_name=item["knowledge_name"],
                knowledge_id=item["knowledge_id"],
                subject_name=item["subject_name"],
                step=item["step"],
                due_date=item["due_date"],
                eligible_on=today.isoformat(),
                match_kind="today_review",
                state_version=item.get("state_version"),
                last_reviewed_on=item.get("last_reviewed_on"),
                review_count=item.get("review_count"),
                plan_state=item.get("state"),
            )
            for item in today_plan
        ],
    )
