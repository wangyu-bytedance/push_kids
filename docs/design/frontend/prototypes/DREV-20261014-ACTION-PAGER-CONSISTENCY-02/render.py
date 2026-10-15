"""Editable synthetic style proposal; not native evidence."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'docs/design/frontend/snapshots/UI-001/DREV-20261014-ACTION-PAGER-CONSISTENCY-02'
if (OUT / 'APPROVAL.md').exists() and '- Status: APPROVED' in (OUT / 'APPROVAL.md').read_text():
    raise SystemExit('Approved design snapshots are immutable; create a new revision.')
OUT.mkdir(parents=True, exist_ok=True)
sources, rows = [], []
for w, h in [(320,568),(390,844),(430,932)]:
    for state in ['content','completed','pending','last-page','long-page']:
        p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="#FAF7F0"/>']
        def text(x,y,s,color='#28382f',size=14,anchor='start'):
            p.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="PingFang SC,sans-serif" font-size="{size}" fill="{color}">{s}</text>')
        text(24,42,'按钮与分页统一',size=20)
        for y,title in [(64,'复习安排'),(190,'每日任务')]:
            p.append(f'<rect x="16" y="{y}" width="{w-32}" height="110" rx="24" fill="#FFFDF8"/>')
            text(32,y+30,title,size=16)
            label='撤销' if state=='completed' and y==190 else '完成'
            x=w-118
            color='#e4ede6' if label=='撤销' else '#1F5B45'
            p.append(f'<rect x="{x}" y="{y+48}" width="86" height="44" rx="22" fill="{color}"/>')
            text(x+43,y+76,('◌ ' if state=='pending' else '')+label,'#1F5B45' if label=='撤销' else '#FFFDF8',anchor='middle')
        text(24,342,'编辑计划 · 分页',size=16)
        left, inner = 24,w-48
        side=(inner-64-16)/2
        for x,label,disabled in [(left,'回到首页',state in ['content','pending']), (left+side+80,'下一页',state in ['last-page','pending'])]:
            fill='#F3EFE4' if disabled else '#e4ede6'
            p.append(f'<rect x="{x}" y="366" width="{side}" height="44" rx="12" fill="{fill}"/>')
            text(x+side/2,394,label,'#8d9386' if disabled else '#1F5B45',anchor='middle')
        page='999999' if state=='long-page' else '8' if state=='last-page' else '1' if state=='content' else '2'
        if state=='long-page':
            text(w/2,386,'第 '+page,size=14,anchor='middle');text(w/2,404,'页',anchor='middle')
        else:
            text(w/2,394,'第 '+page+' 页',anchor='middle')
        text(24,450,'首页 / 末页 / 加载中：保留位置，明确禁用',size=12,color='#6b7868')
        p.append('</svg>')
        name=f'{state}-{w}x{h}';svg=HERE/(name+'.svg');png=OUT/(name+'.png')
        svg.write_text(''.join(p));subprocess.run(['rsvg-convert',str(svg),'-o',str(png)],check=True)
        digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
        sources.append(f'{svg.relative_to(ROOT)}={digest(svg)}')
        rows.append(f'| {png.name} | {state} | {w}x{h} | 1x | {digest(png)} | 合成局部样式；原生另验 |')
base='docs/design/frontend/prototypes/DREV-20261014-ACTION-PAGER-CONSISTENCY-02/'
(OUT/'APPROVAL.md').write_text('# 按钮与分页统一候选\n\n- Status: AWAITING_APPROVAL\n- UI ID: UI-001\n- Design Revision: DREV-20261014-ACTION-PAGER-CONSISTENCY-02\n- Frontend baseline revision: FDB-20260913-04\n- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02\n- Task Spec path and revision: specs/active/FEAT-010-TODAY-ACTION-STYLE.md#SPEC-20261014-ACTION-PAGER-CONSISTENCY-02\n- Frontend spec path: '+base+'FRONTEND-SPEC.md\n- Editable design source path(s): '+'; '.join(s.split('=')[0] for s in sources)+'\n- Editable source SHA-256: '+'; '.join(sources)+'\n- Approval evidence: pending\n- Approved by: pending\n- Approved at: pending\n\n## Export manifest\n\n| File | State | Viewport | Scale | SHA-256 | Notes |\n|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n')
