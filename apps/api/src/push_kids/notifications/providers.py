"""Notification channel providers.

`build_sender` never raises for a missing channel: an unconfigured deployment gets a sender that
honestly reports itself unavailable, so the product can still show accurate in-app state instead of
claiming that WeChat reminders are switched on.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Literal, Protocol

from push_kids.notifications.templates import TemplateBinding
from push_kids.platform.config import Settings

logger = logging.getLogger("push_kids")

WECHAT_SEND_URL = "http://api.weixin.qq.com/cgi-bin/message/subscribe/send"
# WeChat error codes that will never succeed on retry for the same message.
PERMANENT_ERRORS = {
    40003: "invalid_receiver",
    43101: "user_refused",
    47003: "template_param_invalid",
    41030: "invalid_page",
}
# Transient platform conditions; the outbox retries these with bounded backoff.
RETRYABLE_ERRORS = {-1: "platform_busy", 45009: "rate_limited", 45011: "rate_limited"}

SendStatus = Literal["sent", "retry", "permanent"]


@dataclass(frozen=True)
class SendOutcome:
    status: SendStatus
    code: str


class NotificationSender(Protocol):
    @property
    def available(self) -> bool: ...

    @property
    def unavailable_reason(self) -> str: ...

    def send(
        self, *, receiver: str, binding: TemplateBinding, values: dict[str, str], deep_link: str
    ) -> SendOutcome: ...


class UnavailableSender:
    """Used when no external channel is configured. Deliveries are skipped, never faked."""

    def __init__(self, reason: str) -> None:
        self._reason = reason

    @property
    def available(self) -> bool:
        return False

    @property
    def unavailable_reason(self) -> str:
        return self._reason

    def send(
        self, *, receiver: str, binding: TemplateBinding, values: dict[str, str], deep_link: str
    ) -> SendOutcome:
        return SendOutcome("permanent", "channel_unavailable")


class RecordingSender:
    """Deterministic sender for tests and local runs: records calls without leaving the process."""

    def __init__(self) -> None:
        self.sent: list[dict[str, object]] = []

    @property
    def available(self) -> bool:
        return True

    @property
    def unavailable_reason(self) -> str:
        return ""

    def send(
        self, *, receiver: str, binding: TemplateBinding, values: dict[str, str], deep_link: str
    ) -> SendOutcome:
        self.sent.append(
            {
                "receiver": receiver,
                "type": binding.type,
                "template_id": binding.template_id,
                "data": binding.render(values),
                "deep_link": deep_link,
            }
        )
        return SendOutcome("sent", "ok")


class WeChatSubscribeSender:
    """Sends through the Cloud Hosting WeChat gateway, which injects platform credentials.

    Inside a WeChat Cloud Hosting container `api.weixin.qq.com` is reachable without an access
    token, so no AppSecret is stored or transmitted by this service.
    """

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self._timeout = timeout_seconds

    @property
    def available(self) -> bool:
        return True

    @property
    def unavailable_reason(self) -> str:
        return ""

    def send(
        self, *, receiver: str, binding: TemplateBinding, values: dict[str, str], deep_link: str
    ) -> SendOutcome:
        body = {
            "touser": receiver,
            "template_id": binding.template_id,
            "page": deep_link.lstrip("/"),
            "data": binding.render(values),
            "miniprogram_state": "formal",
            "lang": "zh_CN",
        }
        request = urllib.request.Request(
            WECHAT_SEND_URL,
            data=json.dumps(body, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                decoded = json.loads(response.read().decode() or "{}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            # The exception type is safe to log; the payload and receiver are not.
            logger.warning("notification_send_transport_error type=%s", type(exc).__name__)
            return SendOutcome("retry", "transport_error")
        code = int(decoded.get("errcode", 0) or 0)
        if code == 0:
            return SendOutcome("sent", "ok")
        if code in PERMANENT_ERRORS:
            return SendOutcome("permanent", PERMANENT_ERRORS[code])
        if code in RETRYABLE_ERRORS:
            return SendOutcome("retry", RETRYABLE_ERRORS[code])
        logger.warning("notification_send_rejected errcode=%s", code)
        return SendOutcome("permanent", f"wechat_{code}")


def build_sender(settings: Settings) -> NotificationSender:
    channel = settings.notification_channel
    if channel == "disabled":
        return UnavailableSender("当前部署未开启外部通知通道")
    if channel == "recording":
        if settings.env not in {"test", "e2e", "development"}:
            raise ValueError("recording 通知通道只能在测试或本地环境使用")
        return RecordingSender()
    if len(settings.notification_secret_value) < 32:
        return UnavailableSender("缺少通知加密密钥，无法安全保存接收标识")
    return WeChatSubscribeSender()
