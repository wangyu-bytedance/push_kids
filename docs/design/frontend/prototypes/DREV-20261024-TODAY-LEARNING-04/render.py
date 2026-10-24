"""Render synthetic design only with isolated headless Chrome; no app/model calls."""

import asyncio
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-04"
VIEWPORTS = [(320, 568), (390, 844), (430, 932)]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "kind": "synthetic-html-design-only",
        "native_acceptance": "NOT_RUN",
        "exports": [],
        "interactions": [],
    }
    with tempfile.TemporaryDirectory(prefix="pk-title-design-") as profile:
        process = subprocess.Popen(
            [
                CHROME,
                "--headless",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--remote-debugging-port=0",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            port_file = Path(profile) / "DevToolsActivePort"
            for _ in range(200):
                if port_file.exists():
                    break
                if process.poll() is not None:
                    raise RuntimeError("headless_chrome_exited")
                await asyncio.sleep(0.1)
            port, endpoint = port_file.read_text().splitlines()[:2]
            async with websockets.connect(
                f"ws://127.0.0.1:{port}{endpoint}", max_size=20_000_000
            ) as ws:
                seq = 0
                errors = []

                async def call(method, params=None, session=None):
                    nonlocal seq
                    seq += 1
                    request = {"id": seq, "method": method, "params": params or {}}
                    if session:
                        request["sessionId"] = session
                    await ws.send(json.dumps(request))
                    while True:
                        event = json.loads(await ws.recv())
                        if event.get("method") == "Runtime.exceptionThrown":
                            errors.append(event["params"]["exceptionDetails"].get("text"))
                        if event.get("id") == request["id"]:
                            if "error" in event:
                                raise RuntimeError(event["error"])
                            return event.get("result", {})

                targets = await call("Target.getTargets")
                target = next(t for t in targets["targetInfos"] if t["type"] == "page")
                sid = (
                    await call(
                        "Target.attachToTarget", {"targetId": target["targetId"], "flatten": True}
                    )
                )["sessionId"]
                await call("Page.enable", session=sid)
                await call("Runtime.enable", session=sid)

                async def evaluate(expression):
                    result = await call(
                        "Runtime.evaluate",
                        {"expression": expression, "returnByValue": True, "awaitPromise": True},
                        sid,
                    )
                    if "exceptionDetails" in result:
                        raise RuntimeError(result["exceptionDetails"])
                    return result["result"].get("value")

                await call("Page.navigate", {"url": (HERE / "index.html").as_uri()}, sid)
                for _ in range(100):
                    if await evaluate("document.body && document.body.dataset.ready==='true'"):
                        break
                    await asyncio.sleep(0.05)
                states = await evaluate("window.designStates")
                for width, height in VIEWPORTS:
                    await call(
                        "Emulation.setDeviceMetricsOverride",
                        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False},
                        sid,
                    )
                    for state in states:
                        await evaluate("window.designShow(" + json.dumps(state) + ")")
                        await evaluate(
                            "new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
                        )
                        audit = await evaluate("""(() => {
                          const rect=e=>e.getBoundingClientRect();
                          const sheet=document.querySelector('.sheet');
                          const actions=document.querySelector('.sheet .actions');
                          const head=document.querySelector('.sheet .head');
                          const body=document.querySelector('.sheet .body');
                          const title=document.querySelector('.sheet .title');
                          const controls=Array.from(document.querySelectorAll('.sheet button'));
                          const bad=controls.filter(e=>{const r=rect(e);
                            return r.width<43.9||r.height<43.9||r.left< -1||
                              r.right>innerWidth+1||r.bottom>innerHeight+1;}).length;
                          const titleHeight=title?rect(title).height:0;
                          const counter=document.getElementById('title-counter');
                          const input=document.getElementById('edit-title');
                          return {horizontal:document.documentElement.scrollWidth>innerWidth+1,
                            badControls:bad,sheetContained:!sheet||(rect(sheet).top>=-1&&rect(sheet).bottom<=innerHeight+1),
                            bodyHeight:body&&rect(body).height,
                            overlap:body&&(rect(head).bottom>rect(body).top+1||rect(body).bottom>rect(actions).top+1),
                            titleHeight,titleLines:titleHeight/29,
                            counter:counter&&counter.textContent,titleValue:input&&input.value,
                            error:document.getElementById('title-error')?.textContent||'',
                            bodyScroll:body&&body.scrollHeight>body.clientHeight,
                            legacyScroll:document.querySelector('.legacy-scroll')?.scrollHeight||0,
                            legacyHeight:document.querySelector('.legacy-scroll')?.clientHeight||0,
                            busy:document.body.dataset.state==='edit-saving'&&Array.from(
                              document.querySelectorAll(
                                '.sheet button,.sheet input,.sheet textarea')
                            ).every(e=>e.disabled),
                            small:controls.some(e=>parseFloat(getComputedStyle(e).fontSize)<14)};
                        })()""")
                        assert not any(
                            [
                                audit["horizontal"],
                                audit["badControls"],
                                audit["overlap"],
                                audit["small"],
                            ]
                        ), (width, state, audit)
                        assert audit["sheetContained"], (width, state, audit)
                        assert audit["bodyHeight"] is None or audit["bodyHeight"] > 0
                        if state in {"proposal", "proposal-max"}:
                            assert audit["titleLines"] <= 2.01, (width, state, audit)
                        if state == "edit-max":
                            assert audit["counter"] == "20/20" and not audit["error"]
                        if state == "edit-over":
                            assert audit["counter"] == "21/20" and audit["error"]
                        if state == "edit-legacy":
                            assert len(audit["titleValue"]) == 120 and audit["error"]
                        if state == "edit-saving":
                            assert audit["busy"]
                        filename = f"{state}-{width}x{height}.png"
                        shot = await call(
                            "Page.captureScreenshot",
                            {"format": "png", "captureBeyondViewport": False},
                            sid,
                        )
                        (OUT / filename).write_bytes(base64.b64decode(shot["data"]))
                        report["exports"].append(
                            {
                                "file": filename,
                                "viewport": [width, height],
                                "state": state,
                                "layout": audit,
                                "sha256": hashlib.sha256((OUT / filename).read_bytes()).hexdigest(),
                            }
                        )

                    # Interaction assertions use synthetic local calls only, never app APIs.
                    async def check(name, script, width=width, height=height):
                        assert await evaluate(script), (width, name)
                        report["interactions"].append(
                            {"viewport": [width, height], "case": name, "result": "PASS"}
                        )

                    await check(
                        "20-code-point-save",
                        """(() => {
                      designShow('edit-max');const n=designCalls.length;
                      document.querySelector('[data-action=save]').click();
                      return designCalls.length===n+1&&designCalls.at(-1).title.length===20&&
                        document.querySelector('.title').textContent===designCalls.at(-1).title;
                    })()""",
                    )
                    await check(
                        "21-preserved-zero-write",
                        """(() => {
                      designShow('edit-over');const n=designCalls.length;
                      const value=document.getElementById('edit-title').value;
                      document.querySelector('[data-action=save]').click();
                      return designCalls.length===n&&
                        document.getElementById('edit-title').value===value&&
                        document.activeElement.id==='edit-title';
                    })()""",
                    )
                    await check(
                        "empty-zero-write",
                        """(() => {
                      designShow('edit-empty');const n=designCalls.length;
                      document.querySelector('[data-action=save]').click();
                      return designCalls.length===n&&
                        !!document.getElementById('title-error').textContent;
                    })()""",
                    )
                    await check(
                        "legacy-no-truncation-and-shorten",
                        """(() => {
                      designShow('legacy');document.querySelector('[data-action=edit]').click();
                      const input=document.getElementById('edit-title');const original=input.value;
                      const n=designCalls.length;
                      document.querySelector('[data-action=save]').click();
                      if(original.length!==120||designCalls.length!==n)return false;
                      input.value='用积木表示加法';input.dispatchEvent(new Event('input'));
                      document.querySelector('[data-action=save]').click();
                      return designCalls.length===n+1&&designCalls.at(-1).title==='用积木表示加法';
                    })()""",
                    )
                    await check(
                        "non-bmp-count-and-line-break",
                        """
                      designCount('  '+ '🌱'.repeat(20)+'  ')===20&&
                      !designTitleError('🌱'.repeat(20))&&
                      !!designTitleError('🌱'.repeat(21))&&!!designTitleError('活动\\n步骤')
                    """,
                    )
                    await check(
                        "save-failure-retains-form",
                        """(() => {
                      designShow('edit-error');const input=document.getElementById('edit-title');
                      input.value='用积木数一数';input.dispatchEvent(new Event('input'));
                      document.querySelector('[data-action=save]').click();
                      return document.getElementById('edit-title').value==='用积木数一数'&&
                        !!document.querySelector('[role=alert]');
                    })()""",
                    )
                    await check(
                        "pending-disables-submit-and-close",
                        """(() => {
                      designShow('edit-saving');const n=designCalls.length;
                      document.querySelector('[data-action=save]').click();
                      document.querySelector('[data-action=close]').click();
                      return designCalls.length===n&&document.body.dataset.state==='edit-saving';
                    })()""",
                    )
                    print(
                        f"exported {len(states)} states and 7 interactions at {width}x{height}",
                        flush=True,
                    )
                assert not errors, errors
                report["runtime_errors"] = errors
                report["browser_version"] = await call("Browser.getVersion")
                report["source_sha256"] = hashlib.sha256(
                    (HERE / "index.html").read_bytes()
                ).hexdigest()
                (HERE / "render-report.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n"
                )
                await call("Browser.close")
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    asyncio.run(main())
