"""Bounded enqueue and versioned generation results; no network inside transactions."""

import json
import re
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from push_kids.agent_processing.suggestion_contracts import LearningSuggestionContent
from push_kids.knowledge.learning_context import get_context
from push_kids.learning_suggestions import queries
from push_kids.learning_suggestions.models import StudyTask, Suggestion, SuggestionJob
from push_kids.learning_suggestions.policy import eligibility
from push_kids.platform.errors import ConflictError, TooManyRequestsError
from push_kids.platform.time import local_date, local_day_bounds, utcnow


def content_hash(content: dict) -> str:
    # Stable across transport-only metadata and edits to the estimated duration.
    return queries.fingerprint(
        {
            k: re.sub(r"\s+", "", str(content.get(k, ""))).casefold()
            for k in ("title", "instructions", "subject_id")
        }
    )


def check_quota(db, family_id, child_id, *, claiming=False, retrying=False):
    start, _ = local_day_bounds(local_date())
    scope = (SuggestionJob.family_id == family_id, SuggestionJob.child_id == child_id)
    attempts = case((SuggestionJob.attempts > 0, SuggestionJob.attempts), else_=1)
    totals = db.execute(
        select(
            func.coalesce(func.sum(attempts), 0),
            func.coalesce(
                func.sum(
                    case(
                        (SuggestionJob.updated_at >= utcnow() - timedelta(hours=1), attempts),
                        else_=0,
                    )
                ),
                0,
            ),
        ).where(*scope, SuggestionJob.updated_at >= start)
    ).one()
    concurrent = (
        db.scalar(
            select(func.count())
            .select_from(SuggestionJob)
            .where(
                SuggestionJob.family_id == family_id, SuggestionJob.state.in_(["queued", "running"])
            )
        )
        or 0
    )
    # A queued job reserves its first attempt. When claiming, that reservation is
    # already included; a retry needs another unit. A job crossing a day/hour
    # conservatively carries its previous attempts into the new window.
    full = (
        (totals[0] >= 10 or totals[1] >= 3)
        if (not claiming or retrying)
        else (totals[0] > 10 or totals[1] > 3)
    )
    if full or (not claiming and concurrent >= 2):
        raise TooManyRequestsError("建议生成次数较多，请稍后再试；仍可手动记录学习")


def enqueue(
    db: Session,
    family_id: str,
    child_id: str,
    shared,
    request_id: str,
    *,
    context=None,
    excluded=None,
    replay_checked=False,
) -> SuggestionJob:
    if not db.info.get("learning_suggestions_enabled", False):
        raise ConflictError("学习建议暂未启用")
    replay = (
        None
        if replay_checked
        else db.scalar(
            select(SuggestionJob)
            .where(
                SuggestionJob.family_id == family_id,
                SuggestionJob.child_id == child_id,
                SuggestionJob.request_id == request_id,
            )
            .with_for_update()
        )
    )
    if replay:
        return replay
    if shared.pending_task_id:
        raise ConflictError("已有一项待学，请先记录或删除")
    if excluded is None and not shared.current_suggestion_id and int(shared.version or 0) > 0:
        removed_content = db.scalar(
            select(Suggestion.validated_content_json)
            .join(StudyTask, StudyTask.suggestion_id == Suggestion.id)
            .where(
                StudyTask.family_id == family_id,
                StudyTask.child_id == child_id,
                StudyTask.state == "removed",
                Suggestion.family_id == family_id,
                Suggestion.child_id == child_id,
            )
            .order_by(StudyTask.approved_at.desc(), StudyTask.id.desc())
            .limit(1)
        )
        if removed_content:
            excluded = json.loads(removed_content)
    context = context or get_context(db, family_id, child_id)
    code = eligibility(context, local_date(), enabled=True)
    if code != "eligible" and not (excluded and code in {"recent_new", "warming_up"}):
        raise ConflictError("暂不满足学习建议条件，请先核对年级与已学内容")
    active = queries.scoped(db, SuggestionJob, family_id, child_id, shared.active_job_id, lock=True)
    if active and active.state in {"queued", "running"}:
        return active
    check_quota(db, family_id, child_id)
    bounded = dict(context)
    previous = list(
        db.scalars(
            select(Suggestion.validated_content_json)
            .join(StudyTask, StudyTask.suggestion_id == Suggestion.id)
            .where(
                StudyTask.family_id == family_id,
                StudyTask.child_id == child_id,
                Suggestion.family_id == family_id,
                Suggestion.child_id == child_id,
            )
            .order_by(StudyTask.approved_at.desc(), StudyTask.id.desc())
            .limit(6)
        )
    )
    bounded["previous"] = [{"title": json.loads(p or "{}").get("title", "")} for p in previous]
    if excluded:
        bounded["excluded_content"] = {
            k: excluded[k] for k in ("title", "instructions", "subject_id")
        }
    while (
        len(json.dumps(bounded, ensure_ascii=False).encode()) > 24 * 1024
        and len(bounded["knowledge"]) > 1
    ):
        bounded["knowledge"] = bounded["knowledge"][:-1]
        bounded["truncated"] = True
    payload = json.dumps(bounded, ensure_ascii=False)
    if len(payload.encode()) > 24 * 1024:
        raise ValueError("学习上下文超出预算，请稍后重试")
    job = SuggestionJob(
        id=str(uuid4()),
        family_id=family_id,
        child_id=child_id,
        request_id=request_id,
        input_revision=context["input_revision"],
        input_fingerprint=queries.fingerprint(context),
        bounded_context_json=payload,
        excluded_content_hash=content_hash(excluded) if excluded else None,
    )
    db.add(job)
    shared.active_job_id = job.id
    shared.version += 1
    db.flush()
    return job


def validate_content(content: LearningSuggestionContent, context: dict, excluded_hash=None) -> dict:
    # Provider adapters may return a constructed/mutated instance; validate before persisting.
    content = LearningSuggestionContent.model_validate(content.model_dump())
    payload = content.model_dump()
    if len(json.dumps(payload, ensure_ascii=False).encode()) > 6144:
        raise ValueError("output_budget")
    subjects = {s["id"] for s in context["subjects"]}
    sources = {k["alias"]: k for k in context["knowledge"]}
    if content.subject_id not in subjects or len(set(content.source_aliases)) != len(
        content.source_aliases
    ):
        raise ValueError("invalid_subject_or_source")
    if any(
        a not in sources or sources[a]["subject_id"] != content.subject_id
        for a in content.source_aliases
    ):
        raise ValueError("invalid_source")
    if re.search(
        r"已[经]?完全掌握|已掌握|成绩为|正确率|下一课必须|教材第.{0,8}页|课标规定",
        json.dumps(payload, ensure_ascii=False),
    ):
        raise ValueError("unsupported_claim")
    if excluded_hash and content_hash(payload) == excluded_hash:
        raise ValueError("repeated_content")
    payload["sources"] = [
        {"knowledge_id": sources[a]["id"], "name": sources[a]["name"]}
        for a in content.source_aliases
    ]
    payload["subject_name"] = next(
        s["name"] for s in context["subjects"] if s["id"] == content.subject_id
    )
    return payload


def commit_result(db, family_id, child_id, shared, job, token, content):
    if job.state != "running" or job.lease_token != token or job.lease_until <= utcnow():
        return False
    context = get_context(db, family_id, child_id)
    if (
        not db.info.get("learning_suggestions_enabled", False)
        or not context.get("active")
        or shared.active_job_id != job.id
        or shared.pending_task_id
        or queries.fingerprint(context) != job.input_fingerprint
    ):
        job.state, job.safe_error_code = "cancelled", "context_changed"
        job.lease_until, job.lease_token = None, None
        return False
    payload = validate_content(
        content, json.loads(job.bounded_context_json), job.excluded_content_hash
    )
    old = queries.scoped(
        db, Suggestion, family_id, child_id, shared.current_suggestion_id, lock=True
    )
    if old and old.status in {"proposed", "deferred_today"}:
        old.status = "replaced"
        old.version += 1
    proposal = Suggestion(
        family_id=family_id,
        child_id=child_id,
        subject_id=payload["subject_id"],
        validated_content_json=json.dumps(payload, ensure_ascii=False),
        input_fingerprint=job.input_fingerprint,
        expires_at=utcnow() + timedelta(days=7),
    )
    db.add(proposal)
    db.flush()
    shared.current_suggestion_id, shared.active_job_id = proposal.id, None
    shared.version += 1
    job.state, job.result_suggestion_id = "succeeded", proposal.id
    job.lease_until, job.lease_token = None, None
    return True
