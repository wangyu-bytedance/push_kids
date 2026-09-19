"""add active six-digit family invite codes

Revision ID: 20260913_0014
Revises: 20260913_0013
Create Date: 2026-09-13
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260913_0014"
down_revision: str | Sequence[str] | None = "20260913_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "family_invites", sa.Column("active_code_hash", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "family_invites",
        sa.Column("code_nonce", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        "ux_family_invites_active_code_hash",
        "family_invites",
        ["active_code_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_family_invites_active_code_hash", table_name="family_invites")
    op.drop_column("family_invites", "code_nonce")
    op.drop_column("family_invites", "active_code_hash")
