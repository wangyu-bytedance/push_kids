"""Generate editable proposal exports; not native acceptance evidence."""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261014-SUBJECT-MANAGEMENT-01"
OUT.mkdir(parents=True, exist_ok=True)
manifest = OUT / "APPROVAL.md"
if manifest.exists() and "Status: APPROVED" in manifest.read_text():
    raise SystemExit("Approved evidence is immutable")
rows = []
for w, h in [(320, 568), (390, 844), (430, 932)]:
    for state in ["list", "panel", "unselected", "confirm", "readonly", "restricted", "pending", "error", "long-name"]:
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#FAF7F0"/>']
        def text(x, y, value, size=14, color="#28382f"):
            p.append(f'<text x="{x}" y="{y}" font-family="PingFang SC,sans-serif" font-size="{size}" fill="{color}">{value}</text>')
        def box(x, y, width, height, fill="#fffdf8"):
            p.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" fill="{fill}"/>')
        text(24, 42, "按你们的节奏来", 24)
        box(16, 66, w-32, 310)
        text(32, 101, "在学科目", 18)
        for i, name in enumerate(["数学", "语文", "英语"]):
            y = 126 + i*64
            p.append(f'<path d="M34 {y+12}h22v22H34z M45 {y+12}v22" fill="none" stroke="#1F5B45" stroke-width="2"/>')
            text(74, y+22, name, 16)
            text(74, y+44, "未加入" if i == 2 else "已加入", 14, "#6b7868")
            if state not in ["readonly", "restricted"]:
                p.append(f'<path d="M{w-43} {y+18}l6 6-6 6" fill="none" stroke="#6b7868" stroke-width="2"/>')
        if state != "readonly":
            text(32, 353, "添加其他科目", 16, "#1F5B45")
        if state not in ["list", "readonly", "restricted"]:
            p.append(f'<rect width="{w}" height="{h}" fill="#000" opacity=".25"/>')
            top = h-350
            box(0, top, w, 350)
            text(24, top+40, "管理科目", 18)
            text(w-58, top+40, "关闭")
            text(24, top+88, "英语" if state == "unselected" else "数学", 18)
            if state == "long-name":
                text(24, top+88, "自定义中文长名称科目")
                text(24, top+113, "延续名称，完整换行显示")
            text(24, top+148, "已有的学习记录会保留。")
            text(24, top+174, "移出后不再出现在选项里。")
            if state == "error":
                text(24, top+215, "移出失败，请重试", 14, "#A6423B")
            box(24, top+246, w-48, 48, "#1F5B45" if state == "unselected" else "#f5ebe7")
            text(40, top+276, "加入此科目" if state == "unselected" else "移出中…" if state == "pending" else "移出此科目", 16, "#fffdf8" if state == "unselected" else "#A6423B")
            if state == "confirm":
                p.append(f'<rect width="{w}" height="{h}" fill="#000" opacity=".25"/>')
                box(24, h//2-105, w-48, 210)
                text(40, h//2-68, "移出「数学」？", 18)
                text(40, h//2-24, "已有的学习记录会保留，")
                text(40, h//2+2, "只是不再出现在选项里。")
                text(44, h//2+70, "取消", 16)
                text(w-82, h//2+70, "移出", 16, "#A6423B")
        p.append('</svg>')
        path = HERE / f"{state}-{w}x{h}.svg"
        path.write_text(''.join(p))
        rows.append(f"| {path.relative_to(ROOT)} | {hashlib.sha256(path.read_bytes()).hexdigest()} |")
manifest.write_text("# 学科管理设计候选\n\n- Status: AWAITING_APPROVAL\n- Task Spec: SPEC-20261014-SUBJECT-MANAGEMENT-01\n- Design Revision: DREV-20261014-SUBJECT-MANAGEMENT-01\n- Frontend baseline revision: FDB-20260913-04\n- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02\n- Approval evidence: PENDING\n- Viewports: 320×568 / 390×844 / 430×932\n- Exports: editable SVG; synthetic proposal, not native acceptance\n\n| Source/export | SHA-256 |\n|---|---|\n" + '\n'.join(rows) + '\n')
