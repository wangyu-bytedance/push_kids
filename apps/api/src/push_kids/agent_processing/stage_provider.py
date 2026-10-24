"""Ark structured calls with absolute deadlines and a process-wide request bound."""

from __future__ import annotations

import asyncio
import base64
import json
import threading
from pathlib import Path
from time import monotonic
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI
from pydantic import BaseModel, ValidationError

from push_kids.agent_processing.contracts import AnalysisCapabilityError
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings

_REQUEST_SLOTS = threading.BoundedSemaphore(2)


class StagedArkProvider:
    """No DB ownership; every request is stateless and returns a validated DTO."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.coverage_enabled = settings.coverage_enabled
        self.model = settings.ark_model
        self.concurrency = settings.analysis_concurrency
        self.parameter_revision = f"{self.model}:disabled:4096:8192:2048"

    async def generate_stage(
        self,
        stage: str,
        instructions: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
        images: list[tuple[str, Path]],
        deadline: float,
        trace: AnalysisTrace,
    ) -> BaseModel:
        key = self.settings.ark_api_key
        if not key:
            raise StageFailure("config", retryable=False)
        limit = 45 if stage in {"extract", "group"} else 30
        timeout = min(limit, deadline - monotonic())
        if timeout <= 0:
            raise StageFailure("local_deadline")
        started = monotonic()
        acquired = False
        try:
            # Covers semaphore queueing, pool/connect/read and the entire response body.
            async with asyncio.timeout(timeout):
                while not _REQUEST_SLOTS.acquire(blocking=False):
                    await asyncio.sleep(0.01)
                acquired = True
                queued_ms = int((monotonic() - started) * 1000)
                content: list[dict[str, Any]] = [
                    {"type": "input_text", "text": json.dumps(payload, ensure_ascii=False)}
                ]
                for alias, path in images:
                    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
                        path.suffix.lower(), "image/png"
                    )
                    content.extend(
                        [
                            {"type": "input_text", "text": f"材料短编号 {alias}"},
                            {
                                "type": "input_image",
                                "image_url": f"data:{mime};base64,"
                                + base64.b64encode(path.read_bytes()).decode(),
                            },
                        ]
                    )
                async with AsyncOpenAI(
                    base_url=self.settings.ark_base_url,
                    api_key=key.get_secret_value(),
                    max_retries=0,
                    timeout=max(0.001, deadline - monotonic()),
                ) as client:
                    request: Any = dict(
                        model=self.model,
                        instructions=instructions,
                        input=[{"role": "user", "content": content}],
                        store=False,
                        max_output_tokens={
                            "extract": 4096,
                            "group": 4096,
                            "merge": 8192,
                            "match": 2048,
                            "coverage": 4096,
                        }[stage],
                        extra_body={"thinking": {"type": "disabled"}},
                        text={
                            "format": {
                                "type": "json_schema",
                                "name": stage,
                                "strict": True,
                                "schema": schema.model_json_schema(),
                            }
                        },
                    )
                    response = await client.responses.create(**request)
                usage = response.usage
                trace.info(
                    "analysis_stage_completed",
                    stage=stage,
                    duration_ms=int((monotonic() - started) * 1000),
                    queue_ms=queued_ms,
                    input_tokens=usage.input_tokens if usage else None,
                    output_tokens=usage.output_tokens if usage else None,
                    reasoning_tokens=(
                        usage.output_tokens_details.reasoning_tokens
                        if usage and usage.output_tokens_details
                        else None
                    ),
                    status=response.status,
                    request_id=getattr(response, "_request_id", None),
                )
                if response.status != "completed":
                    raise StageFailure("incomplete")
                try:
                    return schema.model_validate_json(response.output_text)
                except (ValidationError, ValueError):
                    raise StageFailure("validation") from None
        except (TimeoutError, APITimeoutError):
            raise StageFailure(
                "local_deadline" if monotonic() >= deadline else "provider_timeout"
            ) from None
        except APIStatusError as exc:
            status = exc.status_code
            if status == 400:
                # Preserve the existing public structured-output capability contract.
                raise AnalysisCapabilityError() from None
            reason = (
                "rate_limited"
                if status == 429
                else "auth"
                if status in {401, 403}
                else "provider_error"
                if status >= 500
                else "config"
            )
            raw_retry = exc.response.headers.get("retry-after", "0")
            retry = int(raw_retry) if raw_retry.isdigit() else 0
            trace.warning("analysis_stage_failed", stage=stage, reason=reason, http_status=status)
            raise StageFailure(
                reason, retryable=status == 429 or status >= 500, retry_after=retry
            ) from None
        except APIConnectionError:
            raise StageFailure("network") from None
        finally:
            if acquired:
                _REQUEST_SLOTS.release()
