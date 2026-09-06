const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

const KEYS = ["learning_records", "new_knowledge_items", "review_feedback_count", "activity_records"];

function addDays(day, offset) {
  const date = new Date(`${day}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + offset);
  return date.toISOString().slice(0, 10);
}

function trendFixture(values, options = {}) {
  const days = options.days || 30;
  const starts = Array(7).fill(null);
  const ends = Array(7).fill(null);
  for (let offset = 0; offset < days; offset += 1) {
    const index = Math.floor(offset * 7 / days);
    if (starts[index] === null) starts[index] = addDays("2026-05-31", offset);
    ends[index] = addDays("2026-05-31", offset);
  }
  return {
    timezone: options.timezone || "Asia/Shanghai",
    aggregation: options.aggregation || "equal_time_sum",
    buckets: starts.map((day, index) => {
      const bucket = { start_day: day, end_day: ends[index] };
      KEYS.forEach((key) => { bucket[key] = values[key][index]; });
      return bucket;
    })
  };
}

function totals(values) {
  return Object.fromEntries(KEYS.map((key) => [key, values[key].reduce((sum, value) => sum + value, 0)]));
}

async function render(values, options = {}) {
  const overview = options.overview || totals(values);
  const days = options.days || 30;
  const timeline = Array.from({ length: days }, (_, index) => ({
    day: addDays("2026-02-27", index), level: 0, passed: false, pending_count: 0, count: 0
  }));
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child-1", name: "旺仔", active: true }];
    if (requestPath.includes("/report?days=")) return {
      overview,
      ...(options.omitTrend ? {} : { overview_trends: options.trend || trendFixture(values, { days }) }),
      review_urgency: timeline,
      review_activity: timeline,
      subjects: []
    };
    throw new Error("activity detail unavailable in fixture");
  }
  const loaded = loadPage("pages/reports/index.js", request, { wx: {} });
  loaded.page.data.days = days;
  await loaded.page.load();
  return loaded.page.data.metrics;
}

function valuesOf(value = [0, 1, 2, 3, 2, 1, 4]) {
  return Object.fromEntries(KEYS.map((key) => [key, [...value]]));
}

test("7, 30 and 100 day ranges always render exactly seven aggregate points", async () => {
  for (const days of [7, 30, 100]) {
    const metrics = await render(valuesOf(), { days });
    metrics.forEach((metric) => {
      assert.equal(metric.trend.dots.length, 7);
      assert.equal(metric.trend.segments.length, 6);
      assert.match(metric.trend.summary, new RegExp(`近 ${days} 天分为 7 段`));
    });
  }
});

test("new-user zero series remains an honest flat seven-point line", async () => {
  const metrics = await render(valuesOf([0, 0, 0, 0, 0, 0, 0]), { days: 100 });
  assert.equal(metrics[0].trend.available, true);
  assert.equal(new Set(metrics[0].trend.dots.map((dot) => dot.style.split("top:")[1])).size, 1);
  assert.match(metrics[0].trend.summary, /最高 0，最近一段 0/);
});

test("missing or invalid trend contracts degrade all cards to no-trend copy", async () => {
  const values = valuesOf();
  const missing = await render(values, { omitTrend: true });
  assert.equal(missing.every((metric) => !metric.trend.available), true);

  const badSum = totals(values);
  badSum.learning_records += 1;
  const mismatched = await render(values, { overview: badSum });
  assert.equal(mismatched.every((metric) => !metric.trend.available), true);

  const nonContiguous = trendFixture(values);
  nonContiguous.buckets[2].start_day = addDays(nonContiguous.buckets[2].start_day, 1);
  const invalidDates = await render(values, { trend: nonContiguous });
  assert.equal(invalidDates.every((metric) => !metric.trend.available), true);
});
