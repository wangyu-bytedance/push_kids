from __future__ import annotations

from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")


def utcnow() -> datetime:
    return datetime.now(UTC)


def local_date(value: datetime | None = None) -> date:
    current = value or utcnow()
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(SHANGHAI).date()


def local_day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=SHANGHAI)
    end = datetime.combine(day, time.max, tzinfo=SHANGHAI)
    return start.astimezone(UTC), end.astimezone(UTC)
