from __future__ import annotations

import base64
import json
import mimetypes
import re
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path
from time import monotonic, time
from typing import Annotated, Any

from openai import BadRequestError, OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from push_kids.agent_processing.contracts import (
    AnalysisCapabilityError,
    AnalysisDeadlineExceededError,
    AnalysisInput,
    AnalysisInputError,
    AnalysisOutputExhaustedError,
    AnalysisOutputValidationError,
    AnalysisProposal,
    EvidenceReference,
    KnowledgeProposal,
    ModelAnalysisResult,
    TodoCandidate,
    explicit_same_day_review,
    infer_display_kind,
)
from push_kids.agent_processing.history_search import HistorySearchRequest
from push_kids.agent_processing.prompt import ANALYSIS_RULES, PROMPT_REVISION
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.platform.config import Settings
from push_kids.platform.errors import DependencyError


class DeterministicTestProvider:
    """Deterministic provider available only in the explicit test environment."""

    def analyze(self, data: AnalysisInput) -> AnalysisProposal:
        """Legacy one-shot fallback used by old test doubles and rollback tests."""
        return self._analyze(data, None)

    def analyze_with_history(
        self,
        data: AnalysisInput,
        search_history: Callable[[HistorySearchRequest], list[dict[str, object]]],
        *,
        max_turns: int,
        trace: AnalysisTrace | None = None,
        deadline: float | None = None,
    ) -> AnalysisProposal:
        del max_turns, trace, deadline
        return self._analyze(data, search_history)

    def _analyze(
        self,
        data: AnalysisInput,
        search_history: Callable[[HistorySearchRequest], list[dict[str, object]]] | None,
    ) -> AnalysisProposal:
        text = (data.text or "").strip()
        subject = self._subject(text)
        separators = str.maketrans({",": "\n", "，": "\n", "。": "\n", "；": "\n", ";": "\n"})
        raw_points = [
            part.strip() for part in text.translate(separators).splitlines() if part.strip()
        ]
        if not raw_points:
            raw_points = ["图片中的学习内容"]
        points = [
            KnowledgeProposal(
                name=point[:120],
                category=self._category(subject),
                display_kind=infer_display_kind(point[:120], self._category(subject)),
                review_method=self._method(subject),
                estimated_minutes=3,
                direct_evidence=[
                    EvidenceReference(
                        source="parent_text" if text else "image",
                        image_index=None if text else 1,
                        detail="自动化测试输入",
                    )
                ],
                confidence="high",
                subject_name=subject,
            )
            for point in raw_points[:20]
        ]
        summary = f"整理了{subject}学习内容：" + "、".join(point.name for point in points[:3])
        matches: list[TodoCandidate] = [
            candidate.model_copy(update={"evidence": "自动化测试输入"})
            for candidate in data.todo_candidates
            if _names_overlap(candidate.knowledge_name, text)
        ]
        reviewed_names = {
            (candidate.subject_name or subject, normalize_knowledge_name(candidate.knowledge_name))
            for candidate in matches
        }
        same_day_names = {
            (item.subject_name, normalize_knowledge_name(item.name))
            for item in data.same_day_learning
        }
        if not explicit_same_day_review(data.text):
            matches = [
                candidate
                for candidate in matches
                if (
                    candidate.subject_name or subject,
                    normalize_knowledge_name(candidate.knowledge_name),
                )
                not in same_day_names
            ]
        deduplicated_same_day = set() if explicit_same_day_review(data.text) else same_day_names
        remaining: list[KnowledgeProposal] = []
        for point in points:
            point_key = (point.subject_name or subject, normalize_knowledge_name(point.name))
            if any(
                point_key[0] == known_subject
                and (known_name in point_key[1] or point_key[1] in known_name)
                for known_subject, known_name in reviewed_names | deduplicated_same_day
            ):
                continue
            historical: list[dict[str, object]] = []
            if search_history is not None:
                historical = search_history(
                    HistorySearchRequest(
                        candidate_key=point.name,
                        subject_name=point.subject_name or subject,
                        keywords=tuple(_search_keywords(point.name)),
                    )
                )
            match = next(
                (
                    item
                    for item in historical
                    if _names_overlap(str(item.get("name", "")), point.name)
                ),
                None,
            )
            if match is not None:
                matches.append(
                    TodoCandidate(
                        review_id=match.get("review_id") or None,
                        knowledge_id=str(match["knowledge_id"]),
                        knowledge_name=str(match["name"]),
                        subject_name=str(match["subject_name"]),
                        step=match.get("review_step"),
                        due_date=match.get("review_due_date"),
                        match_kind="history_item",
                        state_version=match.get("state_version"),
                        last_reviewed_on=match.get("last_reviewed_on"),
                        review_count=match.get("review_count"),
                        evidence="自动化测试输入",
                    )
                )
                continue
            remaining.append(point)
        points = remaining
        return AnalysisProposal(
            summary=summary[:60],
            subject_name=subject,
            source="手动记录" if text else "图片记录",
            knowledge_points=points,
            todo_matches=matches,
        )

    @staticmethod
    def _subject(text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ("英语", "english", "单词", "phonics")):
            return "英语"
        if any(word in lowered for word in ("数学", "加法", "减法", "乘法", "除法", "分数")):
            return "数学"
        return "语文"

    @staticmethod
    def _category(subject: str) -> str:
        return {"英语": "词汇与表达", "数学": "计算与概念", "语文": "字词与阅读"}[subject]

    @staticmethod
    def _method(subject: str) -> str:
        return {"英语": "主动回忆", "数学": "变式练习", "语文": "主动回忆"}[subject]


def _names_overlap(left: str, right: str) -> bool:
    left_name = normalize_knowledge_name(left)
    right_name = normalize_knowledge_name(right)
    return bool(left_name and right_name and (left_name in right_name or right_name in left_name))


def _search_keywords(name: str) -> list[str]:
    values = [name]
    cleaned = re.sub(r"^(?:复习|学习|练习|再次练习)[：:、\s]*", "", name).strip()
    if cleaned and cleaned != name:
        values.append(cleaned)
    return list(dict.fromkeys(values))[:8]


class _HistorySearchToolQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    candidate_key: str = Field(min_length=1, max_length=120, pattern=r".*\S.*")
    subject_name: str = Field(min_length=1, max_length=40, pattern=r".*\S.*")
    keywords: list[Annotated[str, Field(min_length=1, max_length=40, pattern=r".*\S.*")]] = Field(
        min_length=1, max_length=8
    )


class _HistorySearchToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    queries: list[_HistorySearchToolQuery] = Field(min_length=1, max_length=20)


def _parse_history_tool_calls(
    calls: list[dict[str, object]],
    existing_subjects: list[str],
) -> list[tuple[dict[str, object], _HistorySearchToolArguments]]:
    parsed: list[tuple[dict[str, object], _HistorySearchToolArguments]] = []
    for call in calls:
        if call.get("name") != "search_history_items":
            raise AnalysisOutputValidationError(["tool.name"])
        try:
            arguments = _HistorySearchToolArguments.model_validate_json(
                str(call.get("arguments") or "{}")
            )
        except ValidationError as exc:
            raise AnalysisOutputValidationError(["tool.arguments"]) from exc
        if any(query.subject_name not in existing_subjects for query in arguments.queries):
            raise AnalysisOutputValidationError(["tool.arguments"])
        parsed.append((call, arguments))
    return parsed


def _response_cached_tokens(response: object) -> int | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    usage_model_dump = getattr(usage, "model_dump", None)
    if callable(usage_model_dump):
        usage = usage_model_dump(exclude_none=True)
    if not isinstance(usage, dict):
        return None
    for key in ("input_tokens_details", "prompt_tokens_details"):
        details = usage.get(key)
        details_model_dump = getattr(details, "model_dump", None)
        if callable(details_model_dump):
            details = details_model_dump(exclude_none=True)
        if not isinstance(details, dict):
            continue
        value = details.get("cached_tokens")
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    return None


class ArkAnalysisProvider:
    _CONTEXT_TTL_SECONDS = 600
    _CLEANUP_TIMEOUT_SECONDS = 0.5

    def __init__(self, settings: Settings) -> None:
        self.client = (
            OpenAI(
                base_url=settings.ark_base_url,
                api_key=settings.ark_api_key.get_secret_value(),
                max_retries=0,
            )
            if settings.ark_api_key
            else None
        )
        self.model = settings.ark_model
        self.context_cache_enabled = settings.ark_context_cache_enabled

    def _cleanup_context_session(
        self,
        response_ids: list[str],
        trace: AnalysisTrace,
    ) -> None:
        if self.client is None or not response_ids:
            return
        deleted = 0
        failed = False
        for response_id in reversed(response_ids):
            try:
                self.client.responses.delete(
                    response_id,
                    timeout=self._CLEANUP_TIMEOUT_SECONDS,
                )
                deleted += 1
            except Exception:
                failed = True
        event = (
            "analysis_context_session_cleanup_failed"
            if failed
            else "analysis_context_session_cleanup_completed"
        )
        emit = trace.warning if failed else trace.info
        emit(
            event,
            context_mode="session",
            request_count=len(response_ids),
            cleanup_count=deleted,
            reason="provider_delete" if failed else "completed",
        )

    def analyze(self, data: AnalysisInput) -> AnalysisProposal:
        if self.client is None:
            raise AnalysisInputError("学习内容分析尚未配置，请设置 ARK_API_KEY 后重试")
        content: list[dict[str, str]] = []
        seen_images: dict[str, int] = {}
        for index, path in enumerate(data.image_paths, start=1):
            digest = sha256(path.read_bytes()).hexdigest()
            if digest in seen_images:
                content.append(
                    {
                        "type": "input_text",
                        "text": (
                            f"照片{index}与照片{seen_images[digest]}字节完全相同，"
                            f"证据统一引用照片{seen_images[digest]}。"
                        ),
                    }
                )
                continue
            seen_images[digest] = index
            content.append(
                {
                    "type": "input_text",
                    "text": f"以下是原始照片{index}，证据image_index使用{index}。",
                }
            )
            content.append({"type": "input_image", "image_url": self._data_url(path)})
        validation_codes: list[str] = []
        for _attempt in range(3):
            attempt_content = list(content)
            attempt_content.append(
                {
                    "type": "input_text",
                    "text": self._prompt(data, validation_codes),
                }
            )
            try:
                provider_input: Any = [{"role": "user", "content": attempt_content}]
                response = self.client.responses.create(
                    model=self.model,
                    input=provider_input,
                    store=False,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "subject_grouped_learning_analysis",
                            "strict": True,
                            "schema": data.structured_output_schema(),
                        }
                    },
                )
                if getattr(response, "status", "completed") != "completed":
                    raise DependencyError("学习内容分析未完整返回，请稍后重试")
                raw = response.output_text.strip()
                result = ModelAnalysisResult.model_validate(json.loads(raw))
                return data.validate_model_result(result)
            except BadRequestError as exc:
                raise AnalysisCapabilityError() from exc
            except json.JSONDecodeError:
                validation_codes = ["json.parse"]
            except ValidationError as exc:
                validation_codes = [
                    "schema." + ".".join(str(part) for part in error["loc"])
                    for error in exc.errors()[:20]
                ]
            except AnalysisOutputValidationError as exc:
                validation_codes = exc.codes
            except (AnalysisCapabilityError, AnalysisOutputExhaustedError):
                raise
            except Exception as exc:
                raise DependencyError("学习内容分析暂时失败，请稍后重试") from exc
        raise AnalysisOutputExhaustedError()

    def analyze_with_history(
        self,
        data: AnalysisInput,
        search_history: Callable[[HistorySearchRequest], list[dict[str, object]]],
        *,
        max_turns: int,
        trace: AnalysisTrace | None = None,
        deadline: float | None = None,
    ) -> AnalysisProposal:
        """Run a bounded Responses tool loop with optional attempt-local session reuse."""
        if self.client is None:
            raise AnalysisInputError("学习内容分析尚未配置，请设置 ARK_API_KEY 后重试")
        trace = trace or AnalysisTrace.disabled()
        session_enabled = bool(getattr(self, "context_cache_enabled", False))
        context_mode = "session" if session_enabled else "stateless"
        response_ids: list[str] = []
        previous_response_id: str | None = None
        content: list[dict[str, str]] = []
        seen_images: dict[str, int] = {}
        for index, path in enumerate(data.image_paths, start=1):
            digest = sha256(path.read_bytes()).hexdigest()
            if digest in seen_images:
                content.append(
                    {
                        "type": "input_text",
                        "text": (
                            f"照片{index}与照片{seen_images[digest]}字节完全相同，"
                            f"证据统一引用照片{seen_images[digest]}。"
                        ),
                    }
                )
                continue
            seen_images[digest] = index
            content.append(
                {
                    "type": "input_text",
                    "text": f"以下是原始照片{index}，证据image_index使用{index}。",
                }
            )
            content.append({"type": "input_image", "image_url": self._data_url(path)})
        content.append({"type": "input_text", "text": self._prompt(data)})
        provider_input: Any = [{"role": "user", "content": content}]
        tools: Any = [
            {
                "type": "function",
                "name": "search_history_items",
                "description": "按科目和关键词检索该孩子的历史知识候选；只用于判断是否为历史复习。",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "queries": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 20,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "candidate_key": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 120,
                                    },
                                    "subject_name": {
                                        "type": "string",
                                        "enum": list(data.existing_subjects),
                                    },
                                    "keywords": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 40,
                                        },
                                        "minItems": 1,
                                        "maxItems": 8,
                                    },
                                },
                                "required": ["candidate_key", "subject_name", "keywords"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["queries"],
                    "additionalProperties": False,
                },
            }
        ]
        validation_codes: list[str] = []
        total_logical_calls = 0
        total_results = 0
        try:
            for turn in range(1, max_turns + 1):
                remaining_ms = (
                    max(0, int((deadline - monotonic()) * 1000)) if deadline is not None else 0
                )
                if deadline is not None and remaining_ms <= 0:
                    trace.warning(
                        "analysis_generation_failed",
                        turn=turn,
                        max_turns=max_turns,
                        remaining_turns=max_turns - turn,
                        remaining_time_ms=0,
                        context_mode=context_mode,
                        reason="time_budget",
                    )
                    raise AnalysisDeadlineExceededError()
                trace.info(
                    "analysis_generation_started",
                    turn=turn,
                    max_turns=max_turns,
                    remaining_turns=max_turns - turn + 1,
                    remaining_time_ms=remaining_ms,
                    context_mode=context_mode,
                    total_logical_calls=total_logical_calls,
                    total_results=total_results,
                    validation_codes=validation_codes,
                )
                started = monotonic()
                request_kwargs: Any = {
                    "model": self.model,
                    "input": provider_input,
                    "store": session_enabled,
                    "tools": tools,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": "subject_grouped_learning_analysis",
                            "strict": True,
                            "schema": data.structured_output_schema(),
                        }
                    },
                }
                if session_enabled:
                    request_kwargs["extra_body"] = {
                        "expire_at": int(time()) + self._CONTEXT_TTL_SECONDS
                    }
                    if previous_response_id is not None:
                        request_kwargs["previous_response_id"] = previous_response_id
                if turn == max_turns:
                    request_kwargs["tool_choice"] = "none"
                if deadline is not None:
                    request_kwargs["timeout"] = max(0.001, remaining_ms / 1000)
                try:
                    response = self.client.responses.create(**request_kwargs)
                except Exception:
                    trace.warning(
                        "analysis_generation_failed",
                        turn=turn,
                        max_turns=max_turns,
                        remaining_turns=max_turns - turn,
                        remaining_time_ms=max(
                            0,
                            int((deadline - monotonic()) * 1000),
                        )
                        if deadline is not None
                        else 0,
                        duration_ms=int((monotonic() - started) * 1000),
                        context_mode=context_mode,
                        reason="provider_call",
                    )
                    raise
                cached_tokens = _response_cached_tokens(response)
                if session_enabled:
                    response_id = getattr(response, "id", None)
                    if not isinstance(response_id, str) or not response_id:
                        raise DependencyError("学习内容分析会话未返回有效标识，请稍后重试")
                    response_ids.append(response_id)
                    previous_response_id = response_id
                output_items = [
                    item.model_dump(exclude_none=True)
                    if hasattr(item, "model_dump")
                    else dict(item)
                    for item in getattr(response, "output", [])
                ]
                calls = [item for item in output_items if item.get("type") == "function_call"]
                status = (
                    "completed"
                    if getattr(response, "status", "completed") == "completed"
                    else "incomplete"
                )
                if status != "completed":
                    trace.warning(
                        "analysis_generation_failed",
                        turn=turn,
                        max_turns=max_turns,
                        remaining_turns=max_turns - turn,
                        remaining_time_ms=max(
                            0,
                            int((deadline - monotonic()) * 1000),
                        )
                        if deadline is not None
                        else 0,
                        context_mode=context_mode,
                        reason="incomplete",
                    )
                    raise DependencyError("学习内容分析未完整返回，请稍后重试")
                if calls:
                    if turn == max_turns:
                        trace.warning(
                            "analysis_generation_failed",
                            turn=turn,
                            max_turns=max_turns,
                            remaining_turns=0,
                            remaining_time_ms=max(
                                0,
                                int((deadline - monotonic()) * 1000),
                            )
                            if deadline is not None
                            else 0,
                            duration_ms=int((monotonic() - started) * 1000),
                            context_mode=context_mode,
                            reason="final_turn_tool_call",
                        )
                        raise AnalysisOutputExhaustedError(
                            reason="final_turn_tool_call",
                            codes=["tool.final_turn"],
                        )
                    if session_enabled:
                        provider_input = []
                    else:
                        provider_input.extend(output_items)
                    try:
                        parsed_calls = _parse_history_tool_calls(calls, data.existing_subjects)
                    except AnalysisOutputValidationError as exc:
                        validation_codes = exc.codes
                        for call in calls:
                            provider_input.append(
                                {
                                    "type": "function_call_output",
                                    "call_id": str(call.get("call_id") or ""),
                                    "output": json.dumps(
                                        {"error": validation_codes[0]},
                                        ensure_ascii=False,
                                        separators=(",", ":"),
                                    ),
                                }
                            )
                        trace.info(
                            "analysis_generation_completed",
                            turn=turn,
                            max_turns=max_turns,
                            remaining_turns=max_turns - turn,
                            remaining_time_ms=max(
                                0,
                                int((deadline - monotonic()) * 1000),
                            )
                            if deadline is not None
                            else 0,
                            duration_ms=int((monotonic() - started) * 1000),
                            context_mode=context_mode,
                            cached_tokens=cached_tokens,
                            status=status,
                            response_kind="tool",
                            output_items=len(output_items),
                            logical_calls=0,
                            total_logical_calls=total_logical_calls,
                            total_results=total_results,
                        )
                        trace.warning(
                            "analysis_validation_failed",
                            turn=turn,
                            validation_codes=validation_codes,
                            reason="tool_arguments",
                        )
                        provider_input.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_text",
                                        "text": (
                                            "工具参数未通过校验，仅修正规则代码："
                                            + json.dumps(validation_codes, ensure_ascii=False)
                                        ),
                                    }
                                ],
                            }
                        )
                        continue
                    turn_logical_calls = 0
                    for call, arguments in parsed_calls:
                        queries = arguments.queries
                        trace.info(
                            "analysis_history_batch_started",
                            turn=turn,
                            request_count=len(queries),
                            total_logical_calls=total_logical_calls,
                            total_results=total_results,
                        )
                        batch_results: list[dict[str, object]] = []
                        batch_result_count = 0
                        try:
                            for query in queries:
                                request = HistorySearchRequest(
                                    candidate_key=query.candidate_key,
                                    subject_name=query.subject_name,
                                    keywords=tuple(query.keywords),
                                )
                                tool_result = search_history(request)
                                total_logical_calls += 1
                                batch_result_count += len(tool_result)
                                total_results += len(tool_result)
                                batch_results.append(
                                    {
                                        "candidate_key": request.candidate_key,
                                        "items": tool_result,
                                    }
                                )
                        except Exception:
                            trace.warning(
                                "analysis_history_batch_failed",
                                turn=turn,
                                request_count=len(queries),
                                total_logical_calls=total_logical_calls,
                                total_results=total_results,
                                reason="validation",
                            )
                            trace.warning(
                                "analysis_generation_failed",
                                turn=turn,
                                reason="tool_execution",
                            )
                            raise
                        trace.info(
                            "analysis_history_batch_completed",
                            turn=turn,
                            request_count=len(queries),
                            result_count=batch_result_count,
                            total_logical_calls=total_logical_calls,
                            total_results=total_results,
                        )
                        turn_logical_calls += len(queries)
                        provider_input.append(
                            {
                                "type": "function_call_output",
                                "call_id": str(call.get("call_id") or ""),
                                "output": json.dumps(
                                    {"queries": batch_results},
                                    ensure_ascii=False,
                                    separators=(",", ":"),
                                ),
                            }
                        )
                    trace.info(
                        "analysis_generation_completed",
                        turn=turn,
                        max_turns=max_turns,
                        remaining_turns=max_turns - turn,
                        remaining_time_ms=max(
                            0,
                            int((deadline - monotonic()) * 1000),
                        )
                        if deadline is not None
                        else 0,
                        duration_ms=int((monotonic() - started) * 1000),
                        context_mode=context_mode,
                        cached_tokens=cached_tokens,
                        status=status,
                        response_kind="tool",
                        output_items=len(output_items),
                        logical_calls=turn_logical_calls,
                        total_logical_calls=total_logical_calls,
                        total_results=total_results,
                    )
                    continue
                trace.info(
                    "analysis_generation_completed",
                    turn=turn,
                    max_turns=max_turns,
                    remaining_turns=max_turns - turn,
                    remaining_time_ms=max(
                        0,
                        int((deadline - monotonic()) * 1000),
                    )
                    if deadline is not None
                    else 0,
                    duration_ms=int((monotonic() - started) * 1000),
                    context_mode=context_mode,
                    cached_tokens=cached_tokens,
                    status=status,
                    response_kind="final",
                    output_items=len(output_items),
                    logical_calls=0,
                    total_logical_calls=total_logical_calls,
                    total_results=total_results,
                )
                raw = response.output_text.strip()
                try:
                    model_result = ModelAnalysisResult.model_validate(json.loads(raw))
                    return data.validate_model_result(model_result)
                except json.JSONDecodeError:
                    validation_codes = ["json.parse"]
                except ValidationError as exc:
                    validation_codes = [
                        "schema." + ".".join(str(part) for part in error["loc"])
                        for error in exc.errors()[:20]
                    ]
                except AnalysisOutputValidationError as exc:
                    validation_codes = exc.codes
                trace.warning(
                    "analysis_validation_failed",
                    turn=turn,
                    validation_codes=validation_codes,
                    reason="output_validation",
                )
                if session_enabled:
                    provider_input = []
                else:
                    provider_input.extend(output_items)
                provider_input.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "上次输出未通过校验，仅修正规则代码："
                                    + json.dumps(validation_codes, ensure_ascii=False)
                                ),
                            }
                        ],
                    }
                )
        except BadRequestError as exc:
            raise AnalysisCapabilityError() from exc
        except (
            AnalysisCapabilityError,
            AnalysisDeadlineExceededError,
            AnalysisOutputExhaustedError,
        ):
            raise
        except AnalysisOutputValidationError:
            raise
        except Exception as exc:
            raise DependencyError("学习内容分析暂时失败，请稍后重试") from exc
        finally:
            if session_enabled:
                self._cleanup_context_session(response_ids, trace)
        raise AnalysisOutputExhaustedError(
            reason="output_validation" if validation_codes else "turn_budget",
            codes=validation_codes,
        )

    @staticmethod
    def _data_url(path: Path) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def _prompt(data: AnalysisInput, validation_codes: list[str] | None = None) -> str:
        def compact_json(value: object) -> str:
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

        candidates_json = compact_json([item.model_dump() for item in data.todo_candidates])
        same_day_json = compact_json([item.model_dump() for item in data.same_day_learning])
        feedback = (
            "上次输出未通过校验，仅修正这些字段路径/规则代码："
            + json.dumps(validation_codes, ensure_ascii=False)
            + "。"
            if validation_codes
            else ""
        )
        return (
            f"规则版本：{PROMPT_REVISION}。{ANALYSIS_RULES}\n"
            f"孩子学习档案：年级={data.grade or '未填写，不推断'}；"
            f"已配置学习科目={compact_json(data.existing_subjects)}。"
            f"本次实际发生时间：{data.occurred_at or '未提供'}。"
            f"today_review_plan（今日完整计划，最多120项，只是匹配上下文）：{candidates_json}。"
            f"same_day_knowledge_refs（本次发生日已确认，必须去重）：{same_day_json}。"
            "历史知识不在首轮上下文中；对每个未由上述两类上下文匹配的候选，"
            "必须调用search_history_items后才能判为new或history_item。"
            f"{feedback}"
            f"家长补充文字：{data.text or '无'}"
        )


def build_provider(settings: Settings):
    if settings.ai_provider == "test":
        if settings.env not in {"test", "e2e"}:
            raise DependencyError("test Provider 只能在 PUSH_KIDS_ENV=test/e2e 使用")
        return DeterministicTestProvider()
    return ArkAnalysisProvider(settings)
