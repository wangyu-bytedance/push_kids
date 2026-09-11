from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import time

WEEKLY_TIME_SLOTS_CAPABILITY = "weekly-time-slots-v1"


@dataclass(frozen=True, order=True)
class WeeklySlotValue:
    weekday: int
    start_time: time
    end_time: time


def canonicalize_weekly_slots(slots: Iterable[WeeklySlotValue]) -> tuple[WeeklySlotValue, ...]:
    ordered = sorted(slots, key=lambda item: item.weekday)
    seen: set[int] = set()
    for slot in ordered:
        if slot.weekday < 0 or slot.weekday > 6:
            raise ValueError("weekday must be 0-6")
        if slot.weekday in seen:
            raise ValueError("同一天只能设置一个时间段")
        if slot.end_time <= slot.start_time:
            raise ValueError(f"星期{slot.weekday + 1}的结束时间必须晚于开始时间")
        seen.add(slot.weekday)
    return tuple(ordered)


def slots_from_legacy(
    weekdays: Iterable[int], start_time: time | None, end_time: time | None
) -> tuple[WeeklySlotValue, ...]:
    days = sorted(set(weekdays))
    if not days:
        if start_time is not None or end_time is not None:
            raise ValueError("没有选择星期时不能设置开始或结束时间")
        return ()
    if start_time is None or end_time is None:
        raise ValueError("固定安排必须包含开始和结束时间")
    return canonicalize_weekly_slots(
        WeeklySlotValue(weekday=day, start_time=start_time, end_time=end_time) for day in days
    )


def uniform_range(slots: Iterable[WeeklySlotValue]) -> tuple[time, time] | None:
    canonical = canonicalize_weekly_slots(slots)
    if not canonical:
        return None
    first = (canonical[0].start_time, canonical[0].end_time)
    return first if all((slot.start_time, slot.end_time) == first for slot in canonical) else None


def has_weekly_time_slots_capability(header_value: str | None) -> bool:
    if not header_value:
        return False
    return WEEKLY_TIME_SLOTS_CAPABILITY in {
        value.strip() for value in header_value.split(",") if value.strip()
    }
