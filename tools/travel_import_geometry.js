// Approved import simplification: native node geometry, offline synthetic copy only.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9586);
const out = path.resolve("docs/quality/evidence/travel-import-simplification-20261025/native");
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = ({ data }) => { const m = JSON.parse(data); pending.get(m.id)?.(m); };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, m => { pending.delete(id); clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const selectors = [".fp-sheet", ".fp-sheet-head", ".fp-sheet-head .fp-place-title", ".fp-sheet-body", ".fp-sheet-footer", ".fp-sheet-footer .fp-button", ".fp-sheet-footer .fp-text-button", ".fp-close", ".fp-text-button", ".fp-tab", ".fp-import", ".fp-switch", ".fp-upload-progress", ".fp-error"];
const fixture = `function(state){const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');p.pausePlayback();if(p.pollTimer)clearTimeout(p.pollTimer);
  p.pendingFiles=null;p.uploading=false;
  const data={loading:false,error:'',importError:'',canWrite:true,child:{id:'synthetic',name:'合成孩子',active:true},childId:'synthetic',mode:'timeline',sheet:'',sheetError:'',saving:false,selecting:false,keyboardHeight:0,aiEnabled:false,hasPendingUpload:false,importCompleted:2,importCount:3,importProgress:67,summary:{photos:0,places:0,cities:0,countries:0},visits:[]};
  if(state==='selecting')data.selecting=true;
  if(state==='uploading'){data.sheet='uploading';data.saving=true;}
  if(state==='upload-error'){data.sheet='upload-error';data.sheetError='第3张上传失败，请重试';data.hasPendingUpload=true;}
  if(state==='settings')data.sheet='settings';
  p.applyGeometryFixture(JSON.stringify(data));return true;}`;
async function capture(state) {
  await call(fixture, [state]);
  await new Promise(resolve => setTimeout(resolve, 120));
  if (["entry", "selecting"].includes(state)) await call(`function(){return new Promise(resolve=>{const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary'),q=wx.createSelectorQuery().in(p);q.select('.fp-import').boundingClientRect();q.selectViewport().scrollOffset();q.exec(([r,v])=>wx.pageScrollTo({scrollTop:Math.max(0,v.scrollTop+r.bottom-wx.getSystemInfoSync().windowHeight+90),duration:0,complete:()=>resolve(true)}));});}`);
  const data = await call(`function(selectors){return new Promise(resolve=>{const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary'),q=wx.createSelectorQuery().in(p),i=wx.getSystemInfoSync();selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize']}));q.selectViewport().scrollOffset();q.exec(rows=>{const nodes={};selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(r=>r.width&&r.height));resolve({nodes,scrollLeft:rows[selectors.length]?.scrollLeft||0,viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion},sheet:p.data.sheet,selecting:p.data.selecting});});});}`, [selectors]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); };
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport mismatch");
  check(data.scrollLeft === 0, "horizontal root scroll");
  for (const [selector, rows] of Object.entries(data.nodes)) for (const r of rows) {
    check(r.left >= -1 && r.right <= width + 1, selector + " horizontal overflow");
    if ([".fp-close", ".fp-text-button", ".fp-tab", ".fp-import", ".fp-switch", ".fp-sheet-footer .fp-button"].includes(selector)) check(r.width >= 43 && r.height >= 43, selector + " target below 44px");
    if (r.fontSize && selector !== ".fp-close") check(parseFloat(r.fontSize) >= 14, selector + " font below 14px");
  }
  const sheet = data.nodes[".fp-sheet"][0], footer = data.nodes[".fp-sheet-footer"][0], close = data.nodes[".fp-close"][0], title = data.nodes[".fp-sheet-head .fp-place-title"][0];
  if (sheet) {
    check(sheet.top >= -1 && footer.bottom <= data.viewport.height + 1, "sheet actions outside window");
    check(title.right <= close.left - 7, "sheet title overlaps close");
    check(data.nodes[".fp-sheet-body"][0].height >= 44, "body too short");
    for (const r of data.nodes[".fp-sheet-footer .fp-text-button"]) check(r.top >= footer.top, "footer action outside footer");
  } else {
    const button = data.nodes[".fp-import"][0];
    check(button.top >= -1 && button.bottom <= data.viewport.height - 64, "import unreachable above tabbar");
  }
  for (const r of data.nodes[".fp-sheet-footer .fp-button"]) check(r.height >= 47 && parseFloat(r.fontSize) >= 16, "primary dimensions");
  const shot = await send("App.captureScreenshot"), bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true }); const name = `${state}-${width}`;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({ ...data, state, errors, capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS")); return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  await call("function(){return new Promise(resolve=>wx.switchTab({url:'/pages/records/index',success:()=>resolve(true)}));}");
  await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}");
  let failures = 0;
  for (const state of ["entry", "selecting", "uploading", "upload-error", "settings"]) failures += await capture(state);
  socket.close(); process.exitCode = failures ? 1 : 0;
}
main().catch(error => { console.error(error.message); socket.close(); process.exitCode = 1; });
