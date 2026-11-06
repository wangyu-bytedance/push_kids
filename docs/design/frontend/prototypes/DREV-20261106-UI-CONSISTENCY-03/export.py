"""Export six Settings-page visual candidates. Never accesses production data."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-03"
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    exports, checks, errors, requests, contrast = [], [], [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        page.goto((HERE / "index.html").as_uri())
        variants = page.evaluate("window.STYLE_VARIANTS")
        for width, height in VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            for variant in variants:
                key = variant["id"]
                page.goto((HERE / "index.html").as_uri() + "?style=" + key)
                page.wait_for_function("window.DESIGN_READY === true")
                page.evaluate("document.fonts.ready")
                path = OUT / f"style-{key}-{width}x{height}.png"
                page.screenshot(path=str(path), animations="disabled")
                geometry = page.evaluate("""() => {
                    const controls=[...document.querySelectorAll('button')];
                    const shortControls=controls.filter(el=>el.getBoundingClientRect().width<43.9||el.getBoundingClientRect().height<43.9)
                      .map(el=>({text:el.textContent.trim()||el.getAttribute('aria-label'),width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}));
                    const horizontalOverflow=document.documentElement.scrollWidth>innerWidth || document.querySelector('.content').scrollWidth>document.querySelector('.content').clientWidth;
                    const addButtons=[...document.querySelectorAll('.add')].map(el=>{const c=getComputedStyle(el);return {background:c.backgroundColor,color:c.color,border:c.border,radius:c.borderRadius}});
                    const navTop=document.querySelector('.tabbar').getBoundingClientRect().top;
                    const secondAddBottom=document.querySelectorAll('.add')[1].getBoundingClientRect().bottom;
                    return {shortControls,horizontalOverflow,addButtonsConsistent:addButtons.every(v=>JSON.stringify(v)===JSON.stringify(addButtons[0])),dailyAddVisible:secondAddBottom<=navTop,bodyScrollWidth:document.body.scrollWidth};
                }""")
                checks.append({"style": key, "viewport": [width, height], **geometry})
                if width == 390:
                    result = page.evaluate(r"""() => {
                        const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number);
                        const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
                        const failures=[];let count=0;
                        for(const el of document.querySelectorAll('.app *')){
                            if(el.closest('svg'))continue;
                            const direct=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join(' ').trim();
                            if(!direct||!el.getBoundingClientRect().width)continue;
                            const c=getComputedStyle(el),fg=rgb(c.color);let parent=el,bg;
                            while(parent){const b=rgb(getComputedStyle(parent).backgroundColor);if((b[3]??1)>.99){bg=b;break;}parent=parent.parentElement;}
                            if(!bg)continue;
                            const x=lum(fg),y=lum(bg),ratio=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);
                            const min=(parseFloat(c.fontSize)>=24||(parseFloat(c.fontSize)>=18.66&&parseFloat(c.fontWeight)>=700))?3:4.5;
                            count++;
                            if(ratio+.01<min)failures.push({text:direct,ratio:Math.round(ratio*100)/100,fg:c.color,bg});
                        }
                        return {count,failures};
                    }""")
                    contrast.append({"style": key, **result})
                exports.append({"path": path.relative_to(ROOT).as_posix(), "style": key, "viewport": [width, height], "sha256": digest(path)})
            print(f"Rendered 6 styles at {width}×{height}", flush=True)

        page.set_viewport_size({"width": 1400, "height": 2100})
        page.goto((HERE / "index.html").as_uri())
        page.wait_for_selector("iframe")
        for frame in page.frames[1:]:
            frame.wait_for_function("window.DESIGN_READY === true")
            frame.evaluate("document.fonts.ready")
        page.evaluate("document.fonts.ready")
        board = OUT / "six-styles-board.png"
        page.screenshot(path=str(board), full_page=True, animations="disabled")
        exports.append({"path": board.relative_to(ROOT).as_posix(), "kind": "comparison-board", "sha256": digest(board)})

        interactions = []
        page.set_viewport_size({"width": 390, "height": 844})
        for variant in variants:
            page.goto((HERE / "index.html").as_uri() + "?style=" + variant["id"])
            page.get_by_role("button", name="添加每日任务", exact=True).click()
            toast = page.get_by_role("status").inner_text()
            page.locator(".content").evaluate("el=>el.scrollTop=el.scrollHeight")
            management_visible = page.get_by_role("button", name="数据管理", exact=True).evaluate("el=>{const r=el.getBoundingClientRect();return r.top>=72 && r.bottom<=document.querySelector('.tabbar').getBoundingClientRect().top}")
            selected_tab = page.locator('.tab[aria-current="page"]').inner_text()
            interactions.append({"style": variant["id"], "previewFeedback": "本页用于风格预览" in toast, "managementReachable": management_visible, "selectedTab": selected_tab})
        browser.close()

    verification = {"designRevision": HERE.name, "scope": "Settings only: six independent visual candidates; no native acceptance", "viewports": VIEWPORTS, "checks": checks, "javascriptErrors": errors, "externalRequests": requests, "interactions": interactions}
    (OUT / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
    (OUT / "contrast-screening.json").write_text(json.dumps({"scope": "Computed solid text at 390x844; excludes icons and alpha compositing. Not full accessibility or native acceptance.", "checks": contrast}, ensure_ascii=False, indent=2) + "\n")
    sources = [{"path": file.relative_to(ROOT).as_posix(), "sha256": digest(file)} for file in sorted(HERE.iterdir()) if file.is_file()]
    manifest = {"designRevision": HERE.name, "taskSpecRevision": "DESIGN-002-SPEC-03", "approval": "PENDING_STYLE_SELECTION", "generatedAt": datetime.now(timezone.utc).isoformat(), "sources": sources, "exports": exports, "verificationSha256": digest(OUT / "verification.json"), "contrastScreeningSha256": digest(OUT / "contrast-screening.json")}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    failed = [c for c in checks if c["horizontalOverflow"] or c["shortControls"] or not c["addButtonsConsistent"] or (c["viewport"][0] >= 390 and not c["dailyAddVisible"])]
    contrast_failed = [c for c in contrast if c["failures"]]
    print(json.dumps({"exports": len(exports), "geometryFailures": failed, "contrastFailures": contrast_failed, "javascriptErrors": errors, "externalRequests": requests, "interactions": interactions}, ensure_ascii=False, indent=2))
    if failed or contrast_failed or errors or requests or not all(i["previewFeedback"] and i["managementReachable"] and i["selectedTab"] == "设置" for i in interactions):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
