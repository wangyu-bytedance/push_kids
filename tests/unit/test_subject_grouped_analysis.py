import json
from types import SimpleNamespace

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisOutputExhaustedError,
    ModelAnalysisResult,
)
from push_kids.agent_processing.providers import ArkAnalysisProvider


def item(name: str, *, kind: str = "new_learning", review_id: str | None = None):
    return {
        "kind": kind,
        "name": name,
        "review_id": review_id,
        "existing_knowledge_id": None,
        "category": "计算",
        "display_kind": "arithmetic",
        "review_method": "口算与讲解",
        "estimated_minutes": 3,
        "direct_evidence": [{"source": "parent_text", "image_index": None, "detail": name}],
        "context_used": [],
        "confidence": "high",
    }


def result(*rows: dict):
    return {
        "summary": "请确认",
        "source": "家长文字",
        "subjects": {"数学": list(rows), "语文": []},
        "uncertainties": [],
    }


def test_provider_regenerates_with_sanitized_feedback_and_strict_schema():
    calls = []
    outputs = ["not-json SECRET_RAW", json.dumps(result(item("两位数进位加法")))]

    def respond(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(output_text=outputs.pop(0))

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))
    proposal = provider.analyze(AnalysisInput(text="28+17", existing_subjects=["数学", "语文"]))

    assert [point.name for point in proposal.knowledge_points] == ["两位数进位加法"]
    assert len(calls) == 2
    assert calls[0]["store"] is False
    schema = calls[0]["text"]["format"]["schema"]
    assert calls[0]["text"]["format"]["strict"] is True
    assert schema["properties"]["subjects"]["required"] == ["数学", "语文"]
    assert schema["properties"]["subjects"]["additionalProperties"] is False
    retry_prompt = calls[1]["input"][0]["content"][-1]["text"]
    assert "json.parse" in retry_prompt
    assert "SECRET_RAW" not in retry_prompt


def test_provider_stops_after_three_invalid_structured_results():
    calls = []

    def respond(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(output_text="{}")

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))

    with pytest.raises(AnalysisOutputExhaustedError):
        provider.analyze(AnalysisInput(text="分数", existing_subjects=["数学"]))
    assert len(calls) == 3


def test_validation_outputs_only_increment_and_maps_due_review():
    data = AnalysisInput(
        text="今天练了进位加法，也新学了退位减法",
        existing_subjects=["数学", "语文"],
        same_day_learning=[
            {
                "knowledge_id": "known-today",
                "subject_name": "数学",
                "name": "两位数进位加法",
                "category": "计算",
            }
        ],
        todo_candidates=[
            {
                "review_id": "review-1",
                "knowledge_id": "known-review",
                "subject_name": "数学",
                "knowledge_name": "20以内加法",
                "step": 1,
                "due_date": "2026-09-06",
                "eligible_on": "2026-09-06",
            }
        ],
    )
    raw = result(
        item("两位数进位加法"),
        item("20以内加法", kind="review", review_id="review-1"),
        item("退位减法"),
    )

    proposal = data.validate_model_result(ModelAnalysisResult.model_validate(raw))

    assert [point.name for point in proposal.knowledge_points] == ["退位减法"]
    assert [match.review_id for match in proposal.todo_matches] == ["review-1"]
    assert proposal.todo_matches[0].eligible_on == "2026-09-06"
