from datetime import date, timedelta

import pytest
from push_kids.reporting.trends import (
    TREND_METRIC_KEYS,
    build_overview_trends,
    equal_time_bucket_index,
)


@pytest.mark.parametrize(
    ("range_days", "expected_lengths"),
    [
        (7, [1, 1, 1, 1, 1, 1, 1]),
        (30, [5, 4, 4, 5, 4, 4, 4]),
        (100, [15, 14, 14, 15, 14, 14, 14]),
    ],
)
def test_overview_trends_use_seven_contiguous_near_equal_buckets(
    range_days: int, expected_lengths: list[int]
) -> None:
    start = date(2026, 1, 1)

    result = build_overview_trends(
        start,
        range_days,
        {key: [0] * range_days for key in TREND_METRIC_KEYS},
    )

    buckets = result["buckets"]
    assert result["timezone"] == "Asia/Shanghai"
    assert result["aggregation"] == "equal_time_sum"
    assert len(buckets) == 7
    lengths = [
        (date.fromisoformat(item["end_day"]) - date.fromisoformat(item["start_day"])).days + 1
        for item in buckets
    ]
    assert lengths == expected_lengths
    assert sum(lengths) == range_days
    for previous, current in zip(buckets, buckets[1:], strict=False):
        assert date.fromisoformat(previous["end_day"]) + timedelta(days=1) == date.fromisoformat(
            current["start_day"]
        )
    assert all(item[key] == 0 for item in buckets for key in TREND_METRIC_KEYS)


def test_overview_trends_preserve_database_aggregate_totals() -> None:
    start = date(2026, 4, 1)
    daily_counts = {
        "learning_records": [1] * 30,
        "new_knowledge_items": [1 if offset % 2 == 0 else 0 for offset in range(30)],
        "review_feedback_count": [0] * 29 + [3],
        "activity_records": [0] * 30,
    }

    result = build_overview_trends(start, 30, daily_counts)

    expected = {
        "learning_records": 30,
        "new_knowledge_items": 15,
        "review_feedback_count": 3,
        "activity_records": 0,
    }
    for key, total in expected.items():
        assert sum(item[key] for item in result["buckets"]) == total


def test_overview_trends_reject_incomplete_or_negative_aggregates() -> None:
    start = date(2026, 4, 1)
    complete = {key: [0] * 7 for key in TREND_METRIC_KEYS}
    with pytest.raises(ValueError, match="complete report range"):
        build_overview_trends(start, 7, {**complete, "learning_records": [0] * 6})
    with pytest.raises(ValueError, match="non-negative"):
        build_overview_trends(start, 7, {**complete, "learning_records": [0] * 6 + [-1]})


def test_equal_time_bucket_index_rejects_invalid_ranges_and_offsets() -> None:
    with pytest.raises(ValueError, match="at least seven"):
        equal_time_bucket_index(0, 6)
    with pytest.raises(ValueError, match="outside"):
        equal_time_bucket_index(-1, 7)
    with pytest.raises(ValueError, match="outside"):
        equal_time_bucket_index(7, 7)
