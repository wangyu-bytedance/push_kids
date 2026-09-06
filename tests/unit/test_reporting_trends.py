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
        (100, [15, 14, 14, 14, 15, 14, 14]),
    ],
)
def test_overview_trends_use_seven_contiguous_near_equal_buckets(
    range_days: int, expected_lengths: list[int]
) -> None:
    start = date(2026, 1, 1)

    result = build_overview_trends(start, range_days, {})

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


def test_overview_trends_preserve_metric_totals_and_ignore_out_of_range_days() -> None:
    start = date(2026, 4, 1)
    in_range = [start + timedelta(days=offset) for offset in range(30)]
    event_days = {
        "learning_records": [*in_range, start - timedelta(days=1), start + timedelta(days=30)],
        "new_knowledge_items": in_range[::2],
        "review_feedback_count": [start + timedelta(days=29)] * 3,
        "activity_records": [],
    }

    result = build_overview_trends(start, 30, event_days)

    expected = {
        "learning_records": 30,
        "new_knowledge_items": 15,
        "review_feedback_count": 3,
        "activity_records": 0,
    }
    for key, total in expected.items():
        assert sum(item[key] for item in result["buckets"]) == total


def test_equal_time_bucket_index_rejects_invalid_ranges_and_offsets() -> None:
    with pytest.raises(ValueError, match="at least seven"):
        equal_time_bucket_index(0, 6)
    with pytest.raises(ValueError, match="outside"):
        equal_time_bucket_index(-1, 7)
    with pytest.raises(ValueError, match="outside"):
        equal_time_bucket_index(7, 7)
