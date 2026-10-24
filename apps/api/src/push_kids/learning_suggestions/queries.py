"""Bounded, scoped suggestion reads and public Today projection."""

import json
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.knowledge.learning_context import get_context
from push_kids.learning_suggestions.models import (
    StudyTask,
    Suggestion,
    SuggestionJob,
    SuggestionState,
)
from push_kids.learning_suggestions.policy import eligibility
from push_kids.platform.errors import NotFoundError
from push_kids.platform.time import local_date, utcnow


def fingerprint(context: dict) -> str:
    return sha256(
        json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def scoped(db: Session, model, family_id: str, child_id: str, item_id: str | None, *, lock=False):
    if not item_id:
        return None
    query = select(model).where(
        model.family_id == family_id, model.child_id == child_id, model.id == item_id
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    return db.scalar(query)


def state(db: Session, family_id: str, child_id: str, *, lock=False) -> SuggestionState | None:
    query = select(SuggestionState).where(
        SuggestionState.family_id == family_id, SuggestionState.child_id == child_id
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    return db.scalar(query)


def proposal_view(proposal: Suggestion | None) -> dict | None:
    if proposal is None:
        return None
    return {
        "id": proposal.id,
        "version": proposal.version,
        "status": proposal.status,
        **json.loads(proposal.validated_content_json or "{}"),
    }


def task_view(task: StudyTask | None, proposal: Suggestion | None = None) -> dict | None:
    if task is None:
        return None
    return {
        "id": task.id,
        "version": task.version,
        "state": task.state,
        "last_partial_at": task.last_partial_at.isoformat() if task.last_partial_at else None,
        "approved_at": task.approved_at.isoformat() if task.approved_at else None,
        "content": proposal_view(proposal),
    }


def job_view(job: SuggestionJob) -> dict:
    return {
        "id": job.id,
        "state": job.state,
        "attempts": job.attempts,
        "suggestion_id": job.result_suggestion_id,
        "error_code": job.safe_error_code,
    }


def valid_proposal(proposal: Suggestion, context: dict) -> bool:
    return (
        proposal.status in {"proposed", "deferred_today"}
        and proposal.expires_at is not None
        and proposal.expires_at > utcnow()
        and proposal.input_fingerprint == fingerprint(context)
    )


def current(db: Session, family_id: str, child_id: str) -> dict:
    context = get_context(db, family_id, child_id)
    if not context:
        raise NotFoundError("没有找到这个孩子")
    shared = state(db, family_id, child_id)
    task = scoped(db, StudyTask, family_id, child_id, shared.pending_task_id if shared else None)
    proposal = scoped(
        db,
        Suggestion,
        family_id,
        child_id,
        task.suggestion_id if task else (shared.current_suggestion_id if shared else None),
    )
    job = scoped(db, SuggestionJob, family_id, child_id, shared.active_job_id if shared else None)
    can_regenerate_after_removal = False
    if not task and not proposal:
        code = eligibility(
            context, local_date(), enabled=db.info.get("learning_suggestions_enabled", False)
        )
        if code in {"recent_new", "warming_up"}:
            can_regenerate_after_removal = bool(
                db.scalar(
                    select(StudyTask.id)
                    .where(
                        StudyTask.family_id == family_id,
                        StudyTask.child_id == child_id,
                        StudyTask.state == "removed",
                    )
                    .limit(1)
                )
            )
    return project_current(
        context,
        shared,
        task,
        proposal,
        job,
        enabled=db.info.get("learning_suggestions_enabled", False),
        can_regenerate_after_removal=can_regenerate_after_removal,
    )


def project_current(
    context, shared, task, proposal, job, *, enabled, can_regenerate_after_removal=False
):
    """Pure response projection, also used before committing a prompt command."""
    code = eligibility(
        context,
        local_date(),
        enabled=enabled,
        pending=task is not None,
    )
    is_valid = bool(proposal and (task or valid_proposal(proposal, context)))
    return {
        "day": local_date().isoformat(),
        "version": int(shared.version or 0) if shared else 0,
        "eligibility": code,
        "proposal": proposal_view(proposal) if is_valid and not task else None,
        "task": task_view(task, proposal),
        "job": job_view(job) if job else None,
        "stale": bool(proposal and not is_valid),
        "can_regenerate": code == "eligible" or can_regenerate_after_removal,
        "coverage": context.get("coverage"),
    }


def get_job(db: Session, family_id: str, child_id: str, job_id: str) -> dict:
    ChildrenService.get_child(db, family_id, child_id)
    job = scoped(db, SuggestionJob, family_id, child_id, job_id)
    if job is None:
        raise NotFoundError("没有找到这项生成请求")
    return job_view(job)
