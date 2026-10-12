// Validate native Mini Program rectangles captured via its automation runtime.
const fs = require("node:fs");

const SELECTORS = [".page", ".daily-task-section", ".daily-task-settings",
  ".daily-task-row", ".daily-task-copy", ".daily-task-action",
  ".daily-task-setting-row", ".daily-task-setting-copy", ".daily-task-edit",
  ".daily-task-presets", ".daily-task-preset", ".daily-task-form-actions",
  ".daily-task-form-actions button", ".daily-task-form .pk-input", ".sec-bar"];
const QUERY = `function() {
  return new Promise(resolve => {
    const q = wx.createSelectorQuery();
    ${SELECTORS.map(selector => `q.selectAll("${selector}").fields({rect: true, size: true});`).join("\n")}
    q.exec(results => {
      const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
      resolve({ viewport: {width: info.windowWidth, height: info.windowHeight},
        nodes: results.map(group => (group || []).map(node => ({
          left: node.left, right: node.right, top: node.top, bottom: node.bottom,
          width: node.width, height: node.height
        }))) });
    });
  });
}`;

function audit(capture) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  const width = capture.viewport?.width;
  check([320, 390, 430].includes(width), "unapproved viewport");
  check(Math.abs(width - capture.expectedWidth) <= 1, "viewport does not match requested width");
  const [page = [], today = [], settings = [], rows = [], copies = [], actions = [],
    settingRows = [], settingCopies = [], edits = [], presets = [], chips = [],
    formActions = [], formButtons = [], inputs = [], bars = []] = capture.nodes || [];
  check(page.length === 1, "page root missing");
  check(today.length + settings.length === 1, "daily task region missing");
  const inside = (node, parent) => node.left >= parent.left - 1 && node.right <= parent.right + 1;
  for (const node of [page[0], ...today, ...settings].filter(Boolean)) {
    check(node.left >= -1 && node.right <= width + 1, "region extends outside viewport");
  }
  const pairs = (containers, texts, buttons) => {
    containers.forEach((row, index) => {
      const copy = texts[index];
      if (copy) check(inside(copy, row), "task text outside row");
      const action = buttons[index];
      if (action) {
        check(inside(action, row), "task action outside row");
        if (copy) check(copy.right <= action.left - 7, "task text overlaps action or lacks clearance");
      }
    });
  };
  pairs(rows, copies, actions);
  pairs(settingRows, settingCopies, edits);
  for (const node of [...actions, ...edits, ...chips, ...formButtons, ...inputs, ...bars]) {
    check(node.width >= 43 && node.height >= 43, "control target below 44px tolerance");
    check(node.left >= -1 && node.right <= width + 1, "control outside viewport");
  }
  for (const chip of chips) if (presets[0]) check(inside(chip, presets[0]), "preset outside group");
  for (let index = 1; index < chips.length; index += 1) {
    const a = chips[index - 1];
    const b = chips[index];
    if (Math.abs(a.top - b.top) <= 1) check(b.left - a.right >= 7, "preset gap below 8px tolerance");
    else check(b.top - a.bottom >= 7, "preset row gap below 8px tolerance");
  }
  for (const button of formButtons) if (formActions[0]) check(inside(button, formActions[0]), "form button outside action group");
  if (formButtons.length === 2) {
    check(Math.abs(formButtons[0].width - formButtons[1].width) <= 1, "unequal form action columns");
    check(formButtons[1].left - formButtons[0].right >= 11, "form action gap below 12px tolerance");
  }
  return errors;
}

async function capture(endpoint, surface, expectedWidth, file) {
  const socket = new WebSocket(endpoint);
  const pending = new Map();
  let sequence = 0;
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error(`${method} timed out`)); }, 10000);
    pending.set(id, message => { clearTimeout(timer); if (message.error) reject(Error(`${method} failed`)); else resolve(message.result); });
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
    if (page.path !== `pages/${surface}/index`) throw Error(`open ${surface} before capturing`);
    const state = await send("App.callFunction", { functionDeclaration: "function() { const d=getCurrentPages().slice(-1)[0].data; return {loading:d.loading,error:d.error}; }", args: [] });
    if (state.result.loading || state.result.error) throw Error("page is not loaded successfully");
    const payload = { ...(await send("App.callFunction", { functionDeclaration: QUERY, args: [] })).result, surface, expectedWidth };
    fs.writeFileSync(file, `${JSON.stringify(payload, null, 2)}\n`);
    const errors = audit(payload);
    if (errors.length) throw Error(errors.join("; "));
    console.log(`NATIVE_DAILY_TASK_GEOMETRY_VALID ${surface} ${expectedWidth}px`);
  } finally { socket.close(); }
}

async function main() {
  const [mode, surface, width, file] = process.argv.slice(2);
  if (mode === "audit") {
    for (const input of process.argv.slice(3)) {
      const errors = audit(JSON.parse(fs.readFileSync(input, "utf8")));
      if (errors.length) throw Error(`${input}: ${errors.join("; ")}`);
      console.log(`NATIVE_DAILY_TASK_GEOMETRY_VALID ${input}`);
    }
  } else if (mode === "capture" && ["settings", "today"].includes(surface) && file) {
    await capture(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420", surface, Number(width), file);
  } else throw Error("usage: capture <settings|today> <320|390|430> <file.json> | audit <file.json>...");
}
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 1; });
module.exports = { audit };
