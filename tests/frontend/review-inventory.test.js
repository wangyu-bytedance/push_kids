const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

const result = { items: [], total: 0, next_cursor: null, child_writable: true, as_of_day: "2026-10-06" };
function setup(request = async () => result, options) {
  const loaded = loadPage("pages/review-inventory/index.js", request, options);
  loaded.page.onLoad({ childId: "child" }); loaded.page.visible = true;
  return loaded;
}
const event = (dataset) => ({ currentTarget: { dataset } });

test("dates and arrangement labels distinguish reservations and legacy responses", async () => {
  const { page } = setup(async () => ({ ...result, items: [
    { knowledge_id: "auto", arrangement_state: "waiting", suggested_review_on: "2026-10-07" },
    { knowledge_id: "manual", arrangement_state: "reserved", scheduled_on: "2026-10-08", suggested_review_on: null },
    { knowledge_id: "legacy", due_date: "2026-10-06" },
    { knowledge_id: "unknown", arrangement_state: "new-state", due_date: null },
    { knowledge_id: "done", arrangement_state: "reviewed_today", suggested_review_on: "2026-10-10" }
  ] }));
  await page.loadItems();
  assert.equal(page.data.items[0].dateText, "建议复习日：2026-10-07");
  assert.equal(page.data.items[0].arrangementText, "等待安排");
  assert.equal(page.data.items[1].dateText, "家长安排日期：2026-10-08");
  assert.equal(page.data.items[2].dateText, "计划日期：2026-10-06");
  assert.equal(page.data.items[2].arrangementText, "安排状态待更新");
  assert.equal(page.data.items[3].dateText, "");
  assert.equal(page.data.items[4].arrangementText, "今日已完成");
});

test("cloud bootstrap may establish family and still load; switching context clears old rows", async () => {
  let ready; const paths = [];
  const { page, app } = setup(async path => { paths.push(path); return result; },
    { globalData: { useCloud: true } });
  app.refreshBootstrap = () => new Promise(resolve => { ready = () => {
    app.globalData.familyId = "family-a";
    app.globalData.currentMember = { role: "viewer" }; resolve();
  }; });
  const showing = page.onShow(); assert.equal(paths.length, 0); ready(); await showing;
  assert.equal(paths.length, 1); assert.equal(page.data.canWrite, false);
  page.onHide(); page.data.items = [{ knowledge_id: "private-old" }];
  app.globalData.familyId = "family-b"; app.globalData.selectedChildId = "new-child";
  const next = page.onShow(); assert.equal(page.data.items.length, 0); await next;
  assert.match(paths.at(-1), /children\/new-child/);
});

test("specific count commits only on confirmation and uses exact server filter", async () => {
  const paths = [];
  const { page } = setup(async path => { paths.push(path); return result; });
  page.data.view = "count";
  page.openCount(); page.inputCount({ detail: { value: "6" } }); page.closeCount();
  assert.equal(page.data.count, null); assert.equal(paths.length, 0);
  page.openCount(); page.inputCount({ detail: { value: "-1" } }); await page.confirmCount();
  assert.ok(page.data.countError); assert.equal(page.data.showCountInput, true);
  for (const value of ["", "1.5", "2147483648", "foo"]) {
    page.inputCount({ detail: { value } }); await page.confirmCount(); assert.equal(paths.length, 0);
  }
  page.inputCount({ detail: { value: "6" } }); await page.confirmCount();
  assert.equal(page.data.count, 6); assert.equal(page.data.showCountInput, false);
  assert.match(paths.at(-1), /review_count=6/);
  page.openCount(); page.inputCount({ detail: { value: "0" } }); await page.confirmCount();
  assert.equal(page.data.count, 0); assert.match(paths.at(-1), /review_count=0/);
  await page.selectCount(event({ count: "all" })); assert.doesNotMatch(paths.at(-1), /review_count=/);
});

test("current cursor page groups by subject and resets folding on a new page", async () => {
  const requests = [];
  const pages = [
    { ...result, items: [
      { knowledge_id: "e1", subject_id: "en", subject_name: "英语" },
      { knowledge_id: "cn1", subject_id: "cn", subject_name: "语文" },
      { knowledge_id: "e2", subject_id: "en", subject_name: "英语" },
      { knowledge_id: "m1", subject_id: "math", subject_name: "数学" }
    ], next_cursor: "next" },
    { ...result, items: [{ knowledge_id: "cn2", subject_id: "cn", subject_name: "语文" }] }
  ];
  const { page } = setup(async path => { requests.push(path); return pages[requests.length - 1]; });
  await page.loadItems();
  assert.deepEqual(Array.from(page.data.groups, group => group.name), ["英语", "语文", "数学"]);
  assert.deepEqual(Array.from(page.data.groups[0].entries, entry => entry.knowledge_id), ["e1", "e2"]);
  assert.deepEqual(Array.from(page.data.groups, group => group.expanded), [true, false, false]);
  page.toggleGroup(event({ key: "cn" }));
  assert.deepEqual(Array.from(page.data.groups, group => group.expanded), [true, true, false]);
  assert.equal(requests.length, 1);
  await page.nextPage();
  assert.deepEqual(Array.from(page.data.groups, group => group.name), ["语文"]);
  assert.equal(page.data.groups[0].expanded, true);
  assert.equal(page.data.pageNumber, 2);
});

test("ellipsis menu is one-at-a-time, closes on repeat or fold, and delete still confirms", async () => {
  const { page } = setup();
  page.data.canWrite = true;
  page.data.items = [
    { knowledge_id: "a", subject_id: "en", subject_name: "英语", can_schedule: true },
    { knowledge_id: "b", subject_id: "en", subject_name: "英语", can_schedule: false }
  ];
  page.data.groups = [{ key: "en", name: "英语", expanded: true, entries: page.data.items }];
  page.openActions(event({ id: "a" }));
  assert.equal(page.data.actionMenuId, "a");
  assert.equal(page.data.target.knowledge_id, "a");
  page.openActions(event({ id: "b" }));
  assert.equal(page.data.actionMenuId, "b");
  page.closeActionMenu();
  assert.equal(page.data.actionMenuId, "");
  assert.equal(page.data.target, null);
  page.openActions(event({ id: "a" }));
  page.openActions(event({ id: "a" }));
  assert.equal(page.data.actionMenuId, "");
  page.openActions(event({ id: "a" }));
  page.toggleGroup(event({ key: "en" }));
  assert.equal(page.data.groups[0].expanded, false);
  assert.equal(page.data.actionMenuId, "");
  page.openActions(event({ id: "a" }));
  page.askDelete();
  assert.equal(page.data.actionMenuId, "");
  assert.equal(page.data.deleting, true);
  assert.equal(page.data.target.knowledge_id, "a");
});

test("ellipsis menu opens upward when the trigger is near the viewport bottom", () => {
  const query = {
    in() { return this; },
    select() { return { boundingClientRect() {} }; },
    exec(callback) { callback([{ top: 510, bottom: 554 }, { height: 156 }]); }
  };
  const { page } = setup(undefined, { wx: {
    createSelectorQuery: () => query,
    getWindowInfo: () => ({ windowHeight: 568 })
  } });
  page.data.actionMenuId = "a";
  page.placeActionMenu("a");
  assert.equal(page.data.actionMenuAbove, true);
});

test("pagination replaces rows and old filter responses cannot overwrite selection", async () => {
  const pending = [];
  const { page } = setup(path => new Promise(resolve => pending.push({ path, resolve })));
  const old = page.loadItems();
  const newer = page.changeView(event({ id: "count" }));
  pending[1].resolve({ ...result, items: [{ knowledge_id: "new" }], next_cursor: "next" }); await newer;
  pending[0].resolve({ ...result, items: [{ knowledge_id: "old" }] }); await old;
  assert.equal(page.data.items[0].knowledge_id, "new");
  const next = page.nextPage(); pending[2].resolve({ ...result, items: [{ knowledge_id: "second" }] }); await next;
  assert.equal(page.data.items.length, 1); assert.equal(page.data.items[0].knowledge_id, "second");
  assert.equal(page.data.pageNumber, 2);
});

test("single subject includes zero-count subjects and requests only selected subject", async () => {
  const paths = [];
  const { page } = setup(async path => {
    paths.push(path);
    return path.includes("/subjects") ? { items: [{ id: "math", count: 0 }, { id: "cn", count: 2 }] } : result;
  });
  await page.changeView(event({ id: "subject" }));
  assert.equal(page.data.subjectId, "math"); assert.match(paths.at(-1), /subject_id=math/);
  await page.selectSubject(event({ id: "cn" })); assert.match(paths.at(-1), /subject_id=cn/);
});

test("refresh keeps a subject selected from a later subject page", async () => {
  const paths = [];
  const { page } = setup(async path => {
    paths.push(path);
    if (path.includes("/subjects")) return path.includes("cursor=next-subjects")
      ? { items: [{ id: "science", count: 2 }], next_cursor: null }
      : { items: [{ id: "math", count: 1 }], next_cursor: "next-subjects" };
    return { ...result, total: 3 };
  });
  await page.changeView(event({ id: "subject" }));
  await page.nextSubjects();
  assert.equal(page.data.subjectId, "science");
  const subjectRequests = paths.filter(path => path.includes("/subjects")).length;
  await page.reload();
  assert.equal(page.data.subjectId, "science");
  assert.equal(paths.filter(path => path.includes("/subjects")).length, subjectRequests);
  assert.match(paths.at(-1), /subject_id=science/);
  assert.equal(page.data.subjects[0].count, 3);
});

test("schedule failure preserves selection and retry key; conflicts demand reload", async () => {
  const calls = []; let fail = true;
  const { page } = setup(async (path, options) => {
    if (!options) return result;
    calls.push({ path, options });
    if (fail) throw new Error("网络异常");
    return { due_date: "2026-10-07", over_budget_minutes: 5 };
  });
  Object.assign(page.data, { canWrite: true, asOfDay: "2026-10-06", items: [{ knowledge_id: "k", review_id: "r", state_version: 3, can_schedule: true }] });
  page.openActions(event({ id: "k" })); await page.schedule(event({ action: "tomorrow" }));
  assert.ok(page.data.target); assert.equal(page.data.actionError, "网络异常");
  fail = false; await page.schedule(event({ action: "tomorrow" }));
  assert.equal(calls[0].options.idempotencyKey, calls[1].options.idempotencyKey);
  assert.equal(calls[1].options.data.expected_version, 3);
  assert.equal(page.data.target, null); assert.match(page.data.notice, /超出日常预算 5/);
});

test("delete requires confirmation, blocks duplicate saves, viewer and late family responses", async () => {
  let release; const calls = [];
  const { page, app } = setup((path, options) => { calls.push({ path, options }); return new Promise(resolve => { release = resolve; }); });
  Object.assign(page.data, { canWrite: true, items: [{ knowledge_id: "k" }] });
  page.openActions(event({ id: "k" })); page.askDelete(); page.closeActions(); await page.confirmDelete();
  assert.equal(calls.length, 0);
  page.openActions(event({ id: "k" })); page.askDelete(); const saving = page.confirmDelete();
  await page.confirmDelete(); assert.equal(calls.length, 1); assert.equal(calls[0].options.method, "DELETE");
  app.globalData.familyId = "new-family"; page.onHide(); release(); await saving;
  assert.equal(page.data.target, null); assert.equal(calls.length, 1);
  page.visible = true; app.globalData.currentMember = { role: "viewer" };
  page.openActions(event({ id: "k" })); assert.equal(page.data.target, null);
});
