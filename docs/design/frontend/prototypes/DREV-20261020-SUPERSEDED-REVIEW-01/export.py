"""Reproduce local design exports; does not connect to any application data."""

import hashlib
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[5]
source = Path(__file__).with_name("index.html")
out = root / "docs/design/frontend/snapshots/UI-001/DREV-20261020-SUPERSEDED-REVIEW-01"
out.mkdir(parents=True, exist_ok=True)
rows = []
for state in ("normal", "superseded", "menu", "viewer", "long", "deleted", "empty"):
    for width, height in ((320, 568), (390, 844), (430, 932)):
        name = f"{state}-{width}x{height}.png"
        subprocess.run(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--user-data-dir=/private/tmp/push-kids-design-chrome",
                f"--screenshot={out / name}",
                f"--window-size={width},{height}",
                "--timeout=1000",
                source.as_uri() + "?state=" + state + "&width=" + str(width),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        digest = hashlib.sha256((out / name).read_bytes()).hexdigest()
        rows.append(
            f"| {name} | UI-001/{state} | {width}×{height} | 1x | {digest} | HTML设计；非原生验收 |"
        )
        print(name, flush=True)
rel = source.relative_to(root)
task_ref = (
    "specs/active/FEAT-001-AUTO-SUPERSEDED-REVIEW-STATE.md#SPEC-20261020-AUTO-SUPERSEDED-REVIEW-02"
)
front_ref = str(source.parent.relative_to(root) / "FRONTEND-SPEC.md")
header = f"""# UI-001 — 已替代复习词条设计清单

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: DREV-20261020-SUPERSEDED-REVIEW-01
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {task_ref}
- Frontend spec path: {front_ref}
- Editable design source path(s): {rel}
- Editable source SHA-256: {rel}={hashlib.sha256(source.read_bytes()).hexdigest()}
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
(out / "APPROVAL.md").write_text(header + "\n".join(rows) + "\n")
