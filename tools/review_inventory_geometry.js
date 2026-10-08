#!/usr/bin/env node
// Audit rectangles returned by the native Mini Program renderer, not HTML previews.
const fs = require("node:fs");

const SELECTORS = [".inventory-page", ".choices", ".choice", ".more", ".item-title", ".item-meta", ".action-menu"];
const QUERY = `function() {
  return new Promise(resolve => {
    const q = wx.createSelectorQuery();
    ${SELECTORS.map(selector => `q.selectAll("${selector}").fields({ rect: true, size: true, computedStyle: ["paddingRight"] });`).join("\n    ")}
    q.exec(results => {
      const info = typeof wx.getWindowInfo === "function" ? wx.getWindowInfo() : wx.getSystemInfoSync();
      resolve({
        view: getCurrentPages().slice(-1)[0].data.view,
        viewport: { width: info.windowWidth, height: info.windowHeight },
        nodes: results.map(group => (group || []).map(node => ({
          left: node.left, right: node.right, top: node.top, bottom: node.bottom,
          width: node.width, height: node.height, paddingRight: node.paddingRight
        })))
      });
    });
  });
}`;

function audit(capture, expectedWidth) {
  const errors = [];
  const check = (condition, message) => { if (!condition) errors.push(message); };
  const [page = [], containers = [], choices = [], more = [], titles = [], metadata = [], menus = []] = capture.nodes || [];
  const columns = capture.view === "time" ? 2 : 3;
  const expectedChoices = capture.view === "time" ? 2 : capture.view === "count" ? 6 : null;
  check(Math.abs(capture.viewport?.width - expectedWidth) <= 1, `viewport: expected ${expectedWidth}px`);
  check(page.length === 1 && containers.length === 1, "page/selector container missing");
  if (page[0]) check(page[0].left >= -1 && page[0].right <= capture.viewport.width + 1, "page extends horizontally outside viewport");
  check(choices.length >= columns, "selector row incomplete");
  if (expectedChoices !== null) check(choices.length === expectedChoices, `expected ${expectedChoices} choices`);
  if (capture.view === "subject") check(choices.length >= 4, "subject partial row missing");
  const bounds = containers[0];
  const rows = [];
  for (const rect of choices) {
    check(rect.width >= 44 && rect.height >= 44, "selector target below 44px");
    if (bounds) check(rect.left >= bounds.left - 1 && rect.right <= bounds.right + 1, "selector outside container");
    let row = rows.find(group => Math.abs(group[0].top - rect.top) <= 1);
    if (!row) { row = []; rows.push(row); }
    row.push(rect);
  }
  rows.sort((a, b) => a[0].top - b[0].top);
  rows.forEach((row, rowIndex) => {
    row.sort((a, b) => a.left - b.left);
    check(row.length === (rowIndex < rows.length - 1 ? columns : Math.min(columns, choices.length - columns * rowIndex)), `row ${rowIndex}: wrong column count`);
    for (let index = 0; index < row.length; index += 1) {
      check(Math.abs(row[index].width - row[0].width) <= 1, `row ${rowIndex}: unequal widths`);
      check(Math.abs(row[index].height - row[0].height) <= 1, `row ${rowIndex}: unequal heights`);
      if (index > 0) check(row[index].left - row[index - 1].right >= 7.5, `row ${rowIndex}: horizontal gap below 8px`);
      if (rowIndex > 0) check(Math.abs(row[index].left - rows[0][index].left) <= 1, `row ${rowIndex}: column misaligned`);
    }
    if (rowIndex > 0) check(row[0].top - rows[rowIndex - 1][0].bottom >= 7.5, `row ${rowIndex}: vertical gap below 8px`);
  });
  check(more.length > 0, "no expanded writable item action to measure");
  more.forEach((rect, index) => {
    check(Math.abs(rect.width - 44) <= 1 && Math.abs(rect.height - 44) <= 1, `more ${index}: must be 44×44px`);
    if (page[0]) check(rect.left >= page[0].left - 1 && rect.right <= page[0].right + 1, `more ${index}: outside page`);
    const title = titles[index];
    check(Boolean(title), `more ${index}: missing title`);
    if (title) check(title.right - parseFloat(title.paddingRight || "0") <= rect.left - 8, `more ${index}: title clearance below 8px`);
    for (const meta of metadata) {
      if (meta.top >= rect.top - 1 && meta.top < rect.bottom && Math.abs(meta.right - title?.right) <= 1) {
        check(meta.right - parseFloat(meta.paddingRight || "0") <= rect.left - 8, `more ${index}: metadata clearance below 8px`);
      }
    }
  });
  menus.forEach((menu, index) => {
    check(menu.left >= -1 && menu.right <= capture.viewport.width + 1 && menu.top >= -1 && menu.bottom <= capture.viewport.height + 1, `menu ${index}: outside viewport`);
    check(menu.width >= 44 && menu.height >= 44, `menu ${index}: too small`);
    if (more[0]) check(menu.top >= more[0].bottom - 1 || menu.bottom <= more[0].top + 1, `menu ${index}: overlaps trigger`);
  });
  return errors;
}

async function capture(endpoint, view, openMenu = false) {
  const socket = new WebSocket(endpoint);
  const pending = new Map();
  let sequence = 0;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`${method} timed out`)); }, 12000);
    pending.set(id, message => {
      clearTimeout(timer);
      if (message.error) reject(new Error(message.error.message)); else resolve(message.result);
    });
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
    if (page.path !== "pages/review-inventory/index") {
      await send("App.callWxMethod", { method: "navigateTo", args: [{ url: "/pages/review-inventory/index" }] });
    }
    await send("App.callFunction", { functionDeclaration: "function(view) { const p = getCurrentPages().slice(-1)[0]; return p.data.view === view ? null : p.changeView({ currentTarget: { dataset: { id: view } } }); }", args: [view] });
    let ready = false;
    for (let attempt = 0; attempt < 40; attempt += 1) {
      const state = (await send("App.callFunction", { functionDeclaration: "function() { const d = getCurrentPages().slice(-1)[0].data; return { view: d.view, loaded: d.loaded, loading: d.loading, error: d.error }; }", args: [] })).result;
      if (state.error) throw new Error(`page error: ${state.error}`);
      if (state.view === view && state.loaded && !state.loading) { ready = true; break; }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    if (!ready) throw new Error(`${view} did not finish loading`);
    if (openMenu) {
      await send("App.callFunction", { functionDeclaration: "function() { const p = getCurrentPages().slice(-1)[0]; const first = p.data.groups[0]?.entries[0]; if (!first) throw Error('no item to open'); if (p.data.actionMenuId) p.closeActionMenu(); p.openActions({ currentTarget: { dataset: { id: first.knowledge_id } } }); }", args: [] });
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return (await send("App.callFunction", { functionDeclaration: QUERY, args: [] })).result;
  } finally { socket.close(); }
}

async function main() {
  const [mode, ...args] = process.argv.slice(2);
  if (mode === "audit") {
    const files = args;
    if (!files.length) throw new Error("usage: audit <native-capture.json>...");
    for (const file of files) {
      const payload = JSON.parse(fs.readFileSync(file, "utf8"));
      const errors = audit(payload, payload.expectedWidth);
      if (errors.length) throw new Error(`${file}: ${errors.join("; ")}`);
      console.log(`NATIVE_GEOMETRY_VALID ${payload.view} ${payload.expectedWidth}px`);
    }
  } else if (mode === "capture") {
    const [view, widthText, file, menuFlag] = args;
    const width = Number(widthText);
    if (!["time", "subject", "count"].includes(view) || ![320, 390, 430].includes(width) || !file) {
      throw new Error("usage: capture <time|subject|count> <320|390|430> <output.json> [--open-menu]");
    }
    if (menuFlag && menuFlag !== "--open-menu") throw new Error("unknown capture option");
    const payload = { ...(await capture(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420", view, menuFlag === "--open-menu")), expectedWidth: width };
    if (menuFlag === "--open-menu" && !payload.nodes[6]?.length) throw new Error("native action menu missing");
    const errors = audit(payload, width);
    if (errors.length) throw new Error(errors.join("; "));
    fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
    console.log(`NATIVE_GEOMETRY_VALID ${view} ${width}px`);
  } else throw new Error("usage: capture|audit");
}

if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { audit };
