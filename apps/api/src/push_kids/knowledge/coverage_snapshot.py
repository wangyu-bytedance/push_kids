"""Stable content snapshots used across proposal, confirmation and background work."""

import hashlib
import json


def content_fingerprint(
    name: str | None, category: str | None, method: str | None, evidence: str
) -> str:
    return hashlib.sha256(
        json.dumps(
            [name, category, method, evidence], ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def point_fingerprint(point) -> str:
    return hashlib.sha256(
        json.dumps(
            point.model_dump(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
