import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path("/Users/bytedance/Documents/push_kids")
OUT = Path("/tmp/push-kids-footer-native-20261101")
if OUT.exists():
    raise SystemExit("Native copy already exists; do not overwrite it.")
shutil.copytree(ROOT / "apps/miniprogram", OUT)
config = json.loads((ROOT / "project.config.json").read_text())
config.update(miniprogramRoot="./", projectname="push-kids-footer-synthetic", libVersion="3.16.2")
(OUT / "project.config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
(OUT / "config.js").write_text("""module.exports={useCloud:false,cloudEnv:'',cloudService:'',
apiBasePath:'/api/v1',localApiBaseUrl:'http://127.0.0.1:1',
localFamilyId:'synthetic',localActorId:'synthetic'};\n""")
(OUT / "utils/api.js").write_text("""const child={id:'synthetic',name:'合成孩子',active:true,
grade:'三年级',avatar:'合'};
module.exports={
newIdempotencyKey:()=> 'synthetic-key',
request:async function(url,options={}){
  if(options.method&&options.method!=='GET')throw Error('Synthetic copy forbids writes');
  if(url==='/me')return {state:'bound',family:{id:'synthetic'},
    member:{role:'manager'},children:[child]};
  if(url==='/children')return [child];
  if(url.includes('/history?'))return {items:[],pending_count:0,
    has_processing:false,next_cursor:null};
  if(url.includes('/report?'))return {subjects:[],overview:{
    learning_records:1,new_knowledge_items:1,
    review_feedback_count:0,activity_records:0},review_urgency:[],review_activity:[],activity_subjects:[]};
  if(url.includes('/review-inventory/subjects?'))return {
    items:[{id:'english',name:'英语',count:42}],next_cursor:null};
  if(url.includes('/review-inventory?'))return {items:[],total:0,next_cursor:null,
    as_of_day:'2026-11-01',child_writable:true};
  return {};
}}\n""")
files = [
    "pages/review-inventory/content.wxml",
    "pages/review-inventory/content.wxss",
    "pages/review-inventory/controller.js",
    "components/review-inventory/index.wxss",
    "components/review-inventory/index.js",
    "pages/reports/index.wxml",
    "pages/reports/index.wxss",
    "app.wxss",
    "styles/tokens.wxss",
]
manifest = {
    "scope": "production templates/styles/controllers; isolated config and read-only synthetic API",
    "files": {file: hashlib.sha256((OUT / file).read_bytes()).hexdigest() for file in files},
}
(OUT / "source-baseline.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(str(OUT))
