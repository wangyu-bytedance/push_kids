import importlib.util
from pathlib import Path

import pytest

_MODULE_SPEC = importlib.util.spec_from_file_location(
    "prepare_cloud_release",
    Path(__file__).resolve().parents[2] / "tools/prepare_cloud_release.py",
)
assert _MODULE_SPEC and _MODULE_SPEC.loader
_MODULE = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(_MODULE)
prepare_release = _MODULE.prepare_release


def _release_fixture(root: Path, provider_source: str = "VALUE = 'safe'\n") -> None:
    for filename in ("Dockerfile", "pyproject.toml", "uv.lock", "wxcloud.config.json"):
        (root / filename).write_text(f"fixture:{filename}\n", encoding="utf-8")
    package = root / "apps/api/src/push_kids"
    package.mkdir(parents=True)
    (package / "providers.py").write_text(provider_source, encoding="utf-8")
    cache = package / "__pycache__"
    cache.mkdir()
    (cache / "providers.pyc").write_bytes(b"compiled")
    (root / ".env").write_text("ARK_API_KEY=must-not-copy\n", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git/config").write_text("secret repository data\n", encoding="utf-8")


def test_prepare_release_copies_only_production_allowlist(tmp_path: Path) -> None:
    _release_fixture(tmp_path)
    output = tmp_path / "dist/cloud-release"

    manifest = prepare_release(tmp_path, output, environ={})

    paths = {item["path"] for item in manifest}
    assert paths == {
        "Dockerfile",
        "apps/api/src/push_kids/providers.py",
        "pyproject.toml",
        "uv.lock",
        "wxcloud.config.json",
    }
    assert (output / "release-manifest.json").is_file()
    assert not (output / ".env").exists()
    assert not (output / ".git").exists()
    assert not any("__pycache__" in path.parts for path in output.rglob("*"))


def test_prepare_release_rejects_runtime_secret_value(tmp_path: Path) -> None:
    sentinel = "ark-test-secret-sentinel"
    _release_fixture(tmp_path, provider_source=f"VALUE = {sentinel!r}\n")
    output = tmp_path / "dist/cloud-release"

    with pytest.raises(RuntimeError, match="ARK_API_KEY") as error:
        prepare_release(tmp_path, output, environ={"ARK_API_KEY": sentinel})

    assert sentinel not in str(error.value)
    assert not output.exists()


def test_prepare_release_refuses_output_outside_dist(tmp_path: Path) -> None:
    _release_fixture(tmp_path)

    with pytest.raises(ValueError, match="dist"):
        prepare_release(tmp_path, tmp_path / "cloud-release", environ={})
