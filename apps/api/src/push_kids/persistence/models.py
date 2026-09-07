import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

from push_kids.persistence.types import UTCDateTime
from push_kids.platform.time import utcnow

Base = declarative_base()


def new_id() -> str:
    return str(uuid.uuid4())


class SubjectKind(enum.StrEnum):
    learning = "learning"
    activity = "activity"


class SubmissionState(enum.StrEnum):
    queued = "queued"
    analyzing = "analyzing"
    pending_confirmation = "pending_confirmation"
    failed = "failed"
    cancelled = "cancelled"
    confirmed = "confirmed"


class JobState(enum.StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class MediaState(enum.StrEnum):
    ticketed = "ticketed"
    claimed = "claimed"
    deleted = "deleted"


class FamilyStatus(enum.StrEnum):
    active = "active"
    deleting = "deleting"
    disabled = "disabled"


class MemberRole(enum.StrEnum):
    viewer = "viewer"
    editor = "editor"
    manager = "manager"


class MemberStatus(enum.StrEnum):
    active = "active"
    removed = "removed"
    disabled = "disabled"


class InviteStatus(enum.StrEnum):
    active = "active"
    exhausted = "exhausted"
    expired = "expired"
    revoked = "revoked"


class JoinRequestStatus(enum.StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
    expired = "expired"


class DeletionState(enum.StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class NotificationType(enum.StrEnum):
    member_application = "member_application"
    schedule_reminder = "schedule_reminder"
    review_digest = "review_digest"


class SubscriptionStatus(enum.StrEnum):
    unknown = "unknown"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"
    # Membership ended: the grant is unusable until the member joins and grants again.
    revoked = "revoked"


class DeliveryState(enum.StrEnum):
    pending = "pending"
    sending = "sending"
    sent = "sent"
    skipped = "skipped"
    failed = "failed"
    cancelled = "cancelled"


class WeChatActorBinding(Base):
    __tablename__ = "wechat_actor_bindings"
    __table_args__ = (UniqueConstraint("app_id", "subject_hmac", name="uq_wechat_actor_subject"),)
    id = Column(String(36), primary_key=True, default=new_id)
    app_id = Column(String(32), nullable=False)
    subject_hmac = Column(String(64), nullable=False)
    family_id = Column(String(80), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class Family(Base):
    __tablename__ = "families"
    id = Column(String(80), primary_key=True, default=new_id)
    display_name = Column(String(60), nullable=False)
    status = Column(String(20), nullable=False, default=FamilyStatus.active.value, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class FamilyMember(Base):
    __tablename__ = "family_members"
    __table_args__ = (
        UniqueConstraint("active_actor_binding_id", name="uq_family_member_active_actor"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    actor_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=False, index=True
    )
    # MySQL and SQLite both allow multiple NULL values in a unique key. Keeping the
    # active projection separate preserves removed membership history while enforcing
    # at most one active family for an actor at the database boundary.
    active_actor_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=True, index=True
    )
    role = Column(String(20), nullable=False, default=MemberRole.viewer.value, index=True)
    relationship_label = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default=MemberStatus.active.value, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    removed_at = Column(UTCDateTime(), nullable=True)


class FamilyInvite(Base):
    __tablename__ = "family_invites"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_family_invite_token"),
        UniqueConstraint("family_id", "idempotency_key", name="uq_family_invite_request"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False)
    idempotency_key = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default=InviteStatus.active.value, index=True)
    expires_at = Column(UTCDateTime(), nullable=False, index=True)
    created_by_member_id = Column(
        String(36), ForeignKey("family_members.id"), nullable=False, index=True
    )
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class FamilyJoinRequest(Base):
    __tablename__ = "family_join_requests"
    __table_args__ = (
        UniqueConstraint(
            "applicant_binding_id", "idempotency_key", name="uq_family_join_request_key"
        ),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    invite_id = Column(String(36), ForeignKey("family_invites.id"), nullable=False, index=True)
    applicant_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=False, index=True
    )
    idempotency_key = Column(String(100), nullable=False)
    relationship_label = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default=JoinRequestStatus.pending.value, index=True)
    decided_role = Column(String(20), nullable=True)
    decided_by_member_id = Column(String(36), ForeignKey("family_members.id"), nullable=True)
    decision_reason = Column(String(160), nullable=True)
    decision_idempotency_key = Column(String(100), nullable=True)
    decided_at = Column(UTCDateTime(), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class FamilyAuditEvent(Base):
    __tablename__ = "family_audit_events"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    actor_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=False, index=True
    )
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(40), nullable=False)
    resource_id = Column(String(36), nullable=True)
    outcome = Column(String(20), nullable=False, default="success")
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow, index=True)


class DeletionRequest(Base):
    __tablename__ = "deletion_requests"
    __table_args__ = (
        UniqueConstraint(
            "actor_binding_id", "idempotency_key_hash", name="uq_deletion_actor_request"
        ),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    actor_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=False, index=True
    )
    family_id = Column(String(80), nullable=True, index=True)
    target_type = Column(String(20), nullable=False, index=True)
    target_id = Column(String(80), nullable=True, index=True)
    idempotency_key_hash = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    state = Column(String(20), nullable=False, default=DeletionState.queued.value, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    available_at = Column(UTCDateTime(), nullable=False, default=utcnow, index=True)
    lease_until = Column(UTCDateTime(), nullable=True)
    error_code = Column(String(50), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    completed_at = Column(UTCDateTime(), nullable=True)
    expires_at = Column(UTCDateTime(), nullable=True, index=True)


class MediaObject(Base):
    __tablename__ = "media_objects"
    __table_args__ = (
        UniqueConstraint("storage_ref", name="uq_media_storage_ref"),
        UniqueConstraint("storage_path", name="uq_media_storage_path"),
        UniqueConstraint("family_id", "idempotency_key", name="uq_media_ticket_request"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    submission_id = Column(
        String(36), ForeignKey("learning_submissions.id"), nullable=False, index=True
    )
    backend = Column(String(30), nullable=False, default="wechat_cloud")
    storage_path = Column(String(500), nullable=False)
    storage_ref = Column(String(700), nullable=True)
    uploader_subject_hmac = Column(String(64), nullable=False)
    idempotency_key = Column(String(100), nullable=False)
    state = Column(String(20), nullable=False, default=MediaState.ticketed.value, index=True)
    content_type = Column(String(80), nullable=True)
    byte_size = Column(Integer, nullable=True)
    sha256 = Column(String(64), nullable=True)
    expires_at = Column(UTCDateTime(), nullable=False, index=True)
    claimed_at = Column(UTCDateTime(), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class Child(Base):
    __tablename__ = "children"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    name = Column(String(40), nullable=False)
    grade = Column(String(20), nullable=True)
    daily_budget_minutes = Column(Integer, nullable=False, default=15)
    # False archives the profile: it leaves the switcher and refuses new writes, while every
    # existing record, review item and report stays readable. There is no physical delete.
    active = Column(Boolean, nullable=False, default=True, index=True)
    # A durable deletion request freezes all new writes before the cross-store purge starts.
    deleting = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("family_id", "child_id", "name", name="uq_subject_name"),)
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String(40), nullable=False)
    kind = Column(String(20), nullable=False, default=SubjectKind.learning.value)
    color = Column(String(20), nullable=False, default="#39847A")
    active = Column(Boolean, nullable=False, default=True)
    # False marks the system preset catalog; True marks a parent- or proposal-created subject.
    is_custom = Column(Boolean, nullable=False, default=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class LearningSubmission(Base):
    __tablename__ = "learning_submissions"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    occurred_at = Column(UTCDateTime(), nullable=False)
    input_text = Column(Text, nullable=True)
    source = Column(String(30), nullable=False, default="manual")
    state = Column(String(30), nullable=False, default=SubmissionState.queued.value, index=True)
    proposal_json = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(String(300), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    confirmed_at = Column(UTCDateTime(), nullable=True)


class SubmissionMedia(Base):
    __tablename__ = "submission_media"
    id = Column(String(36), primary_key=True, default=new_id)
    submission_id = Column(
        String(36), ForeignKey("learning_submissions.id"), nullable=False, index=True
    )
    media_object_id = Column(String(36), ForeignKey("media_objects.id"), nullable=True, index=True)
    path = Column(String(700), nullable=False)
    content_type = Column(String(80), nullable=False)
    byte_size = Column(Integer, nullable=False)
    # Stable parent-visible photo position inside one submission, assigned on write.
    sort_order = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class AgentJob(Base):
    __tablename__ = "agent_jobs"
    __table_args__ = (UniqueConstraint("submission_id", name="uq_job_submission"),)
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    submission_id = Column(String(36), ForeignKey("learning_submissions.id"), nullable=False)
    state = Column(String(20), nullable=False, default=JobState.queued.value, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    available_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    lease_until = Column(UTCDateTime(), nullable=True)
    error_message = Column(String(300), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class SubmissionRequest(Base):
    """Maps a client retry key to exactly one learning submission."""

    __tablename__ = "submission_requests"
    __table_args__ = (
        UniqueConstraint("family_id", "idempotency_key", name="uq_submission_request_key"),
        UniqueConstraint("submission_id", name="uq_submission_request_submission"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    submission_id = Column(
        String(36), ForeignKey("learning_submissions.id"), nullable=False, index=True
    )
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    # Not unique: one photo batch can span several subjects and then holds one record per subject.
    submission_id = Column(
        String(36), ForeignKey("learning_submissions.id"), nullable=False, index=True
    )
    occurred_at = Column(UTCDateTime(), nullable=False, index=True)
    summary = Column(String(500), nullable=False)
    source = Column(String(30), nullable=False)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    __table_args__ = (
        UniqueConstraint(
            "family_id",
            "child_id",
            "subject_id",
            "normalized_name",
            "category",
            name="uq_knowledge_identity",
        ),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    normalized_name = Column(String(140), nullable=False)
    category = Column(String(50), nullable=False, default="知识点")
    review_method = Column(String(60), nullable=False, default="口头回顾")
    estimated_minutes = Column(Integer, nullable=False, default=3)
    # Machine recognition reliability of the extraction only; never a mastery judgement.
    confidence = Column(String(10), nullable=True)
    # Quoted material lines the extraction came from; never an evaluation of the child.
    evidence_json = Column(Text, nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class KnowledgeOccurrence(Base):
    __tablename__ = "knowledge_occurrences"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    knowledge_item_id = Column(
        String(36), ForeignKey("knowledge_items.id"), nullable=False, index=True
    )
    learning_record_id = Column(
        String(36), ForeignKey("learning_records.id"), nullable=False, index=True
    )
    occurred_at = Column(UTCDateTime(), nullable=False, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class ReviewItem(Base):
    __tablename__ = "review_items"
    __table_args__ = (UniqueConstraint("knowledge_item_id", name="uq_review_knowledge"),)
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    knowledge_item_id = Column(String(36), ForeignKey("knowledge_items.id"), nullable=False)
    # First confirmation that created this review item; NULL for unrecoverable history.
    source_submission_id = Column(
        String(36), ForeignKey("learning_submissions.id"), nullable=True, index=True
    )
    step = Column(Integer, nullable=False, default=0)
    due_date = Column(Date, nullable=False, index=True)
    last_feedback = Column(String(30), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class ReviewFeedback(Base):
    __tablename__ = "review_feedback"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    review_item_id = Column(String(36), ForeignKey("review_items.id"), nullable=False, index=True)
    action = Column(String(30), nullable=False)
    occurred_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class ReviewFeedbackRequest(Base):
    """Stores one parent feedback result so a network retry cannot advance twice."""

    __tablename__ = "review_feedback_requests"
    __table_args__ = (
        UniqueConstraint("family_id", "idempotency_key", name="uq_review_feedback_request_key"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False)
    review_item_id = Column(String(36), ForeignKey("review_items.id"), nullable=False, index=True)
    action = Column(String(30), nullable=False)
    result_step = Column(Integer, nullable=False)
    result_due_date = Column(Date, nullable=False)
    result_active = Column(Boolean, nullable=False)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class ActivitySchedule(Base):
    __tablename__ = "activity_schedules"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    weekdays = Column(String(30), nullable=False, default="")
    time_text = Column(String(20), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    target_per_week = Column(Integer, nullable=True)
    note = Column(String(200), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    event_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    kind = Column(String(20), nullable=False, default="other")
    repeat_weekly = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class CalendarEventRequest(Base):
    __tablename__ = "calendar_event_requests"
    __table_args__ = (
        UniqueConstraint("family_id", "idempotency_key", name="uq_calendar_event_request_key"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    event_id = Column(String(36), ForeignKey("calendar_events.id"), nullable=False, index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class TravelArrangement(Base):
    __tablename__ = "travel_arrangements"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String(30), nullable=False)
    weekdays = Column(String(30), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class TravelArrangementRequest(Base):
    __tablename__ = "travel_arrangement_requests"
    __table_args__ = (
        UniqueConstraint("family_id", "idempotency_key", name="uq_travel_request_key"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    idempotency_key = Column(String(100), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    arrangement_id = Column(
        String(36), ForeignKey("travel_arrangements.id"), nullable=False, index=True
    )
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class ActivityRecord(Base):
    __tablename__ = "activity_records"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    occurred_at = Column(UTCDateTime(), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    note = Column(String(300), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class NotificationPreference(Base):
    """One family member's own opt-in for one reminder type. Never a family-wide switch."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("member_id", "type", name="uq_notification_preference_member_type"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    member_id = Column(String(36), ForeignKey("family_members.id"), nullable=False, index=True)
    type = Column(String(30), nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class NotificationDestination(Base):
    """Encrypted external receiver identity. The plaintext OpenID is never stored or indexed.

    The row is keyed by family member so the scheduled dispatcher can route a queued message
    without reading membership tables that belong to the families domain.
    """

    __tablename__ = "notification_destinations"
    __table_args__ = (UniqueConstraint("member_id", name="uq_notification_destination_member"),)
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    member_id = Column(String(36), ForeignKey("family_members.id"), nullable=False, index=True)
    actor_binding_id = Column(
        String(36), ForeignKey("wechat_actor_bindings.id"), nullable=True, index=True
    )
    app_id = Column(String(32), nullable=False)
    key_version = Column(String(10), nullable=False, default="v1")
    ciphertext = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class NotificationSubscription(Base):
    """Latest WeChat one-off subscription grant per member and reminder type."""

    __tablename__ = "notification_subscriptions"
    __table_args__ = (
        UniqueConstraint("member_id", "type", name="uq_notification_subscription_member_type"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    member_id = Column(String(36), ForeignKey("family_members.id"), nullable=False, index=True)
    type = Column(String(30), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=SubscriptionStatus.unknown.value)
    # One accepted WeChat one-off subscription authorises exactly one message, so the balance
    # is a real spend counter, not a boolean. Long-term templates set it to -1 (unlimited).
    remaining_quota = Column(Integer, nullable=False, default=0)
    granted_at = Column(UTCDateTime(), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class NotificationDelivery(Base):
    """Durable outbox row: one intended message to one member, claimed and retried at most once."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (UniqueConstraint("dedupe_key", name="uq_notification_delivery_dedupe"),)
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), ForeignKey("families.id"), nullable=False, index=True)
    member_id = Column(String(36), ForeignKey("family_members.id"), nullable=False, index=True)
    type = Column(String(30), nullable=False, index=True)
    # Stable identity of the real-world source (join request id, occurrence id, digest day) so an
    # edited schedule updates the same row instead of queueing a second message.
    dedupe_key = Column(String(200), nullable=False)
    payload_json = Column(Text, nullable=False)
    scheduled_at = Column(UTCDateTime(), nullable=False, index=True)
    state = Column(String(20), nullable=False, default=DeliveryState.pending.value, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    available_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    lease_until = Column(UTCDateTime(), nullable=True)
    # Safe classification only: never the WeChat payload, template content or receiver identity.
    result_code = Column(String(50), nullable=True)
    sent_at = Column(UTCDateTime(), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)


class NotificationDeliveryChild(Base):
    """Normalized child ownership for delivery payloads that can mention multiple children."""

    __tablename__ = "notification_delivery_children"
    __table_args__ = (
        UniqueConstraint("delivery_id", "child_id", name="uq_notification_delivery_child_scope"),
    )
    id = Column(String(36), primary_key=True, default=new_id)
    delivery_id = Column(
        String(36),
        ForeignKey("notification_deliveries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    child_id = Column(
        String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
