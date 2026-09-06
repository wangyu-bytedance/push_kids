from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections.abc import Mapping
from pathlib import Path

ROOT_FILES = ("Dockerfile", "pyproject.toml", "uv.lock", "wxcloud.config.json")
SECRET_ENV_NAMES = ("ARK_API_KEY", "MYSQL_PASSWORD", "PUSH_KIDS_ACTOR_HMAC_KEY")
SOURCE_DIRECTORY = Path("apps/api/src")


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _secret_values(environ: Mapping[str, str]) -> dict[str, bytes]:
    return {
        name: value.encode()
        for name in SECRET_ENV_NAMES
        if len(value := environ.get(name, "").strip()) >= 8
    }


def _assert_no_runtime_secret(path: Path, secrets: Mapping[str, bytes]) -> None:
    content = path.read_bytes()
    for name, value in secrets.items():
        if value in content:
            raise RuntimeError(f"发布文件包含运行时秘密变量 {name} 的值：{path.name}")


def _assert_safe_output(project_root: Path, output_dir: Path) -> None:
    dist_root = (project_root / "dist").resolve()
    try:
        output_dir.resolve().relative_to(dist_root)
    except ValueError as exc:
        raise ValueError("发布目录必须位于项目 dist/ 下") from exc
    if output_dir.resolve() == dist_root:
        raise ValueError("发布目录不能直接使用 dist/ 根目录")


def prepare_release(
    project_root: Path,
    output_dir: Path,
    environ: Mapping[str, str] | None = None,
) -> list[dict[str, str | int]]:
    project_root = project_root.resolve()
    output_dir = output_dir.resolve()
    _assert_safe_output(project_root, output_dir)
    secrets = _secret_values(environ or os.environ)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    try:
        for relative_name in ROOT_FILES:
            source = project_root / relative_name
            if not source.is_file():
                raise FileNotFoundError(f"缺少发布必需文件：{relative_name}")
            target = output_dir / relative_name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        source_root = project_root / SOURCE_DIRECTORY
        if not source_root.is_dir():
            raise FileNotFoundError(f"缺少发布源码目录：{SOURCE_DIRECTORY}")
        for source in sorted(source_root.rglob("*.py")):
            if "__pycache__" in source.parts:
                continue
            relative_path = source.relative_to(project_root)
            target = output_dir / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        release_files = sorted(path for path in output_dir.rglob("*") if path.is_file())
        for path in release_files:
            if any(part in {".git", "__pycache__"} for part in path.parts):
                raise RuntimeError(f"发布目录包含禁止路径：{path.name}")
            if path.name == ".env" or path.name.startswith(".env."):
                raise RuntimeError(f"发布目录包含环境文件：{path.name}")
            _assert_no_runtime_secret(path, secrets)

        manifest: list[dict[str, str | int]] = [
            {
                "path": path.relative_to(output_dir).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _digest(path),
            }
            for path in release_files
        ]
        (output_dir / "release-manifest.json").write_text(
            json.dumps({"files": manifest}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="生成不含运行时密钥、测试、文档和本地数据的微信云托管发布目录。"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/cloud-release"),
        help="项目 dist/ 下的输出目录，默认 dist/cloud-release",
    )
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    output_dir = args.output if args.output.is_absolute() else project_root / args.output
    manifest = prepare_release(project_root, output_dir)
    total_bytes = sum(int(item["bytes"]) for item in manifest)
    print(f"cloud_release_ready files={len(manifest)} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
