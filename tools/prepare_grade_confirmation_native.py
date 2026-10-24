"""Build a synthetic offline layout copy; production transport/config stay unchanged."""

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/private/tmp/push-kids-grade-native-20261024")


def main():
    source = ROOT / "apps/miniprogram"
    shutil.copytree(source, OUT, dirs_exist_ok=True)
    config = json.loads((OUT / "project.config.json").read_text())
    config.update(projectname="push-kids-grade-synthetic", libVersion="3.17.4")
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
grade:'小学二年级',grade_revision:1,daily_budget_minutes:15,avatar:'合'};
let gradeInteraction=false,gradeAttempts=0;
module.exports={newIdempotencyKey:()=> 'synthetic-key',removePreview(){},
enableGradeInteraction(){gradeInteraction=true;gradeAttempts=0;},gradeAttempts:()=>gradeAttempts,
async request(url,options={}){
if(options.method&&options.method!=='GET'){
if(url.endsWith('/grade-confirmation'))gradeAttempts++;
throw Error('Synthetic copy forbids business writes');}
if(url==='/me')return {state:'bound',family:{id:'synthetic'},
member:{id:'synthetic',role:'manager'},children:[child]};
if(url==='/children/grade-confirmations')return {school_year:2026,can_confirm:true,
items:gradeInteraction?[{id:'synthetic',name:'小满',revision:1,current_grade:'小学二年级',
suggested_grade:'小学三年级',reason:'annual_progression'}]:[]};
if(url.startsWith('/children?')||url==='/children')return [child];
if(url.endsWith('/subjects'))return [];
if(url.endsWith('/current'))return {day:'2026-10-24',version:1,
eligibility:'recent_new',task:null,proposal:null,job:null};
if(url.endsWith('/dashboard'))return {day:'2026-10-24',todo_count:0,
required_todo_count:0,estimated_minutes:0,todo_groups:[],schedule_items:[],
activity_suggestions:[],activity_remaining_count:0,analyzing_count:0,failed_count:0,
pending_confirmation_count:0,daily_summary:{record_count:0,subjects:[]},
daily_tasks:{day:'2026-10-24',items:[],total_count:0,remaining_count:0},
review_selection:{plan_id:'synthetic-plan',sessions:[],selected_count:0,planned_count:0,
selected_minutes:0,all_items:[],total_due:0,early_count:0,early_minutes:0,today_feedback_count:0},
next_review:null};
if(url.includes('/notifications/'))return {};
throw Error('No synthetic fixture for request');}};
""")
    app_file = OUT / "app.js"
    app_file.write_text(
        app_file.read_text().replace(
            "App({",
            """App({
  startGradeInteractionFixture() {
    const api=require('./utils/api');api.enableGradeInteraction();
    if(this.gradeConfirmation)this.gradeConfirmation.background();
    this.gradeConfirmation=require('./utils/grade-confirmation').createController(
      this,api,()=>getCurrentPages().slice(-1)[0]);
    this.gradeConfirmation.foreground();
    this.gradeConfirmation.handle(getCurrentPages().slice(-1)[0],{action:'show',blocked:false});
  },
  gradeFixtureAttempts(){return require('./utils/api').gradeAttempts();},
""",
            1,
        )
    )
    # Only copy-only fixture injection; WXML, WXSS and production handlers remain exact.
    for relative in ["pages/today/index.js", "pages/child-edit/index.js"]:
        file = OUT / relative
        file.write_text(
            file.read_text().replace(
                "  data: {",
                "  applyGeometryFixture(serialized) { this.setData(JSON.parse(serialized)); },\n"
                "  data: {",
                1,
            )
        )
    files = [
        *source.glob("components/grade-confirmation/*"),
        source / "utils/grade-confirmation.js",
        source / "utils/child-context.js",
        source / "app.js",
        source / "pages/today/index.js",
        source / "pages/today/index.wxml",
        source / "pages/child-edit/index.wxml",
        source / "pages/child-edit/index.wxss",
    ]
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT / "grade-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
