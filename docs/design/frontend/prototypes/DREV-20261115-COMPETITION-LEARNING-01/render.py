"""Bind repository theme tokens, verify the candidate in Chromium and export evidence."""

import asyncio
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REVISION = HERE.name
OUT = HERE.parents[1] / "snapshots" / "UI-001" / REVISION
TASK = "specs/active/FEAT-015-COMPETITION-LEARNING.md"
GLYPHS = (
    "book",
    "calendar",
    "camera",
    "chart",
    "check",
    "chip",
    "plus",
    "sliders",
    "sprout",
    "star",
    "user",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    command = (
        "JSON.stringify([require('./apps/miniprogram/presentation/theme/registry').listThemes(),"
        "require('./apps/miniprogram/presentation/theme/glyphs')])"
    )
    themes, glyphs = json.loads(
        subprocess.check_output(["node", "-p", command], cwd=ROOT, text=True)
    )
    policy = json.loads((ROOT / "tools/frontend_viewports.json").read_text())
    baseline = policy["current"]
    sizes = policy["byBaseline"][baseline]
    source = (HERE / "source.html").read_text()
    values = {
        "THEMES": [{key: item[key] for key in ("id", "name", "tokens")} for item in themes],
        "SIZES": sizes,
        "GLYPHS": {key: glyphs[key] for key in GLYPHS},
    }
    for key, value in values.items():
        source = source.replace(f"__{key}__", json.dumps(value, ensure_ascii=False))
    preview = HERE / "index.html"
    preview.write_text(source)
    return preview, [theme["id"] for theme in themes], sizes, baseline


GEOMETRY = """() => {
    const phone = document.querySelector(".phone");
    const { width, height } = phone.getBoundingClientRect();
    const visible = [...phone.querySelectorAll("button,input,summary")].filter(
      item => !item.closest("[inert]") && item.getClientRects().length
    );
    const insufficient = visible.filter(item => {
      const rect = item.getBoundingClientRect();
      return rect.width < 44 || rect.height < 44;
    }).map(item => item.textContent);
    const spilling = visible.filter(item => item.scrollWidth > item.clientWidth + 1)
      .map(item => item.textContent);
    return { exact: width === innerWidth && height === innerHeight, insufficient, spilling,
      overflow: phone.scrollWidth > innerWidth ||
        document.querySelector("main").scrollWidth > innerWidth };
}"""

CONTRAST = r"""() => {
    const rgba = color => color.match(/[\d.]+/g).map(Number);
    const over = (front, back) => {
      const alpha = front.length === 4 ? front[3] : 1;
      return back.map((channel, i) => front[i] * alpha + channel * (1 - alpha));
    };
    const luminance = rgb => rgb.map(n => {
      const x = n / 255;
      return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
    }).reduce((sum, n, i) => sum + n * [.2126, .7152, .0722][i], 0);
    const nodes = document.querySelectorAll(
      ".phone h1, .phone h2, .badge, .meta, .label, .phone button, .phone summary"
    );
    const failures = [];
    let minimum = 21;
    for (const node of nodes) {
      if (!node.getClientRects().length || node.closest("[inert]")) continue;
      const layers = [];
      for (let element = node; element; element = element.parentElement) {
        layers.push(rgba(getComputedStyle(element).backgroundColor));
      }
      const background = layers.reverse()
        .reduce((back, front) => over(front, back), [255, 255, 255]);
      const a = luminance(background);
      const b = luminance(over(rgba(getComputedStyle(node).color), background));
      const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
      minimum = Math.min(minimum, ratio);
      if (ratio < 4.5) failures.push([node.textContent.trim(), ratio.toFixed(2)]);
    }
    return { minimum, failures };
}"""


async def capture(browser, source, theme, sizes):
    rows = []
    minimum = 21.0
    for width, height in sizes.items():
        page = await browser.new_page(
            viewport={"width": int(width), "height": height}, offline=True
        )
        faults = []
        page.on("pageerror", lambda error, faults=faults: faults.append(str(error)))
        try:
            await page.goto(source.as_uri())
            states = await page.locator("#scenes option").evaluate_all(
                "items => items.map(item => item.value)"
            )
            for state in states:
                query = urlencode({"export": 1, "theme": theme, "size": width, "scene": state})
                await page.goto(f"{source.as_uri()}?{query}")
                await page.evaluate("document.fonts.ready")
                box = await page.evaluate(GEOMETRY)
                if (
                    not box["exact"]
                    or box["overflow"]
                    or box["insufficient"]
                    or box["spilling"]
                    or faults
                ):
                    raise AssertionError((theme, width, state, box, faults))
                contrast = await page.evaluate(CONTRAST)
                if contrast["failures"]:
                    raise AssertionError((theme, width, state, contrast))
                minimum = min(minimum, contrast["minimum"])
                viewport = f"{width}x{height}"
                target = OUT / f"{theme}-{state}-{viewport}.png"
                await page.screenshot(path=target, animations="disabled")
                rows.append(
                    f"| {target.name} | {theme} / {state} | {viewport} | 1x | {digest(target)} |"
                )
        finally:
            await page.close()
    return rows, minimum


async def exercise(browser, source, width, height):
    page = await browser.new_page(viewport={"width": width, "height": height}, offline=True)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        await page.goto(source.as_uri())
        assert await page.locator("#nav button").all_text_contents() == [
            "今日",
            "日程",
            "记录",
            "报表",
            "竞赛",
        ]
        await page.get_by_role("button", name="打开孩子选择框").click()
        await page.get_by_role("button", name="设置", exact=True).click()
        assert await page.locator("h1").inner_text() == "设置"
        await page.get_by_role("button", name="返回").click()
        assert await page.locator("h1").inner_text() == "竞赛"
        await page.get_by_role("button", name="整数加减法", exact=False).click()
        await page.get_by_role("button", name="学习完成", exact=True).click()
        assert await page.locator(".progress .badge").inner_text() == "已学习"
        await page.get_by_role("button", name="返回").click()
        assert await (
            page.get_by_role("button", name="集合", exact=False).get_by_text("该学习").is_visible()
        )
        await page.get_by_role("button", name="打开孩子选择框").click()
        await page.get_by_role("button", name="切换到小满").click()
        assert await (
            page.get_by_role("button", name="整数加减法", exact=False)
            .get_by_text("该学习")
            .is_visible()
        )
        await page.get_by_role("button", name="物理", exact=True).click()
        assert await (
            page.get_by_role("button", name="位置", exact=False).get_by_text("该学习").is_visible()
        )
        await page.get_by_role("button", name="数学", exact=True).click()
        await page.get_by_role("searchbox").fill("阿式圆")
        await page.get_by_role("button", name="阿氏圆", exact=False).click()
        await page.get_by_role("button", name="返回").click()
        assert await page.get_by_role("searchbox").input_value() == "阿式圆"
        await page.locator("#scenes").select_option("review")
        await page.get_by_role("button", name="完成第 2 轮复习").click()
        assert await page.get_by_text("已复习 2 / 5 轮").is_visible()
        await page.locator("#scenes").select_option("question")
        await page.get_by_text("参考答案", exact=True).click()
        assert not await page.get_by_text("90°。直径所对的圆周角是直角。").is_visible()
        await page.locator("#scenes").select_option("no-child")
        await page.get_by_role("button", name="设置", exact=True).click()
        assert await page.get_by_text("家庭设置", exact=True).is_visible()
        await page.locator("#scenes").select_option("catalog")
        await page.get_by_role("button", name="日程", exact=True).click()
        await page.get_by_role("button", name="去设置固定时间").click()
        assert await page.locator("#schedule-anchor").is_visible()
        await page.get_by_role("button", name="返回").click()
        assert await page.locator("h1").inner_text() == "日程"
        assert not errors, errors
        print(
            "PASS navigation, learning and review demo, topic search, child scope, "
            f"settings return {width}x{height}"
        )
    finally:
        await page.close()


async def main():
    approval = OUT / "APPROVAL.md"
    assert not approval.exists() or "- Status: APPROVED" not in approval.read_text()
    preview, themes, sizes, baseline = build()
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pipe:
        browser = await pipe.chromium.launch()
        for width, height in sizes.items():
            await exercise(browser, preview, int(width), height)
        rows = await asyncio.gather(*(capture(browser, preview, theme, sizes) for theme in themes))
        await browser.close()
    listed = [row for theme_rows, _ in rows for row in theme_rows]
    minimum = min(value for _, value in rows)
    source = preview.relative_to(ROOT)
    evidence = (
        f"""# {REVISION} — 竞赛与设置导航

- Status: AWAITING_APPROVAL
- UI ID: UI-001
- Design Revision: {REVISION}
- Frontend baseline revision: {baseline}
- Frontend engineering revision: FEC-20261107-AGENT-DEVICE-MATRIX-03
- Task Spec path and revision: {TASK} / COMPETITION-LEARNING-SPEC-02
- Frontend spec path: {(HERE / "FRONTEND-SPEC.md").relative_to(ROOT)}
- Editable design source path(s): {source}
- Editable source SHA-256: {source}={digest(preview)}
- Approved by: pending
- Approved at: pending
- Approval evidence: pending

Chromium 导出 {len(listed)} 张。六主题及两档当前视口。候选交互控件最小 44 CSS px，\
采样文字最低对比度 {minimum:.2f}:1。微信原生、真机和上线均尚未进行。

## Export manifest

| File | State | Viewport | Scale | SHA-256 |
| --- | --- | --- | --- | --- |
"""
        + "\n".join(listed)
        + "\n"
    )
    (OUT / "APPROVAL.md").write_text(evidence)
    print(f"PASS {len(listed)} Chromium viewport/state/theme captures")


if __name__ == "__main__":
    asyncio.run(main())
