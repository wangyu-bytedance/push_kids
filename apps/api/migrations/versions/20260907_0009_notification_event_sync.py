"""notification event sync: receiver lookup index and provider message id

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
    # Two nullable columns only. Existing rows stay valid: the service resolves a receiver by
    # decrypting once and backfills the index on first match, so no data migration is needed.
    op.add_column(
        "notification_destinations",
        sa.Column("receiver_hmac", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_notification_destinations_receiver_hmac"),
        "notification_destinations",
        ["receiver_hmac"],
        unique=False,
    )
    op.add_column(
        "notification_deliveries",
        sa.Column("provider_msg_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_notification_deliveries_provider_msg_id"),
        "notification_deliveries",
        ["provider_msg_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_deliveries_provider_msg_id"),
        table_name="notification_deliveries",
    )
    op.drop_column("notification_deliveries", "provider_msg_id")
    op.drop_index(
        op.f("ix_notification_destinations_receiver_hmac"),
        table_name="notification_destinations",
    )
    op.drop_column("notification_destinations", "receiver_hmac")
