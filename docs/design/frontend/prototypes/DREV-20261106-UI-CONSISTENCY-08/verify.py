"""Export the approved-size design review and test its local interactions."""

import asyncio
import hashlib
import json
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001" / HERE.name
THEMES = ("original", "garden", "space", "midnight", "ocean", "tech")
SIZES = ((320, 568), (390, 844), (430, 932))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def settle(page):
    await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
    await page.evaluate("document.fonts.ready")


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    geometry, interactions, errors, requests = [], [], [], []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda req: (
                requests.append(req.url) if req.url.startswith(("http:", "https:")) else None
            ),
        )
        base = (HERE / "index.html").as_uri()
        for theme in THEMES:
            for width, height in SIZES:
                await page.set_viewport_size({"width": width, "height": height})
                for state in ("closed", "picker", "storage-error"):
                    await page.goto(f"{base}?theme={theme}&state={state}&section=settings")
                    await settle(page)
                    result = await page.evaluate("""() => {
                      const visible=e=>e.getBoundingClientRect().width>0;
                      const nodes=[...document.querySelectorAll('button')].filter(visible);
                      const rect=e=>{
                        const r=e.getBoundingClientRect();
                        return {width:r.width,height:r.height,left:r.left,right:r.right}
                      };
                      return {
                        entryCovered:!document.querySelector('.sheet')&&
                          document.querySelector('#open-picker').getBoundingClientRect().bottom>
                          document.querySelector('.tabbar').getBoundingClientRect().top,
                        overflow:document.documentElement.scrollWidth>innerWidth,
                        smallTargets:nodes.filter(e=>{
                          const r=rect(e);return r.width<43.5||r.height<43.5
                        }).map(e=>e.textContent),
                        outside:nodes.filter(e=>{
                          const r=rect(e);return r.left<-.5||r.right>innerWidth+.5
                        }).map(e=>e.textContent),
                        sheetOutside:!!document.querySelector('.sheet')&&
                          document.querySelector('.sheet').getBoundingClientRect().top<0
                      }
                    }""")
                    result.update(theme=theme, state=state, viewport=[width, height])
                    geometry.append(result)
                    assert (
                        not result["overflow"]
                        and not result["entryCovered"]
                        and not result["smallTargets"]
                        and not result["outside"]
                        and not result["sheetOutside"]
                    ), result
                    await page.screenshot(path=str(OUT / f"{theme}-{state}-{width}x{height}.png"))
            await page.set_viewport_size({"width": 390, "height": 844})
            await page.goto(f"{base}?theme={theme}")
            await page.click("#open-picker")
            target = THEMES[(THEMES.index(theme) + 1) % len(THEMES)]
            await page.click(f'[data-theme="{target}"]')
            await page.click("#close-picker")
            assert await page.evaluate("DESIGN_STATE()") == {
                "current": theme,
                "selected": theme,
                "open": False,
            }
            interactions.append({"case": "cancel-retains-theme", "theme": theme, "result": "PASS"})
            await page.click("#open-picker")
            assert await page.locator("#apply-theme").is_disabled()
            await page.click(f'[data-theme="{target}"]')
            await page.click("#apply-theme")
            assert await page.evaluate("DESIGN_STATE()") == {
                "current": target,
                "selected": target,
                "open": False,
            }
            assert await page.locator(".entry-meta").text_content() == await page.evaluate(
                "THEMES.find(t=>t.id===DESIGN_STATE().current).name"
            )
            interactions.append(
                {
                    "case": "apply-updates-page-and-entry",
                    "theme": theme,
                    "target": target,
                    "result": "PASS",
                }
            )
        await page.goto(f"{base}?theme=not-a-theme")
        assert (await page.evaluate("DESIGN_STATE()"))["current"] == "original"
        interactions.append({"case": "invalid-theme-fallback", "result": "PASS"})
        await page.click("#open-picker")
        await page.keyboard.press("Escape")
        assert not (await page.evaluate("DESIGN_STATE()"))["open"]
        assert await page.evaluate("document.activeElement.id") == "open-picker"
        interactions.append({"case": "escape-and-focus-return", "result": "PASS"})
        await page.click("#open-picker")
        await page.keyboard.press("Shift+Tab")
        assert await page.evaluate("document.activeElement.dataset.theme") == "tech"
        await page.keyboard.press("Tab")
        assert await page.evaluate("document.activeElement.id") == "close-picker"
        interactions.append({"case": "dialog-focus-containment", "result": "PASS"})
        assert not errors and not requests, (errors, requests)
        board = """<html lang="zh-CN"><meta charset="utf-8"><style>
        body{margin:0;padding:28px;background:#e8edee;font:16px sans-serif;color:#1d3436}
        h1{font-size:27px}main{display:grid;grid-template-columns:repeat(6,270px);gap:18px}
        h2{font-size:16px}img{width:270px;border-radius:16px}p{color:#52676b}</style>
        <h1>设置页底部 · 六种界面风格</h1>
        <p>DREV08 / 上：底部设置列表　下：六种风格选择器</p><main>"""
        for state in ("closed", "picker"):
            for theme in THEMES:
                board += (
                    f"<section><h2>{theme} · {state}</h2>"
                    f'<img src="{theme}-{state}-390x844.png"></section>'
                )
        board += "</main></html>"
        (OUT / "board.html").write_text(board)
        await page.set_viewport_size({"width": 1770, "height": 1420})
        await page.goto((OUT / "board.html").as_uri())
        await settle(page)
        await page.screenshot(path=str(OUT / "overview.png"), full_page=True)
        await page.set_viewport_size({"width": 915, "height": 904})
        await page.goto(f"{base}?theme=original&section=settings")
        await settle(page)
        await page.screenshot(path=str(OUT / "browser-915x904.png"))
        await browser.close()
    (OUT / "verification.json").write_text(
        json.dumps(
            {
                "scope": "HTML prototype only; not native product verification",
                "geometry": geometry,
                "interactions": interactions,
                "page_errors": errors,
                "external_requests": requests,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    app_files = sorted(
        p
        for p in (ROOT / "apps").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    baseline = {
        str(p.relative_to(ROOT)): {"sha256": sha(p), "bytes": p.stat().st_size} for p in app_files
    }
    baseline_path = OUT / "production-baseline.json"
    if baseline_path.exists():
        recorded = {
            k: v
            for k, v in json.loads(baseline_path.read_text()).items()
            if "__pycache__" not in k and not k.endswith(".pyc")
        }
        assert recorded == baseline, "Product source changed during design prework"
        baseline_path.write_text(json.dumps(baseline, indent=2))
    else:
        baseline_path.write_text(json.dumps(baseline, indent=2))
    previous = json.loads(
        (HERE.parent / "DREV-20261106-UI-CONSISTENCY-06/production-before.json").read_text()
    )
    assert previous == {k: v["sha256"] for k, v in baseline.items()}, (
        "Unexpected change since DREV06"
    )
    print(
        json.dumps(
            {
                "html_geometry_exports": len(geometry),
                "local_interactions": len(interactions),
                "png_files": len(list(OUT.glob("*.png"))),
                "apps_unchanged_hashes": len(baseline),
                "errors": errors,
                "external_requests": requests,
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
