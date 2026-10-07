"""Pure, bounded daily selection with subject, first-review and waiting fairness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

DAILY_REVIEW_POLICY_REVISION = "daily-plan-fair-v2"
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
    review_count: int = 0
    missed_plan_days: int = 0
    waiting_since: date | None = None
    subject_last_offered_on: date | None = None

    @property
    def bounded_minutes(self) -> int:
        return min(5, max(1, self.estimated_minutes))


def candidate_priority(row: ReviewSelectionCandidate) -> tuple:
    """Aging applies within both the coverage round and the first/repeat pools."""
    return (
        -min(3, max(0, row.missed_plan_days)),
        row.waiting_since or row.due_date,
        row.due_date,
        row.last_reviewed_on is not None,
        row.last_reviewed_on or date.min,
        row.review_id,
    )


def select_daily_reviews(
    candidates: list[ReviewSelectionCandidate],
    *,
    budget_minutes: int,
) -> list[ReviewSelectionCandidate]:
    """Reservations, affordable subject coverage, then balanced first/repeat opportunities."""
    selected: list[ReviewSelectionCandidate] = []
    seen: set[str] = set()
    used = 0
    counts = [0, 0]
    budget = min(120, max(0, budget_minutes))
    ordered = sorted({r.review_id: r for r in candidates}.values(), key=candidate_priority)

    def add(row: ReviewSelectionCandidate) -> None:
        nonlocal used
        selected.append(row)
        seen.add(row.review_id)
        used += row.bounded_minutes
        if not row.manually_scheduled:
            counts[int(row.review_count > 0)] += 1

    for row in sorted(
        (r for r in ordered if r.manually_scheduled), key=lambda r: (r.due_date, r.review_id)
    )[:DAILY_REVIEW_CANDIDATE_LIMIT]:
        add(row)
    covered = {r.subject_id for r in selected}
    subjects: dict[str, list[ReviewSelectionCandidate]] = {}
    for row in ordered:
        if not row.manually_scheduled and row.subject_id not in covered:
            subjects.setdefault(row.subject_id, []).append(row)
    groups = sorted(
        subjects.values(),
        key=lambda rows: (
            rows[0].subject_last_offered_on or date.min,
            -max(r.missed_plan_days for r in rows),
            min(r.waiting_since or r.due_date for r in rows),
            rows[0].subject_id,
        ),
    )
    groups = groups[:DAILY_REVIEW_CANDIDATE_LIMIT]
    minima = [min(r.bounded_minutes for r in rows) for rows in groups]
    reserve_all = sum(minima) <= budget - used
    reserved = sum(minima) if reserve_all else 0
    for rows, minimum in zip(groups, minima, strict=True):
        if len(selected) >= DAILY_REVIEW_CANDIDATE_LIMIT:
            break
        if reserve_all:
            reserved -= minimum
        available = budget - used - reserved
        pick = next((r for r in rows if r.bounded_minutes <= available), None)
        if pick is not None:
            add(pick)
    pools = [
        [r for r in ordered if not r.manually_scheduled and (r.review_count > 0) == kind]
        for kind in (False, True)
    ]
    while used < budget and len(selected) < DAILY_REVIEW_CANDIDATE_LIMIT:
        preferred = 0 if counts[0] <= counts[1] else 1
        pick = None
        for kind in (preferred, 1 - preferred):
            pick = next(
                (
                    r
                    for r in pools[kind]
                    if r.review_id not in seen and r.bounded_minutes <= budget - used
                ),
                None,
            )
            if pick is not None:
                break
        if pick is None:
            break
        add(pick)
    return selected
