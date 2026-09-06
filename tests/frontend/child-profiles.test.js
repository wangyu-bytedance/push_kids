const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const childContext = require("../../apps/miniprogram/utils/child-context");

/* 用真实的 child-context 装载页面，只把 api 与 wx 换成可观测的替身。 */
function loadPage(entry, request, overrides = {}) {
  let definition;
  const calls = [];
  const navigations = [];
  const toasts = [];
  const app = {
    globalData: { selectedChildId: overrides.selectedChildId || "", currentMember: overrides.member || null },
    selectChild(id) { this.globalData.selectedChildId = id; },
    refreshBootstrap: async () => ({ state: "bound", children: [] })
  };
  const filename = path.resolve(__dirname, "../../apps/miniprogram", entry);
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require(name) {
      if (name.includes("child-context")) return childContext;
      if (name.includes("utils/ui")) return { readPreference: (key, id, fallback) => fallback, writePreference() {}, subjectClass: () => "", subjectMark: () => "", monthDay: (value) => value };
      return {
        request: async (requestPath, options = {}) => { calls.push({ path: requestPath, options }); return request(requestPath, options); },
        newIdempotencyKey: () => "fixture-key"
      };
    },
    Page(value) { definition = value; },
    wx: {
      showToast(options) { toasts.push(options.title); },
      showModal(options) { if (options.success) options.success({ confirm: overrides.confirm !== false }); },
      navigateTo(options) { navigations.push(options.url); },
      navigateBack() { navigations.push("back"); },
      setNavigationBarTitle() {},
      stopPullDownRefresh() {}
    },
    getApp: () => app
  }, { filename });
  const page = {
    ...definition,
    data: JSON.parse(JSON.stringify(definition.data)),
    setData(update) { Object.assign(this.data, update); }
  };
  return { page, app, calls, navigations, toasts };
}

const profile = (id, name, extra = {}) => ({ id, name, grade: null, daily_budget_minutes: 15, active: true, ...extra });

test("child selection falls back when the stored child was archived", () => {
  const resolved = childContext.resolveSelection([profile("b", "小星")], "a");
  assert.equal(resolved.childId, "b");
  assert.equal(resolved.childIndex, 0);
  assert.equal(resolved.changed, true, "回落必须被报告出来，否则全局态会一直指向失效档案");
  assert.equal(resolved.multiChild, false);
});

test("child selection keeps the parent's choice and derives switcher labels", () => {
  const resolved = childContext.resolveSelection(
    [profile("a", "小雨"), profile("b", "小星", { grade: "小学四年级" })],
    "b"
  );
  assert.equal(resolved.childId, "b");
  assert.equal(resolved.changed, false);
  assert.equal(resolved.multiChild, true);
  assert.equal(resolved.children[1].label, "小星 · 小学四年级");
  assert.equal(resolved.children[0].label, "小雨");
  assert.equal(resolved.children[0].avatar, "小");
});

test("selection sync writes the fallback back into global state exactly once", () => {
  const writes = [];
  const app = { globalData: { selectedChildId: "gone" }, selectChild(id) { writes.push(id); this.globalData.selectedChildId = id; } };
  childContext.syncSelection(app, [profile("a", "小雨")]);
  assert.deepEqual(writes, ["a"]);
  childContext.syncSelection(app, [profile("a", "小雨")]);
  assert.deepEqual(writes, ["a"], "选择没变时不该重复写 storage");
  childContext.syncSelection(app, []);
  assert.deepEqual(writes, ["a", ""], "档案全部归档后必须清空选择");
});

test("the profile ceiling matches the server and ignores archived profiles", () => {
  const active = Array.from({ length: childContext.MAX_ACTIVE_CHILDREN }, (_, index) => profile(`c${index}`, `孩子${index}`));
  assert.equal(childContext.canAddChild(active), false);
  assert.equal(childContext.canAddChild([...active.slice(1), profile("old", "旧档案", { active: false })]), true);
});

test("settings lists profiles in use, archived profiles and an add entry", async () => {
  const profiles = [profile("a", "小雨"), profile("b", "小星"), profile("c", "毕业了", { active: false })];
  const { page, app, calls } = loadPage("pages/settings/index.js", async (requestPath) => {
    if (requestPath.startsWith("/children?include_archived")) return profiles;
    if (requestPath.endsWith("/subjects")) return [];
    if (requestPath.endsWith("/activity-schedules")) return { items: [] };
    if (requestPath === "/families/current/requests") return [];
    throw new Error(`unexpected path: ${requestPath}`);
  }, { selectedChildId: "b" });

  await page.load();

  assert.deepEqual(page.data.children.map((item) => item.id), ["a", "b"], "切换列表只放在用的档案");
  assert.deepEqual(page.data.archivedChildren.map((item) => item.id), ["c"]);
  assert.equal(page.data.childId, "b", "已经选中的档案不该被重置");
  assert.equal(app.globalData.selectedChildId, "b");
  assert.equal(page.data.canAddChild, true);
  /* 只读成员看不到写入入口，但仍要能读到档案列表。 */
  assert.equal(page.data.canWrite, true);
  assert.ok(calls.some((call) => call.path === "/children?include_archived=true"));
  assert.ok(calls.every((call) => !call.path.startsWith("/children/c/")), "不该为归档档案发起详情请求");
});

test("settings drops a stale response when the parent switched child mid-flight", async () => {
  let subjectsGate;
  const { page } = loadPage("pages/settings/index.js", async (requestPath) => {
    if (requestPath.startsWith("/children?include_archived")) return [profile("a", "小雨"), profile("b", "小星")];
    if (requestPath.endsWith("/subjects")) return new Promise((resolve) => { subjectsGate = () => resolve([{ id: "s", name: "语文", kind: "learning", active: true, is_custom: false }]); });
    if (requestPath.endsWith("/activity-schedules")) return { items: [] };
    if (requestPath === "/families/current/requests") return [];
    throw new Error(`unexpected path: ${requestPath}`);
  }, { selectedChildId: "a" });

  const first = page.load();
  await new Promise((resolve) => setImmediate(resolve));
  page.loadGeneration = page.loadGeneration + 1;
  subjectsGate();
  await first;
  assert.equal(page.data.loading, true, "迟到的响应不能覆盖新一轮加载的状态");
});

test("settings refuses to add a profile past the ceiling and never navigates", () => {
  const { page, navigations, toasts } = loadPage("pages/settings/index.js", async () => []);
  page.data.canWrite = true;
  page.data.canAddChild = false;
  page.addChild();
  assert.deepEqual(navigations, []);
  assert.match(toasts[0], /最多同时保留/);

  page.data.canAddChild = true;
  page.addChild();
  assert.deepEqual(navigations, ["/pages/child-edit/index?mode=create"]);
  assert.equal(page.data.showChildSheet, false);
});

test("read-only members cannot reach the profile form", () => {
  const { page, navigations, toasts } = loadPage("pages/settings/index.js", async () => []);
  page.data.canWrite = false;
  page.addChild();
  page.editChild({ currentTarget: { dataset: { id: "a" } } });
  assert.deepEqual(navigations, []);
  assert.match(toasts[0], /只读成员/);
});

test("creating a profile seeds the picked subjects and switches to the new child", async () => {
  const { page, app, calls, navigations } = loadPage("pages/child-edit/index.js", async (requestPath, options) => {
    if (requestPath.startsWith("/children?include_archived")) return [profile("a", "小雨")];
    if (requestPath === "/children" && options.method === "POST") return profile("new", options.data.name);
    throw new Error(`unexpected path: ${requestPath}`);
  }, { selectedChildId: "a" });

  page.onLoad({ mode: "create" });
  await new Promise((resolve) => setImmediate(resolve));
  page.setName({ detail: { value: " 小星 " } });
  page.chooseGrade({ detail: { value: 4 } });
  page.togglePreset({ currentTarget: { dataset: { index: 1 } } });
  await page.save();

  const created = calls.find((call) => call.path === "/children" && call.options.method === "POST");
  assert.equal(created.options.data.name, "小星", "名字要去掉首尾空格，避免看起来重名的两个档案");
  assert.equal(created.options.data.grade, "小学三年级");
  assert.deepEqual(created.options.data.subject_names, ["数学"]);
  assert.equal(app.globalData.selectedChildId, "new", "建完直接切过去，家长下一步就是记录");
  assert.deepEqual(navigations, ["back"]);
});

test("an empty name never reaches the server", async () => {
  const { page, calls } = loadPage("pages/child-edit/index.js", async (requestPath) => {
    if (requestPath.startsWith("/children?include_archived")) return [];
    throw new Error(`unexpected path: ${requestPath}`);
  });
  page.onLoad({ mode: "create" });
  await new Promise((resolve) => setImmediate(resolve));
  page.setName({ detail: { value: "   " } });
  await page.save();
  assert.equal(calls.filter((call) => call.options.method === "POST").length, 0);
  assert.match(page.data.error, /请填写孩子的名字/);
});

test("a rejected create keeps the form so the parent can fix the name", async () => {
  const { page, navigations } = loadPage("pages/child-edit/index.js", async (requestPath, options) => {
    if (requestPath.startsWith("/children?include_archived")) return [profile("a", "小雨")];
    if (options.method === "POST") throw new Error("这个名字已经在用了，换一个更好区分的名字");
    throw new Error(`unexpected path: ${requestPath}`);
  });
  page.onLoad({ mode: "create" });
  await new Promise((resolve) => setImmediate(resolve));
  page.setName({ detail: { value: "小雨" } });
  await page.save();
  assert.equal(page.data.nameDraft, "小雨");
  assert.equal(page.data.saving, false);
  assert.match(page.data.error, /这个名字已经在用了/);
  assert.deepEqual(navigations, [], "失败不能把家长弹回上一页");
});

test("editing an archived profile shows restore instead of archive", async () => {
  const { page, calls } = loadPage("pages/child-edit/index.js", async (requestPath, options = {}) => {
    if (requestPath.startsWith("/children?include_archived")) {
      return [profile("c", "毕业了", { active: false, grade: "小学六年级", daily_budget_minutes: 30 })];
    }
    if (requestPath === "/children/c/restore" && options.method === "POST") return profile("c", "毕业了");
    throw new Error(`unexpected path: ${requestPath}`);
  });

  page.onLoad({ mode: "edit", child_id: "c" });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(page.data.active, false);
  assert.equal(page.data.nameDraft, "毕业了");
  assert.equal(page.data.budgetOptions[page.data.budgetIndex], 30);

  await page.restore();
  assert.ok(calls.some((call) => call.path === "/children/c/restore"));
  assert.equal(page.data.active, true);
});

test("archiving asks first and reports the server's refusal", async () => {
  const { page, calls } = loadPage("pages/child-edit/index.js", async (requestPath, options = {}) => {
    if (requestPath.startsWith("/children?include_archived")) return [profile("a", "小雨")];
    if (requestPath === "/children/a/archive" && options.method === "POST") throw new Error("只有家庭管理员可以执行此操作");
    throw new Error(`unexpected path: ${requestPath}`);
  }, { confirm: false });

  page.onLoad({ mode: "edit", child_id: "a" });
  await new Promise((resolve) => setImmediate(resolve));
  await page.archive();
  assert.equal(calls.filter((call) => call.path.includes("/archive")).length, 0, "家长取消时不能发出归档请求");

  page.data.working = false;
  await page.lifecycle("archive", "已归档");
  assert.match(page.data.error, /只有家庭管理员/);
  assert.equal(page.data.working, false);
});
