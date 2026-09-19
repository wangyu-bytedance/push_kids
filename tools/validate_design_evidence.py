from __future__ import annotations

import argparse
import hashlib
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_VIEWPORTS = {(320, 568), (390, 844), (430, 932)}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
DIMENSION_RE = re.compile(r"^(\d+)\s*[×xX]\s*(\d+)$")
SCALE_RE = re.compile(r"^(\d+(?:\.\d+)?)x$")
PROHIBITED_CURRENT_POLICY = (
    re.compile(r"Frontend Design Impact and Figma Approval", re.IGNORECASE),
    re.compile(r"Figma project/file URL\s*:", re.IGNORECASE),
    re.compile(r"Figma node(?: URL\(s\)| URLs?| URL)?\s*:", re.IGNORECASE),
    re.compile(r"Figma waiver\s*:", re.IGNORECASE),
    re.compile(r"BLOCKED_FIGMA|FIGMA_WAIVED", re.IGNORECASE),
    re.compile(r"https://(?:www\.)?figma\.com", re.IGNORECASE),
)


def _plain(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1].strip()
    return value


def _metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^- ([^:]+):\s*(.*)$", line)
        if match:
            result[match.group(1).strip()] = _plain(match.group(2))
    return result


def _parts(value: str) -> list[str]:
    return [_plain(part) for part in re.split(r"[;；]", value) if part.strip()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_path(root: Path, raw_path: str) -> tuple[Path | None, str | None]:
    candidate = Path(_plain(raw_path))
    if candidate.is_absolute():
        return None, f"path must be repository-relative: {raw_path}"
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None, f"path escapes repository: {raw_path}"
    return resolved, None


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def _table_rows(text: str, heading: str) -> list[list[str]]:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return []
    rows: list[list[str]] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if not line.strip().startswith("|"):
            continue
        cells = [_plain(cell) for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] == "File" or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def _is_pending(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().upper()
    return not normalized or normalized in {"PENDING", "N/A", "NONE", "[TODO]"}


def validate_manifest(
    manifest_path: Path,
    *,
    repo_root: Path = ROOT,
    require_approved: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not manifest_path.exists():
        return [f"manifest not found: {manifest_path}"]

    text = manifest_path.read_text(encoding="utf-8")
    meta = _metadata(text)
    required = (
        "Status",
        "UI ID",
        "Design Revision",
        "Frontend baseline revision",
        "Frontend engineering revision",
        "Task Spec path and revision",
        "Frontend spec path",
        "Editable design source path(s)",
        "Editable source SHA-256",
        "Approved by",
        "Approved at",
        "Approval evidence",
    )
    for key in required:
        if key not in meta or not meta[key].strip():
            errors.append(f"missing metadata: {key}")

    design_revision = meta.get("Design Revision", "")
    frontend_spec_raw = meta.get("Frontend spec path", "")
    if frontend_spec_raw:
        frontend_spec, path_error = _repo_path(repo_root, frontend_spec_raw)
        if path_error:
            errors.append(path_error)
        elif frontend_spec is not None:
            expected_dir = repo_root / "docs" / "design" / "frontend" / "prototypes"
            try:
                relative = frontend_spec.relative_to(expected_dir.resolve())
            except ValueError:
                errors.append(f"frontend spec must be under {expected_dir.relative_to(repo_root)}")
            else:
                if not relative.parts or relative.parts[0] != design_revision:
                    errors.append("frontend spec directory must match Design Revision")
            if not frontend_spec.is_file():
                errors.append(f"frontend spec not found: {frontend_spec_raw}")

    source_paths = _parts(meta.get("Editable design source path(s)", ""))
    hash_entries = _parts(meta.get("Editable source SHA-256", ""))
    source_hashes: dict[str, str] = {}
    for entry in hash_entries:
        raw_path, separator, digest = entry.rpartition("=")
        if not separator or not raw_path.strip() or not HASH_RE.fullmatch(digest.strip()):
            errors.append(f"invalid editable source hash entry: {entry}")
            continue
        source_hashes[_plain(raw_path)] = digest.strip()

    if not source_paths:
        errors.append("at least one editable design source is required")
    for raw_path in source_paths:
        source, path_error = _repo_path(repo_root, raw_path)
        if path_error:
            errors.append(path_error)
            continue
        assert source is not None
        expected_dir = repo_root / "docs" / "design" / "frontend" / "prototypes" / design_revision
        try:
            source.relative_to(expected_dir.resolve())
        except ValueError:
            errors.append(f"editable source must be under {expected_dir.relative_to(repo_root)}")
        if source.suffix.lower() not in {".svg", ".html"}:
            errors.append(f"unsupported editable source format: {raw_path}")
        if not source.is_file():
            errors.append(f"editable source not found: {raw_path}")
            continue
        expected_hash = source_hashes.get(raw_path)
        if expected_hash is None:
            errors.append(f"missing editable source hash: {raw_path}")
        elif _sha256(source) != expected_hash:
            errors.append(f"editable source hash mismatch: {raw_path}")
        source_text = source.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?:src|href)\s*=\s*['\"]https?://|url\(\s*https?://", source_text, re.I):
            errors.append(f"editable source must be self-contained: {raw_path}")

    for extra_hash_path in source_hashes.keys() - set(source_paths):
        errors.append(f"hash recorded for unlisted editable source: {extra_hash_path}")

    rows = _table_rows(text, "## Export manifest")
    if not rows:
        errors.append("export manifest must contain at least one row")
    seen_viewports: set[tuple[int, int]] = set()
    for row in rows:
        if len(row) < 5:
            errors.append(f"invalid export row: {' | '.join(row)}")
            continue
        raw_file, _, raw_viewport, raw_scale, raw_hash = row[:5]
        relative_export = Path(_plain(raw_file))
        if relative_export.is_absolute():
            errors.append(f"export path must be relative to manifest: {raw_file}")
            continue
        export_path = (manifest_path.parent / relative_export).resolve()
        try:
            export_path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"export path escapes repository: {raw_file}")
            continue
        try:
            export_path.relative_to(manifest_path.parent.resolve())
        except ValueError:
            errors.append(f"export must stay in the manifest directory: {raw_file}")
            continue
        if export_path.suffix.lower() != ".png":
            errors.append(f"export must be PNG: {raw_file}")
        if not export_path.is_file():
            errors.append(f"export not found: {raw_file}")
            continue
        dimension_match = DIMENSION_RE.fullmatch(raw_viewport)
        scale_match = SCALE_RE.fullmatch(raw_scale)
        if not dimension_match:
            errors.append(f"invalid CSS viewport: {raw_viewport}")
            continue
        if not scale_match:
            errors.append(f"invalid export scale: {raw_scale}")
            continue
        css_size = (int(dimension_match.group(1)), int(dimension_match.group(2)))
        seen_viewports.add(css_size)
        scale = float(scale_match.group(1))
        expected_pixels = (round(css_size[0] * scale), round(css_size[1] * scale))
        actual_pixels = _png_dimensions(export_path)
        if actual_pixels != expected_pixels:
            errors.append(
                f"export dimensions mismatch: {raw_file} "
                f"expected={expected_pixels} actual={actual_pixels}"
            )
        digest = _plain(raw_hash)
        if not HASH_RE.fullmatch(digest):
            errors.append(f"invalid export hash: {raw_file}")
        elif _sha256(export_path) != digest:
            errors.append(f"export hash mismatch: {raw_file}")

    missing_viewports = REQUIRED_VIEWPORTS - seen_viewports
    if missing_viewports:
        formatted = ", ".join(f"{width}x{height}" for width, height in sorted(missing_viewports))
        errors.append(f"missing required viewport exports: {formatted}")

    if require_approved:
        if meta.get("Status", "").upper() != "APPROVED":
            errors.append("manifest status must be APPROVED")
        for key in ("Approved by", "Approved at", "Approval evidence"):
            if _is_pending(meta.get(key)):
                errors.append(f"approved manifest requires {key}")
    elif meta.get("Status", "").upper() not in {"AWAITING_APPROVAL", "APPROVED"}:
        errors.append("candidate manifest status must be AWAITING_APPROVAL or APPROVED")

    return errors


def current_policy_files(repo_root: Path) -> list[Path]:
    files = [
        repo_root / "AGENTS.md",
        repo_root / "docs" / "architecture" / "ARCHITECTURE.md",
        repo_root / "docs" / "architecture" / "ARCHITECTURE-CONSTRAINTS.md",
        repo_root / "docs" / "design" / "frontend" / "README.md",
        repo_root / "docs" / "design" / "frontend" / "FRONTEND-DESIGN.md",
        repo_root / "docs" / "design" / "frontend" / "FRONTEND-ENGINEERING-CONSTRAINTS.md",
        repo_root / "docs" / "design" / "frontend" / "UI-CURRENT-STATE-TEMPLATE.md",
        repo_root / "docs" / "design" / "frontend" / "snapshots" / "APPROVAL-TEMPLATE.md",
    ]
    for directory in (
        repo_root / "docs" / "design" / "frontend" / "ui",
        repo_root / "specs" / "_templates",
        repo_root / "specs" / "active",
    ):
        if directory.exists():
            files.extend(sorted(directory.glob("*.md")))
    governance_spec = (
        repo_root / "specs" / "active" / ("GOV-001-REPOSITORY-NATIVE-FRONTEND-DESIGN-EVIDENCE.md")
    )
    return [path for path in files if path.exists() and path != governance_spec]


def validate_current_policy(repo_root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in current_policy_files(repo_root):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(pattern.search(line) for pattern in PROHIBITED_CURRENT_POLICY):
                errors.append(
                    f"prohibited current Figma dependency: "
                    f"{path.relative_to(repo_root)}:{line_number}: {line.strip()}"
                )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate repository-native design evidence")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--allow-pending", action="store_true")
    parser.add_argument("--check-current-policy", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.manifest is None and not args.check_current_policy:
        parser.error("provide --manifest and/or --check-current-policy")

    repo_root = args.repo_root.resolve()
    errors: list[str] = []
    if args.manifest is not None:
        manifest = args.manifest
        if not manifest.is_absolute():
            manifest = repo_root / manifest
        errors.extend(
            validate_manifest(
                manifest,
                repo_root=repo_root,
                require_approved=not args.allow_pending,
            )
        )
    if args.check_current_policy:
        errors.extend(validate_current_policy(repo_root))

    if errors:
        print("DESIGN_EVIDENCE_INVALID")
        print("\n".join(errors))
        raise SystemExit(1)
    print("DESIGN_EVIDENCE_VALID")


if __name__ == "__main__":
    main()
