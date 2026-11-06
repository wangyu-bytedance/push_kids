"""Verify the six-theme review page and export its board; no production writes."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-05"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    errors, requests, checks, switches = [], [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda r: requests.append(r.url) if r.url.startswith(("http:", "https:")) else None)
        for width, height in [(1440, 1000), (390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            page.goto((HERE / "index.html").as_uri())
            page.wait_for_function("window.DESIGN_READY && [...document.querySelectorAll('.grid img')].length===6 && [...document.querySelectorAll('.grid img')].every(i=>i.complete && i.naturalWidth>0)")
            page.evaluate("document.fonts.ready")
            checks.append(page.evaluate("""() => ({mode:document.body.dataset.mode,viewport:[innerWidth,innerHeight],images:[...document.querySelectorAll('.grid img')].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,height:i.naturalHeight})),horizontalOverflow:document.documentElement.scrollWidth>innerWidth})"""))
            if width == 1440:
                page.screenshot(path=str(OUT / "six-selected-themes-board.png"), full_page=True, animations="disabled")
            page.get_by_role("button", name="单独预览海洋风格", exact=True).click()
            page.wait_for_function("document.body.dataset.mode==='single' && document.body.dataset.selectedTheme==='e'")
            themes = page.evaluate("window.THEME_PREVIEWS")
            for theme in themes:
                page.locator(f'[data-theme="{theme["id"]}"]').click()
                page.wait_for_function("document.querySelector('#single-image').complete && document.querySelector('#single-image').naturalWidth>0")
                result = page.evaluate("""() => ({selected:document.body.dataset.selectedTheme,title:document.querySelector('#single-title').textContent,fallback:document.querySelector('#fallback-name').textContent,src:document.querySelector('#single-image').getAttribute('src'),href:document.querySelector('#original-link').getAttribute('href'),selectedCount:document.querySelectorAll('[data-theme][aria-pressed="true"]').length,horizontalOverflow:document.documentElement.scrollWidth>innerWidth})""")
                result["viewport"] = [width, height]
                result["passed"] = result["selected"] == theme["id"] and result["title"] == theme["name"] and result["fallback"] == theme["fallback"] and result["src"] == result["href"] and result["selectedCount"] == 1 and not result["horizontalOverflow"]
                switches.append(result)
            page.get_by_role("button", name="六版对比", exact=True).click()
            if page.locator("body").get_attribute("data-mode") != "grid":
                raise RuntimeError("Cannot return to comparison mode")
        browser.close()
    verification = {"scope": "Review gallery only; image switching is not native Mini Program theming.", "gridChecks": checks, "themeSwitchChecks": switches, "javascriptErrors": errors, "externalRequests": requests, "nativeAcceptance": "NOT_RUN", "productGeometry": "NOT_RUN", "generatedImageText": "MANUALLY_REVIEWED"}
    (OUT / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
    sources = [{"path": f.relative_to(ROOT).as_posix(), "sha256": digest(f)} for f in sorted(HERE.iterdir()) if f.is_file()]
    exports = [{"path": f.relative_to(ROOT).as_posix(), "sha256": digest(f)} for f in sorted(OUT.glob("*.png"))]
    manifest = {"designRevision": HERE.name, "taskSpecRevision": "DESIGN-002-SPEC-05", "status": "THEME_ROSTER_CONFIRMED_VISUAL_PENDING", "generatedAt": datetime.now(timezone.utc).isoformat(), "sources": sources, "exports": exports, "assetsSha256": digest(OUT / "assets.json"), "verificationSha256": digest(OUT / "verification.json"), "pixelEditing": "none; six generated originals copied byte-for-byte"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"pngs": len(exports), "galleryChecks": len(checks), "themeSwitchChecks": len(switches), "themeSwitchFailures": [s for s in switches if not s["passed"]], "javascriptErrors": errors, "externalRequests": requests}, ensure_ascii=False, indent=2))
    if errors or requests or any(c["horizontalOverflow"] for c in checks) or not all(s["passed"] for s in switches):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
