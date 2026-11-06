"""Task-owned offline Mini Program copy; all writes are rejected, no cloud transport."""

import argparse
import hashlib
import json
from pathlib import Path

import prepare_grade_confirmation_native as base

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/private/tmp/push-kids-workday-native-20261105")


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    OUT = parser.parse_args().output.resolve()
    base.OUT = OUT
    base.main()
    config_file = OUT / "project.config.json"
    config = json.loads(config_file.read_text())
    config["projectname"] = OUT.name
    config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
    api = OUT / "utils/api.js"
    (OUT / "utils/workday-offline-base.js").write_text(api.read_text())
    api.write_text("""
const base=require('./workday-offline-base');
const subject={id:'synthetic-subject',child_id:'synthetic',name:'英语辅导课',
kind:'activity',active:true,is_custom:true};
const schedule={id:'synthetic-schedule',child_id:'synthetic',subject_id:subject.id,
workday_only:true,
time_slots:[],weekdays:[],start_time:'18:00:00',end_time:'19:00:00',active:true};
module.exports={...base,async request(url,options={}){
if(options.method&&options.method!=='GET')throw Error('合成验收：写入已禁用');
if(url.endsWith('/activity-schedules'))return {items:[schedule]};
if(url.endsWith('/travel-arrangements')||url.endsWith('/daily-tasks'))return {items:[]};
if(url.endsWith('/subjects'))return [subject];
if(url.includes('/schedule?'))return {items:[{id:'synthetic-event',name:'阅读时间',kind:'other',
source:'calendar',day:'2026-01-04',event_date:'2026-01-01',start_time:'18:00',end_time:'19:00',
workday_only:true,repeat_weekly:false,conflicts:[],past:false}]};
if(url.includes('/family-requests'))return {items:[]};
return base.request(url,options);}};
""")
    for route in ["settings", "calendar"]:
        file = OUT / "pages" / route / "index.js"
        file.write_text(
            file.read_text().replace(
                "  data: {",
                "  applyWorkdayFixture(serialized) { this.setData(JSON.parse(serialized)); },\n"
                "  data: {",
                1,
            )
        )
    manifest = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (ROOT / "apps/miniprogram").rglob("*")
        if path.is_file() and path.suffix in {".js", ".json", ".wxml", ".wxss"}
    }
    (OUT / "workday-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"WORKDAY_NATIVE_COPY={OUT}; OFFLINE_WRITE_REJECTING")


if __name__ == "__main__":
    main()
