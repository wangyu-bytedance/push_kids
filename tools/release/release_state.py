"""Local release journal and subprocess boundary shared by both entry points."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_ID = "wx5d2e0014690bf285"
ENV_ID = "prod-d2g14rwoycac6b45d"
SERVICE = "flask-ik19"
TARGET = ["-e", ENV_ID, "-s", SERVICE]
DEVTOOLS = "/Applications/wechatwebdevtools.app/Contents/MacOS/cli"


class ReleaseError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as f:
        temporary = Path(f.name)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_sha(files: dict[str, str]) -> str:
    data = json.dumps(files, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode()).hexdigest()


@contextmanager
def release_lock(channel: str) -> Iterator[Path]:
    result = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    state = Path(result.stdout.strip()) / "push-kids-release"
    state.mkdir(mode=0o700, exist_ok=True)
    with (state / f"{channel}.lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReleaseError("已有同目标发布正在运行") from exc
        yield state / f"{channel}.json"


def run_dir(channel: str) -> Path:
    parent = ROOT / "dist/release"
    parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f"{channel}-", dir=parent))


class Run:
    def __init__(self, log: Path):
        self.log = log

    def record(self, name: str, status: str, **fields) -> None:
        with self.log.open("a", encoding="utf-8") as out:
            out.write(json.dumps({"step": name, "status": status, "at": now(), **fields}) + "\n")

    def step(
        self,
        name: str,
        command: list[str],
        *,
        cwd: Path = ROOT,
        timeout: int = 180,
        env: dict[str, str] | None = None,
    ) -> str:
        self.record(name, "START")
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.record(name, "FAIL", category=type(exc).__name__)
            raise ReleaseError(f"{name} 未完成（{type(exc).__name__}）") from None
        if result.returncode:
            self.record(name, "FAIL", exit_code=result.returncode)
            raise ReleaseError(f"{name} 失败（退出码 {result.returncode}）")
        self.record(name, "PASS")
        return result.stdout


def cloud_state(run: Run) -> dict:
    output = run.step(
        "cloud_state",
        ["node", str(ROOT / "tools/release/wechat_readonly.cjs"), "state", ENV_ID, SERVICE],
    )
    state = json.loads(output)
    if state["status"] != "normal" or state["public"] is not False:
        raise ReleaseError("云托管状态或入口未满足发布门禁")
    return state


def live_version(state: dict) -> dict:
    active = [item for item in state["versions"] if item["flow"] == 100]
    if len(active) != 1 or active[0]["status"] != "normal" or active[0]["replicas"] < 1:
        raise ReleaseError("未核实唯一正常承载流量的后端版本")
    if any(item["flow"] != 0 and item != active[0] for item in state["versions"]):
        raise ReleaseError("后端流量分配与发布基线不一致")
    return active[0]
