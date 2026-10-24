"""Export and exercise the isolated FEAT-012 HTML candidate; no business API calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = HERE / "index.html"
OUT = HERE.parents[1] / "snapshots" / "UI-018" / HERE.name
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
TASK_SPEC = "specs/active/FEAT-012-FOOTPRINTS-UI-COPY.md#SPEC-20261018-FOOTPRINTS-UI-COPY-01"
STATES = (
    "records",
    "timeline",
    "empty",
    "import",
    "consent",
    "importing",
    "review",
    "batch",
    "confirm",
    "saved",
    "playback",
    "paused",
    "lit",
    "world",
    "place",
    "failed",
    "unknown",
    "denied",
    "viewer",
    "map-error",
    "ai-settings",
    "archived",
    "photo-edit",
    "photo-delete",
    "expired",
    "draft-delete",
    "photo",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise RuntimeError("Approved snapshots are immutable; create a new DREV.")
    OUT.mkdir(parents=True, exist_ok=True)
    exports, rows = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome", args=["--disk-cache-size=1", "--media-cache-size=1"]
        )
        for state in STATES:
            for width, height in VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    reduced_motion="reduce",
                )
                errors = []
                page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))
                page.goto(f"{SOURCE.as_uri()}?capture=1&state={state}")
                page.evaluate("document.fonts.ready")
                if state == "unknown":
                    page.locator(".review-list").evaluate(
                        "el => { el.scrollTop = el.scrollHeight; }"
                    )
                rects = page.evaluate("""() => ({
                  width: document.documentElement.scrollWidth,
                  controls: [...document.querySelectorAll('#phone button,#phone input')]
                    .filter(n=>n.type!=='checkbox' && n.getBoundingClientRect().width>0)
                    .map(n=>{const r=n.getBoundingClientRect();return {
                      name:n.getAttribute('aria-label')||n.textContent.trim(),
                      x:r.x,y:r.y,w:r.width,h:r.height,
                      dialog:!!n.closest('[role=dialog]')};})
                })""")
                assert not errors, (state, errors)
                assert rects["width"] <= width, (state, width, rects)
                for r in rects["controls"]:
                    assert r["w"] >= 43.9 and r["h"] >= 43.9, (state, width, r)
                    assert r["x"] >= -0.1 and r["x"] + r["w"] <= width + 0.1, (state, width, r)
                    if r["dialog"]:
                        assert r["y"] >= 0, (state, width, r)
                critical = page.locator(
                    ".footbar button,.sheet-actions button,"
                    ".player-controls button,.player-controls input"
                )
                for i in range(critical.count()):
                    r = critical.nth(i).bounding_box()
                    assert r and r["y"] >= 0 and r["y"] + r["height"] <= height - 14, (
                        state,
                        width,
                        r,
                    )
                filename = f"{state}-{width}x{height}.png"
                page.screenshot(path=str(OUT / filename))
                rows.append(
                    f"| {filename} | UI-018/{state} | {width}×{height} | 1x | "
                    f"{sha(OUT / filename)} | HTML设计；非原生验收 |"
                )
                exports.append(
                    {
                        "state": state,
                        "viewport": [width, height],
                        "console_errors": errors,
                        "dom": rects,
                    }
                )
                page.close()
        # Exercise actual controls, not just direct state URLs.
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(f"{SOURCE.as_uri()}?capture=1")
        page.get_by_role("button", name="导入照片", exact=True).click()
        page.get_by_role("button", name="使用 4 张示例照片").click()
        page.get_by_label("同意处理这批照片的时间和位置信息").check()
        page.get_by_label("AI 辅助补地点（可选）").check()
        page.get_by_role("button", name="开始整理", exact=True).click()
        page.get_by_role("button", name="确认选中的 6 张").wait_for()
        assert page.locator(".review-card").count() == 8
        assert page.locator(".source.ai").count() == 2
        page.get_by_role("button", name="确认选中的 6 张").click()
        page.get_by_label("已核对日期、地点，确认孩子实际到访").check()
        page.get_by_role("button", name="确认并加入足迹").click()
        assert page.get_by_text("已入档", exact=True).is_visible()
        page.get_by_role("button", name="查看时间线", exact=True).click()
        assert page.locator("[data-album-count='46']").is_visible()
        page.get_by_role("tab", name="轨迹回放").click()
        assert page.locator(".map-canvas").get_attribute("data-camera") == "paris"
        page.get_by_role("button", name="播放轨迹", exact=True).click()
        page.get_by_role("button", name="暂停回放", exact=True).click()
        page.get_by_label("轨迹时间进度").fill("2")
        assert page.locator(".map-canvas").get_attribute("data-camera") == "tokyo"
        page.get_by_role("tab", name="地图点亮").click()
        page.get_by_role("button", name="世界", exact=True).click()
        assert page.get_by_text("全球足迹", exact=True).is_visible()
        page.get_by_role("button", name="东亚 · 5城，展开地点列表").click()
        assert page.get_by_role("dialog", name="这个区域的足迹").is_visible()
        page.get_by_role("button", name="东京 · 上野公园").click()
        assert page.get_by_role("dialog", name="上野公园").is_visible()
        page.keyboard.press("Escape")
        page.reload()
        page.get_by_role("button", name="足迹设置", exact=True).click()
        assert page.locator("#setting-ai").is_checked()
        page.locator("#setting-ai").uncheck()
        page.get_by_role("button", name="保存设置", exact=True).click()
        page.reload()
        page.get_by_role("button", name="导入照片", exact=True).click()
        page.get_by_role("button", name="使用 4 张示例照片").click()
        page.get_by_role("button", name="确认选中的 3 张").wait_for()
        assert page.locator(".review-card").count() == 6
        assert page.locator(".source.ai").count() == 0
        assert page.get_by_text("故宫博物院 · 北京", exact=True).is_visible()
        page.evaluate("resetting=true;localStorage.clear()")
        page.goto(f"{SOURCE.as_uri()}?capture=1&state=review")
        page.get_by_role("button", name="修改第4张照片时间和地点").click()
        page.locator("#edit-date").fill("2026-10-02")
        page.locator("#edit-place").fill("北京 · 北海公园")
        page.get_by_role("button", name="保存修改", exact=True).click()
        assert page.get_by_text("北京 · 北海公园", exact=True).is_visible()
        page.reload()
        assert page.get_by_text("北京 · 北海公园", exact=True).is_visible()
        page.get_by_role("button", name="全选", exact=True).click()
        page.get_by_role("button", name="确认选中的 4 张").click()
        assert page.get_by_role("dialog", name="确认入档").is_visible()
        page.evaluate("resetting=true;localStorage.clear()")
        page.goto(f"{SOURCE.as_uri()}?capture=1")
        page.get_by_role("button", name="查看故宫博物院照片", exact=True).first.click()
        page.get_by_role("button", name="下一张照片", exact=True).click()
        assert page.get_by_text("2 / 4", exact=True).is_visible()
        page.get_by_role("button", name="上一张照片", exact=True).click()
        page.get_by_role("button", name="修改日期 / 地点", exact=True).click()
        page.locator("#edit-date").fill("2026-10-02")
        page.get_by_role("button", name="保存修改", exact=True).click()
        page.get_by_role("tab", name="地图点亮").click()
        assert page.get_by_role("button", name="北京，来过3天，8张照片").is_visible()
        page.get_by_role("button", name="北京，来过3天，8张照片").click()
        page.get_by_role("button", name="2026.10.02 1 张照片").click()
        page.get_by_role("button", name="删除这张照片", exact=True).click()
        page.get_by_role("button", name="确认删除这张照片", exact=True).click()
        assert page.locator("[data-album-count='39']").is_visible()
        page.get_by_role("tab", name="地图点亮").click()
        assert page.get_by_role("button", name="北京，来过2天，7张照片").is_visible()
        page.evaluate("resetting=true;localStorage.clear()")
        page.goto(f"{SOURCE.as_uri()}?capture=1&state=archived")
        assert page.get_by_role("button", name="导入照片", exact=True).count() == 0
        page.get_by_role("button", name="1 张待核对", exact=False).click()
        page.get_by_role("button", name="确认选中的 1 张").click()
        page.get_by_label("已核对日期、地点，确认孩子实际到访").check()
        page.get_by_role("button", name="确认并加入足迹").click()
        page.evaluate("resetting=true;localStorage.clear()")
        page.goto(f"{SOURCE.as_uri()}?capture=1&state=review")
        page.evaluate("demoNow=SAMPLE_NOW+WEEK-1;purgeExpired();render()")
        assert page.locator(".review-card").count() == 3
        page.evaluate("demoNow=SAMPLE_NOW+WEEK;purgeExpired();navigate('expired')")
        assert page.get_by_text("草稿已到期", exact=True).is_visible()
        page.get_by_role("button", name="查看时间线", exact=True).click()
        assert page.locator("[data-album-count='40']").is_visible()
        page.evaluate("document.body.classList.remove('capture')")
        page.set_viewport_size({"width": 1600, "height": 1040})
        page.get_by_role("button", name="重置演示数据", exact=True).click()
        page.wait_for_load_state()
        assert page.locator("[data-album-count='40']").is_visible()
        page.get_by_role("button", name="删除草稿", exact=True).click()
        page.get_by_role("button", name="确认删除草稿", exact=True).click()
        assert page.locator(".review-card").count() == 3
        page.reload()
        page.get_by_role("button", name="3 张待核对", exact=False).click()
        assert page.locator(".review-card").count() == 3
        page.close()
        desktop = browser.new_page(
            viewport={"width": 1600, "height": 1040}, reduced_motion="reduce"
        )
        desktop.goto(SOURCE.as_uri())
        desktop.evaluate("document.fonts.ready")
        desktop.screenshot(path=str(OUT / "desktop-1600x1040.png"))
        rows.append(
            "| desktop-1600x1040.png | review workbench | 1600×1040 | 1x | "
            f"{sha(OUT / 'desktop-1600x1040.png')} | 桌面评审工作台，非额外小程序视口 |"
        )
        desktop.close()
        browser.close()
    source = SOURCE.relative_to(ROOT)
    manifest.write_text(
        f"""# UI-018 — {HERE.name} 候选设计清单

- Status: AWAITING_APPROVAL
- UI ID: UI-018
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK_SPEC}
- Frontend spec path: {HERE.relative_to(ROOT)}/FRONTEND-SPEC.md
- Editable design source path(s): {source}
- Editable source SHA-256: {source}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-18
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING — 用户要求删除冗余提示；本次Spec/DREV精简候选待确认。
- Superseded by: N/A

## Candidate scope

{len(STATES)}个HTML状态，全部覆盖320×568、390×844、430×932。
合计{len(STATES) * len(VIEWPORTS)}张手机PNG，另附1张桌面评审工作台。
照片、孩子、时间、地点均为虚构示例，照片用内嵌SVG插画占位。
地图仅为坐标点位示意，无真实底图、行政边界、道路、定位或地理检索服务。
完整候选交互和限制见FRONTEND-SPEC.md。批准后源与清单冻结，只能添加Superseded by。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## Verification and gaps

- 浏览器静态导出、无页面JS错误、按钮/文本输入44px、水平边界检查：PASS。
- 示例导入/同意/核对/确认/时间线/回放/暂停/拖动/世界视图：PASS。
- 聚合展开/地点详情、单张修改/全选4张/确认：PASS。
- R3/R4分批追加、AI开启/沿用/关闭、刷新继续、到访日重算、逐张删除、归档收尾与7天边界演示：PASS。
- 主动删除单张草稿、重置后恢复初始示例且不会重新保存已重置内容：PASS。
- 以上仅为隔离HTML设计验证；不证明微信原生节点/地图覆盖层/真机选图/AI/后端可用。
- 本次文案Spec与DREV待批准；主功能Spec04仍VERIFYING，原设计DREV01冻结。
- 原生三视口、字体放大、读屏、iOS/Android、照片与地图服务：NOT_RUN。
""",
        encoding="utf-8",
    )
    (HERE / "render-audit.json").write_text(
        json.dumps(
            {
                "scope": "Isolated HTML prototype only; not native or production acceptance",
                "exports": exports,
                "flow": (
                    "PASS: import/consent/review/confirm/timeline/play/pause/seek/world/"
                    "cluster/place/edit/select-all/batch-append/ai-toggle/reload/"
                    "visit-day-recompute/delete/archived/expiry-boundary"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"DESIGN_EXPORTS={len(exports)}; DOM checks and prototype flow PASS; native NOT_RUN")


if __name__ == "__main__":
    main()
