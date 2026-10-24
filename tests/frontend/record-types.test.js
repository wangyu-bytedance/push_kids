const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const event = (type) => ({ currentTarget: { dataset: { type } } });
const tick = () => new Promise((resolve) => setImmediate(resolve));

function learningEntry(entry, method) {
  const calls = [];
  const loaded = records(async (url, options) => {
    calls.push({ url, options });
    if (url === "/children") return [{ id: "child", name: "合成孩子", active: true }];
    return { items: [], pending_count: 0, has_processing: false };
  });
  loaded.page.setData({ childId: "child", recordType: "travel" });
  const caller = loadPage(entry, async () => [], { wx: {
    switchTab({ url }) { assert.equal(url, "/pages/records/index"); loaded.page.onShow(); }
  } });
  caller.app.globalData = loaded.app.globalData;
  caller.page.setData({ childId: "child" });
  return { ...loaded, calls, enter: () => caller.page[method]() };
}

for (const [entry, method] of [["pages/today/index.js", "recordLearning"], ["pages/reports/index.js", "goRecord"]]) {
  test(`${method} uses the real entry, learning load and intent consumption after travel`, async () => {
    const { page: p, app, calls, enter } = learningEntry(entry, method);
    let guards = 0;
    p.selectComponent = () => ({ canLeave: async () => { guards++; return true; } });
    enter(); await tick(); await tick();
    assert.equal(p.data.recordType, "learning");
    assert.equal(p.data.loading, false);
    assert.equal(p.data.childId, "child");
    assert.equal(app.globalData.recordIntent, undefined);
    assert.equal(guards, 1);
    assert.ok(calls.some(({ url }) => url === "/children"));
    assert.ok(calls.every(({ options }) => !options || !options.method || options.method === "GET"));
  });
}

test("a new learning entry resumes after a stale leave guard finishes", async () => {
  const { page: p, app, enter } = learningEntry("pages/today/index.js", "recordLearning");
  let finish, guards = 0;
  p.selectComponent = () => ({ canLeave: () => ++guards === 1
    ? new Promise((resolve) => { finish = resolve; }) : Promise.resolve(true) });
  const old = p.selectRecordType(event("learning"));
  p.onHide(); enter();
  finish(true); await old; await tick(); await tick();
  assert.equal(p.data.recordType, "learning");
  assert.equal(app.globalData.recordIntent, undefined);
  assert.equal(p.data.recordSwitching, false);
  assert.equal(guards, 2);
});

function records(request = async () => []) {
  const loaded = loadPage("pages/records/index.js", request);
  loaded.page.pageVisible = true;
  loaded.page.setData({ loading: false, childId: "original", children: [{ id: "original", name: "合成孩子" }] });
  return loaded;
}

test("type round trip preserves the complete unsent learning form and original child", async () => {
  const { page: p } = records();
  let cancels = 0, resumes = 0;
  p.voiceController = { cancel() { cancels++; } };
  p.load = async () => { resumes++; };
  p.selectComponent = () => ({ canLeave: async () => true });
  p.setData({ text: "未提交内容", hasText: true, photos: ["private-local-file"], date: "2020-01-01", time: "12:30", submissionKey: "stable-key" });
  const before = JSON.stringify(p.data);
  p.openRecordTypes();
  await p.selectRecordType(event("travel"));
  assert.equal(p.data.recordType, "travel");
  assert.equal(p.data.travelChildId, "original");
  assert.equal(p.hidden, true);
  p.travelContextChanged({ detail: { children: [{ id: "archived", label: "已归档孩子" }], childIndex: 0 } });
  await p.selectRecordType(event("learning"));
  await tick();
  const old = JSON.parse(before);
  for (const key of ["text", "hasText", "photos", "date", "time", "childId", "submissionKey"]) assert.equal(JSON.stringify(p.data[key]), JSON.stringify(old[key]), key);
  assert.equal(cancels, 1);
  assert.equal(resumes, 1);
  assert.equal(p.hidden, false);
});

test("upload, cancelled travel edits and unknown types cannot switch the record domain", async () => {
  const { page: p } = records();
  p.setData({ saving: true });
  await p.selectRecordType(event("travel"));
  assert.equal(p.data.recordType, "learning");
  p.setData({ saving: false, recordType: "travel", recordTypeOpen: true });
  p.selectComponent = () => ({ canLeave: async () => false });
  await p.selectRecordType(event("learning"));
  assert.equal(p.data.recordType, "travel");
  assert.equal(p.data.recordTypeOpen, false);
  await p.selectRecordType(event("future-plugin"));
  assert.equal(p.data.recordType, "travel");
  await p.selectRecordType(event("travel"));
  assert.equal(p.data.recordTypeOpen, false);
});

test("a pending leave confirmation cannot switch after the page hides", async () => {
  const { page: p } = records();
  let approve;
  p.setData({ recordType: "travel", recordTypeOpen: true });
  p.selectComponent = () => ({ canLeave: () => new Promise((resolve) => { approve = resolve; }) });
  const pending = p.selectRecordType(event("learning"));
  p.onHide();
  approve(true);
  await pending;
  assert.equal(p.data.recordType, "travel");
  assert.equal(p.data.recordTypeOpen, false);
});

test("late learning reads and polling stop when entering travel; travel owns refresh and paging", async () => {
  let resolveProfiles;
  const { page: p, timers } = records(() => new Promise((resolve) => { resolveProfiles = resolve; }));
  p.hidden = false;
  const pending = p.load();
  p.setData({ pendingProcessing: true });
  p.schedulePoll();
  assert.equal(timers.size, 1);
  await p.selectRecordType(event("travel"));
  resolveProfiles([{ id: "late-child", name: "过期响应" }]);
  await pending;
  assert.equal(p.data.childId, "original");
  assert.equal(timers.size, 0);
  let refresh = 0, more = 0;
  p.selectComponent = () => ({ onPullDownRefresh() { refresh++; }, onReachBottom() { more++; } });
  await p.onPullDownRefresh(); await p.onReachBottom(); p.onShow();
  assert.equal(refresh, 1); assert.equal(more, 1);
  assert.equal(p.data.childId, "original");
});

test("embedded and standalone footprints share methods, with isolated controller state and cleanup", async () => {
  const { exports: createController } = loadPage("pages/footprints/controller.js", async () => []);
  const a = createController(), b = createController();
  a.data.visits.push({ id: "only-a" });
  assert.equal(b.data.visits.length, 0);
  const { page: c, timers } = loadPage("pages/footprints/embedded.js", async () => [], { api: { removePreview() {} } });
  Object.assign(c, c.methods);
  c.triggerEvent = () => {};
  c.setData({ saving: true });
  assert.equal(await c.canLeave(), false);
  c.setData({ saving: false, mode: "playback", playback: [{ id: "point", latitude: 1, longitude: 2 }] });
  c.togglePlayback(); assert.equal(timers.size, 1);
  c.observers.menuOpen.call(c, true); assert.equal(c.data.playing, false);
  c.togglePlayback(); c.lifetimes.detached.call(c);
  assert.equal(timers.size, 0); assert.equal(c.hidden, true);
});

test("late consent persistence cannot open the album after travel is removed", async () => {
  let finish, opened = 0;
  const { page: p } = loadPage("pages/footprints/index.js", () => new Promise((resolve) => { finish = resolve; }), {
    wx: { chooseMedia() { opened++; } }, api: { removePreview() {} }
  });
  p.sequence = 1; p.hidden = false; p.setData({ photoConsent: true });
  const pending = p.choosePhotos();
  p.onHide(); finish({}); await pending;
  assert.equal(opened, 0);
});

test("explicit learning intents leave travel through its guard; ordinary tab returns stay travel", async () => {
  const { page: p, app } = records();
  let resumes = 0, allowed = false;
  p.load = async () => { resumes++; delete app.globalData.recordIntent; };
  p.selectComponent = () => ({ canLeave: async () => allowed });
  p.setData({ recordType: "travel" });
  p.onShow(); assert.equal(resumes, 0);
  app.globalData.recordIntent = { view: "new" };
  await p.onShow();
  assert.equal(p.data.recordType, "travel"); assert.ok(app.globalData.recordIntent);
  allowed = true;
  await p.onShow(); await tick();
  assert.equal(p.data.recordType, "learning"); assert.equal(resumes, 1);
});

test("selecting an older archived profile keeps the visible picker aligned to that child", async () => {
  const { page: p } = loadPage("pages/footprints/index.js", async () => [], {
    wx: { showActionSheet({ success }) { success({ tapIndex: 0 }); } }, api: { removePreview() {} }
  });
  p.sequence = 1; p.hidden = false; p.load = async () => {};
  p.setData({ childId: "active", childIndex: 0, children: [{ id: "active" }],
    allChildren: [{ id: "archived", active: false }, { id: "active", active: true }] });
  await p.showArchived();
  assert.equal(p.data.childId, "archived"); assert.equal(p.data.childIndex, 0);
  assert.equal(p.data.children[p.data.childIndex].id, p.data.childId);
});

test("an upload remains protected across backgrounding until its outstanding request terminates", async () => {
  let finish;
  const { page: c } = loadPage("pages/footprints/embedded.js", () => new Promise((resolve) => { finish = resolve; }), { api: { removePreview() {} } });
  Object.assign(c, c.methods);
  c.sequence = 1; c.hidden = false; c.pendingFiles = ["private-local-file"];
  const pending = c.uploadBatch();
  c.pageLifetimes.hide.call(c);
  assert.equal(c.data.saving, true);
  assert.equal(await c.canLeave(), false);
  // A hidden upload finishes no further files; the existing retry context survives.
  finish({ id: "synthetic-batch", photos: [{ id: "synthetic-photo" }] });
  await pending;
  assert.equal(c.data.saving, false); assert.equal(c.pendingFiles.length, 1);
  assert.equal(await c.canLeave(), true);
});

test("type dropdown keeps the tab bar visible; photo sheets hide it until close or page departure", () => {
  const { page: p } = records();
  const bar = { setData(value) { this.value = value.recordOverlayVisible; } };
  p.getTabBar = () => bar;
  p.openRecordTypes(); assert.equal(bar.value, false);
  assert.equal(p.data.recordTypeOpen, true);
  p.openRecordTypes(); assert.equal(p.data.recordTypeOpen, false);
  p.openRecordTypes(); p.onPageScroll({ scrollTop: 10 }); assert.equal(p.data.recordTypeOpen, false);
  p.closeRecordTypes(); assert.equal(bar.value, false);
  p.travelOverlayChanged({ detail: { open: true } }); assert.equal(bar.value, true);
  p.onHide(); assert.equal(bar.value, false);
  p.setData({ recordType: "travel" }); p.onShow(); assert.equal(bar.value, true);
  p.travelOverlayChanged({ detail: { open: false } }); assert.equal(bar.value, false);
});

test("a cancelled current leave guard closes the menu and never retries the pending intent", async () => {
  const { page: p, app } = records();
  let guards = 0;
  p.setData({ recordType: "travel", recordTypeOpen: true });
  app.globalData.recordIntent = { view: "new", childId: "original" };
  p.selectComponent = () => ({ canLeave: async () => {
    guards++; assert.equal(p.data.recordTypeOpen, false); return false;
  } });
  await p.onShow(); await tick();
  assert.equal(guards, 1);
  assert.equal(p.data.recordType, "travel");
  assert.ok(app.globalData.recordIntent);
});

test("travel child labels retain archive context while gaining the shared avatar", () => {
  const { page: p } = records();
  p.setData({ recordType: "travel" });
  p.travelContextChanged({ detail: { children: [{ id: "archived", name: "合成孩子", label: "合成孩子（已归档）", active: false }], childIndex: 0 } });
  assert.equal(p.data.travelChildren[0].label, "合成孩子（已归档）");
  assert.equal(p.data.travelChildren[0].avatar, "合");
});
