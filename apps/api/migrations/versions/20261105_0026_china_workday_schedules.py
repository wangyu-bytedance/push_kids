"""Explicit national workday modes; existing schedules retain their original rules."""

import sqlalchemy as sa
from alembic import op

revision = "20261105_0026"
down_revision = "20261024_0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("activity_schedules", "calendar_events"):
        op.add_column(
            table,
            sa.Column("workday_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    for table in ("activity_schedules", "calendar_events"):
        if op.get_bind().scalar(sa.text(f"SELECT COUNT(*) FROM {table} WHERE workday_only = 1")):
            raise RuntimeError("Cannot discard workday schedules; use a forward fix")
    for table in ("activity_schedules", "calendar_events"):
        op.drop_column(table, "workday_only")
