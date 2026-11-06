"""Prepare an offline synthetic native theme acceptance copy, never a release source."""

import hashlib
import json
from pathlib import Path

import prepare_grade_confirmation_native as base

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/private/tmp/push-kids-themes-native-20261106")


def main():
    base.OUT = OUT
    base.main()
    app = OUT / "app.js"
    app.write_text(
        app.read_text().replace(
            "App({",
            """let themeFixturePicker;
App({
  getThemeFixturePicker(){return themeFixturePicker;},
  setThemeFixturePicker(value){themeFixturePicker=value;},
  themeFixture(data) {
    const p=getCurrentPages().slice(-1)[0];
    this.gradeConfirmation=null;
    return p.applyThemePresentationFixture(JSON.stringify(data));
  },
  themeFixtureRequestCount(){return require('./utils/api').themeFixtureRequestCount;},
""",
            1,
        )
    )
    api = OUT / "utils/api.js"
    api.write_text(
        api.read_text() + "\nconst originalRequest=module.exports.request;"
        "module.exports.themeFixtureRequestCount=0;"
        "module.exports.request=function(...args){module.exports.themeFixtureRequestCount++;"
        "return originalRequest.apply(this,args);};\n"
    )
    picker = OUT / "components/theme-picker/index.js"
    picker.write_text(
        picker.read_text().replace(
            "  observers: {",
            "  lifetimes:{attached(){getApp().setThemeFixturePicker(this);},"
            "detached(){if(getApp().getThemeFixturePicker()===this)"
            "getApp().setThemeFixturePicker(null);}},\n"
            "  observers: {",
            1,
        )
    )
    # Native presentation fixtures use real handlers/adapters but suppress page data
    # loading/navigation. Business lifecycle behavior is checked in the VM suite.
    routes = json.loads((OUT / "app.json").read_text())["pages"]
    for route in routes:
        file = OUT / (route + ".js")
        text = file.read_text()
        text = text.replace("Page(withThemePage(", "Page(withThemePage(themeFixtureDefinition(", 1)
        end = text.rfind(");")
        text = text[:end] + ")" + text[end:]
        helper = """function themeFixtureDefinition(definition) {
  const initial=JSON.stringify(definition.data||{});
  return {...definition,
    applyThemePresentationFixture(serialized){
      this.setData({...JSON.parse(initial),...JSON.parse(serialized)});return this.route;
    },
    onLoad(){},onShow(){},onPullDownRefresh(){}};
}
"""
        file.write_text(helper + text)
    production = ROOT / "apps/miniprogram"
    files = sorted(p for p in production.rglob("*") if p.is_file())
    manifest = {
        str(p.relative_to(production)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
    }
    (OUT / "theme-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
