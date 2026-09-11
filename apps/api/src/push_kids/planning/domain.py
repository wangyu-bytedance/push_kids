from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

REVIEW_INTERVALS = (1, 3, 7, 14, 30, 60)
FeedbackAction = Literal["complete", "reinforce", "partial", "defer"]


@dataclass(frozen=True)
class ReviewTransition:
    step: int
    due_date: date
    active: bool = True


def initial_review_date(learned_on: date, today: date) -> date:
    proposed = learned_on + timedelta(days=REVIEW_INTERVALS[0])
    return max(proposed, today)


def apply_feedback(step: int, action: FeedbackAction, today: date) -> ReviewTransition:
    if action == "complete":
        next_step = min(step + 1, len(REVIEW_INTERVALS))
        if next_step >= len(REVIEW_INTERVALS):
            return ReviewTransition(step=next_step, due_date=today, active=False)
        return ReviewTransition(next_step, today + timedelta(days=REVIEW_INTERVALS[next_step]))
    if action == "partial":
        next_step = min(step + 1, len(REVIEW_INTERVALS) - 1)
        return ReviewTransition(
            next_step, today + timedelta(days=max(1, REVIEW_INTERVALS[next_step] // 2))
        )
    if action == "reinforce":
        return ReviewTransition(max(0, step - 1), today + timedelta(days=1))
    if action == "defer":
        return ReviewTransition(step, today + timedelta(days=1))
    raise ValueError(f"unknown feedback: {action}")


@dataclass(frozen=True)
class DueKnowledge:
    review_id: str
    subject_id: str
    subject_name: str
    knowledge_name: str
    review_method: str
    estimated_minutes: int
    due_date: date
    # Provenance of the Todo, supplied by the service layer; the client renders the wording.
    source_submission_id: str | None = None
    source_occurred_on: date | None = None
    review_round: int = 1
    interval_days: int | None = None


def review_interval_days(
    due_date: date, last_reviewed_on: date | None, source_occurred_on: date | None
) -> int | None:
    """Deterministic gap between this due date and the previous review or first learning."""
    anchor = last_reviewed_on or source_occurred_on
    if anchor is None:
        return None
    return (due_date - anchor).days


def group_daily_todos(
    items: list[DueKnowledge], budget_minutes: int, *, starting_minutes: int = 0
) -> list[dict]:
    groups: dict[tuple[str, str, str, bool], dict] = {}
    used = max(0, starting_minutes)
    for item in sorted(
        items,
        key=lambda value: (
            value.due_date,
            value.subject_name,
            value.review_method,
            value.review_id,
        ),
    ):
        minutes = max(1, item.estimated_minutes)
        optional = used + minutes > budget_minutes
        key = (item.subject_id, item.subject_name, item.review_method, optional)
        group_kind = "optional" if optional else "required"
        group = groups.setdefault(
            key,
            {
                "id": f"{item.subject_id}:{item.review_method}:{group_kind}",
                "subject_id": item.subject_id,
                "subject_name": item.subject_name,
                "review_method": item.review_method,
                "estimated_minutes": 0,
                "optional": optional,
                "items": [],
            },
        )
        group["estimated_minutes"] += minutes
        group["optional"] = group["optional"] and optional
        group["items"].append(
            {
                "review_id": item.review_id,
                "knowledge_name": item.knowledge_name,
                "due_date": item.due_date.isoformat(),
                "source_submission_id": item.source_submission_id,
                "source_occurred_on": item.source_occurred_on.isoformat()
                if item.source_occurred_on
                else None,
                "review_round": item.review_round,
                "interval_days": item.interval_days,
            }
        )
        used += minutes
    return list(groups.values())
