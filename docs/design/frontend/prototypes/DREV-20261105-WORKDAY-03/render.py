"""Deterministic synthetic HTML exports; never native acceptance evidence."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001" / HERE.name
SOURCE = HERE / "index.html"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved evidence is immutable")
    OUT.mkdir(parents=True, exist_ok=True)
    rows, audits = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--disable-gpu"])
        version = browser.version
        for width, height in [(320, 568), (390, 844), (430, 932)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
            page.goto(SOURCE.as_uri())
            for state in page.evaluate("window.designStates"):
                page.evaluate("window.designShow", state)
                assert not errors, errors
                assert page.evaluate("document.documentElement.scrollWidth") == width
                assert (
                    page.locator(".sheet").count() == 0
                    or page.locator(".foot").bounding_box()["y"] < height
                )
                assert page.evaluate("""() => [...document.querySelectorAll('button')].filter(e=>{
                    const r=e.getBoundingClientRect();return r.width&&r.height;
                  }).every(e=>e.getBoundingClientRect().height>=44)""")
                dest = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(dest), animations="disabled")
                rows.append(
                    f"| {dest.name} | UI-001/{state} | {width}×{height} | 1x | "
                    f"{sha(dest)} | HTML设计导出，非原生验收 |"
                )
                audits.append({"state": state, "viewport": [width, height], "status": "PASS"})
            page.evaluate("window.designShow('settings-workday')")
            assert page.locator(".body").inner_text().count("按中国大陆法定安排") == 0
            assert page.get_by_label("开始时间").input_value() == "18:00"
            page.keyboard.press("Escape")
            assert page.locator(".mask").count() == 0
            page.close()
        browser.close()
    source = SOURCE.relative_to(ROOT)
    task = "specs/active/FEAT-001-WORKDAY-COPY-CLEANUP.md#SPEC-20261105-WORKDAY-COPY-01"
    manifest.write_text(
        f"""# UI-001 — {HERE.name}

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {task}
- Frontend spec path: {HERE.relative_to(ROOT)}/FRONTEND-SPEC.md
- Editable design source path(s): {source}
- Editable source SHA-256: {source}={sha(SOURCE)}
- Prototype generated/updated at: 2026-11-05
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING；本具体Spec01与DREV03待用户审阅。
- Superseded by: N/A

Chrome {version} / macOS系统字体 / font scale100% / DPR1。
8态×3视口=24张HTML导出；不替代原生三视口、真机或可访问性验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    (HERE / "render-report.json").write_text(
        json.dumps(
            {
                "source_sha256": sha(SOURCE),
                "exports": audits,
                "interactions": "PASS: form fields retained, redundant rule absent, close/focus",
                "native_acceptance": "NOT_RUN",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(f"DESIGN_EXPORTS={len(rows)}; VIEWPORTS=3; HTML_ONLY")


if __name__ == "__main__":
    main()
