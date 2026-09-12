#!/usr/bin/env python3
"""小程序发布版本号工具。

微信开发者工具 CLI（`cli upload`）只接受 `--version`，无法读取小程序后台的
线上/审核/体验/开发版本号，因此历史上版本号靠人工填写，容易复用导致三条通道
（线上/审核/开发）版本号相同、无法区分。

本工具用仓库内的 ``miniprogram_version.json`` 记录“已上传给微信的最新版本号”
作为体验版基准，并在其第三位（patch）上 +1 计算下一个上传版本号，杜绝复用。

用法::

    python3 tools/release/miniprogram_version.py current   # 打印当前基准版本
    python3 tools/release/miniprogram_version.py next      # 打印下一个上传版本（patch+1）
    python3 tools/release/miniprogram_version.py bump       # 上传成功后：把基准推进到 next 并写回

约定：patch 版本号不可复用；``next`` 恒为 ``current`` 的第三位 +1。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATE_PATH = Path(__file__).with_name("miniprogram_version.json")
_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _parse(version: str) -> tuple[int, int, int]:
    match = _SEMVER.match(version.strip())
    if not match:
        raise ValueError(f"版本号必须是 major.minor.patch 三段数字，收到：{version!r}")
    return int(match[1]), int(match[2]), int(match[3])


def _read_released() -> str:
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"找不到版本状态文件：{STATE_PATH}")
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    released = data.get("released")
    if not isinstance(released, str):
        raise ValueError(f"{STATE_PATH} 缺少字符串字段 'released'")
    _parse(released)  # 校验格式
    return released


def _next(version: str) -> str:
    major, minor, patch = _parse(version)
    return f"{major}.{minor}.{patch + 1}"


def cmd_current() -> str:
    return _read_released()


def cmd_next() -> str:
    return _next(_read_released())


def cmd_bump() -> str:
    """把基准版本推进到 next 并写回状态文件（上传成功后调用）。"""
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    new_version = _next(data["released"])
    data["released"] = new_version
    STATE_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return new_version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["current", "next", "bump"], help="要执行的操作"
    )
    args = parser.parse_args(argv)

    try:
        result = {"current": cmd_current, "next": cmd_next, "bump": cmd_bump}[
            args.command
        ]()
    except (ValueError, FileNotFoundError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
