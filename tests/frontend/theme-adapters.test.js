const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function runtime() {
  const cache = new Map(), writes = [], chrome = [], events = [];
  let currentPage, component;
  const wx = { getStorageSync() {}, setStorageSync(...args) { writes.push(args); },
    setNavigationBarColor(value) { chrome.push(value); }, setBackgroundColor() {}, setBackgroundTextStyle() {} };
  function load(relative) {
    const file = path.resolve("apps/miniprogram", relative);
    if (cache.has(file)) return cache.get(file).exports;
    const module = { exports: {} }; cache.set(file, module);
    vm.runInNewContext(fs.readFileSync(file, "utf8"), {
      module, wx, console: { warn() {} },
      getCurrentPages: () => currentPage ? [currentPage] : [],
      Component(value) { component = value; },
      require(name) { return load(path.relative(path.resolve("apps/miniprogram"), path.resolve(path.dirname(file), name + ".js"))); }
    }, { filename: file });
    return module.exports;
  }
  function host(definition) {
    const h = { ...definition, ...definition.methods, data: JSON.parse(JSON.stringify(definition.data)),
      updates: [], setData(value) { this.updates.push(value); Object.assign(this.data, value); },
      triggerEvent(name, detail) { events.push({ name, detail }); } };
    return h;
  }
  return { load, host, wx, writes, chrome, events, current(h) { currentPage = h; }, component: () => component };
}

test("page adapters retain lifecycle arguments, Promise identity, drafts and current-page chrome ownership", async () => {
  const r = runtime(), { withThemePage } = r.load("presentation/theme/adapters.js");
  const { themeState } = r.load("presentation/theme/state.js");
  const returned = Promise.resolve("loaded"), calls = [];
  const definition = withThemePage({ data: { draft: "未提交的自然观察", cursor: "next", saving: true },
    onLoad(arg) { calls.push([this, arg]); return returned; }, onShow() { calls.push("show"); } });
  const first = r.host(definition), second = r.host(withThemePage({ data: {} }));
  r.current(first);
  assert.equal(first.onLoad("query"), returned);
  first.onShow(); first.onShow();
  second.onLoad(); // Hidden page may subscribe, but cannot take over system chrome.
  r.chrome.length = 0;
  themeState.setTheme("midnight");
  assert.equal(r.chrome.length, 1);
  assert.equal(first.data.theme.id, "midnight"); assert.equal(second.data.theme.id, "midnight");
  assert.equal(first.data.draft, "未提交的自然观察"); assert.equal(first.data.cursor, "next"); assert.equal(first.data.saving, true);
  assert.equal(calls[0][0], first); assert.equal(calls[0][1], "query");
  assert.equal(calls.length, 3, "theme notifications never rerun business lifecycle handlers");
  const count = first.updates.length;
  first.onUnload(); themeState.setTheme("ocean");
  assert.equal(first.updates.length, count);
  assert.equal(second.data.theme.id, "ocean");
  second.onUnload(); await returned;
});

test("isolated components synchronize once and unsubscribe even when original detach throws", () => {
  const r = runtime(), { withThemeComponent } = r.load("presentation/theme/adapters.js");
  const { themeState } = r.load("presentation/theme/state.js");
  const d = withThemeComponent({ data: { input: "草稿" }, methods: { retained() { return this.data.input; } },
    lifetimes: { attached(arg) { this.attachedArg = arg; }, detached() { throw Error("original detach"); } } });
  const h = r.host(d); d.lifetimes.attached.call(h, "native");
  d.pageLifetimes.show.call(h); d.pageLifetimes.show.call(h);
  const count = h.updates.length; themeState.setTheme("space");
  assert.equal(h.updates.length, count + 1); assert.equal(h.retained(), "草稿"); assert.equal(h.attachedArg, "native");
  assert.throws(() => d.lifetimes.detached.call(h), /original detach/);
  themeState.setTheme("tech"); assert.equal(h.updates.length, count + 1);
});

test("component adapters preserve legacy root lifecycle and native lifetimes precedence", () => {
  const r = runtime(), { withThemeComponent } = r.load("presentation/theme/adapters.js");
  const calls = [], original = { data: { group: "待复习" },
    attached(arg) { calls.push([this.data.group, arg]); }, detached() { calls.push("detach"); } };
  const d = withThemeComponent(original), h = r.host(d);
  d.lifetimes.attached.call(h, "native"); d.lifetimes.detached.call(h);
  assert.deepEqual(calls, [["待复习", "native"], "detach"]);
  const preferred = withThemeComponent({ ...original, lifetimes: { attached() { calls.push("preferred"); } } });
  preferred.lifetimes.attached.call(r.host(preferred));
  assert.deepEqual(calls, [["待复习", "native"], "detach", "preferred"]);
});

test("unknown subject icons use the six fixed local glyphs, with no user-controlled URL", () => {
  const r = runtime(), { iconStyle } = r.load("components/theme-icon/index.js");
  const registry = r.load("presentation/theme/registry.js");
  const expected = { original: "book", garden: "sprout", space: "planet", midnight: "compass", ocean: "shell", tech: "chip" };
  for (const [id, fallback] of Object.entries(expected)) {
    assert.equal(registry.getTheme(id).fallback, fallback);
    assert.equal(iconStyle("自定义<image src=https://invalid>", "primary", id), iconStyle(fallback, "primary", id));
    assert.equal(iconStyle("__proto__", "primary", id), iconStyle(fallback, "primary", id));
    assert.match(iconStyle(fallback, "primary", id), /^background-image:url\("data:image\/svg\+xml,/);
    assert.doesNotMatch(iconStyle(fallback, "primary", id), /https/);
  }
});

test("picker stages choices, cancels without persistence and emits application failures honestly", () => {
  const r = runtime(); r.load("components/theme-picker/index.js");
  const d = r.component(), h = r.host(d), { themeState } = r.load("presentation/theme/state.js");
  d.observers.visible.call(h, true);
  h.choose({ currentTarget: { dataset: { id: "garden" } } });
  assert.equal(themeState.current().id, "original"); assert.equal(r.writes.length, 0);
  h.close(); assert.equal(r.events[0].name, "close");
  d.observers.visible.call(h, true); assert.equal(h.data.selectedId, "original");
  h.apply(); assert.equal(r.writes.length, 0);
  h.choose({ currentTarget: { dataset: { id: "not-a-theme" } } }); assert.equal(h.data.selectedId, "original");
  h.choose({ currentTarget: { dataset: { id: "tech" } } });
  r.wx.setStorageSync = () => { throw Error("full"); }; h.apply();
  assert.equal(themeState.current().id, "tech");
  assert.equal(r.events.at(-1).detail.persisted, false); assert.equal(r.events.at(-1).detail.id, "tech");
});
