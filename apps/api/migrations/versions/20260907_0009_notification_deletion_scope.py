"""track child ownership for notification deliveries

Revision ID: 20260907_0009
Revises: 20260906_0008
Create Date: 2026-09-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260907_0009"
down_revision: str | Sequence[str] | None = "20260906_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_delivery_children",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("delivery_id", sa.String(length=36), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["delivery_id"], ["notification_deliveries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id", "child_id", name="uq_notification_delivery_child_scope"),
    )
    op.create_index(
        op.f("ix_notification_delivery_children_delivery_id"),
        "notification_delivery_children",
        ["delivery_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_delivery_children_child_id"),
        "notification_delivery_children",
        ["child_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_delivery_children_child_id"),
        table_name="notification_delivery_children",
    )
    op.drop_index(
        op.f("ix_notification_delivery_children_delivery_id"),
        table_name="notification_delivery_children",
    )
    op.drop_table("notification_delivery_children")
