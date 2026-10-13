"""Editable design candidate; synthetic previews are not native acceptance evidence."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261013-SETTINGS-CONSISTENCY-01"
OUT.mkdir(parents=True, exist_ok=True)
if (OUT / "APPROVAL.md").exists() and "- Status: APPROVED" in (OUT / "APPROVAL.md").read_text():
    raise SystemExit("Approved design evidence is immutable; create a new revision to regenerate.")
sources, rows = [], []
for w, h in [(320, 568), (390, 844), (430, 932)]:
    for state in ["content", "subjects", "empty", "readonly", "catalog", "form", "error", "pending", "long-name", "no-art"]:
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><defs><radialGradient id="paper" cx="95%" cy="0%" r="100%"><stop stop-color="#e7eddd"/><stop offset="1" stop-color="#fffdf8"/></radialGradient></defs><rect width="{w}" height="{h}" fill="#FAF7F0"/>']
        def text(x, y, s, size=14, color="#28382f"):
            p.append(f'<text x="{x}" y="{y}" font-family="PingFang SC,sans-serif" font-size="{size}" fill="{color}">{s}</text>')
        def rect(x, y, bw, bh, fill, radius=12):
            p.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="{radius}" fill="{fill}"/>')
        def art(y, kind):
            if state == "no-art":
                return
            x = w - 112
            p.append(f'<g transform="translate({x},{y})" opacity=".8"><ellipse cx="39" cy="58" rx="42" ry="8" fill="#d8e2ce"/>')
            if kind == "activity":
                p.append('<circle cx="32" cy="35" r="23" fill="#d8bc86"/><path d="M10 32q22 10 44 0M32 12q-14 24 0 46M32 12q14 24 0 46" stroke="#a88d5b" fill="none"/><path d="M56 56q30-43 5-46" stroke="#7b9d7a" stroke-width="4" fill="none"/>')
            else:
                p.append('<path d="M4 22l31-5 10 36-32 7z" fill="#98b391"/><path d="M13 16l32-4 10 35-33 7z" fill="#e4d4ac"/><path d="M20 23l22-3M23 30l21-3M26 37l16-2" stroke="#fffdf8" stroke-width="3"/>')
                if kind == "daily":
                    p.append('<circle cx="60" cy="40" r="20" fill="#fffdf8" stroke="#96b197" stroke-width="3"/><path d="M60 27v14l9 5" fill="none" stroke="#1F5B45" stroke-width="2"/>')
                else:
                    p.append('<path d="M62 58V26q-22-13-19 0q2 10 19 9q19-25 25-13q4 13-25 17" stroke="#6c9671" fill="none" stroke-width="3"/>')
            p.append('</g>')
        def card(y, title, subtitle, entries, kind):
            height = 94 + len(entries) * 64 + (0 if state == "readonly" else 54)
            rect(16, y, w - 32, height, "url(#paper)", 24)
            text(32, y + 35, title, 18)
            text(32, y + 60, subtitle, 14, "#6b7868")
            art(y + 8, kind)
            yy = y + 84
            for name, sub, action in entries:
                rect(32, yy + 7, 36, 36, "#e3ece0")
                text(43, yy + 32, "✓" if kind == "subject" else "◷", 18, "#1F5B45")
                text(80, yy + 24, name, 16)
                text(80, yy + 46, sub, 14, "#6b7868")
                if state != "readonly":
                    text(w - 65, yy + 32, action, 14, "#1F5B45")
                yy += 64
                p.append(f'<path d="M80 {yy}H{w-32}" stroke="#e4e7dd"/>')
            if state != "readonly":
                text(32, yy + 36, "＋ 添加其他科目" if kind == "subject" else f"＋ 添加{title}", 15, "#1F5B45")
            return y + height + 16
        text(24, 40, "按你们的节奏来", 24)
        y = 64
        if state == "subjects":
            card(y, "在学科目", "记录正在学习的内容", [("数学", "已加入", "移出"), ("语文", "已加入", "移出"), ("英语", "未加入", "加入")], "subject")
        elif state in ["catalog", "form", "error", "pending"]:
            text(24, 90, "添加每日任务" if state == "catalog" else "编辑每日任务", 18)
            if state == "catalog":
                for i, (name, mins) in enumerate([("阅读", 20), ("跳绳", 10), ("练字", 20), ("户外运动", 20)]):
                    rect(16, 112 + i * 64, w - 32, 60, "#FFFDF8")
                    text(32, 137 + i * 64, name, 16)
                    text(32, 158 + i * 64, f"建议 {mins} 分钟 · 可调整", 14, "#6b7868")
                    text(w - 42, 146 + i * 64, "›", 20)
                text(32, 402, "＋ 自定义任务", 15, "#1F5B45")
            else:
                text(24, 130, "任务名称")
                rect(24, 144, w - 48, 48, "#FFFDF8")
                text(36, 174, "阅读", 16)
                text(24, 226, "目标时长（分钟）")
                rect(24, 240, w - 48, 48, "#FFFDF8")
                text(36, 270, "20", 16)
                if state == "error":
                    text(24, 320, "保存失败，输入已保留，请重试", 14, "#a04436")
                rect(24, 346, w - 48, 48, "#1F5B45")
                text(40, 376, "保存中…" if state == "pending" else "保存任务", 16, "#fffdf8")
                text(24, 430, "取消", 16, "#1F5B45")
        else:
            y = card(y, "课外活动", "让兴趣慢慢长大", [("游泳", "每周六 · 15:00–16:00", "›")], "activity")
            entries = [] if state == "empty" else [("阅读", "每天 20 分钟", "›"), ("跳绳", "每天 10 分钟", "›")]
            if state == "long-name":
                entries = [("每日阅读与摘抄", "每天 20 分钟", "›")]
            card(y, "每日任务", "每天重复 · 按自己的节奏", entries, "daily")
        p.append('</svg>')
        name = f"{state}-{w}x{h}"
        svg, png = HERE / f"{name}.svg", OUT / f"{name}.png"
        svg.write_text("".join(p))
        subprocess.run(["rsvg-convert", str(svg), "-o", str(png)], check=True)
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        sources.append(f"{svg.relative_to(ROOT)}={digest(svg)}")
        rows.append(f"| {png.name} | {state} | {w}x{h} | 1x | {digest(png)} | 合成设计；原生另验 |")
(OUT / "APPROVAL.md").write_text("# 设置统一设计候选\n\n- Status: AWAITING_APPROVAL\n- Task Spec: SPEC-20261013-SETTINGS-CONSISTENCY-01\n- Design Revision: DREV-20261013-SETTINGS-CONSISTENCY-01\n- Baseline: FDB-20260913-04\n- Engineering: FEC-20261007-NATIVE-GEOMETRY-02\n- Source SHA-256: " + "; ".join(sources) + "\n- Approval evidence: pending\n\n| File | State | Viewport | Scale | SHA-256 | Notes |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
manifest = OUT / "APPROVAL.md"
content = manifest.read_text().replace("- Baseline:", "- Frontend baseline revision:").replace("- Engineering:", "- Frontend engineering revision:").replace("- Source SHA-256:", "- Editable source SHA-256:").replace("\n| File |", "\n## Export manifest\n\n| File |")
metadata = "\n- UI ID: UI-001\n- Task Spec path and revision: specs/active/FEAT-001-SETTINGS-CONSISTENCY.md#SPEC-20261013-SETTINGS-CONSISTENCY-01\n- Frontend spec path: docs/design/frontend/prototypes/DREV-20261013-SETTINGS-CONSISTENCY-01/FRONTEND-SPEC.md\n- Editable design source path(s): " + "; ".join(item.split("=")[0] for item in sources) + "\n- Approved by: pending\n- Approved at: pending\n"
manifest.write_text(content.replace("\n## Export manifest", metadata + "\n## Export manifest"))
