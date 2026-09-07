"""Inbound WeChat subscription events.

WeChat pushes three subscription events to the configured message-push URL: the parent's answer to
a subscribe dialog, a later "stop receiving" switch inside 服务通知, and the asynchronous result of
a message we already handed over. Without them the outbox is blind: it keeps spending one-off
grants on a parent who has already refused, and reports `sent` for a message WeChat later dropped.

This module only verifies the caller and turns the payload into a small, safe shape. It performs no
database work and holds no policy, so a malformed or hostile body cannot reach the outbox.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from xml.etree import ElementTree

# A subscription event is a few hundred bytes. Anything larger is refused before parsing so an
# oversized or expansion-style XML body never reaches the parser.
MAX_BODY_BYTES = 16 * 1024
_UNSAFE_XML_MARKERS = ("<!DOCTYPE", "<!ENTITY", "<?xml-stylesheet")

POPUP = "popup"
CHANGE = "change"
SENT = "sent"
EVENT_KINDS = {
    "subscribe_msg_popup_event": POPUP,
    "subscribe_msg_change_event": CHANGE,
    "subscribe_msg_sent_event": SENT,
}
# WeChat's own words for what the parent did. Anything else is treated as "no conclusion".
DECISIONS = ("accept", "reject", "ban", "filter")


class InboundEventError(ValueError):
    """Raised when a pushed body cannot be trusted or understood."""


@dataclass(frozen=True)
class TemplateDecision:
    template_id: str
    status: str


@dataclass(frozen=True)
class InboundEvent:
    kind: str
    receiver: str
    decisions: tuple[TemplateDecision, ...] = ()
    msg_id: str = ""
    error_code: int = 0


def verify_signature(token: str, timestamp: str, nonce: str, signature: str) -> bool:
    """WeChat's message-push signature: sha1 over the sorted token/timestamp/nonce triple."""
    if not token or not signature:
        return False
    payload = "".join(sorted([token, timestamp or "", nonce or ""]))
    expected = hashlib.sha1(payload.encode(), usedforsecurity=False).hexdigest()
    return hmac.compare_digest(expected, signature)


def _decision(template_id: str, status: str) -> TemplateDecision | None:
    if not template_id:
        return None
    value = status if status in DECISIONS else ""
    return TemplateDecision(template_id=template_id, status=value)


def _entries(payload: object) -> list[dict[str, object]]:
    """`List` is a bare object for a single template and an array for several."""
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _from_json(body: bytes) -> InboundEvent | None:
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InboundEventError("消息推送内容不是合法 JSON") from exc
    if not isinstance(decoded, dict):
        raise InboundEventError("消息推送内容结构无法识别")
    kind = EVENT_KINDS.get(str(decoded.get("Event") or ""))
    if kind is None:
        return None
    receiver = str(decoded.get("FromUserName") or decoded.get("openid") or "")
    rows = _entries(decoded.get("List"))
    if kind == SENT:
        first = rows[0] if rows else {}
        return InboundEvent(
            kind=kind,
            receiver=receiver,
            msg_id=str(first.get("MsgID") or ""),
            error_code=_as_int(first.get("ErrorCode")),
        )
    decisions = []
    for row in rows:
        item = _decision(
            str(row.get("TemplateId") or ""), str(row.get("SubscribeStatusString") or "")
        )
        if item is not None:
            decisions.append(item)
    return InboundEvent(kind=kind, receiver=receiver, decisions=tuple(decisions))


def _as_int(value: object) -> int:
    try:
        return int(str(value or 0))
    except ValueError:
        return 0


def _text(node: ElementTree.Element, tag: str) -> str:
    found = node.find(tag)
    return (found.text or "").strip() if found is not None else ""


def _from_xml(body: bytes) -> InboundEvent | None:
    text = body.decode("utf-8", errors="replace")
    if any(marker in text for marker in _UNSAFE_XML_MARKERS):
        # No legitimate WeChat payload declares a doctype or entities; refusing them removes the
        # entity-expansion class of attack without pulling in another XML dependency.
        raise InboundEventError("消息推送内容包含不允许的 XML 声明")
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise InboundEventError("消息推送内容不是合法 XML") from exc
    kind = EVENT_KINDS.get(_text(root, "Event"))
    if kind is None:
        return None
    receiver = _text(root, "FromUserName")
    rows = root.findall(".//List")
    if kind == SENT:
        first = rows[0] if rows else None
        return InboundEvent(
            kind=kind,
            receiver=receiver,
            msg_id=_text(first, "MsgID") if first is not None else "",
            error_code=_as_int(_text(first, "ErrorCode")) if first is not None else 0,
        )
    decisions = []
    for row in rows:
        item = _decision(_text(row, "TemplateId"), _text(row, "SubscribeStatusString"))
        if item is not None:
            decisions.append(item)
    return InboundEvent(kind=kind, receiver=receiver, decisions=tuple(decisions))


def parse_event(body: bytes) -> InboundEvent | None:
    """Parse one pushed body. Returns `None` for a well-formed event we deliberately ignore."""
    if len(body) > MAX_BODY_BYTES:
        raise InboundEventError("消息推送内容过大")
    stripped = body.strip()
    if not stripped:
        return None
    if stripped.startswith(b"<"):
        return _from_xml(stripped)
    return _from_json(stripped)
