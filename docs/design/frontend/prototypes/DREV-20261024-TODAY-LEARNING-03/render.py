"""Export this synthetic HTML design with installed Chrome; never accesses app data."""

import asyncio
import base64
import json
import subprocess
import tempfile
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-03"
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
    with tempfile.TemporaryDirectory(prefix="pk-design-") as profile:
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
                            errors.append(
                                event["params"]["exceptionDetails"].get("text", "script_error")
                            )
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
                        raise RuntimeError("design_script_failed")
                    return result["result"].get("value")

                await call("Page.navigate", {"url": (HERE / "index.html").as_uri()}, sid)
                for _ in range(100):
                    if await evaluate("document.body && document.body.dataset.ready === 'true'"):
                        break
                    await asyncio.sleep(0.05)
                states = await evaluate("window.designStates")
                assert len(states) == 21
                for width, height in VIEWPORTS:
                    await call(
                        "Emulation.setDeviceMetricsOverride",
                        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": True},
                        sid,
                    )
                    for state in states:
                        await evaluate("window.designShow(" + json.dumps(state) + ")")
                        await evaluate(
                            "document.fonts.ready.then(() => new Promise(resolve => "
                            "requestAnimationFrame(() => requestAnimationFrame(resolve))))"
                        )
                        await evaluate("""(() => {
                          const scroll=document.querySelector('.scroll');
                          scroll.scrollTop=0;
                          if(document.body.dataset.state==='proposal-long'){
                            const card=document.querySelector('.study-region');
                            scroll.scrollTop=card.offsetTop-scroll.offsetTop;
                          }
                        })()""")
                        audit = await evaluate("""(() => {
                          const rect=el=>el.getBoundingClientRect();
                          const region=document.querySelector('.study-region');
                          const card=document.querySelector('.study-card');
                          const review=document.querySelector('.review-region');
                          const hero=document.querySelector('.hero');
                          const title=region&&region.querySelector('.s-t');
                          const ref=getComputedStyle(review.querySelector('.s-t'));
                          const bad=Array.from(document.querySelectorAll('button,a')).filter(el=>{
                            const r=rect(el);return r.width<43.9||r.height<43.9||
                              r.left< -1||r.right>innerWidth+1;
                          }).map(el=>el.textContent.trim());
                          const outside=Array.from(document.querySelectorAll(
                            '.study-region,.study-card,.study-title,.study-meta,.study-copy,.review-region'
                          )).filter(el=>rect(el).left< -1||rect(el).right>innerWidth+1).length;
                          const current=title&&getComputedStyle(title);
                          const expectedHidden=window.hiddenStates.includes(
                            document.body.dataset.state);
                          const gap=rect(review).top-rect(hero).bottom;
                          const expectedGap=parseFloat(getComputedStyle(review).marginTop);
                          const fontMatch=!current||(current.fontFamily===ref.fontFamily&&
                            current.fontSize===ref.fontSize&&current.fontWeight===ref.fontWeight);
                          const small=Array.from(document.querySelectorAll(
                            '.study-title,.study-meta,.study-copy,.study-progress,.study-region a'
                          )).filter(el=>parseFloat(getComputedStyle(el).fontSize)<14).length;
                          return {state:document.body.dataset.state,expectedHidden,region:!!region,
                            horizontal:document.documentElement.scrollWidth>innerWidth+1,
                            scrollLeft:document.querySelector('.scroll').scrollLeft,bad,outside,
                            fontMatch,small,emptyGap:gap,expectedGap,
                            gapMatch:!expectedHidden||Math.abs(gap-expectedGap)<1,
                            marketingCopy:!!region&&/小步延展，家长做主|沿着学过的，再走一小步/.test(region.innerText),
                            card:!!card,viewerWrite:document.body.dataset.state==='viewer-task'&&
                              !!region.querySelector('a,button'),
                            contentTitle:card&&getComputedStyle(card.querySelector('.study-title')).fontSize};
                        })()""")
                        assert not any(
                            [
                                audit["horizontal"],
                                audit["scrollLeft"],
                                audit["bad"],
                                audit["outside"],
                                audit["small"],
                                audit["marketingCopy"],
                                audit["viewerWrite"],
                            ]
                        ), (width, state, audit)
                        assert audit["fontMatch"] and audit["gapMatch"], (width, state, audit)
                        assert not audit["card"] or audit["contentTitle"] == "16px"
                        assert not (audit["expectedHidden"] and audit["region"]), (
                            width,
                            state,
                            audit,
                        )
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
                            }
                        )
                    print(f"exported {len(states)} states at {width}x{height}", flush=True)
                for start, label, target in [
                    ("proposal", "查看学习建议", "suggestion"),
                    ("task", "记录实际学习", "suggestion-record"),
                    ("task", "删除并换一项", "suggestion-delete"),
                    ("generating", "查看进度", "suggestion-loading"),
                    ("generation-error", "查看并重试", "suggestion-error"),
                    ("stale", "查看并重新准备", "suggestion-stale"),
                    ("recover-after-remove", "重新准备建议", "suggestion-loading"),
                    ("network-error", "重新加载", "suggestion-offline"),
                ]:
                    url = (HERE / "index.html").as_uri() + "?state=" + start
                    await call("Page.navigate", {"url": url}, sid)
                    for _ in range(100):
                        if await evaluate(
                            "document.body && document.body.dataset.ready === 'true'"
                        ):
                            break
                        await asyncio.sleep(0.05)
                    await evaluate(
                        "Array.from(document.querySelectorAll('a')).find(el=>el.textContent==="
                        + json.dumps(label)
                        + ").click()"
                    )
                    found = False
                    for _ in range(100):
                        found = await evaluate(
                            "location.href.includes('DREV-20261024-TODAY-LEARNING-02') && "
                            "document.body.dataset.ready==='true' && document.body.dataset.state==="
                            + json.dumps(target)
                        )
                        if found:
                            break
                        await asyncio.sleep(0.05)
                    assert found, (start, label, target)
                    assert await evaluate("!!document.querySelector('[role=dialog]')")
                    report["interactions"].append(
                        {
                            "from": start,
                            "action": label,
                            "approved_target": target,
                            "result": "PASS",
                        }
                    )
                assert not errors, errors
                report["runtime_errors"] = errors
                report["browser_version"] = await call("Browser.getVersion")
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
