const fs = require("node:fs");
const path = require("node:path");
const host = process.argv[2];
if (!["embedded", "standalone"].includes(host)) throw Error("invalid host");
const out = "/Users/bytedance/Documents/push_kids/docs/quality/evidence/report-footer-tips-20261101";
const socket = new WebSocket("ws://127.0.0.1:9612");
const pending = new Map();
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
      message.error ? reject(Error(message.error.message)) : resolve(message.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) =>
  (await send("App.callFunction", { functionDeclaration, args })).result;
const operate = `function(host,operation,json){
  const current=getCurrentPages().slice(-1)[0],
    p=host==='embedded'?current.selectComponent('#inventory-component'):current,
    g=getApp().globalData;
  if(operation==='configure'){g.footerFixture=JSON.parse(json);return true;}
  if(operation==='release'){g.footerFixture.release();return true;}
  if(operation==='ready'){p.visible=true;p.familyAtLoad=g.familyId;return true;}
  if(operation==='next'){p.nextPage();return true;}
  if(operation==='reload'){p.reload();return true;}
  if(operation==='retry'){p.retry();return true;}
  if(operation==='readonly'){p.setData({canWrite:false});return true;}
  if(operation==='footer')return new Promise(resolve=>{
    const q=wx.createSelectorQuery().in(p);
    q.selectAll('.inventory-pagination').boundingClientRect();q.selectViewport().scrollOffset();
    q.exec(([rows,scroll])=>{
      const pager=rows.slice(-1)[0];
      wx.pageScrollTo({scrollTop:Math.max(0,scroll.scrollTop+pager.top-140),duration:0,
        complete:()=>wx.nextTick(()=>{
          const local=wx.createSelectorQuery().in(p),root=wx.createSelectorQuery().in(current);
          local.selectAll('.inventory-pagination').boundingClientRect();
          local.exec(([pagers])=>{
            root.selectAll('#report-edit-plan .disclosure-footer').boundingClientRect();
            root.exec(([footers])=>{
              const tab=current.getTabBar&&current.getTabBar();
              const finish=tabbars=>resolve({pagers,footers,tabbars,
                viewport:{width:wx.getSystemInfoSync().windowWidth,height:wx.getSystemInfoSync().windowHeight}});
              if(!tab)return finish([]);
              const tq=wx.createSelectorQuery().in(tab);
              tq.selectAll('.tabbar').boundingClientRect();tq.exec(([tabbars])=>finish(tabbars));
            });
          });
        })});
    });
  });
  return new Promise(resolve=>wx.nextTick(()=>{
    const q=wx.createSelectorQuery().in(p);
    q.selectAll('.inventory-page-button').fields({rect:true,properties:['disabled']});
    q.selectAll('.more').boundingClientRect();
    q.selectAll('.readonly').boundingClientRect();
    q.selectAll('.inventory-feedback').boundingClientRect();
    q.exec(([buttons,more,readonly,feedback])=>resolve({
      pageNumber:p.data.pageNumber,loading:p.data.loading,error:p.data.error,notice:p.data.notice,
      ids:p.data.items.map(item=>item.knowledge_id),nextCursor:p.data.nextCursor,
      calls:g.footerFixture.calls,buttons,more,readonly,feedback,
      width:wx.getSystemInfoSync().windowWidth
    }));
  }));
}`;
const response = (id, next) => JSON.stringify({
  items: [{ knowledge_id: id, knowledge_name: "合成分页条目 " + id, subject_id: "english",
    subject_name: "英语", review_count: 1, review_status: "normal", arrangement_state: "waiting",
    can_schedule: true, state_version: 1 }],
  total: 3, next_cursor: next, as_of_day: "2026-11-01", child_writable: true
});
const states = [];
const check = (ok, message) => { if (!ok) throw Error(message); };
async function step(operation, config) {
  return call(operate, [host, operation, JSON.stringify(config || {})]);
}
async function settled(name) {
  for (let i = 0; i < 12; i++) {
    const state = await step("state");
    if (!state.loading) { states.push({ name, ...state }); return state; }
  }
  throw Error("native request did not settle: " + name);
}
async function main() {
  await new Promise((resolve, reject) => {
    socket.onopen = resolve; socket.onerror = () => reject(Error("automation unavailable"));
  });
  const runtime = await call(`function(){return {offline:getApp().globalData.useCloud===false,
    synthetic:getApp().globalData.familyId==='synthetic',width:wx.getSystemInfoSync().windowWidth};}`);
  check(runtime.offline && runtime.synthetic && runtime.width === 430, "offline native precondition");
  const url = host === "embedded" ? "/pages/reports/index" : "/pages/review-inventory/index?childId=synthetic";
  await send("App.callWxMethod", { method: host === "embedded" ? "switchTab" : "navigateTo", args: [{ url }] });
  if (host === "embedded") {
    await call(`function(){const p=getCurrentPages().slice(-1)[0];return new Promise(resolve=>
      p.setData({childId:'synthetic',inventoryExpanded:true},()=>wx.nextTick(()=>resolve(true))));}`);
  }
  await step("ready");
  await step("configure", { payload: response("page1", "cursor2"), calls: 0 });
  await step("reload");
  let state = await settled("reload-first");
  check(state.pageNumber === 1 && state.ids.join() === "page1", "first page did not load");
  await step("configure", { payload: response("page2", "cursor3"), calls: 0, hold: true });
  await step("next");
  state = await step("state");
  states.push({ name: "loading", ...state });
  check(state.loading && state.ids.join() === "page1" && state.buttons.slice(-2).every(b => b.disabled),
    "loading did not preserve data/disable pagination");
  await step("next");
  state = await step("state");
  check(state.calls === 1, "loading allowed duplicate next request");
  await step("release");
  state = await settled("next-replaces-first");
  check(state.pageNumber === 2 && state.ids.join() === "page2", "next page did not replace first");
  await step("configure", { fail: true, payload: response("page3", null), calls: 0 });
  await step("next");
  state = await settled("failure-preserves-current-page");
  check(state.pageNumber === 2 && state.ids.join() === "page2" && state.error === "合成读取失败",
    "failure lost current page");
  check(!state.notice && state.feedback.length === 0, "read failure displayed success feedback");
  await step("configure", { payload: response("page2-retry", "cursor3"), calls: 0 });
  await step("retry");
  state = await settled("retry-current-page");
  check(state.pageNumber === 2 && state.ids.join() === "page2-retry" && !state.error, "retry failed");
  await step("configure", { payload: response("page1-reload", "cursor2"), calls: 0 });
  await step("reload");
  state = await settled("back-to-first");
  check(state.pageNumber === 1 && state.ids.join() === "page1-reload", "reload did not reset page");
  await step("readonly");
  state = await step("state");
  states.push({ name: "readonly", ...state });
  check(state.more.length === 0 && state.readonly.length === 1, "readonly exposed actions");
  const footer = await step("footer");
  states.push({ name: "footer-clearance", ...footer });
  const pager = footer.pagers.slice(-1)[0];
  check(pager && pager.top >= 0 && pager.bottom <= footer.viewport.height, "pager outside visible window");
  if (host === "embedded") {
    const collapse = footer.footers[0], tab = footer.tabbars[0];
    check(collapse && collapse.height >= 44 && collapse.top >= pager.bottom, "collapse overlaps pager");
    check(tab && collapse.bottom <= tab.top && pager.bottom <= tab.top, "tab obscures footer");
  }
  console.log(host + ": PASS 8 native method/state/clearance checks; tap/device NOT_RUN");
}
main().then(() => {
  fs.writeFileSync(path.join(out, "native-behavior-" + host + "-430.json"), JSON.stringify({
    status: "PASS", scope: "isolated read-only synthetic API; real production controller/WXML/WXSS",
    mechanism: "official App.callFunction invokes existing native controller methods; no simulated touch",
    host, viewport: "430x932", states, capturedAt: new Date().toISOString(),
    physicalDeviceStatus: "NOT_RUN", tapStatus: "NOT_RUN"
  }, null, 2) + "\n");
}).catch(error => {
  console.error(error.message);
  fs.writeFileSync(path.join(out, "native-behavior-" + host + "-430.json"), JSON.stringify({
    status: "FAIL", host, states, error: error.message, capturedAt: new Date().toISOString()
  }, null, 2) + "\n");
  process.exitCode = 1;
}).finally(() => socket.close());
