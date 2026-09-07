const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");

const calendarJs = fs.readFileSync("apps/miniprogram/pages/calendar/index.js", "utf8");
const calendarWxml = fs.readFileSync("apps/miniprogram/pages/calendar/index.wxml", "utf8");
const calendarWxss = fs.readFileSync("apps/miniprogram/pages/calendar/index.wxss", "utf8");
const settingsWxml = fs.readFileSync("apps/miniprogram/pages/settings/index.wxml", "utf8");
const { loadPage } = require("./harness");

test("travel is configured in settings and explicitly excluded from today", () => {
  assert.match(settingsWxml, />出行安排</);
  assert.match(settingsWxml, /只显示在日程，不生成待办/);
  /* 同一条边界只在卡片副标题上说明一次，弹层里不再重复。 */
  assert.doesNotMatch(settingsWxml, /这项安排只会显示在日程，不会生成今日待办/);
  assert.match(settingsWxml, /bindtap="saveTravel"/);
  assert.match(settingsWxml, /bindtap="deleteTravel"/);
});

test("calendar conflict state has text semantics in addition to red styling", () => {
  assert.match(calendarJs, /travel: "出行"/);
  assert.match(calendarJs, /conflictLines/);
  assert.match(calendarWxml, /项存在时间冲突，请核对安排/);
  assert.match(calendarWxml, /item\.conflict_lines/);
  assert.match(calendarWxml, /时间冲突/);
  assert.match(calendarWxss, /var\(--pk-danger-bg\)/);
  assert.match(calendarWxss, /border-left: 8rpx solid var\(--pk-danger\)/);
});

test("calendar lists every conflict object with its time and overlap", async () => {
  const schedule = {
    items: [{
      id: "travel", name: "上学", source: "travel_arrangement", kind: "travel",
      start_time: "07:30", end_time: "08:10", repeat_weekly: true, past: false,
      has_conflict: true,
      conflicts: [
        { item_id: "reading", name: "早读", start_time: "07:50", end_time: "08:20", overlap_minutes: 20 },
        { item_id: "exercise", name: "晨练", start_time: "08:00", end_time: "08:30", overlap_minutes: 10 }
      ]
    }]
  };
  const { page } = loadPage("pages/calendar/index.js", async (requestPath) => {
    if (requestPath === "/children") return [{ id: "child", name: "小芽", active: true }];
    if (requestPath.includes("/schedule?")) return schedule;
    throw new Error(`unexpected path: ${requestPath}`);
  });
  page.onLoad();
  await page.load();

  assert.equal(page.data.items[0].conflict_summary, "与 2 项安排时间重叠");
  assert.deepEqual(Array.from(page.data.items[0].conflict_lines), [
    "与「早读」07:50–08:20 重叠 20 分钟",
    "与「晨练」08:00–08:30 重叠 10 分钟"
  ]);
});

test("tapping a projected travel item returns to its settings editor", () => {
  assert.match(calendarJs, /item\.source === "travel_arrangement"/);
  assert.match(calendarJs, /openTravelArrangementId = item\.id/);
  assert.match(calendarJs, /switchTab\(\{ url: "\/pages\/settings\/index" \}\)/);
});
