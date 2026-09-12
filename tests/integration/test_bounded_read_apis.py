from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from push_kids.persistence.models import (
    ActivityRecord,
    KnowledgeItem,
    LearningSubmission,
    ReviewItem,
    Subject,
    SubjectKind,
    SubmissionState,
    new_id,
)
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import event


def _database_session(app):
    return app.state.database.session_factory()


def test_large_response_log_uses_route_template_and_no_resource_value(app, client, caplog) -> None:
    def large_response(resource_id: str) -> dict[str, str]:
        return {"payload": "x" * (129 * 1024)}

    app.add_api_route("/__performance_test__/{resource_id}", large_response)
    caplog.set_level(logging.WARNING, logger="push_kids")

    response = client.get("/__performance_test__/private-resource-id?cursor=private-cursor")

    assert response.status_code == 200
    assert "api_read_budget_exceeded" in caplog.text
    assert "route=/__performance_test__/{resource_id}" in caplog.text
    assert "response_bytes=" in caplog.text
    assert "private-resource-id" not in caplog.text
    assert "private-cursor" not in caplog.text


def test_activity_records_use_stable_cursor_and_report_uses_complete_aggregate(
    app, client, family_headers, child
) -> None:
    family_id = family_headers["X-Family-ID"]
    subject_id = new_id()
    now = datetime.now(UTC)
    with _database_session(app) as db:
        db.add(
            Subject(
                id=subject_id,
                family_id=family_id,
                child_id=child["id"],
                name="游泳",
                kind=SubjectKind.activity.value,
            )
        )
        db.flush()
        db.add_all(
            ActivityRecord(
                id=new_id(),
                family_id=family_id,
                child_id=child["id"],
                subject_id=subject_id,
                occurred_at=now - timedelta(minutes=index),
                duration_minutes=30,
                note=f"第 {index + 1} 次",
            )
            for index in range(101)
        )
        db.commit()

    activity_queries = []

    def capture_activity_query(_conn, _cursor, statement, parameters, *_args) -> None:
        if "FROM activity_records" in statement and "ORDER BY" in statement:
            activity_queries.append((statement, parameters))

    event.listen(app.state.database.engine, "before_cursor_execute", capture_activity_query)
    try:
        first = client.get(
            f"/api/v1/children/{child['id']}/activity-records",
            headers=family_headers,
        )
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", capture_activity_query)
    assert first.status_code == 200
    assert len(first.json()) == 100
    assert first.headers["X-Result-Limit"] == "100"
    cursor = first.headers["X-Next-Cursor"]

    second = client.get(
        f"/api/v1/children/{child['id']}/activity-records",
        headers=family_headers,
        params={"cursor": cursor},
    )
    assert second.status_code == 200
    assert len(second.json()) == 1
    assert "X-Next-Cursor" not in second.headers
    assert {item["id"] for item in first.json()}.isdisjoint({item["id"] for item in second.json()})
    assert activity_queries
    with app.state.database.engine.connect() as connection:
        plan = connection.exec_driver_sql(
            f"EXPLAIN QUERY PLAN {activity_queries[0][0]}", activity_queries[0][1]
        ).all()
    assert "ix_activity_records_family_child_occurred_id" in " ".join(str(row[-1]) for row in plan)
    other_child = client.post(
        "/api/v1/children",
        headers=family_headers,
        json={"name": "小满", "daily_budget_minutes": 15},
    ).json()
    assert (
        client.get(
            f"/api/v1/children/{other_child['id']}/activity-records",
            headers=family_headers,
            params={"cursor": cursor},
        ).status_code
        == 400
    )
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/activity-records",
            headers={"X-Family-ID": "family-other"},
            params={"cursor": cursor},
        ).status_code
        == 404
    )

    report = client.get(
        f"/api/v1/children/{child['id']}/report",
        headers=family_headers,
        params={"days": 7},
    )
    assert report.status_code == 200
    body = report.json()
    assert body["overview"]["activity_records"] == 101
    assert body["activity_subjects"] == [
        {
            "subject_id": subject_id,
            "subject_name": "游泳",
            "records": 101,
            "minutes": 3030,
            "last_occurred_on": local_date(now).isoformat(),
        }
    ]


def test_dashboard_and_report_emit_no_window_or_cte_sql(app, client, family_headers, child) -> None:
    """TP-005: the affected read paths must stay MySQL-5.7 compatible (ARC-015).

    MySQL 5.7 rejects window functions and CTEs, so no captured statement for the Today
    dashboard or the Report may contain an ``OVER (`` projection or a ``WITH ... AS`` prelude.
    """
    family_id = family_headers["X-Family-ID"]
    subject_id = new_id()
    activity_subject_id = new_id()
    target = local_date()
    now = datetime.now(UTC)
    with _database_session(app) as db:
        db.add(
            Subject(
                id=subject_id,
                family_id=family_id,
                child_id=child["id"],
                name="数学",
                kind=SubjectKind.learning.value,
            )
        )
        db.add(
            Subject(
                id=activity_subject_id,
                family_id=family_id,
                child_id=child["id"],
                name="游泳",
                kind=SubjectKind.activity.value,
            )
        )
        db.flush()
        for index in range(30):
            knowledge_id = new_id()
            db.add(
                KnowledgeItem(
                    id=knowledge_id,
                    family_id=family_id,
                    child_id=child["id"],
                    subject_id=subject_id,
                    name=f"知识点 {index + 1}",
                    normalized_name=f"知识点-{index + 1}",
                    category="知识点",
                    review_method="口头回顾",
                    estimated_minutes=1,
                )
            )
            db.flush()
            db.add(
                ReviewItem(
                    id=new_id(),
                    family_id=family_id,
                    child_id=child["id"],
                    knowledge_item_id=knowledge_id,
                    due_date=target,
                    active=True,
                )
            )
        db.add(
            ActivityRecord(
                id=new_id(),
                family_id=family_id,
                child_id=child["id"],
                subject_id=activity_subject_id,
                occurred_at=now,
                duration_minutes=30,
            )
        )
        db.commit()

    captured: list[str] = []

    def capture_select(_conn, _cursor, statement, _parameters, *_args) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            captured.append(statement)

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture_select)
    try:
        dashboard = client.get(f"/api/v1/children/{child['id']}/dashboard", headers=family_headers)
        # Exercise both the first Todo page and a cursor page so the anchored branch is covered.
        first_todo = client.get(
            f"/api/v1/children/{child['id']}/todos",
            headers=family_headers,
            params={"day": target.isoformat(), "limit": 20},
        )
        cursor = first_todo.json()["next_cursor"]
        client.get(
            f"/api/v1/children/{child['id']}/todos",
            headers=family_headers,
            params={"day": target.isoformat(), "limit": 20, "cursor": cursor},
        )
        report = client.get(
            f"/api/v1/children/{child['id']}/report",
            headers=family_headers,
            params={"days": 100},
        )
    finally:
        event.remove(engine, "before_cursor_execute", capture_select)

    assert dashboard.status_code == 200
    assert first_todo.status_code == 200
    assert report.status_code == 200
    assert captured
    upper = [statement.upper() for statement in captured]
    assert not any("OVER (" in statement for statement in upper)
    assert not any("OVER(" in statement for statement in upper)
    assert not any(statement.lstrip().startswith("WITH ") for statement in upper)


def test_submission_list_has_constant_query_count_and_cursor_compatibility(
    app, client, family_headers, child
) -> None:
    family_id = family_headers["X-Family-ID"]
    now = datetime.now(UTC)
    with _database_session(app) as db:
        db.add_all(
            LearningSubmission(
                id=new_id(),
                family_id=family_id,
                child_id=child["id"],
                occurred_at=now - timedelta(minutes=index),
                input_text=f"学习记录 {index + 1}",
                source="manual",
                state=SubmissionState.pending_confirmation.value,
                created_at=now - timedelta(minutes=index),
                updated_at=now - timedelta(minutes=index),
            )
            for index in range(101)
        )
        db.commit()

    statements = 0
    submission_queries = []

    def count_statement(_conn, _cursor, statement, parameters, *_args) -> None:
        nonlocal statements
        statements += 1
        if "FROM learning_submissions" in statement and "ORDER BY" in statement:
            submission_queries.append((statement, parameters))

    event.listen(app.state.database.engine, "before_cursor_execute", count_statement)
    try:
        first = client.get(
            "/api/v1/submissions",
            headers=family_headers,
            params={"child_id": child["id"], "pending_only": "true"},
        )
    finally:
        event.remove(app.state.database.engine, "before_cursor_execute", count_statement)

    assert first.status_code == 200
    assert len(first.json()) == 100
    assert statements <= 6
    assert submission_queries
    with app.state.database.engine.connect() as connection:
        plan = connection.exec_driver_sql(
            f"EXPLAIN QUERY PLAN {submission_queries[0][0]}", submission_queries[0][1]
        ).all()
    assert "ix_learning_submissions_family_child_state_created_id" in " ".join(
        str(row[-1]) for row in plan
    )
    cursor = first.headers["X-Next-Cursor"]
    second = client.get(
        "/api/v1/submissions",
        headers=family_headers,
        params={"child_id": child["id"], "pending_only": "true", "cursor": cursor},
    )
    assert second.status_code == 200
    assert len(second.json()) == 1
    assert "X-Next-Cursor" not in second.headers
    invalid_mix = client.get(
        "/api/v1/submissions",
        headers=family_headers,
        params={
            "child_id": child["id"],
            "pending_only": "true",
            "cursor": cursor,
            "offset": 1,
        },
    )
    assert invalid_mix.status_code == 400
    wrong_filter = client.get(
        "/api/v1/submissions",
        headers=family_headers,
        params={"child_id": child["id"], "state": "confirmed", "cursor": cursor},
    )
    assert wrong_filter.status_code == 400


def test_todo_totals_remain_exact_while_payload_is_paged(
    app, client, family_headers, child
) -> None:
    family_id = family_headers["X-Family-ID"]
    subject_id = new_id()
    target = local_date()
    with _database_session(app) as db:
        db.add(
            Subject(
                id=subject_id,
                family_id=family_id,
                child_id=child["id"],
                name="数学",
                kind=SubjectKind.learning.value,
            )
        )
        db.flush()
        knowledge_items = []
        review_items = []
        for index in range(55):
            knowledge_id = new_id()
            knowledge_items.append(
                KnowledgeItem(
                    id=knowledge_id,
                    family_id=family_id,
                    child_id=child["id"],
                    subject_id=subject_id,
                    name=f"知识点 {index + 1}",
                    normalized_name=f"知识点-{index + 1}",
                    category="知识点",
                    review_method="口头回顾",
                    estimated_minutes=1,
                )
            )
            review_items.append(
                ReviewItem(
                    id=new_id(),
                    family_id=family_id,
                    child_id=child["id"],
                    knowledge_item_id=knowledge_id,
                    due_date=target,
                    active=True,
                )
            )
        db.add_all(knowledge_items)
        db.flush()
        db.add_all(review_items)
        db.commit()

    first = client.get(
        f"/api/v1/children/{child['id']}/todos",
        headers=family_headers,
        params={"day": target.isoformat(), "limit": 20},
    )
    assert first.status_code == 200
    body = first.json()
    first_items = [item for group in body["groups"] for item in group["items"]]
    assert len(first_items) == 20
    assert body["total_count"] == 55
    assert body["required_count"] == 15
    assert body["estimated_minutes"] == 15
    assert body["returned_count"] == 20
    assert body["remaining_count"] == 35
    assert body["next_cursor"]
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/todos",
            headers=family_headers,
            params={"day": (target - timedelta(days=1)).isoformat(), "cursor": body["next_cursor"]},
        ).status_code
        == 400
    )
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/todos",
            headers=family_headers,
            params={"day": target.isoformat(), "cursor": "not-a-cursor"},
        ).status_code
        == 400
    )
    assert (
        client.get(
            f"/api/v1/children/{child['id']}/todos",
            headers=family_headers,
            params={"day": target.isoformat(), "limit": 51},
        ).status_code
        == 422
    )

    # The cursor freezes new/changed rows by updated_at. A concurrent insert and an
    # update to an unseen row are intentionally deferred until the parent refreshes.
    concurrent_knowledge_id = new_id()
    concurrent_review_id = new_id()
    first_review_ids = {item["review_id"] for item in first_items}
    changed_review_id = next(item.id for item in review_items if item.id not in first_review_ids)
    with _database_session(app) as db:
        changed = db.get(ReviewItem, changed_review_id)
        assert changed is not None
        changed.updated_at = utcnow() + timedelta(seconds=1)
        db.add(
            KnowledgeItem(
                id=concurrent_knowledge_id,
                family_id=family_id,
                child_id=child["id"],
                subject_id=subject_id,
                name="并发新增知识",
                normalized_name="并发新增知识",
                category="知识点",
                review_method="口头回顾",
                estimated_minutes=1,
            )
        )
        db.flush()
        db.add(
            ReviewItem(
                id=concurrent_review_id,
                family_id=family_id,
                child_id=child["id"],
                knowledge_item_id=concurrent_knowledge_id,
                due_date=target,
                active=True,
                updated_at=utcnow() + timedelta(seconds=1),
            )
        )
        db.commit()

    second = client.get(
        f"/api/v1/children/{child['id']}/todos",
        headers=family_headers,
        params={
            "day": target.isoformat(),
            "limit": 50,
            "cursor": body["next_cursor"],
        },
    )
    assert second.status_code == 200
    second_body = second.json()
    second_items = [item for group in second_body["groups"] for item in group["items"]]
    assert len(second_items) == 34
    assert second_body["total_count"] == 54
    assert second_body["remaining_count"] == 0
    assert second_body["next_cursor"] is None
    assert {item["review_id"] for item in first_items}.isdisjoint(
        {item["review_id"] for item in second_items}
    )
    assert concurrent_review_id not in {item["review_id"] for item in second_items}
    assert changed_review_id not in {item["review_id"] for item in second_items}

    empty_child = client.post(
        "/api/v1/children",
        headers=family_headers,
        json={"name": "空分页孩子", "daily_budget_minutes": 15},
    ).json()
    empty = client.get(
        f"/api/v1/children/{empty_child['id']}/todos",
        headers=family_headers,
        params={"day": target.isoformat(), "limit": 50},
    )
    assert empty.status_code == 200
    assert empty.json() == {
        "day": target.isoformat(),
        "groups": [],
        "total_count": 0,
        "required_count": 0,
        "estimated_minutes": 0,
        "returned_count": 0,
        "remaining_count": 0,
        "next_cursor": None,
    }
