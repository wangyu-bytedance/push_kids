"""Render synthetic report disclosure candidates as editable SVG and exact-size PNG."""

from __future__ import annotations

import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT.parent.parent / "snapshots" / "UI-001" / ROOT.name
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
STATES = ("collapsed", "history-open", "review-open", "both-open")


def text(x: int, y: int, value: str, size: int = 14, color: str = "#24342B", weight: int = 400) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
        'font-family="PingFang SC, Noto Sans CJK SC, sans-serif">'
        f"{escape(value)}</text>"
    )


def box(x: int, y: int, w: int, h: int, radius: int = 20, fill: str = "#FFFDF8", stroke: str = "#EBE8DE") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def divider(x: int, y: int, width: int) -> str:
    return f'<path d="M{x} {y}h{width}" stroke="#EDE9E0" stroke-width="1"/>'


def chevron(x: int, y: int, opened: bool) -> str:
    shape = f"M{x - 6} {y + 3}l6 -6 6 6" if opened else f"M{x - 6} {y - 3}l6 6 6 -6"
    return f'<path d="{shape}" fill="none" stroke="#8C988B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'


def disclosure(parts: list[str], x: int, y: int, w: int, title: str, hint: str, opened: bool, icon: str) -> int:
    parts.append(box(x, y, w, 64, 20))
    if icon == "clock":
        parts.append(f'<circle cx="{x + 24}" cy="{y + 32}" r="9" fill="none" stroke="#315E48" stroke-width="1.8"/>')
        parts.append(f'<path d="M{x + 24} {y + 26}v6l4 2" fill="none" stroke="#315E48" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        parts.append(f'<path d="M{x + 16} {y + 26}h16M{x + 16} {y + 32}h16M{x + 16} {y + 38}h11" fill="none" stroke="#315E48" stroke-width="1.8" stroke-linecap="round"/>')
    parts.append(text(x + 44, y + 39, title, 16, "#24342B", 600))
    parts.append(text(x + w - 32 - len(hint) * 12, y + 38, hint, 12, "#798777"))
    parts.append(chevron(x + w - 18, y + 32, opened))
    return y + 64


def history_body(parts: list[str], x: int, y: int, w: int) -> int:
    parts.append(box(x, y + 8, w, 286, 20))
    tab_w = (w - 32) // 3
    parts.append(box(x + 16, y + 22, tab_w, 36, 18, "#E8F0E7", "#E8F0E7"))
    parts.append(text(x + 25, y + 46, "已确认", 13, "#1F5B45", 600))
    parts.append(text(x + 16 + tab_w + 17, y + 46, "待处理", 13, "#657264"))
    parts.append(text(x + 16 + 2 * tab_w + 15, y + 46, "全部", 13, "#657264"))
    parts.append(box(x + 16, y + 72, w - 112, 40, 12, "#FAF8F1"))
    parts.append(text(x + 28, y + 98, "搜索学习记录", 13, "#889286"))
    parts.append(box(x + w - 88, y + 72, 72, 40, 12, "#F3EFE4"))
    parts.append(text(x + w - 76, y + 98, "筛选", 13, "#355C47"))
    parts.append(text(x + 18, y + 142, "今天 · 10月11日", 12, "#798777"))
    parts.append(box(x + 16, y + 154, w - 32, 92, 14, "#FFFFFF"))
    parts.append(text(x + 30, y + 182, "数学 · 乘法练习", 15, "#24342B", 600))
    parts.append(text(x + 30, y + 207, "已确认 · 2 个知识点", 12, "#657264"))
    parts.append(text(x + 30, y + 231, "查看详情  ›", 12, "#1F5B45"))
    parts.append(divider(x + 18, y + 258, w - 36))
    parts.append(text(x + 18, y + 279, "每页最多 20 条 · 查看下一页", 12, "#1F5B45"))
    return y + 294


def review_body(parts: list[str], x: int, y: int, w: int) -> int:
    parts.append(box(x, y + 8, w, 280, 20))
    parts.append(text(x + 18, y + 34, "按时间", 13, "#1F5B45", 600))
    parts.append(text(x + 106, y + 34, "按科目", 13, "#657264"))
    parts.append(text(x + 194, y + 34, "按次数", 13, "#657264"))
    parts.append(divider(x + 18, y + 47, w - 36))
    parts.append(box(x + 18, y + 61, (w - 44) // 2, 44, 12, "#E8F0E7", "#C7D9C6"))
    parts.append(text(x + 32, y + 89, "明天", 14, "#1F5B45", 600))
    parts.append(box(x + 26 + (w - 44) // 2, y + 61, (w - 44) // 2, 44, 12, "#F7F5EF"))
    parts.append(text(x + 40 + (w - 44) // 2, y + 89, "后天", 14, "#657264"))
    parts.append(text(x + 18, y + 131, "预计 3 项 · 约 7 分钟", 13, "#657264"))
    parts.append(divider(x + 18, y + 145, w - 36))
    parts.append(text(x + 18, y + 171, "数学 · 本页 2 项", 14, "#1F5B45", 600))
    parts.append(text(x + 18, y + 201, "乘法口诀", 14, "#24342B"))
    parts.append(text(x + 18, y + 223, "已复习 1 次 · 最近 10月9日", 12, "#657264"))
    parts.append(divider(x + 18, y + 239, w - 36))
    parts.append(text(x + 18, y + 268, "加载更多条目", 12, "#1F5B45"))
    return y + 288


def render(width: int, height: int, state: str) -> str:
    x, w = 16, width - 32
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="{width}" height="{height}" fill="#FAF7F0"/>']
    parts.append(text(18, 35, "报表", 12, "#798777"))
    parts.append(text(18, 66, "一点一滴，看得见", 21, "#1F5B45", 600))
    parts.append(text(18, 92, "近 7 天 · 只统计已确认的学习", 12, "#657264"))
    y = 127
    parts.append(text(x, y, "科目学习记录", 17, "#24342B", 600))
    parts.append(text(width - 72, y, "近 7 天", 12, "#798777"))
    y += 13
    parts.append(box(x, y, w, 91, 20))
    parts.append(text(x + 18, y + 32, "语文", 14, "#24342B"))
    parts.append(text(x + w - 74, y + 32, "8 条  ›", 12, "#657264"))
    parts.append(divider(x + 18, y + 46, w - 36))
    parts.append(text(x + 18, y + 75, "数学", 14, "#24342B"))
    parts.append(text(x + w - 74, y + 75, "5 条  ›", 12, "#657264"))
    y += 107
    is_history = state in {"history-open", "both-open"}
    is_review = state in {"review-open", "both-open"}
    y = disclosure(parts, x, y, w, "历史记录", "1 条待处理", is_history, "clock")
    if is_history:
        y = history_body(parts, x, y, w)
    y += 12
    y = disclosure(parts, x, y, w, "编辑计划", "", is_review, "list")
    if is_review:
        y = review_body(parts, x, y, w)
    y += 29
    parts.append(text(x, y, "课外活动投入", 17, "#24342B", 600))
    parts.append(text(width - 72, y, "近 7 天", 12, "#798777"))
    y += 16
    parts.append(box(x, y, w, 70, 20))
    parts.append(text(x + 18, y + 43, "游泳 · 2 次 · 共 90 分钟", 13, "#24342B"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        for width, height in VIEWPORTS:
            name = f"{state}-{width}x{height}"
            svg = ROOT / f"{name}.svg"
            png = EXPORTS / f"{name}.png"
            svg.write_text(render(width, height, state), encoding="utf-8")
            subprocess.run(["rsvg-convert", "--output", str(png), str(svg)], check=True)


if __name__ == "__main__":
    main()
