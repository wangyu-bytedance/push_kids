"""Render candidate design exports and checks, never native acceptance."""

import asyncio
import hashlib
import json
from pathlib import Path

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001" / HERE.name
THEMES = ("original", "garden", "space", "midnight", "ocean", "tech")
SCENES = (
    "reports",
    "records",
    "settings",
    "nested",
    "loading",
    "empty",
    "error",
    "disabled",
    "sheet",
)
SIZES = ((320, 568), (390, 844), (430, 932))


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def production():
    return {
        str(p.relative_to(ROOT)): sha(p)
        for folder in ("apps", "tests", "tools")
        for p in sorted((ROOT / folder).rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    baseline, rows, exports, errors, network = production(), [], [], [], []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=str(
                Path.home()
                / "Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64"
                / "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
            )
        )
        page = await browser.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda req: (
                network.append(req.url) if req.url.startswith(("http:", "https:")) else None
            ),
        )
        base = (HERE / "index.html").as_uri()
        for theme in THEMES:
            for width, height in SIZES:
                await page.set_viewport_size({"width": width, "height": height})
                for scene in SCENES:
                    await page.goto(f"{base}?single=1&theme={theme}&scene={scene}")
                    await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
                    await page.evaluate("document.fonts.ready")
                    geometry = await page.evaluate("""() => {
                      const title=document.querySelector('.report-title');
                      const art=document.querySelector('.hero-art');
                      const range=title&&document.createRange();
                      if(range)range.selectNodeContents(title);
                      const controls=[...document.querySelectorAll('button')]
                        .filter(e=>e.getBoundingClientRect().width);
                      return {
                        overflow:document.documentElement.scrollWidth>innerWidth,
                        title_lines:range&&range.getClientRects().length,
                        title_font:title&&getComputedStyle(title).fontSize,
                        title_clipped:title&&title.scrollWidth>title.clientWidth,
                        hero_ratio:art&&art.getBoundingClientRect().width/art.getBoundingClientRect().height,
                        hero_fit:art&&getComputedStyle(art).objectFit,
                        upload_has_panorama:!!document.querySelector('.upload .hero-art'),
                        small_controls:controls.filter(e=>{
                          const r=e.getBoundingClientRect();
                          return r.width<43.5||r.height<43.5;
                        }).map(e=>e.textContent),
                        failed_images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,
                        cards:[...document.querySelectorAll('.card')].map(e=>getComputedStyle(e).borderTopColor)
                      };
                    }""")
                    geometry.update(theme=theme, scene=scene, viewport=[width, height])
                    assert (
                        not geometry["overflow"]
                        and not geometry["small_controls"]
                        and not geometry["failed_images"]
                    ), geometry
                    if scene == "reports":
                        assert (
                            geometry["title_lines"] == 1
                            and geometry["title_font"] == "24px"
                            and not geometry["title_clipped"]
                        ), geometry
                    if theme != "original":
                        assert abs(geometry["hero_ratio"] - 780 / 304) < 0.001, geometry
                        assert all(c == "rgba(0, 0, 0, 0)" for c in geometry["cards"]), geometry
                    assert not geometry["upload_has_panorama"], geometry
                    rows.append(geometry)
                    file = OUT / f"{theme}-{scene}-{width}x{height}.png"
                    await page.screenshot(path=str(file))
                    exports.append(
                        {
                            "path": str(file.relative_to(ROOT)),
                            "theme": theme,
                            "state": scene,
                            "viewport": [width, height],
                            "sha256": sha(file),
                        }
                    )
        for scene in ("records", "reports"):
            await page.set_viewport_size({"width": 1080, "height": 1280})
            await page.goto(f"{base}?board=1&scene={scene}")
            await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
            file = OUT / f"overview-{scene}.png"
            await page.locator(".board").screenshot(path=str(file))
            box = await page.locator(".board").bounding_box()
            exports.append(
                {
                    "path": str(file.relative_to(ROOT)),
                    "theme": "all",
                    "state": "overview-" + scene,
                    "viewport": [round(box["width"]), round(box["height"])],
                    "sha256": sha(file),
                }
            )
        # Only the design's theme/scene selectors have behavior in this HTML.
        await page.goto(base)
        await page.select_option("#theme", "midnight")
        await page.select_option("#scene", "reports")
        assert await page.locator(".phone").get_attribute("class") == "phone theme-midnight"
        assert await page.locator(".report-title").text_content() == "一点一滴，看得见"
        await browser.close()
    assert not errors and not network, (errors, network)
    assert production() == baseline, "Production/test/tool files changed during design export"
    verification = {
        "status": "DESIGN_HTML_PASS",
        "groups": len(rows),
        "geometry": rows,
        "errors": errors,
        "network_requests": network,
        "selector_interaction": "PASS",
        "production_export_before_after_unchanged": True,
        "native_acceptance": "NOT_RUN",
        "production_file_hashes": baseline,
    }
    (OUT / "verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n"
    )
    sources = [
        {"path": str(f.relative_to(ROOT)), "sha256": sha(f)}
        for f in sorted(HERE.iterdir())
        if f.is_file()
    ]
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "status": "AWAITING_APPROVAL",
                "designRevision": HERE.name,
                "taskSpecRevision": "DESIGN-003-SPEC-01",
                "sources": sources,
                "exports": exports,
                "verificationSha256": sha(OUT / "verification.json"),
                "nativeAcceptance": "NOT_RUN",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    prefix = str(HERE.relative_to(ROOT))
    spec = "specs/active/DESIGN-003-THEME-VISUAL-REFINEMENT.md"
    text = f"""# {HERE.name} — candidate approval manifest

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: {HERE.name}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {spec} / DESIGN-003-SPEC-01
- Frontend spec path: {prefix}/FRONTEND-SPEC.md
- Editable design source path(s): {prefix}/index.html
- Editable source SHA-256: {prefix}/index.html={sha(HERE / "index.html")}
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING — 用户本轮四项反馈授权准备调优，未提前记为具体Spec01和DREV09批准。

本清单只有设计HTML的162组几何与截图，另2张六主题总览；不是生产实现、原生或设备验收。原DREV06/08及已有生产/测试/工具不改。完整源/导出哈希见manifest.json。

## Export manifest

| File | State | Viewport | Scale | SHA-256 |
|---|---|---|---|---|
"""
    for entry in exports:
        text += (
            f"| {Path(entry['path']).name} | {entry['theme']} / {entry['state']} | "
            f"{entry['viewport'][0]}x{entry['viewport'][1]} | 1x | {entry['sha256']} |\n"
        )
    (OUT / "APPROVAL.md").write_text(text)
    print(
        json.dumps(
            {
                "status": "DESIGN_HTML_PASS",
                "groups": len(rows),
                "exports": len(exports),
                "native": "NOT_RUN",
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
