"""FEAT-003：通知策略与配置解析的纯函数行为。

这些规则决定"提醒说什么、什么时候能重试、什么算同一条消息"，必须能脱离数据库和微信账号验证。
"""

from __future__ import annotations

from datetime import date

import pytest
from push_kids.notifications.destinations import DestinationCipher, DestinationCipherError
from push_kids.notifications.domain import (
    FIELD_LIMIT,
    KINDS,
    ChildReviewLoad,
    kind_for,
    member_application_content,
    member_application_key,
    retry_delay_seconds,
    review_digest_content,
    review_digest_key,
    schedule_reminder_content,
    schedule_reminder_key,
    truncate,
)
from push_kids.notifications.providers import UnavailableSender, build_sender
from push_kids.notifications.templates import parse_templates
from push_kids.platform.config import Settings


def test_reminder_types_are_closed_and_named() -> None:
    assert [kind.type for kind in KINDS] == [
        "member_application",
        "schedule_reminder",
        "review_digest",
    ]
    # 审批是管理员的任务，不是家庭新闻。
    assert kind_for("member_application").managers_only is True
    assert kind_for("schedule_reminder").managers_only is False
    assert kind_for("review_digest").managers_only is False
    with pytest.raises(ValueError):
        kind_for("marketing_push")


def test_every_rendered_field_fits_the_wechat_limit() -> None:
    long_name = "很长很长很长很长很长很长很长的课程名称"
    contents = [
        member_application_content("外公外婆一起提交的申请", "AB12CD34"),
        schedule_reminder_content("小雨", long_name, "17:30", 60),
        review_digest_content(
            [
                ChildReviewLoad("小雨", 3, ("数学", "语文", "英语")),
                ChildReviewLoad("小满", 2, ("数学",)),
            ]
        ),
    ]
    for content in contents:
        assert content is not None
        for value in content.fields.values():
            assert len(value) <= FIELD_LIMIT, value
        assert content.deep_link.startswith("/pages/")
    assert truncate("一二三四五六七八九十一二三四五六七八九十一") == (
        "一二三四五六七八九十一二三四五六七八九" + "…"
    )


def test_schedule_reminder_says_which_child_when_and_what() -> None:
    content = schedule_reminder_content("小雨", "钢琴课", "17:30", 60)
    assert content.fields["child"] == "小雨"
    assert content.fields["time"] == "17:30"
    assert content.fields["headline"] == "钢琴课"
    assert content.full_text == "小雨 17:30 钢琴课，1 小时后开始"
    # 不足一小时的日程照样提醒，但要说清真实的剩余时间。
    late = schedule_reminder_content("小雨", "钢琴课", "17:30", 20)
    assert late.full_text.endswith("20 分钟后开始")


def test_evening_digest_stays_silent_without_outstanding_review() -> None:
    assert review_digest_content([]) is None
    assert review_digest_content([ChildReviewLoad("小雨", 0, ())]) is None
    content = review_digest_content(
        [ChildReviewLoad("小雨", 2, ("数学", "语文")), ChildReviewLoad("小满", 1, ("英语",))]
    )
    assert content is not None
    assert content.full_text.startswith("还有 3 个知识点没有复习：")
    assert "小雨 2 个（数学、语文）" in content.full_text
    assert content.fields["child"] == "全部孩子"


def test_dedupe_keys_identify_the_real_world_source() -> None:
    day = date(2026, 9, 6)
    # 同一个日程改时间仍然是同一条提醒，所以键里没有时间。
    assert (
        schedule_reminder_key("event-1", day, "member-1")
        == "schedule_reminder:event-1:2026-09-06:member-1"
    )
    assert schedule_reminder_key("event-1", day, "member-2") != schedule_reminder_key(
        "event-1", day, "member-1"
    )
    assert review_digest_key(day, "member-1") == "review_digest:2026-09-06:member-1"
    assert member_application_key("req-1", "member-1") == "member_application:req-1:member-1"


def test_retry_backoff_is_bounded() -> None:
    assert [retry_delay_seconds(attempt) for attempt in (1, 2, 3, 4, 10)] == [
        60,
        300,
        900,
        900,
        900,
    ]


def test_template_map_is_validated_before_it_can_be_used() -> None:
    bindings = parse_templates(
        '{"review_digest": {"template_id": "tpl-1", '
        '"fields": {"thing1": "headline", "thing2": "detail"}, "long_term": true}}'
    )
    assert set(bindings) == {"review_digest"}
    binding = bindings["review_digest"]
    assert binding.long_term is True
    assert binding.render({"headline": "还有 3 个知识点没复习", "detail": "小雨 3 个"}) == {
        "thing1": {"value": "还有 3 个知识点没复习"},
        "thing2": {"value": "小雨 3 个"},
    }
    # 缺失语义值不能渲染成空字符串塞给微信。
    assert binding.render({"headline": "只有标题"}) == {"thing1": {"value": "只有标题"}}
    assert parse_templates("") == {}
    for broken in (
        "{",
        "[]",
        '{"unknown_type": {"template_id": "x", "fields": {"thing1": "headline"}}}',
        '{"review_digest": {"fields": {"thing1": "headline"}}}',
        '{"review_digest": {"template_id": "tpl-1"}}',
        '{"review_digest": {"template_id": "tpl-1", "fields": {"thing1": "secret"}}}',
    ):
        with pytest.raises(ValueError):
            parse_templates(broken)


def test_unconfigured_deployment_reports_itself_unavailable() -> None:
    sender = build_sender(Settings(PUSH_KIDS_ENV="test"))
    assert isinstance(sender, UnavailableSender)
    assert sender.available is False
    assert sender.unavailable_reason
    # 没有加密密钥时也不能开微信通道。
    wechat_without_key = build_sender(
        Settings(PUSH_KIDS_ENV="test", PUSH_KIDS_NOTIFICATION_CHANNEL="wechat")
    )
    assert wechat_without_key.available is False
    with pytest.raises(ValueError):
        build_sender(Settings(PUSH_KIDS_ENV="cloud", PUSH_KIDS_NOTIFICATION_CHANNEL="recording"))


def test_receiver_identity_is_encrypted_and_authenticated() -> None:
    cipher = DestinationCipher("a" * 32)
    ciphertext = cipher.encrypt("oABC-openid-value")
    assert "oABC-openid-value" not in ciphertext
    assert cipher.decrypt(ciphertext) == "oABC-openid-value"
    # 同一个 OpenID 两次加密结果不同，密文不能被当成可比较的身份。
    assert cipher.encrypt("oABC-openid-value") != ciphertext
    with pytest.raises(DestinationCipherError):
        DestinationCipher("b" * 32).decrypt(ciphertext)
    with pytest.raises(DestinationCipherError):
        cipher.decrypt("not-base64-$$")
    with pytest.raises(DestinationCipherError):
        cipher.decrypt("c2hvcnQ=")
    with pytest.raises(ValueError):
        DestinationCipher("too-short")
