"""Export the compact grade-dialog proposal; no native or service access."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = ROOT / "docs/design/frontend/snapshots/UI-015" / HERE.name
TASK = (
    "specs/active/FEAT-013-GRADE-DIALOG-SIMPLIFICATION.md"
    "#SPEC-20261024-GRADE-DIALOG-SIMPLIFICATION-01"
)
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
                for control in page.locator("button:visible,select:visible").all():
                    rect = control.bounding_box()
                    assert rect["width"] >= 44 and rect["height"] >= 44, rect
                    assert rect["x"] >= 0 and rect["x"] + rect["width"] <= width + 1
                    assert rect["y"] >= 0 and rect["y"] + rect["height"] <= height + 1
                assert page.locator(".body").evaluate("e=>e.scrollHeight<=e.clientHeight+1")
                for item in page.locator("h1:visible,.message:visible,select:visible").all():
                    assert item.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)") >= 14
                destination = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(destination), animations="disabled")
                rows.append(
                    f"| {destination.name} | UI-015/{state} | {width}×{height} | 1x | "
                    f"{sha(destination)} | HTML候选，非原生验收 |"
                )
                audits.append(
                    {
                        "state": state,
                        "viewport": [width, height],
                        "sheet_height": page.locator(".sheet").bounding_box()["height"],
                        "status": "PASS",
                    }
                )
            page.evaluate("window.designShow('annual')")
            assert page.locator("#grade option").count() == 12
            assert page.locator("#background").evaluate("e=>e.inert")
            page.select_option("#grade", "二年级")
            page.locator(".primary").click()
            assert page.evaluate("window.designEvents.includes('confirm:二年级')")
            assert page.locator("#grade").is_disabled()
            assert page.locator(".secondary").is_disabled()
            page.evaluate("window.designShow('error')")
            assert page.locator("#grade").input_value() == "四年级"
            page.locator(".secondary").click()
            assert page.locator(".overlay").is_hidden()
            page.evaluate("window.designShow('conflict')")
            page.locator(".primary").click()
            assert page.locator(".field").is_hidden()
            assert page.locator(".latest-grade").inner_text() == "三年级"
            if width == 390:
                page.evaluate("window.designShow('annual')")
                page.locator(".sheet").screenshot(path=str(HERE / "preview.png"))
            if width == 320:
                page.evaluate("window.designShow('error')")
                page.locator(".sheet").screenshot(path=str(HERE / "preview-error.png"))
                page.evaluate("window.designShow('long-name')")
                page.locator(".sheet").screenshot(path=str(HERE / "preview-long-name.png"))
            page.close()
        browser.close()
    relative_source = SOURCE.relative_to(ROOT)
    manifest.write_text(
        f"""# UI-015 / UI-001 — {HERE.name}

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
- Approval evidence: PENDING；用户要求精简，尚未批准本具体Spec/Design修订。
- Superseded by: N/A

Chrome {version} / macOS系统字体 / font scale100% / DPR1。
11态×3视口=33张HTML导出。原生picker外观由平台决定；本HTML不证明微信或真机验收。
仅替代五Tab共享年级弹窗的呈现，UI-015档案表单继续沿用DREV01。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(rows)
        + "\n\n## Pending gates\n\n"
        "- [x] 33导出、几何/字体与HTML选择/禁用/失败/最新结果检查。\n"
        "- [ ] 具体Spec01+DREV02批准。\n"
        "- [ ] 生产实现与原生/设备/可访问性验收。\n",
        encoding="utf-8",
    )
    (HERE / "render-report.json").write_text(
        json.dumps(
            {
                "renderer": version,
                "source_sha256": sha(SOURCE),
                "exports": audits,
                "interactions": (
                    "PASS: 12 choices, keep, pending, retry draft, later, "
                    "conflict/latest; three viewports"
                ),
                "native_acceptance": "NOT_RUN",
                "previews": [
                    {"file": name, "sha256": sha(HERE / name), "kind": "element crop"}
                    for name in ["preview.png", "preview-error.png", "preview-long-name.png"]
                ],
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
