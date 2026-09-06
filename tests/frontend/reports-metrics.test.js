const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { loadPage } = require("./harness");

function dayAt(index) {
  const day = new Date(Date.UTC(2026, 5, 1 + index));
  return day.toISOString().slice(0, 10);
}

function overviewTrends(overview) {
  const keys = ["learning_records", "new_knowledge_items", "review_feedback_count", "activity_records"];
  return {
    timezone: "Asia/Shanghai",
    aggregation: "equal_time_sum",
    buckets: Array.from({ length: 7 }, (_, index) => {
      const bucket = { start_day: dayAt(index), end_day: dayAt(index) };
      keys.forEach((key) => { bucket[key] = index === 6 ? overview[key] : 0; });
      return bucket;
    })
  };
}

function loadReportsPage(overview, trends = overviewTrends(overview)) {
  const reportDays = Array.from({ length: 7 }, (_, index) => ({
    day: dayAt(index), level: 1, has_items: true, passed: false, pending_count: 1, count: 1
  }));
  const calls = { tabs: [] };
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child-1", name: "旺仔", active: true }];
    if (requestPath.includes("/report?days=7")) {
      return { overview, overview_trends: trends, review_urgency: reportDays, review_activity: reportDays, subjects: [] };
    }
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const wx = { switchTab(options) { calls.tabs.push(options.url); } };
  const loaded = loadPage("pages/reports/index.js", request, { wx });
  return { page: loaded.page, calls, globalData: loaded.app.globalData };
}

function plain(value) { return JSON.parse(JSON.stringify(value)); }

test("overview metric cards are passive summaries with seven-point trends", async () => {
  const overview = { learning_records: 6, new_knowledge_items: 12, review_feedback_count: 3, activity_records: 2 };
  const { page } = loadReportsPage(overview);
  await page.load();

  assert.deepEqual(Array.from(page.data.metrics, (item) => item.trend.available), [true, true, true, true]);
  assert.deepEqual(Array.from(page.data.metrics, (item) => item.trend.dots.length), [7, 7, 7, 7]);
  assert.deepEqual(Array.from(page.data.metrics, (item) => item.trend.segments.length), [6, 6, 6, 6]);
  assert.equal(page.data.metrics[0].ariaLabel, "学习记录 6，近 7 天分为 7 段，最高 6，最近一段 6");
  assert.equal(page.openMetric, undefined);
});

test("subject rows keep their explicit history drill-down", async () => {
  const overview = { learning_records: 6, new_knowledge_items: 12, review_feedback_count: 3, activity_records: 2 };
  const { page, calls, globalData } = loadReportsPage(overview);
  await page.load();
  page.openSubjectHistory({ currentTarget: { dataset: { id: "math" } } });

  assert.deepEqual(calls.tabs, ["/pages/records/index"]);
  assert.deepEqual(plain(globalData.recordIntent), {
    childId: "child-1", view: "history", status: "confirmed",
    filters: { subject_id: "math", from: "2026-06-01", to: "2026-06-07" }
  });
});

test("metric tiles expose no tap affordance and render a native mini trend", () => {
  const template = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.wxml"), "utf8");
  const atoms = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/styles/atoms.wxss"), "utf8");
  const pageStyle = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.wxss"), "utf8");
  const metricBlock = template.match(/<view class="metrics mt3">([\s\S]*?)<\/view>\s*<\/view>/)[1];

  assert.match(atoms, /\.metric \{[^}]*min-height: 168rpx/);
  assert.doesNotMatch(metricBlock, /bindtap="openMetric"|hover-class=|aria-role="button"|class="chev/);
  assert.match(metricBlock, /class="metric-trend"/);
  assert.match(metricBlock, /class="trend-segment"/);
  assert.match(metricBlock, /class="trend-dot/);
  assert.match(pageStyle, /\.metric-trend \{[^}]*width: 128rpx/);
});
