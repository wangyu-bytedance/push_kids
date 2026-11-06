"""Assemble the review-only design into one portable HTML file."""
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "DREV-20261106-UI-CONSISTENCY-02" / "index.html"


def build():
    source = BASE.read_text()
    css = source.split("<style>", 1)[1].split("</style>", 1)[0]
    script = source.split("<script>", 1)[1].split("</script>", 1)[0]
    # Keep the frozen design component source; replace its old review gallery.
    script = script.split("let selectedReviewScene=", 1)[0]
    images = {}
    for theme in ["garden", "space", "midnight", "ocean", "tech"]:
        raw = base64.b64encode((HERE / "assets" / f"{theme}.png").read_bytes()).decode()
        images[theme] = f"data:image/png;base64,{raw}"
    html = "\n".join([
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>知芽 · 五主题全界面</title><style>',
        css, (HERE / "themes.css").read_text(),
        '</style></head><body><div id="app"></div><script>',
        "const THEME_ART=" + json.dumps(images) + ";",
        script, (HERE / "screens.js").read_text(), (HERE / "gallery.js").read_text(),
        '</script></body></html>',
    ])
    (HERE / "index.html").write_text(html)
    print(f"Built {HERE / 'index.html'} ({len(html.encode()):,} bytes; design-only)")


if __name__ == "__main__":
    build()
