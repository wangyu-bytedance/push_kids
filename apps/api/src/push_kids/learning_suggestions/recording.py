"""Recoverable association of parent-confirmed actual learning, never suggested facts."""

from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select

from push_kids.learning.confirmation_query import confirmed_submission, existing_record_ids
from push_kids.learning_suggestions import queries
from push_kids.learning_suggestions.models import RecordIntent, StudyTask, StudyTaskRecord
from push_kids.learning_suggestions.service import lock_state
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.pagination import decode_cursor, encode_cursor
from push_kids.platform.time import utcnow


def intent_view(intent):
    return {
        "id": intent.id,
        "task_id": intent.task_id,
        "mode": intent.mode,
        "state": intent.state,
        "submission_id": intent.submission_id,
        "submission_idempotency_key": f"study:{intent.id}",
    }


def create_intent(db, family_id, child_id, actor, task_id, version, mode, request_id):
    shared = lock_state(db, family_id, child_id)
    prior = db.scalar(
        select(RecordIntent)
        .where(
            RecordIntent.family_id == family_id,
            RecordIntent.child_id == child_id,
            RecordIntent.request_id == request_id,
        )
        .with_for_update()
    )
    if prior:
        if prior.task_id != task_id or prior.mode != mode:
            raise ConflictError("这次操作标识已用于其他内容")
        db.commit()
        return intent_view(prior)
    task = queries.scoped(db, StudyTask, family_id, child_id, task_id, lock=True)
    if task is None:
        raise NotFoundError("没有找到这项待学")
    if task.version != version or task.state != "planned" or shared.pending_task_id != task.id:
        raise ConflictError("待学已有变化，请刷新后重试")
    intent = RecordIntent(
        family_id=family_id,
        child_id=child_id,
        task_id=task_id,
        task_version=task.version,
        mode=mode,
        created_by=actor,
        request_id=request_id,
    )
    db.add(intent)
    db.commit()
    return intent_view(intent)


def link_records(
    db, family_id, child_id, task_id, intent_id, submission_id=None, *, recovery=False
):
    shared = lock_state(db, family_id, child_id)
    intent = queries.scoped(db, RecordIntent, family_id, child_id, intent_id, lock=True)
    task = queries.scoped(db, StudyTask, family_id, child_id, task_id, lock=True)
    if intent is None or task is None or intent.task_id != task_id:
        raise NotFoundError("没有找到这次实际学习记录")
    if intent.state == "linked":
        if submission_id and submission_id != intent.submission_id:
            raise ConflictError("记录已关联到另一次确认")
        db.commit()
        return queries.task_view(task)
    if intent.state != "draft":
        raise ConflictError("这次记录操作已结束")
    confirmed = confirmed_submission(db, family_id, child_id, f"study:{intent.id}", submission_id)
    if confirmed is None or not confirmed["record_ids"]:
        if recovery:
            intent.recovery_after = utcnow() + timedelta(seconds=30)
            db.commit()
            return None
        raise ConflictError("请先确认本次实际学过的内容，再完成关联")
    for record_id in confirmed["record_ids"]:
        db.add(
            StudyTaskRecord(
                family_id=family_id,
                child_id=child_id,
                task_id=task.id,
                record_id=record_id,
                intent_id=intent.id,
                confirmed_at=confirmed["confirmed_at"],
            )
        )
    intent.submission_id, intent.state = confirmed["submission_id"], "linked"
    # Removal or a later different task never gets undone by a late confirmation.
    if task.state == "planned" and shared.pending_task_id == task.id:
        task.version += 1
        if intent.mode == "complete":
            task.state, task.completed_at = "recorded", confirmed["confirmed_at"]
            shared.pending_task_id = None
        else:
            task.last_partial_at = confirmed["confirmed_at"]
        shared.version += 1
    db.commit()
    return queries.task_view(task)


def records_page(db, family_id, child_id, task_id, *, limit=20, cursor=None):
    task = queries.scoped(db, StudyTask, family_id, child_id, task_id)
    if task is None:
        raise NotFoundError("没有找到这项待学")
    limit = min(50, max(1, limit))
    scope = ["study-records-v1", family_id, child_id, task_id]
    as_of = utcnow()
    query = select(StudyTaskRecord).where(
        StudyTaskRecord.family_id == family_id,
        StudyTaskRecord.child_id == child_id,
        StudyTaskRecord.task_id == task_id,
    )
    if cursor:
        anchor = decode_cursor(cursor, scope)
        try:
            as_of = datetime.fromisoformat(anchor["as_of"])
            after = datetime.fromisoformat(anchor["confirmed_at"])
            if not as_of.tzinfo or not after.tzinfo:
                raise ValueError
            query = query.where(
                or_(
                    StudyTaskRecord.confirmed_at < after,
                    and_(StudyTaskRecord.confirmed_at == after, StudyTaskRecord.id < anchor["id"]),
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("分页已失效，请刷新") from exc
    rows = list(
        db.scalars(
            query.where(StudyTaskRecord.created_at <= as_of)
            .order_by(StudyTaskRecord.confirmed_at.desc(), StudyTaskRecord.id.desc())
            .limit(limit + 1)
        )
    )
    page = rows[:limit]
    existing = existing_record_ids(db, family_id, child_id, [r.record_id for r in page])
    next_cursor = None
    if len(rows) > limit:
        last = page[-1]
        next_cursor = encode_cursor(
            scope,
            {
                "as_of": as_of.isoformat(),
                "confirmed_at": last.confirmed_at.isoformat(),
                "id": last.id,
            },
        )
    return {
        "items": [
            {
                "id": r.id,
                "record_id": r.record_id if r.record_id in existing else None,
                "removed": r.record_id not in existing,
                "confirmed_at": r.confirmed_at.isoformat(),
            }
            for r in page
        ],
        "next_cursor": next_cursor,
    }
