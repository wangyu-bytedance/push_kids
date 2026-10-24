"""Versioned storage contract for migration 0023; max three rows per review."""

from sqlalchemy import text

from push_kids.persistence.review_queue_v2 import TRIGGER_SOURCES

COLUMNS = "review_item_id,slot_on,family_id,child_id,subject_id,minutes,priority_key"


def projection_select(dialect: str, condition: str = "1=1") -> str:
    parts = []
    for days in (3, 2, 1):
        slot = (
            f"DATE_SUB(r.due_date, INTERVAL {days} DAY)"
            if dialect == "mysql"
            else f"DATE(r.due_date, '-{days} day')"
        )
        elapsed = (
            f"DATEDIFF({slot},r.last_reviewed_on)"
            if dialect == "mysql"
            else f"(JULIANDAY({slot})-JULIANDAY(r.last_reviewed_on))"
        )
        interval = (
            "DATEDIFF(r.due_date,r.last_reviewed_on)"
            if dialect == "mysql"
            else "(JULIANDAY(r.due_date)-JULIANDAY(r.last_reviewed_on))"
        )
        cooldown = (
            f"DATEDIFF({slot},r.last_offered_on)>=2"
            if dialect == "mysql"
            else f"JULIANDAY({slot})-JULIANDAY(r.last_offered_on)>=2"
        )
        key = (
            "CONCAT(r.due_date,r.last_reviewed_on,r.id)"
            if dialect == "mysql"
            else "(r.due_date || r.last_reviewed_on || r.id)"
        )
        parts.append(f"""SELECT r.id AS review_item_id,{slot} AS slot_on,
            r.family_id AS family_id,r.child_id AS child_id,k.subject_id AS subject_id,
            CASE WHEN k.estimated_minutes<1 THEN 1 WHEN k.estimated_minutes>5 THEN 5
              ELSE k.estimated_minutes END AS minutes,{key} AS priority_key
            FROM review_items r
            JOIN knowledge_items k ON k.id=r.knowledge_item_id
              AND k.family_id=r.family_id AND k.child_id=r.child_id
            JOIN subjects s ON s.id=k.subject_id AND s.family_id=r.family_id
              AND s.child_id=r.child_id
            JOIN children c ON c.id=r.child_id AND c.family_id=r.family_id
            LEFT JOIN review_schedule_overrides o ON o.review_item_id=r.id
              AND o.family_id=r.family_id AND o.child_id=r.child_id
            WHERE ({condition}) AND r.active AND r.review_count>0 AND r.last_reviewed_on IS NOT NULL
              AND k.review_status='normal' AND s.active AND s.kind='learning'
              AND c.active AND NOT c.deleting AND o.review_item_id IS NULL
              AND {interval}>0 AND {elapsed}>=2 AND 5*{elapsed}>=4*{interval}
              AND (r.last_offered_on IS NULL OR {cooldown})
              AND (r.queue_eligible_on IS NULL OR r.queue_eligible_on=r.due_date
                   OR r.queue_eligible_on<={slot})
              AND (c.review_queue_resumed_on IS NULL OR c.review_queue_resumed_on<={slot})
              AND (s.review_queue_resumed_on IS NULL OR s.review_queue_resumed_on<={slot})""")
    return " UNION ALL ".join(parts)


def refresh_sql(dialect: str, condition: str) -> str:
    return f"INSERT INTO review_early_slots ({COLUMNS}) " + projection_select(dialect, condition)


def trigger_statements(dialect: str):
    for table, (key, fields, review_key) in TRIGGER_SOURCES.items():
        operations = (
            ("insert", "update", "delete")
            if table == "review_schedule_overrides"
            else (("insert", "update", "delete") if table == "review_items" else ("update",))
        )
        for operation in operations:
            row = "OLD" if operation == "delete" else "NEW"
            condition = f"{review_key}={row}.{key} AND r.family_id={row}.family_id"
            if table != "children":
                condition += f" AND r.child_id={row}.child_id"
            remove = (
                f"DELETE FROM review_early_slots WHERE review_item_id={row}.id"
                if table == "review_items"
                else (
                    "DELETE FROM review_early_slots WHERE review_item_id IN "
                    "(SELECT r.id FROM review_items r JOIN knowledge_items k "
                    f"ON k.id=r.knowledge_item_id WHERE {condition})"
                )
            )
            insert = (
                ""
                if table == "review_items" and operation == "delete"
                else refresh_sql(dialect, condition) + ";"
            )
            body = remove + ";" + insert
            name = f"ers_v1_{table}_{operation}"
            if dialect == "mysql":
                changed = " OR ".join(f"NOT (OLD.{f} <=> NEW.{f})" for f in fields)
                if operation == "update":
                    body = f"IF {changed} THEN {body} END IF;"
                sql = (
                    f"CREATE TRIGGER {name} AFTER {operation.upper()} ON {table} "
                    f"FOR EACH ROW BEGIN {body} END"
                )
            else:
                changed = " OR ".join(f"OLD.{f} IS NOT NEW.{f}" for f in fields)
                when = f" WHEN {changed}" if operation == "update" else ""
                sql = (
                    f"CREATE TRIGGER {name} AFTER {operation.upper()} ON {table} "
                    f"FOR EACH ROW{when} BEGIN {body} END"
                )
            yield name, sql


def install(connection) -> None:
    dialect = connection.dialect.name
    uninstall(connection)
    for _, sql in trigger_statements(dialect):
        connection.execute(text(sql))
    after = ""
    while True:
        ids = list(
            connection.execute(
                text("SELECT id FROM review_items WHERE id>:after ORDER BY id LIMIT 1000"),
                {"after": after},
            ).scalars()
        )
        if not ids:
            break
        connection.execute(
            text(refresh_sql(dialect, "r.id>:after AND r.id<=:last")),
            {"after": after, "last": ids[-1]},
        )
        after = ids[-1]


def uninstall(connection) -> None:
    for name, _ in trigger_statements(connection.dialect.name):
        connection.execute(text(f"DROP TRIGGER IF EXISTS {name}"))
