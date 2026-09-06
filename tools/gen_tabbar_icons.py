"""Generates apps/miniprogram/assets/tab-*.png from the PKDS-2.0 line-icon set.

TabBar icons cannot use WXSS background-image with data URIs on every platform, so
they stay PNG. Rendering them from the same 24x24 line grammar as styles/icons.wxss
keeps stroke weight and optical size consistent across the whole app.
"""

from __future__ import annotations

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT / "apps" / "miniprogram" / "assets"
SIZE = 72  # 40rpx (20px) at 3x, with headroom for aspectFit

INK_IDLE = "#8E9686"  # between ink-3 and ink-4: readable but recessive
INK_ACTIVE = "#1F5B45"  # primary
INK_KEY = "#FFFDF8"  # on primary key

ICONS: dict[str, str] = {
    "today": (
        "<path d='M12 21v-7'/><path d='M12 14C12 9 8 6 4 6c0 5 3 8 8 8Z'/>"
        "<path d='M12 14c0-4 3-7 8-7 0 4-3 7-8 7Z'/>"
    ),
    "calendar": (
        "<rect x='3.6' y='5.4' width='16.8' height='15' rx='2.4'/><path d='M3.6 10h16.8'/>"
        "<path d='M8.4 3.6v3.4'/><path d='M15.6 3.6v3.4'/>"
    ),
    "records": (
        "<path d='M3 8.5A2 2 0 0 1 5 6.5h1.6l1.2-2h8.4l1.2 2H19a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5"
        "a2 2 0 0 1-2-2Z'/><circle cx='12' cy='12.5' r='3.4'/>"
    ),
    "reports": (
        "<path d='M3.8 19.6h16.4'/>"
        "<path d='M6.6 16.4v-4.2'/><path d='M12 16.4V6.8'/><path d='M17.4 16.4v-6.6'/>"
    ),
    "settings": (
        "<path d='M4 8h9.2'/><path d='M18.4 8H20'/><circle cx='15.8' cy='8' r='2.3'/>"
        "<path d='M4 16h4.4'/><path d='M13.6 16H20'/><circle cx='11' cy='16' r='2.3'/>"
    ),
}

TEMPLATE = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24' "
    "fill='none' stroke='{color}' stroke-width='{width}' stroke-linecap='round' "
    "stroke-linejoin='round'>{body}</svg>"
)


def render(name: str, body: str, color: str, width: float) -> None:
    svg = TEMPLATE.format(color=color, width=width, body=body)
    out = TARGET_DIR / f"tab-{name}.png"
    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(out),
        output_width=SIZE,
        output_height=SIZE,
    )
    print(f"TAB_ICON {out.relative_to(ROOT)} {out.stat().st_size}B")


def main() -> None:
    for name, body in ICONS.items():
        render(name, body, INK_IDLE, 1.8)
        render(f"{name}-active", body, INK_ACTIVE, 2.1)
    render("records-key", ICONS["records"], INK_KEY, 2.0)


if __name__ == "__main__":
    main()
