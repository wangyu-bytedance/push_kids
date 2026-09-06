from push_kids.activities.capacity import ensure_timed_item_capacity
from sqlalchemy.dialects import mysql


class RecordingSession:
    def __init__(self) -> None:
        self.statements = []

    def scalar(self, statement):
        self.statements.append(statement)
        return object()

    def scalars(self, statement):
        self.statements.append(statement)
        return []


def test_capacity_uses_locking_current_reads_after_the_child_lock() -> None:
    db = RecordingSession()
    ensure_timed_item_capacity(db, "family", "child")  # type: ignore[arg-type]

    sql = [str(statement.compile(dialect=mysql.dialect())).upper() for statement in db.statements]
    assert len(sql) == 4
    assert all("FOR UPDATE" in statement for statement in sql)
