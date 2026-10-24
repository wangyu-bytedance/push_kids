"""Conservative empty-day review snapshots and indexed opportunities."""

import sqlalchemy as sa
from alembic import op
from push_kids.persistence import early_review_slots_v1

revision = "20261024_0023"
down_revision = "20261020_0022"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("daily_review_plans") as batch:
        batch.add_column(
            sa.Column(
                "materialization_state",
                sa.String(20),
                nullable=False,
                server_default="legacy_fixed",
            )
        )
        batch.add_column(sa.Column("evaluated_inventory_revision", sa.Integer(), nullable=True))
    with op.batch_alter_table("daily_review_plan_items") as batch:
        batch.add_column(
            sa.Column("selection_kind", sa.String(8), nullable=False, server_default="due")
        )
        batch.add_column(sa.Column("original_due_date", sa.Date(), nullable=True))
        batch.add_column(sa.Column("selected_review_version", sa.Integer(), nullable=True))
    op.create_table(
        "review_early_slots",
        sa.Column(
            "review_item_id",
            sa.String(36),
            sa.ForeignKey("review_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("slot_on", sa.Date(), primary_key=True),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), nullable=False),
        sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("priority_key", sa.String(66), nullable=False),
    )
    for name, fields in (
        ("ix_early_slots_pool", ["minutes", "priority_key"]),
        ("ix_early_slots_subject", ["subject_id", "minutes", "priority_key"]),
        ("ix_early_slots_first", ["subject_id", "priority_key"]),
    ):
        op.create_index(name, "review_early_slots", ["family_id", "child_id", "slot_on", *fields])
    early_review_slots_v1.install(op.get_bind())


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT COUNT(*) FROM daily_review_plan_items WHERE selection_kind='early'")
    ):
        raise RuntimeError("Cannot discard existing early review snapshots")
    early_review_slots_v1.uninstall(op.get_bind())
    op.drop_table("review_early_slots")
    with op.batch_alter_table("daily_review_plan_items") as batch:
        for name in ("selection_kind", "original_due_date", "selected_review_version"):
            batch.drop_column(name)
    with op.batch_alter_table("daily_review_plans") as batch:
        batch.drop_column("materialization_state")
        batch.drop_column("evaluated_inventory_revision")
