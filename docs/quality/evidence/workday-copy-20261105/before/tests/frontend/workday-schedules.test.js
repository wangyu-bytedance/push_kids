const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const tap = (dataset) => ({ currentTarget: { dataset } });
const plain = (value) => JSON.parse(JSON.stringify(value));

function settings(options = {}) {
  const calls = [];
  const fixture = loadPage("pages/settings/index.js", async (...args) => {
    calls.push(args);
    if (options.request) return options.request(...args);
    return {};
  }, options);
  const page = fixture.page;
  Object.assign(page.data, { childId: "child", canWrite: true, addedActivities: [{ id: "subject", name: "英语辅导课",
    schedule: { id: "schedule", workday_only: true, time_slots: [], start_time: "18:15:00", end_time: "19:15:00" } }] });
  page.load = async () => {};
  page.openActivitySchedule(tap({ index: 0 }));
  return { ...fixture, calls };
}

test("activity workday hydrates and saves uniform time without weekday slots", async () => {
  const { page, calls } = settings();
  assert.equal(page.data.workdayOnly, true);
  assert.equal(page.data.flexible, false);
  assert.equal(page.data.workdayStartTime, "18:15");
  assert.match(page.data.scheduleSummary, /工作日.*18:15/);
  await page.saveSchedule();
  assert.deepEqual(plain(calls[0][1].data), { child_id: "child", subject_id: "subject", workday_only: true,
    start_time: "18:15", end_time: "19:15", target_per_week: null });
});

test("switching modes preserves unsaved per-day draft and confirms saved heterogenous replacement", async () => {
  let modal;
  const { page, calls } = settings({ wx: { showModal(value) { modal = value; } } });
  page.data.addedActivities[0].schedule = { id: "schedule", workday_only: false, time_slots: [
    { weekday: 1, start_time: "18:00", end_time: "19:00" },
    { weekday: 3, start_time: "18:30", end_time: "19:30" }] };
  page.openActivitySchedule(tap({ index: 0 }));
  const before = plain(page.data.dayRows);
  page.chooseScheduleMode(tap({ mode: "workday" }));
  page.chooseScheduleMode(tap({ mode: "flexible" }));
  page.chooseScheduleMode(tap({ mode: "fixed" }));
  assert.deepEqual(plain(page.data.dayRows), before);
  assert.equal(page.data.perDay, true);
  page.chooseScheduleMode(tap({ mode: "workday" }));
  const pending = page.saveSchedule();
  assert.equal(calls.length, 0);
  assert.match(modal.content, /不同星期/);
  modal.success({ confirm: false });
  await pending;
  assert.equal(calls.length, 0);
  const confirmed = page.saveSchedule();
  modal.success({ confirm: true });
  await confirmed;
  assert.equal(calls.length, 1);
});

test("activity workday validation, readonly, duplicate save and failure recovery", async () => {
  const { page, calls } = settings({ request: async () => { throw new Error("离线"); } });
  page.data.workdayEndTime = "17:00";
  await page.saveSchedule();
  assert.equal(calls.length, 0);
  page.data.workdayEndTime = "19:15";
  page.data.canWrite = false;
  await page.saveSchedule();
  assert.equal(calls.length, 0);
  page.data.canWrite = true;
  const pending = page.saveSchedule();
  await page.saveSchedule();
  await pending;
  assert.equal(calls.length, 1);
  assert.equal(page.data.showSchedule, true);
  assert.equal(page.data.workdayOnly, true);
  assert.equal(page.data.workdayStartTime, "18:15");
  assert.match(page.data.scheduleError, /离线/);
});

test("calendar workday roundtrip keeps series start date and exclusive repeat flags", async () => {
  const calls = [];
  const { page } = loadPage("pages/calendar/index.js", async (...args) => { calls.push(args); return {}; });
  Object.assign(page.data, { childId: "child", selectedDay: "2026-01-04", canWrite: true,
    items: [{ id: "event", name: "阅读时间", kind: "other", source: "calendar", day: "2026-01-04",
      event_date: "2026-01-01", start_time: "18:00", end_time: "19:00", workday_only: true, repeat_weekly: false }] });
  page.load = async () => {};
  page.openEvent(tap({ id: "event" }));
  assert.equal(page.data.workdayOnly, true);
  assert.equal(page.data.eventDate, "2026-01-01");
  await page.saveEvent();
  assert.equal(calls[0][1].data.workday_only, true);
  assert.equal(calls[0][1].data.repeat_weekly, false);
  assert.equal(calls[0][1].data.event_date, "2026-01-01");
  page.chooseRepeatMode(tap({ mode: "weekly" }));
  assert.equal(page.data.workdayOnly, false);
  assert.equal(page.data.repeatWeekly, true);
});

test("calendar activity source opens its own settings editor", () => {
  const { page, app } = loadPage("pages/calendar/index.js", async () => ({}));
  page.data.items = [{ id: "schedule", source: "activity_schedule", subject_id: "subject" }];
  page.openEvent(tap({ id: "schedule" }));
  assert.equal(app.globalData.openActivitySubjectId, "subject");
});

test("calendar readonly blocks changes; failed writes retain mode, time and inline error", async () => {
  let writes = 0;
  const { page } = loadPage("pages/calendar/index.js", async () => { writes += 1; throw new Error("离线"); });
  Object.assign(page.data, { canWrite: true, childId: "child", selectedDay: "2026-01-04" });
  page.openCreate();
  page.chooseRepeatMode(tap({ mode: "workday" }));
  page.data.eventName = "阅读时间";
  page.data.canWrite = false;
  page.chooseRepeatMode(tap({ mode: "weekly" }));
  await page.saveEvent();
  assert.equal(writes, 0);
  assert.equal(page.data.workdayOnly, true);
  page.data.canWrite = true;
  const pending = page.saveEvent();
  await page.saveEvent(); await pending;
  assert.equal(writes, 1);
  assert.equal(page.data.showEditor, true);
  assert.equal(page.data.workdayOnly, true);
  assert.equal(page.data.eventName, "阅读时间");
  assert.match(page.data.eventError, /离线/);
});

test("closing a heterogeneous replacement confirmation cannot submit its stale draft", async () => {
  let modal;
  const { page, calls } = settings({ wx: { showModal(value) { modal = value; } } });
  page.data.scheduleHadDifferentTimes = true;
  const pending = page.saveSchedule();
  page.closeSchedule();
  modal.success({ confirm: true }); await pending;
  assert.equal(calls.length, 0);
});

test("returning to weekday mode submits the original distinct slots with explicit workday false", async () => {
  const { page, calls } = settings();
  const slots = [{ weekday: 1, start_time: "18:00", end_time: "19:00" },
    { weekday: 3, start_time: "19:30", end_time: "20:30" }];
  page.data.addedActivities[0].schedule = { id: "schedule", time_slots: slots };
  page.openActivitySchedule(tap({ index: 0 }));
  page.chooseScheduleMode(tap({ mode: "workday" }));
  page.chooseScheduleMode(tap({ mode: "fixed" }));
  await page.saveSchedule();
  assert.equal(calls[0][1].data.workday_only, false);
  assert.deepEqual(plain(calls[0][1].data.time_slots), slots);
});

test("coverage warning survives cached day selection and avoids false whole-week empty", async () => {
  const warning = { code: "workday_calendar_coverage_missing", coverage_end: "2026-12-31" };
  const { page } = loadPage("pages/calendar/index.js", async (path) => {
    if (path === "/children") return [{ id: "child", name: "合成孩子", active: true }];
    return { items: [], workday_calendar_warning: warning };
  });
  page.onLoad();
  page.data.selectedDay = "2027-01-04";
  await page.load();
  assert.match(page.data.workdayWarning, /2026/);
  await page.fillWeek("child", "2027-01-04", page.loadGeneration);
  assert.equal(page.data.weekEmpty, false);
  page.chooseDay(tap({ day: "2027-01-05" }));
  assert.match(page.data.workdayWarning, /2026/);
});

test("Today exposes unsupported workday data and expands its activity warning", async () => {
  const dashboard = { day: "2027-01-04", todo_groups: [], todo_count: 0, required_todo_count: 0,
    estimated_minutes: 0, pending_confirmation_count: 0, analyzing_count: 0, failed_count: 0,
    daily_summary: { subjects: [], record_count: 0 }, schedule_items: [], activity_suggestions: [],
    activity_remaining_count: 0, next_review: null,
    workday_calendar_warning: { code: "workday_calendar_coverage_missing", coverage_end: "2026-12-31" } };
  const { page } = loadPage("pages/today/index.js", async (path) => {
    if (path === "/children") return [{ id: "child", name: "合成孩子", active: true }];
    if (path.endsWith("/subjects")) return [];
    if (path.includes("/dashboard")) return dashboard;
    throw new Error(`Unexpected path: ${path}`);
  });
  await page.load();
  assert.match(page.data.dashboard.workday_warning_text, /2026/);
  assert.equal(page.data.sections.activity, true);
  assert.equal(page.data.sectionMeta.activity, "数据待更新");
  assert.equal(page.data.dashboard.is_empty, false);
});
