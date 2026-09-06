from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from push_kids.agent_processing.contracts import AnalysisProposal
from push_kids.agent_processing.presentation import DisplayGroup


class SubmissionCreate(BaseModel):
    child_id: str
    occurred_at: datetime
    input_text: str = Field(min_length=1, max_length=4000)
    source: str = Field(default="manual", max_length=30)


class PhotoDraftCreate(BaseModel):
    child_id: str
    occurred_at: datetime
    input_text: str | None = Field(default=None, max_length=4000)


class MediaUploadTicketRequest(BaseModel):
    submission_id: str
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    byte_size: int = Field(gt=0)


class MediaUploadTicket(BaseModel):
    ticket_id: str
    cloud_path: str
    expires_at: datetime


class MediaClaimRequest(BaseModel):
    ticket_id: str
    file_id: str = Field(min_length=12, max_length=700)


class SubmissionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    occurred_at: datetime
    input_text: str | None
    source: str
    state: str
    proposal: AnalysisProposal | None = None
    display_groups: list[DisplayGroup] = Field(default_factory=list, max_length=7)
    error_code: str | None
    error_message: str | None
    media_count: int = 0
    can_finalize_upload: bool = False
    awaiting_upload: bool = False
    upload_batch_key: str | None = None
    created_at: datetime
    updated_at: datetime


class ConfirmSubmission(BaseModel):
    manual_entry: bool = False
    subject_id: str | None = None
    proposal: AnalysisProposal


class ConfirmationResult(BaseModel):
    record_id: str
    subject_id: str
    knowledge_item_ids: list[str]
    review_item_ids: list[str]


class FeedbackRequest(BaseModel):
    action: Literal["complete", "reinforce", "partial", "defer"]
