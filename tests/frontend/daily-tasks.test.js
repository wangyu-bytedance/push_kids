const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const childContext = require("../../apps/miniprogram/utils/child-context");

const plain = (value) => JSON.parse(JSON.stringify(value));
const event = (dataset) => ({ currentTarget: { dataset } });
const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};

function harness(name, request) {
  let definition;
  const calls = [];
  const app = { globalData: { familyId: "family-a", selectedChildId: "child-a" },
    selectChild(id) { this.globalData.selectedChildId = id; } };
  const source = fs.readFileSync(path.join(__dirname, `../../apps/miniprogram/pages/${name}/index.js`), "utf8");
  vm.runInNewContext(source, {
    require(module) {
      if (module.includes("child-context")) return childContext;
      if (module.includes("/ui")) return { subjectClass: () => "", subjectMark: () => "",
        readPreference() { throw Error("old folding preference must not be read"); },
        writePreference() { throw Error("folding must not persist"); } };
      return { request: async (...args) => { calls.push(args); return request(...args); } };
    },
    Page(value) { definition = value; },
    getApp: () => app,
    wx: { showToast() {}, switchTab() {}, navigateTo() {}, stopPullDownRefresh() {},
      showModal(options) { options.success({ confirm: true }); } }
  });
  const page = { ...definition, data: plain(definition.data),
    setData(update) {
      for (const [key, value] of Object.entries(update)) {
        const parts = key.split(".");
        let target = this.data;
        while (parts.length > 1) target = target[parts.shift()];
        target[parts[0]] = value;
      }
    } };
  return { page, app, calls };
}

function dashboard(overrides = {}) {
  return { day: "2026-10-12", todo_count: 0, required_todo_count: 0, estimated_minutes: 0,
    todo_groups: [], schedule_items: [], activity_suggestions: [], activity_remaining_count: 0,
    pending_confirmation_count: 0, daily_summary: { record_count: 0, subjects: [] },
    daily_tasks: { day: "2026-10-12", total_count: 0, remaining_count: 0, items: [] }, ...overrides };
}

function todayHarness(getDashboard) {
  return harness("today", async (url) => {
    if (url === "/children") return [{ id: "child-a", name: "姐姐" }, { id: "child-b", name: "弟弟" }];
    if (url.endsWith("/subjects")) return [];
    if (url.endsWith("/dashboard")) return plain(getDashboard(url));
    throw Error(`unexpected request ${url}`);
  });
}

test("empty sections collapse and remain manually expandable without storage", async () => {
  const { page } = todayHarness(() => dashboard());
  await page.load();
  assert.deepEqual(plain(page.data.sections), { review: false, daily: false, learning: false, activity: false });
  for (const section of ["review", "daily", "learning", "activity"]) {
    page.toggleSection(event({ section }));
    assert.equal(page.data.sections[section], true);
  }
  await page.load();
  assert.ok(Object.values(page.data.sections).every(Boolean));
  await page.onPullDownRefresh();
  assert.ok(Object.values(page.data.sections).every((value) => !value));
});

test("full remaining aggregates expand even when rendered preview is empty", async () => {
  const { page } = todayHarness(() => dashboard({ todo_count: 12, todo_remaining_count: 12,
    daily_tasks: { total_count: 2, remaining_count: 1, items: [] },
    daily_summary: { record_count: 40, subjects: [] }, activity_remaining_count: 3 }));
  await page.load();
  assert.deepEqual(plain(page.data.sections), { review: true, daily: true, learning: true, activity: true });
  assert.equal(page.data.sectionMeta.daily, "1 / 2 已完成");
});

test("finished sections collapse; stable plan uses selected count rather than backlog", async () => {
  const { page } = todayHarness(() => dashboard({ todo_count: 90,
    review_selection: { sessions: [], selected_count: 0, planned_count: 4, today_feedback_count: 4 },
    daily_tasks: { total_count: 2, remaining_count: 0, items: [] },
    schedule_items: [{ id: "swim", name: "游泳", past: true, completed: true }], activity_remaining_count: 0 }));
  await page.load();
  assert.equal(page.data.sections.review, false);
  assert.equal(page.data.sections.daily, false);
  assert.equal(page.data.sections.activity, false);
  assert.equal(page.data.planCompleted, true);
});

test("manual choice resets on child/day change and leaving today", async () => {
  let day = "2026-10-12";
  const { page, app } = todayHarness(() => dashboard({ day }));
  await page.load();
  page.toggleSection(event({ section: "daily" }));
  app.selectChild("child-b");
  await page.load();
  assert.equal(page.data.sections.daily, false);
  page.toggleSection(event({ section: "daily" }));
  day = "2026-10-13";
  await page.load();
  assert.equal(page.data.sections.daily, false);
  page.toggleSection(event({ section: "daily" }));
  page.onHide();
  page.onShow();
  await page.load();
  assert.equal(page.data.sections.daily, false);
});

test("daily completion commits returned facts; duplicate taps are blocked and manual choice retained", async () => {
  const pending = deferred();
  const { page, calls } = harness("today", () => pending.promise);
  page.data.childId = "child-a";
  page.data.loading = false;
  page.data.canWrite = true;
  page.data.dashboard = dashboard({ daily_tasks: { total_count: 1, remaining_count: 1,
    items: [{ id: "read", name: "阅读", completed: false }] } });
  page.data.sections.daily = true;
  page.toggleSection(event({ section: "daily" }));
  const first = page.toggleDailyTask(event({ id: "read" }));
  await page.toggleDailyTask(event({ id: "read" }));
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/children/child-a/daily-tasks/read/today-completion");
  assert.deepEqual(plain(calls[0][1]), { method: "PUT", data: { completed: true } });
  assert.equal(page.data.dashboard.daily_tasks.remaining_count, 1);
  pending.resolve({ day: "2026-10-12", total_count: 1, remaining_count: 0,
    items: [{ id: "read", name: "阅读", completed: true }] });
  await first;
  assert.equal(page.data.dashboard.daily_tasks.remaining_count, 0);
  assert.equal(page.data.sections.daily, false);
  assert.equal(page.data.dailyTaskPendingId, "");
});

test("last completion collapses automatically and undo opens it", async () => {
  const { page } = harness("today", (_url, options) => ({ day: "2026-10-12", total_count: 1,
    remaining_count: options.data.completed ? 0 : 1,
    items: [{ id: "read", name: "阅读", completed: options.data.completed }] }));
  page.data.childId = "child-a";
  page.data.loading = false;
  page.data.canWrite = true;
  page.data.dashboard = dashboard({ daily_tasks: { total_count: 1, remaining_count: 1,
    items: [{ id: "read", name: "阅读", completed: false }] } });
  await page.toggleDailyTask(event({ id: "read" }));
  assert.equal(page.data.sections.daily, false);
  await page.toggleDailyTask(event({ id: "read" }));
  assert.equal(page.data.sections.daily, true);
});

test("failed completion keeps original facts and read-only members send no requests", async () => {
  const { page, calls } = harness("today", () => { throw Error("暂时无法保存"); });
  page.data.childId = "child-a";
  page.data.loading = false;
  page.data.canWrite = true;
  page.data.dashboard = dashboard({ daily_tasks: { total_count: 1, remaining_count: 1,
    items: [{ id: "read", name: "阅读", completed: false }] } });
  await page.toggleDailyTask(event({ id: "read" }));
  assert.equal(page.data.dashboard.daily_tasks.remaining_count, 1);
  assert.equal(page.data.dailyTaskError, "暂时无法保存");
  page.data.canWrite = false;
  await page.toggleDailyTask(event({ id: "read" }));
  assert.equal(calls.length, 1);
});

test("late completion response cannot overwrite another child or hidden page", async () => {
  for (const transition of ["child", "hide", "family"]) {
    const pending = deferred();
    const { page, app } = harness("today", () => pending.promise);
    page.data.childId = "child-a";
    page.data.loading = false;
    page.data.canWrite = true;
    const initial = dashboard({ daily_tasks: { total_count: 1, remaining_count: 1,
      items: [{ id: "read", completed: false }] } });
    page.data.dashboard = initial;
    const write = page.toggleDailyTask(event({ id: "read" }));
    if (transition === "child") page.data.childId = "child-b";
    if (transition === "hide") page.onHide();
    if (transition === "family") app.globalData.familyId = "family-b";
    pending.resolve({ day: "2026-10-12", total_count: 1, remaining_count: 0, items: [] });
    await write;
    assert.equal(page.data.dashboard, initial);
  }
});

test("settings presets are drafts and invalid or cancelled forms perform zero writes", async () => {
  const { page, calls } = harness("settings", () => ({}));
  page.data.loading = false;
  page.data.childId = "child-a";
  page.openDailyTaskForm(event({ name: "跳绳" }));
  assert.equal(page.data.dailyTaskName, "跳绳");
  assert.equal(page.data.dailyTaskMinutes, "10");
  page.data.dailyTaskMinutes = "1.5";
  await page.saveDailyTask();
  assert.match(page.data.dailyTaskError, /整数分钟/);
  assert.equal(page.data.dailyTaskName, "跳绳");
  page.data.dailyTaskName = "   ";
  page.data.dailyTaskMinutes = "20";
  await page.saveDailyTask();
  assert.match(page.data.dailyTaskError, /名称/);
  page.closeDailyTaskForm();
  assert.equal(page.data.showDailyTaskForm, false);
  assert.deepEqual(calls, []);
});

test("settings creates then edits the same task and deletion uses confirmation", async () => {
  const { page, calls } = harness("settings", (_url, options) => options.method === "DELETE" ? null
    : { id: "read", ...options.data });
  page.data.loading = false;
  page.data.childId = "child-a";
  page.openDailyTaskForm(event({ name: "阅读" }));
  await page.saveDailyTask();
  assert.equal(page.data.dailyTasks.length, 1);
  assert.equal(calls[0][1].method, "POST");
  page.openDailyTaskForm(event({ id: "read" }));
  page.data.dailyTaskMinutes = "30";
  await page.saveDailyTask();
  assert.equal(calls[1][1].method, "PATCH");
  assert.equal(page.data.dailyTasks[0].target_minutes, 30);
  page.openDailyTaskForm(event({ id: "read" }));
  page.deleteDailyTask();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(calls[2][1].method, "DELETE");
  assert.equal(page.data.dailyTasks.length, 0);
});

test("settings write failure retains form; pending blocks edits and late save cannot leak", async () => {
  const pending = deferred();
  const { page, calls } = harness("settings", () => pending.promise);
  page.data.loading = false;
  page.data.childId = "child-a";
  page.openDailyTaskForm(event({ name: "阅读" }));
  const first = page.saveDailyTask();
  await page.saveDailyTask();
  page.setDailyTaskField({ currentTarget: { dataset: { field: "dailyTaskName" } }, detail: { value: "跳绳" } });
  assert.equal(page.data.dailyTaskName, "阅读");
  assert.equal(calls.length, 1);
  pending.reject(Error("保存失败"));
  await first;
  assert.equal(page.data.showDailyTaskForm, true);
  assert.equal(page.data.dailyTaskName, "阅读");
  assert.equal(page.data.dailyTaskError, "保存失败");
  const late = deferred();
  const other = harness("settings", () => late.promise).page;
  other.data.loading = false;
  other.data.childId = "child-a";
  other.openDailyTaskForm(event({ name: "阅读" }));
  const write = other.saveDailyTask();
  other.resetDailyTaskForm();
  other.data.childId = "child-b";
  late.resolve({ id: "read", name: "阅读", target_minutes: 20 });
  await write;
  assert.equal(other.data.dailyTasks.length, 0);
});

test("daily task markup orders the region below review and empty learning/activity obey collapse", () => {
  const source = fs.readFileSync(path.join(__dirname, "../../apps/miniprogram/pages/today/index.wxml"), "utf8");
  assert.ok(source.indexOf('data-section="review"') < source.indexOf('data-section="daily"'));
  assert.ok(source.indexOf('data-section="daily"') < source.indexOf('data-section="learning"'));
  assert.doesNotMatch(source, /sections\.(learning|activity)\s*\|\|/);
});
