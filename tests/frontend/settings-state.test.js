const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const childContext = require("../../apps/miniprogram/utils/child-context");

/* VM 沙箱里的对象与测试域原型不同，比较前先转成本域的普通值。 */
function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

function loadSettingsPage(overrides = {}) {
  const calls = [];
  let definition;
  const filename = path.resolve(__dirname, "../../apps/miniprogram/pages/settings/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require(name) {
      if (name.includes("child-context")) return childContext;
      return { request: async (...args) => { calls.push(args); return {}; }, newIdempotencyKey: () => "key" };
    },
    Page(value) { definition = value; },
    wx: { showToast() {}, showModal() {}, ...overrides.wx },
    getApp() { return { globalData: {}, selectChild() {} }; },
    Set, Object, Array, Number, String, Boolean, Promise
  }, { filename });
  const page = {
    ...definition,
    data: JSON.parse(JSON.stringify(definition.data)),
    setData(update) { Object.assign(this.data, update); }
  };
  return { page, calls };
}

test("opening and cancelling settings editors performs zero writes", () => {
  const { page, calls } = loadSettingsPage();
  page.data.subjects = [];
  page.openCatalog({ currentTarget: { dataset: { type: "activity" } } });
  assert.equal(page.data.showCatalog, true);
  assert.equal(page.data.catalogOptions.length, 17);
  page.closeCatalog();
  assert.equal(page.data.showCatalog, false);

  page.data.addedActivities = [{
    id: "activity-a", name: "游泳", schedule: null, scheduleLabel: "尚未设置时间"
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  assert.equal(page.data.showSchedule, true);
  assert.equal(page.data.perDay, false);
  page.closeSchedule();
  assert.equal(page.data.showSchedule, false);

  page.openTravelCreate();
  assert.equal(page.data.showTravelEditor, true);
  assert.deepEqual(Array.from(page.data.travelWeekdays), [0, 1, 2, 3, 4]);
  page.closeTravelEditor();
  assert.equal(page.data.showTravelEditor, false);
  assert.deepEqual(calls, []);
});

test("travel form preserves validation state and creates one weekly arrangement with canonical slots", async () => {
  const { page, calls } = loadSettingsPage();
  page.load = async () => {};
  page.openTravelCreate();
  page.data.travelEndTime = "07:00";
  await page.saveTravel();
  assert.match(page.data.travelError, /结束时间/);
  assert.equal(page.data.travelEndError, true);
  assert.deepEqual(calls, []);

  page.data.travelEndTime = "08:10";
  await page.saveTravel();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/travel-arrangements");
  assert.equal(calls[0][1].method, "POST");
  assert.equal(calls[0][1].idempotencyKey, "key");
  assert.equal(calls[0][1].capabilities, "weekly-time-slots-v1");
  const slots = calls[0][1].data.time_slots;
  assert.equal(slots.length, 5);
  assert.deepEqual(plain(slots).map((slot) => slot.weekday), [0, 1, 2, 3, 4]);
  assert.ok(slots.every((slot) => slot.start_time === "07:30" && slot.end_time === "08:10"));
  assert.equal(calls[0][1].data.weekdays, undefined);
  assert.equal(page.data.showTravelEditor, false);
});

test("activity editor opens mixed-time schedule in per-day mode and groups the summary", () => {
  const { page } = loadSettingsPage();
  page.data.addedActivities = [{
    id: "activity-a", name: "线上英语", scheduleLabel: "",
    schedule: {
      id: "sch-1", subject_id: "activity-a",
      time_slots: [
        { weekday: 1, start_time: "18:00", end_time: "19:00" },
        { weekday: 2, start_time: "19:00", end_time: "20:00" }
      ]
    }
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  assert.equal(page.data.perDay, true);
  assert.deepEqual(page.data.weekdays, [1, 2]);
  assert.deepEqual(page.data.dayRows.map((row) => row.label), ["周二", "周三"]);
  assert.equal(page.data.scheduleGroups.length, 2);
  assert.match(page.data.scheduleSummary, /二 18:00–19:00；.*三 19:00–20:00/);
});

test("expanding per-day inherits uniform time and added weekday inherits first row", () => {
  const { page } = loadSettingsPage();
  page.data.addedActivities = [{ id: "a", name: "游泳", schedule: null, scheduleLabel: "" }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  page.toggleWeekday({ currentTarget: { dataset: { value: 1 } } });
  page.toggleWeekday({ currentTarget: { dataset: { value: 2 } } });
  page.toggleSchedulePerDay();
  assert.equal(page.data.perDay, true);
  assert.equal(page.data.dayRows.length, 2);
  assert.ok(page.data.dayRows.every((row) => row.start === "18:00" && row.end === "19:00"));

  page.data.dayRows[1] = { ...page.data.dayRows[1], start: "19:00", end: "20:00" };
  page.setDayTime({ currentTarget: { dataset: { index: 1, field: "start" } }, detail: { value: "19:00" } });
  page.toggleWeekday({ currentTarget: { dataset: { value: 4 } } });
  const added = page.data.dayRows.find((row) => row.weekday === 4);
  assert.equal(added.start, "18:00");
  assert.equal(added.end, "19:00");
});

test("removing a weekday drops its per-day row without writes", () => {
  const { page, calls } = loadSettingsPage();
  page.data.addedActivities = [{
    id: "a", name: "线上英语", scheduleLabel: "",
    schedule: { id: "s", subject_id: "a", time_slots: [
      { weekday: 1, start_time: "18:00", end_time: "19:00" },
      { weekday: 2, start_time: "19:00", end_time: "20:00" }
    ] }
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  page.toggleWeekday({ currentTarget: { dataset: { value: 2 } } });
  assert.deepEqual(page.data.weekdays, [1]);
  assert.deepEqual(page.data.dayRows.map((row) => row.weekday), [1]);
  assert.deepEqual(calls, []);
});

test("merging back to uniform requires confirmation and applies first weekday time", () => {
  const modals = [];
  const { page } = loadSettingsPage({ wx: {
    showModal(options) { modals.push(options); options.success({ confirm: true }); }
  } });
  page.data.addedActivities = [{
    id: "a", name: "线上英语", scheduleLabel: "",
    schedule: { id: "s", subject_id: "a", time_slots: [
      { weekday: 1, start_time: "18:00", end_time: "19:00" },
      { weekday: 2, start_time: "19:00", end_time: "20:00" }
    ] }
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  assert.equal(page.data.perDay, true);
  page.toggleSchedulePerDay();
  assert.equal(modals.length, 1);
  assert.equal(page.data.perDay, false);
  assert.equal(page.data.startTime, "18:00");
  assert.equal(page.data.endTime, "19:00");
});

test("cancelling the merge confirmation keeps every per-day row", () => {
  const { page } = loadSettingsPage({ wx: {
    showModal(options) { options.success({ confirm: false }); }
  } });
  page.data.addedActivities = [{
    id: "a", name: "线上英语", scheduleLabel: "",
    schedule: { id: "s", subject_id: "a", time_slots: [
      { weekday: 1, start_time: "18:00", end_time: "19:00" },
      { weekday: 2, start_time: "19:00", end_time: "20:00" }
    ] }
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  page.toggleSchedulePerDay();
  assert.equal(page.data.perDay, true);
  assert.equal(page.data.dayRows.length, 2);
});

test("saving a per-day schedule submits distinct slots with the capability header", async () => {
  const { page, calls } = loadSettingsPage();
  page.load = async () => {};
  page.data.childId = "child-1";
  page.data.addedActivities = [{
    id: "a", name: "线上英语", scheduleLabel: "",
    schedule: { id: "sch-9", subject_id: "a", time_slots: [
      { weekday: 1, start_time: "18:00", end_time: "19:00" },
      { weekday: 2, start_time: "19:00", end_time: "20:00" }
    ] }
  }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  await page.saveSchedule();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/activity-schedules/sch-9");
  assert.equal(calls[0][1].method, "PATCH");
  assert.equal(calls[0][1].capabilities, "weekly-time-slots-v1");
  assert.deepEqual(plain(calls[0][1].data.time_slots), [
    { weekday: 1, start_time: "18:00", end_time: "19:00" },
    { weekday: 2, start_time: "19:00", end_time: "20:00" }
  ]);
});

test("a flexible activity submits empty slots", async () => {
  const { page, calls } = loadSettingsPage();
  page.load = async () => {};
  page.data.childId = "child-1";
  page.data.addedActivities = [{ id: "a", name: "游泳", schedule: null, scheduleLabel: "" }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  page.chooseScheduleMode({ currentTarget: { dataset: { mode: "flexible" } } });
  await page.saveSchedule();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/activity-schedules");
  assert.deepEqual(plain(calls[0][1].data.time_slots), []);
});

test("a per-day row with end before start blocks the save and keeps rows", async () => {
  const { page, calls } = loadSettingsPage();
  page.load = async () => {};
  page.data.childId = "child-1";
  page.data.addedActivities = [{ id: "a", name: "游泳", schedule: null, scheduleLabel: "" }];
  page.openActivitySchedule({ currentTarget: { dataset: { index: 0 } } });
  page.toggleWeekday({ currentTarget: { dataset: { value: 1 } } });
  page.toggleSchedulePerDay();
  page.setDayTime({ currentTarget: { dataset: { index: 0, field: "end" } }, detail: { value: "17:00" } });
  await page.saveSchedule();
  assert.match(page.data.scheduleError, /周二的结束时间/);
  assert.deepEqual(calls, []);
  assert.equal(page.data.dayRows.length, 1);
});
