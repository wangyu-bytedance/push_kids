#!/usr/bin/env python3
"""Safely identify or fail legacy pending analyses whose proposal is empty."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from push_kids.learning.service import LearningService  # noqa: E402
from push_kids.platform.config import Settings  # noqa: E402
from push_kids.platform.database import Database  # noqa: E402


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family-id",
        help="tenant boundary for targeted apply; never included in tool output",
    )
    parser.add_argument(
        "--submission-id",
        action="append",
        default=[],
        help="explicit target; repeat for multiple records",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="change matching pending records to failed; default is dry-run",
    )
    args = parser.parse_args()
    if args.apply and (not args.family_id or not args.submission_id):
        parser.error("--apply requires --family-id and at least one --submission-id")

    database = Database(Settings())
    with database.session_factory() as db:
        matches = LearningService.repair_empty_pending_analysis(
            db,
            family_id=args.family_id,
            submission_ids=args.submission_id or None,
            apply=args.apply,
        )
    print(
        json.dumps(
            {
                "mode": "apply" if args.apply else "dry-run",
                "matched_count": len(matches),
                "submission_fingerprints": [_fingerprint(item) for item in matches],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
