"""Family-scoped read projections of submissions and confirmed learning evidence."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from push_kids.children.service import ChildrenService
from push_kids.persistence.models import (
    AgentJob,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    MediaObject,
    Subject,
    SubmissionMedia,
)
from push_kids.platform.errors import GoneError, NotFoundError
from push_kids.platform.time import SHANGHAI, utcnow

PENDING = ("queued", "analyzing", "pending_confirmation", "failed")


def _boundary(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time(), tzinfo=SHANGHAI)


def _stored_evidence(payload: str | None) -> list:
    """Stored evidence is untrusted history: unreadable or non-list content reads as empty."""
    if not payload:
        return []
    try:
        parsed = json.loads(payload)
    except (ValueError, TypeError):
        return []
    return parsed if isinstance(parsed, list) else []


def _knowledge_view(item: KnowledgeItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "confidence": item.confidence,
        "evidence": _stored_evidence(item.evidence_json),
    }


class LearningHistory:
    @staticmethod
    def submission(db: Session, family: str, child: str, sid: str) -> LearningSubmission:
        ChildrenService.get_child(db, family, child)
        item = db.scalar(
            select(LearningSubmission).where(
                LearningSubmission.id == sid,
                LearningSubmission.family_id == family,
                LearningSubmission.child_id == child,
            )
        )
        if item is None:
            raise NotFoundError("没有找到这条学习记录")
        return item

    @staticmethod
    def page(
        db: Session,
        family: str,
        child: str,
        *,
        view: str = "confirmed",
        q: str = "",
        subject_id: str | None = None,
        source: str | None = None,
        start: date | None = None,
        end: date | None = None,
        cancelled: bool = False,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict:
        ChildrenService.get_child(db, family, child)
        if start and end and start > end:
            raise ValueError("开始日期不能晚于结束日期")
        if subject_id:
            subject = db.scalar(
                select(Subject.id).where(
                    Subject.id == subject_id,
                    Subject.family_id == family,
                    Subject.child_id == child,
                )
            )
            if subject is None:
                raise NotFoundError("没有找到所选科目")
        # "r3" marks the row identity used by the cursor: one row per learning record, because a
        # submission that spans subjects now holds several records. Older cursors stop matching and
        # the client is told to refresh instead of silently skipping rows.
        scope = hashlib.sha256(
            json.dumps(
                ["r3", family, child, view, q, subject_id, source, str(start), str(end), cancelled],
                ensure_ascii=False,
            ).encode()
        ).hexdigest()
        upper = utcnow()
        anchor = None
        if cursor:
            try:
                payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
                if payload["scope"] != scope:
                    raise ValueError
                upper = datetime.fromisoformat(payload["upper"])
                anchor = (
                    datetime.fromisoformat(payload["at"]),
                    payload["id"],
                    payload["record_id"],
                )
                if not upper.tzinfo or not anchor[0].tzinfo:
                    raise ValueError
                if not isinstance(anchor[1], str) or not isinstance(anchor[2], str):
                    raise ValueError
            except (ValueError, KeyError, TypeError, UnicodeError) as exc:
                raise ValueError("分页已失效，请刷新列表") from exc
        s, r = LearningSubmission, LearningRecord
        if view == "confirmed":
            # Confirmed rows have the same occurrence time as their source submission. Starting
            # from the record lets the tenant/time/submission index satisfy keyset ordering without
            # sorting the complete history table.
            timestamp = r.occurred_at
            query = (
                select(s, r, Subject)
                .select_from(r)
                .join(
                    s,
                    and_(
                        s.id == r.submission_id,
                        s.family_id == family,
                        s.child_id == child,
                    ),
                )
                .join(Subject, and_(Subject.id == r.subject_id, Subject.family_id == family))
            )
        else:
            timestamp = s.created_at
            query = (
                select(s, r, Subject)
                .outerjoin(
                    r,
                    and_(
                        r.submission_id == s.id,
                        r.family_id == family,
                        r.child_id == child,
                    ),
                )
                .outerjoin(Subject, and_(Subject.id == r.subject_id, Subject.family_id == family))
            )
        query = query.where(s.family_id == family, s.child_id == child, s.created_at <= upper)
        if view == "confirmed":
            query = query.where(
                s.state == "confirmed",
                r.family_id == family,
                r.child_id == child,
                r.created_at <= upper,
            )
        elif view == "pending":
            query = query.where(s.state.in_(PENDING))
        if cancelled:
            query = query.where(s.state == "cancelled")
        if subject_id:
            query = query.where(r.subject_id == subject_id)
        if source:
            query = query.where(s.source == ("photo" if source == "photo" else "manual"))
        if start:
            query = query.where(timestamp >= _boundary(start))
        if end:
            query = query.where(timestamp < _boundary(end + timedelta(days=1)))
        if q:
            knowledge_match = (
                select(KnowledgeOccurrence.id)
                .join(
                    KnowledgeItem,
                    KnowledgeItem.id == KnowledgeOccurrence.knowledge_item_id,
                )
                .where(
                    KnowledgeOccurrence.learning_record_id == r.id,
                    KnowledgeOccurrence.family_id == family,
                    KnowledgeItem.family_id == family,
                    KnowledgeItem.name.contains(q, autoescape=True),
                )
                .exists()
            )
            # JSON summary extraction is supported by both SQLite and MySQL.
            draft_summary = func.json_extract(s.proposal_json, "$.summary")
            query = query.where(
                or_(
                    r.summary.contains(q, autoescape=True),
                    s.input_text.contains(q, autoescape=True),
                    knowledge_match,
                    and_(s.state != "confirmed", draft_summary.contains(q, autoescape=True)),
                )
            )
        submission_key = r.submission_id if view == "confirmed" else s.id
        record_key = r.id if view == "confirmed" else func.coalesce(r.id, "")
        if anchor:
            query = query.where(
                or_(
                    timestamp < anchor[0],
                    and_(timestamp == anchor[0], submission_key < anchor[1]),
                    and_(
                        timestamp == anchor[0],
                        submission_key == anchor[1],
                        record_key < anchor[2],
                    ),
                )
            )
        rows = db.execute(
            query.order_by(timestamp.desc(), submission_key.desc(), record_key.desc()).limit(
                limit + 1
            )
        ).all()
        more = len(rows) > limit
        rows = rows[:limit]
        ids = [s.id for s, _, _ in rows]
        media_counts: dict = (
            dict(
                db.execute(
                    select(SubmissionMedia.submission_id, func.count())
                    .where(
                        SubmissionMedia.submission_id.in_(ids),
                    )
                    .group_by(SubmissionMedia.submission_id)
                )
                .tuples()
                .all()
            )
            if ids
            else {}
        )
        record_ids = [r.id for _, r, _ in rows if r]
        knowledge_counts: dict = (
            dict(
                db.execute(
                    select(KnowledgeOccurrence.learning_record_id, func.count())
                    .where(
                        KnowledgeOccurrence.learning_record_id.in_(record_ids),
                        KnowledgeOccurrence.family_id == family,
                    )
                    .group_by(KnowledgeOccurrence.learning_record_id)
                )
                .tuples()
                .all()
            )
            if record_ids
            else {}
        )
        items = []
        for submission, record, subject in rows:
            proposal = json.loads(submission.proposal_json or "{}")
            items.append(
                {
                    "id": record.id if record else submission.id,
                    "submission_id": submission.id,
                    "record_id": record.id if record else None,
                    "state": submission.state,
                    "source": submission.source,
                    "occurred_at": submission.occurred_at.isoformat(),
                    "created_at": submission.created_at.isoformat(),
                    "summary": record.summary
                    if record
                    else proposal.get("summary") or submission.input_text or "",
                    "subject_id": subject.id if subject else None,
                    "subject_name": subject.name if subject else proposal.get("subject_name"),
                    "media_count": media_counts.get(submission.id, 0),
                    "knowledge_count": knowledge_counts.get(record.id, 0) if record else 0,
                }
            )
        next_cursor = None
        if more and rows:
            last, last_record, _ = rows[-1]
            if view == "confirmed":
                if last_record is None:
                    raise RuntimeError("确认记录缺少学习记录")
                at = last_record.occurred_at
            else:
                at = last.created_at
            next_cursor = base64.urlsafe_b64encode(
                json.dumps(
                    {
                        "scope": scope,
                        "upper": upper.isoformat(),
                        "at": at.isoformat(),
                        "id": last.id,
                        "record_id": last_record.id if last_record else "",
                    }
                ).encode()
            ).decode()
        pending_count = (
            db.scalar(
                select(func.count())
                .select_from(s)
                .where(
                    s.family_id == family,
                    s.child_id == child,
                    s.state.in_(PENDING),
                )
            )
            or 0
        )
        has_job = select(AgentJob.id).where(AgentJob.submission_id == s.id).exists()
        processing = (
            db.scalar(
                select(s.id)
                .where(
                    s.family_id == family,
                    s.child_id == child,
                    or_(s.state == "analyzing", and_(s.state == "queued", has_job)),
                )
                .limit(1)
            )
            is not None
        )
        return {
            "items": items,
            "next_cursor": next_cursor,
            "pending_count": pending_count,
            "has_processing": processing,
        }

    @classmethod
    def detail(cls, db: Session, family: str, child: str, sid: str) -> dict:
        item = cls.submission(db, family, child, sid)
        assert item.occurred_at is not None and item.created_at is not None
        # One submission holds one record per subject, in confirmation order.
        rows = db.execute(
            select(LearningRecord, Subject)
            .join(Subject, Subject.id == LearningRecord.subject_id)
            .where(
                LearningRecord.submission_id == sid,
                LearningRecord.family_id == family,
                LearningRecord.child_id == child,
                Subject.family_id == family,
            )
            .order_by(LearningRecord.created_at, LearningRecord.id)
        ).all()
        records = []
        knowledge_rows: list = []
        for record, subject in rows:
            knowledge = db.scalars(
                select(KnowledgeItem)
                .join(
                    KnowledgeOccurrence,
                    KnowledgeOccurrence.knowledge_item_id == KnowledgeItem.id,
                )
                .where(
                    KnowledgeOccurrence.learning_record_id == record.id,
                    KnowledgeOccurrence.family_id == family,
                    KnowledgeItem.family_id == family,
                    KnowledgeItem.child_id == child,
                )
                .order_by(KnowledgeItem.name, KnowledgeItem.id)
            ).all()
            knowledge_rows.extend(knowledge)
            records.append(
                {
                    "id": record.id,
                    "summary": record.summary,
                    "source": record.source,
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "subject_kind": subject.kind,
                    "knowledge": [_knowledge_view(entry) for entry in knowledge],
                }
            )
        media = db.scalars(
            select(SubmissionMedia)
            .where(
                SubmissionMedia.submission_id == sid,
            )
            .order_by(SubmissionMedia.sort_order, SubmissionMedia.created_at, SubmissionMedia.id)
        ).all()
        return {
            "submission_id": sid,
            "child_id": child,
            "state": item.state,
            "occurred_at": item.occurred_at.isoformat(),
            "created_at": item.created_at.isoformat(),
            "input_text": item.input_text,
            "source": item.source,
            "records": records,
            # `record` and `knowledge` describe the first subject and the union of all knowledge, so
            # readers written before multi-subject submissions keep working.
            "record": {key: value for key, value in records[0].items() if key != "knowledge"}
            if records
            else None,
            "knowledge": [_knowledge_view(entry) for entry in knowledge_rows],
            "media": [
                {
                    "id": m.id,
                    "index": i + 1,
                    "content_type": m.content_type,
                    "available": item.state != "cancelled",
                }
                for i, m in enumerate(media)
            ],
        }

    @classmethod
    def media(cls, db: Session, family: str, child: str, sid: str, mid: str) -> SubmissionMedia:
        submission = cls.submission(db, family, child, sid)
        media = db.scalar(
            select(SubmissionMedia).where(
                SubmissionMedia.id == mid,
                SubmissionMedia.submission_id == sid,
            )
        )
        if media is None:
            raise NotFoundError("没有找到这张照片")
        if submission.state == "cancelled":
            raise GoneError("原图已删除或不可用")
        if media.media_object_id:
            obj = db.scalar(
                select(MediaObject).where(
                    MediaObject.id == media.media_object_id,
                    MediaObject.family_id == family,
                    MediaObject.submission_id == sid,
                    MediaObject.state == "claimed",
                )
            )
            if obj is None or obj.storage_ref != media.path:
                raise GoneError("原图已删除或不可用")
        return media
