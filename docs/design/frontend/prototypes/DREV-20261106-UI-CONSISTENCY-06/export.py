"""Browser-only preview exports. These checks do not constitute native acceptance."""
import argparse
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06"
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
THEMES = ["garden", "space", "midnight", "ocean", "tech"]
GEOMETRY = """() => {
 const width=innerWidth, root=document.querySelector('.phone');
 const horizontal=[...root.querySelectorAll('button,input,textarea,h1,h2,h3,.row,.card,.notice')].filter(e=>{
   const s=getComputedStyle(e),r=e.getBoundingClientRect();
   return !e.closest('[hidden]')&&s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&(r.left < -1 || r.right > width+1);
 }).map(e=>({tag:e.tagName,text:e.textContent.trim().slice(0,45),left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}));
 const smallTargets=[...root.querySelectorAll('button,input,textarea')].filter(e=>{
  const r=e.getBoundingClientRect(); return !e.closest('[hidden]')&&r.width>0&&(r.width<43.5||r.height<43.5);
 }).map(e=>({text:e.getAttribute('aria-label')||e.textContent.trim().slice(0,35),width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}));
 return {horizontal,smallTargets,scrollArea:document.querySelector('.page-scroll').clientHeight,
  bodyOverflow:document.documentElement.scrollWidth>width,theme:document.body.dataset.theme,
  headings:[...root.querySelectorAll('h1')].map(e=>e.textContent),dialog:!!root.querySelector('[role="dialog"]')};
}"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def settle(page):
    await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
    await page.evaluate("() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
    await page.evaluate("document.fonts.ready")


async def run(probe=False):
    OUT.mkdir(parents=True, exist_ok=True)
    errors, external = [], []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, reduced_motion="reduce")
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("request", lambda r: external.append(r.url) if r.url.startswith(("https:", "http:")) else None)
        await page.goto(HERE.joinpath("index.html").as_uri() + "?scene=settings&theme=garden")
        await page.wait_for_function("window.DESIGN_READY === true")
        scenes = await page.evaluate("window.DESIGN_SCENES")
        assert len(scenes) == 65
        checks = []
        for theme in THEMES:
            (OUT / theme).mkdir(exist_ok=True)
        work = [
            (theme, s, w, h)
            for theme in THEMES
            for w, h in ([(390, 844)] if probe else VIEWPORTS)
            for s in scenes
            if not probe or s["id"] in ["today", "settings", "records", "confirm", "daily-presets", "reports"]
        ]
        for index, (theme, scene, width, height) in enumerate(work):
            await page.set_viewport_size({"width": width, "height": height})
            await page.evaluate("([t,s])=>window.setPreview(t,s)", [theme, scene["id"]])
            await settle(page)
            # Export resting pointer states; keyboard focus is checked separately.
            await page.evaluate("document.activeElement?.blur()")
            geom = await page.evaluate(GEOMETRY)
            geom.update(scene=scene["id"], viewport=[width, height])
            checks.append(geom)
            await page.screenshot(path=str(OUT / theme / f"{scene['id']}-{width}x{height}.png"))
            if (index + 1) % 64 == 0:
                print(f"Exported {index + 1}/{len(work)}", flush=True)
        result = {
            "scope": "Editable HTML design only; not native Mini Program acceptance",
            "scenes": scenes,
            "themes": THEMES,
            "checks": checks,
            "javascriptErrors": errors,
            "externalRequests": external,
        }
        (OUT / ("probe.json" if probe else "verification.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        if probe:
            thumb = await browser.new_page(viewport={"width": 1750, "height": 1860}, device_scale_factor=1)
            images = []
            for theme in THEMES:
                for s in ["settings", "records"]:
                    images.append(f'<div><p>{theme} / {s}</p><img src="{(OUT/theme/(s+"-390x844.png")).as_uri()}"></div>')
            await thumb.goto(HERE.joinpath("index.html").as_uri()+"?scene=today")
            await thumb.set_content('<style>body{margin:20px;background:#e8ebe8;font-family:sans-serif}main{display:grid;grid-template-columns:repeat(5,330px);gap:16px}p{font-size:14px}img{width:330px;display:block;border-radius:18px}</style><main>'+"".join(images)+"</main>")
            await thumb.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
            await thumb.screenshot(path=str(OUT/"probe-board.png"), full_page=True)
            await thumb.close()
        else:
            for theme in THEMES:
                for board in ["main", "all"]:
                    await page.set_viewport_size({"width": 2118, "height": 1000})
                    await page.goto(HERE.joinpath("index.html").as_uri()+f"?board={board}&theme={theme}")
                    await page.wait_for_function("window.DESIGN_READY")
                    await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
                    await page.screenshot(path=str(OUT / f"{theme}-{board}.png"), full_page=True)
            await page.goto(HERE.joinpath("index.html").as_uri()+"?board=overview")
            await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
            await page.screenshot(path=str(OUT/"overview.png"), full_page=True)
        await browser.close()
    problems=[c for c in checks if c["horizontal"] or c["smallTargets"] or c["bodyOverflow"]]
    print(json.dumps({"probe":probe,"exports":len(work),"geometryProblems":len(problems),"firstProblems":problems[:4],"javascriptErrors":errors,"externalRequests":external},ensure_ascii=False),flush=True)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--probe",action="store_true")
    asyncio.run(run(parser.parse_args().probe))
