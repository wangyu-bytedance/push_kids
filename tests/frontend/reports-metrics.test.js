const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function dayAt(index) {
  const day = new Date(Date.UTC(2026, 5, 1 + index));
  return day.toISOString().slice(0, 10);
}

/* 报表页在 vm 里加载：wx 与 getApp 都用最小桩，只观察跳转意图与提示。 */
function loadReportsPage(overview) {
  let definition;
  const reportDays = Array.from({ length: 7 }, (_, index) => ({
    day: dayAt(index), level: 1, has_items: true, passed: false, pending_count: 1, count: 1
  }));
  const api = {
    async request(requestPath) {
      if (requestPath === "/children") return [{ id: "child-1", name: "旺仔" }];
      if (requestPath.includes("/report?days=7")) return { overview, review_urgency: reportDays, review_activity: reportDays, subjects: [] };
      throw new Error(`unexpected path: ${requestPath}`);
    }
  };
  const calls = { toasts: [], tabs: [], scrolls: [] };
  const globalData = { selectedChildId: "child-1" };
  const wx = {
    showToast(options) { calls.toasts.push(options); },
    switchTab(options) { calls.tabs.push(options.url); },
    pageScrollTo(options) { calls.scrolls.push(options); },
    getWindowInfo() { return { windowWidth: 375 }; },
    createSelectorQuery() {
      const selected = [];
      return {
        select(selector) { selected.push(selector); return this; },
        boundingClientRect() { return this; },
        selectViewport() { return this; },
        scrollOffset() { return this; },
        exec(callback) {
          calls.scrolls.push({ selector: selected[0] });
          callback([{ top: 600 }, { scrollTop: 100 }]);
        }
      };
    }
  };
  const filename = path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require() { return api; },
    Page(value) { definition = value; },
    getApp() { return { globalData, selectChild() {} }; },
    wx,
    Date,
    Math,
    Number,
    String,
    Object,
    Promise
  }, { filename });
  return {
    page: { ...definition, data: { ...definition.data, days: 7 }, setData(update) { Object.assign(this.data, update); } },
    calls,
    globalData
  };
}

function tap(target) { return { currentTarget: { dataset: { target } } }; }

/* vm 里造的对象原型不同realm，比较前统一成普通结构。 */
function plain(value) { return JSON.parse(JSON.stringify(value)); }

test("overview metrics carry their own jump target, aria label and clickable flag", async () => {
  const { page } = loadReportsPage({ learning_records: 6, new_knowledge_items: 12, review_feedback_count: 3, activity_records: 2 });
  await page.load();

  assert.deepEqual(Array.from(page.data.metrics, (item) => item.target), ["learning", "knowledge", "feedback", "activity"]);
  assert.deepEqual(Array.from(page.data.metrics, (item) => item.actionable), [true, true, true, true]);
  assert.equal(page.data.metrics[0].ariaLabel, "学习记录 6，看这段时间已确认的学习记录");
  assert.equal(page.data.metrics[1].ariaLabel, "新增知识 12，看科目学习记录分布");
});

test("learning metric opens the confirmed history with the report date range", async () => {
  const { page, calls, globalData } = loadReportsPage({ learning_records: 6, new_knowledge_items: 12, review_feedback_count: 3, activity_records: 2 });
  await page.load();
  page.openMetric(tap("learning"));

  assert.deepEqual(calls.tabs, ["/pages/records/index"]);
  assert.deepEqual(plain(globalData.recordIntent), {
    childId: "child-1", view: "history", status: "confirmed",
    filters: { from: "2026-06-01", to: "2026-06-07" }
  });
});

test("in-page metrics scroll to their own section with top headroom", async () => {
  const { page, calls } = loadReportsPage({ learning_records: 6, new_knowledge_items: 12, review_feedback_count: 3, activity_records: 2 });
  await page.load();
  page.openMetric(tap("knowledge"));
  page.openMetric(tap("feedback"));
  page.openMetric(tap("activity"));

  assert.deepEqual(calls.scrolls.filter((item) => item.selector).map((item) => item.selector),
    ["#sec-subjects", "#sec-feedback", "#sec-activities"]);
  assert.deepEqual(plain(calls.scrolls.filter((item) => item.duration)), [{ scrollTop: 638, duration: 200 }, { scrollTop: 638, duration: 200 }, { scrollTop: 638, duration: 200 }]);
});

test("zero metrics explain the empty range instead of jumping to nothing", async () => {
  const { page, calls, globalData } = loadReportsPage({ learning_records: 0, new_knowledge_items: 0, review_feedback_count: 0, activity_records: 0 });
  await page.load();
  page.openMetric(tap("learning"));
  page.openMetric(tap("activity"));

  assert.deepEqual(Array.from(page.data.metrics, (item) => item.actionable), [false, false, false, false]);
  assert.deepEqual(plain(calls.toasts), [
    { title: "这段时间还没有已确认的学习记录", icon: "none" },
    { title: "这段时间还没有活动练习", icon: "none" }
  ]);
  assert.equal(calls.tabs.length, 0);
  assert.equal(globalData.recordIntent, undefined);
});

test("metric tiles are separated cards with real spacing and tappable affordance", () => {
  const template = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.wxml"), "utf8");
  const atoms = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/styles/atoms.wxss"), "utf8");

  assert.match(atoms, /\.metrics \{ display: grid; grid-template-columns: repeat\(2, minmax\(0, 1fr\)\); gap: var\(--pk-s2\);/);
  assert.match(atoms, /\.metric \{[^}]*min-height: 152rpx/);
  assert.match(atoms, /\.metric\.is-press/);
  assert.doesNotMatch(atoms, /\.metric \+ \.metric::before/);
  assert.match(template, /bindtap="openMetric"/);
  assert.match(template, /id="sec-subjects"/);
  assert.match(template, /id="sec-feedback"/);
  assert.match(template, /id="sec-activities"/);
});
