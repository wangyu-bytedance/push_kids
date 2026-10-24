"""Permanent review supersession and bounded coverage work."""

import sqlalchemy as sa
from alembic import op
from push_kids.persistence import review_queue_v1, review_queue_v2

revision = "20261020_0022"
down_revision = "20261018_0021"
branch_labels = None
depends_on = None


def upgrade():
    review_queue_v1.uninstall(op.get_bind())
    with op.batch_alter_table("knowledge_items") as batch:
        batch.add_column(
            sa.Column("review_status", sa.String(20), server_default="normal", nullable=False)
        )
        batch.add_column(sa.Column("superseded_by_knowledge_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("superseded_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("supersession_policy_revision", sa.String(50), nullable=True))
        batch.create_foreign_key(
            "fk_knowledge_superseded_by",
            "knowledge_items",
            ["superseded_by_knowledge_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index(
            "ix_knowledge_status", ["family_id", "child_id", "review_status", "subject_id", "id"]
        )
    op.create_index("ix_knowledge_discovery", "knowledge_items", ["created_at", "id"])
    op.create_index("ix_knowledge_covering", "knowledge_items", ["superseded_by_knowledge_id"])
    op.create_table(
        "knowledge_coverage_scan",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("after_created_at", sa.DateTime(), nullable=True),
        sa.Column("after_id", sa.String(36), nullable=False),
    )
    op.create_table(
        "knowledge_coverage_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "knowledge_item_id",
            sa.String(36),
            sa.ForeignKey("knowledge_items.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(), nullable=False),
        sa.Column("lease_token", sa.String(36)),
        sa.Column("error_code", sa.String(30)),
    )
    op.create_index("ix_coverage_claim", "knowledge_coverage_jobs", ["state", "available_at", "id"])
    op.create_index(
        "ix_coverage_family", "knowledge_coverage_jobs", ["family_id", "child_id", "state"]
    )
    review_queue_v2.install(op.get_bind())


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT COUNT(*) FROM knowledge_items WHERE review_status='superseded'")
    ):
        raise RuntimeError("Cannot discard permanent supersession states")
    review_queue_v2.uninstall(op.get_bind())
    op.drop_table("knowledge_coverage_jobs")
    op.drop_table("knowledge_coverage_scan")
    op.drop_index("ix_knowledge_discovery", "knowledge_items")
    with op.batch_alter_table("knowledge_items") as batch:
        batch.drop_index("ix_knowledge_status")
        batch.drop_constraint("fk_knowledge_superseded_by", type_="foreignkey")
        batch.drop_index("ix_knowledge_covering")
        for name in (
            "supersession_policy_revision",
            "superseded_at",
            "superseded_by_knowledge_id",
            "review_status",
        ):
            batch.drop_column(name)
    review_queue_v1.install(op.get_bind())
