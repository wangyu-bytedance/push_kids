"""Export the unapproved local design; never invoke business services."""

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = HERE.parents[1] / "snapshots" / "UI-001" / HERE.name
STATES = [
    "travel",
    "learning",
    "long",
    "single",
    "types",
    "learning-types",
    "long-types",
    "today",
    "from-learning",
    "travel-bottom",
]
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
TASK = "specs/active/BUG-032-RECORD-ENTRY-CONTEXT.md#BUG-SPEC-20261024-RECORD-ENTRY-05"


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
                errors = []
                page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
                initial = {
                    "from-learning": "travel",
                    "types": "travel",
                    "learning-types": "learning",
                    "long-types": "long",
                    "travel-bottom": "travel",
                }.get(state, state)
                page.goto(SOURCE.as_uri() + "?state=" + initial)
                if state == "travel-bottom":
                    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                if state in ["types", "learning-types", "long-types"]:
                    page.locator("#record-title").click()
                if state == "from-learning":
                    page.locator('[data-route="today"]').click()
                    page.locator("#record-learning").click()
                    assert page.locator("#learning").is_visible()
                    assert page.evaluate("model.entry") == "learning"
                assert not errors, errors
                for art in page.locator(".upload-art").all():
                    art.evaluate("img => img.decode()")
                    assert art.evaluate("img => img.naturalWidth > 0")
                upload_geometry = None
                if page.locator("#travel").count():
                    upload = page.get_by_role("button", name="导入照片", exact=True)
                    assert upload.count() == 1
                    assert page.locator("#travel .subhead button").count() == 0
                    upload_geometry = upload.bounding_box()
                    assert 48 <= upload_geometry["height"] <= 49
                    travel_width = page.locator("#travel").bounding_box()["width"]
                    assert abs(upload_geometry["width"] - travel_width) <= 1
                    content = page.locator("#travel .empty").bounding_box()
                    assert upload_geometry["y"] - content["y"] - content["height"] >= 20
                    assert upload.locator("img, .upload-art").count() == 0
                    if state == "travel-bottom":
                        nav = page.locator(".nav").bounding_box()
                        assert upload_geometry["y"] >= 0
                        assert nav["y"] - upload_geometry["y"] - upload_geometry["height"] >= 8
                        assert upload.evaluate(
                            "e => {const r=e.getBoundingClientRect(); return "
                            "document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)"
                            ".closest('button')===e;}"
                        )
                assert page.locator(".date-filter").count() == 0
                for label in ["开始日期", "结束日期", "全部"]:
                    assert page.get_by_role("button", name=label, exact=True).count() == 0
                assert page.evaluate("document.documentElement.scrollWidth") == width
                menu_geometry = None
                if page.locator(".type-menu").count():
                    title_rect = page.locator("#record-title").bounding_box()
                    menu_geometry = page.locator(".type-menu").bounding_box()
                    assert abs(menu_geometry["x"] - title_rect["x"]) <= 1
                    assert abs(menu_geometry["y"] - title_rect["y"] - title_rect["height"] - 8) <= 1
                    assert menu_geometry["y"] + menu_geometry["height"] < height - 80
                    assert page.locator(".nav").is_visible()
                    assert page.locator(".menu-dismiss").evaluate(
                        "e => getComputedStyle(e).backgroundColor === 'rgba(0, 0, 0, 0)'"
                    )
                    assert page.get_by_role("menuitemradio", checked=True).count() == 1
                    assert page.get_by_role("dialog").count() == 0
                controls = page.locator("button:visible, .child-chip")
                for control in controls.all():
                    rect = control.bounding_box()
                    assert rect["width"] >= 44 and rect["height"] >= 44, rect
                    assert rect["x"] >= -1 and rect["x"] + rect["width"] <= width + 1, rect
                heading = page.locator(".heading")
                geometry = None
                if heading.count():
                    title = page.locator("#record-title").bounding_box()
                    chip = page.locator(".child-chip").bounding_box()
                    if chip["y"] >= title["y"] + title["height"]:
                        assert chip["y"] - title["y"] - title["height"] >= 8
                    else:
                        assert chip["x"] - title["x"] - title["width"] >= 8
                    assert page.locator(".child-name").evaluate(
                        "e => e.scrollWidth <= e.clientWidth + 1"
                    )
                    geometry = {"title": title, "child": chip}
                dest = OUT / f"{state}-{width}x{height}.png"
                page.screenshot(path=str(dest), animations="disabled", timeout=120000)
                exports.append(
                    f"| {dest.name} | UI-001/{state} | {width}×{height} | 1x | "
                    f"{sha(dest)} | HTML设计，非原生验收 |"
                )
                audits.append(
                    {
                        "state": state,
                        "viewport": [width, height],
                        "geometry": geometry,
                        "status": "PASS",
                        "page_errors": errors,
                        "date_filter_removed": True,
                        "dropdown_geometry": menu_geometry,
                        "upload_geometry": upload_geometry,
                    }
                )
                page.close()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(SOURCE.as_uri() + "?state=travel")
            page.locator('[data-route="today"]').click()
            page.locator('[data-route="records"]').click()
            assert page.evaluate("model.type") == "travel"
            page.locator('[data-route="today"]').click()
            page.locator("#record-learning").click()
            assert page.evaluate("model.type") == "learning"
            page.locator("textarea").fill("合成的未提交学习内容")
            for kind in ["travel", "learning"]:
                page.locator("#record-title").click()
                page.locator(f'[data-type="{kind}"]').click()
            assert page.locator("textarea").input_value() == "合成的未提交学习内容"
            page.locator("#record-title").click()
            page.keyboard.press("Escape")
            assert page.locator(".type-menu").count() == 0
            assert page.locator("#record-title").evaluate("e => e === document.activeElement")
            page.locator("#record-title").click()
            page.locator("#record-title").click()
            assert page.locator(".type-menu").count() == 0
            page.locator("#record-title").click()
            page.mouse.click(width - 4, height / 2)
            assert page.locator(".type-menu").count() == 0
            page.locator("#record-title").click()
            page.keyboard.press("Home")
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            assert page.evaluate("model.type") == "travel"
            assert page.locator("#record-title").evaluate("e => e === document.activeElement")
            page.locator("#record-title").click()
            page.keyboard.press("Tab")
            assert page.locator(".type-menu").count() == 0
            assert page.locator("select").evaluate("e => e === document.activeElement")
            interactions.append(
                {
                    "viewport": [width, height],
                    "ordinary_tab_remembers_travel": True,
                    "learning_entry_chooses_learning": True,
                    "unsent_text_retained": True,
                    "escape_restores_focus": True,
                    "trigger_toggle_closes": True,
                    "outside_click_closes": True,
                    "keyboard_selects_type": True,
                    "tab_leaves_menu": True,
                }
            )
            page.close()
        browser.close()
    source = SOURCE.relative_to(ROOT)
    manifest.write_text(
        f"""# UI-001 / UI-018 — {HERE.name}

- Status: AWAITING_APPROVAL
- UI ID: UI-001
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
- Approval evidence: PENDING，待确认Spec05 + DREV01；顶部下拉、默认全部、下方导入按钮。
- Superseded by: N/A

合成内容；仅设计验证，未修改业务源码，不代表原生/真机或生产实施验收。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
"""
        + "\n".join(exports)
        + "\n",
        encoding="utf-8",
    )
    (HERE / "render-audit.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "scope": "CANDIDATE_HTML_ONLY",
                "date": "2026-10-24",
                "source_sha256": sha(SOURCE),
                "exports": audits,
                "interactions": interactions,
                "native_geometry": "NOT_RUN",
                "production_code_modified": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("PASS: 30 exports, three-viewport import button/dropdown/navigation; native NOT_RUN")


if __name__ == "__main__":
    main()
