"""Offline national calendar policy; no school calendar, I/O or weekday fallback."""

from datetime import date
from typing import Literal

from chinese_calendar import constants, is_workday


class ChinaWorkdayPolicy:
    # The pinned dataset contains complete national annual arrangements for these years.
    coverage_start = date(min(day.year for day in constants.holidays), 1, 1)
    coverage_end = date(max(day.year for day in constants.holidays), 12, 31)
    revision = "chinesecalendar-1.11.0"

    @classmethod
    def classify(cls, day: date) -> Literal["workday", "rest_day", "unsupported"]:
        if not cls.coverage_start <= day <= cls.coverage_end:
            return "unsupported"
        return "workday" if is_workday(day) else "rest_day"

    @classmethod
    def warning(cls, day: date) -> dict[str, str] | None:
        if cls.classify(day) != "unsupported":
            return None
        return {
            "code": "workday_calendar_coverage_missing",
            "coverage_end": cls.coverage_end.isoformat(),
        }
