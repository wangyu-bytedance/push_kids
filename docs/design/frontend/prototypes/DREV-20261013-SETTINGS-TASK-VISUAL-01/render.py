"""Editable synthetic design sources; these are not native acceptance evidence."""
from pathlib import Path
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'docs/design/frontend/snapshots/UI-001/DREV-20261013-SETTINGS-TASK-VISUAL-01'
OUT.mkdir(parents=True, exist_ok=True)
rows = []
sources = []
for w, h in [(320, 568), (390, 844), (430, 932)]:
    for state in ['content', 'empty', 'readonly', 'form', 'error', 'pending']:
        c = w - 32
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><radialGradient id="paper" cx="95%" cy="0%" r="100%"><stop stop-color="#e7eddd"/><stop offset="1" stop-color="#fbf9f1"/></radialGradient></defs>', f'<rect width="{w}" height="{h}" fill="#f8f7f1"/>']
        def text(x, y, s, size=14, color='#313c35'):
            parts.append(f'<text x="{x}" y="{y}" font-family="PingFang SC,sans-serif" font-size="{size}" fill="{color}">{s}</text>')
        def box(x,y,bw,bh,fill='#fffdf7',r=20):
            parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="{r}" fill="{fill}" stroke="#e5e7de"/>')
        text(20,30,'设置',20)
        box(16,48,c,72); text(34,78,'课外活动',17); text(34,101,'游泳 · 每周六',14,'#748075')
        box(16,136,c,h-160,'url(#paper)',24)
        text(34,170,'每日任务',18); text(34,195,'每天重复',14,'#738478'); text(34,216,'目标时长以分钟设置',14,'#738478')
        ax=w-109
        parts.append(f'<g transform="translate({ax},154) rotate(7 35 35)"><rect x="4" y="7" width="59" height="68" rx="9" fill="#d7dfca"/><rect width="59" height="68" rx="9" fill="#fffdf6" stroke="#a9bda6"/><rect x="15" y="-4" width="29" height="12" rx="4" fill="#b7ccb4"/><path d="M10 24l4 4 7-8 M10 41l4 4 7-8" fill="none" stroke="#4e8066" stroke-width="2"/><path d="M27 25h21 M27 42h21" stroke="#c5cdbe" stroke-width="3"/><path d="M59 58l14-48 5 2-14 48z" fill="#cba66a"/><path d="M66 71q27-19 17-32q-18 0-17 32" fill="#86a788" opacity=".7"/></g>')
        y=238
        if state!='readonly':
            for i,s in enumerate(['阅读','跳绳','练字','户外运动']):
                x=34+(i%2)*((c-36)/2); yy=y+(i//2)*52
                box(x,yy,(c-48)/2,44,'#edf2e8',12); text(x+12,yy+28,s,14,'#245c46')
            y+=112
        if state=='empty':
            text(34,y+30,'还没有每日任务',14,'#7d877c'); y+=54
        elif state in ['form','error','pending']:
            text(34,y+16,'任务名称'); box(34,y+27,c-36,44,'#fffdf8',12); text(46,y+55,'阅读'); y+=86
            text(34,y+16,'目标时长（分钟）'); box(34,y+27,c-36,44,'#fffdf8',12); text(46,y+55,'20'); y+=86
            if state=='error': text(34,y+15,'保存失败，请重试',14,'#a04436'); y+=28
            box(34,y,c-36,44,'#205d46',12); text(48,y+28,'保存中…' if state=='pending' else '保存任务',14,'#fff')
        else:
            for name,mins in [('阅读','20'),('跳绳','10')]:
                box(34,y+8,36,36,'#e5eddf',10); text(45,y+32,'✓',18,'#3e7659'); text(82,y+24,name,16); text(82,y+47,f'每天 {mins} 分钟',14,'#7b857a')
                if state!='readonly': box(w-88,y+7,54,44,'#fffdf6',12); text(w-75,y+35,'编辑',14,'#416b53')
                y+=68
        if state not in ['readonly','form','error','pending']:
            text(34,y+32,'＋ 添加自定义任务',15,'#245c46')
        parts.append('</svg>')
        name=f'daily-task-{state}-{w}x{h}'
        svg=HERE/f'{name}.svg'; svg.write_text(''.join(parts))
        png=OUT/f'{name}.png'
        subprocess.run(['rsvg-convert',str(svg),'-o',str(png)],check=True)
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        sources.append(f'{svg.relative_to(ROOT)}={digest(svg)}')
        rows.append(f'| {png.name} | {state} | {w}x{h} | 1x | {digest(png)} | 合成设计，长表单纵向滚动；原生另验 |')
(OUT/'APPROVAL.md').write_text('# 每日任务设置设计候选\n\n- Status: AWAITING_APPROVAL\n- Task Spec: SPEC-20261013-SETTINGS-TASK-VISUAL-01\n- Design Revision: DREV-20261013-SETTINGS-TASK-VISUAL-01\n- Baseline: FDB-20260913-04\n- Engineering: FEC-20261007-NATIVE-GEOMETRY-02\n- Source SHA-256: '+'; '.join(sources)+'\n- Approval evidence: pending\n\n| File | State | Viewport | Scale | SHA-256 | Notes |\n|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n')
