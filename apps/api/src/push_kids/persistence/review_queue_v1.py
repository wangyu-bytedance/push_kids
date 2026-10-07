"""Frozen v1 storage contract for planning's derived review queue (migration 0018).

Triggers cover Core/bulk writes and the compatible old application during rollout.
Keep this version immutable after release; future changes get a new migration/contract.
"""

from sqlalchemy import text

COLUMNS = (
    "review_item_id",
    "family_id",
    "child_id",
    "subject_id",
    "minutes",
    "repeated",
    "available",
    "manual",
    "due_on",
    "anchor_on",
    "priority_key",
    "last_offered_on",
)
TRIGGER_SOURCES = {
    "review_items": (
        "id",
        (
            "due_date",
            "queue_eligible_on",
            "last_offered_on",
            "last_reviewed_on",
            "review_count",
            "active",
        ),
        "r.id",
    ),
    "knowledge_items": ("id", ("estimated_minutes", "subject_id"), "r.knowledge_item_id"),
    "children": ("id", ("active", "deleting", "review_queue_resumed_on"), "r.child_id"),
    "subjects": ("id", ("active", "kind", "review_queue_resumed_on"), "k.subject_id"),
    "review_schedule_overrides": ("review_item_id", ("scheduled_on",), "r.id"),
}


def projection_select(dialect: str, condition: str = "1=1") -> str:
    after = (
        "DATE_ADD(r.last_offered_on, INTERVAL 1 DAY)"
        if dialect == "mysql"
        else "DATE(r.last_offered_on, '+1 day')"
    )
    maximum = "GREATEST" if dialect == "mysql" else "MAX"
    anchor = f"""{maximum}(r.due_date, COALESCE(r.queue_eligible_on,r.due_date),
        COALESCE(c.review_queue_resumed_on,r.due_date),
        COALESCE(s.review_queue_resumed_on,r.due_date),
        COALESCE({after},r.due_date))"""
    key = (
        f"CONCAT({anchor},r.due_date,COALESCE(r.last_reviewed_on,'0001-01-01'),r.id)"
        if dialect == "mysql"
        else f"({anchor} || r.due_date || COALESCE(r.last_reviewed_on,'0001-01-01') || r.id)"
    )
    return f"""SELECT r.id AS review_item_id,r.family_id,r.child_id,k.subject_id,
        CASE WHEN k.estimated_minutes<1 THEN 1 WHEN k.estimated_minutes>5 THEN 5
          ELSE k.estimated_minutes END AS minutes,
        (r.review_count>0) AS repeated,
        (r.active AND s.active AND s.kind='learning' AND c.active AND NOT c.deleting) AS available,
        (o.review_item_id IS NOT NULL) AS manual,r.due_date AS due_on,
        {anchor} AS anchor_on,{key} AS priority_key,r.last_offered_on
        FROM review_items r
        JOIN knowledge_items k ON k.id=r.knowledge_item_id
          AND k.family_id=r.family_id AND k.child_id=r.child_id
        JOIN subjects s ON s.id=k.subject_id AND s.family_id=r.family_id AND s.child_id=r.child_id
        JOIN children c ON c.id=r.child_id AND c.family_id=r.family_id
        LEFT JOIN review_schedule_overrides o ON o.review_item_id=r.id
          AND o.family_id=r.family_id AND o.child_id=r.child_id
        WHERE {condition}"""


def upsert_sql(dialect: str, condition: str) -> str:
    insert = f"INSERT INTO review_queue_entries ({','.join(COLUMNS)}) " + projection_select(
        dialect, condition
    )
    if dialect == "mysql":
        return (
            insert + " ON DUPLICATE KEY UPDATE " + ",".join(f"{c}=VALUES({c})" for c in COLUMNS[1:])
        )
    return (
        insert
        + " ON CONFLICT(review_item_id) DO UPDATE SET "
        + ",".join(f"{c}=excluded.{c}" for c in COLUMNS[1:])
    )


def trigger_statements(dialect: str):
    for table, (key, changed_fields, review_key) in TRIGGER_SOURCES.items():
        operations = (
            ("insert", "update", "delete")
            if table == "review_schedule_overrides"
            else (("insert", "update") if table == "review_items" else ("update",))
        )
        for operation in operations:
            name = f"rq_v1_{table}_{operation}"
            row = "OLD" if operation == "delete" else "NEW"
            condition = (
                f"{review_key}={row}.{key} AND r.family_id={row}.family_id "
                f"AND r.child_id={row}.child_id"
                if table != "children"
                else f"{review_key}={row}.{key} AND r.family_id={row}.family_id"
            )
            statement = upsert_sql(dialect, condition)
            if dialect == "mysql":
                changed = " OR ".join(f"NOT (OLD.{f} <=> NEW.{f})" for f in changed_fields)
                body = (
                    f"IF {changed} THEN {statement}; END IF;"
                    if operation == "update"
                    else statement + ";"
                )
                sql = (
                    f"CREATE TRIGGER {name} AFTER {operation.upper()} ON {table} "
                    f"FOR EACH ROW BEGIN {body} END"
                )
            else:
                changed = " OR ".join(f"OLD.{f} IS NOT NEW.{f}" for f in changed_fields)
                when = f" WHEN {changed}" if operation == "update" else ""
                sql = (
                    f"CREATE TRIGGER {name} AFTER {operation.upper()} ON {table} "
                    f"FOR EACH ROW{when} BEGIN {statement}; END"
                )
            yield name, sql


def install(connection) -> None:
    dialect = connection.dialect.name
    for name, sql in trigger_statements(dialect):
        connection.execute(text(f"DROP TRIGGER IF EXISTS {name}"))
        connection.execute(text(sql))
    connection.execute(text(upsert_sql(dialect, "1=1")))


def uninstall(connection) -> None:
    for name, _ in trigger_statements(connection.dialect.name):
        connection.execute(text(f"DROP TRIGGER IF EXISTS {name}"))
