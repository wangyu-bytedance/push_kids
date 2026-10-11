"""Render editable, synthetic review-inventory SVG mockups for design review."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
PALETTE = {
    "canvas": "#FAF7F0",
    "paper": "#FFFDF8",
    "ink": "#22261F",
    "secondary": "#464E43",
    "muted": "#79826F",
    "line": "#EBE5D7",
    "green": "#1F5B45",
    "tint": "#E4EDE6",
    "english": "#565383",
    "english_bg": "#EDECF5",
    "chinese": "#96671F",
    "chinese_bg": "#F5EBDA",
    "math": "#3F6379",
    "math_bg": "#E6EDF3",
    "danger": "#A85742",
}
SANS = "PingFang SC, Hiragino Sans GB, Noto Sans CJK SC, sans-serif"
SERIF = "Songti SC, Noto Serif CJK SC, serif"


def rect(x, y, w, h, *, fill="paper", radius=0, stroke=None, sw=1):
    color = PALETTE.get(fill, fill)
    outline = f' stroke="{PALETTE.get(stroke, stroke)}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}"{outline}/>'


def text(x, y, value, *, size=14, color="ink", weight=400, family=SANS, anchor=None):
    attr = f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{PALETTE.get(color, color)}"{attr}>'
        f'{escape(value)}</text>'
    )


def line(x1, y1, x2, y2, color="line", width=1):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{PALETTE.get(color, color)}" stroke-width="{width}"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{PALETTE.get(color, color)}" stroke-width="{width}"/>'


def shell(width, height, state):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><filter id="paper-shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="3" stdDeviation="8" flood-color="#22261F" flood-opacity=".055"/></filter></defs>',
        rect(0, 0, width, height, fill="canvas"),
        text(19, 29, "9:41", size=15, weight=600),
        rect(width - 47, 15, 28, 14, fill="ink", radius=5),
        rect(width - 44, 18, 18, 8, fill="paper", radius=2),
        f'<path d="M{width-75} 27q8-11 16 0m-13 0q5-6 10 0" fill="none" stroke="{PALETTE["ink"]}" stroke-width="2" stroke-linecap="round"/>',
        f'<path d="M{width-97} 28v-5m5 5v-9m5 9V15" fill="none" stroke="{PALETTE["ink"]}" stroke-width="3" stroke-linecap="round"/>',
        '<path d="M27 67l-9 9 9 9" fill="none" stroke="#22261F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
        text(width / 2, 83, "复习条目", size=17, weight=600, anchor="middle"),
        rect(width - 91, 56, 75, 38, fill="paper", radius=19, stroke="line"),
        f'<circle cx="{width-80}" cy="75" r="2" fill="{PALETTE["ink"]}"/>',
        f'<circle cx="{width-72}" cy="75" r="2" fill="{PALETTE["ink"]}"/>',
        f'<circle cx="{width-64}" cy="75" r="2" fill="{PALETTE["ink"]}"/>',
        line(width - 52, 63, width - 52, 87),
        f'<circle cx="{width-34}" cy="75" r="9" fill="none" stroke="{PALETTE["ink"]}" stroke-width="2.5"/>',
        f'<circle cx="{width-34}" cy="75" r="3" fill="{PALETTE["ink"]}"/>',
        line(0, 100, width, 100),
    ]
    labels = [("time", "按时间"), ("subject", "按科目"), ("count", "按次数")]
    selected = "time" if state in {"time", "actions"} else state
    gutter = 14 if width <= 320 else 18
    span = width - gutter * 2
    tab_width = span / 3
    for index, (key, label) in enumerate(labels):
        cx = gutter + tab_width * (index + .5)
        active = key == selected
        parts.append(text(cx, 138, label, size=15, weight=600 if active else 400, color="green" if active else "secondary", anchor="middle"))
        if active:
            parts.append(rect(cx - 24, 155, 48, 3, fill="green", radius=1.5))
    parts.append(line(gutter, 160, width - gutter, 160))
    return parts, gutter, span


def more_button(x, y, active=False):
    return [
        rect(x, y, 44, 44, fill="tint" if active else "paper", radius=12, stroke="green" if active else "line"),
        text(x + 22, y + 29, "···", size=20, color="green" if active else "secondary", weight=600, anchor="middle"),
    ]


def subject_mark(x, y, subject):
    label, foreground, background = {
        "english": ("英", "english", "english_bg"),
        "chinese": ("语", "chinese", "chinese_bg"),
        "math": ("数", "math", "math_bg"),
    }[subject]
    return [rect(x, y, 36, 36, fill=background, radius=12), text(x + 18, y + 25, label, size=18, color=foreground, weight=600, family=SERIF, anchor="middle")]


def card_base(x, y, width, height):
    return [
        f'<g filter="url(#paper-shadow)">{rect(x, y, width, height, fill="paper", radius=20, stroke="line")}</g>',
        rect(x, y + 20, 4, height - 40, fill="green", radius=2),
    ]


def group_header(x, y, width, subject, count, expanded):
    name = {"english": "英语", "chinese": "语文", "math": "数学"}[subject]
    parts = subject_mark(x + 16, y + 15, subject)
    parts += [
        text(x + 62, y + 39, name, size=16, weight=600),
        text(x + 62 + (38 if len(name) == 2 else 45), y + 39, f"{count}项", size=13, color="muted"),
        f'<path d="M{x+width-34} {y+(39 if expanded else 34)}l6 {-6 if expanded else 6} 6 {6 if expanded else -6}" fill="none" stroke="{PALETTE["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    return parts


def item_row(x, y, width, title, reviewed, previous, date, status, *, active=False):
    # Synthetic examples deliberately avoid children's real learning records.
    room = width - 100
    lines = []
    current = ""
    for character in title:
        if len(current) >= max(9, int(room / 16)):
            lines.append(current)
            current = ""
        current += character
    if current:
        lines.append(current)
    height = 105 + max(0, len(lines) - 1) * 24
    parts = []
    for index, row in enumerate(lines):
        parts.append(text(x + 16, y + 24 + index * 24, row, size=15, weight=600))
    parts += more_button(x + width - 60, y + 10, active)
    meta_y = y + 50 + max(0, len(lines) - 1) * 24
    parts += [
        text(x + 16, meta_y, f"已复习{reviewed}次 · 上次{previous}", size=14, color="secondary"),
        text(x + 16, meta_y + 25, f"建议{date}", size=14, color="muted"),
        text(x + width - 16, meta_y + 25, status, size=14, color="green" if status == "今日已安排" else "muted", anchor="end"),
    ]
    return parts, height


def time_filter(x, width):
    half = width / 2
    return [
        rect(x, 174, width, 48, fill="paper", radius=14, stroke="line"),
        rect(x + 3, 177, half - 6, 42, fill="tint", radius=11),
        text(x + half / 2, 203, "明天 10月11日", size=13.5, color="green", weight=600, anchor="middle"),
        text(x + half * 1.5, 203, "后天 10月12日", size=13.5, color="secondary", anchor="middle"),
    ]


def select_filter(x, width, label, value):
    return [
        rect(x, 174, width, 48, fill="paper", radius=14, stroke="line"),
        text(x + 15, 204, label, size=13, color="muted"),
        text(x + 69, 204, value, size=14, color="ink", weight=600),
        f'<path d="M{x+width-30} 195l6 6 6-6" fill="none" stroke="{PALETTE["secondary"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    ]


def summary(x, width, heading, count, note=None):
    parts = [text(x, 260, heading, size=20, family=SERIF, weight=600), text(x + width, 259, count, size=13, color="muted", anchor="end")]
    if note:
        parts.append(text(x, 287, note, size=12.5, color="muted"))
    return parts


def time_screen(parts, x, width, height, show_menu):
    parts += time_filter(x, width)
    parts += summary(x, width, "预计 4 项", "约 14 分钟", "实际安排会随今天的复习反馈更新")
    top = 307
    row1, h1 = item_row(x, top + 63, width, "大写英文字母辨认", 3, "9月28日", "10月7日", "今日已安排", active=show_menu)
    row2, h2 = item_row(x, top + 63 + h1, width, "节日词汇与短句认读", 1, "10月9日", "10月12日", "尚未到建议日")
    card_height = 63 + h1 + h2 + 5
    parts += card_base(x, top, width, card_height)
    parts += group_header(x, top, width, "english", 2, True)
    parts.append(line(x + 16, top + 62, x + width - 16, top + 62))
    parts += row1
    parts.append(line(x + 16, top + 63 + h1, x + width - 16, top + 63 + h1))
    parts += row2
    second = top + card_height + 14
    parts += card_base(x, second, width, 66)
    parts += group_header(x, second, width, "chinese", 1, False)
    third = second + 80
    if third + 66 <= height - 10:
        parts += card_base(x, third, width, 66)
        parts += group_header(x, third, width, "math", 1, False)
    if show_menu:
        menu_width = min(224, width - 40)
        menu_x = x + width - menu_width - 10
        compact = height <= 600
        menu_y = top + (117 if compact else 126)
        menu_height = 138 if compact else 156
        row_height = 46 if compact else 52
        parts.append(f'<g filter="url(#paper-shadow)">{rect(menu_x, menu_y, menu_width, menu_height, fill="paper", radius=14, stroke="line")}</g>')
        parts += [
            text(menu_x + 18, menu_y + 30, "加入明天复习", size=14, color="ink"),
            line(menu_x + 12, menu_y + row_height, menu_x + menu_width - 12, menu_y + row_height),
            text(menu_x + 18, menu_y + row_height + 30, "改到后天复习", size=14, color="muted"),
            line(menu_x + 12, menu_y + row_height * 2, menu_x + menu_width - 12, menu_y + row_height * 2),
            text(menu_x + 18, menu_y + row_height * 2 + 30, "删除条目", size=14, color="danger"),
        ]


def flat_subject_screen(parts, x, width):
    parts += select_filter(x, width, "科目", "英语 · 16项")
    parts += summary(x, width, "16 个知识条目", "按复习次数排序")
    rows = [
        ("大写英文字母辨认", 3, "9月28日", "10月12日", "尚未到建议日"),
        ("节日词汇与短句认读", 1, "10月9日", "10月13日", "尚未到建议日"),
        ("字母N与n的书写练习", 1, "10月9日", "10月12日", "尚未到建议日"),
        ("阅读后识别自然段并复述内容", 0, "尚未复习", "10月11日", "等待安排"),
    ]
    y = 292
    rendered = []
    for row in rows:
        content, h = item_row(x, y + 1, width, *row)
        rendered.append((y, content))
        y += h
    parts += [f'<g filter="url(#paper-shadow)">{rect(x, 292, width, y - 292, fill="paper", radius=20, stroke="line")}</g>']
    for index, (top, content) in enumerate(rendered):
        if index:
            parts.append(line(x + 16, top, x + width - 16, top))
        parts += content


def count_screen(parts, x, width):
    parts += select_filter(x, width, "次数", "已复习 1 次")
    parts += summary(x, width, "12 个知识条目", "按科目浏览")
    top = 292
    row1, h1 = item_row(x, top + 63, width, "节日词汇与短句认读", 1, "10月9日", "10月13日", "尚未到建议日")
    row2, h2 = item_row(x, top + 63 + h1, width, "字母N与n的书写练习", 1, "10月9日", "10月12日", "尚未到建议日")
    card_height = 63 + h1 + h2 + 5
    parts += card_base(x, top, width, card_height)
    parts += group_header(x, top, width, "english", 5, True)
    parts.append(line(x + 16, top + 62, x + width - 16, top + 62))
    parts += row1
    parts.append(line(x + 16, top + 63 + h1, x + width - 16, top + 63 + h1))
    parts += row2
    second = top + card_height + 14
    parts += card_base(x, second, width, 66)
    parts += group_header(x, second, width, "chinese", 4, False)
    third = second + 80
    parts += card_base(x, third, width, 66)
    parts += group_header(x, third, width, "math", 3, False)


def render(state, width, height):
    parts, gutter, span = shell(width, height, state)
    if state in {"time", "actions"}:
        time_screen(parts, gutter, span, height, state == "actions")
    elif state == "subject":
        flat_subject_screen(parts, gutter, span)
    elif state == "count":
        count_screen(parts, gutter, span)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    for width, height in [(320, 568), (390, 844), (430, 932)]:
        for state in ("time", "subject", "count", "actions"):
            (ROOT / f"{state}-{width}x{height}.svg").write_text(render(state, width, height), encoding="utf-8")
