"""FEAT-003：微信订阅事件的验签与解析。

入站事件是外部输入，先证明它签得对、能被理解，再证明它不能夹带东西进来。
"""

from __future__ import annotations

import hashlib
import json

import pytest
from push_kids.notifications.inbound import (
    MAX_BODY_BYTES,
    InboundEventError,
    parse_event,
    verify_signature,
)

TOKEN = "message-push-token"


def _signature(timestamp: str, nonce: str, token: str = TOKEN) -> str:
    return hashlib.sha1("".join(sorted([token, timestamp, nonce])).encode()).hexdigest()


def test_signature_accepts_only_the_configured_token() -> None:
    assert verify_signature(TOKEN, "1700000000", "abc", _signature("1700000000", "abc"))
    # 换个 token 签出来的请求不认
    assert not verify_signature(
        TOKEN, "1700000000", "abc", _signature("1700000000", "abc", "other")
    )
    # 时间戳或随机串被改过也不认
    assert not verify_signature(TOKEN, "1700000001", "abc", _signature("1700000000", "abc"))
    assert not verify_signature(TOKEN, "1700000000", "abd", _signature("1700000000", "abc"))
    # 没配置 token 时永不放行
    assert not verify_signature("", "1700000000", "abc", _signature("1700000000", "abc"))


def test_popup_event_keeps_wechat_own_wording_per_template() -> None:
    body = json.dumps(
        {
            "Event": "subscribe_msg_popup_event",
            "FromUserName": "openid-a",
            "List": [
                {"TemplateId": "tpl-a", "SubscribeStatusString": "accept"},
                {"TemplateId": "tpl-b", "SubscribeStatusString": "reject"},
                {"TemplateId": "tpl-c", "SubscribeStatusString": "ban"},
            ],
        }
    ).encode()
    event = parse_event(body)
    assert event is not None
    assert event.kind == "popup"
    assert event.receiver == "openid-a"
    assert [(item.template_id, item.status) for item in event.decisions] == [
        ("tpl-a", "accept"),
        ("tpl-b", "reject"),
        ("tpl-c", "ban"),
    ]


def test_single_template_and_unknown_status_are_handled_without_guessing() -> None:
    body = json.dumps(
        {
            "Event": "subscribe_msg_change_event",
            "FromUserName": "openid-a",
            # 单模板时 List 是对象而不是数组
            "List": {"TemplateId": "tpl-a", "SubscribeStatusString": "something-new"},
        }
    ).encode()
    event = parse_event(body)
    assert event is not None
    assert event.kind == "change"
    # 不认识的结论不编成 accept/reject，留空让上层按"没有结论"处理
    assert [(item.template_id, item.status) for item in event.decisions] == [("tpl-a", "")]


def test_sent_event_carries_the_message_id_and_error_code() -> None:
    body = json.dumps(
        {
            "Event": "subscribe_msg_sent_event",
            "FromUserName": "openid-a",
            "List": {"TemplateId": "tpl-a", "MsgID": "1234567890", "ErrorCode": 43101},
        }
    ).encode()
    event = parse_event(body)
    assert event is not None
    assert event.kind == "sent"
    assert event.msg_id == "1234567890"
    assert event.error_code == 43101


def test_xml_payload_is_supported_because_the_console_may_be_set_to_xml() -> None:
    body = (
        b"<xml><Event>subscribe_msg_popup_event</Event><FromUserName>openid-a</FromUserName>"
        b"<List><TemplateId>tpl-a</TemplateId>"
        b"<SubscribeStatusString>accept</SubscribeStatusString></List></xml>"
    )
    event = parse_event(body)
    assert event is not None
    assert event.receiver == "openid-a"
    assert [(item.template_id, item.status) for item in event.decisions] == [("tpl-a", "accept")]


def test_hostile_or_unusable_bodies_are_refused_rather_than_guessed() -> None:
    with pytest.raises(InboundEventError):
        parse_event(
            b"<!DOCTYPE x [<!ENTITY a 'b'>]><xml><Event>subscribe_msg_popup_event</Event></xml>"
        )
    with pytest.raises(InboundEventError):
        parse_event(b"{not json")
    with pytest.raises(InboundEventError):
        parse_event(b"<xml><Event>")
    with pytest.raises(InboundEventError):
        parse_event(b"x" * (MAX_BODY_BYTES + 1))


def test_events_we_do_not_handle_are_ignored_instead_of_failing() -> None:
    # 微信还会推其他事件；不认识的一律忽略，避免把无关事件当订阅结论处理
    assert parse_event(json.dumps({"Event": "some_other_event"}).encode()) is None
    assert parse_event(b"") is None
