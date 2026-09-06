"""child profile lifecycle: archived children leave the switcher but keep their history

Revision ID: 20260906_0005
Revises: 20260906_0004
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0005"
down_revision: str | Sequence[str] | None = "20260906_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Every pre-existing child predates archiving, so the server default lands them as active
    # without a separate backfill statement. The column is additive, which keeps old readers
    # and writers working while the application rolls out.
    op.add_column(
        "children",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index(op.f("ix_children_active"), "children", ["active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_children_active"), table_name="children")
    op.drop_column("children", "active")
