"""Create a synthetic, offline DevTools copy. Production transport stays unchanged."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/private/tmp/push-kids-record-types-native-20261023")


def main():
    shutil.copytree(ROOT / "apps/miniprogram", OUT, dirs_exist_ok=True)
    config = OUT / "project.config.json"
    value = json.loads(config.read_text())
    value["projectname"] = "push-kids-record-types-synthetic"
    value["libVersion"] = "3.17.4"
    value["setting"]["lazyloadPlaceholderEnable"] = False
    config.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    app = OUT / "app.json"
    value = json.loads(app.read_text())
    value["pages"].remove("pages/records/index")
    value["pages"].insert(0, "pages/records/index")
    value["plugins"] = {}
    app.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    (OUT / "config.js").write_text(
        "module.exports={useCloud:false,localFamilyId:'synthetic',localActorId:'synthetic',localApiBaseUrl:'http://127.0.0.1:18769/api/v1'};\n"
    )
    (OUT / "utils/api.js").write_text("""
const child={id:'synthetic',name:'合成孩子',label:'合成孩子',active:true,
grade:'三年级',avatar:'合'};
const photo={id:'synthetic-photo',state:'ready',job_state:'succeeded',
local_date:'2024-02-03',has_display:false,version:1};
const visit={id:'synthetic-visit',local_date:'2024-02-03',place_name:'合成地点',
latitude:39.9,longitude:116.4,photo_count:1,photos:[photo]};
module.exports={newIdempotencyKey:()=> 'synthetic-key',removePreview(){},
downloadPreview:async()=>'/assets/illustrations/record-camera.png',
async request(url,options={}){
if(options.method&&options.method!=='GET')throw Error('Synthetic copy forbids business writes');
if(url==='/me')return {state:'bound',family:{id:'synthetic'},
member:{role:'manager'},children:[child]};
if(url.startsWith('/children?')||url==='/children')return [child];
if(url.includes('/history?'))return {items:[],pending_count:0,has_processing:false};
if(url==='/footprints/preferences')return {ai_enabled:false,consented:true};
if(url.startsWith('/footprints/summary?'))return {places:1,cities:1,countries:1,photos:1,drafts:1};
if(url.includes('/preview?'))return {};
if(url.startsWith('/footprints/visits?'))return {items:[visit],next_cursor:null};
if(url.startsWith('/footprints/drafts?')||url.includes('/photos?'))
return {items:[photo],next_cursor:null};
if(url.startsWith('/footprints/playback?'))return {items:[visit],revision:1};
if(url.startsWith('/footprints/map?'))return {items:[],bounds:[73,18,136,54]};
throw Error('No synthetic fixture for request');}};
""")
    # Harness methods only; production lifecycle/control flow and styles are preserved.
    for relative in ["pages/records/index.js", "pages/footprints/controller.js"]:
        file = OUT / relative
        text = file.read_text()
        needle = "  data: {"
        text = text.replace(
            needle,
            "  applyGeometryFixture(serialized) { this.setData(JSON.parse(serialized)); },\n"
            + needle,
            1,
        )
        file.write_text(text)
    file = OUT / "pages/footprints/index.wxml"
    file.write_text(
        file.read_text().replace(
            'class="fp-sheet-body" scroll-y',
            'class="fp-sheet-body" scroll-top="{{geometryScrollTop}}" scroll-y',
        )
    )
    print(OUT)


if __name__ == "__main__":
    main()
