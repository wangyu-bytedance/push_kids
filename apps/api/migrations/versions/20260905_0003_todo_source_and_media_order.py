"""todo source provenance, media order, recognition evidence and subject origin

Revision ID: 20260905_0003
Revises: 20260905_0002
Create Date: 2026-09-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260905_0003"
down_revision: str | Sequence[str] | None = "20260905_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()

    # SQLite cannot ALTER a table to add a constraint, so the column and its foreign key are
    # created through batch mode, which recreates the table on SQLite and is a plain ALTER
    # on MySQL.
    with op.batch_alter_table("review_items") as batch_op:
        batch_op.add_column(sa.Column("source_submission_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_review_items_source_submission_id",
            "learning_submissions",
            ["source_submission_id"],
            ["id"],
        )
    op.create_index(
        op.f("ix_review_items_source_submission_id"),
        "review_items",
        ["source_submission_id"],
        unique=False,
    )

    op.add_column(
        "submission_media",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        op.f("ix_submission_media_sort_order"), "submission_media", ["sort_order"], unique=False
    )

    op.add_column("knowledge_items", sa.Column("confidence", sa.String(length=10), nullable=True))
    op.add_column("knowledge_items", sa.Column("evidence_json", sa.Text(), nullable=True))

    op.add_column(
        "subjects", sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="1")
    )

    # Backfill 1: the earliest occurrence of a knowledge item names the first source submission.
    connection.execute(
        sa.text(
            "UPDATE review_items SET source_submission_id = ("
            "  SELECT lr.submission_id FROM knowledge_occurrences ko"
            "  JOIN learning_records lr ON lr.id = ko.learning_record_id"
            "  WHERE ko.knowledge_item_id = review_items.knowledge_item_id"
            "    AND ko.family_id = review_items.family_id"
            "    AND lr.family_id = review_items.family_id"
            "  ORDER BY ko.occurred_at, ko.created_at, ko.id"
            "  LIMIT 1"
            ") WHERE source_submission_id IS NULL"
        )
    )

    # Backfill 2: existing photos keep their historical upload order as stable positions.
    rows = connection.execute(
        sa.text(
            "SELECT id, submission_id FROM submission_media ORDER BY submission_id, created_at, id"
        )
    ).all()
    position: dict[str, int] = {}
    for media_id, submission_id in rows:
        index = position.get(submission_id, 0)
        connection.execute(
            sa.text("UPDATE submission_media SET sort_order = :sort_order WHERE id = :id"),
            {"sort_order": index, "id": media_id},
        )
        position[submission_id] = index + 1

    # Backfill 3: the preset learning catalog is not parent-built. No knowledge_items backfill:
    # confidence and evidence only exist for confirmations made after this revision.
    connection.execute(
        sa.text(
            "UPDATE subjects SET is_custom = 0 "
            "WHERE kind = 'learning' AND name IN ('语文', '数学', '英语')"
        )
    )
    connection.execute(
        sa.text(
            "UPDATE subjects SET is_custom = 1 "
            "WHERE NOT (kind = 'learning' AND name IN ('语文', '数学', '英语'))"
        )
    )


def downgrade() -> None:
    op.drop_column("subjects", "is_custom")
    op.drop_column("knowledge_items", "evidence_json")
    op.drop_column("knowledge_items", "confidence")
    op.drop_index(op.f("ix_submission_media_sort_order"), table_name="submission_media")
    op.drop_column("submission_media", "sort_order")
    op.drop_index(op.f("ix_review_items_source_submission_id"), table_name="review_items")
    with op.batch_alter_table("review_items") as batch_op:
        batch_op.drop_constraint("fk_review_items_source_submission_id", type_="foreignkey")
        batch_op.drop_column("source_submission_id")
