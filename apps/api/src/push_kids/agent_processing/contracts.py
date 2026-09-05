from __future__ import annotations

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from push_kids.knowledge.normalization import normalize_knowledge_name

MATERIAL_FINGERPRINT_KEY = "_analysis_material_fingerprint"


class KnowledgeProposal(BaseModel):
    existing_knowledge_id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="知识点", max_length=50)
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
    review_id: str
    knowledge_name: str
    evidence: str | None = Field(default=None, max_length=200)
    step: int | None = None
    due_date: str | None = None


class ExistingKnowledgeContext(BaseModel):
    knowledge_id: str
    subject_name: str
    name: str
    category: str
    review_step: int | None = None
    review_due_date: str | None = None
    review_active: bool | None = None


class RecentLearningContext(BaseModel):
    record_id: str
    subject_name: str
    summary: str = Field(max_length=500)
    occurred_at: str


class AnalysisProposal(BaseModel):
    summary: str = Field(min_length=1, max_length=500)
    subject_name: str = Field(min_length=1, max_length=40)
    subject_kind: str = Field(default="learning", pattern="^(learning|activity)$")
    source: str = Field(default="课内", max_length=30)
    knowledge_points: list[KnowledgeProposal] = Field(min_length=1, max_length=20)
    todo_matches: list[TodoCandidate] = Field(default_factory=list, max_length=20)
    uncertainties: list[str] = Field(default_factory=list, max_length=20)


class AnalysisInput(BaseModel):
    occurred_at: str | None = None
    grade: str | None = None
    text: str | None = None
    image_paths: list[Path] = Field(default_factory=list)
    todo_candidates: list[TodoCandidate] = Field(default_factory=list)
    existing_subjects: list[str] = Field(default_factory=list, max_length=30)
    recent_learning: list[RecentLearningContext] = Field(default_factory=list, max_length=30)
    existing_knowledge: list[ExistingKnowledgeContext] = Field(default_factory=list, max_length=100)

    def validate_proposal(self, proposal: AnalysisProposal) -> AnalysisProposal:
        """Validate model references against this input, not parent-edited proposals."""
        context_ids = {item.record_id for item in self.recent_learning}
        candidates = {item.review_id: item for item in self.todo_candidates}
        knowledge = {item.knowledge_id: item for item in self.existing_knowledge}
        for point in proposal.knowledge_points:
            if point.existing_knowledge_id:
                existing = knowledge.get(point.existing_knowledge_id)
                if existing is None or existing.subject_name != proposal.subject_name:
                    raise ValueError("model knowledge reference is outside the input subject")
                point.name, point.category = existing.name, existing.category
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
            candidate = candidates.get(match.review_id)
            if candidate is None or candidate.knowledge_name != match.knowledge_name:
                raise ValueError("model Todo reference is outside the input")
            if not (match.evidence or "").strip():
                raise ValueError("model Todo match has no evidence")
            match.step, match.due_date = candidate.step, candidate.due_date
        proposal.knowledge_points = unique_knowledge_points(proposal.knowledge_points)
        proposal.todo_matches = list(
            {item.review_id: item for item in proposal.todo_matches}.values()
        )
        return proposal


def unique_knowledge_points(points: list[KnowledgeProposal]) -> list[KnowledgeProposal]:
    """Merge exact/canonical duplicates, retaining evidence without semantic guessing."""
    result: dict[tuple[str, str], KnowledgeProposal] = {}
    for point in points:
        key = (normalize_knowledge_name(point.name), point.category.strip())
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


class AnalysisProvider(Protocol):
    def analyze(self, data: AnalysisInput) -> AnalysisProposal: ...
