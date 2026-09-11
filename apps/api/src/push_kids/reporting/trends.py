from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, timedelta

TREND_BUCKET_COUNT = 7
TREND_METRIC_KEYS = (
    "learning_records",
    "new_knowledge_items",
    "review_feedback_count",
    "activity_records",
)


def equal_time_bucket_index(day_offset: int, range_days: int) -> int:
    """Map an in-range day to one of seven ordered, near-equal time buckets."""
    if range_days < TREND_BUCKET_COUNT:
        raise ValueError("trend range must contain at least seven days")
    if day_offset < 0 or day_offset >= range_days:
        raise ValueError("day offset is outside the trend range")
    return min(TREND_BUCKET_COUNT - 1, day_offset * TREND_BUCKET_COUNT // range_days)


def build_overview_trends(
    start_day: date,
    range_days: int,
    daily_counts: Mapping[str, Sequence[int]],
) -> dict:
    """Build trends from bounded database aggregates, never raw historical events."""
    starts: list[date | None] = [None] * TREND_BUCKET_COUNT
    ends: list[date | None] = [None] * TREND_BUCKET_COUNT
    counts = [{key: 0 for key in TREND_METRIC_KEYS} for _ in range(TREND_BUCKET_COUNT)]
    for offset in range(range_days):
        bucket_index = equal_time_bucket_index(offset, range_days)
        current = start_day + timedelta(days=offset)
        if starts[bucket_index] is None:
            starts[bucket_index] = current
        ends[bucket_index] = current

    for key in TREND_METRIC_KEYS:
        values = daily_counts.get(key, ())
        if len(values) != range_days:
            raise ValueError("trend counts must cover the complete report range")
        for offset, value in enumerate(values):
            if not isinstance(value, int) or value < 0:
                raise ValueError("trend counts must be non-negative integers")
            bucket_index = equal_time_bucket_index(offset, range_days)
            counts[bucket_index][key] += value

    buckets = []
    for index in range(TREND_BUCKET_COUNT):
        bucket_start = starts[index]
        bucket_end = ends[index]
        if bucket_start is None or bucket_end is None:
            raise ValueError("trend range did not populate all seven buckets")
        buckets.append(
            {
                "start_day": bucket_start.isoformat(),
                "end_day": bucket_end.isoformat(),
                **counts[index],
            }
        )

    return {
        "timezone": "Asia/Shanghai",
        "aggregation": "equal_time_sum",
        "buckets": buckets,
    }
