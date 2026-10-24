// Native geometry from production WXML/WXSS in an offline synthetic copy.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { FIXTURE } = require("./footprints_geometry");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9572);
const out = path.resolve("docs/quality/evidence/footprints-minimal-20261024/native");
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
const selectors = [".footprints-page", ".fp-toolbar", ".fp-heading", ".fp-archive", ".fp-summary", ".fp-stats", ".fp-stats text", ".fp-more", ".fp-more .ico", ".fp-tabs", ".fp-tab", ".fp-import", ".fp-settings", ".fp-sheet", ".fp-sheet-head", ".fp-sheet-body", ".fp-sheet-footer", ".fp-switch", ".fp-switch-label", ".fp-close", ".fp-text-button", ".fp-button", ".fp-error"];
async function capture(state) {
  await settle();
  const data = await call(`function(selectors){return new Promise(resolve=>{
    const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary'),nodes={},i=wx.getSystemInfoSync();
    const q=wx.createSelectorQuery().in(c); selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize','position']}));
    q.selectViewport().scrollOffset(); q.exec(rows=>{selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize,position:n.position})));
    const tab=p.getTabBar();const tq=wx.createSelectorQuery().in(tab);tq.selectAll('.tabbar').boundingClientRect();tq.exec(t=>resolve({nodes,nav:t[0]||[],scrollLeft:(rows[selectors.length]||{}).scrollLeft||0,sheet:c.data.sheet,
      viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting}}));});});}`, [selectors]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); }, first = (s) => data.nodes[s]?.[0];
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport mismatch");
  check(data.scrollLeft === 0, "root horizontal scroll");
  check(!first(".fp-heading") && !first(".fp-archive"), "redundant title/archive entry remains");
  for (const [s, rects] of Object.entries(data.nodes)) for (const r of rects) {
    check(r.left >= -1 && r.right <= width + 1, s + " overflows horizontally");
    if ([".fp-more", ".fp-tab", ".fp-import", ".fp-button", ".fp-close", ".fp-text-button"].includes(s)) check(r.width >= 43 && r.height >= 43, s + " target below 44px");
    if (r.fontSize && ![".fp-close", ".fp-more .ico"].includes(s)) check(parseFloat(r.fontSize) >= 14, s + " text below 14px");
  }
  const more = first(".fp-more"), stats = first(".fp-stats");
  check(Boolean(more) === !["viewer", "no-child"].includes(state), "more availability mismatch");
  if (more) { check(Math.abs(more.width - 44) <= 1 && Math.abs(more.height - 44) <= 1, "more must be 44x44"); check(stats && more.left >= stats.right + 7, "statistics/more spacing"); }
  if (state.startsWith("settings")) {
    const sheet = first(".fp-settings"), body = first(".fp-sheet-body"), footer = first(".fp-sheet-footer"), row = first(".fp-switch");
    check(sheet && body && footer && row, "settings structure missing");
    if (sheet && footer) { check(sheet.top >= 0 && sheet.bottom <= data.viewport.height + 1, "settings outside viewport"); check(footer.bottom <= sheet.bottom + 1, "settings footer outside sheet"); }
    if (state === "settings") check(sheet && sheet.height <= 280 && body.height <= 120, "settings retains empty 52vh body");
    check(data.nav.length === 0, "tab bar under settings");
  } else check(data.nav.length === 1, "missing tab bar");
  const shot = await send("App.captureScreenshot"), bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true }); const name = `${state}-${width}`;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({ ...data, state, errors, capturedAt: new Date().toISOString(), screenshot: name + ".png", screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS")); return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  const viewport = await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.screenHeight};}");
  if (viewport.width !== width || viewport.height !== { 320: 568, 390: 844, 430: 932 }[width]) throw Error("Select expected device first: " + JSON.stringify(viewport));
  await call("function(){wx.switchTab({url:'/pages/records/index'});return true;}"); await settle();
  await call("function(){const p=getCurrentPages().slice(-1)[0];return p.selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}"); await settle();
  const fixture = FIXTURE.replace("const p=getCurrentPages().slice(-1)[0];", "const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');");
  let failures = 0;
  for (const [state, base] of [["overview", "timeline"], ["empty", "empty"], ["settings", "ai-settings"], ["settings-error", "ai-settings"], ["archived", "archived"], ["viewer", "viewer"], ["viewer-archive", "viewer"], ["long", "long-content"], ["no-child", "empty"]]) {
    await call(fixture, [base]);
    await call(`function(state){const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary');c.applyGeometryFixture(JSON.stringify({hasArchivedChildren:state==='viewer-archive',sheetError:state==='settings-error'?'网络不可用，请重试':''}));if(state==='no-child')c.applyGeometryFixture(JSON.stringify({childId:'',child:null}));wx.pageScrollTo({scrollTop:0,duration:0});return true;}`, [state]);
    failures += await capture(state);
  }
  socket.close(); process.exitCode = failures ? 1 : 0;
}
if (require.main === module) main().catch((error) => { console.error(error.message); socket.close(); process.exitCode = 1; });
