"""Read-only release gate; inject a migration account through a secure environment."""

from __future__ import annotations

import json

from push_kids.platform.config import Settings
from push_kids.platform.database import Database


def main() -> int:
    database = None
    try:
        database = Database(Settings())
        database.verify_cloud_schema(verify_triggers=True)
    except Exception as exc:
        # Connection errors may embed credentials; never print their message/traceback.
        print(json.dumps({"status": "FAIL", "error_category": type(exc).__name__}))
        return 1
    finally:
        if database is not None:
            database.engine.dispose()
    print(json.dumps({"status": "PASS", "revision": Database.expected_cloud_revision}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
