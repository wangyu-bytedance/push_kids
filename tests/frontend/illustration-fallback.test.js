const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

test("settings decorative failures leave daily task edits and permissions untouched", () => {
  let requests = 0;
  const { page } = loadPage("pages/settings/index.js", () => { requests += 1; });
  page.setData({ dailyTaskName: "保留任务", dailyTaskMinutes: "20", showDailyTaskForm: true, savingDailyTask: true, canWrite: false });
  const before = { ...page.data };
  for (const art of ["learning", "activity", "travel", "unexpected"]) page.onIllustrationError({ currentTarget: { dataset: { art } } });
  assert.deepEqual({ ...page.data }, { ...before, learningArtFailed: true, activityArtFailed: true, travelArtFailed: true });
  assert.equal(requests, 0);
});

test("report decorative failure preserves statistics and disclosure state", () => {
  let requests = 0;
  const { page } = loadPage("pages/reports/index.js", () => { requests += 1; });
  page.setData({ report: { id: "synthetic" }, days: 30, historyExpanded: true, planExpanded: true });
  const before = { ...page.data };
  page.onIllustrationError();
  assert.deepEqual({ ...page.data }, { ...before, introArtFailed: true });
  assert.equal(requests, 0);
});

test("record illustration failures preserve form, upload state and permission without requests", () => {
  let requests = 0;
  const { page } = loadPage("pages/records/index.js", () => { requests += 1; });
  page.setData({ childId: "synthetic", text: "保留输入", photos: ["local-photo"], saving: true, canWrite: false });
  const before = { ...page.data };
  for (const art of ["intro", "upload", "unexpected"]) {
    page.onIllustrationError({ currentTarget: { dataset: { art } } });
  }
  assert.deepEqual({ ...page.data }, { ...before, introArtFailed: true, uploadArtFailed: true });
  assert.equal(requests, 0);
});

test("calendar illustration failure preserves selected date, items and open editor without requests", () => {
  let requests = 0;
  const { page } = loadPage("pages/calendar/index.js", () => { requests += 1; });
  page.setData({ selectedDay: "2026-10-13", items: [{ id: "synthetic" }], showEditor: true, error: "保留错误" });
  const before = { ...page.data };
  page.onIllustrationError();
  assert.deepEqual({ ...page.data }, { ...before, introArtFailed: true });
  assert.equal(requests, 0);
});
