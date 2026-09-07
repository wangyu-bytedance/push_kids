"""FEAT-003：微信订阅事件回调把云端状态与家长的真实选择对齐。

回调不带家庭身份，只带 OpenID 与模板 ID，所以这里同时验证两件事：
状态确实被同步了，以及除了已存的 active destination 之外它什么都不信。
"""

from __future__ import annotations

import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from push_kids.persistence.models import (
    DeliveryState,
    NotificationDelivery,
    NotificationDestination,
    NotificationSubscription,
    SubscriptionStatus,
)
from push_kids.platform.time import utcnow

from tests.conftest import WECHAT_MESSAGE_TOKEN

EVENTS = "/api/v1/notifications/wechat/events"
TIMESTAMP = "1700000000"
NONCE = "nonce-a"


@pytest.fixture
def app(notification_event_app):
    return notification_event_app


def _actor(name: str) -> dict[str, str]:
    return {"X-Debug-Actor": name}


def _signed(token: str = WECHAT_MESSAGE_TOKEN) -> dict[str, str]:
    signature = hashlib.sha1("".join(sorted([token, TIMESTAMP, NONCE])).encode()).hexdigest()
    return {"signature": signature, "timestamp": TIMESTAMP, "nonce": NONCE}


def _create_family(client: TestClient) -> None:
    created = client.post(
        "/api/v1/families",
        headers={**_actor("parent-a"), "Idempotency-Key": "event-family-001"},
        json={
            "display_name": "小雨的家",
            "relationship_label": "妈妈",
            "child": {"name": "小雨", "grade": "小学二年级", "daily_budget_minutes": 15},
        },
    )
    assert created.status_code == 201, created.text


def _grant(client: TestClient, types: list[str], times: int = 1) -> None:
    for _ in range(times):
        response = client.post(
            "/api/v1/notifications/subscriptions",
            headers=_actor("parent-a"),
            json={
                "results": [
                    {"type": item, "accepted": True, "decision": "accept"} for item in types
                ]
            },
        )
        assert response.status_code == 200, response.text


def _receiver(app) -> str:
    """回调用的接收标识：库里只有密文，测试按运行时同一把钥匙解出来。"""
    cipher = app.state.notification_channel.cipher
    with app.state.database.session_factory() as db:
        row = db.query(NotificationDestination).one()
        return cipher.decrypt(str(row.ciphertext))


def _subscription(app, type_name: str) -> NotificationSubscription:
    with app.state.database.session_factory() as db:
        return (
            db.query(NotificationSubscription)
            .filter(NotificationSubscription.type == type_name)
            .one()
        )


def _post_event(client: TestClient, payload: dict) -> None:
    response = client.post(EVENTS, params=_signed(), json=payload)
    assert response.status_code == 200, response.text
    # 微信只认 success；回不了这个字符串它就会一直重推
    assert response.text == "success"


def test_url_verification_echoes_only_a_correctly_signed_challenge(client: TestClient) -> None:
    ok = client.get(EVENTS, params={**_signed(), "echostr": "challenge-1"})
    assert ok.status_code == 200
    assert ok.text == "challenge-1"

    forged = client.get(EVENTS, params={**_signed(token="wrong-token"), "echostr": "challenge-1"})
    assert forged.status_code == 403


def test_callback_is_absent_when_no_message_token_is_configured(notification_app) -> None:
    with TestClient(notification_app) as client:
        response = client.get(EVENTS, params={**_signed(), "echostr": "challenge-1"})
        assert response.status_code == 404
        posted = client.post(EVENTS, params=_signed(), json={"Event": "subscribe_msg_popup_event"})
        assert posted.status_code == 404


def test_refusing_inside_wechat_clears_stored_quota(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=3)
    assert _subscription(app, "review_digest").remaining_quota == 3

    _post_event(
        client,
        {
            "Event": "subscribe_msg_change_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "reject"},
        },
    )

    row = _subscription(app, "review_digest")
    # 在服务通知里关掉是长期拒收：攒下的额度不能再花，页面也必须显示成"已拒收"
    assert row.status == SubscriptionStatus.rejected.value
    assert row.remaining_quota == 0


def test_declining_one_dialog_does_not_destroy_earlier_grants(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=2)

    _post_event(
        client,
        {
            "Event": "subscribe_msg_popup_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "reject"},
        },
    )

    row = _subscription(app, "review_digest")
    # 这次弹窗没同意 ≠ 不要提醒了；已经存下的两条还得能发
    assert row.status == SubscriptionStatus.accepted.value
    assert row.remaining_quota == 2


def test_a_ban_from_the_dialog_stops_spending_grants(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=2)

    _post_event(
        client,
        {
            "Event": "subscribe_msg_popup_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "ban"},
        },
    )

    row = _subscription(app, "review_digest")
    assert row.status == SubscriptionStatus.rejected.value
    assert row.remaining_quota == 0


def test_an_accept_event_does_not_hand_out_a_second_reminder(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"])
    assert _subscription(app, "review_digest").remaining_quota == 1

    _post_event(
        client,
        {
            "Event": "subscribe_msg_popup_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "accept"},
        },
    )

    # 同一次同意已经由小程序回传记过账，事件不能再加一条额度
    assert _subscription(app, "review_digest").remaining_quota == 1


def test_an_unknown_receiver_changes_nothing(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=2)

    _post_event(
        client,
        {
            "Event": "subscribe_msg_change_event",
            "FromUserName": "openid-of-somebody-else",
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "reject"},
        },
    )

    row = _subscription(app, "review_digest")
    assert row.status == SubscriptionStatus.accepted.value
    assert row.remaining_quota == 2


def test_an_unknown_template_id_changes_nothing(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=2)

    _post_event(
        client,
        {
            "Event": "subscribe_msg_change_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-not-ours", "SubscribeStatusString": "reject"},
        },
    )

    assert _subscription(app, "review_digest").remaining_quota == 2


def test_a_failed_delivery_event_corrects_an_optimistic_sent_row(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"])
    with app.state.database.session_factory() as db:
        destination = db.query(NotificationDestination).one()
        db.add(
            NotificationDelivery(
                family_id=str(destination.family_id),
                member_id=str(destination.member_id),
                type="review_digest",
                dedupe_key="review_digest:2026-09-07",
                scheduled_at=utcnow(),
                sent_at=utcnow(),
                state=DeliveryState.sent.value,
                result_code="ok",
                provider_msg_id="9999999999",
                payload_json=json.dumps({"headline": "今天还有 2 项复习"}),
            )
        )
        db.commit()

    _post_event(
        client,
        {
            "Event": "subscribe_msg_sent_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "MsgID": "9999999999", "ErrorCode": 43101},
        },
    )

    with app.state.database.session_factory() as db:
        row = db.query(NotificationDelivery).one()
        # 微信事后说没送到，就不能继续显示成已发送
        assert row.state == DeliveryState.failed.value
        assert row.result_code == "wechat_43101"
        assert row.sent_at is None

    history = client.get("/api/v1/notifications/deliveries", headers=_actor("parent-a"))
    assert history.status_code == 200, history.text
    assert history.json()[0]["state"] == "failed"


def test_a_successful_delivery_event_leaves_the_row_alone(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"])
    with app.state.database.session_factory() as db:
        destination = db.query(NotificationDestination).one()
        db.add(
            NotificationDelivery(
                family_id=str(destination.family_id),
                member_id=str(destination.member_id),
                type="review_digest",
                dedupe_key="review_digest:2026-09-08",
                scheduled_at=utcnow(),
                sent_at=utcnow(),
                state=DeliveryState.sent.value,
                result_code="ok",
                provider_msg_id="8888888888",
                payload_json="{}",
            )
        )
        db.commit()

    _post_event(
        client,
        {
            "Event": "subscribe_msg_sent_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "MsgID": "8888888888", "ErrorCode": 0},
        },
    )

    with app.state.database.session_factory() as db:
        assert db.query(NotificationDelivery).one().state == DeliveryState.sent.value


def test_an_unreadable_body_is_rejected_without_touching_state(client: TestClient) -> None:
    _create_family(client)
    broken = client.post(EVENTS, params=_signed(), content=b"{not json")
    assert broken.status_code == 400
    oversized = client.post(EVENTS, params=_signed(), content=b"x" * (17 * 1024))
    assert oversized.status_code == 400


def test_a_forged_event_cannot_change_anything(client: TestClient, app) -> None:
    _create_family(client)
    _grant(client, ["review_digest"], times=2)

    forged = client.post(
        EVENTS,
        params=_signed(token="wrong-token"),
        json={
            "Event": "subscribe_msg_change_event",
            "FromUserName": _receiver(app),
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "reject"},
        },
    )

    assert forged.status_code == 403
    assert _subscription(app, "review_digest").remaining_quota == 2


def test_a_legacy_destination_without_the_index_is_still_matched(client: TestClient, app) -> None:
    """回调上线前写入的接收标识没有索引列，必须仍然能被匹配并就地补齐。"""
    _create_family(client)
    _grant(client, ["review_digest"], times=2)
    receiver = _receiver(app)
    with app.state.database.session_factory() as db:
        row = db.query(NotificationDestination).one()
        row.receiver_hmac = None
        db.commit()

    _post_event(
        client,
        {
            "Event": "subscribe_msg_change_event",
            "FromUserName": receiver,
            "List": {"TemplateId": "tpl-digest", "SubscribeStatusString": "reject"},
        },
    )

    assert _subscription(app, "review_digest").remaining_quota == 0
    with app.state.database.session_factory() as db:
        assert db.query(NotificationDestination).one().receiver_hmac
