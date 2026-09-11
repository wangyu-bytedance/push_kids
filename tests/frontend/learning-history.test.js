const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function harness(entry, request, wxOverrides = {}, extraApi = {}) {
  let page;
  const timers = new Set();
  const app = { globalData: { selectedChildId: "child" }, selectChild(id) { this.globalData.selectedChildId = id; } };
  const wx = { showToast() {}, setNavigationBarTitle() {}, pageScrollTo() {}, navigateBack() {},
    showModal({ success }) { success({ confirm: true }); }, ...wxOverrides };
  const modules = new Map();
  function load(file) {
    if (file.endsWith("/utils/api.js")) return { request, newIdempotencyKey: () => "fixture-key", ...extraApi };
    if (modules.has(file)) return modules.get(file);
    const module = { exports: {} };
    vm.runInNewContext(fs.readFileSync(file, "utf8"), {
      module, require(name) { return load(path.resolve(path.dirname(file), name + ".js")); },
      Page(p) { page = p; }, wx, getApp: () => app,
      setTimeout(fn) { timers.add(fn); return fn; }, clearTimeout(fn) { timers.delete(fn); }
    }, { filename: file });
    modules.set(file, module.exports);
    return module.exports;
  }
  load(path.resolve("apps/miniprogram", entry));
  page.setData = (updates) => {
    for (const [key, value] of Object.entries(updates)) {
      const parts = key.replace(/\[(\d+)\]/g, ".$1").split(".");
      let target = page.data;
      for (const part of parts.slice(0, -1)) target = target[part];
      target[parts.at(-1)] = value;
    }
  };
  return { page, app, wx, timers };
}
const event = (dataset) => ({ currentTarget: { dataset } });
const row = (id) => ({ submission_id: id, state: "confirmed", source: "manual", record_id: id,
  occurred_at: "2026-09-04T16:30:00Z", created_at: "2026-09-05T12:00:00Z", summary: "已确认的加法", subject_name: "数学" });

test("history paginates with bounded rows, restores cursor and does not write", async () => {
  const calls = [];
  const { page } = harness("pages/records/index.js", async (url, options) => {
    calls.push({ url, options });
    const second = url.includes("cursor=page2");
    return { items: Array.from({ length: 20 }, (_, i) => row(`${second ? 'older' : 'recent'}-${i}`)), next_cursor: second ? null : "page2", pending_count: 7 };
  });
  page.data.childId = "child";
  await page.fetchHistory();
  assert.equal(page.data.historyItems[0].day, "2026-09-05");
  assert.equal(page.data.pendingCount, 7);
  await page.historyNextPage();
  // Wait for the async event handler's fetch.
  await Promise.resolve();
  assert.equal(page.data.historyItems.length, 20);
  assert.equal(page.data.historyPage, 2);
  await page.historyPreviousPage();
  assert.equal(page.data.historyItems[0].submission_id, "recent-0");
  assert.ok(calls.every((c) => !c.options || !c.options.method));
});

test("late search response and hidden page cannot replace current history", async () => {
  const pending = [];
  const { page } = harness("pages/records/index.js", () => new Promise((resolve) => pending.push(resolve)));
  page.data.childId = "child";
  const old = page.fetchHistory();
  page.data.historyFilters.q = "new";
  const current = page.fetchHistory(null, 1);
  pending[1]({ items: [row("new")], pending_count: 0 }); await current;
  pending[0]({ items: [row("old")], pending_count: 0 }); await old;
  assert.equal(page.data.historyItems[0].submission_id, "new");
  const hidden = page.fetchHistory(); page.onHide();
  pending[2]({ items: [row("hidden")], pending_count: 0 }); await hidden;
  assert.equal(page.data.historyItems[0].submission_id, "new");
});

test("filter cancellation is read-only, date semantics reset, navigation intent consumed once", async () => {
  const { page, app } = harness("pages/records/index.js", async (url) => url.includes("subjects") ? [] : { items: [], pending_count: 0 });
  page.data.childId = "child";
  page.data.historyFilters.q = "original";
  await page.openHistoryFilters(); page.data.filterDraft.q = "changed"; page.closeHistoryFilters();
  assert.equal(page.data.historyFilters.q, "original");
  page.data.historyFilters.from = "2026-09-01";
  await page.changeHistoryView(event({ view: "pending" }));
  assert.equal(page.data.historyFilters.from, "");
  app.globalData.recordIntent = { childId: "child", view: "history", status: "confirmed", filters: { subject_id: "math" } };
  await page.consumeRecordIntent();
  assert.equal(page.data.historyExpanded, true);
  assert.equal(page.data.historyFilters.subject_id, "math");
  assert.equal(app.globalData.recordIntent, undefined);
  page.data.historyFilters.subject_id = "english";
  await page.consumeRecordIntent();
  assert.equal(page.data.historyFilters.subject_id, "english");
});

test("confirmed and cancelled submissions open read-only and cannot be reconfirmed", async () => {
  for (const state of ["confirmed", "cancelled"]) {
    const calls = [];
    const { page } = harness("pages/submission/confirm.js", async (url, options) => {
      calls.push({ url, options });
      return url.includes("/history/") ? { state, record: state === "confirmed" ? { summary: "家长确认" } : null, knowledge: [], media: [] }
        : { id: "sid", child_id: "child", state, occurred_at: "2026-09-05T00:00:00Z", created_at: "2026-09-05T01:00:00Z" };
    });
    page.data.id = "sid";
    await page.load(); await page.confirmDraft();
    assert.equal(page.data.error, "");
    assert.equal(page.data.readOnly, true);
    assert.equal(page.data.proposal, null);
    assert.ok(calls.every((c) => !c.options));
  }
});

test("viewer sees submitted material without write affordances; conflicts preserve edits", async () => {
  const { page, app } = harness("pages/submission/confirm.js", async (url) => url.includes("/history/") ? { record: null, knowledge: [] } : { state: "pending_confirmation", child_id: "child", occurred_at: "2026-09-05" });
  app.globalData.currentMember = { role: "viewer" };
  await page.load();
  assert.equal(page.data.canWrite, false);
  assert.equal(page.data.readOnly, true);
  const conflict = harness("pages/submission/confirm.js", async () => { const err = new Error("已被确认"); err.statusCode = 409; throw err; }).page;
  conflict.data.subjects = [{ id: "math", name: "数学" }];
  conflict.data.proposal = { subject_name: "数学", summary: "我的编辑", knowledge_points: [{ name: "加法", subject_name: "数学" }] };
  await conflict.confirmDraft();
  assert.equal(conflict.data.conflict, true);
  assert.equal(conflict.data.proposal.summary, "我的编辑");
});

test("record-to-today review intent contains only existing due IDs and does not feedback", () => {
  let switched;
  const { page, app } = harness("pages/submission/confirm.js", () => { throw new Error("Unexpected write"); }, { switchTab({ url }) { switched = url; } });
  page.data.id = "sid"; page.data.submission = { child_id: "child" };
  page.data.reviews = [{ review_id: "due", is_due: true }, { review_id: "later", is_due: false }];
  page.goReview();
  assert.equal(switched, "/pages/today/index");
  assert.deepEqual(Array.from(app.globalData.reviewReturn.reviewIds), ["due"]);
});

test("list permission failure clears protected history", async () => {
  const { page } = harness("pages/records/index.js", async () => { const error = new Error("访问已失效"); error.statusCode = 403; throw error; });
  page.data.childId = "child"; page.data.historyItems = [row("private")];
  await page.fetchHistory();
  assert.equal(page.data.historyItems.length, 0);
  assert.equal(page.data.historyError, "访问已失效");
});

test("pending polling covers off-page jobs and stops in confirmed history or on hide", () => {
  const { page, timers } = harness("pages/records/index.js", async () => ({}));
  page.data.submissions = [{ state: "queued", awaiting_upload: true }];
  page.schedulePoll(); assert.equal(timers.size, 0);
  page.data.pendingProcessing = true;
  page.schedulePoll(); assert.equal(timers.size, 1);
  page.data.historyExpanded = true; page.data.historyView = "confirmed";
  page.schedulePoll(); assert.equal(timers.size, 0);
  page.data.historyView = "pending"; page.schedulePoll();
  page.onHide(); assert.equal(timers.size, 0);
});

test("resuming an upload in detail retains the same submission identity", async () => {
  const calls = [];
  const { page } = harness("pages/submission/confirm.js", async (url, options) => { calls.push({ url, method: options.method }); },
    { chooseMedia({ success }) { success({ tempFiles: [{ tempFilePath: "synthetic-local-path" }] }); } },
    { appendSubmissionMedia: async (id) => calls.push({ appended: id }) });
  page.data.submission = { id: "original", child_id: "child", media_count: 0, awaiting_upload: true };
  page.load = async () => {};
  await page.resumePhotos();
  assert.equal(calls[0].appended, "original");
  assert.equal(calls[1].url, "/submissions/original/finalize");
  assert.equal(page.data.saving, false);
});

test("changing a child cannot move a dirty or uploading form to another child", async () => {
  const { page, app } = harness("pages/records/index.js", async (url) => {
    if (url === "/children") return [{ id: "child", name: "A" }, { id: "other", name: "B" }];
    if (url.includes("history")) return { pending_count: 0 };
    return [];
  }, { showModal({ success }) { success({ confirm: false }); } });
  page.data.childId = "child"; page.data.text = "未提交的内容";
  app.globalData.selectedChildId = "other";
  await page.load();
  assert.equal(page.data.childId, "child");
  assert.equal(page.data.text, "未提交的内容");
  page.data.saving = true;
  await page.changeChild({ detail: { value: 1 } });
  assert.equal(page.data.childId, "child");
  assert.equal(page.data.text, "未提交的内容");
});

test("history is collapsed by default and loads only when expanded", async () => {
  const calls = [];
  const scrolls = [];
  const { page } = harness("pages/records/index.js", async (url) => {
    calls.push(url);
    return { items: [], pending_count: 0, has_processing: false };
  }, { pageScrollTo(options) { scrolls.push(options); } });
  page.data.childId = "child";
  assert.equal(page.data.historyExpanded, false);
  await page.toggleHistory();
  assert.equal(page.data.historyExpanded, true);
  assert.equal(calls.length, 1);
  assert.equal(scrolls.at(-1).selector, "#record-history");
  await page.toggleHistory();
  assert.equal(page.data.historyExpanded, false);
  assert.equal(calls.length, 1);
});

test("explicit new-record intent collapses history and returns to the form", async () => {
  const scrolls = [];
  const { page, app } = harness("pages/records/index.js", async () => ({ items: [], pending_count: 0 }),
    { pageScrollTo(options) { scrolls.push(options); } });
  page.data.childId = "child";
  page.data.historyExpanded = true;
  app.globalData.recordIntent = { childId: "child", view: "new" };
  await page.consumeRecordIntent();
  assert.equal(page.data.historyExpanded, false);
  assert.equal(scrolls.at(-1).scrollTop, 0);
});

test("viewer enters expanded read-only history", async () => {
  const { page, app } = harness("pages/records/index.js", async (url) => {
    if (url === "/children") return [{ id: "child", name: "A" }];
    return { items: [], pending_count: 0, has_processing: false };
  });
  app.globalData.currentMember = { role: "viewer" };
  page.hidden = false;
  await page.load();
  assert.equal(page.data.canWrite, false);
  assert.equal(page.data.historyExpanded, true);
});

test("unified record form rejects empty material and routes text-only submissions without media", async () => {
  const calls = [];
  const toasts = [];
  const { page } = harness("pages/records/index.js", async (url, options) => {
    calls.push({ url, options });
    return { id: "manual-submission" };
  }, { showToast(options) { toasts.push(options); } });
  page.data.childId = "child";
  page.data.date = "2026-09-11";
  page.data.time = "19:57";
  page.load = async () => {};

  await page.save();
  assert.equal(calls.length, 0);
  assert.equal(toasts[0].title, "请添加学习照片或填写学习内容");

  page.data.text = "  今天练习了乘法  ";
  page.data.hasText = true;
  await page.save();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/submissions");
  assert.equal(calls[0].options.data.source, "manual");
  assert.equal(calls[0].options.data.input_text, "今天练习了乘法");
});

test("unified record form keeps optional text on the existing photo upload path", async () => {
  const calls = [];
  let uploaded;
  const { page } = harness("pages/records/index.js", async (url, options) => {
    calls.push({ url, options });
    return { id: "photo-submission" };
  }, {}, {
    uploadSubmission: async (path, data) => {
      uploaded = { path, data };
      return { id: "photo-submission", media_count: 1 };
    },
    appendSubmissionMedia: async () => { throw new Error("unexpected append"); }
  });
  page.data.childId = "child";
  page.data.date = "2026-09-11";
  page.data.time = "19:57";
  page.data.photos = ["local-photo"];
  page.data.text = "照片补充说明";
  page.data.hasText = true;
  page.load = async () => {};

  await page.save();
  assert.equal(uploaded.path, "local-photo");
  assert.equal(uploaded.data.input_text, "照片补充说明");
  assert.equal(calls[0].url, "/submissions/photo-submission/finalize");
});

test("every photo add entry offers camera and album and can append repeated captures", () => {
  const mediaCalls = [];
  const responses = [
    [{ tempFilePath: "camera-1" }],
    [{ tempFilePath: "camera-2" }],
    Array.from({ length: 8 }, (_, index) => ({ tempFilePath: `album-${index + 1}` }))
  ];
  const { page } = harness("pages/records/index.js", async () => ({}), {
    chooseMedia(options) {
      mediaCalls.push(options);
      options.success({ tempFiles: responses.shift() });
    }
  });

  page.addPhotos();
  page.addPhotos();
  page.addPhotos();

  assert.deepEqual(Array.from(page.data.photos), [
    "camera-1", "camera-2", "album-1", "album-2", "album-3",
    "album-4", "album-5", "album-6", "album-7"
  ]);
  assert.deepEqual(mediaCalls.map((call) => call.count), [9, 8, 7]);
  mediaCalls.forEach((call) => assert.deepEqual(Array.from(call.sourceType), ["camera", "album"]));
  page.addPhotos();
  assert.equal(mediaCalls.length, 3);
});

test("photo picker cancellation, empty results and failures preserve the form", () => {
  const toasts = [];
  let mode = "cancel";
  let calls = 0;
  const { page } = harness("pages/records/index.js", async () => ({}), {
    showToast(options) { toasts.push(options); },
    chooseMedia(options) {
      calls += 1;
      if (mode === "empty") options.success({ tempFiles: [] });
      else options.fail({ errMsg: mode === "cancel" ? "chooseMedia:fail cancel" : "chooseMedia:fail auth deny" });
    }
  });
  page.data.photos = ["existing"];
  page.data.text = "保留学习内容";
  page.data.submissionKey = "original-key";

  page.addPhotos();
  mode = "empty";
  page.addPhotos();
  mode = "failure";
  page.addPhotos();

  assert.deepEqual(Array.from(page.data.photos), ["existing"]);
  assert.equal(page.data.text, "保留学习内容");
  assert.equal(page.data.submissionKey, "original-key");
  assert.equal(toasts.length, 1);
  assert.equal(toasts[0].title, "暂时无法选择照片，可继续填写学习内容");
  page.data.saving = true;
  page.addPhotos();
  assert.equal(calls, 3);
});

test("search text travels outside the URL and stays family scoped", async () => {
  let call;
  const { page } = harness("pages/records/index.js", async (url, options) => { call = { url, options }; return { items: [], pending_count: 0 }; });
  page.data.childId = "child"; page.data.searchText = "孩子的学习内容";
  await page.searchHistory();
  assert.ok(!call.url.includes("q="));
  assert.equal(call.options.historyQuery, "孩子的学习内容");
  assert.ok(call.url.startsWith("/children/child/history?"));
});
