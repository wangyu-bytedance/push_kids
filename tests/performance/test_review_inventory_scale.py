"""Bounded projections and tenant-leading query plans at realistic inventory sizes."""

import json
from datetime import timedelta

import pytest
from push_kids.persistence.models import KnowledgeItem, ReviewItem, Subject
from push_kids.platform.time import local_date
from sqlalchemy import event, insert, update


@pytest.mark.parametrize("review_status", ["normal", "superseded"])
@pytest.mark.parametrize("size", [10_000, 50_000])
def test_inventory_bounded_reads(client, app, family_headers, child, size, review_status):
    family, cid = family_headers["X-Family-ID"], child["id"]
    with app.state.database.session_factory() as db:
        db.add(
            Subject(
                id="scale-subject", family_id=family, child_id=cid, name="scale", kind="learning"
            )
        )
        db.flush()
        for start in range(0, size, 1000):
            rows = [
                {
                    "id": f"k{i:06}",
                    "family_id": family,
                    "child_id": cid,
                    "subject_id": "scale-subject",
                    "name": f"知识{i}",
                    "normalized_name": f"知识{i}",
                    "review_status": "superseded" if i % 2 else "normal",
                }
                for i in range(start, start + 1000)
            ]
            db.execute(insert(KnowledgeItem), rows)
            db.execute(
                insert(ReviewItem),
                [
                    {
                        "id": f"r{i:06}",
                        "family_id": family,
                        "child_id": cid,
                        "knowledge_item_id": f"k{i:06}",
                        "due_date": local_date() + timedelta(days=1),
                        "review_count": i % 7,
                    }
                    for i in range(start, start + 1000)
                ],
            )
        db.execute(
            update(KnowledgeItem)
            .where(
                KnowledgeItem.family_id == family,
                KnowledgeItem.child_id == cid,
                KnowledgeItem.review_status == "superseded",
            )
            .values(superseded_by_knowledge_id="k000000")
        )
        db.commit()
    queries = []
    captured = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        queries.append(statement)
        captured.append((statement, _params))

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        cursor = None
        for view in ["count", "count-next", "count-exact", "subject", "time"]:
            queries.clear()
            params = {"view": view.split("-")[0], "limit": 20, "review_status": review_status}
            if view == "count-next":
                params["cursor"] = cursor
            if view == "count-exact":
                params["review_count"] = 2
            if view == "subject":
                params["subject_id"] = "scale-subject"
            if view == "time":
                params["offset"] = 2
            response = client.get(
                f"/api/v1/children/{cid}/review-inventory", headers=family_headers, params=params
            )
            assert response.status_code == 200, response.text
            data = response.json()
            if view == "count":
                cursor = data["next_cursor"]
            assert len(data["items"]) <= 20
            assert len(json.dumps(data).encode()) <= 96 * 1024
            # Fairness adds fixed coverage/bucket reads and today's arrangement projection.
            # Day two previews need at most three bounded dry runs (never per-subject SQL).
            assert len(queries) <= (27 if view == "time" else 13)
            assert all(q.lstrip().startswith("SELECT") for q in queries)
            # Every row query is LIMIT-bounded; totals use a database aggregate.
            assert all(
                "LIMIT" in q
                or "count(" in q.lower()
                or "children.id =" in q
                or "subjects.id =" in q
                or "SELECT daily_review_plans.id" in q
                for q in queries
            )
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    with engine.connect() as db:
        plans = [
            db.exec_driver_sql("EXPLAIN QUERY PLAN " + sql, params).all()
            for sql, params in captured
        ]
        # Audit the actual ORM queries, including COALESCE sorting and cursor predicates.
        # A tenant-bounded temporary sort is acceptable; a global table scan is not.
        for plan in plans:
            assert not any(
                str(row[3]).startswith("SCAN " + table)
                for row in plan
                for table in (
                    "review_items",
                    "knowledge_items",
                    "subjects",
                    "review_schedule_overrides",
                )
            ), plan
        assert any("ix_review_scope_count_knowledge" in str(plan) for plan in plans)
