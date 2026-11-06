"""Offline BUG-035 native copy; real templates/controllers, synthetic transport only."""

import hashlib
import json
from pathlib import Path

import prepare_record_type_native as base


def main():
    base.OUT = Path("/private/tmp/push-kids-travel-diary-native-20261025")
    base.main()
    config = base.OUT / "project.config.json"
    value = json.loads(config.read_text())
    value["projectname"] = "push-kids-travel-diary-synthetic"
    value["libVersion"] = "3.16.2"
    config.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    with (base.OUT / "utils/api.js").open("a") as output:
        output.write("""
const original=module.exports.request;
let batch=null, rows=[], confirmed=[], aiEnabled=false;
module.exports.syntheticFailUpload=false;
module.exports.uploadFootprint=async(id)=>{
  if(module.exports.syntheticFailUpload&&id==='synthetic-1'){
    module.exports.syntheticFailUpload=false;throw Error('第2张上传失败，请重试');
  }
  const p=rows.find(p=>p.id===id);p.received_at='2026-10-25T00:00:00Z';
  p.state='ready';p.has_display=true;p.job_state='succeeded';return p;
};
module.exports.request=async(url,options={})=>{
  const data=options.data||{};
  if(url==='/footprints/imports'&&options.method==='POST'){
    if(!batch){batch={id:'synthetic-import'};rows=Array.from({length:data.count},(_,i)=>({id:'synthetic-'+i,import_id:batch.id,ordinal:i,version:1,state:'uploading',local_date:null,has_display:false,candidates:[]}));}
    return {...batch,photos:rows.map(p=>({...p}))};
  }
  if(url==='/footprints/preferences'&&options.method==='PATCH'){
    aiEnabled=data.ai_enabled;return data;
  }
  if(url==='/footprints/preferences')return {ai_enabled:aiEnabled,consented:true};
  if(url.startsWith('/footprints/drafts?'))return {items:rows.map(p=>({...p})),next_cursor:null};
  if(url.startsWith('/footprints/photos/')&&options.method==='PATCH'){
    const id=url.split('/')[3].split('?')[0],p=[...rows,...confirmed].find(p=>p.id===id);
    if(!p)throw Error('Synthetic photo not found');
    Object.assign(p,data,{version:p.version+1});return {...p};
  }
  if(url.includes('/confirm?')&&options.method==='POST'){
    for(const item of data.photos){const p=rows.find(p=>p.id===item.id);
      if(!p.local_date)throw Error('请补充日期');confirmed.push({...p,state:'confirmed'});}
    rows=rows.filter(p=>!data.photos.some(item=>item.id===p.id));return {confirmed:data.photos};
  }
  if(url.startsWith('/footprints/summary?'))return {photos:confirmed.length,
    places:confirmed.length?1:0,cities:confirmed.length?1:0,countries:0,drafts:rows.length};
  const v={id:'synthetic-visit',local_date:confirmed[0]?.local_date,place_name:'合成测试地点',
    latitude:39.9,longitude:121.6,coordinate_system:'gcj02',
    photo_count:confirmed.length,photos:confirmed.slice(0,4)};
  if(url.startsWith('/footprints/visits?'))return {items:confirmed.length?[v]:[],next_cursor:null};
  if(url.includes('/visits/')&&url.includes('/photos?')){
    const focus=decodeURIComponent((url.match(/focus_photo_id=([^&]+)/)||[])[1]||'');
    const cursor=decodeURIComponent((url.match(/cursor=([^&]+)/)||[])[1]||'');
    let index=Math.max(0,confirmed.findIndex(p=>p.id===focus)),end=confirmed.length;
    if(cursor.startsWith('before-')){end=Number(cursor.slice(7));index=Math.max(0,end-20);}
    if(cursor.startsWith('after-'))index=Number(cursor.slice(6))+1;
    return {items:confirmed.slice(index,end),
      next_cursor:end<confirmed.length?'after-'+(end-1):null,
      previous_cursor:index?'before-'+index:null};
  }
  if(url.startsWith('/footprints/map?'))return {items:confirmed.length?
    [{...v,id:1,place_key:'synthetic-place',visit_days:1,label:'合成测试地点'}]:[],
    bounds:[120,38,123,41]};
  if(url.startsWith('/footprints/playback?'))return {
    items:confirmed.length?[v]:[],revision:1,next_cursor:null};
  return original(url,options);
};
""")
    files = [
        "pages/footprints/" + file
        for file in [
            "controller.js",
            "imports.js",
            "photos.js",
            "presentation.js",
            "embedded.js",
            "index.wxml",
            "index.wxss",
        ]
    ]
    manifest = {
        "scope": "offline synthetic transport, geometry/scroll bindings only in copy",
        "source_sha256": {
            file: hashlib.sha256((base.ROOT / "apps/miniprogram" / file).read_bytes()).hexdigest()
            for file in files
        },
    }
    (base.OUT / "travel-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
