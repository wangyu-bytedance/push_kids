"""Approved bounded, receiver-free probe for an isolated, zero-traffic cloud version.

No business module, credential, recipient or payload is loaded. Run only under
OPS-SPEC-20261017-NOTIFICATION-HTTP-DIAGNOSIS-03; deterministic tests replace the opener.
"""

from __future__ import annotations

import json
import re
import signal
import urllib.error
import urllib.request
from contextlib import closing
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

TARGET = "http://api.weixin.qq.com/cgi-bin/message/subscribe/send"
HTTPS_TARGET = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"
TIMEOUT_SECONDS = 5.0
MAX_RESPONSE_BYTES = 8192
LOG_PREFIX = "notification_gateway_probe "


@dataclass(frozen=True)
class SafeCode:
    source: str
    value: int


@dataclass(frozen=True)
class ProbeResult:
    http_status: int | None
    platform_errcode: int | None
    exception_type: str | None
    reason: str
    protocol: str = "http"
    response_format: str = "empty"
    error_codes: tuple[SafeCode, ...] = ()
    category: str = "unclassified"


CODE_PATHS = (
    ("errcode",),
    ("code",),
    ("ret",),
    ("error_code",),
    ("base_resp", "ret"),
    ("error", "code"),
)
TEXT_PATHS = (
    ("errmsg",),
    ("message",),
    ("msg",),
    ("error",),
    ("error_msg",),
    ("base_resp", "err_msg"),
    ("error", "message"),
)
# Match known error formats, never general keywords in arbitrary echoed content.
ERROR_FORMATS = (
    ("allowlist_rejected", r"url (?:is )?not in (?:the )?(?:white|allow)list[.!]?"),
    ("token_rejected", r"invalid (?:access_token|cloudbase_access_token|credential)[.!]?"),
    ("token_rejected", r"(?:access_token|cloudbase_access_token) (?:is )?missing[.!]?"),
    ("token_rejected", r"access_token is invalid or not latest[.!]?"),
    (
        "upstream_connect_failed",
        r"connect\(\) failed \(111: connection refused\) "
        r"while connecting to upstream(?:, [^\r\n]*)?",
    ),
    ("upstream_connect_failed", r"dial tcp [^\r\n]{1,200}: connect: connection refused"),
    ("upstream_timeout", r"upstream request timeout[.!]?"),
    ("upstream_timeout", r"upstream timed out(?: \([^\r\n]{1,100}\))? while [^\r\n]{1,200}"),
    ("platform_busy", r"system (?:is )?busy[.!]?"),
)


def _at(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = payload
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _codes(payload: dict[str, Any]) -> tuple[SafeCode, ...]:
    return tuple(
        SafeCode(".".join(path), value)
        for path in CODE_PATHS
        if type(value := _at(payload, path)) is int and -(2**31) <= value < 2**31
    )


def _category(code: int | None, texts: list[str]) -> str:
    if code == 85107:
        return "allowlist_rejected"
    if code == -1:
        return "platform_busy"
    matched = {
        category
        for text in texts
        for category, pattern in ERROR_FORMATS
        if re.fullmatch(pattern, text.strip(), re.IGNORECASE)
    }
    return matched.pop() if len(matched) == 1 else "unclassified"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _result(response: Any, status: int, exception_type: str | None, protocol: str) -> ProbeResult:
    try:
        raw = response.read(MAX_RESPONSE_BYTES)
    except (OSError, TimeoutError):
        return ProbeResult(status, None, exception_type, "response_read_failed", protocol)
    if len(raw) >= MAX_RESPONSE_BYTES:
        return ProbeResult(status, None, exception_type, "response_limit", protocol, "non_json")
    if not raw.strip():
        reason = "http_error" if status >= 300 else "no_rejection_code"
        return ProbeResult(status, None, exception_type, reason, protocol)
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeError):
        return ProbeResult(
            status,
            None,
            exception_type,
            "non_json_response",
            protocol,
            "non_json",
            category=_category(None, [raw.decode("utf-8", errors="replace")]),
        )
    if not isinstance(payload, dict):
        shape = "json_array" if isinstance(payload, list) else "non_json"
        return ProbeResult(status, None, exception_type, "invalid_response_shape", protocol, shape)
    codes = _codes(payload)
    code = next((item.value for item in codes if item.source == "errcode"), None)
    if code == 85107:
        reason = "url_not_allowlisted"
    elif any(item.value != 0 for item in codes):
        reason = "platform_rejected"
    elif status >= 300:
        reason = "http_error"
    else:
        reason = "no_rejection_code"
    texts = [value for path in TEXT_PATHS if isinstance(value := _at(payload, path), str)]
    return ProbeResult(
        status, code, exception_type, reason, protocol, "json_object", codes, _category(code, texts)
    )


def probe_once(opener: Any = None) -> ProbeResult:
    """One fixed empty request: impossible to identify or notify any recipient."""
    return _probe_protocol("http", opener)


def _probe_protocol(protocol: str, opener: Any = None) -> ProbeResult:
    if protocol not in {"http", "https"}:
        raise ValueError("unsupported_probe_protocol")
    request = urllib.request.Request(
        TARGET if protocol == "http" else HTTPS_TARGET,
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    if opener is None:
        opener = urllib.request.build_opener(NoRedirect()).open
    try:
        with closing(opener(request, timeout=TIMEOUT_SECONDS)) as response:
            return _result(response, int(response.getcode()), None, protocol)
    except urllib.error.HTTPError as exc:
        with closing(exc):
            return _result(exc, int(exc.code), "HTTPError", protocol)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        kind = (
            "URLError"
            if isinstance(exc, urllib.error.URLError)
            else "TimeoutError"
            if isinstance(exc, TimeoutError)
            else "OSError"
        )
        return ProbeResult(None, None, kind, "transport_unavailable", protocol)


def probe_comparison(opener: Any = None) -> list[ProbeResult]:
    first = probe_once() if opener is None else probe_once(opener)
    results = [first]
    if first.http_status == 502 and first.category == "unclassified":
        try:
            second = _probe_protocol("https", opener)
        except Exception:
            second = ProbeResult(None, None, "UnexpectedError", "diagnostic_failed", "https")
        results.append(second)
    return results


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        healthy = self.path in {"/health/live", "/health/ready"}
        body = b'{"status":"ok"}' if healthy else b'{"status":"not_found"}'
        self.send_response(200 if healthy else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: Any) -> None:
        # No client addresses, headers, query strings or reflected input in logs.
        pass


def _terminate(signum: int, frame: Any) -> None:
    raise SystemExit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, _terminate)
    server = ThreadingHTTPServer(("0.0.0.0", 8000), HealthHandler)
    try:
        try:
            results = probe_comparison()
        except Exception:
            # Never let an unexpected error print an untrusted response or credential.
            results = [ProbeResult(None, None, "UnexpectedError", "diagnostic_failed")]
        for result in results:
            print(LOG_PREFIX + json.dumps(asdict(result), sort_keys=True), flush=True)
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
