from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    action: Literal["complete", "reinforce", "partial", "defer"]


class FeedbackResult(BaseModel):
    review_id: str
    action: str
    step: int
    due_date: str
    active: bool
