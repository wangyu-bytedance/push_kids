const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

function plain(value) { return JSON.parse(JSON.stringify(value)); }

test("reports consume server-side activity aggregates without loading raw histories", async () => {
  const paths = [];
  async function request(requestPath) {
    paths.push(requestPath);
    if (requestPath === "/children") return [{ id: "child", name: "小雨", active: true }];
    if (requestPath === "/children/child/report?days=7") return {
      overview: { learning_records: 0, new_knowledge_items: 0, review_feedback_count: 0, activity_records: 101 },
      subjects: [],
      activity_subjects: [{
        subject_id: "swim", subject_name: "游泳", records: 101,
        minutes: 3030, last_occurred_on: "2026-09-11"
      }],
      review_urgency: [],
      review_activity: []
    };
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/reports/index.js", request);

  await page.load();

  assert.deepEqual(paths, ["/children", "/children/child/report?days=7"]);
  assert.deepEqual(plain(page.data.activityRows), [{
    id: "swim",
    name: "游泳",
    count: 101,
    minutes: 3030,
    lastDay: "2026-09-11",
    iconClass: "ico-swim-pri",
    meta: "101 次 · 共 3030 分钟 · 上次 09-11"
  }]);
  assert.equal(page.data.activityDetailFailed, false);
});

test("Today loads the next Todo page for the same day and keeps prior rows", async () => {
  const paths = [];
  async function request(requestPath) {
    paths.push(requestPath);
    return {
      groups: [{
        id: "english-read",
        subject_id: "english",
        subject_name: "英语",
        review_method: "朗读",
        optional: true,
        estimated_minutes: 2,
        items: [{ review_id: "review-2", knowledge_name: "课文", estimated_minutes: 2 }]
      }],
      next_cursor: null,
      remaining_count: 0
    };
  }
  const { page } = loadPage("pages/today/index.js", request);
  page.loadGeneration = 4;
  page.data.childId = "child";
  page.data.dashboard = {
    day: "2026-09-10",
    todo_groups: [{
      id: "math-oral",
      subject_id: "math",
      subject_name: "数学",
      review_method: "口头回顾",
      optional: false,
      estimated_minutes: 1,
      items: [{ review_id: "review-1", knowledge_name: "乘法", estimated_minutes: 1 }]
    }],
    must_todo_groups: [],
    optional_todo_groups: [],
    todo_next_cursor: "cursor+/=",
    todo_remaining_count: 1
  };
  page.data.dashboard.must_todo_groups = page.data.dashboard.todo_groups;

  await page.expandTodos();

  assert.deepEqual(paths, [
    "/children/child/todos?day=2026-09-10&limit=50&cursor=cursor%2B%2F%3D"
  ]);
  assert.deepEqual(
    Array.from(page.data.todoCards, (group) => group.items[0].review_id),
    ["review-1", "review-2"]
  );
  assert.equal(page.data.dashboard.todo_next_cursor, null);
  assert.equal(page.data.hiddenTodoCount, 0);
  assert.equal(page.data.loadingMoreTodos, false);
});

test("Today retains loaded Todos when the next page fails", async () => {
  const { page } = loadPage("pages/today/index.js", async () => {
    throw new Error("网络暂不可用");
  });
  page.loadGeneration = 1;
  page.data.childId = "child";
  page.data.dashboard = {
    day: "2026-09-10",
    todo_groups: [{ id: "loaded", optional: false, estimated_minutes: 1,
      items: [{ review_id: "review-loaded", estimated_minutes: 1 }] }],
    must_todo_groups: [{ id: "loaded", optional: false, estimated_minutes: 1,
      items: [{ review_id: "review-loaded", estimated_minutes: 1 }] }],
    optional_todo_groups: [],
    todo_next_cursor: "next",
    todo_remaining_count: 1
  };

  await page.expandTodos();

  assert.equal(page.data.todoCards[0].items[0].review_id, "review-loaded");
  assert.equal(page.data.dashboard.todo_next_cursor, "next");
  assert.equal(page.data.error, "网络暂不可用");
  assert.equal(page.data.loadingMoreTodos, false);
});

test("Today discards a late Todo page after the child generation changes", async () => {
  let resolvePage;
  const pending = new Promise((resolve) => { resolvePage = resolve; });
  const { page } = loadPage("pages/today/index.js", () => pending);
  page.loadGeneration = 2;
  page.data.childId = "child-a";
  page.data.dashboard = {
    day: "2026-09-10", todo_groups: [], must_todo_groups: [], optional_todo_groups: [],
    todo_next_cursor: "late", todo_remaining_count: 1
  };

  const loading = page.expandTodos();
  page.loadGeneration = 3;
  page.data.childId = "child-b";
  page.data.loadingMoreTodos = false;
  page.data.dashboard = {
    day: "2026-09-11", todo_groups: [], must_todo_groups: [], optional_todo_groups: [],
    todo_next_cursor: null, todo_remaining_count: 0
  };
  resolvePage({ groups: [{ id: "stale", items: [{ review_id: "stale" }] }], remaining_count: 0 });
  await loading;

  assert.equal(page.data.childId, "child-b");
  assert.deepEqual(plain(page.data.dashboard.todo_groups), []);
  assert.equal(page.data.loadingMoreTodos, false);
});
