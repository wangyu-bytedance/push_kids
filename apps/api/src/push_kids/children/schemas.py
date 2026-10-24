from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from push_kids.children.grade_policy import canonical_grade


class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    grade: str | None = Field(default=None, max_length=20)
    daily_budget_minutes: int = Field(default=15, ge=5, le=120)
    # Learning subjects the parent already picked in the form. Absent and [] both mean
    # "start empty"; the profile is still usable and subjects can be added in settings.
    subject_names: list[str] = Field(default_factory=list, max_length=20)


class ChildUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    grade: str | None = Field(default=None, max_length=20)
    daily_budget_minutes: int | None = Field(default=None, ge=5, le=120)
    confirm_grade: bool = False
    expected_grade_revision: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def explicit_grade_confirmation(self):
        if self.confirm_grade and (
            "grade" not in self.model_fields_set or self.expected_grade_revision is None
        ):
            raise ValueError("确认年级需要年级值与当前版本")
        return self


class ChildView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    grade: str | None
    grade_confirmed_school_year: int | None
    grade_revision: int
    daily_budget_minutes: int
    active: bool
    created_at: datetime


class PendingGradeConfirmation(BaseModel):
    id: str
    name: str
    current_grade: str
    suggested_grade: str
    reason: Literal["initial_check", "annual_progression"]
    revision: int


class GradeConfirmations(BaseModel):
    school_year: int
    can_confirm: bool
    items: list[PendingGradeConfirmation] = Field(max_length=5)


class GradeConfirmation(BaseModel):
    school_year: int = Field(ge=1900, le=9999)
    expected_grade_revision: int = Field(ge=0)
    grade: str = Field(min_length=1, max_length=20)

    @field_validator("grade")
    @classmethod
    def supported_grade(cls, value: str) -> str:
        grade = canonical_grade(value)
        if grade is None:
            raise ValueError("请选择小班至九年级的实际年级")
        return grade


class GradeConfirmationResult(BaseModel):
    child: ChildView
    outcome: Literal["confirmed", "already_confirmed"]


class SubjectCreate(BaseModel):
    child_id: str
    name: str = Field(min_length=1, max_length=40)
    kind: Literal["learning", "activity"] = "learning"
    color: str = Field(default="#39847A", pattern=r"^#[0-9A-Fa-f]{6}$")


class SubjectView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    name: str
    kind: str
    color: str
    active: bool
    is_custom: bool
    created_at: datetime


class SubjectUpdate(BaseModel):
    active: bool
