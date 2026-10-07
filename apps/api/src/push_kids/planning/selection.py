"""Pure, bounded daily-plan selection ordered by due and last actual review."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

DAILY_REVIEW_POLICY_REVISION = "daily-plan-v1"
DAILY_REVIEW_CANDIDATE_LIMIT = 120


@dataclass(frozen=True)
class ReviewSelectionCandidate:
    review_id: str
    knowledge_id: str
    subject_id: str
    subject_name: str
    knowledge_name: str
    review_method: str
    estimated_minutes: int
    due_date: date
    last_reviewed_on: date | None = None
    review_step: int = 0
    last_feedback: str | None = None
    source_submission_id: str | None = None
    source_occurred_on: date | None = None
    source_summary: str | None = None
    source_image_index: int | None = None
    review_round: int = 1
    interval_days: int | None = None
    manually_scheduled: bool = False

    @property
    def bounded_minutes(self) -> int:
        return min(5, max(1, self.estimated_minutes))


def select_daily_reviews(
    candidates: list[ReviewSelectionCandidate],
    *,
    budget_minutes: int,
) -> list[ReviewSelectionCandidate]:
    """Take the oldest due prefix that fits the child's bounded minute budget."""
    selected: list[ReviewSelectionCandidate] = []
    used = 0
    ordered = sorted(
        candidates,
        key=lambda row: (
            not row.manually_scheduled,
            row.due_date,
            row.last_reviewed_on is not None,
            row.last_reviewed_on or date.min,
            row.review_id,
        ),
    )
    for row in ordered:
        if not row.manually_scheduled and used + row.bounded_minutes > max(0, budget_minutes):
            continue
        selected.append(row)
        used += row.bounded_minutes
        if len(selected) >= DAILY_REVIEW_CANDIDATE_LIMIT:
            break
    return selected
