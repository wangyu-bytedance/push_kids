// Native Mini Program rectangles using synthetic data, never authorization or media/provider calls.
// Requires an isolated copy with applyGeometryFixture(JSON), no-op load and a test-only
// scroll-top="{{geometryScrollTop}}" binding on .fp-sheet-body; see native/README.md evidence.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const STATES = ["timeline", "empty", "consent", "importing", "review", "batch", "confirm",
  "playback", "paused", "lit", "world", "place", "failed", "unknown", "viewer",
  "map-error", "ai-settings", "archived", "photo-edit", "photo", "loading", "error", "long-content", "candidates"];
const SELECTORS = [".footprints-page", ".fp-toolbar", ".fp-child", ".fp-heading", ".fp-tabs",
  ".fp-tab", ".fp-date", ".fp-button", ".fp-text-button", ".fp-archive", ".fp-select",
  ".fp-input", ".fp-close", ".fp-world-point", ".fp-sheet", ".fp-sheet-head",
  ".fp-sheet-body", ".fp-sheet-footer", ".fp-draft-top", ".fp-title", ".fp-muted",
  ".fp-visit", ".fp-empty", ".fp-draft", ".fp-grid", ".fp-thumb", ".fp-drafts",
  ".fp-world-row", ".fp-candidate", ".fp-sheet-footer .fp-full", ".fp-sheet-head .fp-place-title",
  ".fp-review-tools .fp-text-button", ".fp-scope .fp-text-button", ".fp-two-fields .fp-input",
  ".fp-draft-top .fp-grow", ".fp-loading", ".fp-error", ".fp-player", ".fp-world"];
const FIXTURE = `function(state) {
  const p=getCurrentPages().slice(-1)[0];
  p.load=()=>Promise.resolve(); p.fillPreviews=()=>Promise.resolve();p.sequence=(p.sequence||0)+1;
  p.pausePlayback(); if(p.pollTimer)clearTimeout(p.pollTimer);
  const child={id:'synthetic',name:'合成测试孩子',label:'合成测试孩子',active:true};
  const photo={id:'synthetic-photo',import_id:'synthetic-import',version:2,state:'ready',
    job_state:'succeeded',local_date:'2024-02-03',local_time:'12:30:00',has_display:false,
    previewUrl:'/assets/illustrations/record-camera.png',
    is_manual:false,dateLabel:'2024-02-03',placeLabel:'合成地点 · 较长名称用于验证窄屏换行',
    sourceLabel:'照片元数据 · 家长填写',statusLabel:'待核对',expiryLabel:'2026-10-25 12:00 UTC'};
  const visit={id:'synthetic-visit',local_date:'2024-02-03',place_name:'合成地点 · 较长名称用于验证窄屏换行',
    photo_count:3,photos:[photo],latitude:39.9,longitude:116.4};
  const data={loading:false,error:'',canWrite:true,children:[child],allChildren:[child],child,childId:child.id,
    archivedVisible:false,start:'',end:'',mode:'timeline',summary:{places:12,cities:5,countries:2,photos:37,drafts:3,unlocated_photos:2},
    visits:[visit],sheet:'',sheetError:'',saving:false,selectedCount:1,drafts:[{...photo,selected:true}],
    aiEnabled:false,photoConsent:false,form:{local_date:'2024-02-03',local_time:'12:30',day_order:0,
      place_name:'合成地点',city:'合成城市',country:'中国'},editing:photo,manual:false,batchEdit:false,
    photoList:[photo],photoIndex:0,photoCursor:null,hasPreviousPhotoPage:false,
    mapMode:'auto',mapError:false,markers:[],polyline:[],mapLatitude:39.9,mapLongitude:116.4,mapScale:10,
    mapData:{items:[{id:1,label:'合成地点',latitude:39.9,longitude:116.4,worldX:75,worldY:35,visit_days:2}],outside_visit_days:2},
    placeVisits:[visit],placeCursor:null,playback:[visit],currentPoint:visit,playbackIndex:0,playing:false,
    confirmCount:3,unlocatedCount:1,hasPendingUpload:false,placeResults:[],geometryScrollTop:0};
  if(state==='empty'){data.visits=[];data.summary={};}
  if(state==='consent'||state==='importing'){data.sheet='consent';data.saving=state==='importing';data.importProgress=40;}
  if(['review','failed','unknown'].includes(state)){data.sheet='review';
    if(state==='failed'){data.drafts[0].job_state='failed';data.drafts[0].statusLabel='解析失败，可手动补充';}
    if(state==='unknown'){data.drafts[0].dateLabel='待补日期';data.drafts[0].local_date=null;}}
  if(state==='batch'||state==='photo-edit'){data.sheet='edit';data.batchEdit=state==='batch';
    if(state==='photo-edit')data.editing={...photo,state:'confirmed'};}
  if(state==='candidates'){data.sheet='edit';data.placeResults=[
    {id:'synthetic-place-1',place_name:'合成地点候选一 · 较长名称用于验证窄屏完整换行',city:'合成城市',country:'中国'},
    {id:'synthetic-place-2',place_name:'合成地点候选二 · 较长名称用于验证窄屏完整换行',city:'合成城市',country:'中国'},
    {id:'synthetic-place-3',place_name:'合成地点候选三 · 较长名称用于验证窄屏完整换行',city:'合成城市',country:'中国'}];}
  if(state==='confirm')data.sheet='confirm';
  if(['playback','paused'].includes(state)){data.mode='playback';data.playing=state==='playback';}
  if(['lit','world','map-error'].includes(state))data.mode='lit';
  if(state==='world')data.mapMode='world';
  if(state==='map-error')data.mapError=true;
  if(state==='place')data.sheet='place';
  if(state==='viewer')data.canWrite=false;
  if(state==='ai-settings')data.sheet='settings';
  if(state==='archived'){data.child={...child,active:false,label:'合成测试孩子（已归档）'};data.archivedVisible=true;}
  if(state==='photo')data.sheet='photo';
  if(state==='loading'){data.loading=true;data.visits=[];}
  if(state==='error')data.error='合成网络故障提示，可重新读取；表单和已上传内容保留。';
  if(state==='long-content'){data.child={...child,name:'合成测试孩子的长姓名用于窄屏验证',label:'合成测试孩子的长姓名用于窄屏验证'};data.children=[data.child];}
  if(!p.applyGeometryFixture)throw Error('isolated copy requires applyGeometryFixture(serialized)');
  p.applyGeometryFixture(JSON.stringify(data));return true;
}`;
const QUERY = `function(selectors){return new Promise(resolve=>{
  const q=wx.createSelectorQuery();selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize','minWidth','maxWidth','display']}));
  q.selectViewport().scrollOffset();q.exec(groups=>{const i=wx.getSystemInfoSync(),nodes={};
  selectors.forEach((s,k)=>nodes[s]=(groups[k]||[]).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize,minWidth:n.minWidth,maxWidth:n.maxWidth,display:n.display})));
  const p=getCurrentPages().slice(-1)[0];
  resolve({viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting},nodes,
    dataCounts:{children:p.data.children.length,visits:p.data.visits.length,drafts:p.data.drafts.length},
    scrollLeft:(groups[selectors.length]||{}).scrollLeft||0});});});}`;
function audit(capture) {
  const errors = [], { viewport, nodes } = capture;
  const check = (ok, message) => { if (!ok) errors.push(message); };
  check(viewport.width === capture.expectedWidth, "wrong viewport width");
  check(viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[capture.expectedWidth], "wrong screen height");
  check(Math.abs(capture.scrollLeft) <= 1, "horizontal root scroll");
  for (const [selector, rects] of Object.entries(nodes)) for (const rect of rects) {
    check(rect.left >= -1 && rect.right <= viewport.width + 1, `${selector} outside horizontal viewport`);
    if ([".fp-child", ".fp-tab", ".fp-button", ".fp-text-button", ".fp-close", ".fp-select", ".fp-date", ".fp-input", ".fp-archive", ".fp-thumb", ".fp-drafts", ".fp-world-row", ".fp-candidate"].includes(selector))
      check(rect.width >= 43 && rect.height >= 43, `${selector} target below 44px`);
    if(rect.fontSize)check(parseFloat(rect.fontSize)>=14, `${selector} text below 14px`);
  }
  const footer = nodes[".fp-sheet-footer"]?.[0], sheet = nodes[".fp-sheet"]?.[0];
  if (sheet && footer) check(sheet.top >= -1 && footer.bottom <= viewport.height + 1, "sheet actions outside native window");
  check((nodes[".fp-tab"] || []).length === 3, "three view controls missing");
  check(nodes[".fp-child"]?.length === 1 && capture.dataCounts?.children === 1, "child fixture not rendered");
  for(const selector of [".fp-tab", ".fp-scope .fp-text-button", ".fp-two-fields .fp-input"]){
    const rects=nodes[selector]||[];
    if(rects.length>1)check(Math.max(...rects.map(r=>r.width))-Math.min(...rects.map(r=>r.width))<=1, `${selector} unequal columns`);
    rects.slice(1).forEach((r,i)=>check(r.left-rects[i].right>=7, `${selector} gap below 8px or overlap`));
  }
  const footerButtons=nodes[".fp-sheet-footer .fp-full"]||[];
  const footerCounts={consent:2,importing:2,review:1,failed:1,unknown:1,batch:1,
    "photo-edit":1,candidates:1,confirm:2,"ai-settings":1,photo:1};
  check(footerButtons.length===(footerCounts[capture.state]||0), "sheet footer controls missing or unexpected");
  footerButtons.forEach((r,i)=>{
    check(Math.abs(r.width-(viewport.width-32))<=1, "footer button not full content width");
    if(i)check(r.top-footerButtons[i-1].bottom>=7, "footer action gap below 8px");
  });
  (nodes[".fp-select"]||[]).forEach(r=>check(Math.abs(r.width-44)<=1, "selection action not fixed 44px"));
  (nodes[".fp-close"]||[]).forEach(r=>check(Math.abs(r.width-48)<=1&&Math.abs(r.height-48)<=1, "close action not fixed 48px"));
  const title=nodes[".fp-sheet-head .fp-place-title"]?.[0],close=nodes[".fp-close"]?.[0];
  if(title&&close)check(title.right<=close.left-7, "sheet title overlaps close action");
  if(close)check(Math.abs(close.right-(viewport.width-16))<=1,"close action not aligned to sheet edge");
  (nodes[".fp-draft-top .fp-grow"]||[]).forEach((r,i)=>{
    const select=nodes[".fp-select"]?.[i];if(select)check(r.left-select.right>=7, "draft copy overlaps selection");
  });
  const sheetStates=["consent","importing","review","batch","confirm","place","failed","unknown","ai-settings","photo-edit","photo","candidates"];
  check(Boolean(sheet)===sheetStates.includes(capture.state), "unexpected sheet state");
  if(["review","failed","unknown"].includes(capture.state))check(nodes[".fp-draft"]?.length===1&&capture.dataCounts.drafts===1,"draft fixture missing");
  if(["timeline","viewer","archived","long-content"].includes(capture.state))check(nodes[".fp-visit"]?.length===1&&!(nodes[".fp-empty"]||[]).length,"timeline content/empty mismatch");
  if(capture.state==="empty")check(nodes[".fp-empty"]?.length===1&&!(nodes[".fp-visit"]||[]).length,"empty fixture mismatch");
  if(capture.state==="loading")check(nodes[".fp-loading"]?.length===1,"loading fixture missing");
  if(capture.state==="error")check(nodes[".fp-error"]?.length===1,"error fixture missing");
  if(["playback","paused"].includes(capture.state))check(nodes[".fp-player"]?.length===1,"player fixture missing");
  if(capture.state==="world")check(nodes[".fp-world"]?.length===1,"world fixture missing");
  if(["lit","world","map-error"].includes(capture.state))check(nodes[".fp-scope .fp-text-button"]?.length===3,"map scope controls missing");
  if(["batch","photo-edit","candidates"].includes(capture.state))check(nodes[".fp-two-fields .fp-input"]?.length===2,"edit city/country fields missing");
  if(["review","failed","unknown"].includes(capture.state)){
    const tools=nodes[".fp-review-tools .fp-text-button"]||[];
    check(tools.length===2,"review controls missing");
    if(tools.length===2)check(tools[1].left-tools[0].right>=7,"review control gap below 8px or overlap");
  }
  if(capture.state==="candidates"){
    const candidates=nodes[".fp-candidate"]||[];
    const body=nodes[".fp-sheet-body"]?.[0];
    check(candidates.length===3,"place candidates missing");
    candidates.forEach(r=>{
      check(Math.abs(r.width-(viewport.width-32))<=1,"place candidate not full content width");
      if(body)check(r.top>=body.top-1&&r.bottom<=body.bottom+1,"place candidate outside visible sheet body");
    });
  }
  return errors;
}
async function main() {
  if(process.argv[2]==="audit") {
    for(const file of process.argv.slice(3)){const data=JSON.parse(fs.readFileSync(file));const errors=audit(data);
      if(errors.length)throw Error(`${file}: ${errors.join('; ')}`);
      if(data.screenshotError||!data.screenshotSha256||!data.screenshotPixels)throw Error(`${file}: screenshot evidence missing`);
      const bytes=fs.readFileSync(path.join(path.dirname(file),data.screenshot));
      if(crypto.createHash("sha256").update(bytes).digest("hex")!==data.screenshotSha256)throw Error(`${file}: screenshot SHA mismatch`);
      if(bytes.readUInt32BE(16)!==data.screenshotPixels.width||bytes.readUInt32BE(20)!==data.screenshotPixels.height)
        throw Error(`${file}: screenshot size mismatch`);
    }
    return;
  }
  const [widthText,directory,onlyState]=process.argv.slice(2),width=Number(widthText);
  if(![320,390,430].includes(width)||!directory)throw Error("usage: <320|390|430> <directory> [state]");
  const socket=new WebSocket(process.env.MINIPROGRAM_AUTOMATION_WS||"ws://127.0.0.1:9424");
  const pending=new Map();let seq=0;
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    if(process.env.NATIVE_GEOMETRY_DEBUG)console.log(`NATIVE_SEND ${method}`);
    const id=String(++seq),timer=setTimeout(()=>{pending.delete(id);reject(Error(`${method} timed out`));},15000);
    pending.set(id,m=>{clearTimeout(timer);if(process.env.NATIVE_GEOMETRY_DEBUG)console.log(`NATIVE_DONE ${method}`);m.error?reject(Error(`${method}: ${JSON.stringify(m.error)}`)):resolve(m.result);});
    socket.send(JSON.stringify({id,method,params}));
  });
  socket.onmessage=e=>{const m=JSON.parse(e.data),cb=pending.get(m.id);if(cb){pending.delete(m.id);cb(m);}};
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  const call=(functionDeclaration,args=[])=>send("App.callFunction",{functionDeclaration,args});
  try {
    const safe=await call("function(){return getApp().globalData.useCloud===false;}");
    if(!safe.result)throw Error("requires isolated useCloud=false project");
    const actual=(await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.screenHeight};}")).result;
    if(actual.width!==width||actual.height!=={320:568,390:844,430:932}[width])
      throw Error(`native runtime viewport ${actual.width}x${actual.height}; expected ${width}x${{320:568,390:844,430:932}[width]}; reconnect automation after device changes`);
    const current=await send("App.getCurrentPage");
    if(current.path!=="pages/footprints/index") {
      await call("function(){wx.navigateTo({url:'/pages/footprints/index'});return true;}");
      await new Promise(r=>setTimeout(r,500));
      const opened=await send("App.getCurrentPage");
      if(opened.path!=="pages/footprints/index")throw Error("footprints page did not open");
    }
    fs.mkdirSync(directory,{recursive:true});
    let failures=0;
    for(const state of onlyState?[onlyState]:STATES){
      // The isolated-copy method parses JSON in the page realm, preserving array lengths.
      await call(FIXTURE,[state]);
      await call("function(){wx.pageScrollTo({scrollTop:0,duration:0});return true;}");
      await new Promise(r=>setTimeout(r,100));
      if(state==="candidates"){
        const before=(await call(QUERY,[SELECTORS])).result;
        const top=before.nodes[".fp-candidate"][0].top-before.nodes[".fp-sheet-body"][0].top;
        await call("function(top){getCurrentPages().slice(-1)[0].applyGeometryFixture(JSON.stringify({geometryScrollTop:top}));return true;}",[Math.max(0,top-8)]);
        await new Promise(r=>setTimeout(r,100));
      }
      const capture={...(await call(QUERY,[SELECTORS])).result,state,expectedWidth:width,capturedAt:new Date().toISOString(),fixture:"isolated copy with page-realm JSON harness; synthetic; no photo/provider/business writes"};
      capture.errors=audit(capture);
      try {
        const shot=await send("App.captureScreenshot");
        const encoded=typeof shot==="string"?shot:(shot.data||shot.base64);
        const bytes=Buffer.from(encoded.replace(/^data:image\/\w+;base64,/,""),"base64");
        capture.screenshot=`${state}-${width}.png`;
        capture.screenshotSha256=crypto.createHash("sha256").update(bytes).digest("hex");
        capture.screenshotPixels={width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)};
        fs.writeFileSync(path.join(directory,capture.screenshot),bytes);
      } catch(error) {
        const stale=path.join(directory,`${state}-${width}.png`);if(fs.existsSync(stale))fs.unlinkSync(stale);
        capture.screenshot="NOT_RUN: screenshot unavailable";capture.screenshotError=String(error.message).slice(0,200);
      }
      fs.writeFileSync(path.join(directory,`${state}-${width}.json`),JSON.stringify(capture,null,2)+"\n");
      console.log(`${state}-${width}: ${capture.errors.length?capture.errors.join('; '):capture.screenshotError||'PASS'}`);
      if(capture.errors.length||capture.screenshotError)failures++;
    }
    if(failures)throw Error(`${failures} native state audits failed`);
  } finally {socket.close();}
}
if(require.main===module)main().catch(error=>{console.error(error.message);process.exitCode=1;});
module.exports={audit,STATES,FIXTURE};
