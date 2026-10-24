"""Export local design candidates. Never launches WeChat or calls a business API."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FRONTEND_ROOT = HERE.parents[1]
REPO_ROOT = HERE.parents[4]
DREV = HERE.name
SOURCE = HERE / "index.html"
TASK_SPEC = (
    "specs/active/FEAT-011-NOTIFICATION-AUTO-RENEWAL.md#SPEC-20261017-NOTIFICATION-AUTO-RENEWAL-01"
)
VIEWPORTS = ((320, 568), (390, 844), (430, 932))
GROUPS = {
    "UI-001": ("guide", "today-quiet"),
    "UI-011": (
        "settings-off",
        "settings-enabled",
        "settings-cooldown",
        "settings-stopped",
        "settings-pending",
        "settings-loading",
        "settings-error",
        "settings-unavailable",
        "settings-partial",
        "settings-forbidden",
        "settings-empty",
        "settings-saving",
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    records = []
    for ui in GROUPS:
        manifest = FRONTEND_ROOT / "snapshots" / ui / DREV / "APPROVAL.md"
        if manifest.exists() and "- Status: APPROVED" in manifest.read_text(encoding="utf-8"):
            raise RuntimeError("Approved design snapshots are immutable; create a new DREV")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        for ui, states in GROUPS.items():
            output = FRONTEND_ROOT / "snapshots" / ui / DREV
            output.mkdir(parents=True, exist_ok=True)
            rows = []
            for state in states:
                for width, height in VIEWPORTS:
                    errors: list[str] = []
                    page = browser.new_page(
                        viewport={"width": width, "height": height},
                        device_scale_factor=1,
                        reduced_motion="reduce",
                    )
                    page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
                    page.goto(f"{SOURCE.as_uri()}?screen=1&state={state}")
                    page.evaluate("document.fonts.ready")
                    measurements = page.evaluate(
                        """() => ({
                          width: innerWidth,
                          contentWidth: document.documentElement.scrollWidth,
                          controls: [...document.querySelectorAll('button')].map(node => {
                            const r = node.getBoundingClientRect();
                            return {
                              label: node.getAttribute('aria-label') || node.textContent.trim(),
                              x:r.x, y:r.y, width:r.width, height:r.height,
                              dialog:!!node.closest('[role=dialog]')};
                          })
                        })"""
                    )
                    assert not errors, (state, errors)
                    assert measurements["contentWidth"] <= width + 1, (state, width, measurements)
                    for control in measurements["controls"]:
                        assert control["width"] >= 43.9, (state, width, control)
                        assert control["height"] >= 43.9, (state, width, control)
                        assert control["x"] >= -1, (state, width, control)
                        assert control["x"] + control["width"] <= width + 1, (
                            state,
                            width,
                            control,
                        )
                        if control["dialog"]:
                            assert 0 <= control["y"] <= height - control["height"], control
                    name = f"{state}-{width}x{height}.png"
                    page.screenshot(path=str(output / name))
                    rows.append(
                        f"| {name} | {ui}/{state} | {width}×{height} | 1x | "
                        f"{sha(output / name)} | HTML候选；非原生验收 |"
                    )
                    records.append(
                        {
                            "ui": ui,
                            "state": state,
                            "viewport": [width, height],
                            "console_errors": errors,
                            "measurements": measurements,
                        }
                    )
                    page.close()
            source_path = SOURCE.relative_to(REPO_ROOT)
            spec_path = HERE.relative_to(REPO_ROOT) / "FRONTEND-SPEC.md"
            text = f"""# {ui} — {DREV} 候选清单

- Status: AWAITING_APPROVAL
- UI ID: {ui}
- Design Revision: {DREV}
- Frontend baseline revision: FDB-20260913-04
- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02
- Task Spec path and revision: {TASK_SPEC}
- Frontend spec path: {spec_path}
- Editable design source path(s): {source_path}
- Editable source SHA-256: {source_path}={sha(SOURCE)}
- Prototype generated/updated at: 2026-10-17
- Approved by: PENDING
- Approved at: PENDING
- Approval evidence: PENDING — 需求共识不是设计/实施批准
- Superseded by: N/A

## Approved scope

当前为候选范围，尚未批准。覆盖 {ui} 的 {len(states)} 态与320×568、390×844、430×932。
完整状态、交互与排除项见 FRONTEND-SPEC；不模拟微信原生授权面板，不含真实身份或儿童资料。
无可见实施偏离；批准后清单不可变（仅可添加 Superseded by）。

## Export manifest

| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## Gaps and follow-up

- 本清单仅证明本地HTML设计导出；不是小程序原生几何、真机授权、微信送达或发布证据。
- 平台授权面板/记住选项不能由本原型控制；真机矩阵待实施后验证。
- 设计审批、实现、原生三视口/字体放大/读屏/iOS/Android：NOT_RUN。

## Integrity checklist

- [x] 可编辑源与导出已生成，SHA-256列入本候选清单。
- [x] 三个精确视口和声明的全部状态均有PNG。
- [ ] 用户明确批准具体Task Spec + DREV。
- [ ] 批准后冻结本清单。
"""
            (output / "APPROVAL.md").write_text(text, encoding="utf-8")
        browser.close()
    (HERE / "render-audit.json").write_text(
        json.dumps(
            {"scope": "HTML design only; not native acceptance", "exports": records},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"DESIGN_EXPORTS={len(records)}; DOM audit passed; native checks NOT_RUN")


if __name__ == "__main__":
    main()
