"""add durable batch feedback replay records

Revision ID: 20260913_0012
Revises: 20260911_0011
Create Date: 2026-09-13
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260913_0012"
down_revision: str | Sequence[str] | None = "20260911_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_feedback_batch_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_id", "idempotency_key", name="uq_review_feedback_batch_key"),
    )
    op.create_index(
        "ix_review_feedback_batch_requests_family_id",
        "review_feedback_batch_requests",
        ["family_id"],
    )
    op.create_index(
        "ix_review_feedback_batch_requests_child_id",
        "review_feedback_batch_requests",
        ["child_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_review_feedback_batch_requests_child_id",
        table_name="review_feedback_batch_requests",
    )
    op.drop_index(
        "ix_review_feedback_batch_requests_family_id",
        table_name="review_feedback_batch_requests",
    )
    op.drop_table("review_feedback_batch_requests")
