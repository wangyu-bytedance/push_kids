from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_CEILING, Decimal, localcontext
from typing import Literal

CURVE_HEAT_POLICY_REVISION = "curve_heat_v1"
CURVE_INTERVALS = (1, 3, 7, 14, 30, 60, 90)
ReviewEventAction = Literal["observed", "complete", "partial", "reinforce", "defer"]


@dataclass(frozen=True)
class ReviewState:
    step: int
    due_date: date
    active: bool
    last_reviewed_on: date | None = None
    review_count: int = 0
    interval_days: int = 1
    heat_milli: int = 0
    lapse_count: int = 0
    state_version: int = 0


@dataclass(frozen=True)
class ReviewPolicyTransition:
    step: int
    due_date: date
    active: bool
    last_reviewed_on: date | None
    review_count: int
    interval_days: int
    heat_milli: int
    lapse_count: int
    state_version: int
    advanced: bool


def initial_review_state(learned_on: date, today: date) -> ReviewPolicyTransition:
    due = max(learned_on + timedelta(days=CURVE_INTERVALS[0]), today)
    return ReviewPolicyTransition(
        step=0,
        due_date=due,
        active=True,
        last_reviewed_on=None,
        review_count=0,
        interval_days=CURVE_INTERVALS[0],
        heat_milli=0,
        lapse_count=0,
        state_version=0,
        advanced=False,
    )


def apply_review_event(
    state: ReviewState,
    action: ReviewEventAction,
    reviewed_on: date,
) -> ReviewPolicyTransition:
    """Apply the approved deterministic curve/heat policy to one confirmed event."""
    if action == "defer":
        return ReviewPolicyTransition(
            **state.__dict__,
            advanced=False,
        )

    older_day = bool(state.last_reviewed_on and reviewed_on < state.last_reviewed_on)
    if older_day:
        # Historical backfill is an audit fact and count, never a projection rewind.
        return ReviewPolicyTransition(
            step=state.step,
            due_date=state.due_date,
            active=state.active,
            last_reviewed_on=state.last_reviewed_on,
            review_count=state.review_count + 1,
            interval_days=state.interval_days,
            heat_milli=state.heat_milli,
            lapse_count=state.lapse_count,
            state_version=state.state_version + 1,
            advanced=False,
        )

    same_day = state.last_reviewed_on == reviewed_on
    if same_day:
        # A second neutral/success event cannot accelerate the curve. A same-day partial or
        # reinforce signal may only make the projection more conservative.
        if action not in {"partial", "reinforce"}:
            return ReviewPolicyTransition(
                step=state.step,
                due_date=state.due_date,
                active=state.active,
                last_reviewed_on=state.last_reviewed_on,
                review_count=state.review_count + 1,
                interval_days=state.interval_days,
                heat_milli=state.heat_milli,
                lapse_count=state.lapse_count,
                state_version=state.state_version + 1,
                advanced=False,
            )
        conservative_interval = (
            1
            if action == "reinforce"
            else max(1, CURVE_INTERVALS[min(max(0, state.step), len(CURVE_INTERVALS) - 1)] // 2)
        )
        conservative_due = reviewed_on + timedelta(days=conservative_interval)
        due_date = min(state.due_date, conservative_due)
        return ReviewPolicyTransition(
            step=max(0, state.step - 1) if action == "reinforce" else state.step,
            due_date=due_date,
            active=True,
            last_reviewed_on=state.last_reviewed_on,
            review_count=state.review_count + 1,
            interval_days=max(1, (due_date - reviewed_on).days),
            heat_milli=state.heat_milli,
            lapse_count=state.lapse_count + (1 if action == "reinforce" else 0),
            state_version=state.state_version + 1,
            advanced=due_date < state.due_date or action == "reinforce",
        )

    elapsed = max(
        1,
        (reviewed_on - state.last_reviewed_on).days
        if state.last_reviewed_on
        else state.interval_days,
    )
    heat_milli = _next_heat_milli(state.heat_milli, elapsed)

    if action == "reinforce":
        next_step = max(0, state.step - 1)
        next_interval = 1
        lapse_count = state.lapse_count + 1
        active = True
    elif action == "partial":
        next_step = min(max(0, state.step), len(CURVE_INTERVALS) - 1)
        next_interval = max(1, CURVE_INTERVALS[next_step] // 2)
        lapse_count = state.lapse_count
        active = True
    else:
        next_step = min(max(0, state.step) + 1, len(CURVE_INTERVALS))
        lapse_count = state.lapse_count
        if next_step >= len(CURVE_INTERVALS) - 1:
            next_interval = CURVE_INTERVALS[-1]
            active = False
        else:
            next_interval = _adjusted_interval(
                CURVE_INTERVALS[next_step],
                heat_milli,
                elapsed,
                max(1, state.interval_days),
            )
            active = True

    return ReviewPolicyTransition(
        step=next_step,
        due_date=reviewed_on + timedelta(days=next_interval),
        active=active,
        last_reviewed_on=reviewed_on,
        review_count=state.review_count + 1,
        interval_days=next_interval,
        heat_milli=heat_milli,
        lapse_count=lapse_count,
        state_version=state.state_version + 1,
        advanced=True,
    )


def _next_heat_milli(old_heat_milli: int, elapsed: int) -> int:
    with localcontext() as context:
        context.prec = 28
        heat = Decimal(max(0, old_heat_milli)) / Decimal(1000)
        decay = Decimal(2) ** (Decimal(-min(elapsed, 36500)) / Decimal(14))
        value = min(Decimal(5), heat * decay + Decimal(1))
        return int((value * Decimal(1000)).to_integral_value())


def _adjusted_interval(
    base_interval: int,
    heat_milli: int,
    elapsed: int,
    previous_interval: int,
) -> int:
    with localcontext() as context:
        context.prec = 28
        heat = Decimal(heat_milli) / Decimal(1000)
        heat_factor = Decimal(1) + min(
            Decimal("0.25"), max(Decimal(0), heat - Decimal(1)) * Decimal("0.05")
        )
        spacing_ratio = min(
            Decimal("1.5"),
            max(Decimal("0.5"), Decimal(elapsed) / Decimal(previous_interval)),
        )
        spacing_factor = spacing_ratio.sqrt()
        value = Decimal(base_interval) * heat_factor * spacing_factor
        rounded = int(value.to_integral_value(rounding=ROUND_CEILING))
    return min(180, max(1, rounded))
