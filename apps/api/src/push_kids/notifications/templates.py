"""Deployment-owned WeChat template binding.

Template ids and their field names belong to the WeChat console, not to the business database, so
they arrive as one validated JSON environment value. When a type has no binding the channel simply
reports itself unavailable for that type instead of inventing a template.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from push_kids.notifications.domain import KINDS_BY_TYPE, clamp_field

# Semantic keys produced by notifications.domain content builders. A console template may expose
# more slots than the product needs, so the deployment maps only the slots it actually has.
ALLOWED_SEMANTICS = {
    "headline",
    "detail",
    "child",
    "time",
    "code",
    "applicant",
    "applied_at",
    "duration",
    "countdown",
    "notified_at",
}


@dataclass(frozen=True)
class TemplateBinding:
    type: str
    template_id: str
    # WeChat template field key -> semantic key, e.g. {"thing1": "headline", "time2": "time"}.
    fields: dict[str, str]
    # A long-term template may send repeatedly; a one-off template spends one grant per message.
    long_term: bool = False

    def render(self, values: dict[str, str]) -> dict[str, dict[str, str]]:
        """Clamp each field to the limit of its own WeChat type; one long value rejects all."""
        data: dict[str, dict[str, str]] = {}
        for field_key, semantic in self.fields.items():
            value = values.get(semantic)
            if value:
                data[field_key] = {"value": clamp_field(field_key, value)}
        return data

    def missing_fields(self, values: dict[str, str]) -> tuple[str, ...]:
        """WeChat rejects a message whose template has an unfilled slot, so absence is detected
        before the call instead of being discovered as an opaque 47003."""
        return tuple(
            sorted(
                field_key for field_key, semantic in self.fields.items() if not values.get(semantic)
            )
        )


def parse_templates(raw: str) -> dict[str, TemplateBinding]:
    """Parse and validate the template map. Raises ValueError on malformed configuration."""
    text = (raw or "").strip()
    if not text:
        return {}
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"通知模板配置不是合法 JSON：{exc.msg}") from None
    if not isinstance(decoded, dict):
        raise ValueError("通知模板配置必须是对象")
    bindings: dict[str, TemplateBinding] = {}
    for type_name, entry in decoded.items():
        if type_name not in KINDS_BY_TYPE:
            raise ValueError(f"通知模板配置包含未知类型：{type_name}")
        if not isinstance(entry, dict):
            raise ValueError(f"通知模板 {type_name} 配置必须是对象")
        template_id = str(entry.get("template_id") or "").strip()
        if not template_id:
            raise ValueError(f"通知模板 {type_name} 缺少 template_id")
        raw_fields = entry.get("fields") or {}
        if not isinstance(raw_fields, dict) or not raw_fields:
            raise ValueError(f"通知模板 {type_name} 缺少字段映射")
        fields: dict[str, str] = {}
        for field_key, semantic in raw_fields.items():
            if semantic not in ALLOWED_SEMANTICS:
                raise ValueError(f"通知模板 {type_name} 字段 {field_key} 使用了未知语义 {semantic}")
            fields[str(field_key)] = str(semantic)
        bindings[type_name] = TemplateBinding(
            type=type_name,
            template_id=template_id,
            fields=fields,
            long_term=bool(entry.get("long_term", False)),
        )
    return bindings
