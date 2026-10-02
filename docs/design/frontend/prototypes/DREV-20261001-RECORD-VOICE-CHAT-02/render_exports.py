from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).with_name("record-voice-chat.html")
OUTPUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261001-RECORD-VOICE-CHAT-02"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
STATES = ("text", "voice", "holding", "appended")


OUTPUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=CHROME, headless=True)
    for state in STATES:
        for width, height in VIEWPORTS:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            page.goto(f"{SOURCE.as_uri()}?state={state}")
            page.screenshot(path=OUTPUT / f"record-voice-{state}-{width}x{height}.png")
            page.close()
    browser.close()
