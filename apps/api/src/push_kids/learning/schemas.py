from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from push_kids.agent_processing.contracts import AnalysisProposal
from push_kids.agent_processing.presentation import DisplayGroup


class SubjectGroupView(BaseModel):
    """How the draft splits across the child's configured subjects."""

    subject_id: str | None = None
    subject_name: str
    # False means the name is not in the child's catalogue yet and needs a parent decision.
    listed: bool
    knowledge_indexes: list[int] = Field(default_factory=list)
    knowledge_names: list[str] = Field(default_factory=list)


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
    # Deterministic split of the draft against the child's configured subjects.
    subject_groups: list[SubjectGroupView] = Field(default_factory=list, max_length=6)
    # True when the model merged several subjects, guessed a subject, or named an unlisted one.
    subject_review_needed: bool = False
    error_code: str | None
    error_message: str | None
    media_count: int = 0
    can_finalize_upload: bool = False
    awaiting_upload: bool = False
    upload_batch_key: str | None = None
    created_at: datetime
    updated_at: datetime


class ConfirmGroup(BaseModel):
    """One subject worth of a confirmation; a batch spanning subjects sends several."""

    subject_id: str | None = None
    subject_name: str = Field(min_length=1, max_length=40)
    # A parent must answer "add this subject?" before a name outside the catalogue is created.
    create_subject: bool = False
    # Defaults to the batch summary when the parent did not write a per-subject one.
    summary: str | None = Field(default=None, max_length=500)
    # Positions inside `ConfirmSubmission.proposal.knowledge_points` that belong to this subject.
    knowledge_indexes: list[int] = Field(min_length=1, max_length=20)


class ConfirmSubmission(BaseModel):
    manual_entry: bool = False
    subject_id: str | None = None
    create_subject: bool = False
    proposal: AnalysisProposal
    # When present this is authoritative for the records to create; `proposal` still carries the
    # batch-level Todo matches and source so older clients keep working unchanged.
    groups: list[ConfirmGroup] | None = Field(default=None, max_length=6)


class ConfirmedRecord(BaseModel):
    record_id: str
    subject_id: str
    subject_name: str
    knowledge_item_ids: list[str]
    review_item_ids: list[str]


class UpdatedReview(BaseModel):
    review_id: str
    step: int
    due_date: date
    active: bool


class ConfirmationResult(BaseModel):
    record_id: str | None = None
    subject_id: str | None = None
    knowledge_item_ids: list[str]
    review_item_ids: list[str]
    records: list[ConfirmedRecord] = Field(default_factory=list)
    updated_reviews: list[UpdatedReview] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    action: Literal["complete", "reinforce", "partial", "defer"]
