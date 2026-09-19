from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).with_name("family-invite-flow.html")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
TARGETS = {
    "manager": ROOT / "docs/design/frontend/snapshots/UI-009/DREV-20260913-FAMILY-INVITE-CODE-01",
    "join": ROOT / "docs/design/frontend/snapshots/UI-010/DREV-20260913-FAMILY-INVITE-CODE-01",
}


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(CHROME))
        for screen, target in TARGETS.items():
            target.mkdir(parents=True, exist_ok=True)
            for width, height in VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": width, "height": height}, device_scale_factor=1
                )
                page.goto(f"{SOURCE.as_uri()}?screen={screen}")
                page.screenshot(path=str(target / f"{screen}-{width}x{height}.png"))
                page.close()
        browser.close()


if __name__ == "__main__":
    main()
