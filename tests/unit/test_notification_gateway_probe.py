"""Privacy and isolation boundaries for the explicitly approved cloud diagnostic."""

from __future__ import annotations

import io
import json
import urllib.error
from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.diagnostics import notification_gateway_probe as probe


class Response(io.BytesIO):
    def getcode(self) -> int:
        return 200


def test_probe_has_no_recipient_template_or_business_payload() -> None:
    opener = Mock(return_value=Response(b'{"errcode":40003,"errmsg":"private-response"}'))
    result = probe.probe_once(opener)
    request = opener.call_args.args[0]
    assert request.full_url == "http://api.weixin.qq.com/cgi-bin/message/subscribe/send"
    assert request.get_method() == "POST"
    assert request.data == b"{}"
    assert request.header_items() == [("Content-type", "application/json")]
    assert opener.call_args.kwargs == {"timeout": 5.0}
    opener.assert_called_once()
    assert result.platform_errcode == 40003
    assert "private-response" not in json.dumps(asdict(result))


def test_http_error_preserves_only_numeric_codes_and_safe_reason() -> None:
    body = Response(b'{"errcode":85107,"errmsg":"private-response","access_token":"private-token"}')
    error = urllib.error.HTTPError(
        "http://private-url", 502, "private-reason", {"private-header": "private-token"}, body
    )
    opener = Mock(side_effect=error)
    result = probe.probe_once(opener)
    assert asdict(result) == {
        "http_status": 502,
        "platform_errcode": 85107,
        "exception_type": "HTTPError",
        "reason": "url_not_allowlisted",
        "protocol": "http",
        "response_format": "json_object",
        "error_codes": ({"source": "errcode", "value": 85107},),
        "category": "allowlist_rejected",
    }
    assert "private-" not in json.dumps(asdict(result))
    assert body.closed
    opener.assert_called_once()


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        (b"private-html", "non_json_response"),
        (b"\xff", "non_json_response"),
        (b"[]", "invalid_response_shape"),
        (b'{"errcode":"private-secret"}', "http_error"),
        (b'{"errcode":true}', "http_error"),
        (b'{"errcode":0}', "http_error"),
    ],
)
def test_untrusted_error_content_never_appears_in_result(body: bytes, reason: str) -> None:
    error = urllib.error.HTTPError("http://private-url", 503, "private-reason", {}, Response(body))
    result = probe.probe_once(Mock(side_effect=error))
    assert result.reason == reason
    assert result.http_status == 503
    assert result.platform_errcode in {None, 0}
    assert "private-" not in json.dumps(asdict(result))


def test_response_read_is_bounded_and_closed() -> None:
    response = Mock()
    response.getcode.return_value = 200
    response.read.return_value = b"x" * 8192
    result = probe.probe_once(Mock(return_value=response))
    response.read.assert_called_once_with(8192)
    response.close.assert_called_once()
    assert result.reason == "response_limit"


@pytest.mark.parametrize("error", [TimeoutError("private-secret"), OSError("private-secret")])
def test_response_read_failure_is_safe(error: Exception) -> None:
    response = Mock()
    response.getcode.return_value = 200
    response.read.side_effect = error
    result = probe.probe_once(Mock(return_value=response))
    assert result.reason == "response_read_failed"
    assert "private-" not in json.dumps(asdict(result))
    response.close.assert_called_once()


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.URLError("private-secret"),
        TimeoutError("private-secret"),
        OSError("private-secret"),
    ],
)
def test_transport_failure_is_not_retried(error: Exception) -> None:
    opener = Mock(side_effect=error)
    result = probe.probe_once(opener)
    assert result.reason == "transport_unavailable"
    assert result.exception_type == type(error).__name__
    assert "private-" not in json.dumps(asdict(result))
    opener.assert_called_once()


def test_redirects_cannot_change_the_fixed_destination() -> None:
    assert probe.NoRedirect().redirect_request(None, None, 302, "", {}, "http://other-host") is None


@pytest.mark.parametrize("path", ["/health/live", "/health/ready", "/private-input?secret=x"])
def test_health_requests_are_static_and_never_probe(
    path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    outbound = Mock(side_effect=AssertionError("No outbound call from a health request"))
    monkeypatch.setattr(probe, "probe_once", outbound)
    handler = object.__new__(probe.HealthHandler)
    handler.path = path
    handler.wfile = io.BytesIO()
    handler.send_response = Mock()
    handler.send_header = Mock()
    handler.end_headers = Mock()
    for _ in range(3):
        handler.do_GET()
    healthy = path.startswith("/health/")
    assert handler.send_response.call_args.args == (200 if healthy else 404,)
    assert b"private-" not in handler.wfile.getvalue()
    outbound.assert_not_called()


@pytest.mark.parametrize("unexpected", [False, True])
def test_main_runs_exactly_once_and_never_logs_untrusted_exception(
    unexpected: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    server = Mock()
    server.serve_forever.side_effect = SystemExit(0)
    server_class = Mock(return_value=server)
    outbound = Mock(
        return_value=probe.ProbeResult(
            502, 85107, "HTTPError", "url_not_allowlisted", category="allowlist_rejected"
        ),
        side_effect=RuntimeError("private-secret") if unexpected else None,
    )
    monkeypatch.setattr(probe, "ThreadingHTTPServer", server_class)
    monkeypatch.setattr(probe, "probe_once", outbound)
    monkeypatch.setattr(probe, "signal", SimpleNamespace(SIGTERM=15, signal=Mock()))
    with pytest.raises(SystemExit):
        probe.main()
    outbound.assert_called_once_with()
    server_class.assert_called_once_with(("0.0.0.0", 8000), probe.HealthHandler)
    server.server_close.assert_called_once()
    stdout = capsys.readouterr().out
    assert stdout.count(probe.LOG_PREFIX) == 1
    assert "private-" not in stdout
    result = json.loads(stdout.removeprefix(probe.LOG_PREFIX))
    assert set(result) == {
        "http_status",
        "platform_errcode",
        "exception_type",
        "reason",
        "protocol",
        "response_format",
        "error_codes",
        "category",
    }


def test_sigterm_exits_cleanly() -> None:
    with pytest.raises(SystemExit) as error:
        probe._terminate(15, None)
    assert error.value.code == 0


def http_error(body: bytes, status: int = 502) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "http://private-url", status, "private-reason", {}, Response(body)
    )


def test_extracts_only_whitelisted_numeric_positions() -> None:
    payload = {
        "errcode": 0,
        "code": -2,
        "ret": -(2**31),
        "error_code": 2**31 - 1,
        "base_resp": {"ret": 17, "request_id": 123},
        "error": {"code": 18, "private-field": 19},
        "openid": 999,
        "private-field": 20,
        "arbitrary": {"code": 21},
    }
    result = probe.probe_once(Mock(side_effect=http_error(json.dumps(payload).encode())))
    assert [(item.source, item.value) for item in result.error_codes] == [
        ("errcode", 0),
        ("code", -2),
        ("ret", -(2**31)),
        ("error_code", 2**31 - 1),
        ("base_resp.ret", 17),
        ("error.code", 18),
    ]
    assert "private-field" not in json.dumps(asdict(result))


@pytest.mark.parametrize("value", [True, False, "17", None, 1.5, 2**31, -(2**31) - 1, {}, []])
def test_rejects_non_integer_or_out_of_range_codes(value: object) -> None:
    payload = {"errcode": value, "code": value, "base_resp": {"ret": value}}
    result = probe.probe_once(Mock(side_effect=http_error(json.dumps(payload).encode())))
    assert result.error_codes == () and result.platform_errcode is None


@pytest.mark.parametrize(
    ("payload", "category"),
    [
        ({"errcode": 85107}, "allowlist_rejected"),
        ({"errcode": -1}, "platform_busy"),
        ({"message": "URL not in whitelist"}, "allowlist_rejected"),
        ({"base_resp": {"err_msg": "invalid access_token"}}, "token_rejected"),
        ({"error": {"message": "access_token is missing"}}, "token_rejected"),
        ({"errmsg": "access_token is invalid or not latest"}, "token_rejected"),
        (
            {"error": "dial tcp private-address:80: connect: connection refused"},
            "upstream_connect_failed",
        ),
        (
            {
                "msg": (
                    "connect() failed (111: Connection refused) "
                    "while connecting to upstream, private-token"
                )
            },
            "upstream_connect_failed",
        ),
        ({"error_msg": "upstream request timeout"}, "upstream_timeout"),
        (
            {"message": "upstream timed out (110: Connection timed out) while reading upstream"},
            "upstream_timeout",
        ),
        ({"errmsg": "system busy"}, "platform_busy"),
        ({"ret": -1, "errmsg": "unknown private-token"}, "unclassified"),
        ({"errmsg": "user text mentions invalid access_token and private-token"}, "unclassified"),
        ({"arbitrary": {"message": "invalid access_token"}}, "unclassified"),
        ({"errmsg": "invalid access_token", "message": "system busy"}, "unclassified"),
    ],
)
def test_known_error_formats_and_ambiguous_or_unknown_text(
    payload: dict[str, object], category: str
) -> None:
    result = probe.probe_once(Mock(side_effect=http_error(json.dumps(payload).encode())))
    assert result.category == category
    assert "private-" not in json.dumps(asdict(result))


@pytest.mark.parametrize(
    ("body", "shape", "category"),
    [
        (b"", "empty", "unclassified"),
        (b"   ", "empty", "unclassified"),
        (b"[]", "json_array", "unclassified"),
        (b"42", "non_json", "unclassified"),
        (b"\xffprivate-token", "non_json", "unclassified"),
        (b"invalid access_token", "non_json", "token_rejected"),
        (b"private-token", "non_json", "unclassified"),
    ],
)
def test_response_shapes_never_echo_error_content(body: bytes, shape: str, category: str) -> None:
    result = probe.probe_once(Mock(side_effect=http_error(body)))
    assert result.response_format == shape and result.category == category
    assert "private-" not in json.dumps(asdict(result))


@pytest.mark.parametrize(
    ("status", "body", "calls"),
    [
        (502, b'{"code": -500}', 2),
        (502, b'{"message": "private-token"}', 2),
        (502, b'{"errcode": 85107}', 1),
        (502, b'{"message": "invalid access_token"}', 1),
        (503, b"{}", 1),
        (403, b"{}", 1),
    ],
)
def test_only_unclassified_http_502_gets_one_fixed_https_comparison(
    status: int, body: bytes, calls: int
) -> None:
    opener = Mock(side_effect=[http_error(body, status), Response(b'{"errcode":40003}')])
    results = probe.probe_comparison(opener)
    assert opener.call_count == calls == len(results)
    for index, call in enumerate(opener.call_args_list):
        request = call.args[0]
        assert request.full_url == (probe.TARGET if index == 0 else probe.HTTPS_TARGET)
        assert request.data == b"{}" and request.get_method() == "POST"
        assert call.kwargs == {"timeout": 5.0}
    assert [result.protocol for result in results] == ["http", "https"][:calls]


def test_success_or_transport_failure_never_gets_https() -> None:
    for first in [Response(b'{"errcode":40003}'), urllib.error.URLError("private-token")]:
        opener = Mock(side_effect=[first])
        assert len(probe.probe_comparison(opener)) == 1
        opener.assert_called_once()


def test_https_unexpected_failure_preserves_first_result_without_retry() -> None:
    opener = Mock(side_effect=[http_error(b'{"code": -500}'), RuntimeError("private-token")])
    first, second = probe.probe_comparison(opener)
    assert first.http_status == 502 and first.error_codes == (probe.SafeCode("code", -500),)
    assert second.protocol == "https" and second.exception_type == "UnexpectedError"
    assert "private-" not in json.dumps([asdict(first), asdict(second)])
    assert opener.call_count == 2


def test_unsupported_protocol_cannot_change_destination() -> None:
    opener = Mock()
    with pytest.raises(ValueError, match="unsupported_probe_protocol"):
        probe._probe_protocol("http://other-host", opener)
    opener.assert_not_called()


def test_main_outputs_only_safe_fields_for_both_attempts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    server = Mock()
    server.serve_forever.side_effect = SystemExit(0)
    monkeypatch.setattr(probe, "ThreadingHTTPServer", Mock(return_value=server))
    monkeypatch.setattr(probe, "signal", SimpleNamespace(SIGTERM=15, signal=Mock()))
    opener = Mock(
        side_effect=[
            http_error(b'{"ret":-500,"errmsg":"private-token","openid":"private-child"}'),
            http_error(b'{"base_resp":{"ret":17,"err_msg":"private-receiver"}}', 403),
        ]
    )
    monkeypatch.setattr(
        probe.urllib.request, "build_opener", Mock(return_value=SimpleNamespace(open=opener))
    )
    with pytest.raises(SystemExit):
        probe.main()
    output = capsys.readouterr().out
    assert "private-" not in output and output.count(probe.LOG_PREFIX) == 2
    results = [json.loads(line.removeprefix(probe.LOG_PREFIX)) for line in output.splitlines()]
    assert [result["protocol"] for result in results] == ["http", "https"]
    assert results[0]["error_codes"] == [{"source": "ret", "value": -500}]
    assert results[1]["error_codes"] == [{"source": "base_resp.ret", "value": 17}]
    assert opener.call_count == 2
