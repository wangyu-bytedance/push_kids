import json
from types import SimpleNamespace

import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisOutputExhaustedError,
    AnalysisOutputValidationError,
    ModelAnalysisResult,
)
from push_kids.agent_processing.providers import ArkAnalysisProvider
from push_kids.platform.errors import DependencyError


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


def result(*rows: dict, summary: str = "请确认"):
    return {
        "summary": summary,
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


def test_provider_regenerates_when_summary_describes_absent_content():
    calls = []
    outputs = [
        json.dumps(
            result(
                item("集合分组"),
                summary="练习集合分组，无语文、英语相关学习内容。",
            ),
            ensure_ascii=False,
        ),
        json.dumps(
            result(
                item("集合分组"),
                summary="集合分组，寻找规则，并找到每个分类的具体元素。",
            ),
            ensure_ascii=False,
        ),
    ]

    def respond(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(output_text=outputs.pop(0))

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))

    proposal = provider.analyze(AnalysisInput(text="集合分组", existing_subjects=["数学", "语文"]))

    assert proposal.summary == "集合分组，寻找规则，并找到每个分类的具体元素。"
    assert len(calls) == 2
    retry_prompt = calls[1]["input"][0]["content"][-1]["text"]
    assert "summary.exclusion_clause" in retry_prompt
    assert "无语文、英语相关学习内容" not in retry_prompt


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


def test_incomplete_provider_response_uses_worker_transport_retry():
    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **_kwargs: SimpleNamespace(status="incomplete", output_text="")
        )
    )

    with pytest.raises(DependencyError):
        provider.analyze(AnalysisInput(text="分数", existing_subjects=["数学"]))


def test_all_empty_subject_buckets_are_a_valid_incremental_proposal():
    data = AnalysisInput(text="重复材料", existing_subjects=["数学", "语文"])

    proposal = data.validate_model_result(ModelAnalysisResult.model_validate(result()))

    assert proposal.knowledge_points == []
    assert proposal.todo_matches == []
    assert proposal.subject_name == "数学"


@pytest.mark.parametrize(
    "summary",
    [
        "没有识别到英语任务。",
        "没有英语相关的任务。",
        "本次不包含语文内容。",
        "练习分类，无语文、英语相关学习内容。",
        "本次未涉及其他学科知识。",
    ],
)
def test_model_summary_rejects_absent_or_excluded_content(summary: str):
    data = AnalysisInput(text="集合分组", existing_subjects=["数学", "语文"])

    with pytest.raises(AnalysisOutputValidationError) as error:
        data.validate_model_result(
            ModelAnalysisResult.model_validate(result(item("集合分组"), summary=summary))
        )

    assert error.value.codes == ["summary.exclusion_clause"]


def test_model_summary_accepts_short_factual_content_without_banning_valid_terms():
    data = AnalysisInput(text="不规则图形分类", existing_subjects=["数学", "语文"])

    proposal = data.validate_model_result(
        ModelAnalysisResult.model_validate(
            result(
                item("不规则图形分类"),
                summary="不规则图形分类，寻找共同特征。",
            )
        )
    )

    assert proposal.summary == "不规则图形分类，寻找共同特征。"

    proposal = data.model_copy(update={"text": "无括号算式"}).validate_model_result(
        ModelAnalysisResult.model_validate(
            result(
                item("无括号算式"),
                summary="无括号算式学习，辨认运算顺序。",
            )
        )
    )

    assert proposal.summary == "无括号算式学习，辨认运算顺序。"

    proposal = data.model_copy(update={"text": "没有括号的混合运算"}).validate_model_result(
        ModelAnalysisResult.model_validate(
            result(
                item("没有括号的混合运算"),
                summary="没有括号的混合运算学习，辨认运算顺序。",
            )
        )
    )

    assert proposal.summary == "没有括号的混合运算学习，辨认运算顺序。"


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
