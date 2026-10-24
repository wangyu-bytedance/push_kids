"""Independent parent-confirmed photo footprints (expand only, no historical backfill)."""

import sqlalchemy as sa
from alembic import op

revision = "20261018_0021"
down_revision = "20261017_0020"
branch_labels = None
depends_on = None

TABLES = (
    "footprint_scopes",
    "footprint_preferences",
    "footprint_imports",
    "footprint_visits",
    "footprint_photos",
)


def _scope(primary=False):
    return [
        sa.Column(
            "family_id",
            sa.String(80),
            primary_key=primary,
            nullable=False,
        ),
        sa.Column(
            "child_id",
            sa.String(36),
            sa.ForeignKey("children.id"),
            primary_key=primary,
            nullable=False,
        ),
    ]


def _place():
    return [
        sa.Column("place_name", sa.String(120)),
        sa.Column("city", sa.String(80)),
        sa.Column("country", sa.String(80)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("coordinate_system", sa.String(12)),
        sa.Column("precision", sa.String(12), nullable=False),
    ]


def upgrade():
    op.create_table(TABLES[0], *_scope(True), sa.Column("revision", sa.Integer(), nullable=False))
    op.create_table(
        TABLES[1],
        sa.Column("family_id", sa.String(80), primary_key=True),
        sa.Column("member_id", sa.String(36), primary_key=True),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False),
        sa.Column("consented", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        TABLES[2],
        sa.Column("id", sa.String(36), primary_key=True),
        *_scope(),
        sa.Column("member_id", sa.String(36), nullable=False),
        sa.Column("request_key", sa.String(100), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("slot_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ux_footprint_import_request",
        TABLES[2],
        ["family_id", "member_id", "request_key"],
        unique=True,
    )
    op.create_index(
        "ix_footprint_import_scope", TABLES[2], ["family_id", "child_id", "created_at", "id"]
    )
    op.create_table(
        TABLES[3],
        sa.Column("id", sa.String(36), primary_key=True),
        *_scope(),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("sort_time", sa.String(8), nullable=False),
        sa.Column("sort_created_at", sa.DateTime(), nullable=False),
        sa.Column("day_order", sa.Integer(), nullable=False),
        sa.Column("place_key", sa.String(64), nullable=False),
        *_place(),
    )
    op.create_index(
        "ux_footprint_visit_day",
        TABLES[3],
        ["family_id", "child_id", "local_date", "place_key"],
        unique=True,
    )
    op.create_index(
        "ix_footprint_visit_scope", TABLES[3], ["family_id", "child_id", "local_date", "id"]
    )
    op.create_table(
        TABLES[4],
        sa.Column("id", sa.String(36), primary_key=True),
        *_scope(),
        sa.Column(
            "import_id", sa.String(36), sa.ForeignKey("footprint_imports.id"), nullable=False
        ),
        sa.Column("visit_id", sa.String(36), sa.ForeignKey("footprint_visits.id")),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("upload_path", sa.String(300), nullable=False),
        sa.Column("ticket_expires_at", sa.DateTime(), nullable=False),
        sa.Column("original_ref", sa.String(800)),
        sa.Column("display_ref", sa.String(800)),
        sa.Column("thumbnail_ref", sa.String(800)),
        sa.Column("derived_ready", sa.Boolean(), nullable=False),
        sa.Column("is_manual", sa.Boolean(), nullable=False),
        sa.Column("sha256", sa.String(64)),
        sa.Column("duplicate_of", sa.String(36)),
        sa.Column("received_at", sa.DateTime()),
        sa.Column("draft_expires_at", sa.DateTime()),
        sa.Column("original_delete_after", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime()),
        sa.Column("local_date", sa.Date()),
        sa.Column("local_time", sa.String(8)),
        sa.Column("offset_minutes", sa.Integer()),
        sa.Column("occurred_at", sa.DateTime()),
        sa.Column("time_source", sa.String(12), nullable=False),
        *_place(),
        sa.Column("location_source", sa.String(12), nullable=False),
        sa.Column("candidates_json", sa.Text(), nullable=False),
        sa.Column("job_state", sa.String(16), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("lease_until", sa.DateTime()),
        sa.Column("available_at", sa.DateTime(), nullable=False),
        sa.Column("error_code", sa.String(40)),
        sa.Column("cleanup_state", sa.String(16), nullable=False),
        sa.Column("cleanup_attempts", sa.Integer(), nullable=False),
        sa.Column("cleanup_after", sa.DateTime()),
    )
    for name, columns in (
        ("ix_footprint_photo_scope", ["family_id", "child_id", "state", "created_at", "id"]),
        ("ix_footprint_photo_visit", ["family_id", "child_id", "visit_id", "ordinal", "id"]),
        ("ix_footprint_photo_job", ["job_state", "available_at", "lease_until"]),
        ("ix_footprint_photo_gallery", ["family_id", "child_id", "visit_id", "id"]),
        ("ix_footprint_photo_expiry", ["state", "draft_expires_at"]),
        ("ix_footprint_photo_cleanup", ["cleanup_state", "cleanup_after"]),
        ("ix_footprint_photo_hash", ["family_id", "child_id", "sha256", "state"]),
    ):
        op.create_index(name, TABLES[4], columns)


def downgrade():
    connection = op.get_bind()
    for table in TABLES:
        if connection.scalar(sa.text(f"SELECT COUNT(*) FROM {table}")):
            raise RuntimeError(
                "Cannot discard footprint memories or pending cleanup; preserve data first"
            )
    for table in reversed(TABLES):
        op.drop_table(table)
