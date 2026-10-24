// Native offline-copy acceptance: production handlers, local synthetic transport, no writes.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { STATES, FIXTURE } = require("./footprints_geometry");
const width = Number(process.argv[2]), port = Number(process.argv[3]);
const out = path.resolve("docs/quality/evidence/record-types-20261023/native");
const selectors = [".record-heading", ".record-type-title", ".record-child", ".record-type-sheet",
  ".record-type-close", ".record-type-choice", ".record-type-head", ".record-cta"];
const domainSelectors = [".footprints-page", ".fp-tab", ".fp-date", ".fp-button", ".fp-text-button",
  ".fp-close", ".fp-select", ".fp-drafts", ".fp-input", ".fp-candidate", ".fp-sheet",
  ".fp-sheet-head", ".fp-sheet-body", ".fp-sheet-footer", ".fp-draft", ".fp-title", ".fp-muted",
  ".fp-scope .fp-text-button", ".fp-two-fields .fp-input", ".fp-sheet-footer .fp-full", ".fp-check-label"];
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = (event) => { const m = JSON.parse(event.data); const resolve = pending.get(m.id); if (resolve) { pending.delete(m.id); resolve(m); } };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, (m) => { clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const delay = () => new Promise((resolve) => setTimeout(resolve, 150));
async function capture(state) {
  const data = await call(`function(rootSelectors,domainSelectors){return new Promise(resolve=>{
    const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary');
    const nodes={},i=wx.getSystemInfoSync();let left=0;
    function read(target,selectors){return new Promise(done=>{const q=wx.createSelectorQuery().in(target);
      selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize']}));
      q.selectViewport().scrollOffset();q.exec(rows=>{selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize})));left=Math.max(left,(rows[selectors.length]||{}).scrollLeft||0);done();});});}
    read(p,rootSelectors).then(()=>c?read(c,domainSelectors):null).then(()=>read(p.getTabBar(),['.tabbar'])).then(()=>resolve({nodes,scrollLeft:left,
      viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting},
      recordType:p.data.recordType,overlayOpen:p.data.recordTypeOpen||Boolean(c&&c.data.sheet),childId:c?c.data.childId:p.data.childId}));
  });}`, [selectors, domainSelectors]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); };
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "wrong viewport");
  check(data.scrollLeft === 0, "horizontal root scrolling");
  const targets = new Set([...selectors.filter((s) => ![".record-heading", ".record-type-sheet", ".record-type-head", ".record-cta"].includes(s)),
    ...domainSelectors.filter((s) => ![".footprints-page", ".fp-sheet", ".fp-sheet-head", ".fp-sheet-body", ".fp-sheet-footer", ".fp-draft", ".fp-title", ".fp-muted", ".fp-check-label"].includes(s))]);
  for (const [selector, rects] of Object.entries(data.nodes)) for (const r of rects) {
    check(r.left >= -1 && r.right <= width + 1, selector + " outside viewport");
    if (targets.has(selector)) check(r.width >= 43 && r.height >= 43, selector + " below 44px");
    if (r.fontSize) check(parseFloat(r.fontSize) >= 14, selector + " below 14px text");
  }
  for (const selector of [".record-type-sheet", ".record-type-close", ".record-type-choice", ".fp-sheet-footer", ".record-cta"]) {
    for (const r of data.nodes[selector] || []) check(r.top >= -1 && r.bottom <= data.viewport.height + 1, selector + " hidden action");
  }
  const title = data.nodes[".record-type-title"]?.[0], child = data.nodes[".record-child"]?.[0];
  if (title && child) check(child.left - title.right >= 7, "title/child overlap or missing gap");
  for (const selector of [".fp-tab", ".fp-scope .fp-text-button", ".fp-two-fields .fp-input"]) {
    const rows = data.nodes[selector] || [];
    if (rows.length > 1) check(Math.max(...rows.map((r) => r.width)) - Math.min(...rows.map((r) => r.width)) <= 1, selector + " unequal columns");
    rows.slice(1).forEach((r, n) => check(r.left - rows[n].right >= 7, selector + " gap"));
  }
  const close = data.nodes[".record-type-close"]?.[0];
  if (close) {
    check(Math.abs(close.width - 44) <= 1 && Math.abs(close.height - 44) <= 1, "close geometry");
    check(Math.abs(close.right - (width - 16)) <= 1, "close alignment");
  }
  const choices = data.nodes[".record-type-choice"] || [];
  choices.forEach((r, index) => {
    check(Math.abs(r.width - (width - 32)) <= 1 && Math.abs(r.left - 16) <= 1, "choice full width");
    if (index) check(r.top - choices[index - 1].bottom >= 7, "choice gap");
  });
  if (state.includes("picker")) check(data.nodes[".record-type-choice"]?.length === 2, "two record types missing");
  if (data.recordType === "travel") check(data.nodes[".fp-tab"]?.length === 3, "three views missing");
  check((data.nodes[".tabbar"] || []).length === (data.overlayOpen ? 0 : 1), "tab bar occlusion or missing restoration");
  let shot;
  try { shot = await send("App.captureScreenshot"); } catch { shot = await send("App.captureScreenshot"); }
  const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, `${state}-${width}.png`), bytes);
  fs.writeFileSync(path.join(out, `${state}-${width}.json`), JSON.stringify({ ...data, state, errors,
    capturedAt: new Date().toISOString(), screenshot: `${state}-${width}.png`,
    screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex"),
    screenshotPixels: { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) } }, null, 2) + "\n");
  console.log(state + "-" + width + ": " + (errors.join("; ") || "PASS"));
  return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  try {
    if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
    const current = await send("App.getCurrentPage");
    if (current.path !== "pages/records/index") throw Error("Open records tab first");
    let failures = 0;
    // Actual production switching methods exercise component mount + parent event bridge.
    await call("function(){const p=getCurrentPages().slice(-1)[0];p.applyGeometryFixture(JSON.stringify({recordType:'learning',recordTypeOpen:false,childId:'synthetic',text:'保留未提交内容',hasText:true,photos:['/assets/illustrations/record-camera.png']}));return true;}");
    await delay(); failures += await capture("learning");
    await call("function(){getCurrentPages().slice(-1)[0].openRecordTypes();return true;}");
    await delay(); failures += await capture("learning-picker");
    await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}");
    await delay(); failures += await capture("travel");
    await call("function(){getCurrentPages().slice(-1)[0].openRecordTypes();return true;}");
    await delay(); failures += await capture("travel-picker");
    await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'learning'}}}).then(()=>true);}");
    await delay();
    const preserved = await call("function(){const p=getCurrentPages().slice(-1)[0];return p.data.text==='保留未提交内容'&&p.data.photos.length===1&&p.data.childId==='synthetic';}");
    if (!preserved) throw Error("Native round-trip lost learning input");
    await call("function(){const p=getCurrentPages().slice(-1)[0];p.applyGeometryFixture(JSON.stringify({children:[{id:'synthetic',name:'合成孩子的长姓名用于窄屏验证'}]}));return true;}");
    await delay(); failures += await capture("long-child");
    await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}");
    await delay();
    const fixture = FIXTURE.replace("const p=getCurrentPages().slice(-1)[0];", "const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');");
    for (const state of STATES) {
      await call(fixture, [state]);
      await call("function(){wx.pageScrollTo({scrollTop:0,duration:0});return true;}");
      if (state === "candidates") {
        await call(`function(){return new Promise(resolve=>{const c=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');const q=wx.createSelectorQuery().in(c);q.select('.fp-candidate').boundingClientRect();q.select('.fp-sheet-body').boundingClientRect();q.exec(rows=>{c.applyGeometryFixture(JSON.stringify({geometryScrollTop:Math.max(0,rows[0].top-rows[1].top-8)}));resolve(true);});});}`);
      }
      await delay(); failures += await capture(state);
    }
    if (failures) throw Error(`${failures} native captures failed`);
  } finally { socket.close(); }
}
main().catch((error) => { console.error(error.message); process.exitCode = 1; socket.close(); });
