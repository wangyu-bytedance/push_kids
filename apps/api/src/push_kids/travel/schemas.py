from __future__ import annotations

from datetime import time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TravelArrangementCreate(BaseModel):
    child_id: str
    name: str = Field(min_length=1, max_length=30)
    weekdays: list[int] = Field(min_length=1, max_length=7)
    start_time: time
    end_time: time

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("请填写出行安排名称")
        return normalized

    @field_validator("weekdays")
    @classmethod
    def normalize_weekdays(cls, value: list[int]) -> list[int]:
        if any(item < 0 or item > 6 for item in value):
            raise ValueError("weekday must be 0-6")
        normalized = sorted(set(value))
        if not normalized:
            raise ValueError("请至少选择一天")
        return normalized

    @model_validator(mode="after")
    def valid_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("结束时间必须晚于开始时间")
        return self


class TravelArrangementPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    weekdays: list[int] | None = Field(default=None, min_length=1, max_length=7)
    start_time: time | None = None
    end_time: time | None = None

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


class TravelArrangementView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_id: str
    name: str
    weekdays: list[int]
    start_time: time
    end_time: time
    active: bool
