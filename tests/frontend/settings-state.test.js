const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function loadSettingsPage() {
  const calls = [];
  let definition;
  const filename = path.resolve(__dirname, "../../apps/miniprogram/pages/settings/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require() { return { request: async (...args) => { calls.push(args); return {}; }, newIdempotencyKey: () => "key" }; },
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
  assert.deepEqual(calls, []);
});
