"""durable child and family data deletion

Revision ID: 20260906_0007
Revises: 20260906_0006
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0007"
down_revision: str | Sequence[str] | None = "20260906_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "children",
        sa.Column("deleting", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index(op.f("ix_children_deleting"), "children", ["deleting"], unique=False)
    op.create_table(
        "deletion_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_binding_id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=True),
        sa.Column("target_type", sa.String(length=20), nullable=False),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("idempotency_key_hash", sa.String(length=64), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["actor_binding_id"], ["wechat_actor_bindings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "actor_binding_id", "idempotency_key_hash", name="uq_deletion_actor_request"
        ),
    )
    for column in (
        "actor_binding_id",
        "family_id",
        "target_type",
        "target_id",
        "state",
        "available_at",
        "expires_at",
    ):
        op.create_index(op.f(f"ix_deletion_requests_{column}"), "deletion_requests", [column])


def downgrade() -> None:
    for column in (
        "expires_at",
        "available_at",
        "state",
        "target_id",
        "target_type",
        "family_id",
        "actor_binding_id",
    ):
        op.drop_index(op.f(f"ix_deletion_requests_{column}"), table_name="deletion_requests")
    op.drop_table("deletion_requests")
    op.drop_index(op.f("ix_children_deleting"), table_name="children")
    op.drop_column("children", "deleting")
