// Real child-edit WXML/WXSS in the existing write-rejecting synthetic fixture.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const width = Number(process.argv[2]);
const mode = process.argv[3] || "matrix";
const out = path.join(__dirname, "native", String(width));
const selectors = [".page", ".archive-card", ".archive-row", ".archive-copy",
  ".archive-title", ".archive-description", ".archive-pending", ".archive-row .chev",
  ".form-foot .btn", ".pk-notice.err"];
if (![320, 390, 430].includes(width)) throw Error("width must be 320, 390 or 430");
const socket = new WebSocket("ws://127.0.0.1:9612"), pending = new Map();
let sequence = 0;
socket.onmessage = ({ data }) => {
  const message = JSON.parse(data);
  pending.get(message.id)?.(message);
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timed out")); }, 12000);
    pending.set(id, message => {
      clearTimeout(timer); pending.delete(id);
      message.error ? reject(Error(JSON.stringify(message.error))) : resolve(message.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) =>
  (await send("App.callFunction", { functionDeclaration, args })).result;
const fixture = `function(state){
  const p=getCurrentPages().slice(-1)[0];
  const active=!['archived','restoring'].includes(state);
  const unfinished=['unfinished','confirm-unfinished','working'].includes(state);
  p.applyGeometryFixture(JSON.stringify({mode:'edit',childId:'synthetic',loading:false,
    active,isManager:state!=='editor',nameDraft:'合成孩子',saving:false,
    working:['working','restoring'].includes(state),
    unfinishedCount:unfinished?3:0,
    unfinishedHint:unfinished?'还有 3 条记录待处理，归档后仍可继续完成。':'',
    error:state==='error'?'合成错误：暂时无法归档，请稍后重试。':''}));
  return new Promise(resolve=>wx.nextTick(()=>resolve(true)));
}`;
const query = `function(selectors){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);
  selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,
    computedStyle:['fontSize','lineHeight','textAlign','color','backgroundColor','overflow']}));
  q.selectViewport().scrollOffset();q.exec(rows=>{
    const nodes={};selectors.forEach((s,i)=>nodes[s]=rows[i]||[]);
    const i=wx.getSystemInfoSync();resolve({nodes,scroll:rows[selectors.length],
      viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,
        dpr:i.pixelRatio,fontScale:i.fontSizeSetting,baseLibrary:i.SDKVersion},
      data:{active:p.data.active,working:p.data.working,isManager:p.data.isManager,
        nameDraft:p.data.nameDraft,unfinishedCount:p.data.unfinishedCount,error:p.data.error}});
  });
});}`;
async function capture(state) {
  const payload = await call(query, [selectors]), errors = [];
  const check = (ok, reason) => { if (!ok) errors.push(reason); };
  check(payload.viewport.width === width && payload.viewport.screenHeight === {320:568,390:844,430:932}[width], "wrong viewport");
  const n = payload.nodes;
  check(n[".archive-row"].length === (state === "editor" ? 0 : 1), "action row count");
  for (const r of n[".archive-row"]) check(r.height >= 44, "action target below 44px");
  for (const s of [".archive-title", ".archive-description", ".archive-pending"]) {
    for (const r of n[s]) {
      check(parseFloat(r.fontSize) >= 14, s + " font below 14px");
      check(r.textAlign === "left", s + " not left aligned");
    }
  }
  for (const s of selectors.slice(1)) for (const r of n[s]) {
    check(r.left >= -1 && r.right <= width + 1, s + " horizontal overflow");
  }
  check(n[".archive-pending"].length === (["unfinished","working","confirm-unfinished"].includes(state) ? 1 : 0), "pending state");
  check(n[".archive-row .chev"].length === (["working","restoring","editor"].includes(state) ? 0 : 1), "chevron state");
  fs.mkdirSync(out, {recursive:true});
  let screenshotSha256=null;
  if(!process.env.NATIVE_SKIP_SCREENSHOTS) {
    const shot = await send("App.captureScreenshot");
    const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
    fs.writeFileSync(path.join(out, state + ".png"), bytes);
    screenshotSha256=crypto.createHash("sha256").update(bytes).digest("hex");
  }
  fs.writeFileSync(path.join(out, state + ".json"), JSON.stringify({...payload, state, errors,
    capturedAt:new Date().toISOString(), screenshotSha256,
    screenshotStatus:screenshotSha256?"CAPTURED":"NOT_RUN_AFTER_RPC_TIMEOUT",
    scope:"offline synthetic fixture; production WXML/WXSS; no physical device or cloud acceptance"}, null, 2) + "\n");
  console.log(width + " " + state + ": " + (errors.join("; ") || "PASS"));
  return errors.length;
}
async function main() {
  await new Promise((resolve,reject) => {
    const timer=setTimeout(()=>reject(Error("automation handshake timeout")),12000);
    socket.onopen=()=>{clearTimeout(timer);resolve();};
    socket.onerror=()=>{clearTimeout(timer);reject(Error("automation unavailable"));};
  });
  const safe=await call(`function(){const a=getApp(),i=wx.getSystemInfoSync();return {
    offline:a.globalData.useCloud===false,synthetic:a.globalData.familyId==='synthetic',
    fixture:typeof a.startGradeInteractionFixture==='function',width:i.windowWidth,screenHeight:i.screenHeight};}`);
  if(!safe.offline||!safe.synthetic||!safe.fixture||safe.width!==width||safe.screenHeight!=={320:568,390:844,430:932}[width])
    throw Error("offline/viewport precondition: " + JSON.stringify(safe));
  const route=await call("function(){return getCurrentPages().slice(-1)[0].route;}");
  if(route!=="pages/child-edit/index") {
    await call(`function(){wx.navigateTo({url:'/pages/child-edit/index?mode=edit&child_id=synthetic'});return true;}`);
    console.log("Navigation scheduled; rerun after the native page is ready.");
    return;
  }
  if(mode.startsWith("confirm")) {
    await call(fixture,[mode]);
    await call("function(){getCurrentPages().slice(-1)[0].archive();return true;}");
    await capture(mode);
    return;
  }
  let failures=0;
  for(const state of ["active","unfinished","archived","working","restoring","error","editor"]) {
    await call(fixture,[state]);
    await call(`function(){return new Promise(resolve=>{
      const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);
      q.select('.archive-card').boundingClientRect();q.selectViewport().scrollOffset();
      q.exec(([r,s])=>wx.pageScrollTo({scrollTop:r?Math.max(0,s.scrollTop+r.top-130):0,duration:0,
        complete:()=>wx.nextTick(()=>resolve(true))}));
    });}`);
    failures+=await capture(state);
  }
  if(failures) process.exitCode=1;
}
main().catch(error=>{console.error(error.message);process.exitCode=1;}).finally(()=>socket.close());
