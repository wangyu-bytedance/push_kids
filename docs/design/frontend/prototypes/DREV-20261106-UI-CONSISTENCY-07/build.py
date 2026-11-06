"""Build a self-contained Settings theme-picker review; no product code writes."""

import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PREVIOUS = HERE.parent / "DREV-20261106-UI-CONSISTENCY-06"


def build():
    images = {
        name: "data:image/png;base64,"
        + base64.b64encode((PREVIOUS / "assets" / f"{name}.png").read_bytes()).decode()
        for name in ("garden", "space", "midnight", "ocean", "tech")
    }
    images["original"] = (
        "data:image/png;base64,"
        + base64.b64encode(
            (ROOT / "apps/miniprogram/assets/illustrations/record-books.png").read_bytes()
        ).decode()
    )
    source = (HERE / "source.html").read_text()
    source = source.replace("__THEME_ART__", json.dumps(images))
    (HERE / "index.html").write_text(source)
    print(f"Built Settings review: {len(source.encode())} bytes (docs only)")


if __name__ == "__main__":
    build()
