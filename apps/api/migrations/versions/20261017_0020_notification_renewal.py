"""Member completion cursors and idempotent notification grants (expand only)."""

import sqlalchemy as sa
from alembic import op

revision = "20261017_0020"
down_revision = "20261012_0019"
branch_labels = None
depends_on = None

TABLES = (
    "review_member_completion_progress",
    "review_member_completion_receipts",
    "notification_renewal_preferences",
    "notification_renewal_states",
    "notification_grant_attempts",
)


def _scope(*, primary: bool = True) -> list[sa.Column]:
    return [
        sa.Column(
            "family_id",
            sa.String(80),
            sa.ForeignKey("families.id"),
            primary_key=primary,
            nullable=False,
        ),
        sa.Column(
            "member_id",
            sa.String(36),
            sa.ForeignKey("family_members.id"),
            primary_key=primary,
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        TABLES[0],
        *_scope(),
        sa.Column("total_completed", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        TABLES[1],
        *_scope(),
        sa.Column("review_id", sa.String(36), sa.ForeignKey("review_items.id"), primary_key=True),
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_completion_receipt_scope_child", TABLES[1], ["family_id", "child_id"])
    op.create_table(
        TABLES[2],
        *_scope(),
        sa.Column("choice", sa.String(12), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("last_request_key", sa.String(100), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        TABLES[3],
        *_scope(),
        sa.Column("type", sa.String(30), primary_key=True),
        sa.Column("template_fingerprint", sa.String(64), nullable=False),
        sa.Column("consented", sa.Boolean(), nullable=False),
        sa.Column("last_prompt_cursor", sa.Integer(), nullable=False),
        sa.Column("stop_reason", sa.String(30), nullable=True),
        sa.Column("retry_after", sa.DateTime(), nullable=True),
        sa.Column("active_attempt_id", sa.String(36), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        TABLES[4],
        sa.Column("id", sa.String(36), primary_key=True),
        *_scope(primary=False),
        sa.Column("request_key", sa.String(100), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("mode", sa.String(12), nullable=False),
        sa.Column("choice_version", sa.Integer(), nullable=False),
        sa.Column("bindings_json", sa.Text(), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("result_fingerprint", sa.String(64), nullable=True),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "family_id", "member_id", "request_key", name="uq_grant_attempt_request"
        ),
    )
    op.create_index(
        "ix_grant_attempt_scope_created", TABLES[4], ["family_id", "member_id", "created_at"]
    )


def downgrade() -> None:
    connection = op.get_bind()
    for name in TABLES:
        if connection.scalar(sa.text(f"SELECT COUNT(*) FROM {name}")):
            raise RuntimeError(
                "Cannot discard completion facts or WeChat grant events; preserve data first"
            )
    for name in reversed(TABLES):
        op.drop_table(name)
