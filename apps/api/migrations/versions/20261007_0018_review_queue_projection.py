"""Install planning's indexed queue projection and transactional synchronization contract."""

import sqlalchemy as sa
from alembic import op
from push_kids.persistence.review_queue_v1 import install, uninstall

revision = "20261007_0018"
down_revision = "20261007_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_queue_entries",
        sa.Column(
            "review_item_id",
            sa.String(36),
            sa.ForeignKey("review_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), nullable=False),
        sa.Column("subject_id", sa.String(36), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("repeated", sa.Boolean(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("manual", sa.Boolean(), nullable=False),
        sa.Column("due_on", sa.Date(), nullable=False),
        sa.Column("anchor_on", sa.Date(), nullable=False),
        sa.Column("priority_key", sa.String(66), nullable=False),
        sa.Column("last_offered_on", sa.Date(), nullable=True),
    )
    indexes = {
        "pool": ("available", "manual", "repeated", "minutes", "priority_key", "due_on"),
        "subject": ("available", "manual", "subject_id", "minutes", "priority_key", "due_on"),
        "subject_first": ("available", "manual", "subject_id", "priority_key", "due_on"),
        "offer": ("subject_id", "last_offered_on"),
        "manual": ("available", "manual", "due_on", "review_item_id"),
    }
    for name, columns in indexes.items():
        op.create_index(
            f"ix_review_queue_{name}", "review_queue_entries", ["family_id", "child_id", *columns]
        )
    install(op.get_bind())


def downgrade() -> None:
    # Derived data is reconstructible; keep the 0017 facts and stable plans untouched.
    uninstall(op.get_bind())
    op.drop_table("review_queue_entries")
