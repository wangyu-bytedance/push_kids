"""Preflight or create one same-schema, zero-traffic WeChat Cloud Run version."""

from __future__ import annotations

import argparse
import os
import re
import selectors
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4

from sqlalchemy import make_url, text

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.prepare_cloud_release import ROOT_FILES, SOURCE_DIRECTORY, prepare_release
from tools.release import release_state as release

ROOT = release.ROOT
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def source_files(root: Path) -> dict[str, str]:
    paths = [root / name for name in ROOT_FILES]
    source = root / SOURCE_DIRECTORY
    if (
        not source.is_dir()
        or source.is_symlink()
        or any(path.is_symlink() for path in source.rglob("*"))
    ):
        raise release.ReleaseError("后端发布源目录无效或包含符号链接")
    paths += list(source.rglob("*.py"))
    if any(path.is_symlink() or not path.is_file() for path in paths):
        raise release.ReleaseError("后端发布源包含符号链接或不可读文件")
    return {path.relative_to(root).as_posix(): release.sha(path) for path in paths}


def verify_package(folder: Path, files: dict[str, str]) -> None:
    expected = set(files) | {"release-manifest.json"}
    actual = {path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_file()}
    if actual != expected or source_files(folder) != files or source_files(ROOT) != files:
        raise release.ReleaseError("后端白名单与冻结源码不匹配")
    manifest = release.read_json(folder / "release-manifest.json")["files"]
    if {row["path"]: row["sha256"] for row in manifest} != files:
        raise release.ReleaseError("后端冻结清单不匹配")


def code_revision(run: release.Run, env: dict[str, str]) -> str:
    heads = run.step("alembic_heads", ["uv", "run", "alembic", "heads"], env=env).splitlines()
    database_file = ROOT / SOURCE_DIRECTORY / "push_kids/platform/database.py"
    expected = re.findall(r'expected_cloud_revision = "([a-z0-9_]+)"', database_file.read_text())
    if len(heads) != 1 or len(expected) != 1 or heads[0].split()[0] != expected[0]:
        raise release.ReleaseError("Alembic 唯一 head 与应用预期不一致")
    return expected[0]


def schema_gate(revision: str) -> dict:
    from push_kids.platform.config import Settings
    from push_kids.platform.database import Database

    migration = os.environ.get("PUSH_KIDS_RELEASE_MIGRATION_URL")
    runtime = os.environ.get("PUSH_KIDS_RELEASE_RUNTIME_URL")
    if not migration or not runtime:
        raise release.ReleaseError("缺少生产 Schema 两种只读核验身份")
    try:
        admin, app = make_url(migration), make_url(runtime)
        target = (admin.host, admin.port or 3306, admin.database)
        if (
            not admin.host
            or admin.host in {"localhost", "127.0.0.1", "::1"}
            or admin.database != "push_kids"
            or target != (app.host, app.port or 3306, app.database)
            or admin.drivername != app.drivername
            or app.drivername != "mysql+pymysql"
            or not admin.username
            or not app.username
            or admin.username == app.username
        ):
            raise release.ReleaseError("生产 Schema 目标或两种账号不匹配")
        for url, strict in ((migration, True), (runtime, False)):
            database = Database(Settings(_env_file=None, PUSH_KIDS_DATABASE_URL=url))
            try:
                with database.engine.connect() as connection:
                    rows = connection.execute(
                        text("SELECT version_num FROM alembic_version")
                    ).scalars()
                    if list(rows) != [revision]:
                        raise release.ReleaseError("生产 Schema 与唯一代码 head 不同")
                database.verify_cloud_schema(verify_triggers=strict)
            finally:
                database.engine.dispose()
    except release.ReleaseError:
        raise
    except Exception as exc:
        raise release.ReleaseError(f"生产 Schema 只读核验失败（{type(exc).__name__}）") from None
    return {"revision": revision, "strict": "PASS", "runtime": "PASS", "writes": 0}


def isolated_mysql(run: release.Run, env: dict[str, str], revision: str) -> None:
    url = env.get("PUSH_KIDS_TEST_MYSQL_URL")
    if not url:
        raise release.ReleaseError("缺少隔离 MySQL 测试库")
    parsed = make_url(url)
    if (
        parsed.host not in {"127.0.0.1", "::1"}
        or not parsed.database
        or not parsed.database.startswith("pk_release_")
        or parsed.drivername != "mysql+pymysql"
        or parsed.query
    ):
        raise release.ReleaseError("MySQL 测试必须使用本机 pk_release_ 专用库")
    from sqlalchemy import create_engine

    engine = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as connection:
            table_count = connection.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()")
            ).scalar_one()
            server = connection.execute(text("SELECT VERSION()")).scalar_one()
            if table_count or not server.startswith("5.7."):
                raise release.ReleaseError("MySQL 发布回归需要空的 5.7 测试库")
    finally:
        engine.dispose()
    mysql_env = {**env, "PUSH_KIDS_DATABASE_URL": url}
    run.step("mysql_fresh_upgrade", ["uv", "run", "alembic", "upgrade", "head"], env=mysql_env)
    current = run.step("mysql_current", ["uv", "run", "alembic", "current"], env=mysql_env)
    if revision not in current.split():
        raise release.ReleaseError("本地 MySQL 未迁移到唯一 head")
    run.step("mysql_schema_check", ["uv", "run", "alembic", "check"], env=mysql_env)


def container_checks(run: release.Run, package: Path, tag: str) -> None:
    image = f"push-kids-release:{tag}"
    run.step("docker_build", ["docker", "build", "-t", image, str(package)], timeout=600)
    uid = run.step(
        "docker_user", ["docker", "image", "inspect", "--format", "{{.Config.User}}", image]
    ).strip()
    if not uid.isdecimal() or int(uid) <= 0:
        raise release.ReleaseError("冻结镜像未声明非 root UID")
    identifier = run.step(
        "docker_start",
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "-p",
            "127.0.0.1::8000",
            "-e",
            "PUSH_KIDS_ENV=test",
            "-e",
            "PUSH_KIDS_RUN_WORKER=false",
            "-e",
            "PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER=false",
            image,
        ],
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{64}", identifier):
        raise release.ReleaseError("无法核对本地容器 ID")
    try:
        address = run.step("docker_port", ["docker", "port", identifier, "8000/tcp"]).strip()
        if not re.fullmatch(r"127\.0\.0\.1:[0-9]+", address):
            raise release.ReleaseError("本地容器端口未绑定 loopback")
        for endpoint in ("live", "ready"):
            for _ in range(30):
                try:
                    with urlopen(f"http://{address}/health/{endpoint}", timeout=2) as response:
                        if response.status == 200:
                            run.record(f"docker_{endpoint}", "PASS")
                            break
                except (URLError, TimeoutError):
                    time.sleep(1)
            else:
                raise release.ReleaseError(f"本地容器 {endpoint} 检查失败")
    finally:
        run.step("docker_sigterm", ["docker", "stop", "--time", "10", identifier], timeout=30)


def confirmation_fields(remark: str) -> dict[str, str]:
    return {
        "微信AppId": release.APP_ID,
        "环境ID": release.ENV_ID,
        "服务名称": release.SERVICE,
        "部署方式": "手动上传代码包",
        "发布模式": "灰度发布",
        "Dockerfile文件名": "Dockerfile",
        "目标目录": ".",
        "端口号": "8000",
        "版本备注": remark,
    }


def confirmation_matches(output: str, expected: dict[str, str]) -> bool:
    text_output = ANSI.sub("", output)
    entries = {}
    for line in text_output.splitlines():
        cells = line.strip().strip("│").split("│")
        if len(cells) == 2:
            key, value = (cell.strip() for cell in cells)
            if key in entries:
                return False
            entries[key] = value
    return entries == expected


def gray_argv(folder: Path, remark: str) -> list[str]:
    return [
        "wxcloud",
        "run:deploy",
        str(folder),
        *release.TARGET,
        "--containerPort",
        "8000",
        "--dockerfile",
        "Dockerfile",
        "--targetDir",
        ".",
        "--releaseType",
        "GRAY",
        "--remark",
        remark,
        "--override",
        "--detach",
    ]


def confirm_gray(
    run: release.Run, folder: Path, journal: Path, record: dict, files: dict[str, str]
) -> bool:
    if not sys.stdin.isatty():
        raise release.ReleaseError("灰度发布必须在终端核对官方确认表")
    expected = confirmation_fields(record["remark"])
    with (
        subprocess.Popen(
            gray_argv(folder, record["remark"]),
            cwd=folder.parent,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process,
        selectors.DefaultSelector() as reader,
    ):
        assert process.stdin is not None and process.stdout is not None
        reader.register(process.stdout, selectors.EVENT_READ)
        output = bytearray()
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and len(output) < 64_000:
                if not reader.select(timeout=1):
                    continue
                chunk = os.read(process.stdout.fileno(), 4096)
                if not chunk:
                    break
                output.extend(chunk)
                decoded = output.decode(errors="replace")
                if "确定发布" not in decoded:
                    continue
                if not confirmation_matches(decoded, expected):
                    raise release.ReleaseError("wxcloud 确认表缺失或字段不一致")
                for key, value in expected.items():
                    print(f"{key} {value}")
                if input("确认创建零流量灰度版本，输入 yes 继续：").strip() != "yes":
                    process.stdin.write(b"no\n")
                    process.stdin.flush()
                    return False
                verify_package(folder, files)
                release.atomic_json(journal, record)
                process.stdin.write(b"yes\n")
                process.stdin.flush()
                try:
                    process.communicate(timeout=180)
                except subprocess.TimeoutExpired:
                    run.record("gray_cli", "UNKNOWN")
                else:
                    run.record("gray_cli", "RETURNED", exit_code=process.returncode)
                return True
            raise release.ReleaseError("未获得 wxcloud 官方确认表")
        finally:
            if process.poll() is None:
                process.kill()


def observe_gray(run: release.Run, journal: Path, record: dict) -> dict:
    for _ in range(60):
        state = release.cloud_state(run)
        active = release.live_version(state)
        if active["version"] != record["rollback"]:
            raise release.ReleaseError("原承载流量版本发生变化，保留灰度核对记录")
        candidates = [item for item in state["versions"] if item["remark"] == record["remark"]]
        if len(candidates) > 1:
            raise release.ReleaseError("灰度备注匹配多个版本")
        if candidates:
            target = candidates[0]
            if target["flow"] != 0 or target["status"] == "deploy_failed":
                raise release.ReleaseError("灰度版本部署失败或流量不为零")
            if target["status"] == "normal":
                result = {
                    **record,
                    "state": "BACKEND_GRAY",
                    "target": target,
                    "health": "PENDING_TARGET_SMOKE",
                    "public": state["public"],
                }
                release.atomic_json(journal, result)
                return result
        time.sleep(10)
    raise release.ReleaseError("灰度结果待核对，保留备注并停止重试创建")


def publish(args: argparse.Namespace, folder: Path, journal: Path, run: release.Run) -> dict:
    package = folder / "package"
    files = source_files(ROOT)
    digest = release.source_sha(files)
    if journal.exists():
        record = release.read_json(journal)
        if record["state"] == "NEEDS_RECONCILIATION":
            if not args.execute:
                raise release.ReleaseError("上一灰度结果待核对")
            return observe_gray(run, journal, record)
        if record["source_sha256"] == digest:
            return {**record, "state": "SKIPPED_UNCHANGED"}

    prepare_release(ROOT, package)
    verify_package(package, files)
    env = {**os.environ, "PYTHONPATH": str(ROOT / SOURCE_DIRECTORY)}
    for name in (
        "PUSH_KIDS_RELEASE_MIGRATION_URL",
        "PUSH_KIDS_RELEASE_RUNTIME_URL",
        "PUSH_KIDS_DATABASE_URL",
        "MYSQL_ADDRESS",
        "MYSQL_PASSWORD",
        "MYSQL_USERNAME",
        "MYSQL_DATABASE",
    ):
        env.pop(name, None)
    env["PUSH_KIDS_ENV"] = "test"
    revision = code_revision(run, env)
    head = run.step("git_head", ["git", "rev-parse", "HEAD"]).strip()
    receipt = {"source_sha256": digest, "files": len(files), "revision": revision, "git_head": head}
    if not args.execute:
        return {**receipt, "state": "PREFLIGHT", "production_checks": "NOT_RUN"}
    if not sys.stdin.isatty():
        raise release.ReleaseError("灰度发布必须在终端核对官方确认表")

    state = release.cloud_state(run)
    active = release.live_version(state)
    receipt["schema"] = schema_gate(revision)
    run.step("dependencies", ["uv", "sync", "--all-groups"], env=env)
    isolated_mysql(run, env, revision)
    for name, command in (
        (
            "backend_tests",
            ["uv", "run", "pytest", "tests/unit", "tests/integration", "tests/contract", "-q"],
        ),
        ("lint", ["uv", "run", "ruff", "check", "."]),
        ("format", ["uv", "run", "ruff", "format", "--check", "."]),
        ("mypy", ["uv", "run", "mypy", "apps/api/src"]),
        ("architecture", ["uv", "run", "python", "tools/check_architecture.py"]),
        ("frontend_dependencies", ["npm", "install", "--no-audit", "--no-fund"]),
        ("frontend_tests", ["npm", "test"]),
        ("frontend_lint", ["npm", "run", "lint:miniapp"]),
        ("miniapp", ["uv", "run", "python", "tools/validate_miniprogram.py"]),
    ):
        run.step(name, command, env=env, timeout=600)
    tag = uuid4().hex[:10]
    container_checks(run, package, tag)
    run.step("wxcloud_dry_run", ["wxcloud", "deploy", "--dryRun", *release.TARGET], cwd=package)
    verify_package(package, files)
    if release.live_version(release.cloud_state(run)) != active:
        raise release.ReleaseError("确认前生产后端基线发生变化")
    record = {
        **receipt,
        "state": "NEEDS_RECONCILIATION",
        "rollback": active["version"],
        "remark": f"pk-{head[:8]}-{digest[:10]}-{tag}",
        "reserved_at": release.now(),
    }
    if not confirm_gray(run, package, journal, record, files):
        return {**receipt, "state": "OPERATOR_DECLINED"}
    return observe_gray(run, journal, record)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / SOURCE_DIRECTORY))
    folder = release.run_dir("backend")
    run = release.Run(folder / "steps.jsonl")
    try:
        with release.release_lock("backend") as journal:
            result = publish(args, folder, journal, run)
    except release.ReleaseError as exc:
        result = {"state": "BLOCKED", "reason": str(exc)}
    except (OSError, KeyError, TypeError, ValueError) as exc:
        result = {"state": "BLOCKED", "reason": type(exc).__name__}
    release.atomic_json(folder / "result.json", result)
    print(f"{result['state']} {result.get('reason', '')} {folder}")
    return int(result["state"] == "BLOCKED")


if __name__ == "__main__":
    raise SystemExit(main())
