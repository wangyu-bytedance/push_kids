"""Validated System One answers; legacy coverage revision remains read-compatible."""

import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Read-only compatibility for already stored Spec05 snapshots; no new producer.
DECISION_REVISION = "system-one-20261105-01"


class DecisionAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    type: Literal["noul", "choice"]
    noul: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    choice: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    probabilities: dict[str, float] | None = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.type == "noul":
            if self.noul is None or any(
                v is not None for v in (self.choice, self.confidence, self.probabilities)
            ):
                raise ValueError("invalid noul answer")
        else:
            values = self.probabilities or {}
            if (
                self.noul is not None
                or self.choice not in values
                or self.confidence is None
                or any(not math.isfinite(v) or not 0 <= v <= 1 for v in values.values())
                or abs(sum(values.values()) - 1) > 0.002
                or values[self.choice] < max(values.values()) - 0.000001
            ):
                raise ValueError("invalid choice answer")
        return self


def validate_answers(raw: Any, questions: dict[str, dict[str, Any]]) -> dict[str, DecisionAnswer]:
    if not isinstance(raw, dict) or set(raw) != set(questions):
        raise ValueError("answer coverage")
    result = {}
    for key, question in questions.items():
        answer = DecisionAnswer.model_validate(raw[key])
        if answer.type != question["type"]:
            raise ValueError("answer type")
        if answer.type == "choice" and set(answer.probabilities or {}) != set(question["criteria"]):
            raise ValueError("choice coverage")
        result[key] = answer
    return result
