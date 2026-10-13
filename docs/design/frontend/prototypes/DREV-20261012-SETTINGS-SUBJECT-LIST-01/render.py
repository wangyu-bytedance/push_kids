"Synthetic design candidates; never native Mini Program acceptance evidence."

import hashlib
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
OUT = REPO / "docs/design/frontend/snapshots/UI-001" / ROOT.name
STATES = ("content", "unselected", "readonly", "pending", "long-name", "error")


def render(width, height, state):
    p = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}"'
            f' height="{height}" viewBox="0 0 {width} {height}">'
        ),
        '<rect width="100%" height="100%" fill="#FAF7F0"/>',
    ]

    def text(x, y, value, size=14, color="#22261F", weight=400):
        p.append(
            f'<text x="{x}" y="{y}" font-family="PingFang SC,sans-ser'
            f'if" font-size="{size}" fill="{color}" font-weight="{weight}'
            f'">{escape(value)}</text>'
        )

    def box(x, y, w, h, color="#FFFDF8", r=16):
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{color}"/>')

    text(20, 32, "知芽", 18, "#1F5B45", 600)
    text(20, 73, "按你们的节奏来", 22, weight=600)
    y = 96
    if state in ("readonly", "error"):
        box(16, y, width - 32, 52, "#F0F5F0" if state == "readonly" else "#F7E8E2", 12)
        text(
            28,
            y + 22,
            "只读成员，改动需要管理员操作" if state == "readonly" else "加载失败，已读设置仍可查看",
            14,
        )
        text(28, y + 42, "可以查看当前科目" if state == "readonly" else "重新加载", 14, "#1F5B45")
        y += 64

    def card(title, rows, add, start, subtitle=""):
        row_heights = [76 if len(n) > 12 else 64 for n, _, _ in rows]
        h = 54 + sum(row_heights) + (48 if state != "readonly" else 12) + (22 if subtitle else 0)
        box(16, start, width - 32, h)
        text(30, start + 30, title, 17, weight=600)
        ry = start + 44
        if subtitle:
            text(30, ry + 12, subtitle, 13, "#79826F")
            ry += 22
        for (name, meta, action), rh in zip(rows, row_heights, strict=False):
            box(30, ry + 14, 32, 32, "#E4EDE6", 8)
            p.append(
                f'<path d="M39 {ry + 23}h7l4 3v13l-4 -3h-7z M46 {ry + 23}'
                f'v13" fill="none" stroke="#1F5B45" stroke-width="1.5"/>'
            )
            if len(name) > 12:
                text(74, ry + 23, name[:10], 16)
                text(74, ry + 43, name[10:], 16)
            else:
                text(74, ry + 26, name, 16)
            text(74, ry + rh - 12, meta, 14, "#79826F")
            if action:
                text(width - 74, ry + 34, action, 14, "#1F5B45" if action == "加入" else "#464E43")
            ry += rh
            p.append(f'<path d="M30 {ry}H{width - 30}" stroke="#F1ECE0"/>')
        if state != "readonly":
            text(30, ry + 31, "＋ " + add, 14, "#1F5B45")
        return start + h + 12

    rows = [
        (
            "数学",
            "未加入" if state == "unselected" else "在学",
            "加入" if state == "unselected" else "移出",
        ),
        ("语文", "在学", "移出中…" if state == "pending" else "移出"),
        ("英语", "在学", "移出"),
    ]
    if state == "long-name":
        rows.append(("中国传统文化与古诗词阅读", "自定义 · 在学", "移出"))
    if state == "readonly":
        rows = [(n, m, "") for n, m, a in rows]
    y = card("在学科目", rows, "添加其他科目", y)
    y = card("课外活动", [("游泳", "周六 10:00–11:00", "›")], "添加课外活动", y)
    card(
        "出行安排",
        [("上学", "周一至周五 07:30–08:00", "›")],
        "添加出行安排",
        y,
        "只显示在日程，不生成待办",
    )
    box(0, height - 54, width, 54, "#FFFDF8", 0)
    for i, label in enumerate(("今日", "日程", "记录", "报表", "设置")):
        text(width * (i + 0.5) / 5 - 14, height - 20, label, 14, "#1F5B45" if i == 4 else "#79826F")
    p.append("</svg>")
    return "\n".join(p)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = []
    hashes = []
    rows = []
    for state in STATES:
        for w, h in ((320, 568), (390, 844), (430, 932)):
            name = f"{state}-{w}x{h}"
            svg = ROOT / f"{name}.svg"
            png = OUT / f"{name}.png"
            svg.write_text(render(w, h, state))
            subprocess.run(["rsvg-convert", "--output", str(png), str(svg)], check=True)
            path = str(svg.relative_to(REPO))
            sources.append(path)
            hashes.append(path + "=" + hashlib.sha256(svg.read_bytes()).hexdigest())
            rows.append(
                f"| {png.name} | {state} | {w}x{h} | "
                f"1x | {hashlib.sha256(png.read_bytes()).hexdigest()}"
                f" | 合成数据；可纵向滚动，底部遮挡代表首屏外内容 |"
            )
    metadata = (
        f"""# UI-001 设置科目统一列表候选设计

- Status: AW"""
        f"""AITING_APPROVAL
- UI ID: UI-001
- D"""
        f"""esign Revision: {ROOT.name}
- Front"""
        f"""end baseline revision: FDB-20260913"""
        f"""-04
- Frontend engineering revision"""
        f""": FEC-20261007-NATIVE-GEOMETRY-02
-"""
        f""" Task Spec path and revision: specs"""
        f"""/active/FEAT-001-SETTINGS-SUBJECT-L"""
        f"""IST.md#SPEC-20261012-SETTINGS-SUBJE"""
        f"""CT-LIST-01
- Frontend spec path: {ROOT.relative_to(REPO)}"""
        f"""/FRONTEND-SPEC.md
- Editable design"""
        f""" source path(s): {"; ".join(sources)}"""
        f"""
- Editable source SHA-256: {"; ".join(hashes)}"""
        f"""
- Approved by: PENDING
- Approved """
        f"""at: PENDING
- Approval evidence: PE"""
        f"""NDING — 等待用户确认具体 Spec + DREV

## Ex"""
        f"""port manifest

| File | Viewport/st"""
        f"""ate | CSS viewport | Scale/DPR | SH"""
        f"""A-256 | Notes |
|---|---|---|---|--"""
        f"""-|---|
"""
    )
    (OUT / "APPROVAL.md").write_text(
        metadata
        + "\n".join(rows)
        + "\n\n原生节点矩形、交互、iOS/Android NOT_RUN。此处为设计候选图，未修改生产代码。\n"
    )


if __name__ == "__main__":
    main()
