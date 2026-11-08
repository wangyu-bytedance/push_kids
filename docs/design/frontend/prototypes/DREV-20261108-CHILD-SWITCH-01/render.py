"""Export the local review prototype and its pending approval manifest."""

import base64
import hashlib
import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001" / HERE.name
TASK = "specs/active/DESIGN-005-CHILD-SWITCH-HEADER.md"


def build():
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
        roles = ("calendar", "report") if theme["id"] == "original" else ("hero",)
        for role in roles:
            asset = theme["assets"][role]
            path = ROOT / "apps/miniprogram" / asset.lstrip("/")
            mime = "image/jpeg" if path.suffix == ".jpg" else "image/png"
            media[asset] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    policy = json.loads((ROOT / "tools/frontend_viewports.json").read_text())
    baseline = policy["current"]
    sizes = {**policy["byBaseline"][policy["legacy"]], **policy["byBaseline"][baseline]}
    source = (HERE / "source.html").read_text()
    for key, value in (("THEMES", themes), ("MEDIA", media), ("SIZES", sizes)):
        source = source.replace(f"__{key}__", json.dumps(value, ensure_ascii=False))
    preview = HERE / "index.html"
    preview.write_text(source)
    return preview, themes, sizes, baseline


def geometry(page):
    return page.evaluate(r"""async () => {
      const box = s => document.querySelector(s)?.getBoundingClientRect();
      const row = box('.title-row'), title = box('.title');
      const child = box('.child'), menu = box('.menu');
      const hero = document.querySelector('.hero');
      const spot = getComputedStyle(hero, '::before');
      const spotUrl = spot.backgroundImage.match(/^url\("(data:image\/[^"]+)"\)$/)?.[1];
      let backgroundVerified = false;
      if (spotUrl) {
        const picture = new Image();
        picture.src = spotUrl;
        await picture.decode();
        const size = selector => JSON.stringify(box(selector)?.toJSON());
        const before = ['.hero', '.title', '.subtitle', '.child'].map(size);
        const transparentToInput = spot.pointerEvents === 'none' && spot.position === 'absolute';
        hero.classList.remove('hero--spot');
        backgroundVerified = transparentToInput && picture.naturalWidth > 0 &&
          ['.hero', '.title', '.subtitle', '.child'].map(size).every((r, i) => r === before[i]);
        hero.classList.add('hero--spot');
      }
      const chip = document.querySelector('.child'), name = document.querySelector('.name');
      const titleStyle = getComputedStyle(document.querySelector('.title'));
      return {
        noOverflow: document.documentElement.scrollWidth === innerWidth,
        aligned: !child || (
          Math.abs(child.right - row.right) < 0.1 && Math.abs(child.top - row.top) < 0.1
        ),
        tap: !child || (child.height >= 44 && child.width >= 44),
        separate: !child || title.right <= child.left,
        shown: !!child,
        truncated: !!name && name.scrollWidth > name.clientWidth &&
          chip.getAttribute('aria-label').includes(name.textContent),
        wrap: title.height > parseFloat(titleStyle.lineHeight) + 1,
        chevron: !!chip?.querySelector('.chevron'),
        disabled: !!chip?.disabled,
        menu: !!menu && !!document.querySelector('.menu').contains(
          document.elementFromPoint(menu.x + 10, menu.y + 10)
        ),
        hiddenForMenu: chip?.getAttribute('aria-hidden') === 'true',
        art: !!document.querySelector('.art img')?.naturalWidth,
        spotArt: !!spotUrl,
        backgroundVerified
      };
    }""")


def export(preview, themes, sizes):
    rows = []
    errors = []
    external = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        page = browser.new_page(device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda request: (
                external.append(request.url) if request.url.startswith("http") else None
            ),
        )
        page.goto(preview.as_uri())
        scenes = page.locator("#scene option").evaluate_all(
            "options => options.map(option => option.value).slice(1)"
        )
        for width, height in sizes.items():
            page.set_viewport_size({"width": int(width), "height": height})
            for theme in themes:
                for scene in scenes:
                    theme_id = theme["id"]
                    page.goto(
                        f"{preview.as_uri()}?export&theme={theme_id}&scene={scene}&width={width}"
                    )
                    page.evaluate("Promise.all([...document.images].map(image => image.decode()))")
                    page.evaluate("document.fonts.ready")
                    g = geometry(page)
                    assert all(g[key] for key in ("noOverflow", "aligned", "tap", "separate")), g
                    assert g["shown"] == (scene != "empty"), g
                    assert g["art"] == (
                        theme_id != "original" and scene not in {"missing-art", "footprints"}
                    ), g
                    has_local_art = theme_id == "original" and scene in {
                        "calendar",
                        "single",
                        "reports",
                        "long-name",
                    }
                    assert g["spotArt"] == has_local_art, g
                    assert g["backgroundVerified"] == has_local_art, g
                    if scene == "single":
                        assert not g["chevron"], g
                    if scene in {"long-name", "large-text"}:
                        assert g["truncated"], g
                    if scene == "large-text" and width != "430":
                        assert g["wrap"], g
                    if scene == "reports":
                        assert not g["wrap"], (theme_id, width, scene, g)
                    if scene == "record-menu":
                        assert g["menu"] and g["hiddenForMenu"], g
                    if scene == "record-saving":
                        assert g["disabled"], g
                    path = OUT / f"{theme_id}-{scene}-{width}x{height}.png"
                    pixels = page.screenshot(path=path, animations="disabled")
                    rows.append(
                        f"| {path.name} | {theme_id} / {scene} | {width}x{height} | 1x | "
                        f"{hashlib.sha256(pixels).hexdigest()} |"
                    )
        browser.close()
    assert not errors and not external, (errors, external)
    return rows


def main():
    manifest = OUT / "APPROVAL.md"
    if manifest.exists() and "- Status: APPROVED" in manifest.read_text():
        raise SystemExit("Create a new revision for changes to an approved snapshot.")
    OUT.mkdir(parents=True, exist_ok=True)
    preview, themes, sizes, baseline = build()
    rows = export(preview, themes, sizes)
    source = preview.relative_to(ROOT)
    source_hash = hashlib.sha256(preview.read_bytes()).hexdigest()
    manifest.write_text(
        "\n".join(
            [
                f"# {HERE.name} — candidate approval manifest",
                "",
                "- Status: AWAITING_APPROVAL",
                "- UI ID: UI-001",
                f"- Design Revision: {HERE.name}",
                f"- Frontend baseline revision: {baseline}",
                "- Frontend engineering revision: FEC-20261107-AGENT-DEVICE-MATRIX-03",
                f"- Task Spec path and revision: {TASK} / DESIGN-005-SPEC-01",
                f"- Frontend spec path: {source.parent / 'FRONTEND-SPEC.md'}",
                f"- Editable design source path(s): {source}",
                f"- Editable source SHA-256: {source}={source_hash}",
                "- Approved by: PENDING",
                "- Approved at: PENDING",
                "- Approval evidence: PENDING",
                "",
                f"Chromium design exports: {len(rows)}. Includes supplemental 320×568.",
                "Original-style calendar and report art is a background outside the content flow.",
                "Native geometry and device acceptance: NOT_RUN.",
                "",
                "## Export manifest",
                "",
                "| File | State | Viewport | Scale | SHA-256 |",
                "|---|---|---|---|---|",
                *rows,
                "",
            ]
        )
    )
    print(f"DESIGN_HTML_PASS groups={len(rows)} native=NOT_RUN")


if __name__ == "__main__":
    main()
