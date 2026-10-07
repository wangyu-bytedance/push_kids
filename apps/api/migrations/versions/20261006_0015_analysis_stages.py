"""Bounded temporary analysis stages, additive to 20260913_0014."""

import sqlalchemy as sa
from alembic import op

revision = "20261006_0015"
down_revision = "20260913_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_stage_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(80), nullable=False),
        sa.Column("child_id", sa.String(36), sa.ForeignKey("children.id"), nullable=False),
        sa.Column(
            "submission_id", sa.String(36), sa.ForeignKey("learning_submissions.id"), nullable=False
        ),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("agent_jobs.id"), nullable=False),
        sa.Column("unit_key", sa.String(40), nullable=False),
        sa.Column("revision", sa.String(40), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("family_id", "job_id", "unit_key", name="uq_analysis_stage_unit"),
    )
    op.create_index(
        "ix_analysis_stage_scope",
        "analysis_stage_results",
        ["family_id", "child_id", "submission_id"],
    )
    op.create_index("ix_analysis_stage_expiry", "analysis_stage_results", ["expires_at", "id"])


def downgrade() -> None:
    op.drop_table("analysis_stage_results")
