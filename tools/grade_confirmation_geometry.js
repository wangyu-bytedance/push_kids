// DREV02 native presentation evidence in the offline copy; never writes business data.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const choices = require("../apps/miniprogram/utils/child-context").gradeChoices().filter((x) => x.value !== "其他");
const width = Number(process.argv[2]), port = Number(process.argv[3]);
const mode = process.argv[4] || "matrix";
const out = path.resolve("docs/quality/evidence/grade-dialog-simplification-20261024/native");
const selectors = [".grade-sheet", ".grade-body", ".grade-title", ".grade-latest",
  ".grade-picker", ".grade-error", ".grade-actions",
  ".grade-primary", ".grade-secondary"];
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = (event) => {
  const m = JSON.parse(event.data), handler = pending.get(m.id);
  if (handler) { pending.delete(m.id); handler(m); }
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => {
      pending.delete(id); reject(Error(`${method} timed out`));
    }, 15000);
    pending.set(id, (m) => {
      clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const fixture = `function(state,choices){
  const p=getCurrentPages().slice(-1)[0],a=getApp();a.gradeConfirmation=null;
  let v={id:'synthetic',name:'小满',schoolYearLabel:'2026—2027 学年',
    currentLabel:'二年级',selectedLabel:'三年级',reason:'annual_progression',status:'ready',
    choices,index:5,error:''};
  if(state==='initial'){v.reason='initial_check';v.selectedLabel='二年级';v.index=4;}
  if(state==='catchup')v.currentLabel='一年级';
  if(state==='corrected'||state==='error'){v.selectedLabel='四年级';v.index=6;}
  if(state==='keep'){v.selectedLabel='二年级';v.index=4;}
  if(state==='next-child'){v.name='合成豆豆';v.currentLabel='中班';v.selectedLabel='大班';v.index=2;}
  if(state==='long-name'){v.name='这是用于检查换行的合成长姓名小朋友';v.selectedLabel='九年级';v.index=11;}
  if(state==='saving')v.status='saving';
  if(state==='error')v.error='保存失败，请重试。';
  if(state==='conflict'){v.status='conflict';v.error='年级已变化，请查看最新结果。';}
  if(state==='latest'){v.status='latest';v.currentLabel='三年级';}
  if(['deferred','forbidden','archived','terminal','unknown','confirmed'].includes(state))v=null;
  p.applyGeometryFixture(JSON.stringify({loading:false,error:'',gradeConfirmation:v,
    gradeConfirmationVisible:!!v,showRenewalGuide:false}));
  p.getTabBar().setData({gradeConfirmationVisible:!!v});return true;
}`;
const query = `function(selectors){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#grade-confirmation'),nodes={};
  function read(owner,list){return new Promise(done=>{const q=wx.createSelectorQuery().in(owner);
    list.forEach(s=>q.selectAll(s).fields({rect:true,size:true,scrollOffset:true,computedStyle:['fontSize','lineHeight','color','backgroundColor','opacity']}));
    q.exec(rows=>{list.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height));done();});});}
  read(c,selectors).then(()=>read(p.getTabBar(),['.tabbar'])).then(()=>{const i=wx.getSystemInfoSync();
    resolve({nodes,viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,
      dpr:i.pixelRatio,fontScale:i.fontSizeSetting,baseLibrary:i.SDKVersion}});});});}`;
async function main() {
  if (![320, 390, 430].includes(width) || !port) throw Error("usage: <320|390|430> <automation-port>");
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(Error("automation handshake timed out")), 15000);
    socket.onopen = () => { clearTimeout(timer); resolve(); };
    socket.onerror = (error) => { clearTimeout(timer); reject(error); };
  });
  try {
    if (!await call("function(){const a=getApp();return a.globalData.useCloud===false&&a.globalData.familyId==='synthetic'&&typeof a.startGradeInteractionFixture==='function';}")) throw Error("isolated grade synthetic copy required");
    fs.mkdirSync(out, { recursive: true });
    const actual = await call("function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.screenHeight};}");
    if (actual.width !== width || actual.height !== { 320: 568, 390: 844, 430: 932 }[width]) throw Error(`wrong native viewport before capture: ${actual.width}x${actual.height}`);
    if (mode === "interaction-ready") {
      if (!await call("function(){getApp().startGradeInteractionFixture();return true;}")) throw Error("interaction fixture did not start");
      console.log("Production controller ready in write-rejecting synthetic copy");
      return;
    }
    if (["interaction-check", "interaction-dismissed"].includes(mode)) {
      const data = await call(query, [selectors]);
      const observed = await call("function(){const p=getCurrentPages().slice(-1)[0],v=p.data.gradeConfirmation;return {attempts:getApp().gradeFixtureAttempts(),visible:!!v,selected:v&&v.selectedLabel,error:v&&v.error};}");
      if (observed.attempts !== 2) throw Error("expected two rejected synthetic attempts");
      if (mode === "interaction-check" && (!observed.visible || observed.selected !== "四年级" || observed.error !== "保存失败，请重试。")) throw Error("retry did not preserve actual selection/error");
      if (mode === "interaction-dismissed" && (observed.visible || data.nodes[".grade-sheet"].length || data.nodes[".tabbar"].length !== 1)) throw Error("later did not dismiss/restore navigation");
      const shot = await send("App.captureScreenshot");
      const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
      const stem = path.join(out, `${mode}-${width}`);
      fs.writeFileSync(stem + ".png", bytes);
      fs.writeFileSync(stem + ".json", JSON.stringify({ ...data, observed, errors: [], state: mode,
        fixture: "actual picker/component/host/controller; offline transport rejects every write",
        capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
      console.log(`${mode}-${width}: PASS`);
      return;
    }
    if (["matrix", "picker-ready", "error-ready"].includes(mode)) {
      await call("function(){if(getCurrentPages().slice(-1)[0].route==='pages/today/index')return true;return new Promise(resolve=>wx.reLaunch({url:'/pages/today/index',success:()=>resolve(true)}));}");
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
    if (["picker-ready", "error-ready"].includes(mode)) {
      await call(fixture, [mode === "error-ready" ? "error" : "annual", choices]);
      console.log("Fixture ready for native interaction");
      return;
    }
    if (mode === "error-scrolled") {
      const data = await call(query, [selectors]), errors = [];
      const area = data.nodes[".grade-body"][0];
      if (!(area.scrollTop > 0)) errors.push("body did not scroll");
      if (data.viewport.width !== width) errors.push("wrong viewport");
      const shot = await send("App.captureScreenshot");
      const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
      const stem = path.join(out, `error-scrolled-${width}`);
      fs.writeFileSync(stem + ".png", bytes);
      fs.writeFileSync(stem + ".json", JSON.stringify({ ...data, errors,
        fixture: "offline synthetic after CUA scroll; readability reviewed in native window screenshot, no business write",
        capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
      if (errors.length) throw Error(errors.join("; "));
      console.log(`error-scrolled-${width}: PASS`);
      return;
    }
    if (mode === "profile-edit") {
      await call("function(){if(getCurrentPages().slice(-1)[0].route==='pages/child-edit/index')return true;return new Promise(resolve=>wx.navigateTo({url:'/pages/child-edit/index?mode=edit&child_id=synthetic',success:()=>resolve(true)}));}");
      await new Promise((resolve) => setTimeout(resolve, 250));
      await call("function(){const p=getCurrentPages().slice(-1)[0];p.chooseGrade({detail:{value:p.data.gradeChoices.findIndex(x=>x.value==='初中三年级')}});return true;}");
      // The native navigation bar reduces the captured webview on short devices.
      // Scroll the ordinary form so both its grade field and save action can be reviewed.
      await call("function(){return new Promise(resolve=>wx.pageScrollTo({scrollTop:120,duration:0,success:()=>resolve(true)}));}");
      await new Promise((resolve) => setTimeout(resolve, 150));
      const data = await call(`function(){return new Promise(resolve=>{
        const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);
        q.selectAll('.pk-picker,.form-foot .btn').fields({rect:true,size:true,computedStyle:['fontSize']});
        q.exec(rows=>{const i=wx.getSystemInfoSync();resolve({nodes:rows[0],
          viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,
          dpr:i.pixelRatio,baseLibrary:i.SDKVersion},route:p.route,
          selectedLabel:p.data.gradeChoices?.[p.data.gradeIndex]?.label});});});}`);
      const errors = [];
      if (data.viewport.width !== width) errors.push("wrong native viewport");
      if (data.selectedLabel !== "九年级") errors.push("ninth grade label mismatch");
      for (const r of data.nodes) {
        if (r.left < -1 || r.right > width + 1 || r.width < 43 || r.height < 43) errors.push("profile control geometry");
      }
      const shot = await send("App.captureScreenshot");
      const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
      const stem = path.join(out, `${mode}-${width}`);
      fs.writeFileSync(stem + ".png", bytes);
      fs.writeFileSync(stem + ".json", JSON.stringify({ ...data, errors,
        fixture: "offline synthetic profile; production chooseGrade handler, no form submission",
        capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
      if (errors.length) throw Error(errors.join("; "));
      console.log(`${mode}-${width}: PASS`);
      return;
    }
    const contrast = (a, b) => {
      const luminance = (color) => {
        const channels = color.match(/[\d.]+/g).slice(0, 3).map(Number).map((value) => {
          const channel = value / 255;
          return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
        });
        return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
      };
      const x = luminance(a), y = luminance(b);
      return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
    };
    let failures = 0;
    for (const state of ["initial", "annual", "catchup", "corrected", "keep", "next-child", "long-name",
      "saving", "error", "conflict", "latest", "deferred", "forbidden", "archived", "terminal", "unknown", "confirmed"]) {
      await call(fixture, [state, choices]);
      await new Promise((resolve) => setTimeout(resolve, 150));
      const data = await call(query, [selectors]), errors = [];
      const check = (ok, message) => { if (!ok) errors.push(message); };
      check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "wrong native viewport");
      const visible = !["deferred", "forbidden", "archived", "terminal", "unknown", "confirmed"].includes(state);
      check((data.nodes[".grade-sheet"] || []).length === Number(visible), "dialog visibility");
      check((data.nodes[".tabbar"] || []).length === Number(!visible), "tabbar occlusion/restoration");
      for (const [s, rects] of Object.entries(data.nodes)) for (const r of rects) {
        check(r.left >= -1 && r.right <= width + 1, `${s} horizontal overflow`);
        if (r.fontSize) check(parseFloat(r.fontSize) >= 14, `${s} text below 14px`);
        if ([".grade-primary", ".grade-secondary", ".grade-picker"].includes(s)) check(r.width >= 43 && r.height >= 43, `${s} target below 44px`);
        if ([".grade-primary", ".grade-secondary"].includes(s)) check(contrast(r.color, r.backgroundColor) >= 4.5 && Number(r.opacity) === 1, `${s} text contrast below approved readable style`);
        if ([".grade-sheet", ".grade-actions", ".grade-primary", ".grade-secondary"].includes(s)) check(r.top >= -1 && r.bottom <= data.viewport.screenHeight + 1, `${s} outside native viewport`);
      }
      const primary = data.nodes[".grade-primary"]?.[0], secondary = data.nodes[".grade-secondary"]?.[0];
      const actions = data.nodes[".grade-actions"]?.[0];
      if (primary && secondary) {
        check(Math.abs(primary.top - secondary.top) <= 1 && Math.abs(primary.height - secondary.height) <= 1, "actions not aligned");
        check(primary.left - secondary.right >= 11 && primary.left - secondary.right <= 13, "action gap not 12px");
        // Approved HTML uses flex 1:2 plus 12px padding on both sides of each button.
        check(Math.abs((primary.width - 24) - 2 * (secondary.width - 24)) <= 1, "action content widths not flex 1:2");
        check(actions && Math.abs(secondary.left - actions.left) <= 1 && Math.abs(primary.right - actions.right) <= 1, "actions do not fill content width");
      } else if (primary) {
        check(actions && Math.abs(primary.left - actions.left) <= 1 && Math.abs(primary.width - actions.width) <= 1, "single action does not fill content width");
      }
      if (visible) {
        const body = data.nodes[".grade-body"]?.[0], title = data.nodes[".grade-title"]?.[0];
        const field = data.nodes[state === "latest" ? ".grade-latest" : ".grade-picker"]?.[0];
        const error = data.nodes[".grade-error"]?.[0];
        check(title && field && field.top - title.bottom >= 19, "title/field clearance below 20px");
        check(field && body && field.bottom <= body.bottom + 1, "field clipped");
        if (error) check(error.top - field.bottom >= 11 && error.bottom <= body.bottom + 1, "message clipped or overlaps field");
        check(actions && body && actions.top - body.bottom >= 19, "body/action clearance below 20px");
        check((data.nodes[".grade-picker"] || []).length === Number(state !== "latest"), "latest fact offers editable picker");
        check((data.nodes[".grade-secondary"] || []).length === Number(state !== "latest"), "latest action count mismatch");
      }
      const shot = await send("App.captureScreenshot");
      const bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
      const stem = path.join(out, `${state}-${width}`);
      fs.writeFileSync(stem + ".png", bytes);
      fs.writeFileSync(stem + ".json", JSON.stringify({ ...data, state, errors,
        fixture: "synthetic presentation only; actual lifecycle covered by frontend tests",
        capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex"),
        screenshotPixels: { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) } }, null, 2) + "\n");
      failures += errors.length; console.log(`${state}-${width}: ${errors.join('; ') || 'PASS'}`);
    }
    if (failures) throw Error(`${failures} native geometry errors`);
  } finally { socket.close(); }
}
main().catch((error) => { console.error(error.message); process.exitCode = 1; socket.close(); });
