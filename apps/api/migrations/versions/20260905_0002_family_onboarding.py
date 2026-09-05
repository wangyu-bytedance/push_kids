"""family onboarding and membership

Revision ID: 20260905_0002
Revises: 20260903_0001
Create Date: 2026-09-05
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "20260905_0002"
down_revision: str | Sequence[str] | None = "20260903_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    child_families = {
        row[0]
        for row in connection.execute(
            sa.text("SELECT DISTINCT family_id FROM children WHERE family_id IS NOT NULL")
        )
    }
    bound_families = {
        row[0]
        for row in connection.execute(
            sa.text(
                "SELECT DISTINCT family_id FROM wechat_actor_bindings "
                "WHERE family_id IS NOT NULL AND status = 'active'"
            )
        )
    }
    unowned = child_families - bound_families
    if unowned:
        raise RuntimeError("存在没有 active 微信绑定的历史家庭，必须先人工确认归属")

    op.alter_column(
        "wechat_actor_bindings",
        "family_id",
        existing_type=sa.String(length=80),
        nullable=True,
    )
    op.create_table(
        "families",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_families_status"), "families", ["status"], unique=False)

    now = datetime.now(UTC)
    for family_id in sorted(child_families | bound_families):
        connection.execute(
            sa.text(
                "INSERT INTO families (id, display_name, status, created_at, updated_at) "
                "VALUES (:id, :name, 'active', :created_at, :updated_at)"
            ),
            {
                "id": family_id,
                "name": "我的家庭",
                "created_at": now,
                "updated_at": now,
            },
        )

    op.create_table(
        "family_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("actor_binding_id", sa.String(length=36), nullable=False),
        sa.Column("active_actor_binding_id", sa.String(length=36), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("relationship_label", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["actor_binding_id"], ["wechat_actor_bindings.id"]),
        sa.ForeignKeyConstraint(["active_actor_binding_id"], ["wechat_actor_bindings.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("active_actor_binding_id", name="uq_family_member_active_actor"),
    )
    op.create_index(
        op.f("ix_family_members_active_actor_binding_id"),
        "family_members",
        ["active_actor_binding_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_family_members_actor_binding_id"),
        "family_members",
        ["actor_binding_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_family_members_family_id"), "family_members", ["family_id"], unique=False
    )
    op.create_index(op.f("ix_family_members_role"), "family_members", ["role"], unique=False)
    op.create_index(op.f("ix_family_members_status"), "family_members", ["status"], unique=False)

    binding_rows = list(
        connection.execute(
            sa.text(
                "SELECT id, family_id, created_at, updated_at FROM wechat_actor_bindings "
                "WHERE family_id IS NOT NULL AND status = 'active'"
            )
        )
    )
    for binding_id, family_id, created_at, updated_at in binding_rows:
        connection.execute(
            sa.text(
                "INSERT INTO family_members "
                "(id, family_id, actor_binding_id, active_actor_binding_id, role, "
                "relationship_label, status, "
                "created_at, updated_at, removed_at) "
                "VALUES (:id, :family_id, :binding_id, :binding_id, 'manager', "
                "'家庭管理员', 'active', "
                ":created_at, :updated_at, NULL)"
            ),
            {
                "id": str(uuid.uuid4()),
                "family_id": family_id,
                "binding_id": binding_id,
                "created_at": created_at or now,
                "updated_at": updated_at or now,
            },
        )

    op.create_table(
        "family_invites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_member_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_member_id"], ["family_members.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_id", "idempotency_key", name="uq_family_invite_request"),
        sa.UniqueConstraint("token_hash", name="uq_family_invite_token"),
    )
    for name, columns in (
        ("ix_family_invites_created_by_member_id", ["created_by_member_id"]),
        ("ix_family_invites_expires_at", ["expires_at"]),
        ("ix_family_invites_family_id", ["family_id"]),
        ("ix_family_invites_status", ["status"]),
    ):
        op.create_index(name, "family_invites", columns, unique=False)

    op.create_table(
        "family_join_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("invite_id", sa.String(length=36), nullable=False),
        sa.Column("applicant_binding_id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("relationship_label", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("decided_role", sa.String(length=20), nullable=True),
        sa.Column("decided_by_member_id", sa.String(length=36), nullable=True),
        sa.Column("decision_reason", sa.String(length=160), nullable=True),
        sa.Column("decision_idempotency_key", sa.String(length=100), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["applicant_binding_id"], ["wechat_actor_bindings.id"]),
        sa.ForeignKeyConstraint(["decided_by_member_id"], ["family_members.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.ForeignKeyConstraint(["invite_id"], ["family_invites.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "applicant_binding_id", "idempotency_key", name="uq_family_join_request_key"
        ),
    )
    for name, columns in (
        ("ix_family_join_requests_applicant_binding_id", ["applicant_binding_id"]),
        ("ix_family_join_requests_family_id", ["family_id"]),
        ("ix_family_join_requests_invite_id", ["invite_id"]),
        ("ix_family_join_requests_status", ["status"]),
    ):
        op.create_index(name, "family_join_requests", columns, unique=False)

    op.create_table(
        "family_audit_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("actor_binding_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_binding_id"], ["wechat_actor_bindings.id"]),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, columns in (
        ("ix_family_audit_events_action", ["action"]),
        ("ix_family_audit_events_actor_binding_id", ["actor_binding_id"]),
        ("ix_family_audit_events_created_at", ["created_at"]),
        ("ix_family_audit_events_family_id", ["family_id"]),
    ):
        op.create_index(name, "family_audit_events", columns, unique=False)


def downgrade() -> None:
    op.drop_table("family_audit_events")
    op.drop_table("family_join_requests")
    op.drop_table("family_invites")
    op.drop_table("family_members")
    op.drop_table("families")
    op.alter_column(
        "wechat_actor_bindings",
        "family_id",
        existing_type=sa.String(length=80),
        nullable=False,
    )
