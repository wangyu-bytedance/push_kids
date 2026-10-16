"Rasterize frozen approved SVGs; never rewrite approval or source exports."

import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / ("docs/design/frontend/snapshots/UI-001/DREV-20261014-SUBJECT-MANAGEMENT-01")
target = OUT / "VALIDATION.md"
if target.exists():
    raise SystemExit("Supplement already exists; do not overwrite frozen evidence")
sources, rows = [], []
for svg in sorted(HERE.glob("*.svg")):
    state, size = svg.stem.rsplit("-", 1)
    png = OUT / (svg.stem + ".png")
    subprocess.run(["rsvg-convert", str(svg), "-o", str(png)], check=True)
    relative = str(svg.relative_to(ROOT))
    sources.append((relative, hashlib.sha256(svg.read_bytes()).hexdigest()))
    rows.append(
        f"| {png.name} | {state} | {size} | 1x | {hashlib.sha256(png.read_bytes()).hexdigest()} |"
    )
target.write_text(
    (
        "# 原批准设计的导出补充清单\n\n- Status: APPROVED\n- UI ID: U"
        "I-001\n- Design Revision: DREV-20261014-SUBJEC"
        "T-MANAGEMENT-01\n- Frontend baseline revision:"
        " FDB-20260913-04\n- Frontend engineering revis"
        "ion: FEC-20261007-NATIVE-GEOMETRY-02\n- Task S"
        "pec path and revision: specs/active/FEAT-001-"
        "SUBJECT-MANAGEMENT-CONSISTENCY.md#SPEC-202610"
        "14-SUBJECT-MANAGEMENT-01\n- Frontend spec path"
        ": docs/design/frontend/prototypes/DREV-202610"
        "14-SUBJECT-MANAGEMENT-01/FRONTEND-SPEC.md\n- E"
        "ditable design source path(s): "
    )
    + "; ".join(p for p, _ in sources)
    + "\n- Editable source SHA-256: "
    + "; ".join(f"{p}={sha}" for p, sha in sources)
    + (
        "\n- Approved by: 用户\n- Approved at: 2026-10-15\n"
        "- Approval evidence: 本聊天用户针对具体 Spec / DREV 回复"
        "“落地和实现”；原批准记录 APPROVAL.md 未变更。\n\n## Export man"
        "ifest\n\n| File | State | Viewport | Scale | SH"
        "A-256 |\n|---|---|---|---|---|\n"
    )
    + "\n".join(rows)
    + "\n"
)
