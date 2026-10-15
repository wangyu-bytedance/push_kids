"""Synthetic editable design previews, not native geometry evidence."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261014-TODAY-ACTION-STYLE-01"
OUT.mkdir(parents=True, exist_ok=True)
sources, rows = [], []
for w, h in [(320, 568), (390, 844), (430, 932)]:
    for state in ["content", "completed", "pending"]:
        svg = HERE / f"{state}-{w}x{h}.svg"
        png = OUT / f"{state}-{w}x{h}.png"
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="#FAF7F0"/>']
        for y, title, label in [(80, "复习安排", "完成"), (290, "每日任务 · 阅读", "撤销" if state == "completed" else "完成")]:
            parts.append(f'<rect x="16" y="{y}" width="{w-32}" height="170" rx="24" fill="#FFFDF8"/><text x="32" y="{y+36}" font-family="PingFang SC,sans-serif" font-size="16" fill="#28382f">{title}</text>')
            fill, ink = ("#e4ede6", "#1F5B45") if label == "撤销" else ("#1F5B45", "#FFFDF8")
            x = w - 118
            parts.append(f'<rect x="{x}" y="{y+75}" width="86" height="44" rx="22" fill="{fill}"/><text x="{x+43}" y="{y+103}" text-anchor="middle" font-family="PingFang SC,sans-serif" font-size="14" fill="{ink}">{"◌ " if state == "pending" else ""}{label}</text>')
        parts.append('</svg>')
        svg.write_text(''.join(parts))
        subprocess.run(['rsvg-convert', str(svg), '-o', str(png)], check=True)
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        sources.append(f'{svg.relative_to(ROOT)}={digest(svg)}')
        rows.append(f'| {png.name} | {state} | {w}x{h} | 1x | {digest(png)} | 合成数据，仅说明圆角/阴影；原生另验 |')
base = 'docs/design/frontend/prototypes/DREV-20261014-TODAY-ACTION-STYLE-01/'
(OUT / 'APPROVAL.md').write_text('# 今日完成按钮统一候选\n\n- Status: AWAITING_APPROVAL\n- UI ID: UI-001\n- Design Revision: DREV-20261014-TODAY-ACTION-STYLE-01\n- Frontend baseline revision: FDB-20260913-04\n- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02\n- Task Spec path and revision: specs/active/FEAT-010-TODAY-ACTION-STYLE.md#SPEC-20261014-TODAY-ACTION-STYLE-01\n- Frontend spec path: '+base+'FRONTEND-SPEC.md\n- Editable design source path(s): '+'; '.join(s.split('=')[0] for s in sources)+'\n- Editable source SHA-256: '+'; '.join(sources)+'\n- Approved by: pending\n- Approved at: pending\n\n## Export manifest\n\n| File | State | Viewport | Scale | SHA-256 | Notes |\n|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n')
