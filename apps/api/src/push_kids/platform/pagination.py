"""Opaque, scope-bound cursor transport for bounded collection reads.

The codec carries only paging anchors.  It never authorizes a resource: every
consumer must still apply its normal family/resource filters before returning a
row.
"""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping, Sequence

CURSOR_VERSION = 1
MAX_CURSOR_LENGTH = 1500


def _scope_digest(parts: Sequence[object]) -> str:
    raw = json.dumps(list(parts), ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def encode_cursor(scope: Sequence[object], anchor: Mapping[str, object]) -> str:
    payload = {
        "v": CURSOR_VERSION,
        "scope": _scope_digest(scope),
        "anchor": dict(anchor),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_cursor(token: str, scope: Sequence[object]) -> dict[str, object]:
    if not token or len(token) > MAX_CURSOR_LENGTH:
        raise ValueError("分页已失效，请刷新列表")
    try:
        raw = base64.b64decode(token.encode(), altchars=b"-_", validate=True)
        payload = json.loads(raw)
        if (
            not isinstance(payload, dict)
            or payload.get("v") != CURSOR_VERSION
            or payload.get("scope") != _scope_digest(scope)
            or not isinstance(payload.get("anchor"), dict)
        ):
            raise ValueError
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("分页已失效，请刷新列表") from exc
    return payload["anchor"]
