import asyncio
from time import monotonic

import httpx
import pytest
from push_kids.agent_processing.failures import StageFailure
from push_kids.agent_processing.stage_provider import StagedArkProvider
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings


def configured():
    provider = StagedArkProvider(
        Settings(_env_file=None, ARK_API_KEY="synthetic", PUSH_KIDS_SYSTEM_ONE_ENABLED=True)
    )
    decision = getattr(provider, "acceptance_provider", None)
    assert decision is not None, "enabled acceptance owns the dedicated protocol"
    return decision


def evaluate(provider, questions=None):
    return asyncio.run(
        provider.evaluate(
            questions or {"q1": {"type": "noul", "instructions": "是否涉及数学？"}},
            {"text": "合成材料"},
            [],
            monotonic() + 2,
            AnalysisTrace.disabled(),
        )
    )


def test_system_one_uses_dedicated_protocol_and_question_ids():
    provider = configured()
    requests = []

    def respond(request):
        import json

        requests.append((request, json.loads(request.content)))
        return httpx.Response(
            200,
            json={
                "model": "doubao-seed-2-1-lite-260915",
                "answers": {
                    "q2": {"type": "noul", "noul": 0.1},
                    "q1": {"type": "noul", "noul": 0.99},
                },
                "usage": {"input_tokens": 20, "output_tokens": 0},
            },
        )

    provider.transport = httpx.MockTransport(respond)
    result = evaluate(provider, {"q1": {"type": "noul"}, "q2": {"type": "noul"}})
    assert result["q1"].noul == 0.99 and result["q2"].noul == 0.1
    request, body = requests[0]
    assert request.url.path == "/api/v1/systemone"
    assert request.headers["ark-beta-systemone-api"] == "true"
    assert set(body) == {"model", "state", "questions"}


@pytest.mark.parametrize(
    "answer",
    [
        {},
        {"q1": {"type": "noul", "noul": 2}},
        {"q1": {"type": "noul", "noul": float("nan")}},
        {"q1": {"type": "choice", "choice": "fake"}},
    ],
)
def test_invalid_answers_never_become_pass(answer, caplog):
    provider = configured()
    provider.transport = httpx.MockTransport(
        lambda _: httpx.Response(
            200, content=__import__("json").dumps({"model": provider.model, "answers": answer})
        )
    )
    with pytest.raises(StageFailure):
        evaluate(provider)
    assert "合成材料" not in caplog.text


@pytest.mark.parametrize(
    "status,reason",
    [(400, "config"), (401, "auth"), (429, "rate_limited"), (503, "provider_error")],
)
def test_errors_are_classified_without_retry_or_payload(status, reason):
    provider = configured()
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(status, json={"error": {"message": "synthetic-secret"}})

    provider.transport = httpx.MockTransport(respond)
    with pytest.raises(StageFailure) as caught:
        evaluate(provider)
    assert caught.value.reason == reason and len(calls) == 1
    assert "synthetic-secret" not in str(caught.value)


def test_oversized_response_is_stopped_before_full_buffering():
    provider = configured()
    chunks_read = []

    class LargeResponse(httpx.AsyncByteStream):
        async def __aiter__(self):
            for index in range(100):
                chunks_read.append(index)
                yield b"x" * 4096

    provider.transport = httpx.MockTransport(lambda _: httpx.Response(200, stream=LargeResponse()))
    with pytest.raises(StageFailure) as caught:
        evaluate(provider)
    assert caught.value.reason == "capacity"
    assert len(chunks_read) <= 17


def test_acceptance_enabled_by_default_and_can_be_disabled():
    provider = StagedArkProvider(Settings(_env_file=None))
    assert getattr(provider, "acceptance_provider", None) is not None
    assert getattr(provider, "decision_provider", None) is None
    assert (
        StagedArkProvider(
            Settings(_env_file=None, PUSH_KIDS_SYSTEM_ONE_ENABLED=False)
        ).acceptance_provider
        is None
    )


def test_both_protocols_share_two_slots_and_queued_deadline_releases_nothing(monkeypatch):
    from threading import BoundedSemaphore

    from tests.unit.test_stage_provider import install_client

    class Capacity(BoundedSemaphore):
        active = 0
        maximum = 0

        def acquire(self, *args, **kwargs):
            acquired = super().acquire(*args, **kwargs)
            if acquired:
                self.active += 1
                self.maximum = max(self.maximum, self.active)
            return acquired

        def release(self, *args, **kwargs):
            self.active -= 1
            return super().release(*args, **kwargs)

    capacity = Capacity(2)
    monkeypatch.setattr("push_kids.agent_processing.stage_provider._REQUEST_SLOTS", capacity)
    monkeypatch.setattr("push_kids.agent_processing.system_one_provider.REQUEST_SLOTS", capacity)
    install_client(monkeypatch, delay=0.05)
    pro = StagedArkProvider(Settings(_env_file=None, ARK_API_KEY="synthetic"))
    decision = configured()

    async def response(request):
        await asyncio.sleep(0.05)
        return httpx.Response(
            200, json={"model": decision.model, "answers": {"q": {"type": "noul", "noul": 0.99}}}
        )

    decision.transport = httpx.MockTransport(response)

    async def run():
        from push_kids.agent_processing.stage_contracts import MatchingResult

        async def check(seconds):
            return await decision.evaluate(
                {"q": {"type": "noul"}}, {}, [], monotonic() + seconds, AnalysisTrace.disabled()
            )

        first = asyncio.create_task(
            pro.generate_stage(
                "match", "", {}, MatchingResult, [], monotonic() + 2, AnalysisTrace.disabled()
            )
        )
        second = asyncio.create_task(check(2))
        await asyncio.sleep(0.01)
        with pytest.raises(StageFailure) as failure:
            await check(0.001)
        assert failure.value.reason == "queue_deadline"
        await asyncio.gather(first, second)

    asyncio.run(run())
    assert capacity.maximum == 2 and capacity.active == 0
