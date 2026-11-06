from alembic import command
from sqlalchemy import create_engine, inspect

from tests.integration.test_read_path_indexes_migration import _config


def test_recent_subject_index_upgrade_and_downgrade_preserve_prior_head(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'recent-history.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    command.upgrade(config, "20261105_0026")
    engine = create_engine(url)
    assert "ix_knowledge_recent_subject" not in {
        i["name"] for i in inspect(engine).get_indexes("knowledge_items")
    }
    command.upgrade(config, "20261105_0027")
    indexes = {i["name"]: i["column_names"] for i in inspect(engine).get_indexes("knowledge_items")}
    assert indexes["ix_knowledge_recent_subject"] == [
        "family_id",
        "child_id",
        "subject_id",
        "review_status",
        "created_at",
        "id",
    ]
    command.downgrade(config, "20261105_0026")
    assert "ix_knowledge_recent_subject" not in {
        i["name"] for i in inspect(engine).get_indexes("knowledge_items")
    }
    engine.dispose()
