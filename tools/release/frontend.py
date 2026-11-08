"""Validate and upload one frozen WeChat development version."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.release import miniprogram_version as versions
from tools.release import release_state as release

ROOT = release.ROOT
CLIENT = ROOT / "apps/miniprogram"
EVIDENCE = ROOT / "specs/evidence"
BOOTSTRAP = EVIDENCE / "client-release-20261108"
VERSION_PATH = versions.STATE_PATH
LIMIT = 1_500_000
CLIENT_SUFFIXES = {".js", ".json", ".wxml", ".wxss", ".wxs", ".png", ".jpg", ".jpeg"}
SECRETS = (
    "ARK_API_KEY",
    "MYSQL_PASSWORD",
    "PUSH_KIDS_DATABASE_URL",
    "PUSH_KIDS_ACTOR_HMAC_KEY",
    "WECHAT_DEVTOOLS_CLI_TOKEN",
)
SENSITIVE = re.compile(
    rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:mysql(?:\+\w+)?|postgres(?:ql)?)://"
    rb"|[\"'](?:openid|open_id|appsecret)[\"']\s*:\s*[\"'][A-Za-z0-9_-]{12,}",
    re.IGNORECASE,
)


def scan_client(directory: Path, *, generated: bool = False) -> dict[str, str]:
    secret_values = [os.environ.get(name, "").encode() for name in SECRETS]
    files = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if path.is_symlink():
            raise release.ReleaseError("候选小程序包含符号链接")
        if generated and relative.as_posix() == "project.private.config.json":
            continue  # DevTools local settings are not part of the compiled package.
        if any(part.startswith(".") for part in relative.parts):
            raise release.ReleaseError("候选小程序包含隐藏文件")
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix not in CLIENT_SUFFIXES:
            raise release.ReleaseError("候选小程序包含不允许的文件类型")
        if path.suffix in {".png", ".jpg", ".jpeg"} and relative.parts[0] != "assets":
            raise release.ReleaseError("小程序图片必须位于受审查的资源目录")
        data = path.read_bytes()
        if SENSITIVE.search(data) or any(
            len(value) >= 8 and value in data for value in secret_values
        ):
            raise release.ReleaseError("候选小程序命中敏感内容检查")
        files[relative.as_posix()] = release.sha(path)
    return files


def recover(journal: Path, version_path: Path) -> None:
    if not journal.exists():
        return
    item = release.read_json(journal)
    if item["state"] == "needs_reconciliation":
        raise release.ReleaseError(f"上传结果待核对，保留版本 {item['version']}")
    if item["state"] != "receipt":
        raise release.ReleaseError("上传日志状态无效")
    current = release.read_json(version_path)
    if (
        current["released"] == item["version"]
        and current.get("source_sha256") == item["source_sha256"]
    ):
        return
    if (
        current["released"] != item["previous"]
        or versions._next(item["previous"]) != item["version"]
    ):
        raise release.ReleaseError("本地版本与上传回执不一致")
    release.atomic_json(
        version_path,
        {
            **current,
            "released": item["version"],
            "source_sha256": item["source_sha256"],
            "upload_bytes": item["bytes"],
        },
    )


def baseline(version_path: Path) -> tuple[str, str, dict[str, str]]:
    record = release.read_json(version_path)
    released = record["released"]
    if "source_sha256" in record:
        receipt_path = ROOT / f"specs/evidence/client-{released}-upload/source-manifest.json"
        files = release.read_json(receipt_path)["client_files"] if receipt_path.exists() else {}
        if not files:
            for path in (ROOT / "dist/release").glob("frontend-*/source-manifest.json"):
                candidate = release.read_json(path)
                if candidate["source_sha256"] == record["source_sha256"]:
                    files = candidate["client_files"]
                    break
        if files and release.source_sha(files) == record["source_sha256"]:
            return released, record["source_sha256"], files
        raise release.ReleaseError("已上传版本缺少可核对的候选源清单")
    manifest = release.read_json(BOOTSTRAP / "source-manifest.json")
    if released != manifest["expected_version"]:
        raise release.ReleaseError("本地版本缺少可核对的已上传基准")
    package_bytes(BOOTSTRAP / "upload-info.json")
    files = manifest["client_files"]
    return released, release.source_sha(files), files


def package_bytes(path: Path) -> int:
    size = release.read_json(path)["size"]["total"]
    if type(size) is not int or not 0 < size <= LIMIT:
        raise release.ReleaseError("官方包体或回执无效")
    return size


def wechat_command(
    cli: list[str], action: str, frozen: Path, info: Path, qr: Path, version: str, description: str
) -> list[str]:
    if os.environ.get("WECHAT_MINIPROGRAM_CI_KEY_PATH"):
        return [
            "node",
            str(ROOT / "tools/release/wechat_ci.cjs"),
            action,
            release.APP_ID,
            str(frozen),
            str(info),
            str(qr),
            version,
            description,
        ]
    extra = (
        ["--qr-format", "image", "--qr-output", str(qr)]
        if action == "preview"
        else ["--version", version, "--desc", description]
    )
    return [*cli, action, "--project", str(frozen), "--info-output", str(info), *extra]


def confirm_uploaded(journal: Path, version: str, official_info: Path) -> None:
    pending = release.read_json(journal)
    if pending["state"] != "needs_reconciliation" or pending["version"] != version:
        raise release.ReleaseError("没有需要核对的匹配预留版本")
    pending.update(state="receipt", bytes=package_bytes(official_info), reconciled_at=release.now())
    release.atomic_json(journal, pending)
    recover(journal, VERSION_PATH)


def frontend_evidence(digest: str, changed: list[str]) -> dict:
    for path in sorted(EVIDENCE.glob("*/frontend-release-gates.json")):
        gates = release.read_json(path)
        if gates["source_sha256"] != digest:
            continue
        if changed != gates["changed_paths"]:
            raise release.ReleaseError("变更范围与发布证据不符")
        if gates["security_gate"] == "PASS":
            proof = release.read_json(path.parent / "dual-account-smoke.json")
            if (
                proof["source_sha256"] != digest
                or proof["family_isolation"] != "PASS"
                or proof["photo_owner"] != "PASS"
            ):
                raise release.ReleaseError("双账号验收证据与候选包不匹配")
        elif gates["security_gate"] != "NOT_APPLICABLE" or not gates["security_reason"]:
            raise release.ReleaseError("敏感边界变更需按发布手册完成双账号和图片 owner 验收")
        verification = release.read_json(path.parent / "verification.json")
        if not {390, 430} <= {item["width"] for item in verification if item["groups"] > 0}:
            raise release.ReleaseError("缺少两档必需原生布局证据")
        for row in verification:
            native = path.parent / "native" / str(row["width"])
            source = native / "source-sha256.json"
            if release.sha(source) != row["source_manifest_sha256"] or (
                release.source_sha(release.read_json(source)) != digest
            ):
                raise release.ReleaseError("原生证据与候选包摘要不一致")
            results = {}
            for matrix_path in native.glob("matrix*.json"):
                matrix = release.read_json(matrix_path)
                if matrix["source_manifest_sha256"] != row["source_manifest_sha256"]:
                    raise release.ReleaseError("原生矩阵来源与发布证据不一致")
                for item in matrix["results"]:
                    if any(
                        item[key]
                        for key in ("validation_errors", "horizontal_overflow", "screenshot_errors")
                    ):
                        raise release.ReleaseError("候选原生布局或截图校验失败")
                    results[item["name"]] = item["screenshot_sha256"]
            if len(results) != row["groups"] or any(
                release.sha(native / f"{name}.png") != expected
                for name, expected in results.items()
            ):
                raise release.ReleaseError("原生矩阵组数或截图摘要不匹配")
        return gates
    raise release.ReleaseError("缺少匹配候选摘要的前端发布取证")


def backend_compatibility(gates: dict, live: dict) -> int:
    if live["version"] != gates["backend_version"]:
        raise release.ReleaseError("当前后端版本与兼容性证据不一致")
    manifest = ROOT / gates["backend_manifest"]
    files = release.read_json(manifest)["backend"]["files"]
    if not files or any(release.sha(ROOT / item["path"]) != item["sha256"] for item in files):
        raise release.ReleaseError("后端源文件与已部署版本不一致")
    known = {item["path"] for item in files if item["path"].startswith("apps/api/src/")}
    current = {path.relative_to(ROOT).as_posix() for path in (ROOT / "apps/api/src").rglob("*.py")}
    if current != known:
        raise release.ReleaseError("后端源码清单与已部署版本范围不一致")
    return len(files)


def official_smoke(run: release.Run, folder: Path, cli: list[str], frozen: Path) -> list[dict]:
    probe = folder / "smoke-project"
    shutil.copytree(frozen, probe)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = str(reservation.getsockname()[1])
    run.step("devtools_auto", [*cli, "auto", "--project", str(probe), "--auto-port", port])
    rows = json.loads(
        run.step(
            "wechat_container_get",
            [
                "node",
                str(ROOT / "tools/release/wechat_readonly.cjs"),
                "smoke",
                port,
                release.ENV_ID,
                release.SERVICE,
            ],
            timeout=50,
        )
    )
    expected = {"live", "ready", "me", "children", "today", "calendar", "report"}
    if {row["route"] for row in rows if row["status"] == 200} != expected or len(rows) != 7:
        raise release.ReleaseError("微信容器只读主路径检查未通过")
    return rows


def publish(args: argparse.Namespace, folder: Path, journal: Path, run: release.Run) -> dict:
    if args.execute:
        recover(journal, VERSION_PATH)
    elif journal.exists() and release.read_json(journal)["state"] == "needs_reconciliation":
        raise release.ReleaseError("上一上传结果待核对")
    previous, deployed_digest, deployed_files = baseline(VERSION_PATH)
    files = scan_client(CLIENT)
    digest = release.source_sha(files)
    if digest == deployed_digest:
        return {"state": "SKIPPED_UNCHANGED", "version": previous, "source_sha256": digest}

    changed = sorted(
        name
        for name in set(deployed_files) | set(files)
        if files.get(name) != deployed_files.get(name)
    )
    target = versions._next(previous)
    frozen = folder / "client"
    shutil.copytree(CLIENT, frozen)
    if scan_client(frozen) != files:
        raise release.ReleaseError("冻结期间候选源码发生变化")
    config = release.read_json(frozen / "project.config.json")
    js = (frozen / "config.js").read_text()
    if (
        config.get("appid") != release.APP_ID
        or config.get("setting", {}).get("urlCheck") is not True
    ):
        raise release.ReleaseError("候选 AppID 或 urlCheck 不正确")
    for key, literal in (
        ("useCloud", "true"),
        ("cloudEnv", f'"{release.ENV_ID}"'),
        ("cloudService", f'"{release.SERVICE}"'),
    ):
        if re.findall(rf"(?m)^\s*{key}:\s*([^,\n]+)", js) != [literal]:
            raise release.ReleaseError("候选云配置不正确")
    source_bytes = sum((frozen / name).stat().st_size for name in files)
    if source_bytes > LIMIT:
        raise release.ReleaseError("候选源码包体超预算")
    manifest = {
        "version": target,
        "source_sha256": digest,
        "client_files": files,
        "source_bytes": source_bytes,
        "changed_paths": changed,
        "appid": release.APP_ID,
        "env": release.ENV_ID,
        "service": release.SERVICE,
        "git_head": run.step("git_head", ["git", "rev-parse", "HEAD"]).strip(),
    }
    release.atomic_json(folder / "source-manifest.json", manifest)
    gates = frontend_evidence(digest, changed)
    for name, command in (
        ("dependencies", ["npm", "install", "--no-audit", "--no-fund"]),
        ("frontend_tests", ["npm", "test"]),
        ("frontend_lint", ["npm", "run", "lint:miniapp"]),
        ("miniapp", ["uv", "run", "python", "tools/validate_miniprogram.py"]),
        ("architecture", ["uv", "run", "python", "tools/check_architecture.py"]),
        (
            "design_policy",
            ["uv", "run", "python", "tools/validate_design_evidence.py", "--check-current-policy"],
        ),
        (
            "approved_design",
            [
                "uv",
                "run",
                "python",
                "tools/validate_design_evidence.py",
                "--manifest",
                gates["design_manifest"],
            ],
        ),
        ("themes", ["node", "tools/check_themes.js"]),
        ("diff", ["git", "diff", "--check"]),
    ):
        run.step(name, command)
    if not args.execute:
        return {"state": "PREFLIGHT", "version": target, "source_sha256": digest}

    cli = [os.environ.get("WECHAT_DEVTOOLS_CLI", release.DEVTOOLS)]
    devtools = ["--port", args.devtools_port, "--lang", "zh"]
    state = release.cloud_state(run)
    live = release.live_version(state)
    matching = backend_compatibility(gates, live)
    output = run.step("devtools_login", [*cli, "islogin", *devtools])
    if not re.search(r'"login"\s*:\s*true', output):
        raise release.ReleaseError("微信开发者工具需要开发者扫码登录")
    cli = [*cli, *devtools]
    smoke = official_smoke(run, folder, cli, frozen)
    release.atomic_json(
        folder / "cloud.json",
        {
            "target": live,
            "matching_backend_files": matching,
            "public": state["public"],
            "smoke": smoke,
            "writes": 0,
        },
    )
    preview_info = folder / "preview.private.json"
    qr = folder / "preview.private.png"
    run.step(
        "official_preview",
        wechat_command(
            cli,
            "preview",
            frozen,
            preview_info,
            qr,
            target,
            args.description,
        ),
    )
    preview_size = package_bytes(preview_info)
    release.atomic_json(folder / "preview.json", {"bytes": preview_size})
    if scan_client(CLIENT) != files or scan_client(frozen, generated=True) != files:
        raise release.ReleaseError("门禁通过后源码变化，需重新冻结")
    if release.read_json(VERSION_PATH)["released"] != previous:
        raise release.ReleaseError("上传前版本基准发生变化")

    receipt = {
        "state": "needs_reconciliation",
        "previous": previous,
        "version": target,
        "source_sha256": digest,
        "reserved_at": release.now(),
        "transport": "miniprogram-ci"
        if os.environ.get("WECHAT_MINIPROGRAM_CI_KEY_PATH")
        else "devtools-cli",
    }
    release.atomic_json(journal, receipt)
    upload_info = folder / "upload.private.json"
    run.step(
        "official_upload",
        wechat_command(
            cli,
            "upload",
            frozen,
            upload_info,
            qr,
            target,
            args.description,
        ),
    )
    uploaded_size = package_bytes(upload_info)
    receipt.update(state="receipt", bytes=uploaded_size, uploaded_at=release.now())
    release.atomic_json(journal, receipt)
    release.atomic_json(folder / "receipt.json", receipt)
    recover(journal, VERSION_PATH)
    return {
        "state": "UPLOADED_DEVELOPMENT",
        "version": target,
        "bytes": uploaded_size,
        "preview_bytes": preview_size,
        "source_sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--description", default="")
    parser.add_argument("--confirm-uploaded", metavar="VERSION")
    parser.add_argument("--official-info", type=Path)
    parser.add_argument("--devtools-port", default=os.environ.get("WECHAT_DEVTOOLS_PORT", "43391"))
    args = parser.parse_args()
    if (bool(args.confirm_uploaded) != bool(args.official_info)) or (
        args.confirm_uploaded and args.execute
    ):
        parser.error("回执核对需同时指定 --confirm-uploaded 与 --official-info，且不执行上传")
    if args.execute and (
        not 4 <= len(args.description.strip()) <= 100 or not args.description.isprintable()
    ):
        parser.error("执行上传需要 4–100 字的用户可见版本说明")
    if not args.devtools_port.isdecimal() or not 1 <= int(args.devtools_port) <= 65535:
        parser.error("开发者工具服务端口无效")
    folder = release.run_dir("frontend")
    run = release.Run(folder / "steps.jsonl")
    try:
        with release.release_lock("frontend") as journal:
            if args.confirm_uploaded:
                confirm_uploaded(journal, args.confirm_uploaded, args.official_info)
                result = {"state": "RECONCILED_UPLOAD", "version": args.confirm_uploaded}
            else:
                result = publish(args, folder, journal, run)
    except release.ReleaseError as exc:
        result = {"state": "BLOCKED", "reason": str(exc)}
    except (OSError, KeyError, TypeError, ValueError) as exc:
        result = {"state": "BLOCKED", "reason": type(exc).__name__}
    release.atomic_json(folder / "result.json", result)
    print(f"{result['state']} {result.get('version', result.get('reason', ''))} {folder}")
    return int(result["state"] == "BLOCKED")


if __name__ == "__main__":
    raise SystemExit(main())
