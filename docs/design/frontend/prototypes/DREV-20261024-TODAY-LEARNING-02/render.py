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
OUT = ROOT / "docs/design/frontend/snapshots/UI-001/DREV-20261024-TODAY-LEARNING-02"
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
                assert len(states) == 28
                for width, height in VIEWPORTS:
                    await call(
                        "Emulation.setDeviceMetricsOverride",
                        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": True},
                        sid,
                    )
                    for state in states:
                        await evaluate("window.designShow(" + json.dumps(state) + ")")
                        await evaluate(
                            "document.querySelector('.scroll').scrollTop = "
                            + (
                                "220"
                                if state in {"review-early", "review-long", "review-viewer"}
                                else "0"
                            )
                        )
                        await evaluate(
                            "document.fonts.ready.then(() => new Promise(resolve => "
                            "requestAnimationFrame(() => requestAnimationFrame(resolve))))"
                        )
                        audit = await evaluate("""(() => {
                          const active = document.querySelector('.sheet') ||
                            document.querySelector('.app');
                          const controls=active.querySelectorAll('button,input,textarea');
                          const bad = Array.from(controls).filter(el => {
                            const r=el.getBoundingClientRect();
                            return r.width<43.9 || r.height<43.9 ||
                              r.left< -1 || r.right>innerWidth+1;
                          }).map(el=>el.textContent.trim() || el.getAttribute('aria-label'));
                          const pair=Array.from(active.querySelectorAll(
                            '.proposal-actions .row button')).map(el=>el.getBoundingClientRect());
                          const pairBad=pair.length===2 &&
                            (Math.abs(pair[0].width-pair[1].width)>1 ||
                              pair[1].left-pair[0].right<7.9);
                          const body=document.querySelector('.sheet-body');
                          const bodyTooSmall=body && body.clientHeight<44;
                          const footer=document.querySelector('.sheet-actions');
                          const f=footer&&footer.getBoundingClientRect();
                          const keyboard=document.body.classList.contains('keyboard-mode');
                          return {horizontal:document.documentElement.scrollWidth>innerWidth+1,bad,
                            pairBad,bodyTooSmall:!!bodyTooSmall,
                            footerObscured:!!f&&(f.bottom>innerHeight-(keyboard?210:0)+1),
                            dialog:!!document.querySelector('[role=dialog]'),
                            state:document.body.dataset.state};
                        })()""")
                        assert (
                            not audit["horizontal"]
                            and not audit["bad"]
                            and not audit["footerObscured"]
                            and not audit["pairBad"]
                            and not audit["bodyTooSmall"]
                        ), (width, state, audit)
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
                for start, action, expected in [
                    ("suggestion", "suggestion-planned", "suggestion-planned"),
                    ("suggestion", "suggestion-loading", "suggestion-loading"),
                    ("suggestion", "suggestion-deferred", "suggestion-deferred"),
                    ("suggestion", "suggestion-edit", "suggestion-edit"),
                    ("suggestion-edit", "save-edit", "suggestion"),
                    ("suggestion-stale", "suggestion-loading", "suggestion-loading"),
                    ("suggestion-approve-error", "suggestion-planned", "suggestion-planned"),
                    ("suggestion-record", "suggestion-partial", "suggestion-partial"),
                    ("suggestion-record", "suggestion-saved", "suggestion-saved"),
                    ("suggestion-delete", "suggestion-loading", "suggestion-loading"),
                    ("review-early", "review-handled", "review-handled"),
                    ("review-early", "review-source", "review-source"),
                ]:
                    await evaluate("window.designShow(" + json.dumps(start) + ")")
                    await evaluate("document.querySelector('[data-action=" + action + "]').click()")
                    if action == "suggestion-planned":
                        assert await evaluate("document.body.dataset.state") == "suggestion-saving"
                        assert await evaluate(
                            "Array.from(document.querySelectorAll('.sheet button'))"
                            ".every(el=>el.disabled)"
                        )
                        await evaluate("new Promise(resolve=>setTimeout(resolve,750))")
                    assert await evaluate("document.body.dataset.state") == expected
                    report["interactions"].append(
                        {"from": start, "action": action, "to": expected, "result": "PASS"}
                    )
                await evaluate(
                    "window.designShow('suggestion');"
                    "Array.from(document.querySelectorAll('.sheet-actions button')).at(-1).focus()"
                )
                await call(
                    "Input.dispatchKeyEvent",
                    {"type": "keyDown", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9},
                    sid,
                )
                await call(
                    "Input.dispatchKeyEvent",
                    {"type": "keyUp", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9},
                    sid,
                )
                assert await evaluate("document.activeElement.classList.contains('close')")
                report["keyboard_focus_cycle"] = "PASS"
                await evaluate("window.designShow('suggestion-saving')")
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape"}, sid)
                assert await evaluate("document.body.dataset.state") == "suggestion-saving"
                await evaluate("window.designShow('suggestion')")
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape"}, sid)
                assert await evaluate("document.activeElement.dataset.action") == "suggestion"
                report["busy_escape_and_close_focus"] = "PASS"
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
