from datetime import UTC, date, datetime

import pytest
from push_kids.children.grade_policy import (
    GRADE_LABELS,
    GRADE_VALUES,
    canonical_grade,
    propose_grade,
    school_year,
)
from push_kids.platform.time import local_date


@pytest.mark.parametrize("index", range(12))
def test_each_stage_advances_once_and_ninth_is_terminal(index):
    grade = GRADE_VALUES[index]
    assert canonical_grade(GRADE_LABELS[index]) == grade
    proposal = propose_grade(grade, 2026, 2027)
    if index == 11:
        assert proposal is None
    else:
        assert proposal.grade == GRADE_VALUES[index + 1]
        assert propose_grade(grade, 2027, 2027) is None
        assert propose_grade(grade, None, 2030).grade == grade


@pytest.mark.parametrize("value", [None, "", "其他", "学前", "国际学校", " 小班", "高一"])
def test_unknown_values_are_never_guessed(value):
    assert canonical_grade(value) is None
    assert propose_grade(value, None, 2026) is None


def test_accumulation_is_capped_without_yearly_debt():
    assert propose_grade("一年级", 2026, 2028).grade == "小学三年级"
    assert propose_grade("大班", 2026, 2050).grade == "初中三年级"
    assert propose_grade("小学二年级", None, 2050).reason == "initial_check"


@pytest.mark.parametrize(
    "day,expected",
    [
        (date(2026, 8, 31), 2025),
        (date(2026, 9, 1), 2026),
        (date(2027, 1, 1), 2026),
        (date(2028, 2, 29), 2027),
    ],
)
def test_school_year_boundary(day, expected):
    assert school_year(day) == expected


def test_shanghai_midnight_not_utc_midnight():
    assert school_year(local_date(datetime(2026, 8, 31, 15, 59, 59, tzinfo=UTC))) == 2025
    assert school_year(local_date(datetime(2026, 8, 31, 16, tzinfo=UTC))) == 2026


@pytest.mark.parametrize("year", [-1, 0, 1899, 2027, True])
def test_invalid_anchor_fails_closed(year):
    with pytest.raises(ValueError):
        propose_grade("一年级", year, 2026)
