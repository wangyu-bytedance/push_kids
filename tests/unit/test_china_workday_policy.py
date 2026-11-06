from datetime import date, timedelta

from push_kids.activities.workday import ChinaWorkdayPolicy


def test_every_day_of_2026_against_official_national_arrangements():
    # 国办发明电〔2025〕7号 (2025-11-04). Independent expectations, not library constants.
    holidays = [
        ("2026-01-01", "2026-01-03"),
        ("2026-02-15", "2026-02-23"),
        ("2026-04-04", "2026-04-06"),
        ("2026-05-01", "2026-05-05"),
        ("2026-06-19", "2026-06-21"),
        ("2026-09-25", "2026-09-27"),
        ("2026-10-01", "2026-10-07"),
    ]
    adjusted = {
        date.fromisoformat(value)
        for value in [
            "2026-01-04",
            "2026-02-14",
            "2026-02-28",
            "2026-05-09",
            "2026-09-20",
            "2026-10-10",
        ]
    }
    day = date(2026, 1, 1)
    while day.year == 2026:
        holiday = any(
            date.fromisoformat(start) <= day <= date.fromisoformat(end) for start, end in holidays
        )
        expected = day in adjusted or (day.weekday() < 5 and not holiday)
        assert ChinaWorkdayPolicy.classify(day) == ("workday" if expected else "rest_day"), day
        day += timedelta(days=1)


def test_coverage_is_explicit_including_both_boundaries():
    assert ChinaWorkdayPolicy.coverage_start == date(2004, 1, 1)
    assert ChinaWorkdayPolicy.coverage_end == date(2026, 12, 31)
    for day in [date(2003, 12, 31), date(2027, 1, 1), date(2027, 1, 4)]:
        assert ChinaWorkdayPolicy.classify(day) == "unsupported"
        assert ChinaWorkdayPolicy.warning(day)["code"] == "workday_calendar_coverage_missing"
    assert ChinaWorkdayPolicy.classify(date(2004, 1, 1)) != "unsupported"
    assert ChinaWorkdayPolicy.classify(date(2026, 12, 31)) != "unsupported"
    assert ChinaWorkdayPolicy.warning(date(2026, 12, 31)) is None
