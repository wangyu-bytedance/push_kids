const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

/* 共享的小程序页面加载器：在同一个 VM 上下文里按相对路径解析 require，
   页面与它共享的模块（detail.js / draft.js / utils/*）都用真实实现，只有 utils/api 被替换成桩。 */
function loadPage(entry, request, options = {}) {
  let page;
  let component;
  const timers = new Set();
  const app = { globalData: { selectedChildId: "child", ...(options.globalData || {}) },
    selectChild(id) { this.globalData.selectedChildId = id; }, setTabBadge() {} };
  const wx = {
    showToast() {}, showModal({ success }) { success({ confirm: true }); }, setNavigationBarTitle() {},
    navigateTo() {}, navigateBack() {}, switchTab() {}, pageScrollTo() {}, stopPullDownRefresh() {},
    getStorageSync() { return {}; }, setStorageSync() {},
    ...(options.wx || {})
  };
  const modules = new Map();
  function load(file) {
    if (file.endsWith("/utils/api.js")) {
      return { request, newIdempotencyKey: () => "fixture-key", ...(options.api || {}) };
    }
    if (modules.has(file)) return modules.get(file);
    const module = { exports: {} };
    vm.runInNewContext(fs.readFileSync(file, "utf8"), {
      module,
      require(name) { return load(path.resolve(path.dirname(file), name + ".js")); },
      Page(value) { page = value; },
      Component(value) { component = value; },
      wx, getApp: () => app,
      setTimeout(fn) { timers.add(fn); return fn; },
      clearTimeout(fn) { timers.delete(fn); }
    }, { filename: file });
    modules.set(file, module.exports);
    return module.exports;
  }
  const exports = load(path.resolve("apps/miniprogram", entry));
  const target = page || component;
  if (target) {
    target.setData = (updates) => {
      for (const [key, value] of Object.entries(updates)) {
        const parts = key.replace(/\[(\d+)\]/g, ".$1").split(".");
        let node = target.data;
        for (const part of parts.slice(0, -1)) node = node[part];
        node[parts.at(-1)] = value;
      }
    };
  }
  return { page: target, exports, app, wx, timers };
}

module.exports = { loadPage };
