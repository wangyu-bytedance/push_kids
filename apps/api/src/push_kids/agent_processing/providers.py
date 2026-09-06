from __future__ import annotations

import base64
import json
import mimetypes
from hashlib import sha256
from pathlib import Path
from typing import Any

from openai import BadRequestError, OpenAI
from pydantic import ValidationError

from push_kids.agent_processing.contracts import (
    AnalysisCapabilityError,
    AnalysisInput,
    AnalysisOutputExhaustedError,
    AnalysisOutputValidationError,
    AnalysisProposal,
    EvidenceReference,
    KnowledgeProposal,
    ModelAnalysisResult,
    infer_display_kind,
)
from push_kids.agent_processing.prompt import ANALYSIS_RULES, PROMPT_REVISION
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.platform.config import Settings
from push_kids.platform.errors import DependencyError


class DeterministicTestProvider:
    """Deterministic provider available only in the explicit test environment."""

    def analyze(self, data: AnalysisInput) -> AnalysisProposal:
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
            for point in raw_points[:8]
        ]
        summary = f"整理了{subject}学习内容：" + "、".join(point.name for point in points[:3])
        normalized_text = normalize_knowledge_name(text)
        matches = [
            candidate.model_copy(update={"evidence": "自动化测试输入"})
            for candidate in data.todo_candidates
            if normalize_knowledge_name(candidate.knowledge_name) in normalized_text
        ]
        reviewed_names = {
            (candidate.subject_name or subject, normalize_knowledge_name(candidate.knowledge_name))
            for candidate in matches
        }
        same_day_names = {
            (item.subject_name, normalize_knowledge_name(item.name))
            for item in data.same_day_learning
        }
        points = [
            point
            for point in points
            if (point.subject_name or subject, normalize_knowledge_name(point.name))
            not in reviewed_names | same_day_names
        ]
        return AnalysisProposal(
            summary=summary[:120],
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
        return {"英语": "听说与拼写", "数学": "口算与讲解", "语文": "认读与听写"}[subject]


class ArkAnalysisProvider:
    def __init__(self, settings: Settings) -> None:
        self.client = (
            OpenAI(
                base_url=settings.ark_base_url,
                api_key=settings.ark_api_key.get_secret_value(),
            )
            if settings.ark_api_key
            else None
        )
        self.model = settings.ark_model

    def analyze(self, data: AnalysisInput) -> AnalysisProposal:
        if self.client is None:
            raise DependencyError("学习内容分析尚未配置，请设置 ARK_API_KEY 后重试")
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

    @staticmethod
    def _data_url(path: Path) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def _prompt(data: AnalysisInput, validation_codes: list[str] | None = None) -> str:
        candidates_json = json.dumps(
            [item.model_dump() for item in data.todo_candidates], ensure_ascii=False
        )
        recent_json = json.dumps(
            [item.model_dump() for item in data.recent_learning], ensure_ascii=False
        )
        knowledge_json = json.dumps(
            [item.model_dump() for item in data.existing_knowledge], ensure_ascii=False
        )
        same_day_json = json.dumps(
            [item.model_dump() for item in data.same_day_learning], ensure_ascii=False
        )
        feedback = (
            "上次输出未通过校验，仅修正这些字段路径/规则代码："
            + json.dumps(validation_codes, ensure_ascii=False)
            + "。"
            if validation_codes
            else ""
        )
        return (
            f"规则版本：{PROMPT_REVISION}。{ANALYSIS_RULES}\n"
            f"孩子已有科目：{json.dumps(data.existing_subjects, ensure_ascii=False)}。"
            f"本次实际发生时间：{data.occurred_at or '未提供'}。"
            f"年级：{data.grade or '未提供，不推断'}。"
            f"已有知识及计划状态：{knowledge_json}。"
            f"近期已确认学习上下文：{recent_json}。"
            f"本次发生日已经确认的学习条目（必须去重）：{same_day_json}。"
            f"今日可复习Todo候选（只有这些可以标记review）：{candidates_json}。"
            f"{feedback}"
            f"家长补充文字：{data.text or '无'}"
        )


def build_provider(settings: Settings):
    if settings.ai_provider == "test":
        if settings.env not in {"test", "e2e"}:
            raise DependencyError("test Provider 只能在 PUSH_KIDS_ENV=test/e2e 使用")
        return DeterministicTestProvider()
    return ArkAnalysisProvider(settings)
