"""notification channel: per-member reminder opt-in, encrypted receiver, grants and durable outbox

Revision ID: 20260906_0008
Revises: 20260906_0007
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0008"
down_revision: str | Sequence[str] | None = "20260906_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Four additive tables only. No existing table or column changes, so an older running
    # revision keeps serving traffic while this migration is applied.
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id", "type", name="uq_notification_preference_member_type"),
    )
    op.create_index(
        op.f("ix_notification_preferences_family_id"),
        "notification_preferences",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_preferences_member_id"),
        "notification_preferences",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_preferences_type"),
        "notification_preferences",
        ["type"],
        unique=False,
    )

    # `ciphertext` holds an AES-GCM envelope of the WeChat receiver id. There is deliberately no
    # index or unique constraint on it: the plaintext must never be searchable.
    op.create_table(
        "notification_destinations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("actor_binding_id", sa.String(length=36), nullable=True),
        sa.Column("app_id", sa.String(length=32), nullable=False),
        sa.Column("key_version", sa.String(length=10), nullable=False, server_default="v1"),
        sa.Column("ciphertext", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_binding_id"], ["wechat_actor_bindings.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id", name="uq_notification_destination_member"),
    )
    op.create_index(
        op.f("ix_notification_destinations_actor_binding_id"),
        "notification_destinations",
        ["actor_binding_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_destinations_family_id"),
        "notification_destinations",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_destinations_member_id"),
        "notification_destinations",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_destinations_status"),
        "notification_destinations",
        ["status"],
        unique=False,
    )

    op.create_table(
        "notification_subscriptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="unknown"),
        sa.Column("remaining_quota", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id", "type", name="uq_notification_subscription_member_type"),
    )
    op.create_index(
        op.f("ix_notification_subscriptions_family_id"),
        "notification_subscriptions",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_subscriptions_member_id"),
        "notification_subscriptions",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_subscriptions_type"),
        "notification_subscriptions",
        ["type"],
        unique=False,
    )

    # The unique dedupe key is what makes re-planning safe: a second tick can only refresh the
    # existing row for the same real-world source.
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("member_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("dedupe_key", sa.String(length=200), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_code", sa.String(length=50), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedupe_key", name="uq_notification_delivery_dedupe"),
    )
    op.create_index(
        op.f("ix_notification_deliveries_family_id"),
        "notification_deliveries",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_deliveries_member_id"),
        "notification_deliveries",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_deliveries_type"),
        "notification_deliveries",
        ["type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_deliveries_scheduled_at"),
        "notification_deliveries",
        ["scheduled_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_deliveries_state"),
        "notification_deliveries",
        ["state"],
        unique=False,
    )
    # The dispatcher always claims by (state, available_at, scheduled_at); this composite index
    # keeps that scan bounded as history grows.
    op.create_index(
        "ix_notification_deliveries_claim",
        "notification_deliveries",
        ["state", "available_at", "scheduled_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notification_deliveries_claim", table_name="notification_deliveries")
    op.drop_index(op.f("ix_notification_deliveries_state"), table_name="notification_deliveries")
    op.drop_index(
        op.f("ix_notification_deliveries_scheduled_at"), table_name="notification_deliveries"
    )
    op.drop_index(op.f("ix_notification_deliveries_type"), table_name="notification_deliveries")
    op.drop_index(
        op.f("ix_notification_deliveries_member_id"), table_name="notification_deliveries"
    )
    op.drop_index(
        op.f("ix_notification_deliveries_family_id"), table_name="notification_deliveries"
    )
    op.drop_table("notification_deliveries")
    op.drop_index(
        op.f("ix_notification_subscriptions_type"), table_name="notification_subscriptions"
    )
    op.drop_index(
        op.f("ix_notification_subscriptions_member_id"), table_name="notification_subscriptions"
    )
    op.drop_index(
        op.f("ix_notification_subscriptions_family_id"), table_name="notification_subscriptions"
    )
    op.drop_table("notification_subscriptions")
    op.drop_index(
        op.f("ix_notification_destinations_status"), table_name="notification_destinations"
    )
    op.drop_index(
        op.f("ix_notification_destinations_member_id"), table_name="notification_destinations"
    )
    op.drop_index(
        op.f("ix_notification_destinations_family_id"), table_name="notification_destinations"
    )
    op.drop_index(
        op.f("ix_notification_destinations_actor_binding_id"),
        table_name="notification_destinations",
    )
    op.drop_table("notification_destinations")
    op.drop_index(op.f("ix_notification_preferences_type"), table_name="notification_preferences")
    op.drop_index(
        op.f("ix_notification_preferences_member_id"), table_name="notification_preferences"
    )
    op.drop_index(
        op.f("ix_notification_preferences_family_id"), table_name="notification_preferences"
    )
    op.drop_table("notification_preferences")
