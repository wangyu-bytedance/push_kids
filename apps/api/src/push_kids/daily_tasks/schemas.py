from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, field_validator

TaskMinutes = Annotated[StrictInt, Field(ge=1, le=180)]
TaskName = Annotated[str, Field(min_length=1, max_length=30, strict=True)]


class DailyTaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: TaskName
    target_minutes: TaskMinutes

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class DailyTaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: TaskName | None = None
    target_minutes: TaskMinutes | None = None

    @field_validator("name", "target_minutes", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("任务名称和目标分钟不能为空")
        return value.strip() if isinstance(value, str) else value


class DailyTaskView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    child_id: str
    name: str
    target_minutes: int
    active: bool
    created_at: datetime
    updated_at: datetime


class DailyCompletionCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    completed: StrictBool


class DailyTaskTodayItem(DailyTaskView):
    completed: bool
    occurred_at: datetime | None


class DailyTasksToday(BaseModel):
    day: date
    items: list[DailyTaskTodayItem] = Field(max_length=20)
    total_count: int
    remaining_count: int
