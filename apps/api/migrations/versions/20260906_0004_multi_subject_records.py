"""one submission may hold several subject records

A single photo batch often mixes subjects (数学 homework plus 语文 dictation). Before this
revision a submission could only produce one learning record, which forced the confirmation flow
to invent a merged subject such as "数学、语文". Records now stay one-per-subject, so the unique
constraint on learning_records.submission_id becomes a plain index.

Revision ID: 20260906_0004
Revises: 20260905_0003
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0004"
down_revision: str | Sequence[str] | None = "20260905_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEX_NAME = "ix_learning_records_submission_id"
# MySQL names the inline UNIQUE index of `sa.UniqueConstraint("submission_id")` after the column.
MYSQL_UNIQUE_NAME = "submission_id"


def _learning_records(*, unique: bool) -> sa.Table:
    """The table as it exists on disk, used by SQLite batch mode to recreate it."""
    return sa.Table(
        "learning_records",
        sa.MetaData(),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False, index=True),
        sa.Column("child_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("subject_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["learning_submissions.id"]),
        sa.PrimaryKeyConstraint("id"),
        *([sa.UniqueConstraint("submission_id")] if unique else []),
    )


def _has_index(name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(index["name"] == name for index in inspector.get_indexes("learning_records"))


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        # SQLite cannot drop an unnamed table-level constraint, so the table is recreated from the
        # target definition. Batch mode copies the rows and rebuilds the remaining indexes.
        with op.batch_alter_table(
            "learning_records",
            recreate="always",
            copy_from=_learning_records(unique=False),
        ):
            pass
    else:
        if _has_index(MYSQL_UNIQUE_NAME):
            op.drop_index(MYSQL_UNIQUE_NAME, table_name="learning_records")
    if not _has_index(INDEX_NAME):
        op.create_index(INDEX_NAME, "learning_records", ["submission_id"], unique=False)


def downgrade() -> None:
    # Downgrade only restores the shape; it fails loudly if a submission already holds several
    # records, because collapsing them would silently destroy confirmed learning history.
    connection = op.get_bind()
    duplicated = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM (SELECT submission_id FROM learning_records "
            "GROUP BY submission_id HAVING COUNT(*) > 1) AS multi"
        )
    ).scalar()
    if duplicated:
        raise RuntimeError(
            "cannot restore the unique constraint: "
            f"{duplicated} submission(s) already hold several subject records"
        )
    if _has_index(INDEX_NAME):
        op.drop_index(INDEX_NAME, table_name="learning_records")
    if connection.dialect.name == "sqlite":
        with op.batch_alter_table(
            "learning_records",
            recreate="always",
            copy_from=_learning_records(unique=True),
        ):
            pass
    else:
        op.create_index(MYSQL_UNIQUE_NAME, "learning_records", ["submission_id"], unique=True)
