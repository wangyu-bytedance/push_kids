"""Build an isolated native-layout project with unchanged production WXML/WXSS."""

import json
import shutil
import sys
from pathlib import Path


def build(target: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "apps/miniprogram"
    target.mkdir(parents=True, exist_ok=True)
    for directory in ("styles", "pages/review-inventory", "components/review-inventory"):
        shutil.copytree(source / directory, target / directory, dirs_exist_ok=True)
    shutil.copy2(source / "app.wxss", target / "app.wxss")
    (target / "utils").mkdir(exist_ok=True)
    (target / "utils/api.js").write_text(
        'exports.request=()=>Promise.reject(Error("isolated: no business requests"));\n'
        'exports.newIdempotencyKey=()=>"synthetic";\n'
    )
    (target / "app.js").write_text(
        'App({globalData:{useCloud:false,selectedChildId:"synthetic",'
        'familyId:"synthetic",currentMember:{role:"manager"}}});\n'
    )
    (target / "app.json").write_text(
        json.dumps(
            {
                "pages": ["pages/review-inventory/index", "pages/embedded/index"],
                "window": {"navigationBarTitleText": "复习条目 · 合成测试"},
                "style": "v2",
                "lazyCodeLoading": "requiredComponents",
                "sitemapLocation": "sitemap.json",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    (target / "sitemap.json").write_text('{"rules": [{"action":"allow","page":"*"}]}\n')
    project = json.loads((source / "project.config.json").read_text())
    project.update(projectname="supersession-native-20261020", libVersion="3.17.4")
    project["setting"]["lazyloadPlaceholderEnable"] = False
    (target / "project.config.json").write_text(json.dumps(project, indent=2))
    (target / "pages/review-inventory/index.js").write_text(
        'const c=require("./controller");Page({...c,onShow(){this.visible=true;},'
        "applyGeometryFixture(value){this.setData(JSON.parse(value));}});\n"
    )
    component = target / "components/review-inventory/index.js"
    code = component.read_text().replace(
        "  methods,",
        "  methods: {...methods, applyGeometryFixture(value) {"
        " this.setData(JSON.parse(value)); }},",
    )
    assert "return controller.onShow.call(this);" in code
    component.write_text(
        code.replace("return controller.onShow.call(this);", "this.visible = true;")
    )
    embedded = target / "pages/embedded"
    embedded.mkdir(exist_ok=True)
    (embedded / "index.js").write_text("Page({});\n")
    (embedded / "index.json").write_text(
        json.dumps({"usingComponents": {"review-inventory": "/components/review-inventory/index"}})
    )
    (embedded / "index.wxml").write_text(
        '<view class="host"><review-inventory id="inventory-component" '
        'embedded="{{true}}" context-child-id="synthetic" /></view>\n'
    )
    (embedded / "index.wxss").write_text(".host { padding: 0 18px; }\n")
    print(f"ISOLATED_NATIVE_PROJECT {target}")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
