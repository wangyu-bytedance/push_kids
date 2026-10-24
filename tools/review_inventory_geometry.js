#!/usr/bin/env node
// Audit rectangles returned by the native Mini Program renderer, not HTML previews.
const fs = require("node:fs");

const SELECTORS = [".inventory-page", ".filter-row", ".segment", ".filter-trigger", ".filter-panel", ".filter-option", ".more", ".item-main", ".item-title", ".item-meta", ".action-menu", ".group-toggle", ".status-row", ".status-segment", ".source-link", ".item-coverage", ".menu-option"];
const QUERY = `function() {
  return new Promise(resolve => {
    const q = wx.createSelectorQuery();
    ${SELECTORS.map(selector => `q.selectAll("${selector}").fields({ rect: true, size: true });`).join("\n    ")}
    q.exec(results => {
      const info = typeof wx.getWindowInfo === "function" ? wx.getWindowInfo() : wx.getSystemInfoSync();
      resolve({
        view: getCurrentPages().slice(-1)[0].data.view,
        viewport: { width: info.windowWidth, height: info.windowHeight },
        nodes: results.map(group => (group || []).map(node => ({
          left: node.left, right: node.right, top: node.top, bottom: node.bottom,
          width: node.width, height: node.height
        })))
      });
    });
  });
}`;

function audit(capture, expectedWidth) {
  const errors = [];
  const check = (condition, message) => { if (!condition) errors.push(message); };
  const [page = [], filters = [], segments = [], triggers = [], panels = [], options = [], more = [], mains = [], titles = [], metadata = [], menus = [], groups = []] = capture.nodes || [];
  const width = capture.viewport?.width;
  check(Math.abs(width - expectedWidth) <= 1, `viewport: expected ${expectedWidth}px`);
  check(page.length === 1 && filters.length === 1, "page/filter row missing");
  const contained = (inner, outer, slack = 1) => inner.left >= outer.left - slack && inner.right <= outer.right + slack;
  if (page[0]) check(page[0].left >= -1 && page[0].right <= width + 1, "page extends horizontally outside viewport");
  if (filters[0] && page[0]) check(contained(filters[0], page[0]), "filter outside page");
  if (capture.view === "time") {
    check(segments.length === 2 && triggers.length === 0, "time requires exactly two segments");
    if (segments.length === 2) {
      check(Math.abs(segments[0].width - segments[1].width) <= 1, "time segments have unequal widths");
      check(Math.abs(segments[0].top - segments[1].top) <= 1, "time segments are not on one row");
      check(segments[1].left - segments[0].right >= 7.5, "time segment gap below 8px");
    }
  } else {
    check(segments.length === 0 && triggers.length === 1, "subject/count requires one filter trigger");
    if (triggers[0] && filters[0]) check(Math.abs(triggers[0].width - filters[0].width) <= 1, "filter trigger does not fill row");
  }
  for (const rect of [...segments, ...triggers]) {
    check(rect.width >= 44 && rect.height >= 44, "filter target below 44px");
    if (filters[0]) check(contained(rect, filters[0]), "filter target outside row");
  }
  check(panels.length <= 1, "multiple filter panels open");
  for (const panel of panels) {
    if (filters[0]) check(contained(panel, filters[0]), "filter panel outside row");
    if (page[0]) check(contained(panel, page[0]), "filter panel outside page");
  }
  for (const option of options) {
    check(option.width >= 44 && option.height >= 44, "filter option below 44px");
    if (panels[0]) check(contained(option, panels[0]), "filter option outside panel");
  }
  groups.forEach((rect, index) => check(rect.height >= 44, `group ${index}: toggle below 44px`));
  check(more.length > 0 || capture.readOnly || capture.empty, "no expanded writable item action to measure");
  more.forEach((rect, index) => {
    check(Math.abs(rect.width - 44) <= 1 && Math.abs(rect.height - 44) <= 1, `more ${index}: must be 44×44px`);
    if (page[0]) check(contained(rect, page[0]), `more ${index}: outside page`);
    const main = mains[index];
    check(Boolean(main), `more ${index}: missing item main`);
    if (main) check(main.right <= rect.left - 7.5, `more ${index}: text clearance below 8px`);
    for (const textRect of [titles[index], metadata[index]]) {
      if (textRect && main) check(contained(textRect, main), `more ${index}: text outside item main`);
    }
  });
  menus.forEach((menu, index) => {
    check(menu.left >= -1 && menu.right <= width + 1 && menu.top >= -1 && menu.bottom <= capture.viewport.height + 1, `menu ${index}: outside viewport`);
    check(menu.width >= 44 && menu.height >= 44, `menu ${index}: too small`);
    const trigger = more[capture.menuTriggerIndex || 0];
    if (trigger) check(menu.top >= trigger.bottom - 1 || menu.bottom <= trigger.top + 1, `menu ${index}: overlaps trigger`);
  });
  if (capture.reviewStatus) {
    const [statusRows = [], statusButtons = [], sources = [], coverage = [], actions = []] = capture.nodes.slice(12);
    check(statusRows.length === 1 && statusButtons.length === 2, "status selector missing");
    if (statusButtons.length === 2) {
      check(Math.abs(statusButtons[0].width - statusButtons[1].width) <= 1, "status segments unequal");
      check(statusButtons[1].left - statusButtons[0].right >= 7.5, "status gap below 8px");
    }
    for (const rect of [...statusButtons, ...sources, ...actions]) {
      check(rect.width >= 43 && rect.height >= 43, "status/source/action target below 44px");
      if (page[0]) check(contained(rect, page[0]), "status/source/action outside page");
    }
    for (const rect of coverage) if (page[0]) check(contained(rect, page[0]), "covering text outside page");
    check(!capture.readOnly || more.length === 0, "viewer has management actions");
    if (capture.reviewStatus === "superseded") {
      check(capture.view !== "time", "superseded has time view");
      check(coverage.length === (capture.empty ? 0 : 1), "covering relationship missing");
      check(sources.length === (capture.empty ? 0 : 1), "original source missing");
      if (menus.length) check(actions.length === 1, "superseded menu must only delete");
    }
  }
  return errors;
}

async function capture(endpoint, view, menuMode = "", openFilter = false) {
  const socket = new WebSocket(endpoint);
  const pending = new Map();
  let sequence = 0;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`${method} timed out`)); }, 12000);
    pending.set(id, message => { clearTimeout(timer); if (message.error) reject(new Error(`${method}: ${JSON.stringify(message.error)}`)); else resolve(message.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    const callback = pending.get(message.id);
    if (callback) { pending.delete(message.id); callback(message); }
  };
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  try {
    const page = await send("App.getCurrentPage");
    if (page.path !== "pages/review-inventory/index") await send("App.callWxMethod", { method: "navigateTo", args: [{ url: "/pages/review-inventory/index" }] });
    await send("App.callFunction", { functionDeclaration: "function(view) { const p = getCurrentPages().slice(-1)[0]; return p.data.view === view ? null : p.changeView({ currentTarget: { dataset: { id: view } } }); }", args: [view] });
    let ready = false;
    for (let attempt = 0; attempt < 40; attempt += 1) {
      const state = (await send("App.callFunction", { functionDeclaration: "function() { const d = getCurrentPages().slice(-1)[0].data; return { view: d.view, loaded: d.loaded, loading: d.loading, error: d.error }; }", args: [] })).result;
      if (state.error) throw new Error(`page error: ${state.error}`);
      if (state.view === view && state.loaded && !state.loading) { ready = true; break; }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    if (!ready) throw new Error(`${view} did not finish loading`);
    if (menuMode) {
      await send("App.callFunction", { functionDeclaration: "function(mode) { const p = getCurrentPages().slice(-1)[0]; const entries = p.data.groups[0]?.entries || []; const index = mode === 'last' ? entries.length - 1 : mode === 'middle' ? Math.floor((entries.length - 1) / 2) : 0; const target = entries[index]; if (!target) throw Error('no item to open'); if (p.data.actionMenuId) p.closeActionMenu(); p.openActions({ currentTarget: { dataset: { id: target.knowledge_id } } }); }", args: [menuMode] });
    }
    if (openFilter) await send("App.callFunction", { functionDeclaration: "function() { const p = getCurrentPages().slice(-1)[0]; if (!p.data.pickerOpen) p.togglePicker(); }", args: [] });
    await new Promise(resolve => setTimeout(resolve, 100));
    return (await send("App.callFunction", { functionDeclaration: QUERY, args: [] })).result;
  } finally { socket.close(); }
}

async function main() {
  const [mode, ...args] = process.argv.slice(2);
  if (mode === "audit") {
    if (!args.length) throw new Error("usage: audit <native-capture.json>...");
    for (const file of args) {
      const payload = JSON.parse(fs.readFileSync(file, "utf8"));
      const errors = audit(payload, payload.expectedWidth);
      if (errors.length) throw new Error(`${file}: ${errors.join("; ")}`);
      console.log(`NATIVE_GEOMETRY_VALID ${payload.view} ${payload.expectedWidth}px`);
    }
  } else if (mode === "capture") {
    const [view, widthText, file, ...flags] = args;
    const width = Number(widthText);
    if (!["time", "subject", "count"].includes(view) || ![320, 390, 430].includes(width) || !file || flags.some(flag => !["--open-menu", "--open-menu-middle", "--open-menu-last", "--open-filter"].includes(flag))) {
      throw new Error("usage: capture <time|subject|count> <320|390|430> <output.json> [--open-menu|--open-menu-middle|--open-menu-last] [--open-filter]");
    }
    const menuMode = flags.includes("--open-menu-last") ? "last" : flags.includes("--open-menu-middle") ? "middle" : flags.includes("--open-menu") ? "first" : "";
    const payload = { ...(await capture(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420", view, menuMode, flags.includes("--open-filter"))), expectedWidth: width };
    if (menuMode === "last") payload.menuTriggerIndex = (payload.nodes[6] || []).length - 1;
    if (menuMode === "middle") payload.menuTriggerIndex = Math.floor(((payload.nodes[6] || []).length - 1) / 2);
    if (menuMode && !payload.nodes[10]?.length) throw new Error("native action menu missing");
    if (flags.includes("--open-filter") && !payload.nodes[4]?.length) throw new Error("native filter panel missing");
    fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
    const errors = audit(payload, width);
    if (errors.length) throw new Error(errors.join("; "));
    console.log(`NATIVE_GEOMETRY_VALID ${view} ${width}px`);
  } else throw new Error("usage: capture|audit");
}

if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { audit, SELECTORS, QUERY };
