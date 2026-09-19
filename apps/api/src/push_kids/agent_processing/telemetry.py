from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Final

logger = logging.getLogger("push_kids.analysis")

_SAFE_FIELD_NAMES: Final = frozenset(
    {
        "attempt",
        "cached_tokens",
        "cleanup_count",
        "context_mode",
        "duration_ms",
        "job_id",
        "logical_calls",
        "max_turns",
        "output_items",
        "reason",
        "remaining_time_ms",
        "remaining_turns",
        "request_count",
        "response_kind",
        "result_count",
        "status",
        "total_logical_calls",
        "total_results",
        "turn",
        "validation_codes",
    }
)
_SAFE_TOKEN = re.compile(r"^[a-z0-9_.:-]{1,80}$")
_SAFE_CODES: Final = frozenset(
    {
        "context.reference",
        "evidence.detail",
        "evidence.image_index",
        "evidence.parent_text",
        "history_search.candidate_key",
        "history_search.incomplete",
        "history_search.result_budget",
        "history_search.tool_budget",
        "item.blank",
        "json.parse",
        "source.blank",
        "subjects.input_empty",
        "subjects.keys",
        "subjects.max_items",
        "summary.exclusion_clause",
        "summary.too_long",
        "tool.arguments",
        "tool.batch_size",
        "tool.name",
    }
)


def safe_validation_codes(codes: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """Return bounded static categories; never log model-provided paths or values."""
    result: list[str] = []
    for code in codes[:20]:
        if code in _SAFE_CODES:
            safe = code
        elif code.startswith("schema."):
            safe = "schema.fields"
        else:
            safe = "validation.other"
        if safe not in result:
            result.append(safe)
    return tuple(result)


@dataclass(frozen=True)
class AnalysisTrace:
    job_id: str
    attempt: int
    enabled: bool = True

    @classmethod
    def disabled(cls) -> AnalysisTrace:
        return cls(job_id="disabled", attempt=0, enabled=False)

    def info(self, event: str, **fields: object) -> None:
        self._emit(logging.INFO, event, fields)

    def warning(self, event: str, **fields: object) -> None:
        self._emit(logging.WARNING, event, fields)

    def _emit(self, level: int, event: str, fields: dict[str, object]) -> None:
        if not self.enabled:
            return
        if not _SAFE_TOKEN.fullmatch(event):
            raise ValueError("unsafe analysis trace event")
        unknown = fields.keys() - _SAFE_FIELD_NAMES
        if unknown:
            raise ValueError("unsafe analysis trace fields")
        safe_job_id = self.job_id if _SAFE_TOKEN.fullmatch(self.job_id) else "other"
        parts = [event, f"job_id={safe_job_id}", f"attempt={self.attempt}"]
        for key in sorted(fields):
            value = fields[key]
            if key == "validation_codes":
                raw_codes = value if isinstance(value, (list, tuple)) else ()
                values = safe_validation_codes(tuple(str(item) for item in raw_codes))
                rendered = ",".join(values) or "none"
            elif isinstance(value, bool):
                rendered = str(int(value))
            elif isinstance(value, int):
                rendered = str(value)
            elif value is None:
                rendered = "none"
            else:
                rendered = str(value).lower()
                if not _SAFE_TOKEN.fullmatch(rendered):
                    rendered = "other"
            parts.append(f"{key}={rendered}")
        logger.log(level, " ".join(parts))
