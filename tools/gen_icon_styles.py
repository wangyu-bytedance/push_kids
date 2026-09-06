"""Generates apps/miniprogram/styles/icons.wxss from the PKDS line-icon set.

Icons are 24x24 line drawings, stroke width 2, round caps. WXSS cannot inherit
currentColor through background-image, so each icon is emitted once per palette
entry that the design actually uses.
"""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "apps" / "miniprogram" / "styles" / "icons.wxss"

# name -> svg body (paths only, drawn on a 24x24 board)
ICONS: dict[str, str] = {
    "sprout": (
        "<path d='M12 21v-7'/><path d='M12 14C12 9 8 6 4 6c0 5 3 8 8 8Z'/>"
        "<path d='M12 14c0-4 3-7 8-7 0 4-3 7-8 7Z'/>"
    ),
    "camera": (
        "<path d='M3 8.5A2 2 0 0 1 5 6.5h1.6l1.2-2h8.4l1.2 2H19a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5"
        "a2 2 0 0 1-2-2Z'/><circle cx='12' cy='12.5' r='3.4'/>"
    ),
    "image": (
        "<rect x='3' y='4.5' width='18' height='15' rx='2.5'/>"
        "<circle cx='8.5' cy='10' r='1.6'/><path d='M4 17l4.8-4.4 3.6 3.1 3-2.4L20 17'/>"
    ),
    "pen": "<path d='M4 20h4l10-10a2.6 2.6 0 0 0-3.7-3.7L4.3 16.4Z'/><path d='M13.6 7.4l3 3'/>",
    "plus": "<path d='M12 5v14'/><path d='M5 12h14'/>",
    "check": "<path d='M4.5 12.8l4.6 4.4L19.5 6.8'/>",
    "close": "<path d='M6 6l12 12'/><path d='M18 6L6 18'/>",
    "info": "<circle cx='12' cy='12' r='8.6'/><path d='M12 11v6'/><path d='M12 7.6h.01'/>",
    "warn": ("<path d='M12 3.6 21 19.4H3Z'/><path d='M12 9.6v4.6'/><path d='M12 17.2h.01'/>"),
    "clock": "<circle cx='12' cy='12' r='8.6'/><path d='M12 7.4V12l3.4 2.1'/>",
    "refresh": ("<path d='M20 12a8 8 0 1 1-2.6-5.9'/><path d='M20 4v4.4h-4.4'/>"),
    "search": "<circle cx='11' cy='11' r='6.6'/><path d='M15.8 15.8 20 20'/>",
    "filter": "<path d='M4 6.5h16'/><path d='M7 12h10'/><path d='M10 17.5h4'/>",
    "more": (
        "<circle cx='5.5' cy='12' r='1.4' fill='CURRENT' stroke='none'/>"
        "<circle cx='12' cy='12' r='1.4' fill='CURRENT' stroke='none'/>"
        "<circle cx='18.5' cy='12' r='1.4' fill='CURRENT' stroke='none'/>"
    ),
    "sparkle": (
        "<path d='M12 3.4l1.9 4.9 4.9 1.9-4.9 1.9L12 17l-1.9-4.9L5.2 10.2l4.9-1.9Z'/>"
        "<path d='M18.6 16.2l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7Z'/>"
    ),
    "trash": (
        "<path d='M4.5 7h15'/><path d='M9.5 7V4.8h5V7'/>"
        "<path d='M6.6 7l.9 12.2h9l.9-12.2'/><path d='M10.4 10.6v5.6'/><path d='M13.6 10.6v5.6'/>"
    ),
    "family": (
        "<circle cx='8' cy='8' r='3'/><circle cx='16.6' cy='9.4' r='2.4'/>"
        "<path d='M2.8 20c0-3.3 2.3-5.6 5.2-5.6s5.2 2.3 5.2 5.6'/>"
        "<path d='M15 14.6c3 0 5.2 2 5.2 5.4'/>"
    ),
    "user": (
        "<circle cx='12' cy='8' r='3.4'/>"
        "<path d='M5.4 20c0-3.6 2.9-6.2 6.6-6.2S18.6 16.4 18.6 20'/>"
    ),
    "share": (
        "<circle cx='17.6' cy='6' r='2.6'/><circle cx='6.4' cy='12' r='2.6'/>"
        "<circle cx='17.6' cy='18' r='2.6'/><path d='M8.8 10.8 15.2 7.3'/>"
        "<path d='M8.8 13.2l6.4 3.5'/>"
    ),
    "book": (
        "<path d='M4 5.4A1.4 1.4 0 0 1 5.4 4h5.2A2 2 0 0 1 12 5.8v13a1.8 1.8 0 0 0-1.4-1.2H4Z'/>"
        "<path d='M20 5.4A1.4 1.4 0 0 0 18.6 4h-5.2A2 2 0 0 0 12 5.8v13"
        "a1.8 1.8 0 0 1 1.4-1.2H20Z'/>"
    ),
    "list": "<path d='M4.6 7h14.8'/><path d='M4.6 12h14.8'/><path d='M4.6 17h9.6'/>",
    "cloud-off": (
        "<path d='M6.6 18.4h9.6a4 4 0 0 0 1-7.9'/><path d='M15.6 8.6A5.2 5.2 0 0 0 7 9.9"
        "a4 4 0 0 0-.4 8'/><path d='M3.6 3.6 20.4 20.4'/>"
    ),
    "eye": (
        "<path d='M2.4 12S6 6.4 12 6.4 21.6 12 21.6 12 18 17.6 12 17.6 2.4 12 2.4 12Z'/>"
        "<circle cx='12' cy='12' r='2.8'/>"
    ),
    "shield": (
        "<path d='M12 3.4 19.4 6v6.2c0 4-3.1 7.1-7.4 8.4-4.3-1.3-7.4-4.4-7.4-8.4V6Z'/>"
        "<path d='M9.2 12.2 11.4 14.4 15 10.4'/>"
    ),
    "calendar": (
        "<rect x='3.6' y='5.4' width='16.8' height='15' rx='2.4'/><path d='M3.6 10h16.8'/>"
        "<path d='M8.4 3.6v3.4'/><path d='M15.6 3.6v3.4'/>"
    ),
    "note": (
        "<path d='M5.4 4h9.2L19 8.4V20H5.4Z'/><path d='M14.2 4v4.6H19'/>"
        "<path d='M8.4 13h7'/><path d='M8.4 16.6h4.6'/>"
    ),
    # 课外活动图标：按活动语义区分，映射规则见 utils/ui.js 的 activityIcon。
    "swim": (
        "<circle cx='16.2' cy='6.8' r='1.9'/><path d='M14.4 8 5.2 12.4'/>"
        "<path d='M9.8 10.2 6.4 5.8'/><path d='M2.4 18q2.4-2.2 4.8 0t4.8 0t4.8 0t4.8 0'/>"
    ),
    "pingpong": (
        "<circle cx='9.4' cy='9' r='5.4'/><path d='M12.4 13.4 16.8 20.2'/>"
        "<circle cx='18.6' cy='6' r='1.9'/>"
    ),
    "basketball": (
        "<circle cx='12' cy='12' r='8.6'/><path d='M3.4 12h17.2'/><path d='M12 3.4v17.2'/>"
        "<path d='M6 6c3.3 3.3 3.3 8.7 0 12'/><path d='M18 6c-3.3 3.3-3.3 8.7 0 12'/>"
    ),
    "badminton": (
        "<path d='M14.6 14.8 18 5.4H6l3.4 9.4Z'/><path d='M12 5.4v9.4'/>"
        "<path d='M10.2 10.8h3.6'/><path d='M9.4 14.8q2.6 3.6 5.2 0'/>"
    ),
    "soccer": (
        "<circle cx='12' cy='12' r='8.6'/><path d='M12 8.2l3.4 2.5-1.3 4h-4.2l-1.3-4Z'/>"
        "<path d='M12 8.2V3.6'/><path d='M15.4 10.7 19.8 9'/><path d='M14.1 14.7 16.8 18.4'/>"
        "<path d='M9.9 14.7 7.2 18.4'/><path d='M8.6 10.7 4.2 9'/>"
    ),
    "tennis": (
        "<circle cx='12' cy='8.6' r='5.6'/><path d='M12 3v11.2'/><path d='M6.4 8.6h11.2'/>"
        "<path d='M12 14.2v6.2'/><path d='M9.8 20.4h4.4'/>"
    ),
    "chess": (
        "<rect x='3.4' y='3.4' width='17.2' height='17.2' rx='2.6'/><path d='M3.4 9.2h17.2'/>"
        "<path d='M3.4 14.8h17.2'/><path d='M9.2 3.4v17.2'/><path d='M14.8 3.4v17.2'/>"
        "<circle cx='14.8' cy='9.2' r='2.9' fill='CURRENT' stroke='none'/>"
    ),
    "piano": (
        "<rect x='3.4' y='4.6' width='17.2' height='14.8' rx='2.2'/><path d='M9 4.6v14.8'/>"
        "<path d='M15 4.6v14.8'/>"
        "<rect x='7.3' y='4.6' width='3.4' height='8' rx='0.8' fill='CURRENT' stroke='none'/>"
        "<rect x='13.3' y='4.6' width='3.4' height='8' rx='0.8' fill='CURRENT' stroke='none'/>"
    ),
    "music": (
        "<circle cx='7' cy='17.4' r='2.6'/><circle cx='17.4' cy='15.4' r='2.6'/>"
        "<path d='M9.6 17.4V6.2l10.4-2.2v11.4'/>"
    ),
    "dance": (
        "<circle cx='13.8' cy='4.6' r='2.1'/>"
        "<path d='M13.2 6.8 10.8 12.6l3.4 3.2-1.2 4.8'/><path d='M10.8 12.6 6.6 16.4'/>"
        "<path d='M12.2 9.2 17 7.2'/><path d='M12.2 9.2 8.2 6.6'/>"
    ),
    "martial": (
        "<rect x='2.6' y='9.4' width='18.8' height='5.2' rx='1.6'/>"
        "<rect x='9' y='7.8' width='6' height='8.4' rx='1.6'/>"
        "<path d='M10.4 16.2 8.4 20.4'/><path d='M13.6 16.2 15.6 20.4'/>"
    ),
    "brush": (
        "<path d='M12 3.4v7.4'/><rect x='9.6' y='10.8' width='4.8' height='2.8' rx='1'/>"
        "<path d='M9.6 13.6c0 3 1.1 5.4 2.4 6.8 1.3-1.4 2.4-3.8 2.4-6.8Z'/>"
    ),
    "palette": (
        "<path d='M12 3.6a8.4 8.4 0 0 0 0 16.8c1.5 0 2.2-1 2.2-2.1 0-1.4 1-2.3 2.4-2.3h1.6"
        "a2.6 2.6 0 0 0 2.6-2.6A9.8 9.8 0 0 0 12 3.6Z'/>"
        "<circle cx='8.4' cy='9.4' r='1.2' fill='CURRENT' stroke='none'/>"
        "<circle cx='13.4' cy='7.8' r='1.2' fill='CURRENT' stroke='none'/>"
        "<circle cx='7.6' cy='14.4' r='1.2' fill='CURRENT' stroke='none'/>"
    ),
    "code": (
        "<path d='M9.4 7.6 4.6 12l4.8 4.4'/><path d='M14.6 7.6 19.4 12l-4.8 4.4'/>"
        "<path d='M13.4 5.2 10.6 18.8'/>"
    ),
    "robot": (
        "<rect x='4.4' y='7.6' width='15.2' height='11.6' rx='3'/><path d='M12 4.2v3.4'/>"
        "<circle cx='12' cy='3' r='1.2'/><path d='M2.6 11.8v3.4'/><path d='M21.4 11.8v3.4'/>"
        "<circle cx='9.4' cy='12.8' r='1.3' fill='CURRENT' stroke='none'/>"
        "<circle cx='14.6' cy='12.8' r='1.3' fill='CURRENT' stroke='none'/>"
        "<path d='M9.6 16.4h4.8'/>"
    ),
    "star": (
        "<path d='M12 3.6l2.7 5.7 6.1.8-4.5 4.3 1.1 6.2L12 17.6l-5.4 3 1.1-6.2L3.2 10.1l6.1-.8Z'/>"
    ),
}

# palette key -> hex
COLORS: dict[str, str] = {
    "": "#464E43",  # ink-2, default
    "-pri": "#1F5B45",  # primary
    "-inv": "#FFFDF8",  # on primary surfaces
    "-mute": "#79826F",  # ink-3
    "-att": "#A9762A",  # attention
    "-dan": "#A85742",  # danger
}

TEMPLATE = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    "stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>"
    "{body}</svg>"
)

# 基础规则单独拼接，避免源码行超长；产物里仍是一行 WXSS。
ICO_BASE = (
    ".ico { display: block; flex: none; width: 42rpx; height: 42rpx; "
    "background-repeat: no-repeat; background-position: center; background-size: 100% 100%; }"
)

HEADER = f"""/* 知芽 Push Kids · PKDS-2.0 线性图标
   由 tools/gen_icon_styles.py 生成，请勿手工编辑。
   用法：<view class="ico ico-camera"></view>；换色加后缀类，例如 ico-camera-pri。
   尺寸：默认 42rpx（21px），.ico.lg 48rpx，.ico.sm 32rpx，.ico.xs 28rpx。 */

{ICO_BASE}
.ico.lg {{ width: 48rpx; height: 48rpx; }}
.ico.xl {{ width: 56rpx; height: 56rpx; }}
.ico.sm {{ width: 32rpx; height: 32rpx; }}
.ico.xs {{ width: 28rpx; height: 28rpx; }}
"""


def data_uri(body: str, color: str) -> str:
    svg = TEMPLATE.format(color=color, body=body.replace("CURRENT", color))
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def main() -> None:
    lines = [HEADER]
    for name, body in ICONS.items():
        for suffix, color in COLORS.items():
            lines.append(
                f".ico-{name}{suffix} {{ background-image: url('{data_uri(body, color)}'); }}"
            )
    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ICONS_WRITTEN {TARGET.relative_to(ROOT)} icons={len(ICONS)} variants={len(COLORS)}")


if __name__ == "__main__":
    main()
