"""Exercise observable review interactions; no production calls."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[4]/"docs/design/frontend/snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06"


async def run():
    checks=[];errors=[];network=[]
    async with async_playwright() as pw:
        browser=await pw.chromium.launch()
        page=await browser.new_page(viewport={"width":390,"height":844},reduced_motion="reduce")
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("request",lambda r:network.append(r.url) if r.url.startswith(("http:","https:")) else None)
        base=HERE.joinpath("index.html").as_uri()
        await page.goto(base+"?scene=settings")
        fallback_paths=[]
        for theme in ["garden","space","midnight","ocean","tech"]:
            await page.evaluate("t=>setPreview(t,'settings')",theme)
            await page.evaluate("Promise.all([...document.images].map(i=>i.decode()))")
            assert await page.locator('.hero-art').evaluate("(e)=>e.naturalWidth>0")
            fallback_paths.append(await page.locator("[data-fallback] path").get_attribute("d"))
            checks.append({"check":"theme illustration and default icon","theme":theme,"passed":True})
        assert len(set(fallback_paths))==5
        await page.evaluate("setPreview('garden','daily-form')")
        await page.get_by_role("textbox",name="任务名称").fill("阅读新计划")
        await page.get_by_role("button",name="返回",exact=True).click()
        assert await page.get_by_role("dialog",name="有修改尚未保存").count()==1
        await page.get_by_role("button",name="继续编辑",exact=True).click()
        assert await page.get_by_role("textbox",name="任务名称").input_value()=="阅读新计划"
        await page.get_by_role("button",name="30 分钟",exact=True).click()
        assert await page.get_by_role("spinbutton",name="每日目标时长，分钟").input_value()=="30"
        checks.append({"check":"unsaved input retention and duration selection","passed":True})
        await page.evaluate("setPreview('midnight','review-feedback')")
        await page.get_by_role("button",name="需要再看看",exact=True).click()
        assert await page.locator(".review-choice.active").inner_text()=="需要再看看"
        await page.get_by_role("button",name="关闭",exact=True).focus()
        await page.keyboard.press("Shift+Tab")
        assert await page.evaluate("document.activeElement.textContent")=="保存这次反馈"
        await page.keyboard.press("Escape")
        assert await page.locator('[role="dialog"]').count()==0
        checks.append({"check":"feedback selection and modal keyboard loop/escape","passed":True})
        for scene,name,button in [
            ("delete-confirm","小禾","#delete-final"),
            ("family-delete","小禾的家","#family-delete-final"),
        ]:
            await page.evaluate("s=>setPreview('tech',s)",scene)
            assert await page.locator(button).is_disabled()
            await page.locator("input").fill("wrong")
            assert await page.locator(button).is_disabled()
            await page.locator("input").fill(name)
            assert await page.locator(button).is_enabled()
            await page.locator(button).click()
            assert "未清理任何资料" in await page.locator(".toast").inner_text()
            checks.append({"check":"destructive confirmation remains a demonstration","scene":scene,"passed":True})
        await page.evaluate("setPreview('ocean','records')")
        await page.locator(".title-switch").click()
        await page.get_by_role("button",name="旅行日记 照片与家长确认的到访").click()
        assert await page.evaluate("ACTIVE_DESIGN.scene")=="travel"
        await page.get_by_role("button",name="地点",exact=True).click()
        assert await page.locator(".map-preview").count()==1
        await page.get_by_role("button",name="回放",exact=True).click()
        assert await page.get_by_role("slider",name="回放进度").count()==1
        checks.append({"check":"record type and travel views","passed":True})
        await page.evaluate("setPreview('space','confirm')")
        await page.locator("[data-disclose]").first.click()
        assert await page.locator("[data-disclose]").first.get_attribute("aria-expanded")=="true"
        assert await page.get_by_text("口头举例 · 预计 5 分钟；复习日期由规则安排。").first.is_visible()
        checks.append({"check":"draft detail disclosure","passed":True})
        await page.evaluate("setPreview('garden','theme-picker')")
        await page.locator('[data-theme-choice="midnight"]').click()
        assert await page.evaluate("ACTIVE_DESIGN.theme")=="midnight"
        assert await page.locator('[data-theme-choice][aria-pressed="true"]').count()==1
        checks.append({"check":"settings theme selector demonstration","passed":True})
        await page.evaluate("setPreview('midnight','error')")
        await page.get_by_role("button",name="重新加载",exact=True).click()
        assert await page.evaluate("ACTIVE_DESIGN.scene")=="settings"
        checks.append({"check":"error recovery action","passed":True})
        for width,height in [(1440,1050),(390,844)]:
            await page.set_viewport_size({"width":width,"height":height})
            await page.goto(base)
            frame=page.frames[1]
            await frame.wait_for_function("window.DESIGN_READY")
            for theme in ["garden","space","midnight","ocean","tech"]:
                await page.locator(f'[data-review-theme="{theme}"]').click()
                await frame.wait_for_function("t=>ACTIVE_DESIGN.theme===t",arg=theme)
            if width==390:
                await page.get_by_label("选择预览页面").select_option("travel-confirm")
            else:
                await page.locator('[data-review-scene="travel-confirm"]').click()
            await frame.wait_for_function("ACTIVE_DESIGN.scene==='travel-confirm'")
            await page.locator('[data-size="430,932"]').click()
            await frame.wait_for_function("innerWidth===430 && innerHeight===932")
            assert not await page.evaluate("document.documentElement.scrollWidth>innerWidth")
            await page.screenshot(path=str(OUT/f"gallery-{width}x{height}.png"),full_page=True)
            checks.append({"check":"gallery themes/scenes/exact iframe viewport","viewport":[width,height],"passed":True})
        await browser.close()
    assert not errors and not network
    result={"checks":checks,"javascriptErrors":errors,"externalRequests":network,"nativeAcceptance":"NOT_RUN"}
    (OUT/"interaction-checks.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"passed":len(checks),"javascriptErrors":errors,"externalRequests":network},ensure_ascii=False))


if __name__=="__main__":
    asyncio.run(run())
