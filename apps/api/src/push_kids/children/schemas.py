from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class ChildView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    grade: str | None
    daily_budget_minutes: int
    active: bool
    created_at: datetime


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
