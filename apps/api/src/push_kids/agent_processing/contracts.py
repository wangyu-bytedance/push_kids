from __future__ import annotations

from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field


class KnowledgeProposal(BaseModel):
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
    text: str | None = None
    image_paths: list[Path] = Field(default_factory=list)
    todo_candidates: list[TodoCandidate] = Field(default_factory=list)
    existing_subjects: list[str] = Field(default_factory=list, max_length=30)
    recent_learning: list[RecentLearningContext] = Field(default_factory=list, max_length=30)


class AnalysisProvider(Protocol):
    def analyze(self, data: AnalysisInput) -> AnalysisProposal: ...
