const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

const slot = (weekday, start_time = "09:00") => ({ weekday, start_time, end_time: "20:00" });
const activity = (id) => ({ id, name: id, kind: "activity", active: true });
function setup(subjects, schedules) {
  const state = { subjects, schedules, fail: false };
  const calls = [];
  const loaded = loadPage("pages/settings/index.js", async (url) => {
    calls.push(url);
    if (url.startsWith("/children?")) return [{ id: "child", name: "六六", active: true }];
    if (url.endsWith("/subjects")) {
      if (state.fail) throw new Error("读取失败");
      return state.subjects;
    }
    if (url.endsWith("/activity-schedules")) return { items: state.schedules };
    if (url.endsWith("/travel-arrangements")) return { items: [] };
    return [];
  });
  return { ...loaded, state, calls };
}
const schedule = (id, ...slots) => ({ id: `schedule-${id}`, subject_id: id, time_slots: slots });
const ids = (page) => Array.from(page.data.addedActivities, (item) => item.id);

test("activities follow Monday through Sunday and first-slot start time, with stable ties", async () => {
  const subjects = ["sun", "piano", "go", "tie", "mon", "sat", "fri", "thu", "tue"].map(activity);
  const schedules = [schedule("sun", slot(6)), schedule("piano", slot(2, "19:00"), slot(5)),
    schedule("go", slot(2, "09:00:00")), schedule("tie", slot(2, "09:00")),
    schedule("mon", slot(0)), schedule("sat", slot(5)), schedule("fri", slot(4)),
    schedule("thu", slot(3)), schedule("tue", slot(1))];
  const original = JSON.stringify({ subjects, schedules });
  const { page, calls } = setup(subjects, schedules);
  await page.load();
  assert.deepEqual(ids(page), ["mon", "tue", "go", "tie", "piano", "thu", "fri", "sat", "sun"]);
  assert.equal(JSON.stringify({ subjects, schedules }), original);
  assert.equal(calls.length, 6, "sorting adds no requests; settings also reads daily tasks");
  page.openActivitySchedule({ currentTarget: { dataset: { index: 2 } } });
  assert.equal(page.data.scheduleSubject.id, "go");
  assert.equal(page.data.scheduleId, "schedule-go");
});

test("first slot is authoritative even when later weekdays or times are earlier", async () => {
  const { page } = setup([activity("multi"), activity("tue"), activity("invalid-first")], [
    schedule("multi", slot(4, "19:00"), slot(0, "08:00")), schedule("tue", slot(1)),
    schedule("invalid-first", slot(null), slot(0))
  ]);
  await page.load();
  assert.deepEqual(ids(page), ["tue", "multi", "invalid-first"]);
});

test("missing slots and invalid weekdays follow all valid weekdays in original order", async () => {
  const badDays = [null, undefined, -1, 7, 1.5, "0"];
  const subjects = [activity("missing"), activity("empty"), ...badDays.map((_, i) => activity(`bad-${i}`)), activity("mon"), activity("sun")];
  const schedules = [schedule("empty"), ...badDays.map((day, i) => schedule(`bad-${i}`, slot(day))), schedule("mon", slot(0)), schedule("sun", slot(6))];
  const { page } = setup(subjects, schedules);
  await page.load();
  assert.deepEqual(ids(page), ["mon", "sun", "missing", "empty", ...badDays.map((_, i) => `bad-${i}`)]);
});

test("invalid times follow valid times within their weekday; seconds sort correctly", async () => {
  const times = [null, undefined, "24:00", "09:60", "09:00:60", "9:00", "09:00:01", "09:00", "23:59:59"];
  const { page } = setup(times.map((_, i) => activity(`a-${i}`)), times.map((time, i) => schedule(`a-${i}`, { weekday: 0, start_time: time, end_time: "20:00" })));
  await page.load();
  assert.deepEqual(ids(page), ["a-7", "a-6", "a-8", "a-0", "a-1", "a-2", "a-3", "a-4", "a-5"]);
});

test("reload reorders changed schedules, preserves other lists and keeps content on error", async () => {
  const learning = { id: "science", name: "科学", kind: "learning", active: true };
  const { page, state } = setup([activity("a"), activity("b"), learning], [schedule("a", slot(4)), schedule("b", slot(1))]);
  await page.load();
  assert.deepEqual(ids(page), ["b", "a"]);
  assert.equal(page.data.addedLearning[0].id, "science");
  state.schedules = [schedule("a", slot(0)), schedule("b", slot(1))];
  await page.load();
  assert.deepEqual(ids(page), ["a", "b"]);
  state.fail = true;
  await page.load();
  assert.deepEqual(ids(page), ["a", "b"]);
  assert.equal(page.data.error, "读取失败");
  state.fail = false; state.subjects = []; state.schedules = [];
  await page.load();
  assert.deepEqual(ids(page), []);
});

test("late activity response cannot overwrite a newly selected child's sorted list", async () => {
  let release;
  const late = new Promise((resolve) => { release = resolve; });
  const { page, app } = loadPage("pages/settings/index.js", async (url) => {
    if (url.startsWith("/children?")) return ["child", "other"].map((id) => ({ id, name: id, active: true }));
    if (url === "/children/child/subjects") return late;
    if (url.endsWith("/subjects")) return [activity("sun"), activity("mon")];
    if (url.endsWith("/activity-schedules")) return { items: [schedule("sun", slot(6)), schedule("mon", slot(0))] };
    if (url.endsWith("/travel-arrangements")) return { items: [] };
    return [];
  });
  const oldLoad = page.load();
  await new Promise((resolve) => setImmediate(resolve));
  app.selectChild("other"); await page.load();
  release([activity("old")]); await oldLoad;
  assert.equal(page.data.childId, "other");
  assert.deepEqual(ids(page), ["mon", "sun"]);
});
