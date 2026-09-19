from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path

from tools.validate_design_evidence import validate_current_policy, validate_manifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png(path: Path, width: int, height: int) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        payload = kind + data
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload))

    row = b"\x00" + b"\xff\xff\xff" * width
    data = b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(row * height)),
            chunk(b"IEND", b""),
        )
    )
    path.write_bytes(data)


def _fixture(tmp_path: Path, *, approved: bool = True, omit_viewport: bool = False) -> Path:
    drev = "DREV-TEST-01"
    source_dir = tmp_path / "docs" / "design" / "frontend" / "prototypes" / drev
    snapshot_dir = tmp_path / "docs" / "design" / "frontend" / "snapshots" / "UI-TEST" / drev
    source_dir.mkdir(parents=True)
    snapshot_dir.mkdir(parents=True)
    frontend_spec = source_dir / "FRONTEND-SPEC.md"
    frontend_spec.write_text("# Test design\n", encoding="utf-8")
    source = source_dir / "screen.svg"
    source.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844"></svg>\n',
        encoding="utf-8",
    )
    viewports = [(320, 568), (390, 844), (430, 932)]
    if omit_viewport:
        viewports.pop()
    rows = []
    for width, height in viewports:
        export = snapshot_dir / f"screen-{width}.png"
        _png(export, width, height)
        rows.append(
            f"| `{export.name}` | default | {width}×{height} | 1x | `{_sha256(export)}` | test |"
        )
    status = "APPROVED" if approved else "AWAITING_APPROVAL"
    approved_by = "Product owner" if approved else "PENDING"
    approved_at = "2026-09-13" if approved else "PENDING"
    evidence = "message-1" if approved else "PENDING"
    source_path = source.relative_to(tmp_path).as_posix()
    spec_path = frontend_spec.relative_to(tmp_path).as_posix()
    manifest = snapshot_dir / "APPROVAL.md"
    manifest.write_text(
        "\n".join(
            (
                "# Test approval",
                "",
                f"- Status: `{status}`",
                "- UI ID: `UI-TEST`",
                f"- Design Revision: `{drev}`",
                "- Frontend baseline revision: `FDB-TEST`",
                "- Frontend engineering revision: `FEC-TEST`",
                "- Task Spec path and revision: `specs/active/test.md#SPEC-TEST`",
                f"- Frontend spec path: `{spec_path}`",
                f"- Editable design source path(s): `{source_path}`",
                f"- Editable source SHA-256: `{source_path}={_sha256(source)}`",
                f"- Approved by: `{approved_by}`",
                f"- Approved at: `{approved_at}`",
                f"- Approval evidence: `{evidence}`",
                "",
                "## Export manifest",
                "",
                "| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |",
                "|---|---|---|---|---|---|",
                *rows,
                "",
            )
        ),
        encoding="utf-8",
    )
    return manifest


def test_valid_approved_manifest(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path)

    assert validate_manifest(manifest, repo_root=tmp_path) == []


def test_missing_editable_source_is_rejected(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path)
    source = tmp_path / "docs/design/frontend/prototypes/DREV-TEST-01/screen.svg"
    source.unlink()

    errors = validate_manifest(manifest, repo_root=tmp_path)

    assert any("editable source not found" in error for error in errors)


def test_tampered_export_is_rejected(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path)
    export = manifest.parent / "screen-390.png"
    export.write_bytes(export.read_bytes() + b"tampered")

    errors = validate_manifest(manifest, repo_root=tmp_path)

    assert any("export hash mismatch" in error for error in errors)


def test_export_cannot_reference_another_design_directory(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path)
    outside = manifest.parent.parent / "other.png"
    _png(outside, 390, 844)
    text = manifest.read_text(encoding="utf-8")
    original = manifest.parent / "screen-390.png"
    text = text.replace(
        f"`screen-390.png` | default | 390×844 | 1x | `{_sha256(original)}`",
        f"`../other.png` | default | 390×844 | 1x | `{_sha256(outside)}`",
    )
    manifest.write_text(text, encoding="utf-8")

    errors = validate_manifest(manifest, repo_root=tmp_path)

    assert "export must stay in the manifest directory: ../other.png" in errors


def test_missing_required_viewport_is_rejected(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path, omit_viewport=True)

    errors = validate_manifest(manifest, repo_root=tmp_path)

    assert "missing required viewport exports: 430x932" in errors


def test_pending_manifest_requires_explicit_allowance(tmp_path: Path) -> None:
    manifest = _fixture(tmp_path, approved=False)

    strict_errors = validate_manifest(manifest, repo_root=tmp_path)
    candidate_errors = validate_manifest(manifest, repo_root=tmp_path, require_approved=False)

    assert "manifest status must be APPROVED" in strict_errors
    assert any("approved manifest requires Approved by" in error for error in strict_errors)
    assert candidate_errors == []


def test_current_policy_scan_ignores_historical_specs(tmp_path: Path) -> None:
    completed = tmp_path / "specs" / "completed"
    completed.mkdir(parents=True)
    (completed / "old.md").write_text(
        "- Figma node URL(s): https://www.figma.com/design/historical\n", encoding="utf-8"
    )

    assert validate_current_policy(tmp_path) == []


def test_current_policy_scan_rejects_active_dependency(tmp_path: Path) -> None:
    active = tmp_path / "specs" / "active"
    active.mkdir(parents=True)
    (active / "new.md").write_text("- Figma node URL(s): PENDING\n", encoding="utf-8")

    errors = validate_current_policy(tmp_path)

    assert len(errors) == 1
    assert "specs/active/new.md:1" in errors[0]


def test_current_policy_scan_includes_current_architecture(tmp_path: Path) -> None:
    architecture = tmp_path / "docs" / "architecture"
    architecture.mkdir(parents=True)
    (architecture / "ARCHITECTURE.md").write_text(
        "- Figma project/file URL: required\n", encoding="utf-8"
    )

    errors = validate_current_policy(tmp_path)

    assert len(errors) == 1
    assert "docs/architecture/ARCHITECTURE.md:1" in errors[0]
