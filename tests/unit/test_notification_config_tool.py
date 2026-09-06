"""The operator tool must agree with the runtime parser; otherwise a "valid" config still fails."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest
from push_kids.notifications.templates import parse_templates

ROOT = Path(__file__).resolve().parents[2]


def load_tool() -> Any:
    spec = importlib.util.spec_from_file_location(
        "notification_config_tool", ROOT / "tools" / "notification_config.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_secret_satisfies_the_runtime_length_rule() -> None:
    tool = load_tool()
    import argparse

    assert tool.cmd_secret(argparse.Namespace()) == 0
    # 与 config.py 的门槛保持一致：32 个字符。
    from push_kids.platform.config import Settings

    settings = Settings(
        PUSH_KIDS_ENV="test",
        PUSH_KIDS_NOTIFICATION_CHANNEL="wechat",
        PUSH_KIDS_NOTIFICATION_SECRET_KEY="x" * 32,
        PUSH_KIDS_NOTIFICATION_TEMPLATES=json.dumps(
            {"review_digest": {"template_id": "t", "fields": {"thing1": "headline"}}}
        ),
    )
    assert len(settings.notification_secret_value) >= 32


def test_scaffold_output_parses_with_the_runtime_parser(
    capsys: pytest.CaptureFixture[str],
) -> None:
    tool = load_tool()
    import argparse

    assert tool.cmd_scaffold(argparse.Namespace()) == 0
    printed = capsys.readouterr().out
    bindings = parse_templates(printed)
    assert set(bindings) == {"member_application", "schedule_reminder", "review_digest"}
    # 骨架至少要覆盖每类提醒必须说清的内容，且不能出现这类提醒产不出的内容。
    for type_name, required in tool.REQUIRED_SEMANTICS.items():
        mapped = set(bindings[type_name].fields.values())
        assert set(required) <= mapped
        assert mapped <= set(tool.AVAILABLE_SEMANTICS[type_name])


def test_check_rejects_configs_the_runtime_would_reject(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"review_digest": {"fields": {"thing1": "headline"}}}))
    assert tool.cmd_check(argparse.Namespace(file=str(bad))) == 1
    assert "NOTIFICATION_TEMPLATES_INVALID" in capsys.readouterr().out

    unknown = tmp_path / "unknown.json"
    unknown.write_text(
        json.dumps({"review_digest": {"template_id": "t", "fields": {"thing1": "mastery"}}})
    )
    assert tool.cmd_check(argparse.Namespace(file=str(unknown))) == 1
    assert "NOTIFICATION_TEMPLATES_INVALID" in capsys.readouterr().out

    empty = tmp_path / "empty.json"
    empty.write_text("   ")
    assert tool.cmd_check(argparse.Namespace(file=str(empty))) == 1
    assert "NOTIFICATION_TEMPLATES_MISSING" in capsys.readouterr().out


def test_check_flags_a_short_secret_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    good = tmp_path / "good.json"
    good.write_text(
        json.dumps({"review_digest": {"template_id": "t", "fields": {"thing1": "headline"}}})
    )
    monkeypatch.setenv("PUSH_KIDS_NOTIFICATION_SECRET_KEY", "short")
    assert tool.cmd_check(argparse.Namespace(file=str(good))) == 1
    output = capsys.readouterr().out
    assert "NOTIFICATION_CONFIG_PROBLEM" in output

    monkeypatch.setenv("PUSH_KIDS_NOTIFICATION_SECRET_KEY", "y" * 40)
    complete = tmp_path / "complete.json"
    complete.write_text(
        json.dumps(
            {
                "review_digest": {
                    "template_id": "t",
                    "fields": {"thing2": "detail", "thing4": "headline"},
                }
            }
        )
    )
    assert tool.cmd_check(argparse.Namespace(file=str(complete))) == 0
    ok = capsys.readouterr().out
    assert "NOTIFICATION_TEMPLATES_VALID types=1" in ok
    # 未配置的类型要如实说明会显示为不可用，而不是静默通过。
    assert "member_application: 未配置" in ok
    # 密钥本身绝不能被打印出来。
    assert "y" * 40 not in ok


# 微信「获取已有模板列表」的真实返回形状（字段结构取自官方文档 api_getwxapubnewtemplate），
# 三个模板与本项目线上后台已选用的模板一致：新队员加入提醒 / 日程提醒 / 复习通知。
WECHAT_TEMPLATE_LIST = {
    "errcode": 0,
    "errmsg": "ok",
    "data": [
        {
            "priTmplId": "TPL_APPLY",
            "title": "新队员加入提醒",
            "content": (
                "姓名:{{thing1.DATA}}\n申请时间:{{time3.DATA}}\n温馨提示:{{thing5.DATA}}\n"
            ),
            "type": 2,
        },
        {
            "priTmplId": "TPL_SCHEDULE",
            "title": "日程提醒",
            "content": (
                "日程主题:{{thing1.DATA}}\n时长:{{thing2.DATA}}\n时间:{{time3.DATA}}\n"
                "开始时间:{{time15.DATA}}\n距离开始时间:{{short_thing18.DATA}}\n"
            ),
            "type": 3,
        },
        {
            "priTmplId": "TPL_DIGEST",
            "title": "复习通知",
            "content": "复习内容:{{thing2.DATA}}\n备注:{{thing4.DATA}}\n",
            "type": 2,
        },
    ],
}


def test_from_wechat_lists_templates_without_choosing_for_the_operator(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    source = tmp_path / "gettemplate.json"
    source.write_text(json.dumps(WECHAT_TEMPLATE_LIST), encoding="utf-8")
    assert tool.cmd_from_wechat(argparse.Namespace(file=str(source), map=None)) == 0
    out = capsys.readouterr().out
    assert "WECHAT_TEMPLATE_LIST count=3" in out
    # 字段键必须从模板正文里解析出来，长期/一次性要如实标注。
    assert "thing1、thing2、time3、time15、short_thing18" in out
    assert "TPL_SCHEDULE · 长期" in out
    assert "TPL_DIGEST · 一次性" in out


def test_from_wechat_output_parses_with_the_runtime_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    source = tmp_path / "gettemplate.json"
    source.write_text(json.dumps(WECHAT_TEMPLATE_LIST), encoding="utf-8")
    args = argparse.Namespace(
        file=str(source),
        map=[
            "member_application=TPL_APPLY",
            "schedule_reminder=TPL_SCHEDULE",
            "review_digest=TPL_DIGEST",
        ],
    )
    assert tool.cmd_from_wechat(args) == 0
    printed = capsys.readouterr().out
    bindings = parse_templates(printed)
    assert bindings["schedule_reminder"].template_id == "TPL_SCHEDULE"
    assert bindings["schedule_reminder"].long_term is True
    assert bindings["review_digest"].long_term is False
    # 后台模板的每个槽位都必须映射到真实内容，否则微信会整条拒发。
    for type_name, required in tool.REQUIRED_SEMANTICS.items():
        mapped = set(bindings[type_name].fields.values())
        assert set(required) <= mapped
        assert mapped <= set(tool.AVAILABLE_SEMANTICS[type_name])
    # 「开始时间」必须拿到真正的开始时间，泛化的「时间」只能退到提醒发出时间。
    assert bindings["schedule_reminder"].fields["time15"] == "time"
    assert bindings["schedule_reminder"].fields["time3"] == "notified_at"
    assert bindings["schedule_reminder"].fields["thing2"] == "duration"
    assert bindings["schedule_reminder"].fields["short_thing18"] == "countdown"
    assert bindings["member_application"].fields["thing1"] == "applicant"
    assert bindings["member_application"].fields["time3"] == "applied_at"
    assert bindings["review_digest"].fields["thing2"] == "detail"
    assert bindings["review_digest"].fields["thing4"] == "headline"


def test_from_wechat_refuses_unknown_types_and_missing_templates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    source = tmp_path / "gettemplate.json"
    source.write_text(json.dumps(WECHAT_TEMPLATE_LIST), encoding="utf-8")
    assert (
        tool.cmd_from_wechat(argparse.Namespace(file=str(source), map=["mastery=TPL_APPLY"])) == 1
    )
    assert "WECHAT_TEMPLATE_MAP_INVALID" in capsys.readouterr().out

    args = argparse.Namespace(file=str(source), map=["review_digest=TPL_MISSING"])
    assert tool.cmd_from_wechat(args) == 1
    assert "WECHAT_TEMPLATE_NOT_FOUND" in capsys.readouterr().out

    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps({"errcode": 40001, "errmsg": "invalid credential"}))
    assert tool.cmd_from_wechat(argparse.Namespace(file=str(broken), map=None)) == 1
    assert "WECHAT_TEMPLATE_LIST_INVALID" in capsys.readouterr().out


def test_from_wechat_warns_when_template_fields_have_no_content(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tool = load_tool()
    import argparse

    source = tmp_path / "gettemplate.json"
    source.write_text(
        json.dumps(
            {
                "data": [
                    {
                        "priTmplId": "TPL_ENUM",
                        "title": "设备提醒",
                        "content": "提醒:{{thing1.DATA}}\n位置:{{enum_string2.DATA}}\n",
                        "type": 2,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(file=str(source), map=["review_digest=TPL_ENUM"])
    assert tool.cmd_from_wechat(args) == 0
    captured = capsys.readouterr()
    # 枚举字段不会被当成自由文本，而且必须提示微信会因缺参数拒发。
    assert "enum_string2" in captured.err
    assert "47003" in captured.err
    assert "enum_string2" not in captured.out
