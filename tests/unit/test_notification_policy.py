"""FEAT-003：通知策略与配置解析的纯函数行为。

这些规则决定"提醒说什么、什么时候能重试、什么算同一条消息"，必须能脱离数据库和微信账号验证。
"""

from __future__ import annotations

from datetime import date, datetime

import pytest
from push_kids.notifications.destinations import DestinationCipher, DestinationCipherError
from push_kids.notifications.domain import (
    FIELD_LIMIT,
    FIELD_TYPE_LIMITS,
    KINDS,
    ChildReviewLoad,
    countdown_text,
    duration_text,
    kind_for,
    local_datetime_text,
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


def test_every_field_is_clamped_to_its_own_wechat_field_type() -> None:
    long_name = "很长很长很长很长很长很长很长的课程名称"
    content = schedule_reminder_content(
        "小雨", long_name, "17:30", 45, duration_minutes=90, notified_at_text="2026年9月7日 16:45"
    )
    binding = parse_templates(
        '{"schedule_reminder": {"template_id": "tpl-1", "fields": {'
        '"thing1": "headline", "thing2": "duration", "time3": "notified_at", '
        '"time15": "time", "short_thing18": "countdown"}}}'
    )["schedule_reminder"]
    rendered = binding.render(content.fields)
    # thing 上限 20、short_thing 上限 5，任何一个超长都会让整条消息被拒。
    assert len(rendered["thing1"]["value"]) <= FIELD_TYPE_LIMITS["thing"]
    assert rendered["thing1"]["value"].endswith("…")
    assert len(rendered["short_thing18"]["value"]) <= FIELD_TYPE_LIMITS["short_thing"]
    assert rendered["short_thing18"]["value"] == "45分钟"
    assert rendered["thing2"]["value"] == "1时30分"
    # 时间字段不能被截断，否则微信无法解析。
    assert rendered["time15"]["value"] == "17:30"
    assert rendered["time3"]["value"] == "2026年9月7日 16:45"
    assert truncate("一二三四五六七八九十一二三四五六七八九十一") == (
        "一二三四五六七八九十一二三四五六七八九" + "…"
    )
    assert FIELD_TYPE_LIMITS["thing"] == FIELD_LIMIT


def test_time_and_span_wording_matches_the_wechat_field_semantics() -> None:
    assert local_datetime_text(datetime(2026, 9, 7, 17, 30)) == "2026年9月7日 17:30"
    assert duration_text(None) == ""
    assert duration_text(0) == ""
    assert duration_text(45) == "45分钟"
    assert duration_text(60) == "1小时"
    assert duration_text(90) == "1时30分"
    # 距离开始时间是 short_thing（上限 5 个字），且"已经到点"要说得明确。
    assert countdown_text(0) == "即将开始"
    assert countdown_text(60) == "1小时"
    assert all(len(countdown_text(minutes)) <= 5 for minutes in (0, 1, 20, 60, 95))


def test_schedule_reminder_says_which_child_when_and_what() -> None:
    content = schedule_reminder_content(
        "小雨",
        "钢琴课",
        "17:30",
        60,
        start_datetime_text="2026年9月7日 17:30",
        duration_minutes=60,
    )
    assert content.fields["child"] == "小雨"
    assert content.fields["time"] == "2026年9月7日 17:30"
    # 日程主题一个字段就要说清是谁的什么事。
    assert content.fields["headline"] == "小雨 钢琴课"
    assert content.fields["duration"] == "1小时"
    assert content.fields["countdown"] == "1小时"
    assert content.full_text == "小雨 17:30 钢琴课，1 小时后开始"
    # 不足一小时的日程照样提醒，但要说清真实的剩余时间。
    late = schedule_reminder_content("小雨", "钢琴课", "17:30", 20)
    assert late.full_text.endswith("20 分钟后开始")
    assert late.fields["countdown"] == "20分钟"
    # 没有可信的结束时间就如实说没设置，而不是编一个时长、也不能因此不发提醒。
    assert late.fields["duration"] == "未设置"


def test_member_application_carries_the_applicant_and_when_they_applied() -> None:
    content = member_application_content("奶奶", "AB12CD34", "2026年9月6日 20:15")
    assert content.fields["applicant"] == "奶奶"
    assert content.fields["applied_at"] == "2026年9月6日 20:15"
    assert content.fields["code"] == "AB12CD34"
    assert "AB12CD34" in content.fields["detail"]
    # 申请时间未知时不能拿散文填进时间字段。
    assert "applied_at" not in member_application_content("奶奶", "AB12CD34").fields


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
    # 模板留了槽位却没有内容，必须在调用微信之前就能看出来。
    assert binding.missing_fields({"headline": "只有标题"}) == ("thing2",)
    assert binding.missing_fields({"headline": "标题", "detail": "详情"}) == ()
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
    sender = build_sender(Settings(_env_file=None, PUSH_KIDS_ENV="test"))
    assert isinstance(sender, UnavailableSender)
    assert sender.available is False
    assert sender.unavailable_reason
    # 没有加密密钥时也不能开微信通道。
    wechat_without_key = build_sender(
        Settings(
            _env_file=None,
            PUSH_KIDS_ENV="test",
            PUSH_KIDS_NOTIFICATION_CHANNEL="wechat",
        )
    )
    assert wechat_without_key.available is False
    with pytest.raises(ValueError):
        build_sender(
            Settings(
                _env_file=None,
                PUSH_KIDS_ENV="cloud",
                PUSH_KIDS_NOTIFICATION_CHANNEL="recording",
            )
        )


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
