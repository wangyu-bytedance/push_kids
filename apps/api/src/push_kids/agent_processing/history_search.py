from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from push_kids.agent_processing.contracts import ExistingKnowledgeContext
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeSearchTerm,
    ReviewItem,
    Subject,
)

MAX_KEYWORDS = 8
MAX_KEYWORD_CHARS = 40
MAX_RESULTS_PER_CALL = 20
MAX_TERMS_PER_ITEM = 32


@dataclass(frozen=True)
class HistorySearchRequest:
    candidate_key: str
    subject_name: str
    keywords: tuple[str, ...]
    # Server-only fallback for a same-day identity already in scoped input. The
    # provider tool parser never accepts or supplies this field.
    knowledge_id: str | None = None


def knowledge_search_terms(name: str) -> list[tuple[str, str]]:
    """Generate a stable, bounded set of exact/token/n-gram lookup terms."""
    normalized = normalize_knowledge_name(name)
    if not normalized:
        return []
    source = unicodedata.normalize("NFKC", name).lower()
    ranked: list[tuple[str, str]] = [(normalized[:MAX_KEYWORD_CHARS], "exact")]
    words = re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", source)
    ranked.extend((word[:MAX_KEYWORD_CHARS], "token") for word in words if word)
    ranked.extend(
        (normalized[index : index + 3], "trigram") for index in range(max(0, len(normalized) - 2))
    )
    ranked.extend(
        (normalized[index : index + 2], "bigram") for index in range(max(0, len(normalized) - 1))
    )
    result: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for term, kind in ranked:
        key = (term, kind)
        if term and key not in seen:
            seen.add(key)
            result.append(key)
        if len(result) == MAX_TERMS_PER_ITEM:
            break
    return result


def add_search_terms(db: Session, knowledge: KnowledgeItem) -> None:
    if not knowledge.id:
        raise RuntimeError("knowledge item must be flushed before indexing")
    existing = set(
        db.execute(
            select(KnowledgeSearchTerm.term, KnowledgeSearchTerm.term_kind).where(
                KnowledgeSearchTerm.family_id == knowledge.family_id,
                KnowledgeSearchTerm.child_id == knowledge.child_id,
                KnowledgeSearchTerm.subject_id == knowledge.subject_id,
                KnowledgeSearchTerm.knowledge_item_id == knowledge.id,
            )
        ).tuples()
    )
    for term, kind in knowledge_search_terms(knowledge.name or ""):
        if (term, kind) not in existing:
            db.add(
                KnowledgeSearchTerm(
                    family_id=knowledge.family_id,
                    child_id=knowledge.child_id,
                    subject_id=knowledge.subject_id,
                    knowledge_item_id=knowledge.id,
                    term=term,
                    term_kind=kind,
                )
            )


def search_history_items(
    db: Session,
    *,
    family_id: str,
    child_id: str,
    request: HistorySearchRequest,
) -> list[ExistingKnowledgeContext]:
    if not request.candidate_key.strip():
        raise ValueError("candidate_key is required")
    if not 1 <= len(request.keywords) <= MAX_KEYWORDS:
        raise ValueError("history search requires 1..8 keywords")
    keyword_names = list(
        dict.fromkeys(
            normalize_knowledge_name(value) for value in request.keywords if value.strip()
        )
    )
    keyword_names = [value for value in keyword_names if value]
    if not keyword_names or any(len(value) > MAX_KEYWORD_CHARS for value in keyword_names):
        raise ValueError("history search keyword is invalid")
    subject = db.scalar(
        select(Subject).where(
            Subject.family_id == family_id,
            Subject.child_id == child_id,
            Subject.name == request.subject_name,
            Subject.kind == "learning",
            Subject.active.is_(True),
        )
    )
    if subject is None:
        # A first-time subject has no history to leak or scan. Confirmation still applies the
        # existing explicit subject-creation consent rule.
        return []

    if request.knowledge_id is not None:
        scoped_rows = db.execute(
            select(KnowledgeItem, ReviewItem)
            .outerjoin(
                ReviewItem,
                and_(
                    ReviewItem.knowledge_item_id == KnowledgeItem.id,
                    ReviewItem.family_id == family_id,
                    ReviewItem.child_id == child_id,
                ),
            )
            .where(
                KnowledgeItem.id == request.knowledge_id,
                KnowledgeItem.family_id == family_id,
                KnowledgeItem.child_id == child_id,
                KnowledgeItem.subject_id == subject.id,
            )
            .limit(1)
        ).all()
        return _contexts(
            [(knowledge, review, 0, 1) for knowledge, review in scoped_rows],
            subject,
            identity_lookup=True,
        )

    lookup_terms = list(
        dict.fromkeys(
            term for keyword in request.keywords for term, _kind in knowledge_search_terms(keyword)
        )
    )[: MAX_KEYWORDS * MAX_TERMS_PER_ITEM]
    matched_count = func.count(func.distinct(KnowledgeSearchTerm.term))
    exact_rank = case((KnowledgeItem.normalized_name.in_(keyword_names), 1), else_=0)
    ranked_ids = (
        select(
            KnowledgeItem.id.label("knowledge_id"),
            matched_count.label("matched_count"),
            exact_rank.label("exact_rank"),
        )
        .join(
            KnowledgeSearchTerm,
            KnowledgeSearchTerm.knowledge_item_id == KnowledgeItem.id,
        )
        .where(
            KnowledgeItem.family_id == family_id,
            KnowledgeItem.child_id == child_id,
            KnowledgeItem.subject_id == subject.id,
            KnowledgeSearchTerm.family_id == family_id,
            KnowledgeSearchTerm.child_id == child_id,
            KnowledgeSearchTerm.subject_id == subject.id,
            KnowledgeSearchTerm.term.in_(lookup_terms),
        )
        .group_by(KnowledgeItem.id, KnowledgeItem.normalized_name)
        .order_by(exact_rank.desc(), matched_count.desc(), KnowledgeItem.id)
        .limit(MAX_RESULTS_PER_CALL)
        .subquery()
    )
    ranked_rows = db.execute(
        select(KnowledgeItem, ReviewItem, ranked_ids.c.matched_count, ranked_ids.c.exact_rank)
        .join(ranked_ids, ranked_ids.c.knowledge_id == KnowledgeItem.id)
        .outerjoin(
            ReviewItem,
            and_(
                ReviewItem.knowledge_item_id == KnowledgeItem.id,
                ReviewItem.family_id == family_id,
                ReviewItem.child_id == child_id,
            ),
        )
        .where(
            KnowledgeItem.family_id == family_id,
            KnowledgeItem.child_id == child_id,
            KnowledgeItem.subject_id == subject.id,
        )
        .order_by(
            ranked_ids.c.exact_rank.desc(),
            ranked_ids.c.matched_count.desc(),
            KnowledgeItem.created_at.desc(),
            KnowledgeItem.id,
        )
        .limit(MAX_RESULTS_PER_CALL)
    ).all()
    rows: list[tuple[KnowledgeItem, ReviewItem | None, int, int]] = [
        (knowledge, review, int(count or 0), int(exact or 0))
        for knowledge, review, count, exact in ranked_rows
    ]

    # Exact fallback keeps freshly upgraded local databases useful before their offline term
    # backfill runs. It is equality-only and remains family/child/subject scoped.
    if not rows:
        rows = [
            (knowledge, review, 0, 1)
            for knowledge, review in db.execute(
                select(KnowledgeItem, ReviewItem)
                .outerjoin(
                    ReviewItem,
                    and_(
                        ReviewItem.knowledge_item_id == KnowledgeItem.id,
                        ReviewItem.family_id == family_id,
                        ReviewItem.child_id == child_id,
                    ),
                )
                .where(
                    KnowledgeItem.family_id == family_id,
                    KnowledgeItem.child_id == child_id,
                    KnowledgeItem.subject_id == subject.id,
                    KnowledgeItem.normalized_name.in_(keyword_names),
                )
                .order_by(KnowledgeItem.created_at.desc(), KnowledgeItem.id)
                .limit(MAX_RESULTS_PER_CALL)
            ).all()
        ]

    return _contexts(rows, subject)


def _contexts(
    rows: list[tuple[KnowledgeItem, ReviewItem | None, int, int]],
    subject: Subject,
    *,
    identity_lookup: bool = False,
) -> list[ExistingKnowledgeContext]:
    return [
        ExistingKnowledgeContext(
            knowledge_id=knowledge.id,
            review_id=review.id if review else None,
            subject_name=subject.name,
            name=knowledge.name,
            category=knowledge.category,
            review_method=knowledge.review_method,
            evidence=(knowledge.evidence_json or "")[:4000],
            coverage_evidence_complete=len(knowledge.evidence_json or "") <= 4000,
            review_status=knowledge.review_status,
            created_at=knowledge.created_at.isoformat() if knowledge.created_at else None,
            review_step=review.step if review else None,
            review_due_date=(review.due_date.isoformat() if review and review.due_date else None),
            review_active=review.active if review else None,
            last_reviewed_on=(
                review.last_reviewed_on.isoformat() if review and review.last_reviewed_on else None
            ),
            review_count=review.review_count if review else 0,
            state_version=review.state_version if review else None,
            match_signals=["scoped_identity"]
            if identity_lookup
            else [
                "exact_name" if int(exact or 0) else "indexed_terms",
                f"matched_terms:{int(count or 0)}",
            ],
        )
        for knowledge, review, count, exact in rows
    ]
