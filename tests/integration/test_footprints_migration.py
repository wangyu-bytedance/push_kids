from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from push_kids.footprints.models import FootprintPreference
from push_kids.persistence.models import Base
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from tests.integration.test_notification_migration import _config, _seed


@pytest.mark.parametrize("from_existing", [False, True])
def test_expand_parity_preservation_and_safe_rollback(tmp_path: Path, monkeypatch, from_existing):
    url = f"sqlite:///{tmp_path / 'footprints-migration.db'}"
    monkeypatch.setenv("PUSH_KIDS_DATABASE_URL", url)
    config = _config(url)
    if from_existing:
        command.upgrade(config, "20261017_0020")
        _seed(url)
    command.upgrade(config, "head")
    engine = create_engine(url)
    tables = {name for name in inspect(engine).get_table_names() if name.startswith("footprint_")}
    assert len(tables) == 5
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
                    in tables
                ),
            },
        )
        assert compare_metadata(context, Base.metadata) == []
    with Session(engine) as db:
        db.add(FootprintPreference(family_id="local-synthetic", member_id="local"))
        db.commit()
    with pytest.raises(RuntimeError, match="Cannot discard"):
        command.downgrade(config, "20261017_0020")
    with Session(engine) as db:
        db.query(FootprintPreference).delete()
        db.commit()
    command.downgrade(config, "20261017_0020")
    assert not any(name.startswith("footprint_") for name in inspect(engine).get_table_names())
    engine.dispose()
