"""Render the review board without editing generated pixels or product code."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-04"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    errors, external, checks = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: external.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        for width, height in [(1440, 1000), (390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            page.goto((HERE / "index.html").as_uri())
            page.wait_for_function("window.DESIGN_READY && [...document.images].length===6 && [...document.images].every(i=>i.complete && i.naturalWidth>0)")
            page.evaluate("document.fonts.ready")
            checks.append(page.evaluate("""() => ({viewport:[innerWidth,innerHeight],images:[...document.images].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,height:i.naturalHeight})),horizontalOverflow:document.documentElement.scrollWidth>innerWidth,links:[...document.querySelectorAll('.picture')].map(a=>a.getAttribute('href'))})"""))
            if width == 1440:
                page.screenshot(path=str(OUT / "six-education-worlds-board.png"), full_page=True, animations="disabled")
        browser.close()
    verification = {"scope": "Review-gallery rendering only. Generated screenshots have no interactive UI nodes.", "checks": checks, "javascriptErrors": errors, "externalRequests": external, "nativeAcceptance": "NOT_RUN", "touchGeometry": "NOT_RUN", "contrastAcceptance": "NOT_RUN"}
    (OUT / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
    sources = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)} for path in sorted(HERE.iterdir()) if path.is_file()]
    exports = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)} for path in sorted(OUT.glob("*.png"))]
    manifest = {"designRevision": HERE.name, "taskSpecRevision": "DESIGN-002-SPEC-04", "status": "CONCEPT_PENDING_STYLE_SELECTION", "generatedAt": datetime.now(timezone.utc).isoformat(), "sources": sources, "exports": exports, "verificationSha256": digest(OUT / "verification.json"), "assetsSha256": digest(OUT / "assets.json"), "pixelEditing": "none; generated originals copied byte-for-byte"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    summary = {"images": len(exports), "galleryViewports": [c["viewport"] for c in checks], "horizontalOverflow": any(c["horizontalOverflow"] for c in checks), "javascriptErrors": errors, "externalRequests": external}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors or external or summary["horizontalOverflow"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
