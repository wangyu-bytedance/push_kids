#!/usr/bin/env node
// Synthetic presentation fixtures only; output contains rectangles and booleans, never family data.
const fs = require("node:fs");
const path = require("node:path");

const SELECTORS = [".pk-hero", ".record-intro-copy, .calendar-intro-copy", ".pg-title", ".child-chip",
  ".record-intro-art, .calendar-intro-art", ".add-photo-tile", ".record-upload-art", ".add-photo-tile > text",
  ".week", ".wd", ".wk-nav", ".wk-nav .icon-btn", ".time-card", ".voice-input-shell", ".pcell", ".pk-notice"];

function audit(payload) {
  const errors = [];
  const check = (condition, message) => { if (!condition) errors.push(message); };
  const { nodes = {}, viewport = {}, expectedWidth, state, surface } = payload;
  check(Math.abs(viewport.width - expectedWidth) <= 1, "native viewport width mismatch");
  check(viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[expectedWidth], "native viewport height mismatch");
  check(Math.abs(payload.scrollLeft || 0) <= 1, "root scrolls horizontally");
  for (const [selector, rects] of Object.entries(nodes)) {
    for (const r of rects) check(r.left >= -1 && r.right <= expectedWidth + 1, `${selector} outside viewport`);
  }
  const hero = nodes[SELECTORS[0]]?.[0], copy = nodes[SELECTORS[1]]?.[0], title = nodes[SELECTORS[2]]?.[0];
  const chip = nodes[SELECTORS[3]]?.[0], art = nodes[SELECTORS[4]]?.[0];
  check(!!hero && !!copy && !!title && !!chip, "header contract missing");
  if (chip) {
    check(chip.width >= 44 && chip.height >= 43.99, "changed child selector below 44px");
    if (copy) check(chip.left >= copy.left - 1 && chip.right <= copy.right + 1, "child selector outside text column");
  }
  if (art && copy) check(copy.right + 4 <= art.left, "illustration overlaps header copy");
  if (hero && art) check(art.top >= hero.top - 1 && art.bottom <= hero.bottom + 1, "illustration outside card");
  check(!!art === (state !== "no-art"), "header image fallback mounting mismatch");
  if (surface === "records") {
    const tile = nodes[SELECTORS[5]]?.[0], upload = nodes[SELECTORS[6]]?.[0], labels = nodes[SELECTORS[7]] || [];
    const hasTile = state !== "photos" && state !== "readonly";
    check(!!tile === hasTile, "empty upload mounting mismatch");
    if (tile) check(tile.height >= 44 && tile.width >= 44, "upload target below 44px");
    check(!!upload === (hasTile && state !== "no-art"), "camera illustration fallback mounting mismatch");
    if (upload && labels[0]) check(upload.bottom <= labels[0].top + 1, "camera overlaps upload label");
    check((nodes[SELECTORS[14]]?.length || 0) === (state === "photos" ? 1 : 0), "photo grid mounting mismatch");
  } else {
    const week = nodes[SELECTORS[8]]?.[0], days = nodes[SELECTORS[9]] || [];
    check(days.length === 7 && !!week, "seven-day selector missing");
    for (const r of days) {
      if (week) check(r.left >= week.left - 1 && r.right <= week.right + 1, "day outside seven-day container");
      check(r.height >= 44, "existing day target height below 44px");
    }
    for (let i = 1; i < days.length; i += 1) {
      check(Math.abs(days[i].width - days[0].width) <= 1, "unequal day widths");
      check(days[i].left >= days[i - 1].right, "days overlap");
    }
    for (const r of nodes[SELECTORS[11]] || []) check(Math.abs(r.width - r.height) <= 1, "week navigation circle distorted");
    if (hero && week) check(hero.bottom <= week.top + 1, "header overlaps calendar");
  }
  return errors;
}

async function connect(endpoint) {
  const socket = new WebSocket(endpoint);
  const pending = new Map();
  let sequence = 0;
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    const callback = pending.get(message.id);
    if (callback) { pending.delete(message.id); callback(message); }
  };
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error(`${method} timed out`)); }, 15000);
    pending.set(id, message => { clearTimeout(timer); if (message.error) reject(Error(`${method} failed: ${JSON.stringify(message.error)}`)); else resolve(message.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
  return { socket, send };
}

const FIXTURE = `function(surface,state) {
  const p=getCurrentPages().slice(-1)[0];
  if (!p.__illustrationOriginal) p.__illustrationOriginal={data:JSON.parse(JSON.stringify(p.data)),load:p.load};
  p.loadGeneration=(p.loadGeneration||0)+1;
  p.loadId=(p.loadId||0)+1;
  if(p.timer) clearTimeout(p.timer);
  p.load=async function(){};
  const data={loading:false,error:state==='error'?'测试加载失败':'',children:[{id:'synthetic',name:state==='long-name'?'用于测试换行和截断的很长孩子名称':'示例孩子',avatar:'示',label:'示例孩子'}],childId:'synthetic',childIndex:0,multiChild:false,introArtFailed:state==='no-art',showChildSheet:false};
  if(surface==='records') Object.assign(data,{canWrite:state!=='readonly',photos:state==='photos'?['/assets/illustrations/record-camera.png']:[],date:'2026-10-13',dateLabel:'10月13日',time:'19:20',today:'2026-10-13',text:'',hasText:false,pendingCount:0,submittedId:'',timeOpen:false,backfill:false,saving:false,voiceState:'idle',voiceBusy:false,uploadArtFailed:state==='no-art'});
  else Object.assign(data,{selectedDay:'2026-10-13',monthLabel:'2026 年 10 月',weekKicker:'本周 · 10月12日 – 10月18日',dayTitle:'10月13日 · 星期二',weekEmpty:state==='empty',showEditor:false,conflictCount:0,week:['一','二','三','四','五','六','日'].map((weekday,i)=>({key:'2026-10-'+(12+i),day:12+i,weekday,marked:i===1,today:i===1,dim:false})),items:state==='empty'?[]:[{id:'synthetic-event',name:state==='long-name'?'用于检查长标题换行的课外活动安排名称':'示例活动',kind:'class',kind_label:'课外活动',start_time:'16:30',time_text:'16:30–17:30 · 每周重复',past:false,has_conflict:false,subject_id:'',action_text:'记录这次练习'}],itemCount:state==='empty'?0:1});
  return new Promise(resolve=>p.setData(data,()=>{wx.pageScrollTo({scrollTop:0,duration:0});resolve(true);}));
}`;

async function capture(surface, state, width, file, shot) {
  const { socket, send } = await connect(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420");
  try {
    const current = await send("App.getCurrentPage");
    if (current.path !== `pages/${surface}/index`) await send("App.callWxMethod", { method: "switchTab", args: [{ url: `/pages/${surface}/index` }] });
    await new Promise(resolve => setTimeout(resolve, 700));
    await send("App.callFunction", { functionDeclaration: FIXTURE, args: [surface, state] });
    await new Promise(resolve => setTimeout(resolve, 350));
    const result = await send("App.callFunction", { functionDeclaration: `function(selectors) {return new Promise(resolve=>{
      const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);
      selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true}));q.selectViewport().scrollOffset();
      q.exec(groups=>{const i=wx.getSystemInfoSync(),nodes={};selectors.forEach((s,k)=>nodes[s]=(groups[k]||[]).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height})));
        resolve({viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,fontScale:i.fontSizeSetting,baseLibrary:i.SDKVersion},nodes,scrollLeft:groups[selectors.length]?.scrollLeft||0});});});}`, args: [SELECTORS] });
    const payload = { ...result.result, surface, state, expectedWidth: width, fixture: "synthetic" };
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(payload, null, 2) + "\n");
    if (shot) {
      const screenshot = await send("App.screenshot");
      const data = screenshot.data || screenshot.base64;
      if (typeof data !== "string") throw Error(`screenshot keys: ${Object.keys(screenshot).join(",")}`);
      fs.writeFileSync(shot, Buffer.from(data.replace(/^data:image\/\w+;base64,/, ""), "base64"));
    }
    const errors = audit(payload);
    if (errors.length) throw Error(errors.join("; "));
    console.log(`ILLUSTRATION_GEOMETRY_VALID ${surface} ${state} ${width}px`);
  } finally {
    await send("App.callFunction", { functionDeclaration: "function(){const p=getCurrentPages().slice(-1)[0],o=p.__illustrationOriginal;if(o){p.load=o.load;p.setData(o.data);delete p.__illustrationOriginal;}return true;}", args: [] }).catch(() => {});
    socket.close();
  }
}

async function main() {
  const [mode, surface, state, width, file, shot] = process.argv.slice(2);
  if (mode === "audit") {
    for (const input of process.argv.slice(3)) {
      const errors = audit(JSON.parse(fs.readFileSync(input, "utf8")));
      if (errors.length) throw Error(`${input}: ${errors.join("; ")}`);
      console.log(`ILLUSTRATION_GEOMETRY_VALID ${input}`);
    }
  } else if (mode === "capture" && ["records", "calendar"].includes(surface) && file) {
    await capture(surface, state, Number(width), file, shot);
  } else throw Error("usage: capture <records|calendar> <state> <320|390|430> <numeric.json> [private-shot.png] | audit <json>...");
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { audit };
