from __future__ import annotations

from push_kids.agent_processing.history_search import (
    MAX_RESULTS_PER_CALL,
    HistorySearchRequest,
    add_search_terms,
    search_history_items,
)
from push_kids.knowledge.normalization import normalize_knowledge_name
from push_kids.persistence.models import KnowledgeItem, ReviewItem, Subject
from push_kids.platform.time import local_date
from sqlalchemy import select


def _create_child(client, family_id: str, name: str) -> dict:
    response = client.post(
        "/api/v1/children",
        headers={"X-Family-ID": family_id},
        json={
            "name": name,
            "grade": "小学二年级",
            "daily_budget_minutes": 15,
            "subject_names": ["数学"],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_history_search_is_scoped_bounded_and_includes_inactive_or_missing_reviews(
    client, app
) -> None:
    child_a = _create_child(client, "family-a", "小雨")
    child_b = _create_child(client, "family-b", "小风")
    with app.state.database.session_factory() as db:
        subject_a = db.scalar(
            select(Subject).where(
                Subject.family_id == "family-a", Subject.child_id == child_a["id"]
            )
        )
        subject_b = db.scalar(
            select(Subject).where(
                Subject.family_id == "family-b", Subject.child_id == child_b["id"]
            )
        )
        assert subject_a is not None and subject_b is not None

        knowledge_a: list[KnowledgeItem] = []
        for index in range(22):
            name = f"共同词{index:02d}"
            item = KnowledgeItem(
                family_id="family-a",
                child_id=child_a["id"],
                subject_id=subject_a.id,
                name=name,
                normalized_name=normalize_knowledge_name(name),
                category="计算",
                review_method="变式练习",
                estimated_minutes=2,
            )
            db.add(item)
            db.flush()
            add_search_terms(db, item)
            knowledge_a.append(item)

        inactive = ReviewItem(
            family_id="family-a",
            child_id=child_a["id"],
            knowledge_item_id=knowledge_a[0].id,
            step=6,
            due_date=local_date(),
            active=False,
        )
        db.add(inactive)

        foreign = KnowledgeItem(
            family_id="family-b",
            child_id=child_b["id"],
            subject_id=subject_b.id,
            name="共同词00",
            normalized_name=normalize_knowledge_name("共同词00"),
            category="计算",
            review_method="变式练习",
            estimated_minutes=2,
        )
        db.add(foreign)
        db.flush()
        add_search_terms(db, foreign)
        db.commit()

        broad = search_history_items(
            db,
            family_id="family-a",
            child_id=child_a["id"],
            request=HistorySearchRequest(
                candidate_key="共同词",
                subject_name="数学",
                keywords=("共同词",),
            ),
        )
        assert len(broad) == MAX_RESULTS_PER_CALL
        assert {item.knowledge_id for item in broad}.issubset({item.id for item in knowledge_a})
        assert foreign.id not in {item.knowledge_id for item in broad}

        scoped_id = search_history_items(
            db,
            family_id="family-a",
            child_id=child_a["id"],
            request=HistorySearchRequest(
                candidate_key="不同表达",
                subject_name="数学",
                keywords=("完全不同",),
                knowledge_id=knowledge_a[0].id,
            ),
        )
        assert len(scoped_id) == 1 and scoped_id[0].knowledge_id == knowledge_a[0].id
        foreign_id = search_history_items(
            db,
            family_id="family-a",
            child_id=child_a["id"],
            request=HistorySearchRequest(
                candidate_key="不同表达",
                subject_name="数学",
                keywords=("完全不同",),
                knowledge_id=foreign.id,
            ),
        )
        assert foreign_id == []

        inactive_result = search_history_items(
            db,
            family_id="family-a",
            child_id=child_a["id"],
            request=HistorySearchRequest(
                candidate_key="共同词00",
                subject_name="数学",
                keywords=("共同词00",),
            ),
        )[0]
        missing_result = search_history_items(
            db,
            family_id="family-a",
            child_id=child_a["id"],
            request=HistorySearchRequest(
                candidate_key="共同词01",
                subject_name="数学",
                keywords=("共同词01",),
            ),
        )[0]
        assert inactive_result.review_id == inactive.id
        assert inactive_result.review_active is False
        assert missing_result.review_id is None
        assert missing_result.review_active is None
