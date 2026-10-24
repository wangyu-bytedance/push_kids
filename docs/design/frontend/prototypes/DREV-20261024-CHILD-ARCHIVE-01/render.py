"""Render the proposed archive row; no native or business-service access."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = ROOT / "docs/design/frontend/snapshots/UI-015" / HERE.name
TASK = "specs/active/BUG-033-CHILD-ARCHIVE-UI.md#BUG-SPEC-20261024-CHILD-ARCHIVE-UI-01"
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved evidence is immutable")
    OUT.mkdir(parents=True, exist_ok=True)
    rows, audits = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", args=["--disable-gpu"])
        version = browser.version
        for width, height in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
            page.goto(SOURCE.as_uri())
            for state in page.evaluate("window.designStates"):
                page.evaluate("window.designShow", state)
                assert not errors, errors
                assert page.evaluate("document.documentElement.scrollWidth") == width
                for control in page.locator("button:visible").all():
                    rect = control.bounding_box()
                    assert rect["width"] >= 44 and rect["height"] >= 44, rect
                    assert rect["x"] >= 0 and rect["x"] + rect["width"] <= width + 1
                    assert rect["y"] >= 0 and rect["y"] + rect["height"] <= height + 1
                texts = page.locator(".description:visible,.pending:visible,.error:visible")
                for text in texts.all():
                    assert text.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)") >= 14
                destination = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(destination), animations="disabled")
                rows.append(
                    f"| {destination.name} | UI-015/{state} | {width}×{height} | 1x | "
                    f"{sha(destination)} | HTML候选，非原生验收 |"
                )
                audits.append({"state": state, "viewport": [width, height], "status": "PASS"})
            page.evaluate("window.designShow('unfinished')")
            page.locator(".archive-row").click()
            assert page.locator(".overlay").is_visible()
            assert page.locator("#background").evaluate("e=>e.inert")
            assert "3 条" in page.locator("#dialog-copy").inner_text()
            page.keyboard.press("Escape")
            assert page.locator(".overlay").is_hidden()
            assert page.locator(".archive-row").evaluate("e=>e===document.activeElement")
            page.locator(".archive-row").click()
            page.locator("#confirm").click()
            assert page.locator(".archive-row").is_disabled()
            if width == 390:
                page.evaluate("window.designShow('active')")
                page.locator("#focus").screenshot(path=str(HERE / "preview.png"))
            page.close()
        browser.close()
    relative_source = SOURCE.relative_to(ROOT)
    manifest.write_text(
        f"""# UI-015 — {HERE.name}

- Status: AWAITING_APPROVAL
- UI ID: UI-015
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK}
- Frontend spec path: {HERE.relative_to(ROOT)}/FRONTEND-SPEC.md
- Editable design source path(s): {relative_source}
- Editable source SHA-256: {relative_source}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-24
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING；用户指出截图问题，尚未批准本具体修订。
- Superseded by: N/A

Chrome {version} / macOS系统字体 / font scale100% / DPR1。
7态×3视口=21张HTML导出。原生确认框及表单上下文仅示意，不是微信或真机验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(rows)
        + "\n\n## Pending gates\n\n"
        "- [x] 21导出/几何/字体与HTML取消/焦点/禁用检查。\n"
        "- [ ] 具体Spec01+DREV01批准。\n"
        "- [ ] 生产实现与原生/真机/可访问性验收。\n",
        encoding="utf-8",
    )
    (HERE / "render-report.json").write_text(
        json.dumps(
            {
                "renderer": version,
                "source_sha256": sha(SOURCE),
                "exports": audits,
                "interactions": "PASS: cancel-focus, count, disabled; all viewports",
                "native_acceptance": "NOT_RUN",
                "preview": {
                    "file": "preview.png",
                    "sha256": sha(HERE / "preview.png"),
                    "kind": "390x844 viewport / element crop only",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"DESIGN_EXPORTS={len(rows)}; VIEWPORTS=3; HTML_ONLY")


if __name__ == "__main__":
    main()
