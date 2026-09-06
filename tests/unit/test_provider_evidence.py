import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from push_kids.agent_processing import providers
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisOutputExhaustedError,
    AnalysisProposal,
)
from push_kids.agent_processing.providers import ArkAnalysisProvider
from push_kids.platform.config import Settings


def valid_proposal():
    return {
        "summary": "本次学习",
        "source": "家长文字",
        "subjects": {
            "数学": [
                {
                    "kind": "new_learning",
                    "name": "分数",
                    "review_id": None,
                    "existing_knowledge_id": None,
                    "category": "数学概念",
                    "display_kind": "concept",
                    "review_method": "口头回顾",
                    "estimated_minutes": 3,
                    "direct_evidence": [
                        {
                            "source": "parent_text",
                            "image_index": None,
                            "detail": "家长说明分数",
                        }
                    ],
                    "context_used": [],
                    "confidence": "high",
                }
            ]
        },
        "uncertainties": [],
    }


@pytest.mark.parametrize("invalid", ["empty", "context", "image", "no_text", "todo", "blank"])
def test_ark_rejects_invalid_evidence(invalid):
    data = AnalysisInput(text="分数", image_paths=[], existing_subjects=["数学"])
    body = valid_proposal()
    point = body["subjects"]["数学"][0]
    if invalid == "empty":
        point["direct_evidence"] = []
    elif invalid == "context":
        point["context_used"] = ["invented-record"]
    elif invalid == "image":
        point["direct_evidence"] = [{"source": "image", "image_index": 1, "detail": "图片"}]
    elif invalid == "no_text":
        data.text = None
    elif invalid == "todo":
        point["kind"] = "review"
        point["review_id"] = "invented"
    else:
        point["direct_evidence"][0]["detail"] = "  "
    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "test"
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(create=lambda **kw: SimpleNamespace(output_text=json.dumps(body)))
    )
    with pytest.raises(AnalysisOutputExhaustedError):
        provider.analyze(data)


def test_valid_evidence_and_parent_additions():
    data = AnalysisInput(
        text="分数",
        image_paths=[Path("test.png")],
        recent_learning=[
            {
                "record_id": "known",
                "subject_name": "数学",
                "summary": "已学",
                "occurred_at": "2026-09-05",
            }
        ],
    )
    body = {
        "summary": "本次学习",
        "subject_name": "数学",
        "knowledge_points": [
            {
                "name": "分数",
                "direct_evidence": [{"source": "parent_text", "detail": "家长说明分数"}],
            }
        ],
    }
    body["knowledge_points"][0]["context_used"] = ["known"]
    body["knowledge_points"][0]["direct_evidence"].append(
        {"source": "image", "image_index": 1, "detail": "题目"}
    )
    assert data.validate_proposal(AnalysisProposal.model_validate(body))
    body["knowledge_points"][0]["direct_evidence"] = []
    assert AnalysisProposal.model_validate(body)  # Parent-edited proposals remain valid.


def test_prompt_keeps_all_accepted_text():
    tail = "末尾内容必须保留"
    content = "学" * (4000 - len(tail)) + tail
    assert ArkAnalysisProvider._prompt(AnalysisInput(text=content)).endswith(content)


def test_ark_provider_unwraps_secret_only_for_sdk(monkeypatch):
    sentinel = "ark-test-secret-sentinel"
    captured: dict[str, str] = {}

    def fake_openai(*, base_url: str, api_key: str):
        captured.update(base_url=base_url, api_key=api_key)
        return SimpleNamespace()

    monkeypatch.setattr(providers, "OpenAI", fake_openai)
    settings = Settings(PUSH_KIDS_ENV="development", ARK_API_KEY=sentinel)

    ArkAnalysisProvider(settings)

    assert captured["api_key"] == sentinel
    assert sentinel not in repr(settings)
