"""History-independent snapshot projection: 10k/50k grants cannot expand response or reads."""

import json
from datetime import date, timedelta
from uuid import uuid4

import pytest
from push_kids.notifications.renewal_service import NotificationRenewalService
from push_kids.persistence.models import (
    NotificationGrantAttempt,
    ReviewMemberCompletionReceipt,
)
from push_kids.platform.context import RequestContext
from push_kids.platform.time import utcnow
from sqlalchemy import event, insert, text

from tests.integration.test_notification_channel import _create_family
from tests.integration.test_notification_renewal import reviews


@pytest.fixture
def app(notification_app):
    return notification_app


@pytest.mark.parametrize("size", [10000, 50000])
def test_renewal_snapshot_ignores_grant_history(client, app, size):
    family = _create_family(client)
    assert_bounded_history(client, app, size, family)


def assert_bounded_history(client, app, size, family):
    fid, mid = family["family"]["id"], family["member"]["id"]
    rid = reviews(app, family, 1)[0]
    now = utcnow()
    with app.state.database.session_factory() as db:
        for start in range(0, size, 1000):
            db.execute(
                insert(NotificationGrantAttempt),
                [
                    {
                        "id": uuid4().hex,
                        "family_id": fid,
                        "member_id": mid,
                        "request_key": f"scale-{i}",
                        "request_fingerprint": "0" * 64,
                        "mode": "manual",
                        "choice_version": 0,
                        "bindings_json": "[]",
                        "state": "registered",
                        "expires_at": now - timedelta(days=1),
                        "created_at": now,
                        "updated_at": now,
                    }
                    for i in range(start, min(size, start + 1000))
                ],
            )
            db.execute(
                insert(ReviewMemberCompletionReceipt),
                [
                    {
                        "family_id": fid,
                        "member_id": mid,
                        "review_id": rid,
                        "child_id": family["children"][0]["id"],
                        "day": date(1800, 1, 1) + timedelta(days=i),
                        "created_at": now,
                    }
                    for i in range(start, min(size, start + 1000))
                ],
            )
        db.commit()
        queries = []

        def capture(_conn, _cursor, statement, _parameters, _context, _many):
            queries.append(statement)

        event.listen(app.state.database.engine, "before_cursor_execute", capture)
        try:
            view = NotificationRenewalService.view(
                db,
                RequestContext(fid, None, None, None, member_id=mid),
                app.state.notification_channel,
            )
        finally:
            event.remove(app.state.database.engine, "before_cursor_execute", capture)
        assert len(queries) <= 6
        assert not any(
            "notification_grant_attempts" in sql or "completion_receipts" in sql for sql in queries
        )
        assert len(view.types) == 3
        assert len(json.dumps(view.model_dump(mode="json")).encode()) <= 12 * 1024
        mysql = db.get_bind().dialect.name == "mysql"
        plan = db.execute(
            text(
                ("EXPLAIN " if mysql else "EXPLAIN QUERY PLAN ") + "SELECT total_completed FROM "
                "review_member_completion_progress WHERE family_id=:fid AND member_id=:mid"
            ),
            {"fid": fid, "mid": mid},
        ).all()
        if mysql:
            assert any("PRIMARY" in str(row) and "const" in str(row) for row in plan)
        else:
            assert any("SEARCH" in str(row) and "INDEX" in str(row) for row in plan)
