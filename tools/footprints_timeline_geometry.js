// Official DevTools automation; production templates/styles with offline synthetic data.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { FIXTURE } = require("./footprints_geometry");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9584);
const out = path.resolve("docs/quality/evidence/footprints-timeline-20261024/native");
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = ({ data }) => { const m = JSON.parse(data); pending.get(m.id)?.(m); };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, (m) => { pending.delete(id); clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const settle = () => new Promise((resolve) => setTimeout(resolve, 180));
const selectors = [".footprints-page", ".fp-tabs", ".fp-tab", ".fp-tab.on", ".fp-import", ".fp-button", ".fp-sheet-footer .fp-button", ".fp-text-button", ".fp-date-label", ".fp-visit", ".fp-card", ".fp-grid", ".fp-thumb", ".fp-thumb-media", ".fp-thumb-image", ".fp-time", ".fp-manual", ".fp-sheet", ".fp-sheet-body", ".fp-sheet-footer", ".fp-close", ".fp-drafts", ".fp-world-row", ".fp-candidate"];
async function fixture(state, standalone = false) {
  const baseState = ({ overview: "timeline", preview_failed: "timeline", long: "long-content", settings: "ai-settings", saving: "ai-settings", older_window: "timeline", standalone: "timeline", edit: "photo-edit" })[state] || state;
  await call(standalone ? FIXTURE : FIXTURE.replace("const p=getCurrentPages().slice(-1)[0];", "const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');"), [baseState]);
  await call(`function(state,standalone){const page=getCurrentPages().slice(-1)[0],c=standalone?page:page.selectComponent('#travel-diary');
    const image='/assets/illustrations/record-camera.png',photo={id:'synthetic-a',is_manual:false,local_time:'14:30:59',has_display:false,previewUrl:state==='preview_failed'?'':image};
    const visits=[{id:'synthetic-recent',local_date:'2026-10-24',place_name:state==='long'?'合成地点的较长名称用于验证窄屏完整换行':'合成地点一',photo_count:2,photos:[photo,{...photo,id:'synthetic-b',local_time:null}]},
      {id:'synthetic-older',local_date:'2026-10-03',place_name:'合成地点二',photo_count:1,photos:[{...photo,id:'synthetic-c',local_time:'10:20:00'}]},
      {id:'synthetic-manual',local_date:'2026-09-18',place_name:'合成手动地点',photo_count:0,photos:[{id:'synthetic-d',is_manual:true,has_display:false,local_time:null}]}];
    if(state==='older_window')visits.forEach(v=>v.local_date=v.local_date.replace('2026','2025'));
    const patch={nextCursor:null,hasArchivedChildren:false};
    if(!['empty','loading'].includes(state))patch.visits=visits;
    if(state==='saving')patch.saving=true;
    if(['overview','preview_failed','long','older_window','standalone'].includes(state))patch.summary={places:3,cities:2,countries:1,photos:3};
    c.applyGeometryFixture(JSON.stringify(patch));wx.pageScrollTo({scrollTop:0,duration:0});return true;}`, [state, standalone]);
}
async function capture(state, standalone = false) {
  await settle();
  const data = await call(`function(selectors,standalone){return new Promise(resolve=>{
    const p=getCurrentPages().slice(-1)[0],c=standalone?p:p.selectComponent('#travel-diary'),i=wx.getSystemInfoSync(),q=wx.createSelectorQuery().in(c),nodes={};
    selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize','borderRadius','backgroundColor','color']}));q.selectViewport().scrollOffset();
    q.exec(rows=>{selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize,borderRadius:n.borderRadius,backgroundColor:n.backgroundColor,color:n.color})));
      resolve({nodes,scrollLeft:(rows[selectors.length]||{}).scrollLeft||0,sheet:c.data.sheet,mode:c.data.mode,
        visits:c.data.visits.map(v=>({id:v.id,date:v.local_date,photoCount:v.photo_count,photos:v.photos.map(p=>({manual:!!p.is_manual,time:p.timeLabel,preview:!!p.previewUrl}))})),
        viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting}});});});}`, [selectors, standalone]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); };
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport mismatch");
  check(data.scrollLeft === 0, "horizontal root scroll");
  for (const [selector, rows] of Object.entries(data.nodes)) for (const r of rows) {
    check(r.left >= -1 && r.right <= width + 1, selector + " horizontal overflow");
    if ([".fp-tab", ".fp-import", ".fp-button", ".fp-text-button", ".fp-thumb", ".fp-close", ".fp-drafts"].includes(selector)) check(r.width >= 43 && r.height >= 43, selector + " target below 44px");
    if (r.fontSize && selector !== ".fp-close") check(parseFloat(r.fontSize) >= 14, selector + " font below 14px");
    if ([".fp-tabs", ".fp-tab", ".fp-button", ".fp-drafts"].includes(selector)) check(parseFloat(r.borderRadius) >= r.height / 2 - 1, selector + " is not pill");
    if ([".fp-import", ".fp-sheet-footer .fp-button"].includes(selector)) check(r.height >= 47 && parseFloat(r.fontSize) >= 16, selector + " primary dimensions");
  }
  const tabs = data.nodes[".fp-tab"], selected = data.nodes[".fp-tab.on"];
  check(tabs.length === 3 && selected.length === 1, "tab selection mismatch");
  check(Math.max(...tabs.map(r => r.width)) - Math.min(...tabs.map(r => r.width)) <= 1, "unequal tabs");
  tabs.slice(1).forEach((r, i) => check(r.left >= tabs[i].right - 1, "tab overlap"));
  check(data.visits.every((v, i) => !i || v.date <= data.visits[i - 1].date), "date order");
  if (["overview", "preview_failed", "long", "older_window", "standalone"].includes(state)) {
    check(data.nodes[".fp-thumb"].length === 3 && data.nodes[".fp-manual"].length === 1, "manual/media shape mismatch");
    check(data.nodes[".fp-thumb-image"].length === (state === "preview_failed" ? 0 : 3), "preview/manual image mismatch");
    check(data.visits[0].photos[0].time === "14:30" && data.visits[0].photos[1].time === "时刻未知", "capture labels mismatch");
    const thumbs = data.nodes[".fp-thumb"]; check(thumbs[1].left - thumbs[0].right >= 7, "thumbnail gap below 8px");
  }
  if (["settings", "saving"].includes(state)) check(data.nodes[".fp-sheet"][0]?.height <= 280, "settings not compact");
  const shot = await send("App.captureScreenshot"), bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true }); const name = `${state}-${width}`;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({ ...data, state, errors, capturedAt: new Date().toISOString(), screenshot: name + ".png", screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS")); return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  await call("function(){return new Promise(resolve=>wx.switchTab({url:'/pages/records/index',success:()=>resolve(true)}));}"); await settle();
  await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}"); await settle();
  let failures = 0;
  for (const state of ["overview", "preview_failed", "empty", "loading", "error", "viewer", "long", "playback", "lit", "settings", "saving", "photo", "older_window", "consent", "review", "edit", "confirm"]) {
    await fixture(state); failures += await capture(state);
  }
  await call("function(){return new Promise(resolve=>wx.reLaunch({url:'/pages/footprints/index',success:()=>resolve(true)}));}"); await settle();
  await fixture("standalone", true); failures += await capture("standalone", true);
  socket.close(); process.exitCode = failures ? 1 : 0;
}
main().catch((error) => { console.error(error.message); socket.close(); process.exitCode = 1; });
