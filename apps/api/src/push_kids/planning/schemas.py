from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    action: Literal["complete", "reinforce", "partial", "defer"]


class FeedbackResult(BaseModel):
    review_id: str
    action: str
    step: int
    due_date: str
    active: bool


class BatchFeedbackItem(BaseModel):
    review_id: str = Field(min_length=1, max_length=36)
    action: Literal["complete", "reinforce", "partial", "defer"]


class BatchFeedbackRequest(BaseModel):
    child_id: str = Field(min_length=1, max_length=36)
    items: list[BatchFeedbackItem] = Field(min_length=1, max_length=120)


class BatchFeedbackResult(BaseModel):
    items: list[FeedbackResult]
    replayed: bool
