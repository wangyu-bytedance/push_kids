"""child-scoped travel arrangements

Revision ID: 20260906_0006
Revises: 20260906_0005
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0006"
down_revision: str | Sequence[str] | None = "20260906_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "travel_arrangements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("weekdays", sa.String(length=30), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_travel_arrangements_family_id"), "travel_arrangements", ["family_id"])
    op.create_index(op.f("ix_travel_arrangements_child_id"), "travel_arrangements", ["child_id"])
    op.create_table(
        "travel_arrangement_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("arrangement_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["arrangement_id"], ["travel_arrangements.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_id", "idempotency_key", name="uq_travel_request_key"),
    )
    op.create_index(
        op.f("ix_travel_arrangement_requests_family_id"),
        "travel_arrangement_requests",
        ["family_id"],
    )
    op.create_index(
        op.f("ix_travel_arrangement_requests_arrangement_id"),
        "travel_arrangement_requests",
        ["arrangement_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_travel_arrangement_requests_arrangement_id"),
        table_name="travel_arrangement_requests",
    )
    op.drop_index(
        op.f("ix_travel_arrangement_requests_family_id"),
        table_name="travel_arrangement_requests",
    )
    op.drop_table("travel_arrangement_requests")
    op.drop_index(op.f("ix_travel_arrangements_child_id"), table_name="travel_arrangements")
    op.drop_index(op.f("ix_travel_arrangements_family_id"), table_name="travel_arrangements")
    op.drop_table("travel_arrangements")
