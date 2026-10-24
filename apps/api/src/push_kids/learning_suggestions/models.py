"""Suggestion-owned state. Child locks enforce single current job/proposal/task."""

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from push_kids.persistence.models import Base, new_id
from push_kids.persistence.types import UTCDateTime
from push_kids.platform.time import utcnow


class SuggestionState(Base):
    __tablename__ = "learning_suggestion_states"
    family_id = Column(String(80), primary_key=True)
    child_id = Column(String(36), ForeignKey("children.id"), primary_key=True)
    version = Column(Integer, nullable=False, default=0)
    current_suggestion_id = Column(String(36))
    pending_task_id = Column(String(36))
    active_job_id = Column(String(36))


class Suggestion(Base):
    __tablename__ = "learning_suggestions"
    __table_args__ = (
        Index("ix_suggestions_history", "family_id", "child_id", "created_at", "id"),
        Index("ix_suggestions_cleanup", "expires_at", "id"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    version = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="proposed")
    subject_id = Column(String(36), nullable=False)
    validated_content_json = Column(Text, nullable=False)
    input_fingerprint = Column(String(64), nullable=False)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    expires_at = Column(UTCDateTime(), nullable=False)
    approved_by = Column(String(80))
    approved_at = Column(UTCDateTime())


class PromptDay(Base):
    __tablename__ = "learning_suggestion_prompt_days"
    __table_args__ = (Index("ix_suggestion_prompt_cleanup", "prompt_on", "family_id", "child_id"),)
    family_id = Column(String(80), primary_key=True)
    child_id = Column(String(36), ForeignKey("children.id"), primary_key=True)
    prompt_on = Column(Date, primary_key=True)
    consumed_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    consumed_by = Column(String(80), nullable=False)
    request_id = Column(String(100), nullable=False)
    displayed_at = Column(UTCDateTime())


class SuggestionJob(Base):
    __tablename__ = "learning_suggestion_jobs"
    __table_args__ = (
        UniqueConstraint("family_id", "child_id", "request_id", name="uq_suggestion_job_request"),
        Index("ix_suggestion_job_scope", "family_id", "child_id", "state", "created_at", "id"),
        Index("ix_suggestion_job_family", "family_id", "state", "id"),
        Index("ix_suggestion_job_claim", "state", "available_at", "id"),
        Index("ix_suggestion_job_quota", "family_id", "child_id", "updated_at", "id"),
        Index("ix_suggestion_job_cleanup", "updated_at", "id"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    request_id = Column(String(100), nullable=False)
    state = Column(String(20), nullable=False, default="queued")
    attempts = Column(Integer, nullable=False, default=0)
    available_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    lease_until = Column(UTCDateTime())
    lease_token = Column(String(36))
    input_revision = Column(Integer, nullable=False)
    input_fingerprint = Column(String(64), nullable=False)
    bounded_context_json = Column(Text, nullable=False)
    excluded_content_hash = Column(String(64))
    result_suggestion_id = Column(String(36))
    safe_error_code = Column(String(40))
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class StudyTask(Base):
    __tablename__ = "study_tasks"
    __table_args__ = (
        UniqueConstraint("family_id", "child_id", "suggestion_id", name="uq_study_task_suggestion"),
        Index("ix_study_task_scope", "family_id", "child_id", "state", "approved_at", "id"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    suggestion_id = Column(String(36), ForeignKey("learning_suggestions.id"), nullable=False)
    version = Column(Integer, nullable=False, default=0)
    state = Column(String(20), nullable=False, default="planned")
    approved_by = Column(String(80), nullable=False)
    approved_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    last_partial_at = Column(UTCDateTime())
    completed_at = Column(UTCDateTime())
    removed_at = Column(UTCDateTime())


class RecordIntent(Base):
    __tablename__ = "study_task_record_intents"
    __table_args__ = (
        UniqueConstraint("family_id", "child_id", "request_id", name="uq_study_intent_request"),
        Index("ix_study_intent_scope", "family_id", "child_id", "state", "created_at", "id"),
        Index("ix_study_intent_recovery", "state", "recovery_after", "id"),
        Index("ix_study_intent_cleanup", "state", "created_at", "id"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("study_tasks.id"), nullable=False)
    task_version = Column(Integer, nullable=False)
    mode = Column(String(10), nullable=False)
    created_by = Column(String(80), nullable=False)
    request_id = Column(String(100), nullable=False)
    submission_id = Column(String(36))
    state = Column(String(20), nullable=False, default="draft")
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    recovery_after = Column(UTCDateTime(), nullable=False, default=utcnow)


class StudyTaskRecord(Base):
    __tablename__ = "study_task_records"
    __table_args__ = (
        UniqueConstraint(
            "family_id", "child_id", "task_id", "record_id", name="uq_study_task_record"
        ),
        Index("ix_study_records_page", "family_id", "child_id", "task_id", "confirmed_at", "id"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("study_tasks.id"), nullable=False)
    record_id = Column(String(36), nullable=False)
    intent_id = Column(String(36), ForeignKey("study_task_record_intents.id"), nullable=False)
    confirmed_at = Column(UTCDateTime(), nullable=False)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
