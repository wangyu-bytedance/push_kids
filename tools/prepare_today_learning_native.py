"""Create an offline synthetic Today copy; production transport is never changed."""

import argparse
import json
import shutil
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/private/tmp/push-kids-today-learning-native-20261024")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence-dir", default="docs/quality/evidence/today-learning-20261024/native"
    )
    args = parser.parse_args()
    evidence = (ROOT / args.evidence_dir).resolve()
    evidence.relative_to(ROOT / "docs/quality/evidence")
    shutil.copytree(ROOT / "apps/miniprogram", OUT, dirs_exist_ok=True)
    config = json.loads((OUT / "project.config.json").read_text())
    config.update(projectname="push-kids-today-learning-synthetic", libVersion="3.17.4")
    config["setting"]["lazyloadPlaceholderEnable"] = False
    (OUT / "project.config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))
    app = json.loads((OUT / "app.json").read_text())
    app["plugins"] = {}
    app["pages"].remove("pages/today/index")
    app["pages"].insert(0, "pages/today/index")
    (OUT / "app.json").write_text(json.dumps(app, ensure_ascii=False, indent=2))
    (OUT / "config.js").write_text(
        "module.exports={useCloud:false,localFamilyId:'synthetic',localActorId:'synthetic',"
        "localApiBaseUrl:'http://127.0.0.1:18769/api/v1'};\n"
    )
    (OUT / "utils/api.js").write_text("""
const child={id:'synthetic',name:'合成孩子',label:'合成孩子',active:true,
grade:'小学三年级',avatar:'合'};
module.exports={newIdempotencyKey:()=> 'synthetic-key',removePreview(){},
async request(url,options={}){
if(options.method&&options.method!=='GET')throw Error('Synthetic copy forbids business writes');
if(url==='/me')return {state:'bound',family:{id:'synthetic'},
member:{role:'manager'},children:[child]};
if(url==='/children')return [child];
if(url.endsWith('/subjects'))return [{id:'synthetic-subject',name:'数学',
kind:'learning',active:true}];
if(url.endsWith('/current'))return {day:'2026-10-24',version:1,
eligibility:'recent_new',task:null,proposal:null,job:null};
if(url.endsWith('/dashboard'))return {day:'2026-10-24',todo_count:0,
required_todo_count:0,estimated_minutes:0,
todo_groups:[],schedule_items:[],activity_suggestions:[],activity_remaining_count:0,analyzing_count:0,failed_count:0,
pending_confirmation_count:0,daily_summary:{record_count:0,subjects:[]},
daily_tasks:{day:'2026-10-24',items:[],total_count:0,remaining_count:0},
review_selection:{plan_id:'synthetic-plan',sessions:[],selected_count:0,planned_count:0,selected_minutes:0,all_items:[],
total_due:0,early_count:0,early_minutes:0,today_feedback_count:0},next_review:null};
if(url.includes('/notifications/'))return {};
throw Error('No synthetic fixture for request');}};
""")
    file = OUT / "components/today-learning/index.js"
    source = file.read_text().replace(
        "  methods: {",
        "  methods: {\n"
        "    applyGeometryFixture(serialized) { const {current,...rest}=JSON.parse(serialized); "
        "this.setData(rest); this.setCurrent(current); },",
        1,
    )
    file.write_text(source)
    markup = OUT / "components/today-learning/index.wxml"
    markup.write_text(
        markup.read_text().replace(
            '<scroll-view class="study-title-scroll"',
            '<scroll-view scroll-top="{{geometryHeadingScroll}}" class="study-title-scroll"',
            1,
        )
    )
    evidence.mkdir(parents=True, exist_ok=True)
    tracked = [
        *sorted((ROOT / "apps/miniprogram/components/today-learning").glob("index.*")),
        *sorted((ROOT / "apps/miniprogram/components/todo-card").glob("index.*")),
        *sorted((ROOT / "apps/miniprogram/pages/today").glob("index.*")),
        ROOT / "tools/today_learning_geometry.js",
        Path(__file__).resolve(),
    ]
    (evidence / "source-manifest.json").write_text(
        json.dumps(
            {
                "scope": "offline synthetic copy; no business writes or production network",
                "source_sha256": {
                    str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in tracked
                },
                "copy_only_changes": [
                    "synthetic read-only api",
                    "Today first",
                    "plugins removed",
                    "geometry fixture setter",
                    "geometry-only heading scroll binding",
                    "base library 3.17.4",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(OUT)


if __name__ == "__main__":
    main()
