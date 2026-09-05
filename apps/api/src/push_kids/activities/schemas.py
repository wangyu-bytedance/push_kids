from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ActivityScheduleCreate(BaseModel):
    child_id: str
    subject_id: str
    weekdays: list[int] = Field(default_factory=list, max_length=7)
    time_text: str | None = Field(default=None, max_length=20)
    start_time: time | None = None
    end_time: time | None = None
    target_per_week: int | None = Field(default=None, ge=1, le=14)
    note: str | None = Field(default=None, max_length=200)

    @field_validator("weekdays")
    @classmethod
    def valid_weekdays(cls, value: list[int]) -> list[int]:
        if any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        return sorted(set(value))

    @field_validator("end_time")
    @classmethod
    def valid_time_range(cls, value: time | None, info):
        start = info.data.get("start_time")
        if value is not None and start is not None and value <= start:
            raise ValueError("结束时间必须晚于开始时间")
        return value

    @model_validator(mode="after")
    def valid_mode(self):
        if self.weekdays and (self.start_time is None or self.end_time is None):
            raise ValueError("固定提醒必须包含开始和结束时间")
        if not self.weekdays and (self.start_time is not None or self.end_time is not None):
            raise ValueError("时间不固定时不能设置开始或结束时间")
        return self


class ActivityScheduleUpdate(BaseModel):
    child_id: str | None = None
    subject_id: str | None = None
    weekdays: list[int] | None = Field(default=None, max_length=7)
    time_text: str | None = Field(default=None, max_length=20)
    start_time: time | None = None
    end_time: time | None = None
    target_per_week: int | None = Field(default=None, ge=1, le=14)
    note: str | None = Field(default=None, max_length=200)

    @field_validator("weekdays")
    @classmethod
    def valid_weekdays(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        return sorted(set(value)) if value is not None else None


class ActivityScheduleView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    subject_id: str
    weekdays: list[int]
    start_time: time | None
    end_time: time | None
    target_per_week: int | None
    note: str | None
    active: bool


class CalendarEventWrite(BaseModel):
    child_id: str
    name: str = Field(min_length=1, max_length=80)
    event_date: date
    start_time: time
    end_time: time
    kind: Literal["class", "activity", "other"] = "other"
    repeat_weekly: bool = False

    @field_validator("end_time")
    @classmethod
    def event_range(cls, value: time, info):
        start = info.data.get("start_time")
        if start is not None and value <= start:
            raise ValueError("结束时间必须晚于开始时间")
        return value


class CalendarEventPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    event_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    kind: Literal["class", "activity", "other"] | None = None
    repeat_weekly: bool | None = None


class CalendarEventView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    name: str
    event_date: date
    start_time: time
    end_time: time
    kind: str
    repeat_weekly: bool


class ActivityRecordCreate(BaseModel):
    child_id: str
    subject_id: str
    occurred_at: datetime
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    note: str | None = Field(default=None, max_length=300)


class ActivityRecordView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    subject_id: str
    occurred_at: datetime
    duration_minutes: int | None
    note: str | None
