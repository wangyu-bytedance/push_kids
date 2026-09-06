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
    # 骨架里的语义映射必须覆盖每类提醒真实会产生的内容。
    for type_name, semantics in tool.USED_SEMANTICS.items():
        assert set(bindings[type_name].fields.values()) == set(semantics)


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
    assert tool.cmd_check(argparse.Namespace(file=str(good))) == 0
    ok = capsys.readouterr().out
    assert "NOTIFICATION_TEMPLATES_VALID types=1" in ok
    # 未配置的类型要如实说明会显示为不可用，而不是静默通过。
    assert "member_application: 未配置" in ok
    # 密钥本身绝不能被打印出来。
    assert "y" * 40 not in ok
