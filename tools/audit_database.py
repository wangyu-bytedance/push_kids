from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

BUSINESS_TABLES = (
    "children",
    "subjects",
    "learning_submissions",
    "submission_media",
    "learning_records",
    "knowledge_items",
    "knowledge_occurrences",
    "review_items",
    "review_feedback",
    "review_feedback_requests",
    "activity_schedules",
    "activity_records",
    "calendar_events",
    "calendar_event_requests",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="审计 Push Kids 本地 SQLite 一致性。")
    parser.add_argument("database", type=Path)
    parser.add_argument("--require-empty", action="store_true")
    return parser.parse_args()


def scalar(db: sqlite3.Connection, query: str) -> int | str:
    value = db.execute(query).fetchone()
    if value is None:
        raise RuntimeError(f"query returned no row: {query}")
    return value[0]


def main() -> int:
    args = parse_args()
    database = args.database.resolve()
    if not database.is_file():
        raise SystemExit(f"DATABASE_AUDIT_FAILED missing={database}")
    with sqlite3.connect(database) as db:
        integrity = scalar(db, "PRAGMA integrity_check")
        if integrity != "ok":
            raise SystemExit(f"DATABASE_AUDIT_FAILED integrity={integrity}")
        foreign_key_errors = list(db.execute("PRAGMA foreign_key_check"))
        if foreign_key_errors:
            raise SystemExit(f"DATABASE_AUDIT_FAILED foreign_keys={foreign_key_errors}")
        checks = {
            "orphan_jobs": """
                SELECT count(*) FROM agent_jobs j
                LEFT JOIN learning_submissions s ON s.id=j.submission_id
                WHERE s.id IS NULL
            """,
            "orphan_media": """
                SELECT count(*) FROM submission_media m
                LEFT JOIN learning_submissions s ON s.id=m.submission_id
                WHERE s.id IS NULL
            """,
            "duplicate_jobs": """
                SELECT count(*) FROM (
                    SELECT submission_id FROM agent_jobs
                    GROUP BY submission_id HAVING count(*)>1
                )
            """,
            "record_family_mismatch": """
                SELECT count(*) FROM learning_records r
                JOIN learning_submissions s ON s.id=r.submission_id
                WHERE r.family_id<>s.family_id OR r.child_id<>s.child_id
            """,
            "review_family_mismatch": """
                SELECT count(*) FROM review_items r
                JOIN knowledge_items k ON k.id=r.knowledge_item_id
                WHERE r.family_id<>k.family_id OR r.child_id<>k.child_id
            """,
            "feedback_request_family_mismatch": """
                SELECT count(*) FROM review_feedback_requests q
                JOIN review_items r ON r.id=q.review_item_id
                WHERE q.family_id<>r.family_id
            """,
            "stranded_photo_uploads": """
                SELECT count(*) FROM (
                    SELECT s.id FROM learning_submissions s
                    LEFT JOIN agent_jobs j ON j.submission_id=s.id
                    LEFT JOIN submission_media m ON m.submission_id=s.id
                    WHERE s.source='photo' AND s.state='queued' AND j.id IS NULL
                    GROUP BY s.id HAVING count(m.id)=0
                )
            """,
            "calendar_request_family_mismatch": """
                SELECT count(*) FROM calendar_event_requests q
                JOIN calendar_events e ON e.id=q.event_id
                WHERE q.family_id<>e.family_id
            """,
        }
        results = {name: scalar(db, query) for name, query in checks.items()}
        failures = {name: value for name, value in results.items() if value}
        if failures:
            raise SystemExit(f"DATABASE_AUDIT_FAILED consistency={failures}")
        counts = {
            table: int(scalar(db, f"SELECT count(*) FROM {table}")) for table in BUSINESS_TABLES
        }
        if args.require_empty and any(counts.values()):
            raise SystemExit(f"DATABASE_AUDIT_FAILED expected_empty={counts}")
    print(f"DATABASE_AUDIT_VALID path={database} counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
