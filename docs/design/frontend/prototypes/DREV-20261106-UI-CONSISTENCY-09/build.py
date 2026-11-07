"""Build a self-contained review only. Does not edit production files."""

import base64
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def main():
    data = json.loads(
        subprocess.check_output(
            [
                "node",
                "-e",
                "console.log(JSON.stringify({themes:require('./apps/miniprogram/presentation/theme/registry').listThemes(),"
                "glyphs:require('./apps/miniprogram/presentation/theme/glyphs')}))",
            ],
            cwd=ROOT,
            text=True,
        )
    )
    art = {}
    for theme in data["themes"]:
        # rpx is shown at the design viewport's width; the live source uses native rpx.
        theme["style"] = re.sub(r"([\d.]+)rpx", r"calc(\1 * 100vw / 750)", theme["style"])
        for resource in theme["assets"].values():
            if resource and resource not in art:
                file = ROOT / "apps/miniprogram" / resource.lstrip("/")
                mime = "image/jpeg" if file.suffix == ".jpg" else "image/png"
                art[resource] = (
                    f"data:{mime};base64," + base64.b64encode(file.read_bytes()).decode()
                )
    source = (HERE / "source.html").read_text()
    source = source.replace("__THEMES__", json.dumps(data["themes"], ensure_ascii=False))
    source = source.replace("__ART__", json.dumps(art))
    source = source.replace("__GLYPHS__", json.dumps(data["glyphs"]))
    (HERE / "index.html").write_text(source)
    print("DESIGN_ONLY_BUILT", len(source.encode()))


if __name__ == "__main__":
    main()
