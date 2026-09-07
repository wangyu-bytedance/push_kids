const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const childContext = require("../../apps/miniprogram/utils/child-context");

function dayAt(index) {
  const day = new Date(Date.UTC(2026, 5, 1 + index));
  return day.toISOString().slice(0, 10);
}

function loadReportsPage() {
  let definition;
  const reportDays = Array.from({ length: 100 }, (_, index) => ({
    day: dayAt(index),
    level: index % 4,
    has_items: index % 3 !== 0,
    passed: index % 11 === 0,
    pending_count: index % 3,
    count: index % 5
  }));
  const api = {
    async request(requestPath) {
      if (requestPath === "/children") return [{ id: "child-1", name: "旺仔" }];
      if (requestPath.includes("/report?days=100")) return {
        overview: { learning_records: 1, new_knowledge_items: 2, review_feedback_count: 3, activity_records: 4 },
        review_urgency: reportDays,
        review_activity: reportDays,
        subjects: []
      };
      throw new Error(`unexpected path: ${requestPath}`);
    }
  };
  const filename = path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require(name) { return name.includes("child-context") ? childContext : api; },
    Page(value) { definition = value; },
    getApp() { return { globalData: { selectedChildId: "child-1" }, selectChild() {} }; }
  }, { filename });
  return {
    ...definition,
    data: { ...definition.data, days: 100 },
    setData(update) { Object.assign(this.data, update); }
  };
}

test("100-day reports render as 30, 30, 30 and 10 day swiper pages", async () => {
  const page = loadReportsPage();
  await page.load();

  assert.deepEqual(Array.from(page.data.urgencyPages, (item) => item.items.length), [30, 30, 30, 10]);
  assert.deepEqual(Array.from(page.data.activityPages, (item) => item.items.length), [30, 30, 30, 10]);
  assert.equal(page.data.urgencyPageLabel, "06-01 至 06-30");

  page.shiftReportPage({ currentTarget: { dataset: { chart: "urgency", offset: 1 } } });
  assert.equal(page.data.urgencyPage, 1);
  assert.equal(page.data.urgencyPageLabel, "07-01 至 07-30");
});

test("report pagination is component-local and uses a six-by-five visual grid", () => {
  const template = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.wxml"), "utf8");
  const styles = fs.readFileSync(path.resolve(__dirname, "../../apps/miniprogram/pages/reports/index.wxss"), "utf8");

  assert.match(template, /<swiper class="day-swiper /);
  assert.match(template, /bindchange="onUrgencyPageChange"/);
  assert.match(template, /<view class="pdots" wx:if="\{\{urgencyPages\.length > 1\}\}">/);
  assert.doesNotMatch(template, /scroll-x/);
  /* 翻页由 pager、圆点和 swiper 自身表达，不再写「左右滑动」这类操作说明；
     取值含义改由图例承担，避免图表上方堆叠说明文字。 */
  assert.doesNotMatch(template, /左右滑动|滑动查看/);
  assert.match(template, /数字：当天待复习/);
  assert.match(template, /已全部通过/);
  assert.match(styles, /grid-template-columns:repeat\(6,minmax\(0,1fr\)\)/);
  assert.match(styles, /grid-template-rows:repeat\(5,86rpx\)/);
});
