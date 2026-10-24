from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from push_kids.agent_processing.suggestion_contracts import SuggestionTitle


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RequestKey(Command):
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$")


class Version(Command):
    expected_version: int = Field(ge=0, strict=True)


class Generate(Version):
    replace_suggestion_id: str | None = Field(None, max_length=36)


class PromptDisplayed(RequestKey):
    prompt_on: date


class Edit(Version):
    title: SuggestionTitle
    instructions: str = Field(min_length=1, max_length=1000)
    estimated_minutes: int | None = Field(None, ge=1, strict=True)


class RecordIntentCreate(Version, RequestKey):
    mode: Literal["partial", "complete"]


class RecordLink(Command):
    intent_id: str = Field(min_length=1, max_length=36)
    submission_id: str = Field(min_length=1, max_length=36)
