from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).with_name("record-voice-input.html")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
TARGET = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261001-RECORD-VOICE-INPUT-01"
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
STATES = ("idle", "recording", "appended")


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(CHROME))
        for state in STATES:
            for width, height in VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": width, "height": height}, device_scale_factor=1
                )
                page.goto(f"{SOURCE.as_uri()}?state={state}")
                page.screenshot(path=str(TARGET / f"record-voice-{state}-{width}x{height}.png"))
                page.close()
        browser.close()


if __name__ == "__main__":
    main()
