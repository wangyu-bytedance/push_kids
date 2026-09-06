"""Pure notification policy: audiences, dedupe keys, retry backoff and message wording.

This module owns every deterministic decision about *what a reminder says* and *when it may be
retried*. It must stay free of FastAPI, SQLAlchemy, settings and provider clients so the wording
and retry contract can be tested without a database or a WeChat account.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

# WeChat subscribe-message `thing` fields reject long values, so every field the template can
# render is capped here instead of at the provider boundary.
FIELD_LIMIT = 20
RETRY_DELAYS_SECONDS = (60, 300, 900)

# WeChat validates a field by the type prefix of its key and rejects the whole message when one
# value is too long, so each value is clamped to the limit of its own field type.
FIELD_TYPE_LIMITS = {
    "short_thing": 5,
    "phrase": 5,
    "name": 10,
    "amount": 13,
    "thing": 20,
    "const": 20,
    "character_string": 32,
    "number": 32,
    "letter": 32,
    "symbol": 5,
}
# Time-like fields carry a formatted timestamp; truncating one would make it unparseable.
UNCLAMPED_FIELD_TYPES = {"time", "date", "date_time"}


@dataclass(frozen=True)
class NotificationKind:
    type: str
    label: str
    description: str
    # managers_only exists because a join request is an approval task, not family news.
    managers_only: bool
    default_enabled: bool


MEMBER_APPLICATION = NotificationKind(
    type="member_application",
    label="有人申请加入家庭",
    description="家人提交加入申请时通知管理员去审批",
    managers_only=True,
    default_enabled=True,
)
SCHEDULE_REMINDER = NotificationKind(
    type="schedule_reminder",
    label="日程开始前 1 小时",
    description="课程或活动开始前 1 小时提醒家庭成员",
    managers_only=False,
    default_enabled=True,
)
REVIEW_DIGEST = NotificationKind(
    type="review_digest",
    label="每天 19:00 复习提醒",
    description="每天 19:00 告知当前还有哪些知识点没有复习",
    managers_only=False,
    default_enabled=True,
)

KINDS: tuple[NotificationKind, ...] = (MEMBER_APPLICATION, SCHEDULE_REMINDER, REVIEW_DIGEST)
KINDS_BY_TYPE = {kind.type: kind for kind in KINDS}


def kind_for(type_name: str) -> NotificationKind:
    kind = KINDS_BY_TYPE.get(type_name)
    if kind is None:
        raise ValueError(f"unknown notification type: {type_name}")
    return kind


def truncate(text: str, limit: int = FIELD_LIMIT) -> str:
    value = " ".join(text.split())
    if len(value) <= limit:
        return value
    if limit <= 1:
        return value[:limit]
    return value[: limit - 1] + "…"


def field_type(field_key: str) -> str:
    """`short_thing18` -> `short_thing`. WeChat encodes the field type in the key prefix."""
    return field_key.rstrip("0123456789")


def clamp_field(field_key: str, value: str) -> str:
    kind = field_type(field_key)
    if kind in UNCLAMPED_FIELD_TYPES:
        return " ".join(value.split())
    return truncate(value, FIELD_TYPE_LIMITS.get(kind, FIELD_LIMIT))


def local_datetime_text(moment: datetime) -> str:
    """WeChat time format: `2026年9月6日 19:00`. The caller passes an already-local datetime."""
    return f"{moment.year}年{moment.month}月{moment.day}日 {moment:%H:%M}"


def duration_text(minutes: int | None) -> str:
    """Human duration for a `时长` field. Empty when the source has no end time to trust."""
    if minutes is None or minutes <= 0:
        return ""
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return f"{hours}时{rest}分"
    if hours:
        return f"{hours}小时"
    return f"{rest}分钟"


def countdown_text(minutes: int) -> str:
    """Short `距离开始时间` value; WeChat caps `short_thing` at 5 characters."""
    return duration_text(minutes) or "即将开始"


def retry_delay_seconds(attempts: int) -> int:
    """Bounded backoff. `attempts` is the number of attempts already made."""
    index = max(0, attempts - 1)
    if index >= len(RETRY_DELAYS_SECONDS):
        return RETRY_DELAYS_SECONDS[-1]
    return RETRY_DELAYS_SECONDS[index]


def member_application_key(request_id: str, member_id: str) -> str:
    return f"member_application:{request_id}:{member_id}"


def schedule_reminder_key(occurrence_id: str, day: date, member_id: str) -> str:
    """Time is deliberately excluded so editing a schedule updates the same pending row."""
    return f"schedule_reminder:{occurrence_id}:{day.isoformat()}:{member_id}"


def review_digest_key(day: date, member_id: str) -> str:
    return f"review_digest:{day.isoformat()}:{member_id}"


@dataclass(frozen=True)
class NotificationContent:
    """Renderable message. `fields` feed the template; `full_text` is for in-app display."""

    headline: str
    detail: str
    full_text: str
    deep_link: str
    fields: dict[str, str] = field(default_factory=dict)

    def as_payload(self) -> dict[str, object]:
        return {
            "headline": self.headline,
            "detail": self.detail,
            "full_text": self.full_text,
            "deep_link": self.deep_link,
            "fields": dict(self.fields),
        }


def member_application_content(
    relationship_label: str, request_code: str, applied_at_text: str = ""
) -> NotificationContent:
    relationship = relationship_label.strip() or "家人"
    full_text = f"{relationship} 申请加入家庭，申请码 {request_code}，请在小程序里审批"
    fields = {
        "headline": "有家人申请加入家庭",
        "detail": f"申请码 {request_code}，请审批",
        "code": request_code,
        "applicant": relationship,
    }
    # A time field must carry a real timestamp, so an unknown application time is left out rather
    # than filled with prose that WeChat would reject.
    if applied_at_text:
        fields["applied_at"] = applied_at_text
    return NotificationContent(
        headline=truncate("有家人申请加入家庭"),
        detail=truncate(f"关系：{relationship}"),
        full_text=full_text,
        deep_link="/pages/family-requests/index",
        fields=fields,
    )


def schedule_reminder_content(
    child_name: str,
    event_name: str,
    start_time_text: str,
    lead_minutes: int,
    *,
    start_datetime_text: str = "",
    duration_minutes: int | None = None,
    notified_at_text: str = "",
) -> NotificationContent:
    child = child_name.strip() or "孩子"
    name = event_name.strip() or "日程"
    lead_text = f"{lead_minutes} 分钟后开始" if lead_minutes < 60 else "1 小时后开始"
    full_text = f"{child} {start_time_text} {name}，{lead_text}"
    fields = {
        "headline": f"{child} {name}",
        "detail": lead_text,
        "child": child,
        "countdown": countdown_text(lead_minutes),
        # A full local timestamp reads better in the card, but a clock-only source is still valid.
        "time": start_datetime_text or start_time_text,
    }
    if notified_at_text:
        fields["notified_at"] = notified_at_text
    # A template slot must always carry a value, and a missing end time is stated as such instead
    # of being invented or silently dropping the whole reminder.
    fields["duration"] = duration_text(duration_minutes) or "未设置"
    return NotificationContent(
        headline=truncate(f"{child} {start_time_text} {name}"),
        detail=truncate(lead_text),
        full_text=full_text,
        deep_link="/pages/calendar/index",
        fields=fields,
    )


@dataclass(frozen=True)
class ChildReviewLoad:
    child_name: str
    pending_count: int
    subject_names: tuple[str, ...]


def review_digest_content(loads: list[ChildReviewLoad]) -> NotificationContent | None:
    """Return None when nothing is due: an empty reminder is noise, not information."""
    active = [item for item in loads if item.pending_count > 0]
    if not active:
        return None
    total = sum(item.pending_count for item in active)
    parts = []
    for item in active:
        subjects = "、".join(item.subject_names[:3])
        if subjects:
            parts.append(f"{item.child_name} {item.pending_count} 个（{subjects}）")
        else:
            parts.append(f"{item.child_name} {item.pending_count} 个")
    detail_source = "；".join(parts)
    full_text = f"还有 {total} 个知识点没有复习：{detail_source}"
    return NotificationContent(
        headline=truncate(f"还有 {total} 个知识点没复习"),
        detail=truncate(detail_source),
        full_text=full_text,
        deep_link="/pages/today/index",
        fields={
            "headline": truncate(f"还有 {total} 个知识点没复习"),
            "detail": truncate(detail_source),
            "child": truncate(active[0].child_name if len(active) == 1 else "全部孩子"),
        },
    )
