// Official native Mini Program capture against the isolated synthetic project only.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { audit, SELECTORS } = require("./review_inventory_geometry");
const STATES = ["normal", "superseded", "menu", "viewer", "long", "deleted", "empty"];
const FIXTURE = `function(state, embedded) {
  const page=getCurrentPages().slice(-1)[0];
  const p=embedded?page.selectComponent('#inventory-component'):page;
  if(!p||!p.applyGeometryFixture)throw Error('isolated fixture method missing');
  const normal=state==='normal';
  const entry={knowledge_id:'synthetic-k',review_id:'synthetic-r',subject_id:'synthetic-subject',subject_name:'数学',
    review_status:normal?'normal':'superseded',source_submission_id:'synthetic-source',
    knowledge_name:state==='long'?'10以内加法：用数量关系说明、口算与应用情境的完整练习范围':'10以内加减法',
    reviewCountText:'已复习3次',lastReviewText:'上次10月18日',can_schedule:normal,
    compactDateText:normal?'建议10月21日':'',arrangementText:normal?'等待安排':'',
    coverageText:normal?'':state==='deleted'?'原承接词条已删除':'由「'+(state==='long'?'20以内加减法：包含旧范围的同类完整练习，保留相同的数量关系与口算能力':'20以内加减法')+'」承接'};
  const items=state==='empty'?[]:[entry];
  p.applyGeometryFixture(JSON.stringify({reviewStatus:normal?'normal':'superseded',view:normal?'time':'count',
    views:normal?[{id:'time',label:'按时间'},{id:'subject',label:'按科目'},{id:'count',label:'按次数'}]:[{id:'subject',label:'按科目'},{id:'count',label:'按次数'}],
    childId:'synthetic',items,groups:items.length?[{key:'synthetic-subject',name:'数学',mark:'数',tone:'math',expanded:true,entries:items}]:[],
    loaded:true,loading:false,total:items.length,canWrite:state!=='viewer',count:null,countLabel:'全部',offset:1,
    tomorrowLabel:'明天 10月21日',dayAfterLabel:'后天 10月22日',asOfDay:'2026-10-20',
    error:'',notice:'',actionError:'',target:null,actionMenuId:'',actionMenuGroup:'',actionMenuAbove:false,
    pickerOpen:false,showCountInput:false,deleting:false,saving:false,nextCursor:null,pageNumber:1}));
  if(state==='menu')p.openActions({currentTarget:{dataset:{id:'synthetic-k'}}});
  return true;
}`;
const QUERY = `function(selectors,embedded){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0],target=embedded?p.selectComponent('#inventory-component'):p;
  const q=wx.createSelectorQuery().in(target);
  selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true}));
  q.exec(results=>{const i=wx.getSystemInfoSync();resolve({
    reviewStatus:target.data.reviewStatus,view:target.data.view,readOnly:!target.data.canWrite,empty:!target.data.items.length,
    viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting},
    nodes:results.map(group=>(group||[]).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height})))
  });});});}`;
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
async function main() {
  if (process.argv[2] === "audit") {
    for (const file of process.argv.slice(3)) {
      const capture = JSON.parse(fs.readFileSync(file));
      const errors = audit(capture, capture.expectedWidth);
      if (errors.length) throw Error(`${file}: ${errors.join("; ")}`);
      const bytes = fs.readFileSync(path.join(path.dirname(file), capture.screenshot));
      if (sha(bytes) !== capture.screenshotSha256) throw Error(`${file}: PNG SHA mismatch`);
    }
    return;
  }
  const [widthText, directory, mode] = process.argv.slice(2), width = Number(widthText);
  const geometryOnly = mode === "--geometry-only";
  if (![320, 390, 430].includes(width) || !directory) throw Error("usage: <320|390|430> <directory> | audit <files>");
  const socket = new WebSocket(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9441");
  let seq = 0;
  const pending = new Map();
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++seq), timer = setTimeout(() => { pending.delete(id); reject(Error(`${method} timeout`)); }, method === "App.captureScreenshot" ? 40000 : 15000);
    pending.set(id, m => { clearTimeout(timer); m.error ? reject(Error(`${method} failed`)) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
  socket.onmessage = e => { const m = JSON.parse(e.data), cb = pending.get(m.id); if (cb) { pending.delete(m.id); cb(m); } };
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  const call = (functionDeclaration, args = []) => send("App.callFunction", { functionDeclaration, args });
  try {
    const safe = (await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")).result;
    if (!safe) throw Error("isolated project required");
    const info = (await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.screenHeight};}")).result;
    if (info.width !== width || info.height !== { 320: 568, 390: 844, 430: 932 }[width]) throw Error(`wrong runtime viewport ${info.width}x${info.height}`);
    fs.mkdirSync(directory, { recursive: true });
    for (const embedded of [false, true]) {
      const wanted = embedded ? "pages/embedded/index" : "pages/review-inventory/index";
      if ((await send("App.getCurrentPage")).path !== wanted) {
        await call("function(url){wx.navigateTo({url});return true;}", [`/${wanted}`]);
        let ready = false;
        for (let attempt = 0; attempt < 20; attempt++) {
          await new Promise(resolve => setTimeout(resolve, 250));
          if ((await send("App.getCurrentPage")).path === wanted) { ready = true; break; }
        }
        if (!ready) throw Error("native page did not open");
      }
      for (const state of STATES) {
        await call(FIXTURE, [state, embedded]);
        await call("function(){wx.pageScrollTo({scrollTop:0,duration:0});return true;}");
        await new Promise(resolve => setTimeout(resolve, 100));
        const capture = { ...(await call(QUERY, [SELECTORS, embedded])).result,
          state, embedded, expectedWidth: width, capturedAt: new Date().toISOString(),
          fixture: "isolated synthetic page-realm JSON; production WXML/WXSS unchanged" };
        capture.errors = audit(capture, width);
        if (capture.empty !== (state === "empty") || capture.readOnly !== (state === "viewer") ||
            capture.reviewStatus !== (state === "normal" ? "normal" : "superseded")) capture.errors.push("fixture did not render");
        const stem = `${embedded ? "embedded" : "page"}-${state}-${width}`;
        fs.writeFileSync(path.join(directory, `${stem}.json`), JSON.stringify({ ...capture, screenshot: "NOT_RUN" }, null, 2) + "\n");
        if (capture.errors.length) throw Error(capture.errors.join("; "));
        if (geometryOnly) {
          console.log(`${stem}: GEOMETRY PASS; screenshot NOT_RUN`);
          continue;
        }
        const shot = await send("App.captureScreenshot"), encoded = typeof shot === "string" ? shot : shot.data || shot.base64;
        const bytes = Buffer.from(encoded.replace(/^data:image\/\w+;base64,/, ""), "base64");
        capture.screenshot = `${stem}.png`; capture.screenshotSha256 = sha(bytes);
        capture.screenshotPixels = { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
        fs.writeFileSync(path.join(directory, capture.screenshot), bytes);
        fs.writeFileSync(path.join(directory, `${stem}.json`), JSON.stringify(capture, null, 2) + "\n");
        console.log(`${stem}: ${capture.errors.length ? capture.errors.join("; ") : "PASS"}`);
        if (capture.errors.length) throw Error("native audit failed");
      }
    }
  } finally { socket.close(); }
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
