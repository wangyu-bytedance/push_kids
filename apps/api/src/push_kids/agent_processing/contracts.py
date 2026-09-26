from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from push_kids.knowledge.normalization import normalize_knowledge_name

MATERIAL_FINGERPRINT_KEY = "_analysis_material_fingerprint"
MODEL_SUMMARY_MAX_LENGTH = 60
MODEL_SUMMARY_FALLBACK = "请确认识别出的学习与复习条目"
_SUMMARY_EXCLUSION_PATTERNS = (
    re.compile(r"(?:不|未)(?:包含|涉及)"),
    re.compile(r"(?:没有|未)(?:识别到|发现|提取到)"),
    re.compile(r"没有[^。！？!?]{0,40}(?:任务|内容|知识)"),
    re.compile(r"无(?:语文|数学|英语|其他学科|相关)[^。！？!?]{0,30}(?:任务|内容|知识|学习)"),
)
_RUNTIME_UNCERTAINTY_ENTITY = re.compile(
    r"(?:历史知识检索|工具|接口|API|数据库|系统|服务)", re.IGNORECASE
)
_RUNTIME_UNCERTAINTY_FAILURE = re.compile(
    r"(?:失败|异常|不可用|超时|未成功|没有成功|无法|不能|未能)", re.IGNORECASE
)

DisplayKind = Literal[
    "hanzi",
    "word",
    "poem",
    "arithmetic",
    "concept",
    "activity",
    "other",
]
ReviewMethod = Literal["主动回忆", "变式练习", "解释应用"]


def infer_display_kind(name: str, category: str) -> DisplayKind:
    """Map legacy/free-form categories into the bounded parent-facing vocabulary."""
    normalized_name = normalize_knowledge_name(name)
    normalized_category = normalize_knowledge_name(category)
    combined = f"{normalized_category} {normalized_name}"
    if any(token in normalized_category for token in ("汉字", "生字")):
        return "hanzi"
    if any(token in normalized_category for token in ("单词", "词汇")):
        return "word"
    if any(token in combined for token in ("古诗", "诗词")) or name.strip().startswith("《"):
        return "poem"
    if any(token in combined for token in ("运算", "计算", "加法", "减法", "乘法", "除法", "口算")):
        return "arithmetic"
    if "活动" in normalized_category:
        return "activity"
    if normalized_category in {"", "其他"}:
        return "other"
    return "concept"


class KnowledgeProposal(BaseModel):
    existing_knowledge_id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    # Which subject this single point belongs to. Set when one batch of photos spans several
    # subjects; empty means "the batch subject". Never a merged label like "数学、语文".
    subject_name: str | None = Field(default=None, max_length=40)
    category: str = Field(default="知识点", max_length=50)
    display_kind: DisplayKind | None = None
    review_method: str = Field(default="口头回顾", max_length=60)
    estimated_minutes: int = Field(default=3, ge=1, le=20)
    direct_evidence: list[EvidenceReference] = Field(default_factory=list, max_length=20)
    context_used: list[str] = Field(default_factory=list, max_length=20)
    confidence: str = Field(default="medium", pattern="^(high|medium|low)$")


class EvidenceReference(BaseModel):
    source: str = Field(pattern="^(image|parent_text)$")
    image_index: int | None = Field(default=None, ge=1, le=9)
    detail: str = Field(min_length=1, max_length=200)


class TodoCandidate(BaseModel):
    review_id: str | None = None
    knowledge_name: str
    knowledge_id: str | None = None
    subject_name: str | None = None
    evidence: str | None = Field(default=None, max_length=200)
    step: int | None = None
    due_date: str | None = None
    eligible_on: str | None = None
    match_kind: Literal["today_review", "history_item"] = "today_review"
    state_version: int | None = None
    last_reviewed_on: str | None = None
    review_count: int | None = None
    plan_state: str | None = None


class ExistingKnowledgeContext(BaseModel):
    knowledge_id: str
    review_id: str | None = None
    subject_name: str
    name: str
    category: str
    review_step: int | None = None
    review_due_date: str | None = None
    review_active: bool | None = None
    last_reviewed_on: str | None = None
    review_count: int | None = None
    state_version: int | None = None
    match_signals: list[str] = Field(default_factory=list, max_length=8)


class RecentLearningContext(BaseModel):
    record_id: str
    subject_name: str
    summary: str = Field(max_length=500)
    occurred_at: str


class SameDayKnowledgeContext(BaseModel):
    knowledge_id: str
    subject_name: str
    name: str
    category: str


class ModelEvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["image", "parent_text"]
    image_index: int | None = Field(ge=1, le=9)
    detail: str = Field(min_length=1, max_length=200)


class ModelLearningItem(BaseModel):
    """One item in the provider-only, strict subject-grouped response."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["new", "today_review", "history_item", "new_learning", "review"]
    name: str = Field(min_length=1, max_length=120)
    review_id: str | None
    existing_knowledge_id: str | None
    category: str = Field(min_length=1, max_length=50)
    display_kind: DisplayKind
    review_method: ReviewMethod
    estimated_minutes: int = Field(ge=1, le=5)
    direct_evidence: list[ModelEvidenceReference] = Field(min_length=1, max_length=20)
    context_used: list[str] = Field(max_length=20)
    confidence: Literal["high", "medium", "low"]


class ModelAnalysisResult(BaseModel):
    """Untrusted provider result before deterministic validation and projection."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(max_length=MODEL_SUMMARY_MAX_LENGTH)
    source: str = Field(min_length=1, max_length=30)
    subjects: dict[str, list[ModelLearningItem]]
    uncertainties: list[str] = Field(max_length=20)


class AnalysisTerminalError(Exception):
    code = "analysis_failed"
    public_message = "分析暂时失败，请重试"


class AnalysisOutputExhaustedError(AnalysisTerminalError):
    code = "analysis_output_invalid"
    public_message = "图片内容暂时无法整理成有效条目，请修改补充说明后重试"

    def __init__(
        self,
        reason: str = "turn_budget",
        codes: list[str] | None = None,
    ) -> None:
        self.reason = reason
        self.codes = list(dict.fromkeys(codes or []))[:20]
        super().__init__(reason)


class AnalysisCapabilityError(AnalysisTerminalError):
    code = "analysis_schema_unsupported"
    public_message = "当前 AI 模型不支持所需的结构化输出，请联系管理员检查模型配置"


class AnalysisInputError(AnalysisTerminalError):
    """A deterministic input or runtime configuration invariant cannot recover on retry."""


class AnalysisDeadlineExceededError(Exception):
    """One Agent attempt exhausted its wall-clock budget."""


@dataclass(frozen=True)
class AnalysisFailureDisposition:
    retryable: bool
    code: str
    public_message: str
    reason: str


def analysis_failure_disposition(exc: Exception) -> AnalysisFailureDisposition:
    """Classify failures without inspecting provider text or coupling policy to inheritance."""
    if isinstance(exc, AnalysisCapabilityError):
        return AnalysisFailureDisposition(
            retryable=False,
            code=exc.code,
            public_message=exc.public_message,
            reason="capability",
        )
    if isinstance(exc, AnalysisInputError):
        return AnalysisFailureDisposition(
            retryable=False,
            code=exc.code,
            public_message=exc.public_message,
            reason="input_invariant",
        )
    if isinstance(exc, (AnalysisOutputExhaustedError, AnalysisOutputValidationError)):
        reason = getattr(exc, "reason", "output_validation")
        return AnalysisFailureDisposition(
            retryable=True,
            code="analysis_output_invalid",
            public_message=AnalysisOutputExhaustedError.public_message,
            reason=reason,
        )
    if isinstance(exc, AnalysisDeadlineExceededError):
        return AnalysisFailureDisposition(
            retryable=True,
            code="analysis_failed",
            public_message=AnalysisTerminalError.public_message,
            reason="time_budget",
        )
    if isinstance(exc, AnalysisTerminalError):
        return AnalysisFailureDisposition(
            retryable=False,
            code=exc.code,
            public_message=exc.public_message,
            reason="terminal",
        )
    return AnalysisFailureDisposition(
        retryable=True,
        code="analysis_failed",
        public_message=AnalysisTerminalError.public_message,
        reason="dependency",
    )


class AnalysisOutputValidationError(ValueError):
    def __init__(self, codes: list[str]) -> None:
        self.codes = list(dict.fromkeys(codes))[:20]
        super().__init__(",".join(self.codes))


class AnalysisProposal(BaseModel):
    summary: str = Field(min_length=1, max_length=500)
    subject_name: str = Field(min_length=1, max_length=40)
    subject_kind: str = Field(default="learning", pattern="^(learning|activity)$")
    source: str = Field(default="课内", max_length=30)
    knowledge_points: list[KnowledgeProposal] = Field(default_factory=list, max_length=20)
    todo_matches: list[TodoCandidate] = Field(default_factory=list, max_length=20)
    uncertainties: list[str] = Field(default_factory=list, max_length=20)


class AnalysisInput(BaseModel):
    occurred_at: str | None = None
    grade: str | None = None
    text: str | None = None
    image_paths: list[Path] = Field(default_factory=list)
    todo_candidates: list[TodoCandidate] = Field(default_factory=list)
    # Subjects already persisted for this child. Confirmation may use these without
    # additional consent; keep the legacy field name for provider/test compatibility.
    existing_subjects: list[str] = Field(default_factory=list, max_length=30)
    # Subjects the model is allowed to analyse. This may include system presets which
    # are not configured yet; confirmation still applies the configured-subject policy.
    analysis_subjects: list[str] = Field(default_factory=list, max_length=33)
    recent_learning: list[RecentLearningContext] = Field(default_factory=list, max_length=6)
    existing_knowledge: list[ExistingKnowledgeContext] = Field(default_factory=list, max_length=100)
    same_day_learning: list[SameDayKnowledgeContext] = Field(default_factory=list, max_length=200)

    def allowed_analysis_subjects(self) -> list[str]:
        values = self.analysis_subjects or self.existing_subjects
        return list(dict.fromkeys(name.strip() for name in values if name.strip()))

    def structured_output_schema(self) -> dict:
        """Return an exact-key schema so the model cannot invent or omit subjects."""
        allowed_subjects = self.allowed_analysis_subjects()
        if not allowed_subjects:
            raise AnalysisOutputValidationError(["subjects.input_empty"])
        schema = ModelAnalysisResult.model_json_schema()
        item_schema = {
            "type": "array",
            "items": {"$ref": "#/$defs/ModelLearningItem"},
            "maxItems": 20,
        }
        schema["properties"]["subjects"] = {
            "type": "object",
            "properties": {name: item_schema for name in allowed_subjects},
            "required": allowed_subjects,
            "additionalProperties": False,
        }
        return schema

    def validate_model_result(self, result: ModelAnalysisResult) -> AnalysisProposal:
        """Validate references/invariants, then expose the compatible editable proposal."""
        allowed_subjects = self.allowed_analysis_subjects()
        if set(result.subjects) != set(allowed_subjects):
            raise AnalysisOutputValidationError(["subjects.keys"])
        if sum(len(items) for items in result.subjects.values()) > 20:
            raise AnalysisOutputValidationError(["subjects.max_items"])

        context_ids = {item.record_id for item in self.recent_learning}
        candidates = self.review_candidates()
        knowledge = {item.knowledge_id: item for item in self.existing_knowledge}
        same_day = {
            (item.subject_name, normalize_knowledge_name(item.name))
            for item in self.same_day_learning
        }
        historical = {
            (item.subject_name, normalize_knowledge_name(item.name))
            for item in self.existing_knowledge
        }
        points: list[KnowledgeProposal] = []
        matches: list[TodoCandidate] = []
        errors = _model_summary_errors(result.summary)
        uncertainties = list(result.uncertainties)
        if _has_runtime_uncertainty(uncertainties):
            errors.append("uncertainty.runtime_claim")
        new_keys: set[tuple[str, str]] = set()
        if not result.source.strip():
            errors.append("source.blank")

        for subject_name, items in result.subjects.items():
            for item in items:
                if (
                    not normalize_knowledge_name(item.name)
                    or not item.category.strip()
                    or not item.review_method.strip()
                ):
                    errors.append("item.blank")
                if not set(item.context_used).issubset(context_ids):
                    errors.append("context.reference")
                for evidence in item.direct_evidence:
                    if not evidence.detail.strip():
                        errors.append("evidence.detail")
                    if evidence.source == "image" and (
                        evidence.image_index is None or evidence.image_index > len(self.image_paths)
                    ):
                        errors.append("evidence.image_index")
                    if evidence.source == "parent_text" and (
                        not (self.text or "").strip() or evidence.image_index is not None
                    ):
                        errors.append("evidence.parent_text")
                key = (subject_name, normalize_knowledge_name(item.name))
                if item.kind in {"today_review", "history_item", "review"}:
                    if key in same_day and not explicit_same_day_review(self.text):
                        if len(uncertainties) < 20:
                            uncertainties.append(
                                f"{subject_name}“{item.name}”当天已确认；未发现独立复习说明，已省略。"
                            )
                        continue
                    candidate = candidates.get(
                        item.review_id or f"knowledge:{item.existing_knowledge_id or ''}"
                    )
                    if (
                        candidate is None
                        or candidate.subject_name != subject_name
                        or normalize_knowledge_name(candidate.knowledge_name)
                        != normalize_knowledge_name(item.name)
                        or item.existing_knowledge_id not in (None, candidate.knowledge_id)
                    ):
                        errors.append("review.reference")
                        continue
                    if item.kind == "today_review" and candidate.match_kind != "today_review":
                        errors.append("today_review.reference")
                        continue
                    if item.kind == "history_item" and candidate.match_kind != "history_item":
                        errors.append("history_item.reference")
                        continue
                    matches.append(
                        candidate.model_copy(
                            update={
                                "evidence": "；".join(
                                    evidence.detail for evidence in item.direct_evidence
                                )[:200]
                            }
                        )
                    )
                    continue
                if item.review_id is not None:
                    errors.append("new.review_id")
                if key in same_day:
                    continue
                existing = knowledge.get(item.existing_knowledge_id or "")
                if item.existing_knowledge_id is not None and existing is None:
                    errors.append("knowledge.reference")
                    continue
                if existing is not None and (
                    existing.subject_name != subject_name
                    or normalize_knowledge_name(existing.name)
                    != normalize_knowledge_name(item.name)
                ):
                    errors.append("knowledge.reference")
                    continue
                if key in historical:
                    if len(uncertainties) < 20:
                        uncertainties.append(
                            f"{subject_name}“{item.name}”是已有知识，未作为新学条目输出。"
                        )
                    continue
                if key in new_keys:
                    continue
                new_keys.add(key)
                points.append(
                    KnowledgeProposal(
                        existing_knowledge_id=item.existing_knowledge_id,
                        name=item.name,
                        subject_name=subject_name,
                        category=item.category,
                        display_kind=item.display_kind,
                        review_method=item.review_method,
                        estimated_minutes=item.estimated_minutes,
                        direct_evidence=[
                            EvidenceReference.model_validate(evidence.model_dump())
                            for evidence in item.direct_evidence
                        ],
                        context_used=item.context_used,
                        confidence=item.confidence,
                    )
                )
        if errors:
            raise AnalysisOutputValidationError(errors)
        points = unique_knowledge_points(points)
        matches = list({review_candidate_key(item): item for item in matches}.values())
        require_actionable_proposal(points, matches)
        primary_subject = (
            points[0].subject_name
            if points
            else next(
                (item.subject_name for item in matches if item.subject_name),
                allowed_subjects[0] if allowed_subjects else "",
            )
        )
        return AnalysisProposal(
            summary=result.summary.strip() or MODEL_SUMMARY_FALLBACK,
            subject_name=primary_subject,
            source=result.source.strip(),
            knowledge_points=points,
            todo_matches=matches,
            uncertainties=uncertainties[:20],
        )

    def validate_proposal(self, proposal: AnalysisProposal) -> AnalysisProposal:
        """Validate model references against this input, not parent-edited proposals."""
        if _has_runtime_uncertainty(proposal.uncertainties):
            raise AnalysisOutputValidationError(["uncertainty.runtime_claim"])
        summary_errors = _model_summary_errors(proposal.summary)
        if "summary.too_long" in summary_errors:
            raise ValueError("model summary is too long for parent confirmation")
        if summary_errors:
            raise ValueError("model summary contains excluded absence metadata")
        context_ids = {item.record_id for item in self.recent_learning}
        candidates = self.review_candidates()
        knowledge = {item.knowledge_id: item for item in self.existing_knowledge}
        same_day = {
            (item.subject_name, normalize_knowledge_name(item.name))
            for item in self.same_day_learning
        }
        for point in proposal.knowledge_points:
            if point.existing_knowledge_id:
                existing = knowledge.get(point.existing_knowledge_id)
                # A linked point must stay inside its own subject; when the batch spans several
                # subjects the point-level subject is what has to agree, not the batch label.
                claimed = point.subject_name or proposal.subject_name
                if existing is None or existing.subject_name != claimed:
                    raise ValueError("model knowledge reference is outside the input subject")
                point.name, point.category = existing.name, existing.category
                point.subject_name = existing.subject_name
            point.display_kind = point.display_kind or infer_display_kind(
                point.name, point.category
            )
            if not point.direct_evidence:
                raise ValueError("model knowledge point has no direct evidence")
            if not set(point.context_used).issubset(context_ids):
                raise ValueError("model context reference is outside the input")
            for evidence in point.direct_evidence:
                if not evidence.detail.strip():
                    raise ValueError("model evidence detail is empty")
                if evidence.source == "image":
                    if evidence.image_index is None or evidence.image_index > len(self.image_paths):
                        raise ValueError("model image reference is outside the input")
                elif not (self.text or "").strip() or evidence.image_index is not None:
                    raise ValueError("model text reference is outside the input")
        for match in proposal.todo_matches:
            candidate = candidates.get(review_candidate_key(match))
            if candidate is None or candidate.knowledge_name != match.knowledge_name:
                raise ValueError("model Todo reference is outside the input")
            candidate_key = (
                candidate.subject_name or proposal.subject_name,
                normalize_knowledge_name(candidate.knowledge_name),
            )
            if candidate_key in same_day and not explicit_same_day_review(self.text):
                raise ValueError("same-day review requires an explicit parent note")
            if not (match.evidence or "").strip():
                raise ValueError("model Todo match has no evidence")
            match.review_id = candidate.review_id
            match.knowledge_id = candidate.knowledge_id
            match.subject_name = candidate.subject_name
            match.knowledge_name = candidate.knowledge_name
            match.step, match.due_date = candidate.step, candidate.due_date
            match.match_kind = candidate.match_kind
            match.state_version = candidate.state_version
            match.last_reviewed_on = candidate.last_reviewed_on
            match.review_count = candidate.review_count
            match.plan_state = candidate.plan_state
        proposal.knowledge_points = unique_knowledge_points(proposal.knowledge_points)
        proposal.todo_matches = list(
            {review_candidate_key(item): item for item in proposal.todo_matches}.values()
        )
        require_actionable_proposal(proposal.knowledge_points, proposal.todo_matches)
        return proposal

    def review_candidates(self) -> dict[str, TodoCandidate]:
        """Return today's plan plus bounded active-history reviews, preferring plan snapshots."""
        historical = {
            item.review_id or f"knowledge:{item.knowledge_id}": TodoCandidate(
                review_id=item.review_id,
                knowledge_id=item.knowledge_id,
                knowledge_name=item.name,
                subject_name=item.subject_name,
                step=item.review_step,
                due_date=item.review_due_date,
                match_kind="history_item",
                state_version=item.state_version,
                last_reviewed_on=item.last_reviewed_on,
                review_count=item.review_count,
            )
            for item in self.existing_knowledge
        }
        historical.update({review_candidate_key(item): item for item in self.todo_candidates})
        return historical


def _model_summary_errors(summary: str) -> list[str]:
    """Return safe provider-facing codes without retaining or echoing untrusted text."""
    value = summary.strip()
    errors: list[str] = []
    if len(value) > MODEL_SUMMARY_MAX_LENGTH:
        errors.append("summary.too_long")
    if any(pattern.search(value) for pattern in _SUMMARY_EXCLUSION_PATTERNS):
        errors.append("summary.exclusion_clause")
    return errors


def _has_runtime_uncertainty(messages: list[str]) -> bool:
    return any(
        _RUNTIME_UNCERTAINTY_ENTITY.search(sentence)
        and _RUNTIME_UNCERTAINTY_FAILURE.search(sentence)
        for message in messages
        for sentence in re.split(r"[。！？!?\n]", message)
    )


def require_actionable_proposal(
    knowledge_points: list[KnowledgeProposal], todo_matches: list[TodoCandidate]
) -> None:
    """Reject an empty final proposal so the provider can correct it or retry durably."""
    if not knowledge_points and not todo_matches:
        raise AnalysisOutputValidationError(["proposal.actionable_items"])


def explicit_same_day_review(text: str | None) -> bool:
    value = (text or "").strip()
    return any(marker in value for marker in ("复习", "再次练习", "重新练习", "又练了"))


def unique_knowledge_points(points: list[KnowledgeProposal]) -> list[KnowledgeProposal]:
    """Merge exact/canonical duplicates, retaining evidence without semantic guessing."""
    result: dict[tuple[str, str, str], KnowledgeProposal] = {}
    for point in points:
        # Same wording under two different subjects is two different things to review.
        key = (
            normalize_knowledge_name(point.name),
            point.category.strip(),
            (point.subject_name or "").strip(),
        )
        if key not in result:
            result[key] = point.model_copy(deep=True)
            continue
        kept = result[key]
        if kept.existing_knowledge_id and point.existing_knowledge_id not in (
            None,
            kept.existing_knowledge_id,
        ):
            raise ValueError("conflicting knowledge references")
        kept.existing_knowledge_id = kept.existing_knowledge_id or point.existing_knowledge_id
        for evidence in point.direct_evidence:
            if evidence not in kept.direct_evidence and len(kept.direct_evidence) < 20:
                kept.direct_evidence.append(evidence)
        kept.context_used = list(dict.fromkeys(kept.context_used + point.context_used))[:20]
        if point.confidence == "low":
            kept.confidence = "low"
    return list(result.values())


def review_candidate_key(item: TodoCandidate) -> str:
    if item.review_id:
        return item.review_id
    if item.knowledge_id:
        return f"knowledge:{item.knowledge_id}"
    raise ValueError("review candidate has no stable reference")


class AnalysisProvider(Protocol):
    def analyze(self, data: AnalysisInput) -> AnalysisProposal: ...
