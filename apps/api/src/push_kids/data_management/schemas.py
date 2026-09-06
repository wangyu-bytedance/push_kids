from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DeletionConfirmation(BaseModel):
    confirmation_name: str = Field(min_length=1, max_length=60)


class DeletionRequestView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    target_type: Literal["child", "family"]
    state: Literal["queued", "running", "succeeded", "failed"]
    attempts: int
    retryable: bool
    error_code: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
