"""Real candidate SQL bounds and query plans, including MySQL 5.7 when configured."""

import json
import os
from time import perf_counter
from uuid import uuid4

import pytest
from push_kids.persistence.models import (
    Child,
    Family,
    KnowledgeItem,
    ReviewItem,
    ReviewQueueEntry,
    Subject,
)
from push_kids.planning.plan_candidates import load_candidates
from push_kids.platform.config import Settings
from push_kids.platform.database import Database
from push_kids.platform.time import local_date
from sqlalchemy import delete, event, insert, select, text


@pytest.mark.parametrize("dialect", ["sqlite", "mysql"])
@pytest.mark.parametrize("size,subjects", [(10_000, 3), (50_000, 130)])
def test_bounded_fair_candidate_scale(dialect, size, subjects):
    url = "sqlite:///:memory:" if dialect == "sqlite" else os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
    if not url:
        pytest.skip("isolated MySQL URL not configured")
    database = Database(Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_DATABASE_URL=url))
    if dialect == "sqlite":
        database.create_schema()
    family, cid = str(uuid4()), str(uuid4())
    sids = [str(uuid4()) for _ in range(subjects)]
    captures = []
    query_ms = []
    started = [0.0]

    def capture(_conn, _cursor, sql, params, _ctx, _many):
        captures.append((sql, params))
        started[0] = perf_counter()

    def captured(_conn, _cursor, sql, params, _ctx, _many):
        query_ms.append((perf_counter() - started[0]) * 1000)

    try:
        with database.session_factory() as db:
            db.add(Family(id=family, display_name="synthetic-scale"))
            db.flush()
            db.add(Child(id=cid, family_id=family, name="synthetic", daily_budget_minutes=30))
            db.flush()
            db.execute(
                insert(Subject), [dict(id=s, family_id=family, child_id=cid, name=s) for s in sids]
            )
            for start in range(0, size, 1000):
                ids = [str(uuid4()) for _ in range(1000)]
                db.execute(
                    insert(KnowledgeItem),
                    [
                        dict(
                            id=rid,
                            family_id=family,
                            child_id=cid,
                            subject_id=sids[(start + i) % subjects],
                            name="synthetic",
                            normalized_name=rid,
                            estimated_minutes=i % 5 + 1,
                        )
                        for i, rid in enumerate(ids)
                    ],
                )
                db.execute(
                    insert(ReviewItem),
                    [
                        dict(
                            id=rid,
                            family_id=family,
                            child_id=cid,
                            knowledge_item_id=rid,
                            due_date=local_date(),
                            queue_eligible_on=local_date(),
                            review_count=i % 2,
                        )
                        for i, rid in enumerate(ids)
                    ],
                )
            db.commit()
            if dialect == "sqlite":
                db.execute(text("ANALYZE"))
            elapsed = []
            event.listen(database.engine, "before_cursor_execute", capture)
            event.listen(database.engine, "after_cursor_execute", captured)
            for _ in range(5):
                captures.clear()
                query_ms.clear()
                start = perf_counter()
                rows = load_candidates(db, family, cid, local_date())
                elapsed.append((perf_counter() - start) * 1000)
                assert len(rows) <= 1268
                assert len(captures) <= 12
                assert all(
                    sql.lstrip().startswith("SELECT") and "LIMIT" in sql for sql, _ in captures
                )
            event.remove(database.engine, "before_cursor_execute", capture)
            event.remove(database.engine, "after_cursor_execute", captured)
            captured = list(captures)
            plans = []
            with database.engine.connect() as connection:
                for sql, params in captured:
                    plans.extend(
                        connection.exec_driver_sql(
                            ("EXPLAIN QUERY PLAN " if dialect == "sqlite" else "EXPLAIN ") + sql,
                            params,
                        )
                        .mappings()
                        .all()
                    )
            print(
                json.dumps(
                    dict(
                        dialect=dialect,
                        size=size,
                        subjects=subjects,
                        candidates=len(rows),
                        queries=len(captured),
                        milliseconds=elapsed,
                        query_ms=query_ms,
                    )
                )
            )
            assert any("INDEX" in str(p).upper() or p.get("key") for p in plans)
            # This is a release gate, not a best-effort diagnostic. A failing run blocks deploy.
            assert max(elapsed) <= 500, "fair candidate p95 exceeds SPEC's 500ms release budget"
    finally:
        if event.contains(database.engine, "before_cursor_execute", capture):
            event.remove(database.engine, "before_cursor_execute", capture)
        with database.session_factory() as db:
            for model in (ReviewQueueEntry, ReviewItem, KnowledgeItem, Subject, Child):
                key = model.review_item_id if model is ReviewQueueEntry else model.id
                while ids := list(
                    db.scalars(select(key).where(model.family_id == family).limit(1000))
                ):
                    db.execute(delete(model).where(key.in_(ids)))
                    db.commit()
            db.execute(delete(Family).where(Family.id == family))
            db.commit()
        database.engine.dispose()
