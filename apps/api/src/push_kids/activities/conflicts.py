from __future__ import annotations

from datetime import time


def _minutes(value: str) -> int:
    parsed = time.fromisoformat(value)
    return parsed.hour * 60 + parsed.minute


def attach_conflicts(items: list[dict]) -> list[dict]:
    """Return schedule items with deterministic half-open interval conflict metadata."""
    result = [{**item, "has_conflict": False, "conflicts": []} for item in items]
    for left_index, left in enumerate(result):
        left_start = _minutes(left["start_time"])
        left_end = _minutes(left["end_time"])
        for right in result[left_index + 1 :]:
            right_start = _minutes(right["start_time"])
            right_end = _minutes(right["end_time"])
            overlap = min(left_end, right_end) - max(left_start, right_start)
            if overlap <= 0:
                continue
            left["has_conflict"] = True
            right["has_conflict"] = True
            left["conflicts"].append(_conflict_view(right, overlap))
            right["conflicts"].append(_conflict_view(left, overlap))
    for item in result:
        item["conflicts"].sort(
            key=lambda conflict: (
                conflict["start_time"],
                conflict["end_time"],
                conflict["source"],
                conflict["item_id"],
            )
        )
    return result


def _conflict_view(item: dict, overlap_minutes: int) -> dict:
    return {
        "item_id": item["id"],
        "name": item["name"],
        "start_time": item["start_time"],
        "end_time": item["end_time"],
        "source": item["source"],
        "overlap_minutes": overlap_minutes,
    }
