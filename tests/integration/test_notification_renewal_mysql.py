"""Isolated MySQL 5.7 two-session renewal/feedback gate; never sends a notification."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from push_kids.bootstrap.app import create_app
from push_kids.platform.config import Settings
from sqlalchemy import create_engine, text

from tests.conftest import NOTIFICATION_TEMPLATES
from tests.integration.test_notification_channel import _create_family
from tests.integration.test_notification_migration import _config, _seed
from tests.integration.test_notification_renewal import (
    choice,
    complete,
    prepare,
    read,
    result,
    reviews,
    spend,
)
from tests.integration.test_notification_renewal_migration import assert_renewal_schema
from tests.performance.test_notification_renewal_reads import assert_bounded_history

MYSQL_URL = os.getenv("PUSH_KIDS_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="isolated MySQL5.7 not configured")


@pytest.mark.skipif(
    not os.getenv("PUSH_KIDS_TEST_MYSQL_MIGRATION_URL"),
    reason="isolated migration DB not configured",
)
def test_mysql57_expand_migration_preserves_data_and_refuses_loss(monkeypatch):
    url = os.environ["PUSH_KIDS_TEST_MYSQL_MIGRATION_URL"]
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, "20261012_0019")
    _seed(url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    assert_renewal_schema(engine)
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM children")) == 1
        connection.execute(
            text(
                "INSERT INTO notification_renewal_preferences "
                "(family_id,member_id,choice,version,updated_at) "
                "VALUES ('family-1','member-1','disabled',1,CURRENT_TIMESTAMP)"
            )
        )
    with pytest.raises(RuntimeError, match="Cannot discard"):
        command.downgrade(config, "20261012_0019")
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM notification_renewal_preferences"))
    command.downgrade(config, "20261012_0019")
    engine.dispose()


def test_mysql57_overlapping_grants_completions_and_choice(tmp_path):
    app = create_app(
        Settings(
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_DATABASE_URL=MYSQL_URL,
            PUSH_KIDS_MEDIA_ROOT=tmp_path,
            PUSH_KIDS_AI_PROVIDER="test",
            PUSH_KIDS_RUN_WORKER=False,
            PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=False,
            PUSH_KIDS_NOTIFICATION_CHANNEL="recording",
            PUSH_KIDS_NOTIFICATION_TEMPLATES=NOTIFICATION_TEMPLATES,
        )
    )
    with TestClient(app) as client:
        family = _create_family(client)
        attempt = prepare(client)

        def overlap(action):
            gate = Barrier(2)

            def run():
                gate.wait(timeout=10)
                response = action()
                assert response.status_code == 200, response.text
                return response.json()

            with ThreadPoolExecutor(max_workers=2) as pool:
                return list(pool.map(lambda _: run(), range(2)))

        assert len(overlap(lambda: result(client, attempt))) == 2
        assert read(client)["settings"]["preferences"][-1]["remaining_quota"] == 1
        spend(app)
        assert choice(client, "enabled").status_code == 200
        rid, *others = reviews(app, family, 3)
        overlap(lambda: complete(client, rid, key="mysql-identical-feedback"))
        assert read(client)["completion_cursor"] == 1
        gate = Barrier(2)

        def finish(rid):
            gate.wait(timeout=10)
            response = complete(client, rid)
            assert response.status_code == 200, response.text

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(finish, others))
        assert read(client)["completion_cursor"] == 3
        version = read(client)["version"]
        key = str(uuid4())
        overlap(lambda: choice(client, "disabled", version=version, key=key))
        assert read(client)["version"] == version + 1
        assert read(client)["choice"] == "disabled"
        assert_bounded_history(client, app, 50000, family)
