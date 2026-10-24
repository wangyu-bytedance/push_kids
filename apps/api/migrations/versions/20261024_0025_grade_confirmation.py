"""Shared child academic-year confirmation; preserve all existing formal grades."""

import sqlalchemy as sa
from alembic import op

revision = "20261024_0025"
down_revision = "20261024_0024"
branch_labels = None
depends_on = None
INDEX = "ix_children_family_active_deleting_created_id"


def upgrade() -> None:
    op.add_column("children", sa.Column("grade_confirmed_school_year", sa.Integer(), nullable=True))
    op.add_column(
        "children", sa.Column("grade_revision", sa.Integer(), nullable=False, server_default="0")
    )
    op.create_index(INDEX, "children", ["family_id", "active", "deleting", "created_at", "id"])


def downgrade() -> None:
    if op.get_bind().scalar(
        sa.text(
            "SELECT COUNT(*) FROM children "
            "WHERE grade_confirmed_school_year IS NOT NULL OR grade_revision <> 0"
        )
    ):
        raise RuntimeError("Cannot discard shared grade confirmation facts; preserve data first")
    op.drop_index(INDEX, table_name="children")
    op.drop_column("children", "grade_revision")
    op.drop_column("children", "grade_confirmed_school_year")
