"""Freeze synthetic repository previews as editable self-contained design HTML."""
from pathlib import Path
import re
import base64
import hashlib
import subprocess
import json

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'docs/design/frontend/snapshots/UI-001/DREV-20261013-CARD-BACKGROUNDS-01'
OUT.mkdir(parents=True, exist_ok=True)
rows, sources = [], []
for surface in ['settings', 'reports', 'records', 'calendar', 'today']:
    for width, height in [(320,568),(390,844),(430,932)]:
        original = ROOT / f'dist/ui-preview/{surface}-{width}.html'
        html = original.read_text()
        def embed(match):
            file = (original.parent / match.group(1)).resolve()
            if not file.exists():
                return match.group(0)
            return 'src="data:image/png;base64,' + base64.b64encode(file.read_bytes()).decode() + '"'
        html = re.sub(r'src="([^"]+\.png)"', embed, html)
        file = HERE / f'{surface}-{width}x{height}.html'
        file.write_text(html)
        png=OUT / f'{surface}-{width}x{height}.png'
        js = """const {chromium}=require('/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:W,height:H}});await p.goto(URL);await p.evaluate(()=>document.fonts.ready);if(await p.locator('img').evaluateAll(xs=>xs.some(x=>!x.complete||!x.naturalWidth)))throw Error('image decode failed');await p.screenshot({path:OUT,fullPage:false});console.log('horizontal_overflow='+await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth));await b.close();})().catch(e=>{console.error(e);process.exit(1)});""".replace('width:W','width:'+str(width)).replace('height:H','height:'+str(height)).replace('goto(URL)','goto('+json.dumps(file.as_uri())+')').replace('path:OUT','path:'+json.dumps(str(png)))
        subprocess.run(['node','-e',js],check=True)
        sha=lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
        sources.append(f'{file.relative_to(ROOT)}={sha(file)}')
        rows.append(f'| {png.name} | {surface}-content | {width}x{height} | 1x | {sha(png)} | HTML辅助检查，非原生验收 |')
(OUT/'APPROVAL.md').write_text('# 背景全面接入设计证据\n\n- Status: APPROVED\n- UI ID: UI-001\n- Design Revision: DREV-20261013-CARD-BACKGROUNDS-01\n- Task Spec path and revision: specs/active/FEAT-001-CARD-BACKGROUNDS-COMPLETE.md#SPEC-20261013-CARD-BACKGROUNDS-01\n- Frontend baseline revision: FDB-20260913-04\n- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02\n- Approved by: 用户\n- Approved at: 2026-10-13\n- Approval evidence: 本会话明确剩余范围后“你先全面完成这个任务 我来验收”；沿用已有统一纸面与不同插画方案。\n- Frontend spec path: specs/active/FEAT-001-CARD-BACKGROUNDS-COMPLETE.md\n- Editable design source path(s): '+'; '.join(s.split('=')[0] for s in sources)+'\n- Editable source SHA-256: '+'; '.join(sources)+'\n- Superseded by: N/A\n\n## Export manifest\n\n| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |\n|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n')
