const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const childContext = require("../../apps/miniprogram/utils/child-context");

function loadSettingsPage() {
  const calls = [];
  let definition;
  const filename = path.resolve(__dirname, "../../apps/miniprogram/pages/settings/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require(name) {
      if (name.includes("child-context")) return childContext;
      return { request: async (...args) => { calls.push(args); return {}; }, newIdempotencyKey: () => "key" };
    },
    Page(value) { definition = value; },
    wx: { showToast() {}, showModal() {} },
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
  page.closeSchedule();
  assert.equal(page.data.showSchedule, false);

  page.openTravelCreate();
  assert.equal(page.data.showTravelEditor, true);
  assert.deepEqual(Array.from(page.data.travelWeekdays), [0, 1, 2, 3, 4]);
  page.closeTravelEditor();
  assert.equal(page.data.showTravelEditor, false);
  assert.deepEqual(calls, []);
});

test("travel form preserves validation state and creates one weekly arrangement", async () => {
  const { page, calls } = loadSettingsPage();
  page.load = async () => {};
  page.openTravelCreate();
  page.data.travelEndTime = "07:00";
  await page.saveTravel();
  assert.match(page.data.travelError, /结束时间/);
  assert.deepEqual(calls, []);

  page.data.travelEndTime = "08:10";
  await page.saveTravel();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/travel-arrangements");
  assert.equal(calls[0][1].method, "POST");
  assert.equal(calls[0][1].idempotencyKey, "key");
  assert.deepEqual(Array.from(calls[0][1].data.weekdays), [0, 1, 2, 3, 4]);
  assert.equal(page.data.showTravelEditor, false);
});
