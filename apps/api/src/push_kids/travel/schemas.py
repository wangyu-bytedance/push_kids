from __future__ import annotations

from datetime import time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from push_kids.activities.weekly_slots import (
    WeeklySlotValue,
    canonicalize_weekly_slots,
    slots_from_legacy,
    uniform_range,
)


class TravelTimeSlot(BaseModel):
    weekday: int
    start_time: time
    end_time: time

    def value(self) -> WeeklySlotValue:
        return WeeklySlotValue(self.weekday, self.start_time, self.end_time)


def _travel_slots(values: list[TravelTimeSlot]) -> list[TravelTimeSlot]:
    return sorted(values, key=lambda item: item.weekday)


class TravelArrangementCreate(BaseModel):
    child_id: str
    name: str = Field(min_length=1, max_length=30)
    weekdays: list[int] | None = Field(default=None, min_length=1, max_length=7)
    start_time: time | None = None
    end_time: time | None = None
    time_slots: list[TravelTimeSlot] | None = Field(default=None, max_length=7)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("请填写出行安排名称")
        return normalized

    @field_validator("weekdays")
    @classmethod
    def normalize_weekdays(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return None
        if any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        normalized = sorted(set(value))
        if not normalized:
            raise ValueError("请至少选择一天")
        return normalized

    @model_validator(mode="after")
    def valid_schedule(self):
        if self.time_slots is not None:
            if {"weekdays", "start_time", "end_time"} & self.model_fields_set:
                raise ValueError("time_slots 不能和旧版星期/时间字段同时提交")
            self.time_slots = _travel_slots(self.time_slots)
            return self
        legacy = slots_from_legacy(self.weekdays or [], self.start_time, self.end_time)
        self.time_slots = [
            TravelTimeSlot(
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
        canonical = canonicalize_weekly_slots(item.value() for item in self.time_slots or [])
        if not canonical:
            raise ValueError("请至少选择一天")
        return canonical


class TravelArrangementPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    weekdays: list[int] | None = Field(default=None, min_length=1, max_length=7)
    start_time: time | None = None
    end_time: time | None = None
    time_slots: list[TravelTimeSlot] | None = Field(default=None, max_length=7)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("请填写出行安排名称")
        return normalized

    @field_validator("weekdays")
    @classmethod
    def normalize_weekdays(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return None
        if any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        normalized = sorted(set(value))
        if not normalized:
            raise ValueError("请至少选择一天")
        return normalized

    @model_validator(mode="after")
    def valid_patch(self):
        if "time_slots" in self.model_fields_set:
            if self.time_slots is None:
                raise ValueError("time_slots 不能为 null")
            if {"weekdays", "start_time", "end_time"} & self.model_fields_set:
                raise ValueError("time_slots 不能和旧版星期/时间字段同时提交")
            self.time_slots = _travel_slots(self.time_slots)
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
        canonical = canonicalize_weekly_slots(item.value() for item in self.time_slots or [])
        if not canonical:
            raise ValueError("请至少选择一天")
        return canonical


class TravelArrangementView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_id: str
    name: str
    weekdays: list[int]
    start_time: time | None
    end_time: time | None
    time_slots: list[TravelTimeSlot]
    active: bool


class TravelArrangementList(BaseModel):
    items: list[TravelArrangementView]
