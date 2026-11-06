const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const host = process.argv[2] || "standalone";
const expectedWidth = Number(process.argv[3] || 320);
const screenHeights = {320:568,390:844,430:932};
const expectedScreenHeight = screenHeights[expectedWidth];
const port = Number(process.argv[4] || 9592);
if (!["standalone", "embedded"].includes(host) || !expectedScreenHeight ||
    !Number.isInteger(port) || port < 1 || port > 65535) {
  throw Error("usage: node collector.js <standalone|embedded> <320|390|430> [automation-port]");
}
const states = ["empty","drafts","legacy","loading","error","viewer","archived"];
const out = "/Users/bytedance/Documents/push_kids/docs/quality/evidence/client-release-20261031/native-approved-" + expectedWidth + "-" + host;
for (const state of states) {
  for (const extension of ["png", "json"]) {
    if (fs.existsSync(path.join(out, state + "-" + expectedWidth + "." + extension))) {
      throw Error("existing native evidence must not be overwritten: " + out);
    }
  }
}
const socket = new WebSocket("ws://127.0.0.1:" + port);
const pending = new Map();
let sequence = 0;
socket.onmessage = ({data}) => {
  const result = JSON.parse(data);
  pending.get(result.id)?.(result);
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, result => {
      clearTimeout(timer); pending.delete(id);
      result.error ? reject(Error(result.error.message)) : resolve(result.result);
    });
    socket.send(JSON.stringify({id, method, params}));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", {functionDeclaration, args})).result;
const selectors = [
  ".footprints-page", ".fp-tabs", ".fp-tab", ".fp-more", ".fp-drafts",
  ".fp-title", ".fp-empty", ".fp-import", ".fp-error", ".fp-manual",
  ".fp-text-button", ".fp-notice"
];
const fixture = `function(state){
  const current=getCurrentPages().slice(-1)[0],p=current.selectComponent?.('#travel-diary')||current;
  p.pausePlayback();if(p.pollTimer)clearTimeout(p.pollTimer);
  const photo={id:'synthetic-photo',version:1,state:'confirmed',is_manual:true,
    dateLabel:'2024-02-03',timeLabel:'时刻未知',placeLabel:'合成地点的较长名称用于窄屏换行验证'};
  const data={loading:false,error:'',importError:'',canWrite:true,child:{id:'synthetic',name:'合成孩子',active:true},
    childId:'synthetic',mode:'timeline',sheet:'',sheetError:'',saving:false,selecting:false,
    keyboardHeight:0,summary:{photos:0,places:0,cities:0,countries:0,drafts:0},
    visits:[],nextCursor:null,hasArchivedChildren:false};
  if(state==='drafts')data.summary.drafts=3;
  if(state==='legacy')data.visits=[{id:'synthetic-visit',local_date:'2024-02-03',
    place_name:photo.placeLabel,photo_count:1,photos:[photo]}];
  if(state==='loading')data.loading=true;
  if(state==='error')data.error='读取失败，请重新读取';
  if(state==='viewer')data.canWrite=false;
  if(state==='archived'){data.child.active=false;data.hasArchivedChildren=true;}
  p.applyGeometryFixture(JSON.stringify(data));
  return new Promise(resolve=>wx.nextTick(()=>resolve(true)));
}`;
async function capture(state) {
  await call(fixture, [state]);
  await call(`function(){return new Promise(resolve=>wx.pageScrollTo({scrollTop:0,duration:0,complete:()=>wx.nextTick(()=>resolve(true))}));}`);
  const before = await call(`function(){return new Promise(resolve=>{
    const current=getCurrentPages().slice(-1)[0],p=current.selectComponent?.('#travel-diary')||current,q=wx.createSelectorQuery().in(p);
    q.select('.fp-import').boundingClientRect();q.selectViewport().scrollOffset();
    q.exec(([r,v])=>resolve({button:r,scroll:v,window:wx.getSystemInfoSync().windowHeight}));
  });}`);
  if (before.button && before.button.bottom > before.window - 64) {
    await call(`function(scrollTop){return new Promise(resolve=>wx.pageScrollTo({scrollTop,duration:0,complete:()=>wx.nextTick(()=>resolve(true))}));}`,
      [before.scroll.scrollTop + before.button.bottom - before.window + 90]);
  }
  const data = await call(`function(selectors){return new Promise(resolve=>{
    const current=getCurrentPages().slice(-1)[0],p=current.selectComponent?.('#travel-diary')||current,q=wx.createSelectorQuery().in(p),i=wx.getSystemInfoSync();
    selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize']}));
    q.selectViewport().scrollOffset();
    q.exec(rows=>{const nodes={};selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(r=>r.width&&r.height));
      resolve({nodes,scroll:rows[selectors.length],viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion},
      sheet:p.data.sheet,canWrite:p.data.canWrite,active:p.data.child.active,
      manualEntryRemoved:typeof p.manualEntry==='undefined'});});
  });}`, [selectors]);
  const errors = [];
  const check = (value, message) => { if (!value) errors.push(message); };
  check(data.viewport.width === expectedWidth && data.viewport.screenHeight === expectedScreenHeight, "viewport mismatch");
  check(data.scroll.scrollLeft === 0, "root horizontal scroll");
  check(data.manualEntryRemoved, "manual creation method remains");
  for (const selector of [".fp-tab", ".fp-more", ".fp-drafts", ".fp-import", ".fp-text-button"]) {
    for (const r of data.nodes[selector]) {
      check(r.left >= -1 && r.right <= expectedWidth + 1, selector + " horizontal overflow");
      check(r.height >= 43 && r.width >= 43, selector + " target below 44px");
      if (r.fontSize && selector !== ".fp-more") check(parseFloat(r.fontSize) >= 14, selector + " font below 14px");
    }
  }
  const tabs = data.nodes[".fp-tab"];
  check(tabs.length === 3, "three tabs absent");
  if (tabs.length === 3) {
    check(Math.max(...tabs.map(r=>r.width))-Math.min(...tabs.map(r=>r.width))<=1, "unequal tabs");
    check(tabs[1].left >= tabs[0].right - 1 && tabs[2].left >= tabs[1].right - 1, "tabs overlap");
  }
  check(data.nodes[".fp-drafts"].length === (state === "drafts" ? 1 : 0), "draft CTA count mismatch");
  const importButton = data.nodes[".fp-import"][0];
  check(Boolean(importButton) === !["viewer", "archived"].includes(state), "import visibility mismatch");
  if (importButton) {
    check(importButton.height >= 47, "primary CTA below 48px");
    check(importButton.top >= -1 && importButton.bottom <= data.viewport.height-63, "import unreachable above tabbar");
  }
  if (state === "legacy") check(data.nodes[".fp-manual"].length === 1, "legacy manual record absent");
  const screenshot = await send("App.captureScreenshot");
  const bytes = Buffer.from((typeof screenshot === "string" ? screenshot : screenshot.data || screenshot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, {recursive:true});
  const name = state + "-" + expectedWidth;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({
    ...data, state, errors, capturedAt:new Date().toISOString(),
    screenshotSha256:crypto.createHash("sha256").update(bytes).digest("hex"),
    host,expectedViewport:{width:expectedWidth,screenHeight:expectedScreenHeight},
    scope:"native synthetic offline " + expectedWidth + "x" + expectedScreenHeight + " " + host + " current-production-wxml-wxss; not device or cloud acceptance",
    unchangedSegmentedTabs:{gapRequirement:"NOT_APPLICABLE_TO_CHANGED_ACTION_GROUP",
      reason:"Contiguous segmented control matches the unchanged approved baseline; this release removes entry controls and does not change tab geometry.",
      observedGaps:tabs.length===3?[tabs[1].left-tabs[0].right,tabs[2].left-tabs[1].right]:[]}
  }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS"));
  return errors.length;
}
async function main() {
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error("automation connection timeout")),15000);
    socket.onopen=()=>{clearTimeout(timer);resolve();};
    socket.onerror=()=>{clearTimeout(timer);reject(Error("automation connection unavailable"));};
  });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("offline copy required");
  const viewport = await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,screenHeight:i.screenHeight};}");
  if (viewport.width !== expectedWidth || viewport.screenHeight !== expectedScreenHeight) {
    throw Error("switch the native simulator to " + expectedWidth + "x" + expectedScreenHeight + " before collection");
  }
  if(host==="standalone"){
    await call("function(){return new Promise(resolve=>wx.navigateTo({url:'/pages/footprints/index?child_id=synthetic',success:()=>resolve(true)}));}");
  }else{
    await call("function(){return new Promise(resolve=>wx.switchTab({url:'/pages/records/index',success:()=>resolve(true)}));}");
    await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}");
  }
  let failures = 0;
  for (const state of states) failures += await capture(state);
  socket.close(); process.exitCode = failures ? 1 : 0;
}
main().catch(error=>{console.error(error.message);socket.close();process.exitCode=1;});
