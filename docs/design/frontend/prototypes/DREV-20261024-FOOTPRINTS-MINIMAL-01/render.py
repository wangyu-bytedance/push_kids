"""Render only the local unapproved design; no business services are called."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = HERE.parents[1] / "snapshots" / "UI-018" / HERE.name
STATES = [
    "overview",
    "empty",
    "actions",
    "settings",
    "archived",
    "viewer",
    "long",
    "standalone",
]
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
TASK = "specs/active/FEAT-012-FOOTPRINTS-MINIMAL-UI.md#SPEC-20261024-FOOTPRINTS-MINIMAL-UI-01"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved exports are immutable")
    OUT.mkdir(parents=True, exist_ok=True)
    exports, audits, interactions = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--disable-gpu"])
        for width, height in VIEWPORTS:
            for state in STATES:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors, requests = [], []
                page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                page.on("request", lambda r, requests=requests: requests.append(r.url))
                page.goto(SOURCE.as_uri() + "?state=" + state)
                assert not errors, errors
                assert all(url.startswith("file:") for url in requests), requests
                assert page.evaluate("document.documentElement.scrollWidth") == width
                assert page.locator("h1").count() == 0
                assert page.locator(".background").inner_text().count("足迹设置") == 0
                assert "查看已归档孩子" not in page.locator(".background").inner_text()
                more = page.locator("#more").bounding_box()
                assert more["width"] >= 44 and more["height"] >= 44
                for control in page.locator("button:visible, .child").all():
                    rect = control.bounding_box()
                    assert rect["width"] >= 44 and rect["height"] >= 44, rect
                    assert rect["x"] >= -1
                    assert rect["x"] + rect["width"] <= width + 1
                if state == "settings":
                    sheet = page.locator(".settings-sheet").bounding_box()
                    assert sheet["height"] <= 260, sheet
                    text = page.get_by_role("dialog").inner_text()
                    assert "AI 地点候选" in text and "保存设置" in text
                    assert all(
                        word not in text for word in ["7天", "24小时", "原件", "火山", "浏览版"]
                    )
                else:
                    sheet = None
                if state in ["overview", "empty", "long", "standalone"]:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    upload = page.locator("#import").bounding_box()
                    assert upload["height"] == 48
                    assert upload["y"] >= 0
                    if state != "standalone":
                        nav = page.locator(".nav").bounding_box()
                        assert nav["y"] - upload["y"] - upload["height"] >= 8
                dest = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(dest), animations="disabled", timeout=60000)
                exports.append(
                    f"| {dest.name} | UI-018/{state} | {width}×{height} | 1x | "
                    f"{sha(dest)} | HTML设计，非原生验收 |"
                )
                audits.append(
                    {
                        "state": state,
                        "viewport": [width, height],
                        "status": "PASS",
                        "more": more,
                        "settings": sheet,
                        "page_errors": errors,
                        "network_requests": 0,
                    }
                )
                page.close()

            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(SOURCE.as_uri())
            page.get_by_role("button", name="更多操作", exact=True).click()
            page.get_by_role("button", name="足迹设置", exact=True).click()
            toggle = page.get_by_role("switch", name="AI 地点候选")
            assert toggle.get_attribute("aria-checked") == "false"
            toggle.click()
            page.get_by_role("button", name="保存设置", exact=True).click()
            assert page.get_by_role("dialog").count() == 0
            assert page.locator("#more").evaluate("e => e === document.activeElement")
            page.locator("#more").click()
            page.get_by_role("button", name="足迹设置", exact=True).click()
            assert page.get_by_role("switch").get_attribute("aria-checked") == "true"
            page.get_by_role("switch").click()
            page.keyboard.press("Tab")
            page.keyboard.press("Tab")
            assert page.locator("#close").evaluate("e => e === document.activeElement")
            page.keyboard.press("Escape")
            assert page.evaluate("model.ai") is True
            page.locator("#more").click()
            page.get_by_role("button", name="已归档孩子", exact=True).click()
            page.get_by_role("button", name="取消", exact=True).click()
            assert page.evaluate("model.name") == "小禾"
            page.locator("#more").click()
            page.get_by_role("button", name="已归档孩子", exact=True).click()
            page.locator("#choose-archive").click()
            assert page.evaluate("model.archived") is True
            assert page.locator("#import").count() == 0
            assert "已归档" in page.locator(".child-name").inner_text()
            page.goto(SOURCE.as_uri() + "?state=viewer")
            assert page.locator("#import").count() == 0
            page.locator("#more").click()
            assert page.get_by_role("dialog").get_attribute("aria-label") == "已归档孩子"
            assert page.get_by_role("button", name="足迹设置", exact=True).count() == 0
            page.keyboard.press("Escape")
            interactions.append({"viewport": [width, height], "status": "PASS"})
            page.close()
        browser.close()

    relative = SOURCE.relative_to(ROOT)
    metadata = f"""# UI-001 / UI-018 — {HERE.name}

- Status: AWAITING_APPROVAL
- UI ID: UI-018
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK}
- Frontend spec path: {(HERE / "FRONTEND-SPEC.md").relative_to(ROOT)}
- Editable design source path(s): {relative}
- Editable source SHA-256: {relative}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-24
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING；用户已明确简洁方向，具体Spec01/DREV01尚未批准。
- Superseded by: N/A

仅设计候选；所有人物、数字与图像均为合成内容，无业务请求。
HTML原生菜单模拟不等于微信原生或真机验收；生产代码未改。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
    manifest.write_text(metadata + "\n".join(exports) + "\n", encoding="utf-8")
    (HERE / "render-audit.json").write_text(
        json.dumps(
            {
                "design_revision": HERE.name,
                "source_sha256": sha(SOURCE),
                "status": "PASS",
                "exports": audits,
                "interactions": interactions,
                "native_status": "NOT_RUN",
                "production_modified": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"PASS: {len(exports)} exports; {len(interactions)} viewport interactions")


if __name__ == "__main__":
    main()
