"""Reliable input clock and parent-approved suggestion workflow (additive)."""

import sqlalchemy as sa
from alembic import op

revision = "20261024_0024"
down_revision = "20261024_0023"
branch_labels = None
depends_on = None


def scope(*, primary=False):
    return [
        sa.Column("family_id", sa.String(80), primary_key=primary, nullable=False),
        sa.Column(
            "child_id",
            sa.String(36),
            sa.ForeignKey("children.id"),
            primary_key=primary,
            nullable=False,
        ),
    ]


def col(name, size=36, *, nullable=True):
    return sa.Column(name, sa.String(size), nullable=nullable)


def timestamp(name, *, nullable=True):
    return sa.Column(name, sa.DateTime(), nullable=nullable)


def entity(name, *fields, constraints=()):
    op.create_table(
        name, sa.Column("id", sa.String(36), primary_key=True), *scope(), *fields, *constraints
    )


def upgrade():
    op.create_table(
        "knowledge_input_clocks",
        *scope(primary=True),
        sa.Column("observed_since", sa.Date(), nullable=False),
        sa.Column("last_new_confirmed_on", sa.Date()),
        sa.Column("input_revision", sa.Integer(), nullable=False),
    )
    dialect = op.get_bind().dialect.name
    day = (
        "DATE(DATE_ADD(UTC_TIMESTAMP(), INTERVAL 8 HOUR))"
        if dialect == "mysql"
        else "DATE('now','+8 hours')"
    )
    knowledge_day = (
        "DATE(DATE_ADD(k.created_at, INTERVAL 8 HOUR))"
        if dialect == "mysql"
        else "DATE(k.created_at,'+8 hours')"
    )
    op.execute(
        sa.text(f"""INSERT INTO knowledge_input_clocks
        (family_id,child_id,observed_since,last_new_confirmed_on,input_revision)
        SELECT c.family_id,c.id,{day},(SELECT MAX({knowledge_day}) FROM knowledge_items k
        WHERE k.family_id=c.family_id AND k.child_id=c.id),0 FROM children c""")
    )
    op.create_table(
        "learning_suggestion_states",
        *scope(primary=True),
        sa.Column("version", sa.Integer(), nullable=False),
        col("current_suggestion_id"),
        col("pending_task_id"),
        col("active_job_id"),
    )
    entity(
        "learning_suggestions",
        sa.Column("version", sa.Integer(), nullable=False),
        col("status", 20, nullable=False),
        col("subject_id", nullable=False),
        sa.Column("validated_content_json", sa.Text(), nullable=False),
        col("input_fingerprint", 64, nullable=False),
        timestamp("created_at", nullable=False),
        timestamp("expires_at", nullable=False),
        col("approved_by", 80),
        timestamp("approved_at"),
    )
    op.create_table(
        "learning_suggestion_prompt_days",
        *scope(primary=True),
        sa.Column("prompt_on", sa.Date(), primary_key=True),
        timestamp("consumed_at", nullable=False),
        col("consumed_by", 80, nullable=False),
        col("request_id", 100, nullable=False),
        timestamp("displayed_at"),
    )
    entity(
        "learning_suggestion_jobs",
        col("request_id", 100, nullable=False),
        col("state", 20, nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        timestamp("available_at", nullable=False),
        timestamp("lease_until"),
        col("lease_token"),
        sa.Column("input_revision", sa.Integer(), nullable=False),
        col("input_fingerprint", 64, nullable=False),
        sa.Column("bounded_context_json", sa.Text(), nullable=False),
        col("excluded_content_hash", 64),
        col("result_suggestion_id"),
        col("safe_error_code", 40),
        timestamp("created_at", nullable=False),
        timestamp("updated_at", nullable=False),
        constraints=[
            sa.UniqueConstraint(
                "family_id", "child_id", "request_id", name="uq_suggestion_job_request"
            )
        ],
    )
    entity(
        "study_tasks",
        sa.Column(
            "suggestion_id", sa.String(36), sa.ForeignKey("learning_suggestions.id"), nullable=False
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        col("state", 20, nullable=False),
        col("approved_by", 80, nullable=False),
        timestamp("approved_at", nullable=False),
        timestamp("last_partial_at"),
        timestamp("completed_at"),
        timestamp("removed_at"),
        constraints=[
            sa.UniqueConstraint(
                "family_id", "child_id", "suggestion_id", name="uq_study_task_suggestion"
            )
        ],
    )
    entity(
        "study_task_record_intents",
        sa.Column("task_id", sa.String(36), sa.ForeignKey("study_tasks.id"), nullable=False),
        sa.Column("task_version", sa.Integer(), nullable=False),
        col("mode", 10, nullable=False),
        col("created_by", 80, nullable=False),
        col("request_id", 100, nullable=False),
        col("submission_id"),
        col("state", 20, nullable=False),
        timestamp("created_at", nullable=False),
        timestamp("recovery_after", nullable=False),
        constraints=[
            sa.UniqueConstraint(
                "family_id", "child_id", "request_id", name="uq_study_intent_request"
            )
        ],
    )
    entity(
        "study_task_records",
        sa.Column("task_id", sa.String(36), sa.ForeignKey("study_tasks.id"), nullable=False),
        col("record_id", nullable=False),
        sa.Column(
            "intent_id",
            sa.String(36),
            sa.ForeignKey("study_task_record_intents.id"),
            nullable=False,
        ),
        timestamp("confirmed_at", nullable=False),
        timestamp("created_at", nullable=False),
        constraints=[
            sa.UniqueConstraint(
                "family_id", "child_id", "task_id", "record_id", name="uq_study_task_record"
            )
        ],
    )
    indexes = [
        (
            "ix_suggestions_history",
            "learning_suggestions",
            ["family_id", "child_id", "created_at", "id"],
        ),
        (
            "ix_suggestion_job_scope",
            "learning_suggestion_jobs",
            ["family_id", "child_id", "state", "created_at", "id"],
        ),
        ("ix_suggestion_job_family", "learning_suggestion_jobs", ["family_id", "state", "id"]),
        ("ix_suggestion_job_claim", "learning_suggestion_jobs", ["state", "available_at", "id"]),
        (
            "ix_suggestion_job_quota",
            "learning_suggestion_jobs",
            ["family_id", "child_id", "updated_at", "id"],
        ),
        (
            "ix_study_task_scope",
            "study_tasks",
            ["family_id", "child_id", "state", "approved_at", "id"],
        ),
        (
            "ix_study_intent_scope",
            "study_task_record_intents",
            ["family_id", "child_id", "state", "created_at", "id"],
        ),
        (
            "ix_study_intent_recovery",
            "study_task_record_intents",
            ["state", "recovery_after", "id"],
        ),
        ("ix_study_intent_cleanup", "study_task_record_intents", ["state", "created_at", "id"]),
        ("ix_suggestions_cleanup", "learning_suggestions", ["expires_at", "id"]),
        ("ix_suggestion_job_cleanup", "learning_suggestion_jobs", ["updated_at", "id"]),
        (
            "ix_suggestion_prompt_cleanup",
            "learning_suggestion_prompt_days",
            ["prompt_on", "family_id", "child_id"],
        ),
        (
            "ix_study_records_page",
            "study_task_records",
            ["family_id", "child_id", "task_id", "confirmed_at", "id"],
        ),
    ]
    for name, table, fields in indexes:
        op.create_index(name, table, fields)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT COUNT(*) FROM study_tasks")):
        raise RuntimeError("Cannot discard approved study tasks or their audit")
    for table in (
        "study_task_records",
        "study_task_record_intents",
        "study_tasks",
        "learning_suggestion_jobs",
        "learning_suggestion_prompt_days",
        "learning_suggestions",
        "learning_suggestion_states",
        "knowledge_input_clocks",
    ):
        op.drop_table(table)
