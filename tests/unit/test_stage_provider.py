import asyncio
import json
from time import monotonic
from types import SimpleNamespace

import httpx
import pytest
from openai import APIConnectionError, APIStatusError, APITimeoutError
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.stage_contracts import MatchingResult
from push_kids.agent_processing.stage_provider import StagedArkProvider
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings


def install_client(monkeypatch, *, error=None, status="completed", invalid=False, delay=0):
    state = SimpleNamespace(active=0, maximum=0, requests=[])

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["max_retries"] == 0
            self.responses = self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def create(self, **kwargs):
            state.requests.append(kwargs)
            state.active += 1
            state.maximum = max(state.maximum, state.active)
            try:
                await asyncio.sleep(delay)
                if error:
                    raise error
                return SimpleNamespace(
                    status=status,
                    usage=None,
                    output_text="private-broken"
                    if invalid
                    else json.dumps(
                        {"decisions": [{"candidate": "i0", "match": None, "uncertain": False}]}
                    ),
                )
            finally:
                state.active -= 1

    monkeypatch.setattr("push_kids.agent_processing.stage_provider.AsyncOpenAI", Client)
    return state


async def call(provider, seconds=2):
    return await provider.generate_stage(
        "match",
        "instructions",
        {},
        MatchingResult,
        [],
        monotonic() + seconds,
        AnalysisTrace.disabled(),
    )


@pytest.mark.parametrize(
    "status,reason,retryable",
    [
        (429, "rate_limited", True),
        (503, "provider_error", True),
        (401, "auth", False),
        (403, "auth", False),
        (404, "config", False),
    ],
)
def test_http_failures_are_safe_and_bounded(monkeypatch, status, reason, retryable, caplog):
    request = httpx.Request("POST", "https://example.invalid")
    error = APIStatusError(
        "private-token-child",
        response=httpx.Response(status, request=request, headers={"retry-after": "999"}),
        body={"private": "child"},
    )
    install_client(monkeypatch, error=error)
    with pytest.raises(StageFailure) as caught:
        asyncio.run(call(StagedArkProvider(Settings(ARK_API_KEY="synthetic"))))
    assert caught.value.reason == reason and caught.value.retryable == retryable
    assert caught.value.retry_after <= 60
    assert "private" not in str(caught.value) + caplog.text


@pytest.mark.parametrize(
    "failure,reason",
    [
        ("timeout", "provider_timeout"),
        ("network", "network"),
        ("incomplete", "incomplete"),
        ("invalid", "validation"),
    ],
)
def test_transport_and_output_failure_classification(monkeypatch, failure, reason):
    request = httpx.Request("POST", "https://example.invalid")
    error = {
        "timeout": APITimeoutError(request=request),
        "network": APIConnectionError(request=request),
    }.get(failure)
    install_client(
        monkeypatch,
        error=error,
        status="incomplete" if failure == "incomplete" else "completed",
        invalid=failure == "invalid",
    )
    with pytest.raises(StageFailure, match=reason):
        asyncio.run(call(StagedArkProvider(Settings(ARK_API_KEY="synthetic"))))


def test_process_concurrency_and_cancellation_release_slots(monkeypatch):
    state = install_client(monkeypatch, delay=0.08)
    provider = StagedArkProvider(Settings(ARK_API_KEY="synthetic"))

    async def scenario():
        tasks = [asyncio.create_task(call(provider)) for _ in range(6)]
        await asyncio.sleep(0.02)
        tasks[0].cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await call(provider)

    asyncio.run(scenario())
    assert state.maximum == 2 and state.active == 0
    assert all(
        r["store"] is False
        and r["extra_body"]["thinking"]["type"] == "disabled"
        and r["max_output_tokens"] == 2048
        for r in state.requests
    )


def test_entire_request_honors_absolute_deadline(monkeypatch):
    state = install_client(monkeypatch, delay=0.5)
    started = monotonic()
    with pytest.raises(StageFailure, match="local_deadline"):
        asyncio.run(call(StagedArkProvider(Settings(ARK_API_KEY="synthetic")), seconds=0.03))
    assert monotonic() - started < 0.2 and state.active == 0


def test_bad_request_preserves_public_capability_code(monkeypatch):
    from push_kids.agent_processing.contracts import (
        AnalysisCapabilityError,
        analysis_failure_disposition,
    )

    request = httpx.Request("POST", "https://example.invalid")
    install_client(
        monkeypatch,
        error=APIStatusError(
            "private-schema", response=httpx.Response(400, request=request), body=None
        ),
    )
    with pytest.raises(AnalysisCapabilityError) as caught:
        asyncio.run(call(StagedArkProvider(Settings(ARK_API_KEY="synthetic"))))
    disposition = analysis_failure_disposition(caught.value)
    assert disposition.code == "analysis_schema_unsupported" and not disposition.retryable
