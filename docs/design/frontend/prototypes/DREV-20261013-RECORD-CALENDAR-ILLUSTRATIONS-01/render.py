"Editable synthetic design exports; native runtime evidence is separate."

import hashlib
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
OUT = REPO / "docs/design/frontend/snapshots/UI-001" / ROOT.name
VIEWS = ((320, 568), (390, 844), (430, 932))
STATES = {
    "records": ("empty", "photos", "readonly", "error"),
    "calendar": ("content", "empty", "error", "long-name"),
}


def render(w, h, page, state):
    parts = [
        (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'),
        (
            '<defs><linearGradient id="paper"><stop stop-color="#FFF'
            'EFA"/><stop offset="1" stop-color="#F7F4EA"/></linearGr'
            'adient><radialGradient id="glow" cx="1" cy="0" r=".9"><'
            'stop stop-color="#7FA65C" stop-opacity=".16"/><stop off'
            'set="1" stop-color="#7FA65C" stop-opacity="0"/></radial'
            "Gradient></defs>"
        ),
        '<rect width="100%" height="100%" fill="#FAF7F0"/>',
    ]

    def text(x, y, value, size=14, color="#22261F", weight=400):
        parts.append(
            f'<text x="{x}" y="{y}" font-family="PingFang SC,sans-ser'
            f'if" font-size="{size}" fill="{color}" font-weight="{weight}'
            f'">{escape(value)}</text>'
        )

    def box(x, y, width, height, fill="#FFFDF8", radius=16):
        parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}"'
            f' rx="{radius}" fill="{fill}" stroke="#EBE5D7" stroke-wi'
            f'dth=".5"/>'
        )

    def art(name, x, y, width, height):
        parts.append(
            f'<image href="assets/{name}.png" x="{x}" y="{y}" width="{width}" height="{height}"/>'
        )

    text(w / 2 - 18, 28, "知芽", 18, "#1F5B45", 600)
    box(18, 46, w - 36, 154, "url(#paper)", 26)
    parts.append(f'<rect x="18" y="46" width="{w - 36}" height="154" rx="26" fill="url(#glow)"/>')
    title = ("一笔一画，", "都算数") if page == "records" else ("这一周，", "心里有数")
    text(32, 89, title[0], 24, weight=600)
    text(32, 119, title[1], 24, weight=600)
    box(32, 135, 108, 44, "#FFFDF8", 22)
    text(44, 163, "小满" if state != "long-name" else "很长的孩子…", 14)
    art("record-books" if page == "records" else "calendar-still-life", w - 146, 65, 120, 118)
    y = 216
    if state == "error":
        box(18, y, w - 36, 48, "#F7E8E2", 12)
        text(30, y + 29, "加载失败，已读内容仍可查看", 14)
        y += 60
    if page == "records":
        if state == "readonly":
            box(18, y, w - 36, 64)
            text(30, y + 27, "历史记录已放在报表中", 14)
            text(30, y + 50, "前往查看", 14, "#1F5B45")
        else:
            box(18, y, w - 36, 68)
            text(30, y + 24, "实际学习时间", 14, "#79826F")
            text(30, y + 47, "2026-10-13 · 19:20", 15, weight=600)
            text(w - 70, y + 42, "修改", 14, "#1F5B45")
            y += 94
            text(18, y, "学习照片", 16, weight=600)
            text(w - 54, y, "0 / 9" if state != "photos" else "1 / 9", 14, "#79826F")
            y += 14
            if state == "photos":
                box(18, y, 88, 100, "#E4EDE6")
                text(30, y + 54, "合成照片", 14)
                text(124, y + 55, "继续添加", 14, "#1F5B45")
                y += 114
            else:
                box(18, y, w - 36, 178, "url(#paper)", 24)
                art("record-camera", w / 2 - 75, y + 2, 150, 104)
                text(w / 2 - 56, y + 127, "添加学习照片", 16, "#14402F", 600)
                text(w / 2 - 70, y + 153, "拍摄或从相册选择", 14, "#79826F")
                y += 202
            text(18, y, "学习内容", 16, weight=600)
            y += 14
            box(18, y, w - 36, 100)
            text(30, y + 30, "可补充照片里不明显的内容", 14, "#79826F")
            text(w - 56, y + 80, "语音", 14, "#1F5B45")
    else:
        box(18, y, w - 36, 150)
        text(w / 2 - 51, y + 32, "2026年10月", 17, weight=600)
        text(32, y + 32, "‹", 20)
        text(w - 44, y + 32, "›", 20)
        for i, day in enumerate("一二三四五六日"):
            x = 32 + i * (w - 64) / 7
            if i == 1:
                box(x - 3, y + 60, (w - 64) / 7 - 4, 70, "#1F5B45", 12)
            text(x + 6, y + 83, day, 14, "#FFFDF8" if i == 1 else "#79826F")
            text(x + 3, y + 113, str(12 + i), 17, "#FFFDF8" if i == 1 else "#22261F")
        y += 182
        text(18, y, "今天 · 10月13日", 17, weight=600)
        y += 18
        if state == "empty":
            box(18, y, w - 36, 120)
            text(38, y + 48, "这天还没有安排", 17)
            text(38, y + 80, "固定活动和出行会自动出现", 14, "#79826F")
        else:
            for title, time in [
                ("游泳课" if state != "long-name" else "很长的活动名称换行展示", "16:30–17:30"),
                ("回家", "18:00–18:30"),
            ]:
                box(18, y, w - 36, 94)
                text(32, y + 30, title, 16, weight=600)
                text(32, y + 55, time, 14, "#79826F")
                text(32, y + 80, "记录这次练习" if title != "回家" else "出行安排", 14, "#1F5B45")
                y += 110
    box(0, h - 54, w, 54, radius=0)
    for i, label in enumerate(("今日", "日程", "记录", "报表", "设置")):
        text(
            w * (i + 0.5) / 5 - 14,
            h - 20,
            label,
            14,
            "#1F5B45" if i == ({"records": 2, "calendar": 1}[page]) else "#79826F",
        )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = []
    hashes = []
    rows = []
    for page, states in STATES.items():
        for state in states:
            for w, h in VIEWS:
                name = f"{page}-{state}-{w}x{h}"
                svg = ROOT / f"{name}.svg"
                png = OUT / f"{name}.png"
                svg.write_text(render(w, h, page, state))
                subprocess.run(["rsvg-convert", "--output", str(png), str(svg)], check=True)
                path = str(svg.relative_to(REPO))
                sources.append(path)
                hashes.append(path + "=" + hashlib.sha256(svg.read_bytes()).hexdigest())
                rows.append(
                    f"| {png.name} | {page}-{state} | {w}"
                    f"x{h} | 1x | {hashlib.sha256(png.read_bytes()).hexdigest()}"
                    f" | 合成设计；原生验收另记 |"
                )
    asset_hashes = [
        "| " + asset.name + " | " + hashlib.sha256(asset.read_bytes()).hexdigest() + " |"
        for asset in sorted((ROOT / "assets").glob("*.png"))
    ]
    metadata = (
        f"""# UI-001 — 记录与日程插画方案批准清单

- Status:"""
        f""" APPROVED
- UI ID: UI-001
- Design """
        f"""Revision: {ROOT.name}
- Frontend ba"""
        f"""seline revision: FDB-20260913-04
- """
        f"""Frontend engineering revision: FEC-"""
        f"""20261007-NATIVE-GEOMETRY-02
- Task """
        f"""Spec path and revision: specs/activ"""
        f"""e/FEAT-001-RECORD-CALENDAR-ILLUSTRA"""
        f"""TIONS.md#SPEC-20261013-RECORD-CALEN"""
        f"""DAR-ILLUSTRATIONS-01
- Frontend spe"""
        f"""c path: {ROOT.relative_to(REPO)}/FR"""
        f"""ONTEND-SPEC.md
- Editable design so"""
        f"""urce path(s): {"; ".join(sources)}
"""
        f"""- Editable source SHA-256: {"; ".join(hashes)}"""
        f"""
- Approved by: 用户
- Approved at: 2"""
        f"""026-10-13
- Approval evidence: 本会话两"""
        f"""张记录/日程效果图后“好的 按照这个方案进行落地”；按既有文案、导航和"""
        f"""操作归一，不批准生成器额外宣传文案。
- Superseded by:"""
        f""" N/A

## Export manifest

| File | """
        f"""Viewport/state | CSS viewport | Sca"""
        f"""le/DPR | SHA-256 | Notes |
|---|---"""
        f"""|---|---|---|---|
"""
    )
    (OUT / "APPROVAL.md").write_text(
        metadata
        + "\n".join(rows)
        + "\n\n## Asset hashes\n\n| Asset | SHA-256 |\n|---|---|\n"
        + "\n".join(asset_hashes)
        + (
            "\n\n设计导出不是原生验收；原生、设备与交互结果见quality evidence。"
            "批准后不修改本清单除Supe"
            "rseded by。\n"
        )
    )


if __name__ == "__main__":
    main()
