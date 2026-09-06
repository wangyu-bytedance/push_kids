"""Deterministic mapping from model-proposed subject text onto the family subject catalogue.

The model may return a merged label such as "数学.语文、英语" for a batch that actually spans
several subjects. Creating a subject from that string produces permanent garbage in the catalogue,
so every proposed label is split and matched here before anything is written. Matching is pure
string policy: it never invents a subject, never ranks subjects, and never decides what the child
should learn. Anything that cannot be matched is reported back as "unlisted" so a parent can
decide whether to add it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from pydantic import BaseModel, Field

from push_kids.agent_processing.contracts import AnalysisProposal

# Separators the model realistically uses when it merges several subjects into one label.
SUBJECT_SEPARATORS = "、，,；;／/｜|＋+&＆·・.。：: \t\u3000"
SUBJECT_CONJUNCTIONS = ("以及", "和", "与", "及", "跟")
# Bookkeeping words the model prefixes onto a merged label; they are never a subject by themselves.
SUBJECT_STOPWORDS = frozenset(
    {"自定义", "综合", "混合", "其他", "其它", "未知", "多科目", "跨科目", "多学科", "合并"}
)

# Alias groups only normalise different spellings of the same school subject.
SUBJECT_ALIASES: dict[str, tuple[str, ...]] = {
    "语文": ("语文", "中文", "汉语", "国文", "chinese"),
    "数学": ("数学", "算术", "math", "maths", "mathematics"),
    "英语": ("英语", "英文", "english"),
    "科学": ("科学", "science"),
    "道德与法治": ("道德与法治", "道法", "品德"),
    "美术": ("美术", "绘画", "画画", "art"),
    "音乐": ("音乐", "乐理", "music"),
    "体育": ("体育", "体锻", "pe"),
    "历史": ("历史", "history"),
    "地理": ("地理", "geography"),
    "物理": ("物理", "physics"),
    "化学": ("化学", "chemistry"),
    "生物": ("生物", "biology"),
    "政治": ("政治", "politics"),
    "劳动": ("劳动", "劳技"),
    "信息技术": ("信息技术", "信息", "计算机", "编程"),
}

# Matches Subject.name and AnalysisProposal.subject_name so a legitimate long custom subject
# survives splitting instead of being silently dropped.
MAX_SUBJECT_NAME_LENGTH = 40


class SubjectGroup(BaseModel):
    """One subject worth of a single submission, in first-appearance order."""

    subject_name: str = Field(min_length=1, max_length=MAX_SUBJECT_NAME_LENGTH)
    listed: bool
    knowledge_indexes: list[int] = Field(default_factory=list)
    knowledge_names: list[str] = Field(default_factory=list)


class SubjectRouting(BaseModel):
    """Routing outcome for one proposal: never a decision, only a checkable default."""

    groups: list[SubjectGroup] = Field(default_factory=list)
    # Resolved subject name per knowledge point, aligned with proposal.knowledge_points.
    point_subjects: list[str] = Field(default_factory=list)
    # The model handed back a label carrying several subjects, so the parent must check routing.
    merged_label: bool = False
    # At least one routed subject is missing from the family catalogue.
    has_unlisted: bool = False
    # A point inherited the batch subject while the batch clearly spans several subjects.
    assumed_points: list[int] = Field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        return self.merged_label or self.has_unlisted or bool(self.assumed_points)


def _canonical(value: str) -> str:
    return value.strip().strip("：:·").lower()


def _alias_index() -> dict[str, str]:
    return {alias: canonical for canonical, group in SUBJECT_ALIASES.items() for alias in group}


def _is_known_subject(text: str, catalogue: Iterable[str]) -> bool:
    """True when the whole string is already one subject, so it must not be split further."""
    token = _canonical(text)
    if not token:
        return False
    if token in _alias_index():
        return True
    return any(_canonical(entry) == token for entry in catalogue)


def split_subject_label(raw: str | None, catalogue: Iterable[str] = ()) -> list[str]:
    """Split a possibly merged label into single subject tokens, keeping input order.

    A label that is already one subject is returned untouched, otherwise names that legitimately
    contain a separator or conjunction ("道德与法治", "机器人编程·进阶") would be shredded.
    """
    if not raw:
        return []
    text = str(raw).strip()
    if not text:
        return []
    entries = list(catalogue)
    if _is_known_subject(text, entries):
        return [text]
    for separator in SUBJECT_SEPARATORS:
        text = text.replace(separator, "\n")
    for conjunction in SUBJECT_CONJUNCTIONS:
        text = text.replace(conjunction, "\n")
    tokens: list[str] = []
    for piece in text.split("\n"):
        token = piece.strip()
        if not token or len(token) > MAX_SUBJECT_NAME_LENGTH:
            continue
        if token in SUBJECT_STOPWORDS:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def is_merged_subject_label(raw: str | None, catalogue: Iterable[str] = ()) -> bool:
    """True when the label carries more than one subject and must never be stored as-is."""
    return len(split_subject_label(raw, catalogue)) > 1


def match_subject(name: str, catalogue: Iterable[str]) -> str | None:
    """Return the catalogue entry this token means, or None when it is not configured yet."""
    token = _canonical(name)
    if not token:
        return None
    entries = list(catalogue)
    for entry in entries:
        if _canonical(entry) == token:
            return entry
    aliases = _alias_index()
    canonical_name = aliases.get(token)
    if canonical_name is None:
        return None
    for entry in entries:
        if _canonical(entry) == _canonical(canonical_name):
            return entry
        if aliases.get(_canonical(entry)) == canonical_name:
            return entry
    return None


def _resolve_token(token: str, catalogue: Sequence[str]) -> tuple[str, bool]:
    matched = match_subject(token, catalogue)
    if matched is not None:
        return matched, True
    return token[:MAX_SUBJECT_NAME_LENGTH], False


def route_subjects(catalogue: Sequence[str], proposal: AnalysisProposal) -> SubjectRouting:
    """Group the proposal's knowledge points by the subject each one actually belongs to.

    Points without their own subject fall back to the batch label's first subject, so a
    single-subject batch keeps behaving exactly as before this routing existed. When the batch
    label itself is merged, the fallback is reported as an assumption instead of a fact.
    """
    batch_tokens = split_subject_label(proposal.subject_name, catalogue)
    merged = len(batch_tokens) > 1
    fallback: tuple[str, bool] | None = (
        _resolve_token(batch_tokens[0], catalogue) if batch_tokens else None
    )
    groups: dict[str, SubjectGroup] = {}
    point_subjects: list[str] = []
    assumed: list[int] = []
    for index, point in enumerate(proposal.knowledge_points):
        tokens = split_subject_label(point.subject_name, catalogue)
        own = bool(tokens)
        resolved = _resolve_token(tokens[0], catalogue) if own else fallback
        if resolved is None:
            point_subjects.append("")
            continue
        name, listed = resolved
        if not own and merged:
            assumed.append(index)
        point_subjects.append(name)
        group = groups.get(name)
        if group is None:
            group = SubjectGroup(subject_name=name, listed=listed)
            groups[name] = group
        group.knowledge_indexes.append(index)
        group.knowledge_names.append(point.name.strip())
    ordered = list(groups.values())
    if not ordered:
        # No point carried a usable subject: keep every batch token visible to the parent instead
        # of silently dropping material.
        for token in batch_tokens:
            name, listed = _resolve_token(token, catalogue)
            if any(item.subject_name == name for item in ordered):
                continue
            ordered.append(SubjectGroup(subject_name=name, listed=listed))
    return SubjectRouting(
        groups=ordered,
        point_subjects=point_subjects,
        merged_label=merged,
        has_unlisted=any(not item.listed for item in ordered),
        assumed_points=assumed,
    )
