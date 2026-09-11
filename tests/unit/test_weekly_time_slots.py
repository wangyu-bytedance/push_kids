from datetime import time

import pytest
from push_kids.activities.weekly_slots import (
    WeeklySlotValue,
    canonicalize_weekly_slots,
    has_weekly_time_slots_capability,
    slots_from_legacy,
    uniform_range,
)


def slot(weekday: int, start: str, end: str) -> WeeklySlotValue:
    return WeeklySlotValue(weekday, time.fromisoformat(start), time.fromisoformat(end))


def test_weekly_slots_are_sorted_and_uniform_range_is_detected() -> None:
    slots = canonicalize_weekly_slots([slot(2, "18:00", "19:00"), slot(1, "18:00", "19:00")])
    assert [item.weekday for item in slots] == [1, 2]
    assert uniform_range(slots) == (time(18), time(19))
    assert uniform_range([slot(1, "18:00", "19:00"), slot(2, "19:00", "20:00")]) is None


@pytest.mark.parametrize(
    ("slots", "message"),
    [
        ([slot(1, "18:00", "19:00"), slot(1, "19:00", "20:00")], "同一天"),
        ([slot(7, "18:00", "19:00")], "0-6"),
        ([slot(1, "19:00", "19:00")], "结束时间"),
    ],
)
def test_weekly_slots_reject_ambiguous_or_invalid_rows(
    slots: list[WeeklySlotValue], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        canonicalize_weekly_slots(slots)


def test_legacy_and_capability_adapters_are_bounded() -> None:
    assert slots_from_legacy([2, 1], time(18), time(19)) == (
        slot(1, "18:00", "19:00"),
        slot(2, "18:00", "19:00"),
    )
    assert has_weekly_time_slots_capability("other, weekly-time-slots-v1") is True
    assert has_weekly_time_slots_capability(None) is False
