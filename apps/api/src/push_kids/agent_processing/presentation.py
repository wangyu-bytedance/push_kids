from __future__ import annotations

from pydantic import BaseModel, Field

from push_kids.agent_processing.contracts import (
    DisplayKind,
    KnowledgeProposal,
    infer_display_kind,
)
from push_kids.knowledge.normalization import normalize_knowledge_name

DISPLAY_KIND_ORDER: tuple[DisplayKind, ...] = (
    "hanzi",
    "word",
    "poem",
    "arithmetic",
    "concept",
    "activity",
    "other",
)

DISPLAY_KIND_LABELS: dict[DisplayKind, str] = {
    "hanzi": "汉字",
    "word": "单词",
    "poem": "古诗",
    "arithmetic": "运算",
    "concept": "知识点",
    "activity": "活动",
    "other": "其他",
}


class DisplayGroup(BaseModel):
    kind: DisplayKind
    label: str = Field(min_length=1, max_length=10)
    items: list[str] = Field(min_length=1, max_length=20)


def project_display_groups(points: list[KnowledgeProposal]) -> list[DisplayGroup]:
    """Create a deterministic, non-authoritative confirmation-list projection."""
    grouped: dict[DisplayKind, list[str]] = {kind: [] for kind in DISPLAY_KIND_ORDER}
    seen: dict[DisplayKind, set[str]] = {kind: set() for kind in DISPLAY_KIND_ORDER}
    for point in points:
        kind = point.display_kind or infer_display_kind(point.name, point.category)
        normalized = normalize_knowledge_name(point.name)
        if normalized in seen[kind]:
            continue
        grouped[kind].append(point.name.strip())
        seen[kind].add(normalized)
    return [
        DisplayGroup(kind=kind, label=DISPLAY_KIND_LABELS[kind], items=grouped[kind])
        for kind in DISPLAY_KIND_ORDER
        if grouped[kind]
    ]
