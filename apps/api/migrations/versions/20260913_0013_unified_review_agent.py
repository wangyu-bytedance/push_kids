"""add unified review projection, daily plans and history-search terms

Revision ID: 20260913_0013
Revises: 20260913_0012
Create Date: 2026-09-13
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "20260913_0013"
down_revision: str | Sequence[str] | None = "20260913_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    return re.sub(r"[\s，。！？、；：,.!?;:（）()\[\]]+", "", normalized)[:140]


def _terms(value: str) -> list[tuple[str, str]]:
    normalized = _normalize(value)
    if not normalized:
        return []
    ranked: list[tuple[str, str]] = [(normalized[:40], "exact")]
    words = re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", unicodedata.normalize("NFKC", value).lower())
    ranked.extend((word[:40], "token") for word in words if word)
    ranked.extend(
        (normalized[index : index + 3], "trigram") for index in range(max(0, len(normalized) - 2))
    )
    ranked.extend(
        (normalized[index : index + 2], "bigram") for index in range(max(0, len(normalized) - 1))
    )
    result: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for term, kind in ranked:
        key = (term, kind)
        if term and key not in seen:
            seen.add(key)
            result.append(key)
        if len(result) == 32:
            break
    return result


def upgrade() -> None:
    op.add_column("review_items", sa.Column("last_reviewed_on", sa.Date(), nullable=True))
    op.add_column(
        "review_items", sa.Column("review_count", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "review_items", sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column(
        "review_items", sa.Column("heat_milli", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "review_items", sa.Column("lapse_count", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "review_items",
        sa.Column(
            "policy_revision", sa.String(length=40), nullable=False, server_default="fixed_v1"
        ),
    )
    op.add_column(
        "review_items", sa.Column("state_version", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("review_feedback", sa.Column("reviewed_on", sa.Date(), nullable=True))
    op.add_column(
        "review_feedback",
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual"),
    )
    op.add_column(
        "review_feedback",
        sa.Column(
            "policy_revision", sa.String(length=40), nullable=False, server_default="fixed_v1"
        ),
    )
    for name, column_type in (
        ("before_step", sa.Integer()),
        ("after_step", sa.Integer()),
        ("before_interval_days", sa.Integer()),
        ("after_interval_days", sa.Integer()),
        ("before_due_date", sa.Date()),
        ("after_due_date", sa.Date()),
    ):
        op.add_column("review_feedback", sa.Column(name, column_type, nullable=True))

    bind = op.get_bind()
    date_expression = (
        "DATE(occurred_at)"
        if bind.dialect.name in {"mysql", "sqlite"}
        else "CAST(occurred_at AS DATE)"
    )
    op.execute(
        sa.text(
            "UPDATE review_feedback SET reviewed_on = CASE "
            f"WHEN action = 'defer' THEN NULL ELSE {date_expression} END"
        )
    )
    op.execute(
        sa.text(
            "UPDATE review_items SET review_count = ("
            "SELECT COUNT(*) FROM review_feedback "
            "WHERE review_feedback.review_item_id = review_items.id "
            "AND review_feedback.reviewed_on IS NOT NULL)"
        )
    )
    op.execute(
        sa.text(
            "UPDATE review_items SET last_reviewed_on = ("
            "SELECT MAX(reviewed_on) FROM review_feedback "
            "WHERE review_feedback.review_item_id = review_items.id)"
        )
    )

    op.drop_index("ix_review_items_family_child_active_due_id", table_name="review_items")
    op.create_index(
        "ix_review_items_family_child_active_due_last_id",
        "review_items",
        ["family_id", "child_id", "active", "due_date", "last_reviewed_on", "id"],
    )
    op.create_index("ix_review_feedback_reviewed_on", "review_feedback", ["reviewed_on"])

    op.create_table(
        "knowledge_search_terms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("subject_id", sa.String(length=36), nullable=False),
        sa.Column("knowledge_item_id", sa.String(length=36), nullable=False),
        sa.Column("term", sa.String(length=40), nullable=False),
        sa.Column("term_kind", sa.String(length=12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "family_id",
            "child_id",
            "subject_id",
            "knowledge_item_id",
            "term",
            "term_kind",
            name="uq_knowledge_search_term",
        ),
    )
    for column in ("family_id", "child_id", "subject_id", "knowledge_item_id"):
        op.create_index(f"ix_knowledge_search_terms_{column}", "knowledge_search_terms", [column])
    op.create_index(
        "ix_knowledge_search_terms_scope_term_item",
        "knowledge_search_terms",
        ["family_id", "child_id", "subject_id", "term", "knowledge_item_id"],
    )

    knowledge = sa.table(
        "knowledge_items",
        sa.column("id", sa.String),
        sa.column("family_id", sa.String),
        sa.column("child_id", sa.String),
        sa.column("subject_id", sa.String),
        sa.column("name", sa.String),
    )
    search_terms = sa.table(
        "knowledge_search_terms",
        sa.column("id", sa.String),
        sa.column("family_id", sa.String),
        sa.column("child_id", sa.String),
        sa.column("subject_id", sa.String),
        sa.column("knowledge_item_id", sa.String),
        sa.column("term", sa.String),
        sa.column("term_kind", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    rows = bind.execute(
        sa.select(
            knowledge.c.id,
            knowledge.c.family_id,
            knowledge.c.child_id,
            knowledge.c.subject_id,
            knowledge.c.name,
        )
    ).mappings()
    batch: list[dict[str, object]] = []
    for row in rows:
        batch.extend(
            {
                "id": str(uuid.uuid4()),
                "family_id": row["family_id"],
                "child_id": row["child_id"],
                "subject_id": row["subject_id"],
                "knowledge_item_id": row["id"],
                "term": term,
                "term_kind": kind,
                "created_at": datetime.now(UTC),
            }
            for term, kind in _terms(str(row["name"]))
        )
        if len(batch) >= 1000:
            op.bulk_insert(search_terms, batch)
            batch = []
    if batch:
        op.bulk_insert(search_terms, batch)

    op.create_table(
        "daily_review_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("budget_minutes", sa.Integer(), nullable=False),
        sa.Column("total_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("earliest_due", sa.Date(), nullable=True),
        sa.Column(
            "policy_revision", sa.String(length=40), nullable=False, server_default="daily-plan-v1"
        ),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("family_id", "child_id", "plan_date", name="uq_daily_review_plan_day"),
    )
    op.create_index("ix_daily_review_plans_family_id", "daily_review_plans", ["family_id"])
    op.create_index("ix_daily_review_plans_child_id", "daily_review_plans", ["child_id"])
    op.create_index(
        "ix_daily_review_plans_family_child_date",
        "daily_review_plans",
        ["family_id", "child_id", "plan_date"],
    )
    op.create_table(
        "daily_review_plan_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("review_item_id", sa.String(length=36), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["daily_review_plans.id"]),
        sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "review_item_id", name="uq_daily_plan_review"),
    )
    for column in ("family_id", "child_id"):
        op.create_index(f"ix_daily_review_plan_items_{column}", "daily_review_plan_items", [column])
    op.create_index(
        "ix_daily_plan_items_plan_ordinal",
        "daily_review_plan_items",
        ["plan_id", "ordinal", "id"],
    )
    op.create_index(
        "ix_daily_plan_items_review_plan",
        "daily_review_plan_items",
        ["review_item_id", "plan_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_daily_plan_items_review_plan", table_name="daily_review_plan_items")
    op.drop_index("ix_daily_plan_items_plan_ordinal", table_name="daily_review_plan_items")
    op.drop_index("ix_daily_review_plan_items_child_id", table_name="daily_review_plan_items")
    op.drop_index("ix_daily_review_plan_items_family_id", table_name="daily_review_plan_items")
    op.drop_table("daily_review_plan_items")
    op.drop_index("ix_daily_review_plans_family_child_date", table_name="daily_review_plans")
    op.drop_index("ix_daily_review_plans_child_id", table_name="daily_review_plans")
    op.drop_index("ix_daily_review_plans_family_id", table_name="daily_review_plans")
    op.drop_table("daily_review_plans")
    op.drop_index("ix_knowledge_search_terms_scope_term_item", table_name="knowledge_search_terms")
    for column in ("knowledge_item_id", "subject_id", "child_id", "family_id"):
        op.drop_index(f"ix_knowledge_search_terms_{column}", table_name="knowledge_search_terms")
    op.drop_table("knowledge_search_terms")
    op.drop_index("ix_review_feedback_reviewed_on", table_name="review_feedback")
    op.drop_index("ix_review_items_family_child_active_due_last_id", table_name="review_items")
    op.create_index(
        "ix_review_items_family_child_active_due_id",
        "review_items",
        ["family_id", "child_id", "active", "due_date", "id"],
    )
    for name in (
        "after_due_date",
        "before_due_date",
        "after_interval_days",
        "before_interval_days",
        "after_step",
        "before_step",
        "policy_revision",
        "source",
        "reviewed_on",
    ):
        op.drop_column("review_feedback", name)
    for name in (
        "state_version",
        "policy_revision",
        "lapse_count",
        "heat_milli",
        "interval_days",
        "review_count",
        "last_reviewed_on",
    ):
        op.drop_column("review_items", name)
