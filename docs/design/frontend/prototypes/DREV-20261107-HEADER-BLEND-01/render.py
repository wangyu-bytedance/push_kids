"""Build and verify the offline proposal. Browser results are design evidence."""

import base64
import hashlib
import json
import re
import subprocess
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001" / HERE.name
TASK = "specs/active/DESIGN-004-HEADER-BLEND.md / DESIGN-004-SPEC-01"
FEC = "FEC-20261107-AGENT-DEVICE-MATRIX-03"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(path):
    return path.relative_to(ROOT).as_posix()


def build():
    source = (HERE / "source.html").read_text()
    themes = json.loads(
        subprocess.check_output(
            [
                "node",
                "-p",
                "JSON.stringify(require('./apps/miniprogram/presentation/theme/registry').listThemes())",
            ],
            cwd=ROOT,
            text=True,
        )
    )
    media = {}
    for theme in themes:
        roles = ("report", "calendar") if theme["id"] == "original" else ("hero",)
        for role in roles:
            asset = theme["assets"][role]
            path = ROOT / "apps/miniprogram" / asset.lstrip("/")
            mime = "image/jpeg" if path.suffix == ".jpg" else "image/png"
            media[asset] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    policy = json.loads((ROOT / "tools/frontend_viewports.json").read_text())
    baseline = policy["current"]
    sizes = policy["byBaseline"][baseline]
    for name, value in (("THEMES", themes), ("MEDIA", media), ("SIZES", sizes)):
        source = source.replace(f"__{name}__", json.dumps(value, ensure_ascii=False))
    preview = HERE / "index.html"
    preview.write_text(source)
    return preview, [t["id"] for t in themes], baseline, sizes


GEOMETRY = """() => {
  const hero = document.querySelector('.page-header');
  const image = hero.querySelector('.hero-picture img');
  const body = document.querySelector('.body').getBoundingClientRect();
  const heading = hero.querySelector('.heading').getBoundingClientRect();
  const title = hero.querySelector('h2');
  const box = hero.getBoundingClientRect();
  const style = getComputedStyle(hero);
  const controls = [...hero.querySelectorAll('button')].map(e => e.getBoundingClientRect());
  const menu = hero.querySelector('.menu');
  const rect = menu && menu.getBoundingClientRect();
  return {
    pageFits: document.documentElement.scrollWidth === innerWidth,
    headerFits: box.left === 0 && box.right === innerWidth && heading.bottom <= body.top,
    frameless: style.borderTopWidth === '0px' && style.borderTopLeftRadius === '0px' &&
      style.backgroundColor === 'rgba(0, 0, 0, 0)' && style.overflow === 'visible',
    artwork: image && image.naturalWidth > 0,
    ratio: image && image.clientWidth / image.getBoundingClientRect().height,
    intrinsicRatio: image && image.naturalWidth / image.naturalHeight,
    fades: image && getComputedStyle(image.parentElement, '::after').backgroundImage,
    titleHeight: title && title.getBoundingClientRect().height,
    titleLineHeight: title && parseFloat(getComputedStyle(title).lineHeight),
    controlsFit: controls.every(r => r.height >= 44 && r.left >= 0 && r.right <= innerWidth),
    menuOnTop: rect && menu.contains(document.elementFromPoint(rect.left+14,rect.top+14))
  };
}"""


TEXT_AREAS = """() => [...document.querySelectorAll('.heading h2,.heading p,.record-trigger')]
  .map(element => {
    const range = new Range();
    range.selectNodeContents(element);
    return {
      color: getComputedStyle(element).color,
      rows: [...range.getClientRects()].map(row => row.toJSON())
    };
  })
"""


def luminance(rgb):
    values = [value / 255 for value in rgb]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values
    ]
    return sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True)
    )


def text_contrast(page):
    """Sample the actual composited pixels behind each title/subtitle line."""
    targets = page.evaluate(TEXT_AREAS)
    visibility = page.add_style_tag(content=".heading { visibility: hidden; }")
    background = Image.open(BytesIO(page.screenshot())).convert("RGB")
    visibility.evaluate("element => element.remove()")
    samples = []
    for target in targets:
        ink = luminance([int(value) for value in re.findall(r"\d+", target["color"])])
        for row in target["rows"]:
            for x in range(round(row["left"]) + 1, round(row["right"]), 3):
                for y in range(round(row["top"]) + 3, round(row["bottom"]) - 2, 3):
                    base = luminance(background.getpixel((x, y)))
                    samples.append((max(ink, base) + 0.05) / (min(ink, base) + 0.05))
    return min(samples)


def render(preview, themes, sizes):
    exports = []
    errors = []
    requests = []
    lowest = float("inf")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))

        def log_remote(request):
            if request.url.startswith(("https:", "http:")):
                requests.append(request.url.split("?")[0])

        page.on("request", log_remote)
        page.goto(preview.as_uri())
        scenes = page.locator("#scene option").evaluate_all(
            "(options) => options.map(o => o.value).slice(1)"
        )
        for width, height in sizes.items():
            page.set_viewport_size({"width": int(width), "height": height})
            for theme in themes:
                for scene in scenes:
                    page.goto(
                        f"{preview.as_uri()}?single&theme={theme}&scene={scene}&width={width}"
                    )
                    page.evaluate("Promise.all([...document.images].map(img => img.decode()))")
                    page.evaluate("document.fonts.ready")
                    g = page.evaluate(GEOMETRY)
                    assert all(
                        g[k] for k in ("pageFits", "headerFits", "frameless", "controlsFit")
                    ), g
                    has_art = theme != "original" and scene != "image-failure"
                    assert bool(g["artwork"]) == has_art, g
                    if has_art:
                        assert abs(g["ratio"] - g["intrinsicRatio"]) < 0.002, g
                        assert g["fades"].count("linear-gradient(") == 2, g
                    if scene in ("reports", "image-failure"):
                        assert abs(g["titleHeight"] - g["titleLineHeight"]) < 0.1, g
                    if scene == "record-menu":
                        assert g["menuOnTop"], g
                    if scene == "long-title":
                        assert g["titleHeight"] > g["titleLineHeight"], g
                    contrast = text_contrast(page)
                    assert contrast >= 4.5, (theme, scene, width, contrast)
                    lowest = min(lowest, contrast)
                    file = OUT / f"{theme}-{scene}-{width}x{height}.png"
                    page.screenshot(path=file, animations="disabled")
                    exports.append(
                        (file.name, f"{theme} / {scene}", f"{width}x{height}", digest(file))
                    )
        browser.close()
    assert not errors and not requests, (errors, requests)
    return exports, lowest


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise SystemExit("Create a new revision for changes to an approved snapshot.")
    OUT.mkdir(parents=True, exist_ok=True)
    preview, themes, baseline, sizes = build()
    exports, contrast = render(preview, themes, sizes)
    rows = [
        f"# {HERE.name} — candidate approval manifest",
        "",
        "- Status: AWAITING_APPROVAL",
        "- UI ID: UI-001",
        f"- Design Revision: {HERE.name}",
        f"- Frontend baseline revision: {baseline}",
        f"- Frontend engineering revision: {FEC}",
        f"- Task Spec path and revision: {TASK}",
        f"- Frontend spec path: {local(HERE / 'FRONTEND-SPEC.md')}",
        f"- Editable design source path(s): {local(preview)}",
        f"- Editable source SHA-256: {local(preview)}={digest(preview)}",
        "- Approved by: PENDING",
        "- Approved at: PENDING",
        "- Approval evidence: PENDING",
        "",
        f"Browser design exports: {len(exports)} groups.",
        f"Lowest sampled heading text contrast in Chromium: {contrast:.2f}:1.",
        "Native geometry and device acceptance: NOT_RUN.",
        "",
        "## Export manifest",
        "",
        "| File | State | Viewport | Scale | SHA-256 |",
        "|---|---|---|---|---|",
    ]
    rows.extend(f"| {file} | {state} | {size} | 1x | {sha} |" for file, state, size, sha in exports)
    manifest.write_text("\n".join(rows) + "\n")
    print(
        f"DESIGN_HTML_PASS groups={len(exports)} sampled_contrast={contrast:.2f}:1 native=NOT_RUN"
    )


if __name__ == "__main__":
    main()
