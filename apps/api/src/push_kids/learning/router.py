from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, Request, UploadFile
from sqlalchemy.orm import Session

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
from push_kids.learning.service import LearningService
from push_kids.media.store import LocalMediaStore, WeChatCloudMediaStore
from push_kids.platform.context import RequestContext, family_id, request_context
from push_kids.platform.dependencies import get_db
from push_kids.platform.errors import ConflictError

router = APIRouter(tags=["learning"])


def _idempotency_header():
    return Header(
        alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
    )


@router.post("/submissions", response_model=SubmissionView, status_code=202)
def create_manual_submission(
    body: SubmissionCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ] = None,
):
    item = LearningService.create_manual(db, family, body, idempotency_key)
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, family, item.id)


@router.post("/submissions/photo-drafts", response_model=SubmissionView, status_code=202)
def create_photo_draft(
    body: PhotoDraftCreate,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[str | None, _idempotency_header()] = None,
):
    item = LearningService.create_photo_draft(db, family, body, idempotency_key)
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, family, item.id)


@router.post("/media/upload-tickets", response_model=MediaUploadTicket, status_code=201)
def create_media_upload_ticket(
    body: MediaUploadTicketRequest,
    request: Request,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
    idempotency_key: Annotated[str, _idempotency_header()],
):
    settings = request.app.state.settings
    return LearningService.issue_media_ticket(
        db,
        context,
        body,
        idempotency_key,
        settings.upload_max_bytes,
        settings.media_ticket_ttl_seconds,
    )


@router.post("/media/claims", response_model=SubmissionView)
def claim_media(
    body: MediaClaimRequest,
    request: Request,
    context: Annotated[RequestContext, Depends(request_context)],
    db: Annotated[Session, Depends(get_db)],
):
    store = request.app.state.media_store
    if not isinstance(store, WeChatCloudMediaStore):
        raise ValueError("云存储上传仅在微信云环境可用")
    item = LearningService.claim_media(db, store, context, body)
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, context.family_id, item.id)


@router.post("/submissions/upload", response_model=SubmissionView, status_code=202)
async def create_photo_submission(
    request: Request,
    child_id: Annotated[str, Form()],
    occurred_at: Annotated[datetime, Form()],
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    files: Annotated[list[UploadFile], File()],
    input_text: Annotated[str | None, Form()] = None,
    defer_analysis: Annotated[bool, Form()] = False,
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"
        ),
    ] = None,
):
    if request.app.state.settings.is_cloud:
        raise ConflictError("云环境请使用对象存储直传")
    media_store = LocalMediaStore(
        request.app.state.settings.media_root, request.app.state.settings.upload_max_bytes
    )
    item = await LearningService.create_upload(
        db,
        media_store,
        family,
        child_id,
        occurred_at,
        input_text,
        files,
        idempotency_key,
        enqueue=not defer_analysis,
    )
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, family, item.id)


@router.post("/submissions/{submission_id}/media", response_model=SubmissionView)
async def append_submission_media(
    submission_id: str,
    request: Request,
    file: Annotated[UploadFile, File()],
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    if request.app.state.settings.is_cloud:
        raise ConflictError("云环境请使用对象存储直传")
    media_store = LocalMediaStore(
        request.app.state.settings.media_root, request.app.state.settings.upload_max_bytes
    )
    item = await LearningService.append_media(db, media_store, family, submission_id, file)
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, family, item.id)


@router.post("/submissions/{submission_id}/finalize", response_model=SubmissionView)
def finalize_submission(
    submission_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    item = LearningService.finalize_upload(db, family, submission_id)
    if item.id is None:
        raise RuntimeError("submission id was not generated")
    return LearningService.get_view(db, family, item.id)


@router.get("/submissions", response_model=list[SubmissionView])
def list_submissions(
    child_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
    state: str | None = None,
):
    return LearningService.list_views(db, family, child_id, state)


@router.get("/submissions/{submission_id}", response_model=SubmissionView)
def get_submission(
    submission_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return LearningService.get_view(db, family, submission_id)


@router.post("/submissions/{submission_id}/confirm", response_model=ConfirmationResult)
def confirm_submission(
    submission_id: str,
    body: ConfirmSubmission,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return LearningService.confirm(db, family, submission_id, body)


@router.post("/submissions/{submission_id}/retry", response_model=SubmissionView)
def retry_submission(
    submission_id: str,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return LearningService.retry(db, family, submission_id)


@router.post("/submissions/{submission_id}/cancel", response_model=SubmissionView)
def cancel_submission(
    submission_id: str,
    request: Request,
    family: Annotated[str, Depends(family_id)],
    db: Annotated[Session, Depends(get_db)],
):
    return LearningService.cancel(db, request.app.state.media_store, family, submission_id)
