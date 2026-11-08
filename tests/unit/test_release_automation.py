from argparse import Namespace
from pathlib import Path

import pytest

from tools.release import backend, frontend, release_state


def test_pending_upload_stops_before_new_version(tmp_path: Path) -> None:
    journal = tmp_path / "pending.json"
    release_state.atomic_json(journal, {"state": "needs_reconciliation", "version": "0.1.20"})
    with pytest.raises(release_state.ReleaseError, match="核对"):
        frontend.recover(journal, tmp_path / "version.json")


def test_receipt_recovers_once(tmp_path: Path) -> None:
    journal = tmp_path / "pending.json"
    versions = tmp_path / "version.json"
    release_state.atomic_json(versions, {"released": "0.1.19"})
    release_state.atomic_json(
        journal,
        {
            "state": "receipt",
            "previous": "0.1.19",
            "version": "0.1.20",
            "source_sha256": "a" * 64,
            "bytes": 100,
        },
    )
    frontend.recover(journal, versions)
    frontend.recover(journal, versions)
    assert release_state.read_json(versions)["released"] == "0.1.20"
    assert release_state.read_json(versions)["source_sha256"] == "a" * 64


def test_failed_tool_does_not_persist_or_echo_secrets(tmp_path: Path) -> None:
    import sys

    log = tmp_path / "log.jsonl"
    with pytest.raises(release_state.ReleaseError) as error:
        release_state.Run(log).step(
            "test", [sys.executable, "-c", "import sys; print('secret-sentinel'); sys.exit(3)"]
        )
    assert "secret-sentinel" not in str(error.value)
    assert "secret-sentinel" not in log.read_text()


@pytest.mark.parametrize("execute", [False, True])
def test_frontend_fake_cli_orders_preview_upload_and_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, execute: bool
) -> None:
    source = tmp_path / "client-source"
    source.mkdir()
    release_state.atomic_json(
        source / "project.config.json",
        {"appid": release_state.APP_ID, "setting": {"urlCheck": True}},
    )
    (source / "config.js").write_text(
        f'useCloud: true,\ncloudEnv: "{release_state.ENV_ID}",\n'
        f'cloudService: "{release_state.SERVICE}",\n'
    )
    version = tmp_path / "version.json"
    release_state.atomic_json(version, {"released": "0.1.19"})
    folder = tmp_path / "run"
    folder.mkdir()
    journal = tmp_path / "journal.json"
    monkeypatch.setattr(frontend, "CLIENT", source)
    monkeypatch.setattr(frontend, "VERSION_PATH", version)
    monkeypatch.setattr(frontend, "baseline", lambda _: ("0.1.19", "old-sha", {}))
    monkeypatch.setattr(frontend, "frontend_evidence", lambda *_: {"design_manifest": "approved"})
    monkeypatch.setattr(frontend, "backend_compatibility", lambda *_: 160)
    monkeypatch.setattr(frontend, "official_smoke", lambda *_: [])
    monkeypatch.setattr(release_state, "cloud_state", lambda _: {"public": False})
    monkeypatch.setattr(release_state, "live_version", lambda _: {"version": "flask-ik19-040"})
    monkeypatch.delenv("WECHAT_MINIPROGRAM_CI_KEY_PATH", raising=False)
    calls = []

    def step(_, name, command):
        calls.append(name)
        if name in {"official_preview", "official_upload"}:
            output = Path(command[command.index("--info-output") + 1])
            release_state.atomic_json(output, {"size": {"total": 123}})
        if name == "official_upload":
            assert release_state.read_json(journal)["state"] == "needs_reconciliation"
            assert command[command.index("--version") + 1] == "0.1.20"
        return '{"login":true}'

    monkeypatch.setattr(release_state.Run, "step", step)
    result = frontend.publish(
        Namespace(execute=execute, description="布局修复", devtools_port="43391"),
        folder,
        journal,
        release_state.Run(folder / "steps.jsonl"),
    )
    if execute:
        assert calls.index("official_preview") < calls.index("official_upload")
        assert result["state"] == "UPLOADED_DEVELOPMENT"
        assert release_state.read_json(version)["released"] == "0.1.20"
    else:
        assert result["state"] == "PREFLIGHT"
        assert "official_upload" not in calls
        assert "official_preview" not in calls
        assert not journal.exists()


def test_backend_confirmation_is_exactly_gray_and_rejects_runtime_values(tmp_path: Path) -> None:
    expected = backend.confirmation_fields("pk-fake")
    table = "\n".join(f"│ {key} │ {value} │" for key, value in expected.items())
    assert backend.confirmation_matches(table, expected)
    assert not backend.confirmation_matches(table.replace("灰度发布", "全量发布"), expected)
    assert not backend.confirmation_matches(table + "\n│ 服务参数 │ secret-sentinel │", expected)
    command = backend.gray_argv(tmp_path, "pk-fake")
    assert "--noConfirm" not in command
    assert command[command.index("--releaseType") + 1] == "GRAY"


def test_backend_unknown_deploy_uses_read_only_polling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rollback = {"version": "flask-ik19-040", "status": "normal", "flow": 100, "replicas": 1}
    target = {"version": "flask-ik19-041", "status": "normal", "flow": 0, "remark": "pk-fake"}
    monkeypatch.setattr(
        release_state, "cloud_state", lambda _: {"versions": [rollback, target], "public": False}
    )
    journal = tmp_path / "journal.json"
    record = {"remark": "pk-fake", "rollback": rollback["version"], "state": "NEEDS_RECONCILIATION"}
    result = backend.observe_gray(release_state.Run(tmp_path / "steps.jsonl"), journal, record)
    assert result["target"] == target
    assert release_state.read_json(journal)["state"] == "BACKEND_GRAY"
