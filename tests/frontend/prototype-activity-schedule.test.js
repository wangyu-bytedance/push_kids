const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const prototypeSource = fs.readFileSync(
  path.resolve(__dirname, "../../docs/design/frontend/prototypes/DREV-20260830-03/index.html"),
  "utf8"
);
const recordsSource = fs.readFileSync(
  path.resolve(__dirname, "../../apps/miniprogram/pages/records/index.js"),
  "utf8"
);
const todaySource = fs.readFileSync(
  path.resolve(__dirname, "../../apps/miniprogram/pages/today/index.js"),
  "utf8"
);
const settingsTemplate = fs.readFileSync(
  path.resolve(__dirname, "../../apps/miniprogram/pages/settings/index.wxml"),
  "utf8"
);

test("activity reminders use an explicit start and end time", () => {
  assert.match(prototypeSource, /id="activity-plan-time"[^>]+aria-label="练习开始时间"/);
  assert.match(prototypeSource, /id="activity-plan-end"[^>]+aria-label="练习结束时间"/);
  assert.match(prototypeSource, /data-plan-time="18:00" data-plan-end="19:00"/);
  assert.doesNotMatch(prototypeSource, /function addMinutes\(/);
});

test("activity reminder validation preserves invalid ranges", () => {
  assert.match(prototypeSource, /if \(selectedDays\.length && end <= start\)/);
  assert.match(prototypeSource, /error\.textContent = '结束时间需晚于开始时间'/);
  assert.match(prototypeSource, /document\.getElementById\('activity-plan-end'\)\.focus\(\);\s+return;/);
});

test("the same activity time range is synchronized to calendar and today", () => {
  assert.match(prototypeSource, /function syncActivitySchedule\(activityName, selectedIndexes, start, end\)/);
  assert.match(prototypeSource, /syncActivitySchedule\(activityName, selectedIndexes, start, end\)/);
  assert.match(prototypeSource, /time\.textContent = `\$\{item\.start\}–\$\{item\.end\}`/);
  assert.match(prototypeSource, /`\$\{selectedDays\.join\('、'\)\} · \$\{start\}–\$\{end\}`/);
});

test("today disclosures and child triggers share vector chevrons", () => {
  const controls = prototypeSource.match(/class="control-chevron (?:today-section-chevron|child-chevron)"/g) || [];

  assert.equal(controls.length, 8);
  assert.doesNotMatch(prototypeSource, />⌄</);
  assert.match(prototypeSource, /<path d="M2\.75 4\.5 6 7\.5l3\.25-3" \/>/);
  assert.match(prototypeSource, /\.today-section-toggle\[aria-expanded="true"\] \.today-section-chevron \{ transform: rotate\(180deg\); \}/);
  assert.match(prototypeSource, /\.child-trigger\[aria-expanded="true"\] \.child-chevron \{ transform: rotate\(180deg\); \}/);
});

test("today starts with its three fact sections instead of a review-only progress card", () => {
  assert.doesNotMatch(prototypeSource, /today-summary|today-progress|progress-ring/);
  assert.doesNotMatch(prototypeSource, /今日进度|完成三件事|还有 2 项建议复习/);
  assert.match(prototypeSource, /id="today-review-title"/);
  assert.match(prototypeSource, /id="today-learning-title"/);
  assert.match(prototypeSource, /id="today-activity-title"/);
});

test("calendar and today use the end-time boundary for the shared past state", () => {
  assert.match(prototypeSource, /const prototypeNow = \{ dayIndex: 0, time: '20:18' \}/);
  assert.match(prototypeSource, /return timeToMinutes\(item\.end\) <= timeToMinutes\(prototypeNow\.time\)/);
  assert.match(prototypeSource, /agenda-item\$\{isPast \? ' is-past' : ''\}/);
  assert.match(prototypeSource, /today-activity\$\{isPast \? ' is-past' : ''\}/);
  assert.match(prototypeSource, /\$\{isPast \? '，已结束' : ''\}/);
  assert.match(prototypeSource, /\.agenda-item\.is-past \.agenda-event/);
  assert.match(prototypeSource, /\.today-activity\.is-past/);
});

test("photo records support single capture and repeated multi-select with one shared cap", () => {
  assert.match(prototypeSource, /id="single-photo-input" type="file" accept="image\/\*" capture="environment" hidden/);
  assert.match(prototypeSource, /id="multiple-photo-input" type="file" accept="image\/\*" multiple hidden/);
  assert.match(prototypeSource, /const remaining = 9 - photoNumber/);
  assert.match(prototypeSource, /const selected = files\.slice\(0, remaining\)/);
  assert.match(prototypeSource, /uploadZone\.querySelectorAll\('\.photo-tile'\)\.length/);
  assert.match(prototypeSource, /URL\.revokeObjectURL\(remove\.dataset\.objectUrl\)/);
  assert.match(prototypeSource, />补充内容<\/label>/);
  assert.doesNotMatch(prototypeSource, /补充一句/);
});

test("interrupted native photo batches can be resumed or cancelled", () => {
  assert.match(recordsSource, /item\.can_finalize_upload \? "照片已保存，可继续分析"/);
  assert.match(recordsSource, /async finalizePending\(event\)/);
  assert.match(recordsSource, /async cancelSubmission\(event\)/);
});

test("native today consumes optional activity suggestions without duplicating fixed schedules", () => {
  assert.match(todaySource, /const scheduledSubjects = new Set/);
  assert.match(todaySource, /dashboard\.optional_activity_suggestions/);
});

test("native settings can remove an activity reminder", () => {
  assert.match(settingsTemplate, /bindtap="removeActivity">移除活动/);
});
