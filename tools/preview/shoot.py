"""按当前视口矩阵把 dist/ui-preview/*.html 渲染成 PNG，供本地设计走查。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "dist" / "ui-preview"
POLICY = json.loads((ROOT / "tools" / "frontend_viewports.json").read_text())
VIEWPORTS = POLICY["byBaseline"][POLICY["current"]]


def main() -> None:
    names = sys.argv[1:]
    files = sorted(file for file in OUT.glob("*.html") if file.stem.rsplit("-", 1)[-1] in VIEWPORTS)
    if names:
        files = [f for f in files if any(f.name.startswith(n) for n in names)]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-device-scale-factor=2"])
        for html in files:
            width = html.stem.rsplit("-", 1)[1]
            page = browser.new_page(
                viewport={"width": int(width), "height": VIEWPORTS[width]}, device_scale_factor=2
            )
            page.goto(html.as_uri())
            page.wait_for_timeout(350)
            viewport_shot = html.with_name(f"{html.stem}-vp.png")
            page.screenshot(path=str(viewport_shot))
            print(f"SHOT {viewport_shot.relative_to(ROOT)}")
            # 全页截图时隐藏固定底栏，避免 fixed 元素落在页面中间
            page.add_style_tag(content=".tabbar,.pk-cta-bar,.pk-fab{display:none}")
            shot = html.with_suffix(".png")
            page.screenshot(path=str(shot), full_page=True)
            print(f"SHOT {shot.relative_to(ROOT)}")
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
