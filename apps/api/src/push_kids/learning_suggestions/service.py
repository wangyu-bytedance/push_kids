"""Parent decisions and shared state; approvals never write formal learning."""

import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from push_kids.knowledge.learning_context import get_context, purge_context
from push_kids.learning_suggestions import queries
from push_kids.learning_suggestions.models import (
    PromptDay,
    RecordIntent,
    StudyTask,
    StudyTaskRecord,
    Suggestion,
    SuggestionJob,
    SuggestionState,
)
from push_kids.learning_suggestions.policy import eligibility
from push_kids.persistence.models import Child, Family
from push_kids.platform.errors import AppError, ConflictError, NotFoundError
from push_kids.platform.time import local_date, utcnow


def lock_state(db: Session, family_id: str, child_id: str) -> SuggestionState:
    shared, _child = _lock_state_and_child(db, family_id, child_id)
    return shared


def _lock_state_and_child(
    db: Session, family_id: str, child_id: str
) -> tuple[SuggestionState, Child]:
    family = db.scalar(
        select(Family)
        .where(Family.id == family_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if family is not None and family.status != "active":
        raise ConflictError("家庭正在清理，暂时不能修改")
    child = db.scalar(
        select(Child)
        .where(Child.family_id == family_id, Child.id == child_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if child is None:
        raise NotFoundError("没有找到这个孩子")
    if child.deleting:
        raise ConflictError("这个孩子的资料正在清理，暂时不能修改")
    if not child.active:
        raise ConflictError("这个学习档案已归档，恢复后才能继续记录")
    shared = queries.state(db, family_id, child_id, lock=True)
    if shared is None:
        shared = SuggestionState(family_id=family_id, child_id=child_id, version=0)
        db.add(shared)
        db.flush()
    return shared, child


def require_enabled(db: Session) -> None:
    if not db.info.get("learning_suggestions_enabled", False):
        raise ConflictError("学习建议暂未启用，已确认的待学仍可记录")


def proposal_for_write(db, family_id, child_id, suggestion_id, version, shared):
    proposal = queries.scoped(db, Suggestion, family_id, child_id, suggestion_id, lock=True)
    if proposal is None:
        raise NotFoundError("没有找到这项建议")
    if shared.current_suggestion_id != suggestion_id or proposal.version != version:
        raise ConflictError("建议已有变化，请刷新后重试")
    if not queries.valid_proposal(proposal, get_context(db, family_id, child_id)):
        raise ConflictError("学习内容或年级已有变化，请重新生成建议")
    return proposal


def automatic_prompt(
    db: Session, family_id: str, child_id: str, actor: str, request_id: str
) -> dict:
    from push_kids.learning_suggestions.generation import enqueue

    shared, child = _lock_state_and_child(db, family_id, child_id)
    context = get_context(db, family_id, child_id, child=child)
    code = eligibility(
        context,
        local_date(),
        enabled=db.info.get("learning_suggestions_enabled", False),
        pending=bool(shared.pending_task_id),
    )
    prior = db.get(PromptDay, (family_id, child_id, local_date()))
    if code != "eligible" or prior is not None:
        db.commit()
        return {"can_auto_open": False, "eligibility": code}
    db.add(
        PromptDay(
            family_id=family_id,
            child_id=child_id,
            prompt_on=local_date(),
            consumed_by=actor,
            request_id=request_id,
        )
    )
    proposal = queries.scoped(
        db, Suggestion, family_id, child_id, shared.current_suggestion_id, lock=True
    )
    job = None
    if proposal is None or not queries.valid_proposal(proposal, context):
        job = enqueue(db, family_id, child_id, shared, request_id, context=context)
    view = queries.project_current(
        context,
        shared,
        None,
        proposal,
        job,
        enabled=db.info.get("learning_suggestions_enabled", False),
    )
    db.commit()
    return {
        "can_auto_open": True,
        "prompt_on": local_date().isoformat(),
        "request_id": request_id,
        "current": view,
    }


def prompt_displayed(db, family_id, child_id, prompt_on, request_id):
    lock_state(db, family_id, child_id)
    row = db.get(PromptDay, (family_id, child_id, prompt_on))
    if row and row.request_id == request_id and row.displayed_at is None:
        row.displayed_at = utcnow()
    db.commit()
    return {"acknowledged": bool(row), "can_auto_open": False}


def approve(db, family_id, child_id, actor, suggestion_id, version):
    require_enabled(db)
    shared = lock_state(db, family_id, child_id)
    existing = queries.scoped(db, StudyTask, family_id, child_id, shared.pending_task_id, lock=True)
    if existing:
        if existing.suggestion_id == suggestion_id:
            db.commit()
            return queries.task_view(
                existing, queries.scoped(db, Suggestion, family_id, child_id, suggestion_id)
            )
        raise ConflictError("已有一项待学，请先记录或删除")
    previous = db.scalar(
        select(StudyTask)
        .where(
            StudyTask.family_id == family_id,
            StudyTask.child_id == child_id,
            StudyTask.suggestion_id == suggestion_id,
        )
        .limit(1)
    )
    if previous:
        db.commit()
        return queries.task_view(
            previous, queries.scoped(db, Suggestion, family_id, child_id, suggestion_id)
        )
    proposal = proposal_for_write(db, family_id, child_id, suggestion_id, version, shared)
    proposal.status, proposal.approved_by, proposal.approved_at = "approved", actor, utcnow()
    proposal.version += 1
    task = StudyTask(
        family_id=family_id, child_id=child_id, suggestion_id=proposal.id, approved_by=actor
    )
    db.add(task)
    db.flush()
    shared.pending_task_id, shared.current_suggestion_id = task.id, None
    shared.version += 1
    db.commit()
    return queries.task_view(task, proposal)


def edit(db, family_id, child_id, suggestion_id, body):
    require_enabled(db)
    shared = lock_state(db, family_id, child_id)
    if shared.pending_task_id:
        raise ConflictError("待学已经确认，请在记录实际学习时核对内容")
    proposal = proposal_for_write(
        db, family_id, child_id, suggestion_id, body.expected_version, shared
    )
    content = json.loads(proposal.validated_content_json)
    content.update(
        title=body.title, instructions=body.instructions, estimated_minutes=body.estimated_minutes
    )
    proposal.validated_content_json = json.dumps(content, ensure_ascii=False)
    proposal.version += 1
    shared.version += 1
    db.commit()
    return queries.proposal_view(proposal)


def defer(db, family_id, child_id, actor, suggestion_id, version):
    shared = lock_state(db, family_id, child_id)
    proposal = proposal_for_write(db, family_id, child_id, suggestion_id, version, shared)
    proposal.status = "deferred_today"
    proposal.version += 1
    shared.version += 1
    prior = db.get(PromptDay, (family_id, child_id, local_date()))
    if prior is None:
        db.add(
            PromptDay(
                family_id=family_id,
                child_id=child_id,
                prompt_on=local_date(),
                consumed_by=actor,
                request_id=f"defer:{proposal.id}",
            )
        )
    db.commit()
    return queries.proposal_view(proposal)


def remove_task(db, family_id, child_id, task_id, version, request_id):
    from push_kids.learning_suggestions.generation import enqueue

    shared, child = _lock_state_and_child(db, family_id, child_id)
    task = queries.scoped(db, StudyTask, family_id, child_id, task_id, lock=True)
    if task is None:
        raise NotFoundError("没有找到这项待学")
    if task.state == "removed":
        db.commit()
        return {
            "removed": True,
            "job": queries.job_view(
                queries.scoped(db, SuggestionJob, family_id, child_id, shared.active_job_id)
            )
            if shared.active_job_id
            else None,
        }
    if task.state != "planned" or task.version != version or shared.pending_task_id != task.id:
        raise ConflictError("待学已有变化，请刷新后重试")
    proposal = queries.scoped(db, Suggestion, family_id, child_id, task.suggestion_id)
    task.state, task.removed_at = "removed", utcnow()
    task.version += 1
    shared.pending_task_id = None
    shared.version += 1
    # Enqueue validates eligibility/resources before mutating job state. Keep the
    # parent removal when that validation fails; provider work starts after commit.
    excluded = json.loads(proposal.validated_content_json) if proposal else None
    try:
        with db.no_autoflush:
            job = enqueue(
                db,
                family_id,
                child_id,
                shared,
                request_id,
                excluded=excluded,
                context=get_context(db, family_id, child_id, child=child),
            )
        db.commit()
        return {"removed": True, "job": queries.job_view(job)}
    except (AppError, ValueError):
        db.commit()
        return {"removed": True, "job": None, "error_code": "generation_unavailable"}


def generate(db, family_id, child_id, expected_version, request_id, replace_suggestion_id=None):
    from push_kids.learning_suggestions.generation import enqueue

    shared = lock_state(db, family_id, child_id)
    replay = db.scalar(
        select(SuggestionJob).where(
            SuggestionJob.family_id == family_id,
            SuggestionJob.child_id == child_id,
            SuggestionJob.request_id == request_id,
        )
    )
    if replay:
        db.commit()
        return queries.job_view(replay)
    if shared.version != expected_version:
        raise ConflictError("建议已有变化，请刷新后重试")
    excluded = None
    if replace_suggestion_id:
        old = queries.scoped(db, Suggestion, family_id, child_id, replace_suggestion_id, lock=True)
        if (
            old is None
            or shared.current_suggestion_id != old.id
            or old.status not in {"proposed", "deferred_today"}
        ):
            raise ConflictError("建议已有变化，请刷新后重试")
        excluded = json.loads(old.validated_content_json)
        old.status = "replaced"
        old.version += 1
        shared.current_suggestion_id = None
    job = enqueue(
        db, family_id, child_id, shared, request_id, excluded=excluded, replay_checked=True
    )
    db.commit()
    return queries.job_view(job)


def purge_data(db: Session, family_id: str, child_id: str | None = None) -> None:
    for model in (
        StudyTaskRecord,
        RecordIntent,
        StudyTask,
        SuggestionJob,
        PromptDay,
        Suggestion,
        SuggestionState,
    ):
        query = delete(model).where(model.family_id == family_id)
        if child_id:
            query = query.where(model.child_id == child_id)
        db.execute(query)
    purge_context(db, family_id, child_id)
