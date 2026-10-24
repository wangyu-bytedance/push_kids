"""Skewed 50k histories: bounded returned rows AND indexed work, SQLite/MySQL 5.7 gate."""

import json
import os
import tracemalloc
from datetime import date, timedelta
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.footprints.models import FootprintImport, FootprintPhoto, FootprintVisit
from push_kids.footprints.reads import FootprintReads
from push_kids.platform.config import Settings
from push_kids.platform.errors import NotFoundError
from push_kids.platform.time import utcnow
from sqlalchemy import create_engine, event, insert
from sqlalchemy.engine import make_url


@pytest.fixture(params=["sqlite", "mysql"])
def read_case(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        yield request.getfixturevalue("app"), request.getfixturevalue("child")
        return
    configured = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
    if not configured:
        pytest.skip("isolated MySQL5.7 not configured")
    base_url = make_url(configured)
    name = "footprint_read_" + uuid4().hex[:12]
    server = create_engine(base_url.set(database=None))
    application = None
    with server.begin() as db:
        assert str(db.exec_driver_sql("SELECT VERSION()").scalar()).startswith("5.7.")
        db.exec_driver_sql(
            f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    try:
        url = base_url.set(database=name).render_as_string(hide_password=False)
        monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
        config = Config()
        config.set_main_option(
            "script_location", str(Path(__file__).parents[2] / "apps/api/migrations")
        )
        config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
        command.upgrade(config, "head")
        application = create_app(
            Settings(
                PUSH_KIDS_ENV="test",
                PUSH_KIDS_DATABASE_URL=url,
                PUSH_KIDS_MEDIA_ROOT=tmp_path,
                PUSH_KIDS_AI_PROVIDER="test",
                PUSH_KIDS_RUN_WORKER=False,
                PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
            )
        )
        with TestClient(application) as client:
            response = client.post(
                "/api/v1/children",
                headers={"X-Family-ID": "family-test-a"},
                json={"name": "合成孩子", "grade": "一年级"},
            )
            assert response.status_code == 201
            yield application, response.json()
    finally:
        if application is not None:
            application.state.database.engine.dispose()
        with server.begin() as db:
            db.exec_driver_sql(f"DROP DATABASE `{name}`")
        server.dispose()


@pytest.mark.parametrize("visit_count", [1, 1000])
def test_skewed_fifty_thousand_photo_read_budget(read_case, visit_count):
    app, child = read_case
    database = app.state.database
    family, cid, now = "family-test-a", child["id"], utcnow()
    scope = {"family_id": family, "child_id": cid}
    with database.session_factory() as db:
        db.execute(
            insert(FootprintImport),
            [
                {
                    **scope,
                    "id": f"batch-{i}",
                    "member_id": "local",
                    "request_key": f"key-{i}",
                    "request_fingerprint": "synthetic",
                    "slot_count": 20,
                }
                for i in range(2500)
            ],
        )
        db.execute(
            insert(FootprintVisit),
            [
                {
                    **scope,
                    "id": f"visit-{i}",
                    "local_date": date(2020, 1, 1) + timedelta(days=i),
                    "place_key": f"place-{i}",
                    "place_name": "合成地点",
                    "country": "中国",
                    "city": "合成城市",
                    "latitude": 39.9 + i * 0.00001,
                    "longitude": 116.4,
                    "coordinate_system": "gcj02",
                    "sort_time": "12:00:00",
                    "sort_created_at": now,
                }
                for i in range(visit_count)
            ],
        )
        db.execute(
            insert(FootprintPhoto),
            [
                {
                    **scope,
                    "id": f"photo-{i:06d}",
                    "import_id": f"batch-{i // 20}",
                    "visit_id": f"visit-{i % visit_count}",
                    "ordinal": i % 20,
                    "state": "confirmed",
                    "ticket_expires_at": now,
                    "upload_path": "synthetic",
                    "derived_ready": True,
                    "local_date": date(2020, 1, 1),
                    "confirmed_at": now,
                }
                for i in range(50000)
            ],
        )
        # Deliberately adversarial rows reference a visible visit. Neither another
        # tenant's photo nor a deleted photo may displace its first four previews.
        for label, photo_family, state in (
            ("foreign", "another-family", "confirmed"),
            ("deleted", family, "deleted"),
        ):
            db.execute(
                insert(FootprintPhoto).values(
                    **{**scope, "family_id": photo_family},
                    id=f"hidden-{label}",
                    import_id="batch-0",
                    visit_id=f"visit-{visit_count - 1}",
                    ordinal=-1,
                    state=state,
                    ticket_expires_at=now,
                    upload_path="synthetic",
                )
            )
        db.commit()
    queries = []

    def record(_connection, _cursor, statement, params, _context, _many):
        queries.append((statement, params))

    event.listen(database.engine, "before_cursor_execute", record)
    tracemalloc.start()
    try:
        with database.session_factory() as db:
            started = perf_counter()
            result = FootprintReads.visits(db, family, cid, limit=50)
            elapsed = perf_counter() - started
            assert len(queries) <= 5
            assert elapsed < 0.5, f"timeline took {elapsed:.3f}s"
            assert len(result["items"]) == min(50, visit_count)
            assert all(len(row["photos"]) <= 4 for row in result["items"])
            assert sum(row["photo_count"] for row in result["items"]) == (
                50000 if visit_count == 1 else 2500
            )
            for row in result["items"]:
                visit_index = int(row["id"].removeprefix("visit-"))
                candidates = range(visit_index, 50000, visit_count)
                expected = sorted(candidates, key=lambda i: (i % 20, i))[:4]
                assert [photo["id"] for photo in row["photos"]] == [
                    f"photo-{i:06d}" for i in expected
                ]
            assert len(json.dumps(jsonable_encoder(result)).encode()) < 512 * 1024
            # Explain the executed preview, including its real bound parameters.
            preview_sql, preview_params = queries[-1]
            queries.clear()
            points = FootprintReads.map_points(db, family, cid)
            assert len(points["items"]) <= 200 and len(queries) <= 7
            assert len(json.dumps(jsonable_encoder(points)).encode()) < 256 * 1024
            queries.clear()
            playback = FootprintReads.playback(db, family, cid)
            assert len(playback["items"]) <= 100 and len(queries) <= 5
            _, peak = tracemalloc.get_traced_memory()
            assert peak < 16 * 1024 * 1024, f"bounded reads allocated {peak} bytes"
            dialect = database.engine.dialect.name
            prefix = "EXPLAIN " if dialect == "mysql" else "EXPLAIN QUERY PLAN "
            plan = list(
                db.connection().exec_driver_sql(prefix + preview_sql, preview_params).mappings()
            )
            if dialect == "mysql":
                assert all("DEPENDENT" not in row["select_type"] for row in plan)
                photos = [row for row in plan if row["table"] == "footprint_photos"]
                ranges = [row for row in photos if row["select_type"] == "DERIVED"]
                assert len(ranges) == min(50, visit_count)
                assert all(
                    row["key"] == "ix_footprint_photo_visit" and row["type"] in {"ref", "range"}
                    for row in ranges
                ), ranges
                joined = [row for row in photos if row["select_type"] == "PRIMARY"]
                assert len(joined) == 1
                assert joined[0]["key"] == "PRIMARY" and joined[0]["type"] == "eq_ref"
            else:
                assert "ix_footprint_photo_visit" in str(plan)
            queries.clear()
            if visit_count > 50:
                second = FootprintReads.visits(
                    db, family, cid, cursor=result["next_cursor"], limit=50
                )
                assert len(queries) <= 5
                assert [row["id"] for row in second["items"]] == [
                    f"visit-{i}" for i in range(visit_count - 51, visit_count - 101, -1)
                ]
            else:
                assert result["next_cursor"] is None
            with pytest.raises(NotFoundError):
                FootprintReads.visits(db, "another-family", cid, cursor=result["next_cursor"])
            print(
                f"FOOTPRINTS_READ_BUDGET dialect={dialect} visits={visit_count} "
                f"timeline_seconds={elapsed:.4f} peak_bytes={peak} plan=passed"
            )
    finally:
        tracemalloc.stop()
        event.remove(database.engine, "before_cursor_execute", record)
