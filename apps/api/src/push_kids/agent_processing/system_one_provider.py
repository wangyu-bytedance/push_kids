"""Dedicated Ark System One transport; no database or business-state ownership."""

from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from time import monotonic
from typing import Any

import httpx

from push_kids.agent_processing.decision_contracts import DecisionAnswer, validate_answers
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.request_limits import REQUEST_SLOTS
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings

MAX_RESPONSE_BYTES = 64 * 1024


class SystemOneDecisionProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.ark_system_one_model
        self.transport: httpx.AsyncBaseTransport | None = None

    async def evaluate(
        self,
        questions: dict[str, dict[str, Any]],
        state: dict[str, Any],
        images: list[tuple[str, Path]],
        deadline: float,
        trace: AnalysisTrace,
    ) -> dict[str, DecisionAnswer]:
        if not 1 <= len(questions) <= 128 or len(images) > 9:
            raise StageFailure("capacity", retryable=False)
        # Keep both protocols on the approved Ark host; custom test traffic uses transport.
        if self.settings.ark_base_url.rstrip("/") != "https://ark.cn-beijing.volces.com/api/v3":
            raise StageFailure("config", retryable=False)
        key = self.settings.ark_api_key
        if not key:
            raise StageFailure("config", retryable=False)
        text_bytes = len(json.dumps([questions, state], ensure_ascii=False).encode())
        if text_bytes > 96 * 1024:
            # UTF-8 byte count is a conservative text-token ceiling; reserve image capacity.
            raise StageFailure("capacity", retryable=False)
        started, acquired = monotonic(), False
        try:
            async with asyncio.timeout(max(0.001, deadline - started)):
                while not acquired:
                    acquired = REQUEST_SLOTS.acquire(blocking=False)
                    if not acquired:
                        await asyncio.sleep(0.01)
                queued = monotonic()
                execution_deadline = min(deadline, queued + 30)
                content: list[dict[str, Any]] = [{"type": "text", "text": state}]
                image_bytes = 0
                for alias, path in images:
                    with path.open("rb") as source:
                        raw = source.read(self.settings.upload_max_bytes + 1)
                    if len(raw) > self.settings.upload_max_bytes:
                        raise StageFailure("capacity", retryable=False)
                    image_bytes += len(raw)
                    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
                        path.suffix.lower(), "image/png"
                    )
                    content.extend(
                        [
                            {"type": "text", "text": {"material": alias}},
                            {
                                "type": "image",
                                "image_url": "data:"
                                + mime
                                + ";base64,"
                                + base64.b64encode(raw).decode(),
                                "image_pixel_limit": {"max_pixels": 1048576},
                            },
                        ]
                    )
                body = {
                    "model": self.model,
                    "state": content if images else state,
                    "questions": questions,
                }
                async with httpx.AsyncClient(
                    timeout=max(0.001, execution_deadline - monotonic()),
                    transport=self.transport,
                    follow_redirects=False,
                ) as client:
                    async with asyncio.timeout(max(0.001, execution_deadline - monotonic())):
                        async with client.stream(
                            "POST",
                            "https://ark.cn-beijing.volces.com/api/v1/systemone",
                            headers={
                                "Authorization": "Bearer " + key.get_secret_value(),
                                "ark-beta-systemone-api": "true",
                            },
                            json=body,
                        ) as response:
                            if not response.is_success:
                                status = response.status_code
                                reason = (
                                    "rate_limited"
                                    if status == 429
                                    else "auth"
                                    if status in {401, 403}
                                    else "provider_error"
                                    if status >= 500
                                    else "config"
                                )
                                raise StageFailure(reason, retryable=status == 429 or status >= 500)
                            response_body = bytearray()
                            async for chunk in response.aiter_bytes(chunk_size=4096):
                                if len(response_body) + len(chunk) > MAX_RESPONSE_BYTES:
                                    raise StageFailure("capacity", retryable=False)
                                response_body.extend(chunk)
                try:
                    raw_result = json.loads(response_body)
                    if raw_result.get("model") != self.model:
                        raise ValueError("model mismatch")
                    result = validate_answers(raw_result.get("answers"), questions)
                except (ValueError, TypeError, AttributeError):
                    raise StageFailure("validation", stage="decision") from None
                usage = raw_result.get("usage") or {}
                trace.info(
                    "analysis_stage_completed",
                    stage="decision",
                    duration_ms=int((monotonic() - started) * 1000),
                    queue_ms=int((queued - started) * 1000),
                    payload_bytes=text_bytes,
                    image_bytes=image_bytes,
                    request_bytes=len(response.request.content),
                    input_tokens=usage.get("input_tokens"),
                    output_tokens=usage.get("output_tokens"),
                    request_id=response.headers.get("X-Request-Id"),
                )
                return result
        except (TimeoutError, httpx.TimeoutException):
            raise StageFailure(
                "queue_deadline"
                if not acquired
                else "local_deadline"
                if monotonic() >= deadline
                else "provider_timeout"
            ) from None
        except httpx.TransportError:
            raise StageFailure("network") from None
        finally:
            if acquired:
                REQUEST_SLOTS.release()
