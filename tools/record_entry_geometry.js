// BUG-032: native node evidence against the approved offline copy; no business writes.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { FIXTURE } = require("./footprints_geometry");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9560);
const out = path.resolve("docs/quality/evidence/record-entry-20261024/native");
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
const rootSelectors = [".record-heading", ".record-type-title", ".child-chip", ".ava", ".record-child-name", ".child-chip .chev", ".record-type-menu", ".record-type-choice", ".record-type-dismiss"];
const domainSelectors = [".footprints-page", ".fp-tab", ".fp-filter", ".fp-date", ".fp-timeline", ".fp-map-content", ".fp-import", ".fp-import .ico", ".fp-import text", ".fp-empty", ".fp-player", ".fp-map", ".fp-world-row", ".fp-sheet", ".fp-sheet-body", ".fp-sheet-footer", ".fp-text-button", ".fp-button"];
async function capture(state) {
  await settle();
  const data = await call(`function(rootSelectors,domainSelectors){return new Promise(resolve=>{
    const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary'),nodes={},i=wx.getSystemInfoSync();let scrollLeft=0,scrollTop=0;
    function read(target,selectors){return new Promise(done=>{const q=wx.createSelectorQuery().in(target);
      selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize','backgroundColor','position','overflowX','overflowY']}));
      q.selectViewport().scrollOffset();q.exec(rows=>{selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize,backgroundColor:n.backgroundColor,position:n.position,overflowX:n.overflowX,overflowY:n.overflowY})));const v=rows[selectors.length]||{};scrollLeft=Math.max(scrollLeft,v.scrollLeft||0);scrollTop=Math.max(scrollTop,v.scrollTop||0);done();});});}
    read(p,rootSelectors).then(()=>c?read(c,domainSelectors):null).then(()=>read(p.getTabBar(),['.tabbar','.is-center .key'])).then(()=>resolve({nodes,scrollLeft,scrollTop,
      viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting},
      recordType:p.data.recordType,menu:p.data.recordTypeOpen,sheet:Boolean(c&&c.data.sheet),counts:c?{visits:c.data.visits.length,placeVisits:c.data.placeVisits.length}:null}));
  });}`, [rootSelectors, domainSelectors]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); };
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport mismatch");
  check(data.scrollLeft === 0, "horizontal root scroll");
  const targets = new Set([".record-type-title", ".child-chip", ".record-type-choice", ".fp-tab", ".fp-import", ".fp-text-button", ".fp-button", ".fp-world-row"]);
  for (const [selector, rects] of Object.entries(data.nodes)) for (const r of rects) {
    check(r.left >= -1 && r.right <= width + 1, selector + " horizontal overflow");
    if (targets.has(selector)) check(r.width >= 43 && r.height >= 43, selector + " target below 44px");
    if (![".is-center .key", ".tabbar", ".child-chip .chev", ".record-type-dismiss"].includes(selector) && r.fontSize)
      check(parseFloat(r.fontSize) >= 14, selector + " text below 14px");
  }
  const first = (s) => data.nodes[s]?.[0], title = first(".record-type-title"), child = first(".child-chip"), menu = first(".record-type-menu");
  if (title && child) check(child.left >= title.right + 7 || child.top >= title.bottom + 7, "title and child overlap");
  if (state.startsWith("long")) check(child && child.top >= title.bottom + 7 && Math.abs(child.right - (width - 16)) <= 1, "long child must wrap as a whole and align right");
  if (state === "single") check(!first(".child-chip .chev"), "single child arrow visible");
  if (data.menu) {
    check(first('.record-heading')?.overflowX === 'visible' && first('.record-heading')?.overflowY === 'visible', 'header clips dropdown');
    check(menu && Math.abs(menu.left - title.left) <= 1 && Math.abs(menu.top - title.bottom - 8) <= 1 && Math.abs(menu.width - 200) <= 1, "menu anchor geometry");
    check(data.nodes[".record-type-choice"]?.length === 2, "menu choices missing");
    (data.nodes[".record-type-choice"] || []).forEach((r) => check(r.height >= 47 && r.top >= menu.top && r.bottom <= menu.bottom, "menu item containment/48px"));
    check(first(".record-type-dismiss")?.backgroundColor === "rgba(0, 0, 0, 0)", "dismiss layer darkens page");
  }
  if (data.recordType === "travel") {
    check(!first(".fp-filter") && !first(".fp-date"), "date filter still rendered");
    check(data.nodes[".fp-tab"]?.length === (state === "no-child" ? 0 : 3), "view tabs mismatch");
    const button = first(".fp-import"), icon = first(".fp-import .ico");
    check(Boolean(button) === !["viewer", "archived", "no-child"].includes(state), "import permission/unique entry");
    check((data.nodes[".fp-import"] || []).length <= 1, "duplicate import entry");
    if (button) {
      check(Math.abs(button.height - 48) <= 1 && Math.abs(button.width - (width - (width <= 340 ? 24 : 32))) <= 1, "48px full-width import");
      check(button.position !== "fixed" && button.position !== "sticky", "import button floats");
      check(icon && Math.abs(icon.width - 20) <= 1 && Math.abs(icon.height - 20) <= 1, "import icon size");
    }
    if (state.includes("bottom")) {
      const content = first(state.startsWith("playback") || state.startsWith("lit") ? ".fp-map-content" : ".fp-timeline");
      const navTop = Math.min(first(".tabbar")?.top ?? Infinity, first(".is-center .key")?.top ?? Infinity);
      check(button && button.top >= 0 && navTop - button.bottom >= 7, "import button occluded by navigation");
      if (content) check(Math.abs(button.top - content.bottom - 20) <= 1, "import content gap");
    }
  }
  check((data.nodes[".tabbar"] || []).length === (data.sheet ? 0 : 1), "tab bar visibility");
  if (state === "timeline-window") check(data.counts.visits === 20 && Math.abs(first(".fp-timeline").top) <= 1, "next timeline window did not return to its start");
  if (state === "place-window") {
    const body = first(".fp-sheet-body"), row = first(".fp-world-row");
    check(data.counts.placeVisits === 20 && row && Math.abs(row.top - body.top - 16) <= 1, "next place window did not return to its start");
  }
  const shot = await send("App.captureScreenshot");
  const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true });
  const name = `${state}-${width}`;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({ ...data, state, errors, capturedAt: new Date().toISOString(), screenshot: name + ".png", screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS"));
  return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  const viewport = await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.screenHeight};}");
  if (viewport.width !== width || viewport.height !== { 320: 568, 390: 844, 430: 932 }[width])
    throw Error(`Select ${width}px device first; actual ${viewport.width}x${viewport.height}`);
  let failures = 0;
  await call(`function(){wx.switchTab({url:'/pages/records/index'});return true;}`); await settle();
  for (const state of ["learning", "learning-menu", "single", "long", "long-menu"]) {
    await call(`function(state){const p=getCurrentPages().slice(-1)[0];const child={id:'synthetic',name:state.startsWith('long')?'合成孩子的非常长姓名用于验证整块换行与完整显示':'合成孩子',avatar:'合'};p.applyGeometryFixture(JSON.stringify({recordType:'learning',recordTypeOpen:false,children:state==='single'?[child]:[child,{id:'second',name:'合成二',avatar:'合'}],childIndex:0}));if(state.endsWith('menu'))p.openRecordTypes();wx.pageScrollTo({scrollTop:0,duration:0});return true;}`, [state]);
    failures += await capture(state);
  }
  await call(`function(){const p=getCurrentPages().slice(-1)[0];p.closeRecordTypes();return p.selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}`); await settle();
  const fixture = FIXTURE.replace("const p=getCurrentPages().slice(-1)[0];", "const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');");
  for (const [state, base] of [["travel", "timeline"], ["travel-menu", "timeline"], ["empty-bottom", "empty"], ["timeline-bottom", "timeline"], ["playback-bottom", "playback"], ["lit-bottom", "lit"], ["viewer", "viewer"], ["archived", "archived"], ["no-child", "empty"], ["photo-sheet", "photo"]]) {
    await call("function(){getCurrentPages().slice(-1)[0].closeRecordTypes();return true;}");
    await call(fixture, [base]);
    await call(`function(state){const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary');if(state==='no-child')c.applyGeometryFixture(JSON.stringify({childId:'',child:null}));if(state==='travel-menu')p.openRecordTypes();wx.pageScrollTo({scrollTop:state.includes('bottom')?100000:0,duration:0});return true;}`, [state]);
    failures += await capture(state);
  }
  // Use production continuation handlers against read-only synthetic transport.
  await call(fixture, ["timeline"]);
  await call(`function(){const c=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');c.applyGeometryFixture(JSON.stringify({visits:Array.from({length:100},(_,i)=>({id:'window-'+i,local_date:'2024-02-03',photo_count:1,photos:[]})),nextCursor:'synthetic-next'}));wx.pageScrollTo({scrollTop:100000,duration:0});return true;}`); await settle();
  await call(`function(){return getCurrentPages().slice(-1)[0].selectComponent('#travel-diary').moreVisits().then(()=>true);}`); failures += await capture("timeline-window");
  await call(fixture, ["place"]);
  await call(`function(){const c=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');c.applyGeometryFixture(JSON.stringify({placeVisits:Array.from({length:100},(_,i)=>({id:'window-'+i,local_date:'2024-02-03',photo_count:1})),placeKey:'synthetic',placeCursor:'synthetic-next',geometryScrollTop:100000}));return true;}`); await settle();
  await call(`function(){return getCurrentPages().slice(-1)[0].selectComponent('#travel-diary').morePlaceVisits().then(()=>true);}`); failures += await capture("place-window");
  if (failures) throw Error(`${failures} native assertions failed`);
}
main().catch((error) => { console.error(error.message); process.exitCode = 1; }).finally(() => socket.close());
