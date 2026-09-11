"""add tenant-leading indexes for bounded read paths

Revision ID: 20260911_0011
Revises: 20260911_0010
Create Date: 2026-09-11
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20260911_0011"
down_revision: str | Sequence[str] | None = "20260911_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INDEXES = (
    (
        "ix_learning_submissions_family_child_state_created_id",
        "learning_submissions",
        ["family_id", "child_id", "state", "created_at", "id"],
    ),
    (
        "ix_learning_submissions_family_child_state_occurred_id",
        "learning_submissions",
        ["family_id", "child_id", "state", "occurred_at", "id"],
    ),
    (
        "ix_learning_records_family_child_occurred_submission",
        "learning_records",
        ["family_id", "child_id", "occurred_at", "submission_id", "id"],
    ),
    (
        "ix_knowledge_items_family_child_created_id",
        "knowledge_items",
        ["family_id", "child_id", "created_at", "id"],
    ),
    (
        "ix_knowledge_occurrences_family_occurred_knowledge",
        "knowledge_occurrences",
        ["family_id", "occurred_at", "knowledge_item_id"],
    ),
    (
        "ix_review_items_family_child_active_due_id",
        "review_items",
        ["family_id", "child_id", "active", "due_date", "id"],
    ),
    (
        "ix_review_feedback_family_review_occurred",
        "review_feedback",
        ["family_id", "review_item_id", "occurred_at"],
    ),
    (
        "ix_activity_records_family_child_occurred_id",
        "activity_records",
        ["family_id", "child_id", "occurred_at", "id"],
    ),
)


def upgrade() -> None:
    for name, table, columns in INDEXES:
        op.create_index(name, table, columns)


def downgrade() -> None:
    for name, table, _columns in reversed(INDEXES):
        op.drop_index(name, table_name=table)
