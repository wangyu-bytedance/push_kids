"""Independent proposal contract; no claims about learned facts or scheduling."""

from typing import Annotated, Protocol

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

SuggestionTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=20,
        pattern=r"^[^\r\n\u2028\u2029]*$",
    ),
]


class LearningSuggestionContent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: SuggestionTitle
    instructions: str = Field(min_length=1, max_length=1000)
    rationale: str = Field(min_length=1, max_length=300)
    uncertainty: str = Field(min_length=1, max_length=200)
    estimated_minutes: int | None = Field(None, ge=1, strict=True)
    subject_id: str = Field(min_length=1, max_length=36)
    source_aliases: list[str] = Field(min_length=1, max_length=5)


class SuggestionProvider(Protocol):
    def suggest(self, context: dict) -> LearningSuggestionContent: ...
