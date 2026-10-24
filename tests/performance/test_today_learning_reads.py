"""Actual bounded context, equality-slot probes and query plans at 10k/50k."""

import json
import time
from datetime import timedelta

import pytest
from push_kids.knowledge.learning_context import KnowledgeInputClock, get_context
from push_kids.learning_suggestions.queries import current
from push_kids.persistence.models import KnowledgeItem, ReviewItem, Subject
from push_kids.planning.early_candidates import select_early_reviews
from push_kids.platform.time import local_date
from sqlalchemy import event, insert


@pytest.mark.parametrize("size", [10_000, 50_000])
def test_context_and_early_reads_bounded_at_scale(app, client, child, family_headers, size):
    family, cid = family_headers["X-Family-ID"], child["id"]
    with app.state.database.session_factory() as db:
        db.add(Subject(id="scale-s", family_id=family, child_id=cid, name="数学", kind="learning"))
        db.add(
            KnowledgeInputClock(
                family_id=family, child_id=cid, observed_since=local_date() - timedelta(days=5)
            )
        )
        db.flush()
        for start in range(0, size, 1000):
            db.execute(
                insert(KnowledgeItem),
                [
                    dict(
                        id=f"scale-k{i:06}",
                        family_id=family,
                        child_id=cid,
                        subject_id="scale-s",
                        name=f"知识{i}",
                        normalized_name=f"知识{i}",
                        estimated_minutes=3,
                    )
                    for i in range(start, start + 1000)
                ],
            )
            db.execute(
                insert(ReviewItem),
                [
                    dict(
                        id=f"scale-r{i:06}",
                        family_id=family,
                        child_id=cid,
                        knowledge_item_id=f"scale-k{i:06}",
                        due_date=local_date() + timedelta(days=1),
                        last_reviewed_on=local_date() - timedelta(days=8),
                        review_count=2,
                    )
                    for i in range(start, start + 1000)
                ],
            )
        db.commit()
    captured = []

    def capture(_conn, _cursor, sql, params, _context, _many):
        captured.append((sql, params))

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        with app.state.database.session_factory() as db:
            db.info["learning_suggestions_enabled"] = True
            started = time.monotonic()
            result = current(db, family, cid)
            assert time.monotonic() - started < 0.5
            assert len(captured) <= 8
            assert len(json.dumps(result).encode()) <= 16 * 1024
            assert len(json.dumps(get_context(db, family, cid)).encode()) <= 24 * 1024
            captured.clear()
            selected = select_early_reviews(db, family, cid, local_date(), 15)
            assert len(selected) == 3 and sum(x.estimated_minutes for x in selected) == 9
            assert len(captured) == 3
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    with engine.connect() as connection:
        plans = [
            row[3]
            for sql, params in captured
            for row in connection.exec_driver_sql("EXPLAIN QUERY PLAN " + sql, params)
        ]
    assert any("ix_early_slots" in row for row in plans)
    assert not any(row.startswith("SCAN review_early_slots") for row in plans)
