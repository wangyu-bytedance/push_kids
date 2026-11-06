"""Bound same-subject recent history with a tenant-leading index."""

from alembic import op

revision = "20261105_0027"
down_revision = "20261105_0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_knowledge_recent_subject",
        "knowledge_items",
        ["family_id", "child_id", "subject_id", "review_status", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_recent_subject", table_name="knowledge_items")
