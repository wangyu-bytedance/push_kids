from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "apps" / "miniprogram"


def fail(message: str) -> None:
    print(f"MINIPROGRAM_INVALID: {message}")
    raise SystemExit(1)


def main() -> None:
    app_json = json.loads((APP_ROOT / "app.json").read_text())
    pages = app_json.get("pages", [])
    primary_tabs = app_json.get("tabBar", {}).get("list", [])
    expected_tabs = [
        "pages/today/index",
        "pages/calendar/index",
        "pages/records/index",
        "pages/reports/index",
        "pages/settings/index",
    ]
    if [item.get("pagePath") for item in primary_tabs] != expected_tabs:
        fail("expected today/calendar/records/reports/settings primary tabs")
    for page in pages:
        for suffix in (".js", ".json", ".wxml", ".wxss"):
            path = APP_ROOT / f"{page}{suffix}"
            if not path.exists():
                fail(f"missing {path.relative_to(ROOT)}")
        json.loads((APP_ROOT / f"{page}.json").read_text())
    json.loads((APP_ROOT / "project.config.json").read_text())
    json.loads((APP_ROOT / "sitemap.json").read_text())
    method_expression = re.compile(r"\{\{[^}]*\.(?:join|slice|map|filter)\(")
    for wxml in APP_ROOT.rglob("*.wxml"):
        text = wxml.read_text()
        if method_expression.search(text):
            fail(f"unsupported method call in WXML: {wxml.relative_to(ROOT)}")
    source_size = sum(path.stat().st_size for path in APP_ROOT.rglob("*") if path.is_file())
    if source_size > 1_500_000:
        fail(f"source package exceeds 1.5 MiB budget: {source_size}")
    print(f"MINIPROGRAM_VALID pages={len(pages)} source_bytes={source_size}")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError) as exc:
        fail(str(exc))
