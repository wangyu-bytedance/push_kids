"""Measure actual ORM SQL with 50k archived children and bounded active candidates."""

import json
from uuid import uuid4

from push_kids.children.grade_confirmation import GradeConfirmationService
from push_kids.persistence.models import Child
from sqlalchemy import event, insert, text


def assert_bounded_grade_reads(engine, factory):
    family = "grade-scale-" + uuid4().hex
    with factory() as db:
        for start in range(0, 50000, 1000):
            db.execute(
                insert(Child),
                [
                    {
                        "id": uuid4().hex,
                        "family_id": family if i % 2 else "other-" + family,
                        "name": "合成归档",
                        "grade": "小学二年级",
                        "active": False,
                    }
                    for i in range(start, start + 1000)
                ],
            )
        db.execute(
            insert(Child),
            [
                {
                    "id": uuid4().hex,
                    "family_id": family,
                    "name": "合成在用" + str(i),
                    "grade": "小学二年级",
                    "active": True,
                }
                for i in range(5)
            ],
        )
        db.commit()
        queries = []

        def capture(_conn, _cursor, statement, _params, _context, _many):
            queries.append(statement)

        event.listen(engine, "before_cursor_execute", capture)
        try:
            view = GradeConfirmationService.pending(db, family, can_confirm=True)
        finally:
            event.remove(engine, "before_cursor_execute", capture)
        assert len(queries) == 1
        assert "LIMIT" in queries[0].upper()
        assert len(view.items) == 5
        assert len(json.dumps(view.model_dump(), ensure_ascii=False).encode()) <= 8192
        prefix = "EXPLAIN " if engine.dialect.name == "mysql" else "EXPLAIN QUERY PLAN "
        plan = db.execute(
            text(
                prefix + "SELECT * FROM children WHERE family_id=:family "
                "AND active=1 AND deleting=0 ORDER BY created_at,id LIMIT 6"
            ),
            {"family": family},
        ).all()
        assert any("ix_children_family_active_deleting_created_id" in str(row) for row in plan)
        if engine.dialect.name == "mysql":
            assert all("filesort" not in str(row).lower() for row in plan)
        else:
            assert not any("TEMP B-TREE" in str(row) for row in plan)


def test_50k_archived_does_not_expand_pending_read(client, app):
    assert_bounded_grade_reads(app.state.database.engine, app.state.database.session_factory)
