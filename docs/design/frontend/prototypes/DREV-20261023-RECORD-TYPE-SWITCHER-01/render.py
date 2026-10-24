"""Export the selected local title-switcher design; never call business services."""

import hashlib
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = HERE.parents[1] / "snapshots" / "UI-001" / HERE.name
TASK = "specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md#SPEC-20261023-RECORD-TYPE-SWITCHER-01"
APPROVAL = (
    "用户选中“标题切换 · 推荐”后要求“完成这个功能的代码编写”；"
    "保留既有品牌栏和五Tab，原生平台几何单独验收。"
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved snapshots are immutable")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--disk-cache-size=1"])
        for w, h in [(320, 568), (390, 844), (430, 932)]:
            for state in ["learning", "travel", "picker", "long"]:
                page = browser.new_page(viewport={"width": w, "height": h})
                errors = []
                page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
                page.goto(SOURCE.as_uri() + "?state=" + state)
                assert not errors
                assert page.evaluate("document.documentElement.scrollWidth") == w
                for control in page.locator("button:visible").all():
                    r = control.bounding_box()
                    assert r["width"] >= 44 and r["height"] >= 44
                    assert r["x"] >= 0 and r["x"] + r["width"] <= w
                dest = OUT / f"{state}-{w}x{h}.png"
                page.screenshot(path=str(dest))
                rows.append(
                    f"| {dest.name} | UI-001/{state} | {w}×{h} | 1x | {sha(dest)} | "
                    "HTML设计；非原生验收 |"
                )
                page.close()
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(SOURCE.as_uri())
            page.locator("textarea").fill("保留未提交内容")
            for kind in ["travel", "learning"]:
                page.locator("#title").click()
                page.locator(f"[data-type={kind}]").click()
            assert page.locator("textarea").input_value() == "保留未提交内容"
            page.locator("#title").click()
            page.keyboard.press("Escape")
            assert page.locator("#overlay").is_hidden()
            page.close()
        browser.close()
    manifest.write_text(
        f"""# UI-001 — {HERE.name}

- Status: APPROVED
- UI ID: UI-001
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK}
- Frontend spec path: specs/active/FEAT-012-RECORD-TYPE-SWITCHER.md
- Editable design source path(s): {SOURCE.relative_to(ROOT)}
- Editable source SHA-256: {SOURCE.relative_to(ROOT)}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-23
- Approved by: 产品负责人（用户）
- Approved at: 2026-10-23
- Approval evidence: {APPROVAL}
- Superseded by: N/A

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(rows)
        + "\n"
    )
    print("PASS: 12 exports; three-viewport menu and input preservation")


if __name__ == "__main__":
    main()
