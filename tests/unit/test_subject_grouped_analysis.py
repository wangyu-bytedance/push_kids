import json
import logging
from types import SimpleNamespace

import push_kids.agent_processing.providers as providers_module
import pytest
from push_kids.agent_processing.contracts import (
    AnalysisDeadlineExceededError,
    AnalysisInput,
    AnalysisOutputExhaustedError,
    AnalysisOutputValidationError,
    ModelAnalysisResult,
)
from push_kids.agent_processing.providers import ArkAnalysisProvider
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.errors import DependencyError


def item(name: str, *, kind: str = "new_learning", review_id: str | None = None):
    return {
        "kind": kind,
        "name": name,
        "review_id": review_id,
        "existing_knowledge_id": None,
        "category": "计算",
        "display_kind": "arithmetic",
        "review_method": "变式练习",
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


def test_provider_history_tool_loop_returns_structured_result_without_provider_storage():
    calls = []
    tool_requests = []
    responses = [
        SimpleNamespace(
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "call-1",
                    "arguments": json.dumps(
                        {
                            "queries": [
                                {
                                    "candidate_key": "两位数进位加法",
                                    "subject_name": "数学",
                                    "keywords": ["进位加法"],
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                }
            ],
        ),
        SimpleNamespace(
            output_text=json.dumps(result(item("两位数进位加法", kind="new")), ensure_ascii=False),
            output=[],
        ),
    ]

    def respond(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.context_cache_enabled = False
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))

    proposal = provider.analyze_with_history(
        AnalysisInput(text="两位数进位加法", existing_subjects=["数学", "语文"]),
        lambda request: tool_requests.append(request) or [],
        max_turns=8,
    )

    assert [point.name for point in proposal.knowledge_points] == ["两位数进位加法"]
    assert len(tool_requests) == 1
    assert tool_requests[0].candidate_key == "两位数进位加法"
    assert len(calls) == 2
    assert all(call["store"] is False for call in calls)
    tool_outputs = [
        item
        for item in calls[1]["input"]
        if isinstance(item, dict) and item.get("type") == "function_call_output"
    ]
    assert tool_outputs == [
        {
            "type": "function_call_output",
            "call_id": "call-1",
            "output": '{"queries":[{"candidate_key":"两位数进位加法","items":[]}]}',
        }
    ]


def test_provider_session_reuse_sends_only_new_input_and_cleans_up(monkeypatch, caplog):
    calls = []
    deleted = []
    responses = [
        SimpleNamespace(
            id="resp-private-first",
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "call-1",
                    "arguments": json.dumps(
                        {
                            "queries": [
                                {
                                    "candidate_key": "分数",
                                    "subject_name": "数学",
                                    "keywords": ["分数"],
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                }
            ],
            usage={"input_tokens_details": {"cached_tokens": 0}},
        ),
        SimpleNamespace(
            id="resp-private-second",
            output_text=json.dumps(result(item("分数", kind="new")), ensure_ascii=False),
            output=[],
            usage={"prompt_tokens_details": {"cached_tokens": 123}},
        ),
    ]

    def respond(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.context_cache_enabled = True
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(
            create=respond,
            delete=lambda response_id, **kwargs: deleted.append((response_id, kwargs)),
        )
    )
    monkeypatch.setattr(providers_module, "time", lambda: 1000)
    caplog.set_level(logging.INFO, logger="push_kids.analysis")

    proposal = provider.analyze_with_history(
        AnalysisInput(text="private-child-content", existing_subjects=["数学", "语文"]),
        lambda _request: [],
        max_turns=8,
        trace=AnalysisTrace(job_id="job-safe", attempt=1),
    )

    assert [point.name for point in proposal.knowledge_points] == ["分数"]
    assert calls[0]["store"] is True
    assert calls[0]["extra_body"] == {"expire_at": 1600}
    assert "previous_response_id" not in calls[0]
    assert "tools" in calls[0]
    assert calls[1]["store"] is True
    assert calls[1]["previous_response_id"] == "resp-private-first"
    assert calls[1]["tools"] == calls[0]["tools"]
    assert calls[1]["input"] == [
        {
            "type": "function_call_output",
            "call_id": "call-1",
            "output": '{"queries":[{"candidate_key":"分数","items":[]}]}',
        }
    ]
    assert all(call["text"]["format"]["strict"] is True for call in calls)
    assert [item[0] for item in deleted] == ["resp-private-second", "resp-private-first"]
    assert all(item[1]["timeout"] == 0.5 for item in deleted)
    assert "cached_tokens=123" in caplog.text
    assert "context_mode=session" in caplog.text
    assert "resp-private" not in caplog.text
    assert "private-child-content" not in caplog.text


def test_provider_session_cleanup_failure_does_not_replace_valid_result(caplog):
    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.context_cache_enabled = True
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **_kwargs: SimpleNamespace(
                id="resp-private",
                output_text=json.dumps(result(), ensure_ascii=False),
                output=[],
            ),
            delete=lambda *_args, **_kwargs: (_ for _ in ()).throw(
                RuntimeError("private-cleanup-detail")
            ),
        )
    )
    caplog.set_level(logging.INFO, logger="push_kids.analysis")

    proposal = provider.analyze_with_history(
        AnalysisInput(text="private-child-content", existing_subjects=["数学", "语文"]),
        lambda _request: [],
        max_turns=8,
        trace=AnalysisTrace(job_id="job-safe", attempt=1),
    )

    assert proposal.knowledge_points == []
    assert "analysis_context_session_cleanup_failed" in caplog.text
    assert "private-cleanup-detail" not in caplog.text
    assert "resp-private" not in caplog.text


def test_provider_session_retries_invalid_tool_arguments_without_querying():
    calls = []
    searched = []
    responses = [
        SimpleNamespace(
            id="resp-1",
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "invalid-call",
                    "arguments": '{"queries":"invalid"}',
                }
            ],
        ),
        SimpleNamespace(
            id="resp-2",
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "valid-call",
                    "arguments": json.dumps(
                        {
                            "queries": [
                                {
                                    "candidate_key": "分数",
                                    "subject_name": "数学",
                                    "keywords": ["分数"],
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                }
            ],
        ),
        SimpleNamespace(
            id="resp-3",
            output_text=json.dumps(result(item("分数", kind="new")), ensure_ascii=False),
            output=[],
        ),
    ]

    def respond(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.context_cache_enabled = True
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(create=respond, delete=lambda *_args, **_kwargs: None)
    )

    provider.analyze_with_history(
        AnalysisInput(text="分数", existing_subjects=["数学", "语文"]),
        lambda request: searched.append(request) or [],
        max_turns=8,
    )

    assert [request.candidate_key for request in searched] == ["分数"]
    assert calls[1]["previous_response_id"] == "resp-1"
    assert calls[2]["previous_response_id"] == "resp-2"
    assert json.loads(calls[1]["input"][0]["output"]) == {"error": "tool.arguments"}
    assert "tool.arguments" in json.dumps(calls[1]["input"][1], ensure_ascii=False)
    assert calls[2]["input"][0]["call_id"] == "valid-call"
    assert all("caching" not in call.get("extra_body", {}) for call in calls)


def test_provider_session_chain_is_never_reused_across_invocations():
    calls = []
    response_ids = iter(("resp-first-job", "resp-second-job"))

    def respond(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            id=next(response_ids),
            output_text=json.dumps(result(), ensure_ascii=False),
            output=[],
        )

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.context_cache_enabled = True
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(create=respond, delete=lambda *_args, **_kwargs: None)
    )
    data = AnalysisInput(text="练习", existing_subjects=["数学", "语文"])

    provider.analyze_with_history(data, lambda _request: [], max_turns=8)
    provider.analyze_with_history(data, lambda _request: [], max_turns=8)

    assert len(calls) == 2
    assert all("previous_response_id" not in call for call in calls)


def test_provider_batches_twenty_candidates_in_one_turn_and_logs_only_safe_counters(caplog):
    secret = "SECRET_CHILD_KEYWORD"
    candidates = [
        {
            "candidate_key": f"{secret}-{index}",
            "subject_name": "数学",
            "keywords": [f"{secret}-{index}"],
        }
        for index in range(20)
    ]
    responses = [
        SimpleNamespace(
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "batch-call",
                    "arguments": json.dumps({"queries": candidates}, ensure_ascii=False),
                }
            ],
        ),
        SimpleNamespace(output_text=json.dumps(result()), output=[]),
    ]
    calls = []

    def respond(**kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))
    searched = []
    caplog.set_level(logging.INFO, logger="push_kids.analysis")

    provider.analyze_with_history(
        AnalysisInput(text="private-child-content", existing_subjects=["数学", "语文"]),
        lambda request: searched.append(request) or [],
        max_turns=8,
        trace=AnalysisTrace(job_id="job-safe", attempt=2),
    )

    assert len(calls) == 2
    assert len(searched) == 20
    assert "request_count=20" in caplog.text
    assert "logical_calls=20" in caplog.text
    assert "total_logical_calls=20" in caplog.text
    assert "job_id=job-safe" in caplog.text
    assert secret not in caplog.text
    assert "private-child-content" not in caplog.text
    assert "数学" not in caplog.text


def test_provider_reserves_the_last_turn_for_final_output():
    tool_response = SimpleNamespace(
        output_text="",
        output=[
            {
                "type": "function_call",
                "name": "search_history_items",
                "call_id": "call",
                "arguments": json.dumps(
                    {
                        "queries": [
                            {
                                "candidate_key": "分数",
                                "subject_name": "数学",
                                "keywords": ["分数"],
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
            }
        ],
    )
    calls = []
    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(create=lambda **kwargs: calls.append(kwargs) or tool_response)
    )

    with pytest.raises(AnalysisOutputExhaustedError) as error:
        provider.analyze_with_history(
            AnalysisInput(text="分数", existing_subjects=["数学"]),
            lambda _request: [],
            max_turns=2,
        )

    assert error.value.reason == "final_turn_tool_call"
    assert calls[1]["tool_choice"] == "none"


@pytest.mark.parametrize(
    "invalid_arguments",
    [
        "[]",
        json.dumps(
            {
                "queries": [
                    {
                        "candidate_key": "SECRET_CANDIDATE",
                        "subject_name": "数学",
                        "keywords": "SECRET_KEYWORD",
                    }
                ]
            }
        ),
        json.dumps(
            {
                "queries": [
                    {
                        "candidate_key": "SECRET_CANDIDATE",
                        "subject_name": "未配置科目",
                        "keywords": ["SECRET_KEYWORD"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        json.dumps(
            {
                "queries": [
                    {
                        "candidate_key": " ",
                        "subject_name": "数学",
                        "keywords": [""],
                    }
                ]
            },
            ensure_ascii=False,
        ),
    ],
)
def test_provider_asks_model_to_fix_invalid_tool_arguments_in_same_loop(invalid_arguments, caplog):
    valid_arguments = json.dumps(
        {
            "queries": [
                {
                    "candidate_key": "分数",
                    "subject_name": "数学",
                    "keywords": ["分数"],
                }
            ]
        },
        ensure_ascii=False,
    )
    responses = [
        SimpleNamespace(
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "invalid-call",
                    "arguments": invalid_arguments,
                }
            ],
        ),
        SimpleNamespace(
            output_text="",
            output=[
                {
                    "type": "function_call",
                    "name": "search_history_items",
                    "call_id": "valid-call",
                    "arguments": valid_arguments,
                }
            ],
        ),
        SimpleNamespace(
            output_text=json.dumps(result(item("分数", kind="new")), ensure_ascii=False),
            output=[],
        ),
    ]
    inputs = []

    def respond(**kwargs):
        inputs.append(json.loads(json.dumps(kwargs["input"], ensure_ascii=False)))
        return responses.pop(0)

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))
    searched = []
    caplog.set_level(logging.INFO, logger="push_kids.analysis")

    proposal = provider.analyze_with_history(
        AnalysisInput(text="分数", existing_subjects=["数学", "语文"]),
        lambda request: searched.append(request) or [],
        max_turns=8,
        trace=AnalysisTrace(job_id="job-safe", attempt=1),
    )

    assert [point.name for point in proposal.knowledge_points] == ["分数"]
    assert len(inputs) == 3
    assert [request.candidate_key for request in searched] == ["分数"]
    correction = json.dumps(inputs[1], ensure_ascii=False)
    assert "tool.arguments" in correction
    tool_outputs = [
        value
        for value in inputs[1]
        if isinstance(value, dict) and value.get("type") == "function_call_output"
    ]
    assert json.loads(tool_outputs[0]["output"]) == {"error": "tool.arguments"}
    assert "SECRET" not in caplog.text


def test_provider_refuses_to_start_after_attempt_deadline():
    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(
        responses=SimpleNamespace(create=lambda **_kwargs: pytest.fail("must not call provider"))
    )

    with pytest.raises(AnalysisDeadlineExceededError):
        provider.analyze_with_history(
            AnalysisInput(text="分数", existing_subjects=["数学"]),
            lambda _request: [],
            max_turns=8,
            deadline=0,
        )


def test_trace_normalizes_dynamic_validation_paths(caplog):
    caplog.set_level(logging.INFO, logger="push_kids.analysis")
    trace = AnalysisTrace(job_id="job-safe", attempt=1)

    trace.info(
        "analysis_validation_failed",
        turn=1,
        validation_codes=["schema.subjects.数学.SECRET_FIELD", "SECRET_RAW_CODE"],
        reason="output_validation",
    )

    assert "validation_codes=schema.fields,validation.other" in caplog.text
    assert "数学" not in caplog.text
    assert "SECRET" not in caplog.text


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


def test_model_output_is_limited_to_twenty_without_a_per_subject_cap():
    data = AnalysisInput(text="练习", existing_subjects=["数学", "语文"])
    allowed = result(*[item(f"数学知识{index}") for index in range(12)])
    allowed["subjects"]["语文"] = [item(f"语文知识{index}") for index in range(8)]
    proposal = data.validate_model_result(ModelAnalysisResult.model_validate(allowed))
    assert len(proposal.knowledge_points) == 20

    seven = result(*[item(f"数学知识{index}") for index in range(12)])
    seven["subjects"]["语文"] = [item(f"语文知识{index}") for index in range(9)]
    with pytest.raises(AnalysisOutputValidationError) as total_error:
        data.validate_model_result(ModelAnalysisResult.model_validate(seven))
    assert total_error.value.codes == ["subjects.max_items"]


def test_active_future_review_is_a_valid_review_reference():
    data = AnalysisInput(
        text="今天提前复习了分数",
        existing_subjects=["数学", "语文"],
        existing_knowledge=[
            {
                "knowledge_id": "knowledge-1",
                "review_id": "review-1",
                "subject_name": "数学",
                "name": "分数初步认识",
                "category": "概念",
                "review_step": 2,
                "review_due_date": "2026-09-20",
                "review_active": True,
            }
        ],
    )
    review = item("分数初步认识", kind="review", review_id="review-1")
    review["existing_knowledge_id"] = "knowledge-1"

    proposal = data.validate_model_result(ModelAnalysisResult.model_validate(result(review)))

    assert proposal.knowledge_points == []
    assert proposal.todo_matches[0].review_id == "review-1"
    assert proposal.todo_matches[0].due_date == "2026-09-20"


def test_same_day_review_requires_an_explicit_parent_note():
    data = AnalysisInput(
        text="又做了一页分数题",
        existing_subjects=["数学", "语文"],
        same_day_learning=[
            {
                "knowledge_id": "knowledge-1",
                "subject_name": "数学",
                "name": "分数初步认识",
                "category": "概念",
            }
        ],
        existing_knowledge=[
            {
                "knowledge_id": "knowledge-1",
                "review_id": "review-1",
                "subject_name": "数学",
                "name": "分数初步认识",
                "category": "概念",
                "review_step": 0,
                "review_due_date": "2026-09-20",
                "review_active": True,
            }
        ],
    )
    review = item("分数初步认识", kind="review", review_id="review-1")
    review["existing_knowledge_id"] = "knowledge-1"

    omitted = data.validate_model_result(ModelAnalysisResult.model_validate(result(review)))
    allowed = data.model_copy(update={"text": "今天单独复习了分数"}).validate_model_result(
        ModelAnalysisResult.model_validate(result(review))
    )

    assert omitted.todo_matches == []
    assert any("当天已确认" in message for message in omitted.uncertainties)
    assert [match.review_id for match in allowed.todo_matches] == ["review-1"]
