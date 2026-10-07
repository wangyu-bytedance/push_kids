"""Parent review inventory and one-shot manual scheduling."""

import sqlalchemy as sa
from alembic import op

revision = "20261006_0016"
down_revision = "20261006_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "children",
        sa.Column("review_inventory_revision", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ix_review_scope_count_knowledge",
        "review_items",
        ["family_id", "child_id", "review_count", "knowledge_item_id"],
    )
    op.create_table(
        "review_schedule_overrides",
        sa.Column(
            "review_item_id", sa.String(36), sa.ForeignKey("review_items.id"), primary_key=True
        ),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column("scheduled_on", sa.Date(), nullable=False),
        sa.Column("requested_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_review_override_scope_day",
        "review_schedule_overrides",
        ["family_id", "child_id", "scheduled_on", "review_item_id"],
    )
    op.create_table(
        "review_schedule_changes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column(
            "review_item_id", sa.String(36), sa.ForeignKey("review_items.id"), nullable=False
        ),
        sa.Column("idempotency_key", sa.String(100), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("before_due_date", sa.Date(), nullable=False),
        sa.Column("after_due_date", sa.Date(), nullable=False),
        sa.Column("before_version", sa.Integer(), nullable=False),
        sa.Column("after_version", sa.Integer(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("family_id", "idempotency_key", name="uq_review_schedule_key"),
    )
    op.create_index(
        "ix_review_schedule_scope_review",
        "review_schedule_changes",
        ["family_id", "child_id", "review_item_id"],
    )


def downgrade() -> None:
    if op.get_bind().scalar(sa.text("SELECT COUNT(*) FROM review_schedule_overrides")):
        raise RuntimeError("Cannot discard pending parent review arrangements")
    op.drop_table("review_schedule_changes")
    op.drop_table("review_schedule_overrides")
    op.drop_index("ix_review_scope_count_knowledge", table_name="review_items")
    op.drop_column("children", "review_inventory_revision")
