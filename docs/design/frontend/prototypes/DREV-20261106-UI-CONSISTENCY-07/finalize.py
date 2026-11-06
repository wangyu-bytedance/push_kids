"""Freeze source/export hashes and check old design evidence without mutating it."""

import hashlib
import json
import struct
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SNAPSHOTS = ROOT / "docs/design/frontend/snapshots/UI-001"
OUT = SNAPSHOTS / HERE.name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def item(path, **extra):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path), **extra}


def main():
    older = []
    for number in range(1, 7):
        folder = SNAPSHOTS / f"DREV-20261106-UI-CONSISTENCY-{number:02d}"
        manifest = json.loads((folder / "manifest.json").read_text())
        checks = []
        for group in ("sources", "files" if "files" in manifest else "exports"):
            for entry in manifest.get(group, []):
                path = ROOT / entry["path"]
                checks.append(path.is_file() and digest(path) == entry["sha256"])
        assert checks and all(checks), str(folder)
        older.append({"design": folder.name, "entries": len(checks), "result": "PASS"})
    baseline = json.loads((OUT / "production-baseline.json").read_text())
    assert len(baseline) == 355
    assert all(digest(ROOT / k) == v["sha256"] for k, v in baseline.items())
    integrity = {
        "previous_revisions": older,
        "product_source": "355 files unchanged against DREV06",
        "production_implementation": "NOT_STARTED",
    }
    (OUT / "integrity-check.json").write_text(json.dumps(integrity, ensure_ascii=False, indent=2))
    exports = []
    for path in sorted(OUT.glob("*.png")):
        entry = item(path)
        if path.name != "overview.png":
            theme, state, dimensions = path.stem.split("-", 2)
            if state == "storage":
                state, dimensions = "storage-error", path.stem.split("storage-error-")[1]
            entry.update(
                theme=theme,
                scene=f"settings-{state}",
                viewport=[int(n) for n in dimensions.split("x")],
            )
        else:
            entry.update(
                scene="overview", viewport=list(struct.unpack(">II", path.read_bytes()[16:24]))
            )
        exports.append(entry)
    sources = [item(p) for p in sorted(HERE.iterdir()) if p.is_file()]
    previous = HERE.parent / "DREV-20261106-UI-CONSISTENCY-06/assets"
    sources += [item(p) for p in sorted(previous.glob("*.png"))]
    sources += [item(ROOT / "apps/miniprogram/assets/illustrations/record-books.png")]
    evidence = {
        name: digest(OUT / name)
        for name in ("verification.json", "integrity-check.json", "production-baseline.json")
    }
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "designRevision": HERE.name,
                "taskSpecRevision": "DESIGN-002-SPEC-07",
                "architectureRevision": "ARCH-20261106-MINIAPP-THEMES-01",
                "status": "AWAITING_IMPLEMENTATION_APPROVAL",
                "generatedAt": datetime.now(UTC).isoformat(),
                "sources": sources,
                "exports": exports,
                "evidenceSha256": evidence,
                "nativeAcceptance": "NOT_RUN",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(
        json.dumps(
            {"sources": len(sources), "exports": len(exports), "old_designs": older},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
