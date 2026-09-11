from __future__ import annotations

import statistics
import tracemalloc
from datetime import UTC, datetime, timedelta
from time import perf_counter
from urllib.parse import quote

from push_kids.persistence.models import (
    ActivityRecord,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import local_date
from sqlalchemy import event, inspect


def _insert_chunks(connection, table, rows, chunk_size: int = 2_000) -> None:
    for offset in range(0, len(rows), chunk_size):
        connection.execute(table.insert(), rows[offset : offset + chunk_size])


def _measure(client, engine, path: str, headers: dict[str, str], runs: int = 5) -> dict:
    durations = []
    peaks = []
    query_counts = []
    responses = []
    client.get(path, headers=headers)
    for _ in range(runs):
        count = 0

        def count_query(*_args) -> None:
            nonlocal count
            count += 1

        event.listen(engine, "before_cursor_execute", count_query)
        tracemalloc.start()
        started = perf_counter()
        try:
            response = client.get(path, headers=headers)
        finally:
            durations.append((perf_counter() - started) * 1000)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            event.remove(engine, "before_cursor_execute", count_query)
        responses.append(response)
        peaks.append(peak)
        query_counts.append(count)
    return {
        "response": responses[-1],
        "median_ms": statistics.median(durations),
        "peak_bytes": max(peaks),
        "query_count": max(query_counts),
    }


def _sqlite_plan_texts(client, engine, path: str, headers: dict[str, str]) -> list[str]:
    captured = []

    def capture_select(_conn, _cursor, statement, parameters, *_args) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            captured.append((statement, parameters))

    event.listen(engine, "before_cursor_execute", capture_select)
    try:
        response = client.get(path, headers=headers)
    finally:
        event.remove(engine, "before_cursor_execute", capture_select)
    assert response.status_code == 200
    plans = []
    with engine.connect() as connection:
        for statement, parameters in captured:
            rows = connection.exec_driver_sql(f"EXPLAIN QUERY PLAN {statement}", parameters).all()
            plans.append(" ".join(str(row[-1]) for row in rows))
    return plans


def _seed_10k_read_fixture(app, family_id: str, child_id: str) -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    target = local_date(now)
    learning_subject_id = "perf-learning-subject"
    activity_subject_id = "perf-activity-subject"
    submission_id = "perf-shared-submission"
    count = 10_000
    learning_records = []
    knowledge_items = []
    reviews = []
    feedback = []
    occurrences = []
    activities = []
    for index in range(count):
        record_id = f"perf-record-{index:05d}"
        knowledge_id = f"perf-knowledge-{index:05d}"
        review_id = f"perf-review-{index:05d}"
        learning_records.append(
            {
                "id": record_id,
                "family_id": family_id,
                "child_id": child_id,
                "subject_id": learning_subject_id,
                "submission_id": submission_id,
                "occurred_at": now,
                "summary": f"学习内容 {index}",
                "source": "manual",
                "created_at": now,
            }
        )
        knowledge_items.append(
            {
                "id": knowledge_id,
                "family_id": family_id,
                "child_id": child_id,
                "subject_id": learning_subject_id,
                "name": f"知识点 {index}",
                "normalized_name": f"知识点-{index}",
                "category": "知识点",
                "review_method": "口头回顾",
                "estimated_minutes": 1,
                "created_at": now,
            }
        )
        reviews.append(
            {
                "id": review_id,
                "family_id": family_id,
                "child_id": child_id,
                "knowledge_item_id": knowledge_id,
                "step": 0,
                "due_date": target,
                "active": True,
                "updated_at": now,
            }
        )
        feedback.append(
            {
                "id": f"perf-feedback-{index:05d}",
                "family_id": family_id,
                "review_item_id": review_id,
                "action": "complete",
                "occurred_at": now,
            }
        )
        occurrences.append(
            {
                "id": f"perf-occurrence-{index:05d}",
                "family_id": family_id,
                "knowledge_item_id": knowledge_id,
                "learning_record_id": record_id,
                "occurred_at": now,
                "created_at": now,
            }
        )
        activities.append(
            {
                "id": f"perf-activity-{index:05d}",
                "family_id": family_id,
                "child_id": child_id,
                "subject_id": activity_subject_id,
                "occurred_at": now,
                "duration_minutes": 30,
                "note": None,
                "created_at": now,
            }
        )
    with app.state.database.engine.begin() as connection:
        connection.execute(
            Subject.__table__.insert(),
            [
                {
                    "id": learning_subject_id,
                    "family_id": family_id,
                    "child_id": child_id,
                    "name": "数学",
                    "kind": "learning",
                    "color": "#39847A",
                    "active": True,
                    "is_custom": True,
                    "created_at": now,
                },
                {
                    "id": activity_subject_id,
                    "family_id": family_id,
                    "child_id": child_id,
                    "name": "游泳",
                    "kind": "activity",
                    "color": "#39847A",
                    "active": True,
                    "is_custom": True,
                    "created_at": now,
                },
            ],
        )
        connection.execute(
            LearningSubmission.__table__.insert(),
            {
                "id": submission_id,
                "family_id": family_id,
                "child_id": child_id,
                "occurred_at": now,
                "input_text": "性能夹具",
                "source": "manual",
                "state": "confirmed",
                "created_at": now,
                "updated_at": now,
                "confirmed_at": now,
            },
        )
        _insert_chunks(connection, LearningRecord.__table__, learning_records)
        _insert_chunks(connection, KnowledgeItem.__table__, knowledge_items)
        _insert_chunks(connection, ReviewItem.__table__, reviews)
        _insert_chunks(connection, ReviewFeedback.__table__, feedback)
        _insert_chunks(connection, KnowledgeOccurrence.__table__, occurrences)
        _insert_chunks(connection, ActivityRecord.__table__, activities)


def test_dashboard_and_report_stay_bounded_at_10k_rows(app, client, family_headers, child) -> None:
    _seed_10k_read_fixture(app, family_headers["X-Family-ID"], child["id"])
    engine = app.state.database.engine

    dashboard = _measure(
        client,
        engine,
        f"/api/v1/children/{child['id']}/dashboard",
        family_headers,
    )
    dashboard_body = dashboard["response"].json()
    returned_todos = sum(len(group["items"]) for group in dashboard_body["todo_groups"])
    assert dashboard["response"].status_code == 200
    assert dashboard_body["todo_count"] == 10_000
    assert returned_todos == 20
    assert dashboard_body["todo_next_cursor"]
    assert dashboard_body["daily_summary"]["record_count"] == 10_000
    assert dashboard_body["daily_summary"]["returned_record_count"] == 20
    assert dashboard_body["daily_summary"]["remaining_record_count"] == 9_980
    assert len(dashboard["response"].content) < 96 * 1024
    assert dashboard["query_count"] <= 14
    assert dashboard["median_ms"] <= 250
    assert dashboard["peak_bytes"] <= 8 * 1024 * 1024
    print(
        "dashboard-10k",
        f"median_ms={dashboard['median_ms']:.1f}",
        f"peak_mib={dashboard['peak_bytes'] / 1024 / 1024:.2f}",
        f"queries={dashboard['query_count']}",
        f"bytes={len(dashboard['response'].content)}",
    )
    dashboard_plans = " ".join(
        _sqlite_plan_texts(
            client,
            engine,
            f"/api/v1/children/{child['id']}/dashboard",
            family_headers,
        )
    )
    assert "ix_review_items_family_child_active_due_id" in dashboard_plans
    assert "ix_learning_records_family_child_occurred_submission" in dashboard_plans

    for days in (7, 30, 100):
        report = _measure(
            client,
            engine,
            f"/api/v1/children/{child['id']}/report?days={days}",
            family_headers,
        )
        body = report["response"].json()
        assert report["response"].status_code == 200
        assert body["overview"] == {
            "learning_records": 10_000,
            "new_knowledge_items": 10_000,
            "review_feedback_count": 10_000,
            "activity_records": 10_000,
        }
        for key, expected in body["overview"].items():
            assert sum(bucket[key] for bucket in body["overview_trends"]["buckets"]) == expected
        assert len(body["review_urgency"]) == days
        assert len(body["review_activity"]) == days
        assert len(report["response"].content) < 128 * 1024
        assert report["query_count"] <= 10
        assert report["median_ms"] <= 400
        assert report["peak_bytes"] <= 8 * 1024 * 1024
        print(
            f"report-{days}d-10k-per-metric",
            f"median_ms={report['median_ms']:.1f}",
            f"peak_mib={report['peak_bytes'] / 1024 / 1024:.2f}",
            f"queries={report['query_count']}",
            f"bytes={len(report['response'].content)}",
        )

    report_plans = " ".join(
        _sqlite_plan_texts(
            client,
            engine,
            f"/api/v1/children/{child['id']}/report?days=100",
            family_headers,
        )
    )
    for index_name in (
        "ix_learning_records_family_child_occurred_submission",
        "ix_knowledge_items_family_child_created_id",
        "ix_knowledge_occurrences_family_occurred_knowledge",
        "ix_activity_records_family_child_occurred_id",
    ):
        assert index_name in report_plans


def _seed_50k_history_fixture(app, family_id: str, child_id: str) -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    subject_id = "history-perf-subject"
    submissions = []
    records = []
    for index in range(50_000):
        submission_id = f"history-submission-{index:05d}"
        occurred_at = now - timedelta(seconds=index)
        submissions.append(
            {
                "id": submission_id,
                "family_id": family_id,
                "child_id": child_id,
                "occurred_at": occurred_at,
                "input_text": None,
                "source": "manual",
                "state": "confirmed",
                "created_at": occurred_at,
                "updated_at": occurred_at,
                "confirmed_at": occurred_at,
            }
        )
        records.append(
            {
                "id": f"history-record-{index:05d}",
                "family_id": family_id,
                "child_id": child_id,
                "subject_id": subject_id,
                "submission_id": submission_id,
                "occurred_at": occurred_at,
                "summary": "唯一搜索目标" if index == 49_999 else f"普通学习记录 {index}",
                "source": "manual",
                "created_at": occurred_at,
            }
        )
    with app.state.database.engine.begin() as connection:
        connection.execute(
            Subject.__table__.insert(),
            {
                "id": subject_id,
                "family_id": family_id,
                "child_id": child_id,
                "name": "语文",
                "kind": "learning",
                "color": "#39847A",
                "active": True,
                "is_custom": True,
                "created_at": now,
            },
        )
        _insert_chunks(connection, LearningSubmission.__table__, submissions)
        _insert_chunks(connection, LearningRecord.__table__, records)


def test_history_50k_first_page_and_substring_search_budget(
    app, client, family_headers, child
) -> None:
    _seed_50k_history_fixture(app, family_headers["X-Family-ID"], child["id"])
    engine = app.state.database.engine
    index_names = {item["name"] for item in inspect(engine).get_indexes("learning_submissions")}
    assert "ix_learning_submissions_family_child_state_occurred_id" in index_names

    captured = []

    def capture_history_query(_conn, _cursor, statement, parameters, *_args) -> None:
        if (
            "FROM learning_records JOIN learning_submissions" in statement
            and "ORDER BY" in statement
        ):
            captured.append((statement, parameters))

    event.listen(engine, "before_cursor_execute", capture_history_query)
    try:
        client.get(
            f"/api/v1/children/{child['id']}/history?view=confirmed&limit=20",
            headers=family_headers,
        )
    finally:
        event.remove(engine, "before_cursor_execute", capture_history_query)
    assert captured
    with engine.connect() as connection:
        plan = connection.exec_driver_sql(
            f"EXPLAIN QUERY PLAN {captured[0][0]}", captured[0][1]
        ).all()
    plan_text = " ".join(str(row[-1]) for row in plan)
    assert "TEMP B-TREE" not in plan_text
    assert "ix_learning_records_family_child_occurred_submission" in plan_text

    common = _measure(
        client,
        engine,
        f"/api/v1/children/{child['id']}/history?view=confirmed&limit=20",
        family_headers,
    )
    assert common["response"].status_code == 200
    assert len(common["response"].json()["items"]) == 20
    assert common["median_ms"] <= 200
    print("history-50k", f"median_ms={common['median_ms']:.1f}")

    search = _measure(
        client,
        engine,
        f"/api/v1/children/{child['id']}/history?view=confirmed&limit=20",
        {**family_headers, "X-History-Query": quote("唯一搜索目标")},
    )
    assert search["response"].status_code == 200
    assert len(search["response"].json()["items"]) == 1
    assert search["median_ms"] <= 250
    print("history-search-50k", f"median_ms={search['median_ms']:.1f}")
