from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from push_kids.persistence.models import Base
from sqlalchemy import create_engine, inspect, text

from tests.integration.test_notification_migration import _config, _seed


@pytest.mark.parametrize("from_existing", [False, True])
def test_renewal_expand_schema_check_and_safe_rollback(tmp_path: Path, monkeypatch, from_existing):
    url = f"sqlite:///{tmp_path / 'renewal-migration.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    if from_existing:
        command.upgrade(config, "20261012_0019")
        _seed(url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    assert_renewal_schema(engine)
    tables = set(inspect(engine).get_table_names())
    assert tables >= {
        "notification_grant_attempts",
        "notification_renewal_states",
        "notification_renewal_preferences",
        "review_member_completion_progress",
        "review_member_completion_receipts",
    }
    if from_existing:
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
    assert "notification_grant_attempts" not in inspect(engine).get_table_names()
    engine.dispose()


def assert_renewal_schema(engine):
    """Check this expand migration without masking unrelated historical index drift."""
    names = {
        "notification_grant_attempts",
        "notification_renewal_states",
        "notification_renewal_preferences",
        "review_member_completion_progress",
        "review_member_completion_receipts",
    }
    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={
                "compare_type": True,
                "include_object": lambda obj, name, kind, reflected, compared: (
                    (
                        name
                        if kind == "table"
                        else getattr(getattr(obj, "table", None), "name", None)
                    )
                    in names
                ),
            },
        )
        assert compare_metadata(context, Base.metadata) == []
