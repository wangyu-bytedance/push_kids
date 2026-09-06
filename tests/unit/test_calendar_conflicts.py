from push_kids.activities.conflicts import attach_conflicts


def item(item_id: str, name: str, start: str, end: str, source: str = "calendar") -> dict:
    return {
        "id": item_id,
        "name": name,
        "start_time": start,
        "end_time": end,
        "source": source,
    }


def test_conflicts_use_half_open_intervals_and_mark_both_sides() -> None:
    result = attach_conflicts(
        [
            item("travel", "上学", "07:30", "08:10", "travel_arrangement"),
            item("reading", "早读", "07:50", "08:20"),
            item("next", "晨会", "08:20", "08:30"),
        ]
    )

    assert result[0]["has_conflict"] is True
    assert result[1]["has_conflict"] is True
    assert result[2]["has_conflict"] is False
    assert result[0]["conflicts"] == [
        {
            "item_id": "reading",
            "name": "早读",
            "start_time": "07:50",
            "end_time": "08:20",
            "source": "calendar",
            "overlap_minutes": 20,
        }
    ]
    assert result[1]["conflicts"][0]["item_id"] == "travel"


def test_nested_and_multiple_conflicts_are_complete_and_stable() -> None:
    result = attach_conflicts(
        [
            item("outer", "接送", "16:00", "18:00", "travel_arrangement"),
            item("later", "钢琴", "17:00", "17:30", "activity_schedule"),
            item("earlier", "家长会", "16:30", "16:45"),
        ]
    )

    assert [conflict["item_id"] for conflict in result[0]["conflicts"]] == [
        "earlier",
        "later",
    ]
    assert result[1]["conflicts"][0]["overlap_minutes"] == 30
    assert result[2]["conflicts"][0]["overlap_minutes"] == 15
