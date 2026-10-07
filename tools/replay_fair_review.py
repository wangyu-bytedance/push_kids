"""Deterministic synthetic replay; prints aggregates only, never reads a real family."""

import json
from dataclasses import replace
from datetime import date, timedelta

from push_kids.planning.policies import ReviewState, apply_review_event
from push_kids.planning.selection import ReviewSelectionCandidate, select_daily_reviews


def replay(subjects: int, completion: str, fair: bool) -> dict:
    today = date(2026, 10, 7)
    candidates = []
    states = {}
    for subject in range(subjects):
        for index in range(140 if subject == 0 else 8):
            rid = f"s{subject:03}-r{index:03}"
            row = ReviewSelectionCandidate(
                review_id=rid,
                knowledge_id=rid,
                subject_id=f"s{subject:03}",
                subject_name="synthetic",
                knowledge_name="synthetic",
                review_method="synthetic",
                estimated_minutes=3,
                due_date=today - timedelta(days=10 - subject % 10),
                review_count=index % 2,
                waiting_since=today,
            )
            candidates.append(row)
            states[rid] = ReviewState(
                step=0, due_date=row.due_date, active=True, review_count=row.review_count
            )
    return simulate(candidates, states, today=today, budget=30, completion=completion, fair=fair)


def simulate(candidates, states, *, today, budget, completion, fair):
    """Simulate supplied in-memory facts; return only aggregate, non-identifying results."""
    states = dict(states)
    offered = {}
    subject_offered = {}
    initial_first = {r.review_id for r in candidates if not r.review_count}
    waits = []
    missing = 0
    total_minutes = 0
    duplicate_count = 0
    exceeded_count = 0
    for offset in range(28):
        day = today + timedelta(days=offset)
        eligible = []
        for row in candidates:
            state = states[row.review_id]
            if not state.active or state.due_date > day:
                continue
            anchor = max(
                today,
                state.due_date,
                offered.get(row.review_id, today - timedelta(days=1)) + timedelta(days=1),
            )
            wait = max(0, (day - anchor).days)
            waits.append(wait)
            eligible.append(
                replace(
                    row,
                    due_date=state.due_date,
                    review_count=state.review_count,
                    last_reviewed_on=state.last_reviewed_on,
                    waiting_since=anchor,
                    missed_plan_days=min(3, wait),
                    subject_last_offered_on=subject_offered.get(row.subject_id),
                )
            )
        if fair:
            chosen = select_daily_reviews(eligible, budget_minutes=budget)
        else:
            ordered = sorted(
                eligible, key=lambda r: (r.due_date, r.last_reviewed_on or date.min, r.review_id)
            )[:120]
            chosen = []
            used = 0
            for row in ordered:
                if used + row.bounded_minutes <= budget:
                    chosen.append(row)
                    used += row.bounded_minutes
        missing += len({r.subject_id for r in eligible} - {r.subject_id for r in chosen})
        minutes = sum(r.bounded_minutes for r in chosen)
        total_minutes += minutes
        exceeded_count += int(minutes > budget)
        duplicate_count += len(chosen) - len({r.review_id for r in chosen})
        for index, row in enumerate(chosen):
            offered[row.review_id] = day
            subject_offered[row.subject_id] = day
            if completion == "all" or completion == "half" and index % 2 == 0:
                change = apply_review_event(states[row.review_id], "complete", day)
                values = dict(change.__dict__)
                values.pop("advanced")
                states[row.review_id] = ReviewState(**values)
    waits.sort()
    return dict(
        subjects=len({r.subject_id for r in candidates}),
        completion=completion,
        policy="fair-v2" if fair else "old-v1",
        days=28,
        missing_subject_days=missing,
        initial_first_never_offered=len(initial_first - offered.keys()),
        initial_first_never_reviewed=sum(states[r].review_count == 0 for r in initial_first),
        max_wait_plan_days=max(waits, default=0),
        p95_wait_plan_days=waits[int((len(waits) - 1) * 0.95)] if waits else 0,
        selected_minutes=total_minutes,
        duplicates=duplicate_count,
        over_budget_days=exceeded_count,
    )


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "assumptions": (
                    "Synthetic fixed backlog, 28 daily plans, 30 minutes, no new intake; "
                    "half means half the selected items receive complete feedback. "
                    "This is not a replay of actual family history."
                ),
                "results": [
                    replay(subjects, completion, fair)
                    for subjects in (3, 10)
                    for completion in ("all", "half", "none")
                    for fair in (False, True)
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
