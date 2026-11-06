"""Render design-only HTML previews. Does not launch or modify the Mini Program."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-02"
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
BOARDS = [
    ("00-direction", "知芽 · 轻盈的陪伴", "第二轮视觉提案 / 清透底色、鲜活绿、轻巧图形。", ["today", "records", "settings"]),
    ("01-settings", "01 / 设置与统一操作", "同样的添加行为，使用同样的按钮。", ["settings", "settings-routines", "daily-form"]),
    ("02-main", "02 / 今日、日程、学习记录", "先看到内容，再完成下一步。", ["today", "calendar", "records"]),
    ("03-learning", "03 / 报表、复习与草稿", "看清时间口径，也保留家长的确认权。", ["reports", "review-inventory", "confirm"]),
    ("04-travel", "04 / 旅行与活动", "照片、日期、地点彼此对应。", ["travel", "travel-review", "activity"]),
    ("05-family", "05 / 家庭与档案", "邀请、权限和档案管理各有明确入口。", ["child", "family-members", "notifications"]),
    ("06-boundaries", "06 / 重要的操作边界", "修改有保护，错误有位置，清理有核对。", ["unsaved", "confirm-error", "delete-confirm"]),
    ("07-access", "07 / 首次进入与家庭协作", "先讲清如何加入，再共享家庭记录。", ["family-onboarding", "family-join", "family-requests"]),
    ("08-states", "08 / 空状态、失败与处理", "让等待、重试和下一步都有依据。", ["empty", "error", "processing"]),
    ("09-forms", "09 / 详情与安排表单", "实际记录和固定安排各自表达。", ["record-detail", "activity-schedule", "travel-plan"]),
    ("10-selectors", "10 / 选择与手动确认", "统一选择层，也保留手动记录路径。", ["child-switch", "grade", "manual-confirm"]),
    ("11-join", "11 / 创建与加入家庭", "称谓、预览和等待状态都清楚。", ["family-create", "family-preview", "join-pending"]),
    ("12-permissions", "12 / 权限与提醒状态", "区分只读、未授权和服务暂不可用。", ["permission", "notifications-unavailable", "channel-unavailable"]),
    ("13-lifecycle", "13 / 加载、保存与资料管理", "从等待到结果，每一步都有状态。", ["loading", "saved", "delete-settings"]),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        page.goto((HERE / "index.html").as_uri())
        scenes = page.evaluate("window.DESIGN_SCENES")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        for width, height in VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            for scene in scenes:
                key = scene["id"]
                page.goto((HERE / "index.html").as_uri() + "?scene=" + key)
                page.wait_for_function("window.DESIGN_READY === true")
                page.evaluate("document.fonts.ready")
                # Default touch preview: dismiss keyboard-only focus rings without activating a control.
                page.mouse.click(width / 2, 60)
                page.wait_for_timeout(60)
                path = OUT / f"{key}-{width}x{height}.png"
                page.screenshot(path=str(path), animations="disabled")
                geometry = page.evaluate("""() => {
                  const controls=[...document.querySelectorAll('button,input,textarea')];
                  const short=controls.filter(el=>el.getBoundingClientRect().height<43.9||el.getBoundingClientRect().width<43.9)
                    .map(el=>({text:el.getAttribute('aria-label')||el.textContent.trim(),height:el.getBoundingClientRect().height,width:el.getBoundingClientRect().width}));
                  const spill=[...document.querySelectorAll('.content *,.footer *,.sheet *,.dialog *')]
                    .filter(el=>el.getBoundingClientRect().width>0 && (el.getBoundingClientRect().right>innerWidth+.5||el.getBoundingClientRect().left<-.5))
                    .map(el=>({tag:el.tagName,text:el.textContent.trim().slice(0,50)}));
                  // Computed-color screening for this solid-surface mockup, not a full accessibility audit.
                  const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number);
                  const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4})
                    .reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
                  const textContrastFailures=[];
                  for(const el of document.querySelectorAll('.phone *')){
                    if(el.closest('[inert]')||el.closest('svg')||el.matches(':disabled'))continue;
                    const direct=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join(' ').trim();
                    if(!direct||!el.getBoundingClientRect().width||getComputedStyle(el).visibility==='hidden')continue;
                    const c=getComputedStyle(el),fg=rgb(c.color);let parent=el,bg;
                    while(parent){const b=rgb(getComputedStyle(parent).backgroundColor);if((b[3]??1)>.99){bg=b;break;}parent=parent.parentElement;}
                    if(!bg)continue;
                    const x=lum(fg),y=lum(bg),ratio=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);
                    const minimum=(parseFloat(c.fontSize)>=24||(parseFloat(c.fontSize)>=18.66&&parseFloat(c.fontWeight)>=700))?3:4.5;
                    if(ratio+.01<minimum)textContrastFailures.push({text:direct.slice(0,40),color:c.color,background:bg.slice(0,3),ratio:Math.round(ratio*100)/100});
                  }
                  return {horizontalOverflow:document.documentElement.scrollWidth>innerWidth,shortControls:short,spilling:spill,textContrastFailures};
                }""")
                checks.append({"scene": key, "viewport": [width, height], **geometry})
                files.append({"path": path.relative_to(ROOT).as_posix(), "scene": key, "viewport": [width, height], "sha256": digest(path)})
            print(f"Rendered {len(scenes)} scenes at {width}×{height}", flush=True)

        # Exercise representative design interactions, without making network requests.
        page.set_viewport_size({"width": 390, "height": 844})
        interactions = []
        page.goto((HERE / "index.html").as_uri() + "?scene=today")
        page.locator('[data-collapse]').first.click()
        interactions.append({"case": "collapse section", "pass": page.locator('[data-collapse]').first.get_attribute('aria-expanded') == 'false'})
        page.goto((HERE / "index.html").as_uri() + "?scene=activity")
        page.get_by_role('button', name='30 分钟', exact=True).click()
        interactions.append({"case": "quick duration updates input", "pass": page.locator('input').input_value() == '30'})
        page.goto((HERE / "index.html").as_uri() + "?scene=daily-form")
        page.locator('input').first.fill('亲子阅读')
        page.get_by_role('button', name='返回', exact=True).click()
        interactions.append({"case": "dirty exit asks before leaving", "pass": page.get_by_role('dialog', name='有修改尚未保存').is_visible()})
        page.get_by_role('button', name='继续编辑', exact=True).click()
        interactions.append({"case": "continue editing preserves value", "pass": page.locator('input').first.input_value() == '亲子阅读'})
        page.get_by_role('button', name='返回', exact=True).click()
        page.get_by_role('button', name='放弃修改', exact=True).click()
        interactions.append({"case": "discard returns to settings", "pass": page.get_by_role('heading', name='设置', exact=True).is_visible()})
        page.goto((HERE / "index.html").as_uri() + "?scene=confirm-error")
        error_field = page.locator('#invalid-item .field-error')
        box = error_field.bounding_box()
        footer_top = page.locator('.footer').bounding_box()['y']
        interactions.append({"case": "field error scrolled above footer", "pass": box['y'] >= 84 and box['y'] + box['height'] <= footer_top})
        page.goto((HERE / "index.html").as_uri() + "?scene=delete-confirm")
        interactions.append({"case": "clear disabled before full name", "pass": page.locator('#delete-final').is_disabled()})
        page.locator('input').fill('小禾')
        interactions.append({"case": "full name enables demo confirmation", "pass": page.locator('#delete-final').is_enabled()})
        page.goto((HERE / "index.html").as_uri() + "?scene=settings")
        page.get_by_role('button', name='切换或管理孩子').click()
        interactions.append({"case": "child selector opens", "pass": page.get_by_role('dialog', name='选择孩子').is_visible()})

        # Check the actual review gallery and the viewport selector too.
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto((HERE / "index.html").as_uri())
        page.locator('[data-review="reports"]').click()
        page.locator('[data-width="320"]').click()
        interactions.append({"case": "gallery selects scene and exact viewport", "pass": page.locator('iframe').get_attribute('width') == '320' and page.locator('iframe').get_attribute('src') == '?scene=reports'})
        gallery_path = OUT / "gallery-1440.png"
        page.screenshot(path=str(gallery_path), full_page=True)
        files.append({"path": gallery_path.relative_to(ROOT).as_posix(), "kind": "review-gallery", "sha256": digest(gallery_path)})

        for key, title, subtitle, keys in BOARDS:
            labels = {s["id"]: s["title"] for s in scenes}
            cards = "".join(f'<section><h2>{labels[s]}</h2><div class="frame"><img src="{s}-390x844.png"></div></section>' for s in keys)
            html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{title}</title>
            <style>*{{box-sizing:border-box}}body{{margin:0;background:#EAF1ED;color:#23392D;font:16px -apple-system,"PingFang SC",sans-serif;padding:40px 44px 28px;width:1350px}}.eyebrow{{font:12px ui-monospace,monospace;letter-spacing:.14em;color:#147D66}}h1{{font:650 32px -apple-system,"PingFang SC",sans-serif;margin:12px 0}}p{{color:#62776B;font-size:16px;margin:12px 0 26px}}main{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}}h2{{font-size:17px;font-weight:500;margin:0 0 12px}}.frame{{border-radius:24px;border:1px solid #D8D5C8;background:#FFFFFF;padding:6px;width:404px;overflow:hidden;box-shadow:0 8px 24px #23392D08}}img{{display:block;width:390px;height:844px;border-radius:18px}}footer{{margin-top:24px;color:#62776B;font-size:13px;line-height:1.6}}</style>
            <div class="eyebrow">ZHIYA · UI REVIEW · DREV 02</div><h1>{title}</h1><p>{subtitle}</p><main>{cards}</main><footer>待评审设计稿 · 390 × 844 · 合成示例数据 · HTML 效果图，尚未修改小程序</footer></html>'''
            board_html = OUT / f"board-{key}.html"
            board_html.write_text(html)
            page.set_viewport_size({"width": 1350, "height": 1120})
            page.goto(board_html.as_uri())
            page.evaluate("document.fonts.ready")
            board_png = OUT / f"board-{key}.png"
            page.screenshot(path=str(board_png), full_page=True)
            files.append({"path": board_png.relative_to(ROOT).as_posix(), "kind": "review-board", "sha256": digest(board_png)})
        browser.close()

    failing = [r for r in checks if r["horizontalOverflow"] or r["shortControls"] or r["spilling"]]
    contrast_failing = [r for r in checks if r["textContrastFailures"]]
    evidence = {"scope": "HTML design preview only; not native Mini Program acceptance; contrast screening excludes inert backgrounds, SVG and disabled controls", "viewportCount": len(VIEWPORTS), "sceneCount": len(scenes), "renderCount": len(checks), "runtimeErrors": errors, "geometryFailures": failing, "textContrastFailures": contrast_failing, "interactions": interactions, "checks": checks}
    (OUT / "verification.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    sources = [p for p in HERE.iterdir() if p.is_file()]
    manifest = {"designRevision": "DREV-20261106-UI-CONSISTENCY-02", "specRevision": "DESIGN-002-SPEC-02", "approvalStatus": "PENDING_REVIEW", "generatedAt": datetime.now(timezone.utc).isoformat(), "sourceOfTruth": "editable local HTML", "viewports": VIEWPORTS, "data": "synthetic examples; no real child photos or family information", "nativeAcceptance": "NOT_RUN", "sources": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in sorted(sources)], "files": files, "verification": {"path": (OUT / "verification.json").relative_to(ROOT).as_posix(), "sha256": digest(OUT / "verification.json")}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"scenes": len(scenes), "screenshots": len(checks), "boards": len(BOARDS), "runtimeErrors": errors, "geometryFailures": len(failing), "textContrastFailures": len(contrast_failing), "failedInteractions": [v for v in interactions if not v['pass']]}, ensure_ascii=False))
    if failing or contrast_failing or errors or any(not item["pass"] for item in interactions):
        raise SystemExit("Design verification has unresolved findings; inspect verification.json")


if __name__ == "__main__":
    main()
