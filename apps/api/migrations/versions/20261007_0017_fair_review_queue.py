"""Add bounded fair-review queue projections; no historical review facts change."""

from datetime import datetime
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision = "20261007_0017"
down_revision = "20261006_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_knowledge_scope_minutes_id",
        "knowledge_items",
        ["family_id", "child_id", "estimated_minutes", "id"],
    )
    for table in ("children", "subjects"):
        op.add_column(table, sa.Column("review_queue_resumed_on", sa.Date(), nullable=True))
    for name in ("queue_eligible_on", "last_offered_on"):
        op.add_column("review_items", sa.Column(name, sa.Date(), nullable=True))
    op.create_index(
        "ix_review_scope_offered_knowledge",
        "review_items",
        ["family_id", "child_id", "last_offered_on", "knowledge_item_id"],
    )
    for name in ("eligible_subject_count", "covered_subject_count"):
        op.add_column("daily_review_plans", sa.Column(name, sa.Integer(), nullable=True))
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    op.get_bind().execute(
        sa.text(
            "UPDATE review_items SET queue_eligible_on = "
            "CASE WHEN due_date > :today THEN due_date ELSE :today END"
        ),
        {"today": today},
    )


def downgrade() -> None:
    if op.get_bind().scalar(
        sa.text(
            "SELECT COUNT(*) FROM daily_review_plans WHERE policy_revision='daily-plan-fair-v2'"
        )
    ):
        raise RuntimeError("Retain fair-review projections after use; roll back application only")
    op.drop_index("ix_knowledge_scope_minutes_id", table_name="knowledge_items")
    op.drop_index("ix_review_scope_offered_knowledge", table_name="review_items")
    for table in ("children", "subjects"):
        op.drop_column(table, "review_queue_resumed_on")
    for name in ("queue_eligible_on", "last_offered_on"):
        op.drop_column("review_items", name)
    for name in ("eligible_subject_count", "covered_subject_count"):
        op.drop_column("daily_review_plans", name)
