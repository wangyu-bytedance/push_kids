const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

function plain(value) { return JSON.parse(JSON.stringify(value)); }

function todayDashboard(overrides = {}) {
  return {
    day: "2026-09-12",
    todo_groups: [], todo_count: 0, required_todo_count: 0, estimated_minutes: 0,
    todo_next_cursor: null, todo_remaining_count: 0,
    pending_confirmation_count: 0, analyzing_count: 0, failed_count: 0,
    daily_summary: { subjects: [], record_count: 1 },
    schedule_items: [], activity_suggestions: [],
    next_review: null,
    ...overrides
  };
}

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

test("Today uses the stable daily selection instead of the full due Todo list", async () => {
  const fullDue = [{ id: "legacy", subject_name: "数学", optional: false, estimated_minutes: 20,
    items: [{ review_id: "legacy-review", knowledge_name: "不应展示" }] }];
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child", name: "小雨", active: true }];
    if (requestPath === "/children/child/subjects") return [];
    if (requestPath === "/children/child/dashboard") return todayDashboard({
      todo_groups: fullDue, todo_count: 12, required_todo_count: 12, estimated_minutes: 20,
      todo_next_cursor: "legacy-next", todo_remaining_count: 11,
      review_selection: {
        plan_id: "plan", selected_count: 2, planned_count: 2, selected_minutes: 4,
        backlog_count: 10, today_feedback_count: 0,
        sessions: [{ id: "plan:math", subject_id: "math", subject_name: "数学", estimated_minutes: 4,
          items: [
            { review_id: "r1", knowledge_name: "乘法", review_method: "口头回顾", estimated_minutes: 2 },
            { review_id: "r2", knowledge_name: "除法", review_method: "口头回顾", estimated_minutes: 2 }
          ] }]
      }
    });
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/today/index.js", request);

  await page.load();

  assert.equal(page.data.stablePlan, true);
  assert.equal(page.data.dashboard.todo_count, 2);
  assert.equal(page.data.dashboard.todo_next_cursor, null);
  assert.deepEqual(Array.from(page.data.todoCards[0].items, (item) => item.review_id), ["r1", "r2"]);
  assert.equal(page.data.hero.note, "今天先做 2 项，其余 10 项会按最早到期顺序安排到后续复习。");
  assert.equal(page.data.sectionMeta.review, "今天安排 2 项 · 约 4 分钟");
});

test("Today reports a completed fixed plan without refilling it", async () => {
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child", name: "小雨", active: true }];
    if (requestPath === "/children/child/subjects") return [];
    if (requestPath === "/children/child/dashboard") return todayDashboard({
      todo_groups: [{ id: "refill", items: [{ review_id: "should-not-refill" }] }], todo_count: 1,
      review_selection: {
        plan_id: "plan", selected_count: 0, planned_count: 3, selected_minutes: 0,
        backlog_count: 4, today_feedback_count: 3, sessions: []
      }
    });
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/today/index.js", request);

  await page.load();

  assert.equal(page.data.planCompleted, true);
  assert.equal(page.data.dashboard.todo_count, 0);
  assert.deepEqual(plain(page.data.todoCards), []);
  assert.equal(page.data.hero.note, "今天安排的 3 项已完成，今天不会再补入新内容。");
  assert.equal(page.data.sectionMeta.review, "今天 3 项已完成");
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

test("Today shows the nearest scheduled review when nothing is due today", async () => {
  const nextReview = {
    day: "2026-09-13", total_count: 3, estimated_minutes: 6,
    returned_count: 3, remaining_count: 0, next_cursor: null,
    groups: [{
      id: "english-read-scheduled", subject_id: "english", subject_name: "英语",
      review_method: "朗读", estimated_minutes: 6,
      items: [
        { review_id: "r1", knowledge_name: "动作词汇：run、jump、swim、dance、sing", due_date: "2026-09-13" },
        { review_id: "r2", knowledge_name: "can't + 动词的用法", due_date: "2026-09-13" },
        { review_id: "r3", knowledge_name: "配套朗读与练习", due_date: "2026-09-13" }
      ]
    }]
  };
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child", name: "小雨", avatar: "雨", active: true }];
    if (requestPath === "/children/child/dashboard") return todayDashboard({ next_review: nextReview });
    if (requestPath === "/children/child/subjects") return [{ id: "english", name: "英语", kind: "learning", active: true }];
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/today/index.js", request);

  await page.load();

  assert.equal(page.data.sectionMeta.review, "今天 0 项 · 明天 3 项");
  assert.equal(page.data.sections.review, true);
  assert.equal(page.data.nextReview.dayLabel, "明天 · 9 月 13 日");
  assert.equal(page.data.nextReview.summary, "3 项 · 约 6 分钟");
  assert.equal(page.data.nextReview.groups[0].subjectMark, "英");
  assert.equal(page.data.nextReview.groups[0].items[0].name, "动作词汇：run、jump、swim、dance、sing");
  assert.equal(page.data.upcomingError, "");
});

test("Today distinguishes an old dashboard from an explicitly empty future plan", async () => {
  let dashboard = todayDashboard({ next_review: null });
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child", name: "小雨", active: true }];
    if (requestPath === "/children/child/dashboard") return dashboard;
    if (requestPath === "/children/child/subjects") return [];
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/today/index.js", request);

  await page.load();
  assert.equal(page.data.nextReviewKnown, true);
  assert.equal(page.data.nextReview, null);

  dashboard = todayDashboard();
  delete dashboard.next_review;
  await page.load();
  assert.equal(page.data.nextReviewKnown, false);
  assert.equal(page.data.nextReview, null);
  assert.equal(page.data.sectionMeta.review, "今天 0 项");
});

test("Today does not show first-use guidance when a future review plan already exists", async () => {
  async function request(requestPath) {
    if (requestPath === "/children") return [{ id: "child", name: "小雨", active: true }];
    if (requestPath === "/children/child/dashboard") return todayDashboard({
      daily_summary: { subjects: [], record_count: 0 },
      next_review: {
        day: "2026-09-13", total_count: 1, estimated_minutes: 2,
        returned_count: 1, remaining_count: 0, next_cursor: null,
        groups: [{ id: "math-read", subject_name: "数学", review_method: "朗读",
          estimated_minutes: 2, items: [{ review_id: "r1", knowledge_name: "乘法", due_date: "2026-09-13" }] }]
      }
    });
    if (requestPath === "/children/child/subjects") return [];
    throw new Error(`unexpected path: ${requestPath}`);
  }
  const { page } = loadPage("pages/today/index.js", request);

  await page.load();

  assert.equal(page.data.dashboard.show_guide, false);
  assert.equal(page.data.sections.review, true);
});

test("Today appends bounded upcoming pages without duplicates and retains rows on retryable failure", async () => {
  let shouldFail = false;
  const paths = [];
  async function request(requestPath) {
    paths.push(requestPath);
    if (shouldFail) throw new Error("后续安排暂时没加载出来");
    return {
      day: "2026-09-13", total_count: 3, estimated_minutes: 6,
      returned_count: 2, remaining_count: 0, next_cursor: null,
      groups: [{ id: "english-read-scheduled", subject_id: "english", subject_name: "英语", review_method: "朗读", estimated_minutes: 4,
        items: [
          { review_id: "r1", knowledge_name: "重复项", due_date: "2026-09-13" },
          { review_id: "r2", knowledge_name: "新增项", due_date: "2026-09-13" }
        ] }]
    };
  }
  const { page } = loadPage("pages/today/index.js", request);
  page.loadGeneration = 2;
  page.data.childId = "child";
  page.data.dashboard = todayDashboard({ next_review: { day: "2026-09-13", total_count: 3, estimated_minutes: 6,
    returned_count: 1, remaining_count: 2, next_cursor: "cursor+/=", groups: [] } });
  page.data.nextReview = { day: "2026-09-13", groups: [{ id: "english-read-scheduled", subject_id: "english", subject_name: "英语", review_method: "朗读", estimated_minutes: 2,
    items: [{ reviewId: "r1", name: "重复项", dueDate: "2026-09-13" }] }], remainingCount: 2, nextCursor: "cursor+/=" };

  await page.expandUpcoming();

  assert.deepEqual(paths, ["/children/child/upcoming-reviews?after=2026-09-12&limit=20&cursor=cursor%2B%2F%3D"]);
  assert.deepEqual(Array.from(page.data.nextReview.groups[0].items, (item) => item.reviewId), ["r1", "r2"]);
  assert.equal(page.data.nextReview.remainingCount, 0);
  assert.equal(page.data.nextReview.nextCursor, null);

  page.data.nextReview.nextCursor = "retry";
  page.data.nextReview.remainingCount = 1;
  shouldFail = true;
  await page.expandUpcoming();

  assert.deepEqual(Array.from(page.data.nextReview.groups[0].items, (item) => item.reviewId), ["r1", "r2"]);
  assert.equal(page.data.nextReview.nextCursor, "retry");
  assert.equal(page.data.upcomingError, "后续安排暂时没加载出来");
  assert.equal(page.data.loadingMoreUpcoming, false);
});

test("Today ignores a late upcoming page after the selected child changes", async () => {
  let resolvePage;
  const pending = new Promise((resolve) => { resolvePage = resolve; });
  const { page } = loadPage("pages/today/index.js", () => pending);
  page.loadGeneration = 8;
  page.data.childId = "child-a";
  page.data.dashboard = todayDashboard({ next_review: { day: "2026-09-13", next_cursor: "late" } });
  page.data.nextReview = { day: "2026-09-13", groups: [], remainingCount: 1, nextCursor: "late" };

  const loading = page.expandUpcoming();
  page.loadGeneration = 9;
  page.data.childId = "child-b";
  page.data.nextReview = null;
  resolvePage({ day: "2026-09-13", groups: [{ id: "stale", items: [{ review_id: "stale" }] }], remaining_count: 0 });
  await loading;

  assert.equal(page.data.childId, "child-b");
  assert.equal(page.data.nextReview, null);
});
