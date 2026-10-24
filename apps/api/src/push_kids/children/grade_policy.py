"""Closed academic-year policy; the caller supplies the Shanghai calendar date."""

from dataclasses import dataclass
from datetime import date
from typing import Literal

GRADE_VALUES = (
    "学前-小班",
    "学前-中班",
    "学前-大班",
    "小学一年级",
    "小学二年级",
    "小学三年级",
    "小学四年级",
    "小学五年级",
    "小学六年级",
    "初中一年级",
    "初中二年级",
    "初中三年级",
)
GRADE_LABELS = (
    "小班",
    "中班",
    "大班",
    "一年级",
    "二年级",
    "三年级",
    "四年级",
    "五年级",
    "六年级",
    "七年级",
    "八年级",
    "九年级",
)
_ALIASES = dict(zip(GRADE_LABELS, GRADE_VALUES, strict=True))
_ALIASES.update({value: value for value in GRADE_VALUES})


def canonical_grade(grade: str | None) -> str | None:
    return _ALIASES.get(grade) if grade is not None else None


def school_year(day: date) -> int:
    return day.year if (day.month, day.day) >= (9, 1) else day.year - 1


@dataclass(frozen=True)
class GradeProposal:
    grade: str
    reason: Literal["initial_check", "annual_progression"]


def propose_grade(
    grade: str | None, confirmed_year: int | None, current_year: int
) -> GradeProposal | None:
    value = canonical_grade(grade)
    if value is None or value == GRADE_VALUES[-1]:
        return None
    if confirmed_year is None:
        return GradeProposal(value, "initial_check")
    if isinstance(confirmed_year, bool) or not 1900 <= confirmed_year <= current_year:
        raise ValueError("invalid grade confirmation year")
    if confirmed_year == current_year:
        return None
    index = min(len(GRADE_VALUES) - 1, GRADE_VALUES.index(value) + current_year - confirmed_year)
    return GradeProposal(GRADE_VALUES[index], "annual_progression")
