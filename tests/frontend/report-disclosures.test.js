const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

function report() {
  return {
    overview: { learning_records: 0, new_knowledge_items: 0, review_feedback_count: 0, activity_records: 0 },
    subjects: [], activity_subjects: [], review_urgency: [], review_activity: []
  };
}

function historyRow() {
  return {
    submission_id: "submission-a", state: "confirmed", source: "manual", record_id: "record-a",
    occurred_at: "2026-10-10T09:00:00Z", created_at: "2026-10-10T09:00:00Z",
    subject_name: "数学", summary: "练习乘法"
  };
}

test("report disclosures start closed and only fetch bounded history on expansion", async () => {
  const paths = [];
  const { page } = loadPage("pages/reports/index.js", async (path) => {
    paths.push(path);
    if (path === "/children") return [{ id: "child", name: "孩子", active: true }];
    if (path.endsWith("/report?days=7")) return report();
    if (path.endsWith("/history?view=pending&limit=1")) return { items: [], pending_count: 1, has_processing: false };
    if (path.endsWith("/history?view=confirmed&limit=20")) return { items: [historyRow(),
      { ...historyRow(), record_id: "record-b", subject_name: "语文" }], pending_count: 1, has_processing: false };
    throw new Error(`unexpected request: ${path}`);
  });
  await page.load();
  assert.equal(page.data.historyExpanded, false);
  assert.equal(page.data.inventoryExpanded, false);
  assert.equal(page.data.pendingCount, 1);
  assert.equal(paths.filter((path) => path.includes("/history?view=confirmed")).length, 0);
  await page.toggleHistory();
  assert.equal(page.data.historyExpanded, true);
  assert.equal(page.data.historyItems[0].submission_id, "submission-a");
  assert.deepEqual(page.data.historyItems.map(item => item.rowKey), ["record-a", "record-b"]);
  page.toggleInventory();
  assert.equal(page.data.inventoryExpanded, true);
  assert.equal(page.data.historyExpanded, true);
  page.onHide();
  assert.equal(page.data.historyExpanded, false);
  assert.equal(page.data.inventoryExpanded, false);
});

test("switching children clears expanded content and ignores the old child's late history page", async () => {
  let completeOldHistory;
  const { page } = loadPage("pages/reports/index.js", async (path) => {
    if (path === "/children") return [{ id: "child", name: "甲", active: true }, { id: "child-b", name: "乙", active: true }];
    if (path.includes("/report?")) return report();
    if (path.includes("view=pending")) return { items: [], pending_count: 0, has_processing: false };
    if (path.includes("/children/child/history?view=confirmed")) return new Promise((resolve) => { completeOldHistory = resolve; });
    throw new Error(`unexpected request: ${path}`);
  });
  await page.load();
  const old = page.toggleHistory();
  page.toggleInventory();
  await page.chooseChild({ currentTarget: { dataset: { index: 1 } } });
  completeOldHistory({ items: [historyRow()], pending_count: 9 });
  await old;
  assert.equal(page.data.childId, "child-b");
  assert.equal(page.data.historyExpanded, false);
  assert.equal(page.data.inventoryExpanded, false);
  assert.equal(page.data.historyItems.length, 0);
  assert.equal(page.data.pendingCount, 0);
});

test("embedded edit plan runs the same bounded controller and discards detached responses", async () => {
  const paths = [];
  let completeSecond;
  const { page: component } = loadPage("components/review-inventory/index.js", async (path) => {
    paths.push(path);
    if (path.includes("offset=2")) return new Promise((resolve) => { completeSecond = resolve; });
    return { items: [], total: 0, as_of_day: "2026-10-11", child_writable: true };
  });
  Object.assign(component, component.methods);
  component.properties = { contextChildId: "child" };
  await component.lifetimes.attached.call(component);
  assert.equal(component.data.childId, "child");
  assert.equal(component.data.loaded, true);
  assert.deepEqual(paths, ["/children/child/review-inventory?view=time&offset=1&limit=20&review_status=normal"]);
  const second = component.selectDay({ currentTarget: { dataset: { offset: 2 } } });
  component.lifetimes.detached.call(component);
  completeSecond({ items: [{ knowledge_id: "old" }], total: 1, as_of_day: "2026-10-11", child_writable: true });
  await second;
  assert.equal(component.data.items.length, 0);
});
