"""Footprint-owned persistence. No learning Submission or MediaObject ownership."""

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Index, Integer, String, Text

from push_kids.persistence.models import Base, new_id
from push_kids.persistence.types import UTCDateTime
from push_kids.platform.time import utcnow


class FootprintScope(Base):
    __tablename__ = "footprint_scopes"
    family_id = Column(String(80), primary_key=True)
    child_id = Column(String(36), ForeignKey("children.id"), primary_key=True)
    revision = Column(Integer, nullable=False, default=0)


class FootprintPreference(Base):
    __tablename__ = "footprint_preferences"
    family_id = Column(String(80), primary_key=True)
    # "local" is only the explicit local-development family identity.
    member_id = Column(String(36), primary_key=True)
    ai_enabled = Column(Boolean, nullable=False, default=False)
    consented = Column(Boolean, nullable=False, default=False)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow)


class FootprintImport(Base):
    __tablename__ = "footprint_imports"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    member_id = Column(String(36), nullable=False)
    request_key = Column(String(100), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    slot_count = Column(Integer, nullable=False)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    __table_args__ = (
        Index("ux_footprint_import_request", "family_id", "member_id", "request_key", unique=True),
        Index("ix_footprint_import_scope", "family_id", "child_id", "created_at", "id"),
    )


class FootprintVisit(Base):
    __tablename__ = "footprint_visits"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    local_date = Column(Date, nullable=False)
    sort_time = Column(String(8), nullable=False)
    sort_created_at = Column(UTCDateTime(), nullable=False)
    day_order = Column(Integer, nullable=False, default=0)
    place_key = Column(String(64), nullable=False)
    place_name = Column(String(120), nullable=True)
    city = Column(String(80), nullable=True)
    country = Column(String(80), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    coordinate_system = Column(String(12), nullable=True)
    precision = Column(String(12), nullable=False, default="unknown")
    __table_args__ = (
        Index(
            "ux_footprint_visit_day",
            "family_id",
            "child_id",
            "local_date",
            "place_key",
            unique=True,
        ),
        Index("ix_footprint_visit_scope", "family_id", "child_id", "local_date", "id"),
    )


class FootprintPhoto(Base):
    __tablename__ = "footprint_photos"
    id = Column(String(36), primary_key=True, default=new_id)
    family_id = Column(String(80), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    import_id = Column(String(36), ForeignKey("footprint_imports.id"), nullable=False)
    visit_id = Column(String(36), ForeignKey("footprint_visits.id"), nullable=True)
    ordinal = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False, default=0)
    state = Column(String(16), nullable=False, default="uploading")
    upload_path = Column(String(300), nullable=False)
    ticket_expires_at = Column(UTCDateTime(), nullable=False)
    original_ref = Column(String(800), nullable=True)
    display_ref = Column(String(800), nullable=True)
    thumbnail_ref = Column(String(800), nullable=True)
    derived_ready = Column(Boolean, nullable=False, default=False)
    is_manual = Column(Boolean, nullable=False, default=False)
    sha256 = Column(String(64), nullable=True)
    duplicate_of = Column(String(36), nullable=True)
    received_at = Column(UTCDateTime(), nullable=True)
    draft_expires_at = Column(UTCDateTime(), nullable=True)
    original_delete_after = Column(UTCDateTime(), nullable=True)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    confirmed_at = Column(UTCDateTime(), nullable=True)
    local_date = Column(Date, nullable=True)
    local_time = Column(String(8), nullable=True)
    offset_minutes = Column(Integer, nullable=True)
    occurred_at = Column(UTCDateTime(), nullable=True)
    time_source = Column(String(12), nullable=False, default="unknown")
    place_name = Column(String(120), nullable=True)
    city = Column(String(80), nullable=True)
    country = Column(String(80), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    coordinate_system = Column(String(12), nullable=True)
    precision = Column(String(12), nullable=False, default="unknown")
    location_source = Column(String(12), nullable=False, default="unknown")
    candidates_json = Column(Text, nullable=False, default="[]")
    job_state = Column(String(16), nullable=False, default="queued")
    attempts = Column(Integer, nullable=False, default=0)
    lease_until = Column(UTCDateTime(), nullable=True)
    available_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    error_code = Column(String(40), nullable=True)
    cleanup_state = Column(String(16), nullable=False, default="none")
    cleanup_attempts = Column(Integer, nullable=False, default=0)
    cleanup_after = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        Index("ix_footprint_photo_scope", "family_id", "child_id", "state", "created_at", "id"),
        Index("ix_footprint_photo_visit", "family_id", "child_id", "visit_id", "ordinal", "id"),
        Index("ix_footprint_photo_gallery", "family_id", "child_id", "visit_id", "id"),
        Index("ix_footprint_photo_job", "job_state", "available_at", "lease_until"),
        Index("ix_footprint_photo_expiry", "state", "draft_expires_at"),
        Index("ix_footprint_photo_cleanup", "cleanup_state", "cleanup_after"),
        Index("ix_footprint_photo_hash", "family_id", "child_id", "sha256", "state"),
    )
