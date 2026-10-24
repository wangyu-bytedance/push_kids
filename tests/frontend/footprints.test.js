const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

const event = (dataset, value) => ({ currentTarget: { dataset }, detail: { value } });
function page(request = async () => ({}), options = {}) {
  const loaded = loadPage("pages/footprints/index.js", request, {
    ...options, api: { removePreview() {}, downloadPreview: async () => "/tmp/synthetic-preview", ...(options.api || {}) }
  });
  loaded.page.sequence = 1;
  loaded.page.hidden = false;
  loaded.page.setData({ childId: "child", child: { id: "child", active: true }, loading: false });
  return loaded;
}

test("unknown capture date and timezone stay unknown", () => {
  const { exports: presentation } = loadPage("pages/footprints/presentation.js", () => {});
  assert.equal(presentation.photoView({}).dateLabel, "待补日期");
  const values = presentation.correction(presentation.editValues({ local_date: "2020-01-01" }));
  assert.equal(values.local_time, null);
  assert.equal(values.offset_minutes, null);
});

test("draft capture fields can be cleared but formal dates remain required", () => {
  const { page: p } = page();
  p.setData({ editing: { state: "ready" }, form: { local_date: "2024-01-01", local_time: "10:00:00", offset_minutes: 480 } });
  p.clearCaptureField(event({ field: "local_date" }));
  assert.equal(p.data.form.local_date, "");
  assert.equal(p.data.form.offset_minutes, null);
  p.setData({ editing: { state: "confirmed" }, form: { local_date: "2024-01-01", local_time: "10:00:00" } });
  p.clearCaptureField(event({ field: "local_date" }));
  assert.equal(p.data.form.local_date, "2024-01-01");
  p.clearCaptureField(event({ field: "local_time" }));
  assert.equal(p.data.form.local_time, "");
});

test("draft paging stops first-page polling and preserves selected rows", async () => {
  const { page: p, timers } = page(async () => ({ items: [{ id: "second", job_state: "queued" }], next_cursor: null }));
  p.setData({ sheet: "review", drafts: [{ id: "first", selected: true, job_state: "queued" }], draftsCursor: "next", selectedCount: 1 });
  p.pollDrafts();
  await p.moreDrafts();
  await p.refreshDrafts();
  assert.equal(p.data.drafts.length, 2);
  assert.equal(p.data.drafts[0].selected, true);
  assert.equal(p.data.selectedCount, 1);
  assert.equal(timers.size, 0);
});

test("confirmation blocks missing date and keeps only selected versions", async () => {
  const calls = [];
  const { page: p } = page(async (url, options) => { calls.push({ url, options }); return {}; });
  p.refresh = async () => {};
  p.setData({ drafts: [{ id: "a", import_id: "batch", selected: true, version: 3, has_display: true }] });
  p.askConfirm();
  assert.match(p.data.sheetError, /拍摄日期/);
  p.data.drafts[0].local_date = "2024-01-01";
  p.askConfirm();
  assert.equal(p.data.sheet, "confirm");
  await p.confirmSelected();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].options.data.photos[0].version, 3);
  assert.equal(calls[0].options.data.confirm_actual_visit, true);
});

test("playback changes the native camera overseas and pauses on hide", () => {
  const { page: p, timers } = page();
  p.setData({ playback: [{ id: "a", latitude: 39.9, longitude: 116.4 },
    { id: "b", latitude: 48.8, longitude: 2.3 }] });
  p.focusPlayback(1);
  assert.equal(p.data.mapLongitude, 2.3);
  assert.equal(p.data.polyline[0].dottedLine, true);
  p.togglePlayback();
  assert.equal(p.data.playing, true);
  p.onHide();
  assert.equal(p.data.playing, false);
  assert.equal(timers.size, 0);
});

test("late child response cannot overwrite another child's view", async () => {
  let resolve;
  const pending = new Promise((done) => { resolve = done; });
  const { page: p } = page((url) => url.includes("summary") ? Promise.resolve({ photos: 10 }) : pending);
  const request = p.refresh(1);
  p.sequence = 2;
  resolve({ items: [{ id: "stale", photos: [] }] });
  await request;
  assert.equal(p.data.visits.length, 0);
});

test("all footprint reads use the current child's complete history, even with obsolete date state", async () => {
  const calls = [];
  const { page: p } = page(async (url) => {
    calls.push(url);
    return url.includes("/map?") ? { items: [], bounds: [73, 18, 136, 54] }
      : { items: [], revision: 1, next_cursor: "next" };
  });
  p.setData({ start: "2024-01-01", end: "2024-02-01" });
  await p.refresh();
  await p.changeMode(event({ mode: "lit" }));
  p.setData({ mapData: { items: [{ id: 1, place_key: "place" }] } });
  await p.mapTap({ detail: { markerId: 1 } });
  await p.morePlaceVisits();
  await p.changeMode(event({ mode: "playback" }));
  await p.nextPlaybackPage();
  assert.ok(calls.length >= 6);
  assert.ok(calls.every((url) => url.includes("child_id=child") && !/[?&](start|end)=/.test(url)));
});

const visitRows = (start, count) => Array.from({ length: count }, (_, index) => ({ id: `visit-${start + index}`, photos: [] }));

test("timeline traverses beyond 100 using bounded windows, explicit replacement and retryable cursors", async () => {
  const calls = [], removed = [], scrolls = [];
  let fail = true;
  const { page: p } = page(async (url) => {
    calls.push(url);
    if (fail) { fail = false; throw Error("暂时离线"); }
    return { items: visitRows(100, 20), next_cursor: "after-120" };
  }, { api: { removePreview: (url) => removed.push(url) }, wx: {
    createSelectorQuery() {
      return { in() { return this; }, select() { return this; }, boundingClientRect() { return this; },
        selectViewport() { return this; }, scrollOffset() { return this; }, exec(done) { done([{ top: -300 }, { scrollTop: 800 }]); } };
    }, pageScrollTo: (value) => scrolls.push(value)
  } });
  p.setData({ visits: visitRows(0, 100), nextCursor: "after-100" });
  p.previewFiles = ["old-preview"];
  await p.onReachBottom(); assert.equal(calls.length, 0);
  await p.moreVisits();
  assert.equal(p.data.visits.length, 100); assert.equal(p.data.nextCursor, "after-100");
  assert.equal(removed.length, 0); assert.equal(p.data.loadingMore, false);
  await p.moreVisits();
  assert.equal(calls[0], calls[1]);
  assert.match(calls[1], /cursor=after-100&limit=20/);
  assert.equal(p.data.visits.length, 20); assert.equal(p.data.visits[0].id, "visit-100");
  assert.equal(p.data.nextCursor, "after-120"); assert.deepEqual(removed, ["old-preview"]);
  assert.equal(scrolls[0].scrollTop, 500);
});

test("timeline appends only the remaining capacity within its current window", async () => {
  const calls = [];
  const { page: p } = page(async (url) => { calls.push(url); return { items: visitRows(95, 5), next_cursor: "after-100" }; });
  p.setData({ visits: visitRows(0, 95), nextCursor: "after-95" });
  await p.onReachBottom();
  assert.equal(p.data.visits.length, 100); assert.match(calls[0], /limit=5/);
  await p.onReachBottom(); assert.equal(calls.length, 1);
});

test("place visits replace a full window, reset its scroll anchor and retry the same cursor on failure", async () => {
  const calls = []; let finish;
  const { page: p } = page((url) => { calls.push(url); return new Promise((resolve, reject) => { finish = { resolve, reject }; }); });
  p.setData({ sheet: "place", placeKey: "place", placeVisits: visitRows(0, 100), placeCursor: "after-100" });
  const failed = p.morePlaceVisits(); await p.morePlaceVisits(); assert.equal(calls.length, 1);
  finish.reject(Error("暂时离线")); await failed;
  assert.equal(p.data.placeVisits.length, 100); assert.equal(p.data.loadingPlaceMore, false);
  const next = p.morePlaceVisits(); finish.resolve({ items: visitRows(100, 20), next_cursor: "after-120" }); await next;
  assert.equal(calls[0], calls[1]); assert.match(calls[1], /place=place&cursor=after-100&limit=20/);
  assert.equal(p.data.placeVisits.length, 20); assert.equal(p.data.placeVisits[0].id, "visit-100");
  assert.equal(p.data.placeScrollTarget, "fp-place-start-1");
  const late = p.morePlaceVisits(); p.setData({ sheet: "photo" });
  finish.resolve({ items: visitRows(120, 20) }); await late;
  assert.equal(p.data.placeVisits.length, 20);
});

test("a replaced timeline discards late preview files and stops requesting the old window", async () => {
  const removed = [], calls = []; let finish;
  const { page: p } = page(async (url) => { calls.push(url); return {}; }, {
    api: { removePreview: (url) => removed.push(url), downloadPreview: () => new Promise((resolve) => { finish = resolve; }) }
  });
  const pending = p.fillPreviews([{ id: "old", has_display: true }, { id: "later-old", has_display: true }], "visits");
  await new Promise((resolve) => setImmediate(resolve));
  p.releasePreviews(); p.setData({ visits: visitRows(100, 20) });
  finish("late-preview"); await pending;
  assert.deepEqual(removed, ["late-preview"]); assert.equal(calls.length, 1);
  assert.equal(p.previewFiles.length, 0); assert.equal(p.data.visits[0].id, "visit-100");
});

test("archived and viewer profiles cannot start new intake", async () => {
  const { page: p } = page();
  p.setData({ child: { active: false } }); await p.beginImport(); p.manualEntry();
  assert.equal(p.data.sheet, "");
  p.setData({ child: { active: true }, canWrite: false }); await p.beginImport(); p.manualEntry();
  assert.equal(p.data.sheet, "");
});

test("the import entry waits for active saving; consent and album cancellation create no footprint facts", async () => {
  const calls = []; let picks = 0;
  const { page: p } = page(async (url, options) => { calls.push({ url, options }); return {}; }, {
    wx: { chooseMedia({ fail }) { picks++; fail({ errMsg: "chooseMedia:fail cancel" }); } }
  });
  p.setData({ saving: true }); await p.beginImport(); assert.equal(p.data.sheet, "");
  p.setData({ saving: false }); await p.beginImport();
  assert.equal(p.data.sheet, "consent"); assert.equal(p.data.photoConsent, false); assert.equal(calls.length, 0);
  await p.choosePhotos(); assert.equal(picks, 0); assert.equal(calls.length, 0);
  p.consentChange({ detail: { value: ["photos"] } }); await p.choosePhotos();
  assert.equal(picks, 1); assert.equal(p.data.hasPendingUpload, false); assert.equal(p.pendingFiles, undefined);
  assert.ok(calls.every(({ url }) => url === "/footprints/preferences"));
  assert.equal(p.data.sheet, "consent"); assert.match(p.data.sheetError, /取消/);
});

test("gallery uses bounded pages and can return to the previous page", async () => {
  const { page: p } = page(async (url) => url.includes("cursor=next")
    ? { items: [{ id: "second" }], next_cursor: null }
    : { items: [{ id: "first" }], next_cursor: "next" });
  await p.openVisit(event({ id: "visit" }));
  await p.nextPhoto(event({ delta: 1 }));
  assert.equal(p.data.editing.id, "second");
  assert.equal(p.data.hasPreviousPhotoPage, true);
  await p.nextPhoto(event({ delta: -1 }));
  assert.equal(p.data.editing.id, "first");
});

test("edit failure preserves values and unsaved close respects cancellation", async () => {
  const { page: p } = page(async () => { throw Error("版本冲突，请刷新"); }, {
    wx: { showModal({ success }) { success({ confirm: false }); } }
  });
  p.setData({ sheet: "edit", editing: { id: "photo", version: 2 }, form: { place_name: "待核对公园" } });
  await p.saveEdit();
  assert.equal(p.data.form.place_name, "待核对公园");
  assert.match(p.data.sheetError, /版本冲突/);
  await p.closeSheet();
  assert.equal(p.data.sheet, "edit");
});

test("first-file upload failure retains a retryable batch", async () => {
  const { page: p } = page(async (url) => {
    if (url.endsWith("/imports")) return { id: "batch", photos: [{ id: "a" }] };
    return { items: [] };
  }, { wx: { getFileInfo({ fail }) { fail({ errMsg: "synthetic failure" }); } } });
  p.pendingFiles = ["/tmp/synthetic"];
  p.pendingBatchKey = "stable-key";
  p.setData({ hasPendingUpload: true });
  await p.uploadBatch();
  assert.equal(p.data.hasPendingUpload, true);
  assert.equal(p.data.importProgress, 0);
  assert.equal(p.pendingBatchKey, "stable-key");
  assert.equal(p.data.sheet, "review");
});

test("footprint actions follow permission and archive availability without one-item menus", async () => {
  const cases = [
    { canWrite: true, archived: false, target: "settings", menus: [] },
    { canWrite: false, archived: false, target: "", menus: [] },
    { canWrite: false, archived: true, target: "archive", menus: [["归档一"]] },
    { canWrite: true, archived: true, target: "settings", menus: [["足迹设置", "已归档孩子"]] }
  ];
  for (const value of cases) {
    const menus = [];
    const { page: p } = page(undefined, { wx: { showActionSheet({ itemList, success }) {
      menus.push(Array.from(itemList)); success({ tapIndex: 0 });
    } } });
    p.setData({ canWrite: value.canWrite, allChildren: value.archived ? [{ id: "archive", name: "归档一", active: false }] : [] });
    p.load = async () => {};
    await p.openFootprintActions();
    assert.deepEqual(menus, value.menus);
    assert.equal(value.target === "settings" ? p.data.sheet : value.target === "archive" ? p.data.childId : p.data.sheet, value.target);
    assert.equal(p.nativeMenuOpen, false);
  }
});

test("native action cancellation and a late selection leave context untouched", async () => {
  let menu;
  const { page: p } = page(undefined, { wx: { showActionSheet(value) { menu = value; } } });
  p.setData({ allChildren: [{ id: "archive", name: "归档", active: false }] });
  const cancelled = p.openFootprintActions();
  await p.openFootprintActions(); // No duplicate native overlays.
  menu.fail({ errMsg: "showActionSheet:fail cancel" }); await cancelled;
  assert.equal(p.data.childId, "child"); assert.equal(p.data.sheet, "");
  const late = p.openFootprintActions(); p.onHide(); menu.success({ tapIndex: 0 }); await late;
  assert.equal(p.data.sheet, ""); assert.equal(p.nativeMenuOpen, false);
});

test("archived selection cancellation preserves the current child and unsaved input", async () => {
  const { page: p } = page(undefined, { wx: { showActionSheet({ fail }) { fail({ errMsg: "cancel" }); } } });
  p.setData({ sheet: "edit", form: { place_name: "未保存公园" }, allChildren: [{ id: "archive", name: "归档", active: false }] });
  await p.showArchived();
  assert.equal(p.data.childId, "child"); assert.equal(p.data.form.place_name, "未保存公园");
  assert.equal(p.data.archivedVisible, false); assert.equal(p.data.sheet, "edit");
});

test("archived selection uses the existing discard guard before changing children", async () => {
  let confirm = false, loads = 0;
  const { page: p } = page(undefined, { wx: {
    showActionSheet({ success }) { success({ tapIndex: 0 }); },
    showModal({ success }) { success({ confirm }); }
  } });
  p.setData({ sheet: "edit", form: { place_name: "未保存" }, allChildren: [{ id: "archive", name: "归档", active: false }] });
  p.pendingFiles = ["synthetic"];
  p.load = async () => { loads++; };
  await p.showArchived();
  assert.equal(p.data.childId, "child"); assert.equal(p.pendingFiles.length, 1); assert.equal(loads, 0);
  confirm = true; await p.showArchived();
  assert.equal(p.data.childId, "archive"); assert.equal(p.data.archivedVisible, true);
  assert.equal(p.data.child.active, false); assert.equal(p.pendingFiles, null); assert.equal(loads, 1);
  await p.beginImport(); p.manualEntry(); assert.equal(p.data.sheet, "");
});

test("every archived child is reachable through bounded native pages in either direction", async () => {
  const menus = [], selections = [4, 4, 4, 0]; // Next, previous, next, choose archive 5.
  const { page: p } = page(undefined, { wx: { showActionSheet({ itemList, success }) {
    menus.push(Array.from(itemList)); success({ tapIndex: selections.shift() });
  } } });
  p.setData({ allChildren: Array.from({ length: 10 }, (_, i) => ({ id: `archive-${i}`, name: `归档${i}`, active: false })) });
  p.load = async () => {};
  await p.showArchived();
  assert.deepEqual(menus.map((menu) => menu.length), [5, 6, 5, 6]);
  assert.equal(p.data.childId, "archive-4"); assert.equal(p.archivePickerOpen, false);
  const tail = page(undefined, { wx: { showActionSheet({ itemList, success }) {
    assert.ok(itemList.length <= 6); success({ tapIndex: itemList.includes("下一页") ? itemList.length - 1 : 1 });
  } } }).page;
  tail.setData({ allChildren: p.data.allChildren }); tail.load = async () => {};
  await tail.showArchived(); assert.equal(tail.data.childId, "archive-9");
});

test("profile loading derives archive availability and permission denial removes it", async () => {
  const { page: p } = page(async (url) => url.startsWith("/children")
    ? [{ id: "child", name: "当前", active: true }, { id: "archive", name: "归档", active: false }]
    : url.includes("preferences") ? { ai_enabled: false } : { items: [] });
  await p.load(); assert.equal(p.data.hasArchivedChildren, true); assert.equal(p.data.children.length, 1);
  p.handleError({ statusCode: 403, message: "无访问权限" });
  assert.equal(p.data.hasArchivedChildren, false); assert.equal(p.data.allChildren.length, 0);
});

test("settings failure keeps the chosen value and retry saves the same preference", async () => {
  const calls = []; let fail = true;
  const { page: p } = page(async (url, options) => {
    calls.push({ url, options }); if (fail) throw Error("网络不可用，请重试"); return {};
  });
  p.openSettings(); p.aiChange(event({}, true)); await p.saveSettings();
  assert.equal(p.data.sheet, "settings"); assert.equal(p.data.aiEnabled, true);
  assert.match(p.data.sheetError, /重试/); assert.equal(p.data.saving, false);
  fail = false; await p.saveSettings();
  assert.equal(p.data.sheet, ""); assert.equal(p.data.aiEnabled, true);
  assert.equal(calls.length, 2); assert.deepEqual(calls[0], calls[1]);
});

for (const pendingDownload of [false, true]) test(`late timeline window preserves ${pendingDownload ? "pending" : "loaded"} photo sheet previews`, async () => {
  let finishWindow, finishDownload; const removed = [];
  const { page: p } = page((url) => {
    if (url.includes("/visits?")) return new Promise((resolve) => { finishWindow = resolve; });
    if (url.includes("/photos?")) return Promise.resolve({ items: [{ id: "photo", has_display: true }], next_cursor: null });
    return Promise.resolve({});
  }, { api: { removePreview: (url) => removed.push(url), downloadPreview: pendingDownload
    ? () => new Promise((resolve) => { finishDownload = resolve; }) : async () => "photo-preview" } });
  p.setData({ visits: visitRows(0, 100), nextCursor: "after-100" });
  const window = p.moreVisits();
  await p.openVisit(event({ id: "visit-0" }));
  await new Promise((resolve) => setImmediate(resolve));
  finishWindow({ items: visitRows(100, 20), next_cursor: "after-120" }); await window;
  if (pendingDownload) finishDownload("photo-preview");
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(p.data.sheet, "photo"); assert.equal(p.data.photoList[0].previewUrl, "photo-preview");
  assert.deepEqual(removed, []); assert.equal(p.data.visits.length, 100);
  assert.equal(p.data.nextCursor, "after-100"); assert.equal(p.data.loadingMore, false);
});

test("superseding a timeline request resets busy state and ignores its late failure", async () => {
  let rejectWindow, finishProfiles, pageRequests = 0;
  const { page: p } = page((url) => {
    if (url.includes("cursor=")) { pageRequests++; return new Promise((_, reject) => { rejectWindow = reject; }); }
    if (url.startsWith("/children")) return new Promise((resolve) => { finishProfiles = resolve; });
    return Promise.resolve({ items: [] });
  });
  p.setData({ visits: visitRows(0, 100), nextCursor: "after-100" });
  const window = p.moreVisits(), refresh = p.load();
  assert.equal(p.data.loadingMore, false);
  await p.moreVisits(); assert.equal(pageRequests, 1); // Refresh owns the current window until it settles.
  finishProfiles([{ id: "child", name: "当前" }]); await refresh;
  rejectWindow(Error("过期失败")); await window; assert.equal(p.data.error, "");
});
