from datetime import date, timedelta

from push_kids.planning.policies import (
    CURVE_HEAT_POLICY_REVISION,
    ReviewState,
    apply_review_event,
    initial_review_state,
)


def test_initial_state_schedules_a_check_without_counting_a_review() -> None:
    learned_on = date(2026, 9, 10)

    state = initial_review_state(learned_on, date(2026, 9, 13))

    assert state.due_date == date(2026, 9, 13)
    assert state.review_count == 0
    assert state.last_reviewed_on is None
    assert state.interval_days == 1
    assert state.active is True
    assert CURVE_HEAT_POLICY_REVISION == "curve_heat_v1"


def test_confirmed_review_updates_fact_projection_and_next_due_date() -> None:
    reviewed_on = date(2026, 9, 13)
    state = ReviewState(
        step=0,
        due_date=reviewed_on,
        active=True,
        interval_days=1,
        state_version=4,
    )

    transition = apply_review_event(state, "observed", reviewed_on)

    assert transition.advanced is True
    assert transition.step == 1
    assert transition.last_reviewed_on == reviewed_on
    assert transition.review_count == 1
    assert transition.state_version == 5
    assert transition.due_date == reviewed_on + timedelta(days=3)
    assert transition.heat_milli == 1000


def test_second_confirmation_on_same_day_is_audited_without_advancing_curve() -> None:
    reviewed_on = date(2026, 9, 13)
    state = ReviewState(
        step=2,
        due_date=date(2026, 9, 20),
        active=True,
        last_reviewed_on=reviewed_on,
        review_count=3,
        interval_days=7,
        heat_milli=1400,
        state_version=8,
    )

    transition = apply_review_event(state, "observed", reviewed_on)

    assert transition.advanced is False
    assert transition.step == state.step
    assert transition.due_date == state.due_date
    assert transition.interval_days == state.interval_days
    assert transition.review_count == 4
    assert transition.state_version == 9


def test_defer_does_not_claim_a_review_or_change_projection() -> None:
    state = ReviewState(
        step=2,
        due_date=date(2026, 9, 13),
        active=True,
        last_reviewed_on=date(2026, 9, 6),
        review_count=2,
        interval_days=7,
        heat_milli=1200,
        lapse_count=1,
        state_version=3,
    )

    transition = apply_review_event(state, "defer", date(2026, 9, 13))

    assert transition.advanced is False
    assert transition.step == state.step
    assert transition.due_date == state.due_date
    assert transition.last_reviewed_on == state.last_reviewed_on
    assert transition.review_count == state.review_count
    assert transition.state_version == state.state_version


def test_same_day_reinforce_can_only_shorten_the_existing_schedule() -> None:
    reviewed_on = date(2026, 9, 13)
    state = ReviewState(
        step=3,
        due_date=date(2026, 9, 27),
        active=True,
        last_reviewed_on=reviewed_on,
        review_count=4,
        interval_days=14,
        heat_milli=1600,
        state_version=9,
    )

    transition = apply_review_event(state, "reinforce", reviewed_on)

    assert transition.step == 2
    assert transition.due_date == date(2026, 9, 14)
    assert transition.interval_days == 1
    assert transition.lapse_count == 1
    assert transition.review_count == 5
    assert transition.advanced is True


def test_older_historical_event_increments_count_without_rewinding_projection() -> None:
    state = ReviewState(
        step=3,
        due_date=date(2026, 9, 27),
        active=True,
        last_reviewed_on=date(2026, 9, 13),
        review_count=4,
        interval_days=14,
        heat_milli=1600,
        state_version=9,
    )

    transition = apply_review_event(state, "reinforce", date(2026, 9, 1))

    assert transition.step == state.step
    assert transition.due_date == state.due_date
    assert transition.last_reviewed_on == state.last_reviewed_on
    assert transition.lapse_count == state.lapse_count
    assert transition.review_count == 5
    assert transition.advanced is False


def test_terminal_completion_deactivates_after_last_supported_curve_stage() -> None:
    reviewed_on = date(2026, 9, 13)
    state = ReviewState(
        step=5,
        due_date=reviewed_on,
        active=True,
        interval_days=60,
    )

    transition = apply_review_event(state, "complete", reviewed_on)

    assert transition.step == 6
    assert transition.interval_days == 90
    assert transition.due_date == date(2026, 12, 12)
    assert transition.active is False
