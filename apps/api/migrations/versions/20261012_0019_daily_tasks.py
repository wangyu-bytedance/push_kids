"""Parent-configured daily tasks and Shanghai-day completion facts."""

import sqlalchemy as sa
from alembic import op

revision = "20261012_0019"
down_revision = "20261007_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("target_minutes", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_daily_tasks_scope_active_order",
        "daily_tasks",
        ["family_id", "child_id", "active", "created_at", "id"],
    )
    op.create_table(
        "daily_task_completions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("daily_tasks.id"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("name_snapshot", sa.String(30), nullable=False),
        sa.Column("minutes_snapshot", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "family_id", "child_id", "task_id", "day", name="uq_daily_task_completion_day"
        ),
    )
    op.create_index(
        "ix_daily_completion_scope_day_task",
        "daily_task_completions",
        ["family_id", "child_id", "day", "task_id"],
    )


def downgrade() -> None:
    connection = op.get_bind()
    if connection.scalar(sa.text("SELECT COUNT(*) FROM daily_tasks")) or connection.scalar(
        sa.text("SELECT COUNT(*) FROM daily_task_completions")
    ):
        raise RuntimeError(
            "Cannot discard parent daily tasks or completion facts; preserve data first"
        )
    op.drop_table("daily_task_completions")
    op.drop_table("daily_tasks")
