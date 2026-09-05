from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from push_kids.agent_processing.contracts import (
    MATERIAL_FINGERPRINT_KEY,
    AnalysisProposal,
    unique_knowledge_points,
)
from push_kids.children.service import ChildrenService
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.learning.schemas import (
    ConfirmationResult,
    ConfirmSubmission,
    MediaClaimRequest,
    MediaUploadTicket,
    MediaUploadTicketRequest,
    PhotoDraftCreate,
    SubmissionCreate,
    SubmissionView,
)
from push_kids.media.store import (
    ALLOWED_IMAGE_TYPES,
    LocalMediaStore,
    MediaStore,
    WeChatCloudMediaStore,
)
from push_kids.persistence.models import (
    AgentJob,
    Child,
    JobState,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    MediaObject,
    MediaState,
    ReviewFeedback,
    ReviewItem,
    Subject,
    SubmissionMedia,
    SubmissionRequest,
    SubmissionState,
)
from push_kids.planning.domain import apply_feedback, initial_review_date
from push_kids.platform.context import RequestContext
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.time import local_date, utcnow


class LearningService:
    @staticmethod
    def _request_fingerprint(
        *,
        child_id: str,
        occurred_at: datetime,
        input_text: str | None,
        source: str,
        media_digests: list[str] | None = None,
    ) -> str:
        canonical = json.dumps(
            {
                "child_id": child_id,
                "occurred_at": occurred_at.astimezone(UTC).isoformat(),
                "input_text": input_text or None,
                "source": source,
                "media_digests": media_digests or [],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(canonical.encode()).hexdigest()

    @classmethod
    def _idempotent_submission(
        cls,
        db: Session,
        family_id: str,
        idempotency_key: str | None,
        fingerprint: str,
    ) -> LearningSubmission | None:
        if not idempotency_key:
            return None
        request = db.scalar(
            select(SubmissionRequest).where(
                SubmissionRequest.family_id == family_id,
                SubmissionRequest.idempotency_key == idempotency_key,
            )
        )
        if request is None:
            return None
        if request.request_fingerprint != fingerprint:
            raise ConflictError("此提交标识已用于不同内容，请重新提交")
        if request.submission_id is None:
            raise RuntimeError("idempotency record has no submission id")
        return cls._submission(db, family_id, request.submission_id)

    @staticmethod
    def _add_idempotency_record(
        db: Session,
        family_id: str,
        idempotency_key: str | None,
        fingerprint: str,
        submission_id: str,
    ) -> None:
        if idempotency_key:
            db.add(
                SubmissionRequest(
                    family_id=family_id,
                    idempotency_key=idempotency_key,
                    request_fingerprint=fingerprint,
                    submission_id=submission_id,
                )
            )

    @staticmethod
    def _submission(
        db: Session,
        family_id: str,
        submission_id: str,
        *,
        for_update: bool = False,
    ) -> LearningSubmission:
        query = select(LearningSubmission).where(
            LearningSubmission.id == submission_id, LearningSubmission.family_id == family_id
        )
        if for_update:
            query = query.with_for_update().execution_options(populate_existing=True)
        item = db.scalar(query)
        if item is None:
            raise NotFoundError("没有找到这条学习记录")
        return item

    @classmethod
    def create_manual(
        cls,
        db: Session,
        family_id: str,
        data: SubmissionCreate,
        idempotency_key: str | None = None,
    ) -> LearningSubmission:
        ChildrenService.get_child(db, family_id, data.child_id)
        fingerprint = cls._request_fingerprint(
            child_id=data.child_id,
            occurred_at=data.occurred_at,
            input_text=data.input_text,
            source=data.source,
        )
        existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
        if existing is not None:
            return existing
        submission = LearningSubmission(family_id=family_id, **data.model_dump())
        db.add(submission)
        db.flush()
        if submission.id is None:
            raise RuntimeError("submission id was not generated")
        db.add(AgentJob(family_id=family_id, submission_id=submission.id))
        cls._add_idempotency_record(db, family_id, idempotency_key, fingerprint, submission.id)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
            if existing is None:
                raise
            return existing
        return submission

    @classmethod
    def create_photo_draft(
        cls,
        db: Session,
        family_id: str,
        data: PhotoDraftCreate,
        idempotency_key: str | None,
    ) -> LearningSubmission:
        ChildrenService.get_child(db, family_id, data.child_id)
        fingerprint = cls._request_fingerprint(
            child_id=data.child_id,
            occurred_at=data.occurred_at,
            input_text=data.input_text,
            source="photo",
        )
        existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
        if existing is not None:
            return existing
        submission = LearningSubmission(
            family_id=family_id,
            child_id=data.child_id,
            occurred_at=data.occurred_at,
            input_text=data.input_text or None,
            source="photo",
        )
        db.add(submission)
        db.flush()
        if submission.id is None:
            raise RuntimeError("submission id was not generated")
        cls._add_idempotency_record(db, family_id, idempotency_key, fingerprint, submission.id)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
            if existing is None:
                raise
            return existing
        return submission

    @classmethod
    def issue_media_ticket(
        cls,
        db: Session,
        context: RequestContext,
        data: MediaUploadTicketRequest,
        idempotency_key: str,
        max_bytes: int,
        ttl_seconds: int,
    ) -> MediaUploadTicket:
        if not context.subject_hmac or not context.openid:
            raise ConflictError("云存储上传只能在微信云环境使用")
        submission = cls._submission(db, context.family_id, data.submission_id, for_update=True)
        if submission.source != "photo" or submission.state != SubmissionState.queued.value:
            raise ConflictError("当前记录不能继续添加照片")
        if db.scalar(select(AgentJob.id).where(AgentJob.submission_id == submission.id)):
            raise ConflictError("当前记录已经进入分析队列")
        if data.byte_size > max_bytes:
            raise ValueError(f"单张图片需小于 {max_bytes // 1024 // 1024}MB")
        existing = db.scalar(
            select(MediaObject).where(
                MediaObject.family_id == context.family_id,
                MediaObject.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if existing.submission_id != submission.id:
                raise ConflictError("此上传标识已用于其他记录")
            if existing.uploader_subject_hmac != context.subject_hmac:
                raise NotFoundError("没有找到上传凭据")
            if not existing.id or not existing.storage_path or not existing.expires_at:
                raise RuntimeError("上传凭据数据不完整")
            existing_expiry = existing.expires_at
            if existing_expiry.tzinfo is None:
                existing_expiry = existing_expiry.replace(tzinfo=UTC)
            if existing.state != MediaState.claimed.value and existing_expiry <= utcnow():
                existing.state = MediaState.ticketed.value
                existing.storage_ref = None
                existing.content_type = None
                existing.byte_size = None
                existing.sha256 = None
                existing.expires_at = utcnow() + timedelta(seconds=ttl_seconds)
                db.commit()
            return MediaUploadTicket(
                ticket_id=existing.id,
                cloud_path=existing.storage_path,
                expires_at=existing.expires_at,
            )
        claimed_count = (
            db.scalar(
                select(func.count(SubmissionMedia.id)).where(
                    SubmissionMedia.submission_id == submission.id
                )
            )
            or 0
        )
        pending_count = (
            db.scalar(
                select(func.count(MediaObject.id)).where(
                    MediaObject.submission_id == submission.id,
                    MediaObject.state == MediaState.ticketed.value,
                    MediaObject.expires_at > utcnow(),
                )
            )
            or 0
        )
        if claimed_count + pending_count >= 9:
            raise ValueError("一条学习记录最多 9 张图片")
        ticket_id = str(uuid.uuid4())
        family_hash = hashlib.sha256(context.family_id.encode()).hexdigest()[:16]
        suffix = ALLOWED_IMAGE_TYPES[data.content_type]
        cloud_path = f"staging/{family_hash}/{submission.id}/{ticket_id}{suffix}"
        expires_at = utcnow() + timedelta(seconds=ttl_seconds)
        ticket = MediaObject(
            id=ticket_id,
            family_id=context.family_id,
            submission_id=submission.id,
            storage_path=cloud_path,
            uploader_subject_hmac=context.subject_hmac,
            idempotency_key=idempotency_key,
            expires_at=expires_at,
        )
        db.add(ticket)
        db.commit()
        return MediaUploadTicket(ticket_id=ticket_id, cloud_path=cloud_path, expires_at=expires_at)

    @classmethod
    def claim_media(
        cls,
        db: Session,
        store: WeChatCloudMediaStore,
        context: RequestContext,
        data: MediaClaimRequest,
    ) -> LearningSubmission:
        if not context.subject_hmac or not context.openid:
            raise ConflictError("云存储上传只能在微信云环境使用")
        ticket = db.scalar(
            select(MediaObject).where(
                MediaObject.id == data.ticket_id,
                MediaObject.family_id == context.family_id,
            )
        )
        if ticket is None:
            raise NotFoundError("没有找到上传凭据")
        if not ticket.submission_id or not ticket.storage_path or not ticket.expires_at:
            raise RuntimeError("上传凭据数据不完整")
        if ticket.uploader_subject_hmac != context.subject_hmac:
            raise NotFoundError("没有找到上传凭据")
        if ticket.state == MediaState.claimed.value:
            if ticket.storage_ref != data.file_id:
                raise ConflictError("上传凭据已经用于其他文件")
            return cls._submission(db, context.family_id, ticket.submission_id)
        initial_expiry = ticket.expires_at
        if initial_expiry.tzinfo is None:
            initial_expiry = initial_expiry.replace(tzinfo=UTC)
        if ticket.state != MediaState.ticketed.value or initial_expiry <= utcnow():
            raise ConflictError("上传凭据已失效，请重新上传")
        claimed = store.claim(data.file_id, ticket.storage_path, context.openid)

        submission = cls._submission(db, context.family_id, ticket.submission_id, for_update=True)
        ticket = db.scalar(
            select(MediaObject)
            .where(
                MediaObject.id == data.ticket_id,
                MediaObject.family_id == context.family_id,
            )
            .with_for_update()
        )
        if ticket is None:
            raise NotFoundError("没有找到上传凭据")
        if not ticket.expires_at:
            raise RuntimeError("上传凭据数据不完整")
        if ticket.uploader_subject_hmac != context.subject_hmac:
            raise NotFoundError("没有找到上传凭据")
        if ticket.state == MediaState.claimed.value:
            if ticket.storage_ref != data.file_id:
                raise ConflictError("上传凭据已经用于其他文件")
            return submission
        expires_at = ticket.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if ticket.state != MediaState.ticketed.value or expires_at <= utcnow():
            raise ConflictError("上传凭据已失效，请重新上传")
        if submission.state != SubmissionState.queued.value:
            raise ConflictError("当前记录不能继续添加照片")
        if db.scalar(select(AgentJob.id).where(AgentJob.submission_id == submission.id)):
            raise ConflictError("当前记录已经进入分析队列")
        count = (
            db.scalar(
                select(func.count(SubmissionMedia.id)).where(
                    SubmissionMedia.submission_id == submission.id
                )
            )
            or 0
        )
        if count >= 9:
            raise ValueError("一条学习记录最多 9 张图片")
        ticket.storage_ref = claimed.storage_ref
        ticket.content_type = claimed.content_type
        ticket.byte_size = claimed.byte_size
        ticket.sha256 = claimed.sha256
        ticket.state = MediaState.claimed.value
        ticket.claimed_at = utcnow()
        db.add(
            SubmissionMedia(
                submission_id=submission.id,
                media_object_id=ticket.id,
                path=claimed.storage_ref,
                content_type=claimed.content_type,
                byte_size=claimed.byte_size,
            )
        )
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError("该文件已经被使用") from exc
        return submission

    @classmethod
    async def create_upload(
        cls,
        db: Session,
        media_store: LocalMediaStore,
        family_id: str,
        child_id: str,
        occurred_at: datetime,
        input_text: str | None,
        files: list[UploadFile],
        idempotency_key: str | None = None,
        enqueue: bool = True,
    ) -> LearningSubmission:
        ChildrenService.get_child(db, family_id, child_id)
        if not files:
            raise ValueError("请至少上传一张图片")
        if len(files) > 9:
            raise ValueError("一次最多上传 9 张图片")
        media_digests: list[str] = []
        for upload in files:
            content = await upload.read(media_store.max_bytes + 1)
            await upload.seek(0)
            media_digests.append(
                f"{upload.content_type or ''}:{upload.filename or ''}:{sha256(content).hexdigest()}"
            )
        fingerprint = cls._request_fingerprint(
            child_id=child_id,
            occurred_at=occurred_at,
            input_text=input_text,
            source="photo",
            media_digests=media_digests,
        )
        existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
        if existing is not None:
            return existing
        submission = LearningSubmission(
            family_id=family_id,
            child_id=child_id,
            occurred_at=occurred_at,
            input_text=input_text or None,
            source="photo",
        )
        db.add(submission)
        db.flush()
        if submission.id is None:
            raise RuntimeError("submission id was not generated")
        stored_paths: list[Path] = []
        try:
            for upload in files:
                stored = await media_store.save(family_id, submission.id, upload)
                stored_paths.append(Path(stored.path))
                db.add(
                    SubmissionMedia(
                        submission_id=submission.id,
                        path=stored.path,
                        content_type=stored.content_type,
                        byte_size=stored.byte_size,
                    )
                )
            if enqueue:
                db.add(AgentJob(family_id=family_id, submission_id=submission.id))
            cls._add_idempotency_record(db, family_id, idempotency_key, fingerprint, submission.id)
            db.commit()
        except IntegrityError:
            db.rollback()
            for path in stored_paths:
                path.unlink(missing_ok=True)
            existing = cls._idempotent_submission(db, family_id, idempotency_key, fingerprint)
            if existing is None:
                raise
            return existing
        except Exception:
            db.rollback()
            for path in stored_paths:
                path.unlink(missing_ok=True)
            raise
        return submission

    @classmethod
    async def append_media(
        cls,
        db: Session,
        media_store: LocalMediaStore,
        family_id: str,
        submission_id: str,
        upload: UploadFile,
    ) -> LearningSubmission:
        submission = cls._submission(db, family_id, submission_id)
        if submission.state != SubmissionState.queued.value:
            raise ConflictError("当前记录已经开始分析，不能继续添加照片")
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == submission.id))
        if job is not None:
            raise ConflictError("当前记录已经进入分析队列")
        count = (
            db.scalar(
                select(func.count(SubmissionMedia.id)).where(
                    SubmissionMedia.submission_id == submission.id
                )
            )
            or 0
        )
        if count >= 9:
            raise ValueError("一条学习记录最多 9 张图片")
        if submission.id is None:
            raise RuntimeError("submission id was not generated")
        stored = await media_store.save(family_id, submission.id, upload)
        try:
            db.add(
                SubmissionMedia(
                    submission_id=submission.id,
                    path=stored.path,
                    content_type=stored.content_type,
                    byte_size=stored.byte_size,
                )
            )
            db.commit()
        except Exception:
            db.rollback()
            Path(stored.path).unlink(missing_ok=True)
            raise
        return submission

    @classmethod
    def finalize_upload(cls, db: Session, family_id: str, submission_id: str) -> LearningSubmission:
        submission = cls._submission(db, family_id, submission_id, for_update=True)
        if submission.state != SubmissionState.queued.value:
            raise ConflictError("当前记录不能再次提交分析")
        media_count = (
            db.scalar(
                select(func.count(SubmissionMedia.id)).where(
                    SubmissionMedia.submission_id == submission.id
                )
            )
            or 0
        )
        if not media_count:
            raise ValueError("请至少上传一张图片")
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == submission.id))
        if job is None:
            db.add(AgentJob(family_id=family_id, submission_id=submission.id))
            db.commit()
        return submission

    @classmethod
    def get_view(cls, db: Session, family_id: str, submission_id: str) -> SubmissionView:
        submission = cls._submission(db, family_id, submission_id)
        media_count = (
            db.scalar(
                select(func.count(SubmissionMedia.id)).where(
                    SubmissionMedia.submission_id == submission.id
                )
            )
            or 0
        )
        proposal = (
            AnalysisProposal.model_validate(json.loads(submission.proposal_json))
            if submission.proposal_json
            else None
        )
        job_count = (
            db.scalar(
                select(func.count(AgentJob.id)).where(AgentJob.submission_id == submission.id)
            )
            or 0
        )
        awaiting_upload = bool(
            submission.source == "photo"
            and submission.state == SubmissionState.queued.value
            and not job_count
        )
        upload_batch_key = (
            db.scalar(
                select(SubmissionRequest.idempotency_key).where(
                    SubmissionRequest.family_id == family_id,
                    SubmissionRequest.submission_id == submission.id,
                )
            )
            if awaiting_upload
            else None
        )
        return SubmissionView(
            id=submission.id,
            child_id=submission.child_id,
            occurred_at=submission.occurred_at,
            input_text=submission.input_text,
            source=submission.source,
            state=submission.state,
            proposal=proposal,
            error_code=submission.error_code,
            error_message=submission.error_message,
            media_count=media_count,
            awaiting_upload=awaiting_upload,
            upload_batch_key=upload_batch_key,
            can_finalize_upload=bool(
                submission.source == "photo"
                and submission.state == SubmissionState.queued.value
                and media_count
                and not job_count
            ),
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )

    @classmethod
    def list_views(
        cls,
        db: Session,
        family_id: str,
        child_id: str,
        state: str | None = None,
        pending_only: bool = False,
        offset: int = 0,
    ) -> list[SubmissionView]:
        ChildrenService.get_child(db, family_id, child_id)
        query = select(LearningSubmission.id).where(
            LearningSubmission.family_id == family_id, LearningSubmission.child_id == child_id
        )
        if state:
            query = query.where(LearningSubmission.state == state)
        if pending_only:
            query = query.where(
                LearningSubmission.state.in_(
                    [
                        SubmissionState.queued.value,
                        SubmissionState.analyzing.value,
                        SubmissionState.pending_confirmation.value,
                        SubmissionState.failed.value,
                    ]
                )
            )
        ids = db.scalars(
            query.order_by(LearningSubmission.created_at.desc(), LearningSubmission.id.desc())
            .offset(offset)
            .limit(100)
        )
        return [cls.get_view(db, family_id, item_id) for item_id in ids if item_id is not None]

    @classmethod
    def cancel(
        cls,
        db: Session,
        media_store: MediaStore,
        family_id: str,
        submission_id: str,
    ) -> SubmissionView:
        job = db.scalar(
            select(AgentJob).where(AgentJob.submission_id == submission_id).with_for_update()
        )
        submission = cls._submission(db, family_id, submission_id, for_update=True)
        if submission.state == SubmissionState.confirmed.value:
            raise ConflictError("当前状态不能取消")
        submission.state = SubmissionState.cancelled.value
        submission.proposal_json = None
        submission.error_code = None
        submission.error_message = None
        if job:
            job.state = JobState.cancelled.value
        db.commit()
        media_objects = list(
            db.scalars(
                select(MediaObject).where(
                    MediaObject.submission_id == submission.id,
                    MediaObject.family_id == family_id,
                    MediaObject.state.in_([MediaState.ticketed.value, MediaState.claimed.value]),
                )
            )
        )
        for media_object in media_objects:
            storage_ref = media_object.storage_ref or media_object.storage_path
            if not storage_ref:
                continue
            try:
                media_store.delete(storage_ref)
            except Exception:
                continue
            media_object.state = MediaState.deleted.value
        db.commit()
        return cls.get_view(db, family_id, submission_id)

    @classmethod
    def retry(cls, db: Session, family_id: str, submission_id: str) -> SubmissionView:
        submission = cls._submission(db, family_id, submission_id)
        if submission.state != SubmissionState.failed.value:
            raise ConflictError("只有失败的分析可以重试")
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == submission.id))
        if job is None:
            job = AgentJob(family_id=family_id, submission_id=submission.id)
            db.add(job)
        else:
            job.state = JobState.queued.value
            job.attempts = 0
            job.available_at = utcnow()
            job.error_message = None
        submission.state = SubmissionState.queued.value
        submission.error_code = None
        submission.error_message = None
        db.commit()
        return cls.get_view(db, family_id, submission_id)

    @classmethod
    def confirm(
        cls, db: Session, family_id: str, submission_id: str, data: ConfirmSubmission
    ) -> ConfirmationResult:
        job = db.scalar(
            select(AgentJob)
            .where(
                AgentJob.submission_id == submission_id,
                AgentJob.family_id == family_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        submission = cls._submission(db, family_id, submission_id, for_update=True)
        allowed = {SubmissionState.pending_confirmation.value}
        if data.manual_entry:
            allowed.update(
                {
                    SubmissionState.queued.value,
                    SubmissionState.analyzing.value,
                    SubmissionState.failed.value,
                }
            )
            if data.proposal.todo_matches:
                raise ValueError("人工录入不能自动标记Todo，请通过Todo反馈入口操作")
        if submission.state not in allowed:
            raise ConflictError("只有待确认的草稿可以确认")
        # Serialize knowledge creation by child as well as confirmation by submission.
        db.scalar(
            select(Child)
            .where(Child.id == submission.child_id, Child.family_id == family_id)
            .with_for_update()
        )
        stored_proposal = json.loads(submission.proposal_json or "{}")
        original_matches = {
            item["review_id"]: item for item in stored_proposal.get("todo_matches", [])
        }
        data.proposal.knowledge_points = unique_knowledge_points(data.proposal.knowledge_points)
        if data.subject_id:
            subject = db.scalar(
                select(Subject).where(
                    Subject.id == data.subject_id,
                    Subject.family_id == family_id,
                    Subject.child_id == submission.child_id,
                )
            )
            if subject is None:
                raise NotFoundError("没有找到所选科目")
        else:
            subject = db.scalar(
                select(Subject).where(
                    Subject.family_id == family_id,
                    Subject.child_id == submission.child_id,
                    Subject.name == data.proposal.subject_name,
                )
            )
            if subject is None:
                if data.proposal.subject_kind != "learning":
                    raise ValueError("活动请通过活动记录入口保存，不加入复习计划")
                subject = Subject(
                    family_id=family_id,
                    child_id=submission.child_id,
                    name=data.proposal.subject_name,
                    kind=data.proposal.subject_kind,
                )
                db.add(subject)
                db.flush()
        if subject.kind != "learning":
            raise ValueError("活动请通过活动记录入口保存，不加入复习计划")
        record = LearningRecord(
            family_id=family_id,
            child_id=submission.child_id,
            subject_id=subject.id,
            submission_id=submission.id,
            occurred_at=submission.occurred_at,
            summary=data.proposal.summary,
            source="人工录入" if data.manual_entry else data.proposal.source,
        )
        db.add(record)
        db.flush()
        knowledge_ids: list[str] = []
        review_ids: list[str] = []
        for point in data.proposal.knowledge_points:
            normalized = normalize_knowledge_name(point.name)
            if not normalized:
                continue
            knowledge_query = select(KnowledgeItem).where(
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == submission.child_id,
                KnowledgeItem.subject_id == subject.id,
                KnowledgeItem.normalized_name == normalized,
                KnowledgeItem.category == point.category,
            )
            if point.existing_knowledge_id:
                knowledge_query = knowledge_query.where(
                    KnowledgeItem.id == point.existing_knowledge_id
                )
            knowledge = db.scalar(knowledge_query)
            if point.existing_knowledge_id and knowledge is None:
                raise ValueError("关联知识点与所选科目或编辑内容不一致，请取消关联后重试")
            if knowledge is None:
                knowledge = KnowledgeItem(
                    family_id=family_id,
                    child_id=submission.child_id,
                    subject_id=subject.id,
                    name=point.name,
                    normalized_name=normalized,
                    category=point.category,
                    review_method=point.review_method,
                    estimated_minutes=point.estimated_minutes,
                )
                db.add(knowledge)
                db.flush()
            db.add(
                KnowledgeOccurrence(
                    family_id=family_id,
                    knowledge_item_id=knowledge.id,
                    learning_record_id=record.id,
                    occurred_at=submission.occurred_at,
                )
            )
            due = initial_review_date(local_date(submission.occurred_at), local_date())
            review = db.scalar(
                select(ReviewItem)
                .where(ReviewItem.knowledge_item_id == knowledge.id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if review is None:
                review = ReviewItem(
                    family_id=family_id,
                    child_id=submission.child_id,
                    knowledge_item_id=knowledge.id,
                    due_date=due,
                )
                db.add(review)
                db.flush()
            if knowledge.id is None or review.id is None:
                raise RuntimeError("confirmed entities have no generated id")
            knowledge_ids.append(knowledge.id)
            review_ids.append(review.id)
        if not knowledge_ids:
            raise ValueError("至少需要保留一个有效知识点")
        unique_matches = {item.review_id: item for item in data.proposal.todo_matches}
        data.proposal.todo_matches = []
        for match in unique_matches.values():
            matched_review = db.scalar(
                select(ReviewItem)
                .join(KnowledgeItem, ReviewItem.knowledge_item_id == KnowledgeItem.id)
                .join(Subject, KnowledgeItem.subject_id == Subject.id)
                .where(
                    ReviewItem.id == match.review_id,
                    ReviewItem.family_id == family_id,
                    ReviewItem.child_id == submission.child_id,
                    ReviewItem.active.is_(True),
                    Subject.kind == "learning",
                )
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if matched_review is None or matched_review.due_date is None:
                continue
            snapshot = original_matches.get(match.review_id)
            if snapshot is None:
                # Confirmation may remove matches, never add unobserved automatic feedback.
                continue
            if snapshot.get("step") is not None and (
                snapshot["step"] != matched_review.step
                or snapshot.get("due_date") != matched_review.due_date.isoformat()
            ):
                continue
            transition = apply_feedback(matched_review.step or 0, "complete", local_date())
            matched_review.step = transition.step
            matched_review.due_date = transition.due_date
            matched_review.active = transition.active
            matched_review.last_feedback = "complete"
            db.add(
                ReviewFeedback(
                    family_id=family_id,
                    review_item_id=matched_review.id,
                    action="complete",
                )
            )
            data.proposal.todo_matches.append(match)
        if data.manual_entry:
            data.proposal.source = "人工录入"
            if job and job.state in {
                JobState.queued.value,
                JobState.running.value,
                JobState.failed.value,
            }:
                job.state = JobState.cancelled.value
        stored = data.proposal.model_dump()
        if MATERIAL_FINGERPRINT_KEY in stored_proposal:
            stored[MATERIAL_FINGERPRINT_KEY] = stored_proposal[MATERIAL_FINGERPRINT_KEY]
        submission.proposal_json = json.dumps(stored, ensure_ascii=False)
        submission.state = SubmissionState.confirmed.value
        submission.error_code = None
        submission.error_message = None
        submission.confirmed_at = utcnow()
        db.commit()
        return ConfirmationResult(
            record_id=record.id,
            subject_id=subject.id,
            knowledge_item_ids=knowledge_ids,
            review_item_ids=review_ids,
        )
