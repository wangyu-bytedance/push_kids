#!/usr/bin/env node
// Native WeChat rectangles only: no child names, record text, IDs, images or response bodies.
const fs = require("node:fs");

const QUERY = `function() {
  return new Promise(resolve => {
    const page = getCurrentPages().slice(-1)[0];
    const q = wx.createSelectorQuery().in(page);
    for (const selector of ["#sec-subjects", "#report-history", "#report-edit-plan", "#sec-activities", ".report-disclosure .history-toggle", "#report-history .h-search"]) {
      q.selectAll(selector).fields({ rect: true, size: true });
    }
    q.exec(groups => {
      const info = typeof wx.getWindowInfo === "function" ? wx.getWindowInfo() : wx.getSystemInfoSync();
      resolve({ viewport: { width: info.windowWidth, height: info.windowHeight, screenHeight: info.screenHeight },
        expanded: { history: !!page.data.historyExpanded, editPlan: !!page.data.inventoryExpanded },
        nodes: groups.map(group => (group || []).map(node => ({ left: node.left, right: node.right,
          top: node.top, bottom: node.bottom, width: node.width, height: node.height }))) });
    });
  });
}`;

function audit(payload, expectedWidth, state) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  const [subject = [], history = [], editPlan = [], activity = [], toggles = [], historyBody = []] = payload.nodes || [];
  check(Math.abs(payload.viewport.width - expectedWidth) <= 1, `viewport must be ${expectedWidth}px`);
  check(payload.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[expectedWidth], "simulator screen height mismatch");
  check(subject.length === 1 && history.length === 1 && editPlan.length === 1 && activity.length === 1, "report sections missing");
  check(toggles.length === 2, "two disclosure toggles required");
  check(payload.expanded?.history === ["history-open", "both-open"].includes(state), "history state mismatch");
  check(payload.expanded?.editPlan === ["review-open", "both-open"].includes(state), "edit plan state mismatch");
  check(historyBody.length === (payload.expanded?.history ? 1 : 0), "history body mounting mismatch");
  if (editPlan[0] && toggles[1]) check((editPlan[0].height > toggles[1].height + 20) === !!payload.expanded?.editPlan, "edit plan body mounting mismatch");
  for (const [index, rect] of toggles.entries()) {
    check(rect.height >= 44 && rect.width >= 44, `toggle ${index} below 44px`);
    check(rect.left >= -1 && rect.right <= expectedWidth + 1, `toggle ${index} outside viewport`);
  }
  for (const rect of [subject[0], history[0], editPlan[0], activity[0]]) {
    if (rect) check(rect.left >= -1 && rect.right <= expectedWidth + 1, "section outside viewport");
  }
  if (subject[0] && history[0]) check(subject[0].bottom <= history[0].top + 1, "history precedes subjects");
  if (history[0] && editPlan[0]) check(history[0].bottom <= editPlan[0].top + 1, "edit plan overlaps history");
  if (editPlan[0] && activity[0]) check(editPlan[0].bottom <= activity[0].top + 1, "activities overlap edit plan");
  return errors;
}

async function capture(endpoint, state) {
  const socket = new WebSocket(endpoint);
  const pending = new Map();
  let sequence = 0;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`${method} timed out`)); }, 15000);
    pending.set(id, message => { clearTimeout(timer); if (message.error) reject(new Error(`${method}: ${JSON.stringify(message.error)}`)); else resolve(message.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
  socket.onmessage = event => { const message = JSON.parse(event.data); const done = pending.get(message.id); if (done) { pending.delete(message.id); done(message); } };
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  try {
    const current = await send("App.getCurrentPage");
    if (current.path !== "pages/reports/index") await send("App.callWxMethod", { method: "switchTab", args: [{ url: "/pages/reports/index" }] });
    let ready = false;
    for (let attempt = 0; attempt < 50; attempt += 1) {
      const result = (await send("App.callFunction", { functionDeclaration: "function() { const p = getCurrentPages().slice(-1)[0]; return { route: p.route, ready: !!p.data.report, failed: !!p.data.error }; }", args: [] })).result;
      if (result.failed) throw new Error("report load failed");
      if (result.route === "pages/reports/index" && result.ready) { ready = true; break; }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    if (!ready) throw new Error("report did not finish loading");
    await send("App.callFunction", { functionDeclaration: `function(state) {
      const p = getCurrentPages().slice(-1)[0];
      p.setData({ historyExpanded: false, inventoryExpanded: false });
      if (state === "history-open" || state === "both-open") return p.toggleHistory();
    }`, args: [state] });
    if (state === "review-open" || state === "both-open") {
      await send("App.callFunction", { functionDeclaration: "function() { getCurrentPages().slice(-1)[0].toggleInventory(); }", args: [] });
    }
    await new Promise(resolve => setTimeout(resolve, 250));
    return (await send("App.callFunction", { functionDeclaration: QUERY, args: [] })).result;
  } finally { socket.close(); }
}

async function main() {
  const [mode, state, widthText, file] = process.argv.slice(2);
  const states = ["collapsed", "history-open", "review-open", "both-open"];
  if (mode === "audit") {
    const payload = JSON.parse(fs.readFileSync(state, "utf8"));
    const errors = audit(payload, payload.expectedWidth, payload.state);
    if (errors.length) throw new Error(errors.join("; "));
    console.log(`REPORT_GEOMETRY_VALID ${payload.state} ${payload.expectedWidth}px`);
    return;
  }
  const width = Number(widthText);
  if (mode !== "capture" || !states.includes(state) || ![320, 390, 430].includes(width) || !file) {
    throw new Error("usage: capture <collapsed|history-open|review-open|both-open> <320|390|430> <file.json> | audit <file.json>");
  }
  const payload = { ...(await capture(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420", state)), expectedWidth: width, state };
  fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
  const errors = audit(payload, width, state);
  if (errors.length) throw new Error(errors.join("; "));
  console.log(`REPORT_GEOMETRY_VALID ${state} ${width}px`);
}

if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { audit };
