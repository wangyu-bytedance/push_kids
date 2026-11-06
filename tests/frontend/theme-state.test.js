const test = require("node:test");
const assert = require("node:assert/strict");
const { createThemeStore, STORAGE_KEY } = require("../../apps/miniprogram/presentation/theme/state");
const registry = require("../../apps/miniprogram/presentation/theme/registry");

function storage(value, fail = "") {
  const writes = [];
  return { writes, getStorageSync(key) { assert.equal(key, STORAGE_KEY); if (fail === "read") throw Error("private payload"); return value; },
    setStorageSync(key, next) { if (fail === "write") throw Error("private payload"); writes.push({ key, value: next }); } };
}

test("every registered theme restores a small versioned display preference", () => {
  for (const theme of registry.listThemes()) {
    const store = createThemeStore(storage({ version: 1, id: theme.id }));
    assert.equal(store.initialize().id, theme.id);
    assert.equal(store.current().id, theme.id);
  }
});
test("invalid, corrupt or unreadable preference restores original without writing", () => {
  for (const value of [undefined, "", [], "midnight", 123, { version: 1, id: "__proto__" }, { version: 2, id: "ocean" }]) {
    const wx = storage(value); const store = createThemeStore(wx);
    assert.equal(store.initialize().id, "original");
    assert.equal(wx.writes.length, 0);
  }
  assert.equal(createThemeStore(storage(null, "read")).initialize().id, "original");
});
test("selection persists once, notifies live consumers and ignores invalid or repeated IDs", () => {
  const wx = storage(null), store = createThemeStore(wx), seen = [];
  store.initialize();
  const stop = store.subscribe((value) => seen.push(value.id));
  assert.deepEqual(store.setTheme("ocean"), { id: "ocean", persisted: true });
  store.setTheme("ocean"); store.setTheme("../remote"); store.setTheme(null);
  assert.deepEqual(seen, ["ocean"]);
  assert.deepEqual(wx.writes, [{ key: STORAGE_KEY, value: { version: 1, id: "ocean" } }]);
  assert.ok(JSON.stringify(wx.writes[0].value).length < 256);
  stop(); store.setTheme("garden");
  assert.deepEqual(seen, ["ocean"]);
});
test("failed persistence applies only this session and initialize cannot overwrite it", () => {
  const store = createThemeStore(storage({ version: 1, id: "space" }, "write")), seen = [];
  store.initialize(); store.subscribe((value) => seen.push(value.id));
  assert.deepEqual(store.setTheme("midnight"), { id: "midnight", persisted: false });
  assert.equal(store.initialize().id, "midnight");
  assert.deepEqual(seen, ["midnight"]);
  assert.equal(store.setTheme("tech").id, "tech");
  assert.deepEqual(seen, ["midnight", "tech"]);
});
