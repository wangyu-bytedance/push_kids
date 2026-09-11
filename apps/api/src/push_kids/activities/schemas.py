from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from push_kids.activities.weekly_slots import (
    WeeklySlotValue,
    canonicalize_weekly_slots,
    slots_from_legacy,
    uniform_range,
)


class ActivityTimeSlot(BaseModel):
    weekday: int
    start_time: time
    end_time: time

    def value(self) -> WeeklySlotValue:
        return WeeklySlotValue(self.weekday, self.start_time, self.end_time)


def _activity_slots(values: list[ActivityTimeSlot]) -> list[ActivityTimeSlot]:
    return sorted(values, key=lambda item: item.weekday)


class ActivityScheduleCreate(BaseModel):
    child_id: str
    subject_id: str
    weekdays: list[int] | None = Field(default=None, max_length=7)
    time_text: str | None = Field(default=None, max_length=20)
    start_time: time | None = None
    end_time: time | None = None
    time_slots: list[ActivityTimeSlot] | None = Field(default=None, max_length=7)
    target_per_week: int | None = Field(default=None, ge=1, le=14)
    note: str | None = Field(default=None, max_length=200)

    @field_validator("weekdays")
    @classmethod
    def valid_weekdays(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return None
        if any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        return sorted(set(value))

    @model_validator(mode="after")
    def valid_mode(self):
        if self.time_slots is not None:
            if {"weekdays", "start_time", "end_time"} & self.model_fields_set:
                raise ValueError("time_slots 不能和旧版星期/时间字段同时提交")
            self.time_slots = _activity_slots(self.time_slots)
            return self
        legacy = slots_from_legacy(self.weekdays or [], self.start_time, self.end_time)
        self.time_slots = [
            ActivityTimeSlot(
                weekday=item.weekday,
                start_time=item.start_time,
                end_time=item.end_time,
            )
            for item in legacy
        ]
        values = tuple(item.value() for item in self.time_slots)
        self.weekdays = [item.weekday for item in values]
        common = uniform_range(values)
        self.start_time = common[0] if common else None
        self.end_time = common[1] if common else None
        return self

    def slot_values(self) -> tuple[WeeklySlotValue, ...]:
        return canonicalize_weekly_slots(item.value() for item in self.time_slots or [])


class ActivityScheduleUpdate(BaseModel):
    child_id: str | None = None
    subject_id: str | None = None
    weekdays: list[int] | None = Field(default=None, max_length=7)
    time_text: str | None = Field(default=None, max_length=20)
    start_time: time | None = None
    end_time: time | None = None
    time_slots: list[ActivityTimeSlot] | None = Field(default=None, max_length=7)
    target_per_week: int | None = Field(default=None, ge=1, le=14)
    note: str | None = Field(default=None, max_length=200)

    @field_validator("weekdays")
    @classmethod
    def valid_weekdays(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        return sorted(set(value)) if value is not None else None

    @model_validator(mode="after")
    def valid_patch(self):
        if "time_slots" in self.model_fields_set:
            if self.time_slots is None:
                raise ValueError("time_slots 不能为 null")
            if {"weekdays", "start_time", "end_time"} & self.model_fields_set:
                raise ValueError("time_slots 不能和旧版星期/时间字段同时提交")
            self.time_slots = _activity_slots(self.time_slots)
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("结束时间必须晚于开始时间")
        return self

    def slot_values(self) -> tuple[WeeklySlotValue, ...] | None:
        if "time_slots" not in self.model_fields_set:
            return None
        return canonicalize_weekly_slots(item.value() for item in self.time_slots or [])


class ActivityScheduleView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    subject_id: str
    weekdays: list[int]
    start_time: time | None
    end_time: time | None
    time_slots: list[ActivityTimeSlot]
    target_per_week: int | None
    note: str | None
    active: bool


class ActivityScheduleList(BaseModel):
    items: list[ActivityScheduleView]


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
