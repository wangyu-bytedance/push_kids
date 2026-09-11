"""weekday-specific activity and travel time slots

Revision ID: 20260911_0010
Revises: 20260907_0009
Create Date: 2026-09-11
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import time
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "20260911_0010"
down_revision: str | Sequence[str] | None = "20260907_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _weekdays(raw: str | None, parent_id: str) -> list[int]:
    try:
        values = [int(value) for value in (raw or "").split(",") if value != ""]
    except ValueError as exc:
        raise RuntimeError(f"invalid legacy weekdays for parent {parent_id}") from exc
    if len(values) != len(set(values)) or any(value < 0 or value > 6 for value in values):
        raise RuntimeError(f"invalid legacy weekdays for parent {parent_id}")
    return sorted(values)


def _validate_range(start: time | None, end: time | None, parent_id: str) -> None:
    if start is None or end is None or end <= start:
        raise RuntimeError(f"invalid legacy time range for parent {parent_id}")


def _parent_tables():
    activity = sa.table(
        "activity_schedules",
        sa.column("id", sa.String(36)),
        sa.column("family_id", sa.String(80)),
        sa.column("child_id", sa.String(36)),
        sa.column("weekdays", sa.String(30)),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )
    travel = sa.table(
        "travel_arrangements",
        sa.column("id", sa.String(36)),
        sa.column("family_id", sa.String(80)),
        sa.column("child_id", sa.String(36)),
        sa.column("weekdays", sa.String(30)),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )
    return activity, travel


def upgrade() -> None:
    op.create_table(
        "activity_schedule_slots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("schedule_id", sa.String(length=36), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_activity_slot_weekday"),
        sa.CheckConstraint("end_time > start_time", name="ck_activity_slot_time_range"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_id"], ["activity_schedules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("schedule_id", "weekday", name="uq_activity_schedule_slot_weekday"),
    )
    for column in ("family_id", "child_id", "schedule_id", "weekday"):
        op.create_index(
            op.f(f"ix_activity_schedule_slots_{column}"),
            "activity_schedule_slots",
            [column],
        )

    op.create_table(
        "travel_arrangement_slots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("family_id", sa.String(length=80), nullable=False),
        sa.Column("child_id", sa.String(length=36), nullable=False),
        sa.Column("arrangement_id", sa.String(length=36), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_travel_slot_weekday"),
        sa.CheckConstraint("end_time > start_time", name="ck_travel_slot_time_range"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["arrangement_id"], ["travel_arrangements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("arrangement_id", "weekday", name="uq_travel_arrangement_slot_weekday"),
    )
    for column in ("family_id", "child_id", "arrangement_id", "weekday"):
        op.create_index(
            op.f(f"ix_travel_arrangement_slots_{column}"),
            "travel_arrangement_slots",
            [column],
        )

    connection = op.get_bind()
    activity_parent, travel_parent = _parent_tables()
    activity_slots = sa.table(
        "activity_schedule_slots",
        sa.column("id", sa.String(36)),
        sa.column("family_id", sa.String(80)),
        sa.column("child_id", sa.String(36)),
        sa.column("schedule_id", sa.String(36)),
        sa.column("weekday", sa.Integer()),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )
    travel_slots = sa.table(
        "travel_arrangement_slots",
        sa.column("id", sa.String(36)),
        sa.column("family_id", sa.String(80)),
        sa.column("child_id", sa.String(36)),
        sa.column("arrangement_id", sa.String(36)),
        sa.column("weekday", sa.Integer()),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )

    activity_values = []
    for row in connection.execute(sa.select(activity_parent)).mappings():
        days = _weekdays(row["weekdays"], row["id"])
        if not days:
            if row["start_time"] is not None or row["end_time"] is not None:
                raise RuntimeError(f"invalid flexible activity parent {row['id']}")
            continue
        _validate_range(row["start_time"], row["end_time"], row["id"])
        activity_values.extend(
            {
                "id": str(uuid4()),
                "family_id": row["family_id"],
                "child_id": row["child_id"],
                "schedule_id": row["id"],
                "weekday": weekday,
                "start_time": row["start_time"],
                "end_time": row["end_time"],
            }
            for weekday in days
        )

    travel_values = []
    for row in connection.execute(sa.select(travel_parent)).mappings():
        days = _weekdays(row["weekdays"], row["id"])
        if not days:
            raise RuntimeError(f"invalid empty travel parent {row['id']}")
        _validate_range(row["start_time"], row["end_time"], row["id"])
        travel_values.extend(
            {
                "id": str(uuid4()),
                "family_id": row["family_id"],
                "child_id": row["child_id"],
                "arrangement_id": row["id"],
                "weekday": weekday,
                "start_time": row["start_time"],
                "end_time": row["end_time"],
            }
            for weekday in days
        )
    if activity_values:
        connection.execute(activity_slots.insert(), activity_values)
    if travel_values:
        connection.execute(travel_slots.insert(), travel_values)


def _restore_uniform_parent_values(connection, parent, slots, parent_key: str) -> None:
    grouped: dict[str, list[tuple[int, time, time]]] = {}
    for row in connection.execute(sa.select(slots)).mappings():
        grouped.setdefault(row[parent_key], []).append(
            (row["weekday"], row["start_time"], row["end_time"])
        )
    for parent_id, values in grouped.items():
        ranges = {(start, end) for _, start, end in values}
        if len(ranges) != 1:
            raise RuntimeError(f"cannot downgrade mixed weekday times for parent {parent_id}")
        start, end = next(iter(ranges))
        weekdays = ",".join(str(weekday) for weekday, _, _ in sorted(values))
        connection.execute(
            parent.update()
            .where(parent.c.id == parent_id)
            .values(weekdays=weekdays, start_time=start, end_time=end)
        )


def downgrade() -> None:
    connection = op.get_bind()
    activity_parent, travel_parent = _parent_tables()
    activity_slots = sa.table(
        "activity_schedule_slots",
        sa.column("schedule_id", sa.String(36)),
        sa.column("weekday", sa.Integer()),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )
    travel_slots = sa.table(
        "travel_arrangement_slots",
        sa.column("arrangement_id", sa.String(36)),
        sa.column("weekday", sa.Integer()),
        sa.column("start_time", sa.Time()),
        sa.column("end_time", sa.Time()),
    )
    _restore_uniform_parent_values(connection, activity_parent, activity_slots, "schedule_id")
    _restore_uniform_parent_values(connection, travel_parent, travel_slots, "arrangement_id")

    for column in ("weekday", "arrangement_id", "child_id", "family_id"):
        op.drop_index(
            op.f(f"ix_travel_arrangement_slots_{column}"),
            table_name="travel_arrangement_slots",
        )
    op.drop_table("travel_arrangement_slots")
    for column in ("weekday", "schedule_id", "child_id", "family_id"):
        op.drop_index(
            op.f(f"ix_activity_schedule_slots_{column}"),
            table_name="activity_schedule_slots",
        )
    op.drop_table("activity_schedule_slots")
