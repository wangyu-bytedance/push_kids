"""Render synthetic design evidence only; never accesses business services or data."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = ROOT / "docs/design/frontend/snapshots/UI-015" / HERE.name
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
TASK = "specs/active/FEAT-013-ANNUAL-GRADE-PROMOTION.md#SPEC-20261024-ANNUAL-GRADE-PROMOTION-02"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved design evidence is immutable")
    OUT.mkdir(parents=True, exist_ok=True)
    rows, audits, interactions = [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", args=["--disable-gpu"])
        version = browser.version
        for width, height in VIEWPORTS:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            errors = []
            page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
            page.goto(SOURCE.as_uri() + "?screen=1&state=annual")
            states = page.evaluate("window.designStates")
            assert len(states) == 19
            for state in states:
                page.evaluate("window.designShow", state)
                assert not errors, errors
                assert page.evaluate("document.documentElement.scrollWidth") == width
                sheet = page.locator(".sheet")
                geometry = sheet.bounding_box() if sheet.count() else None
                if geometry:
                    assert geometry["y"] >= 74 - 1
                    assert geometry["y"] + geometry["height"] <= height + 1
                    assert page.locator("#background").evaluate("e => e.inert")
                for control in page.locator("button:visible,select:visible,input:visible").all():
                    rect = control.bounding_box()
                    assert rect["height"] >= 44 and rect["width"] >= 44, rect
                    assert rect["x"] >= -1 and rect["x"] + rect["width"] <= width + 1
                    if geometry:
                        assert rect["y"] >= -1 and rect["y"] + rect["height"] <= height + 1, (
                            state,
                            rect,
                        )
                if state == "profile-edit":
                    page.locator(".save").scroll_into_view_if_needed()
                    assert page.locator(".save").bounding_box()["y"] + 48 <= height + 1
                    page.evaluate("window.scrollTo(0, 0)")
                dest = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(dest), animations="disabled", timeout=120000)
                rows.append(
                    f"| {dest.name} | UI-015+UI-001/{state} | {width}×{height} | 1x | "
                    f"{sha(dest)} | HTML候选，非原生验收 |"
                )
                audits.append(
                    {
                        "state": state,
                        "viewport": [width, height],
                        "sheet": geometry,
                        "status": "PASS",
                    }
                )
            page.evaluate("window.designShow('annual')")
            page.locator("#grade").select_option(label="二年级")
            assert page.locator("#grade").input_value() == "二年级"
            page.locator(".secondary").click()
            assert page.locator(".child-name").inner_text() == "豆豆"
            assert page.locator(".chip").inner_text() == "小满　⌄"
            page.locator(".primary").click()
            assert page.locator(".primary").is_disabled()
            assert page.locator("#grade").is_disabled()
            page.wait_for_selector(".overlay", state="detached")
            page.evaluate("window.designShow('error')")
            assert page.locator("#grade").input_value() == "四年级"
            assert page.locator(".notice").is_visible()
            page.evaluate("window.designShow('conflict')")
            assert page.locator("#grade").is_disabled()
            page.locator(".primary").click()
            assert page.locator(".old-grade").inner_text() == "已确认：三年级"
            assert page.locator("#grade").count() == 0
            page.evaluate("window.designShow('annual')")
            page.keyboard.press("Escape")
            assert page.locator(".child-name").inner_text() == "豆豆"
            interactions.append(
                {
                    "viewport": [width, height],
                    "status": "PASS",
                    "checks": [
                        "keep-grade",
                        "later-next-child",
                        "global-child-unchanged",
                        "saving-disabled",
                        "failure-retains-input",
                        "conflict-no-overwrite",
                        "escape-next-child",
                    ],
                }
            )
            page.close()
        browser.close()
    source = SOURCE.relative_to(ROOT)
    manifest.write_text(
        f"""# UI-015 / UI-001 — {HERE.name}

- Status: AWAITING_APPROVAL
- UI ID: UI-015
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK}
- Frontend spec path: {HERE.relative_to(ROOT)}/FRONTEND-SPEC.md
- Editable design source path(s): {source}
- Editable source SHA-256: {source}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-24
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING；Q18只确认产品规则，具体Spec/Architecture/DREV待批准。
- Superseded by: N/A

覆盖UI-015与UI-001本功能增量；合成承载背景不扩大批准范围。
Chrome {version} / macOS系统字体 / font scale 100% / DPR 1。
19态×3精确视口=57张。原生picker和微信导航仅示意，非原生/真机证据。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(rows)
        + "\n\n## Pending gates\n\n"
        "- [x] 源/57张导出与SHA已生成；旧批准清单未修改。\n"
        "- [ ] 具体Spec02、Architecture02与DREV01批准。\n"
        "- [ ] 小程序实现、原生三视口、字体放大/读屏、iOS/Android验收。\n",
        encoding="utf-8",
    )
    report = {
        "kind": "synthetic-html-design-only",
        "renderer": "Chrome " + version,
        "base_library": "N/A; self-contained HTML",
        "font_scale": "100%",
        "dpr": 1,
        "source_sha256": sha(SOURCE),
        "exports": audits,
        "interactions": interactions,
        "native_acceptance": "NOT_RUN",
    }
    (HERE / "render-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"DESIGN_EXPORTS={len(rows)}; INTERACTION_SETS={len(interactions)}; HTML_ONLY")


if __name__ == "__main__":
    main()
