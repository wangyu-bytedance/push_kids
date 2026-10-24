const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { createController } = require("../../apps/miniprogram/utils/grade-confirmation");
const { loadPage } = require("./harness");
const childContext = require("../../apps/miniprogram/utils/child-context");
const tick = () => new Promise((resolve) => setImmediate(resolve));
const candidate = (id, grade = "小学二年级") => ({ id, name: id, current_grade: grade,
  suggested_grade: "小学三年级", reason: "annual_progression", revision: 3 });

test("all twelve labels and exact aliases share one catalog without duplicate picker rows", () => {
  const choices = childContext.gradeChoices("一年级", true);
  assert.equal(choices.length, 14);
  assert.equal(choices[childContext.gradeChoiceIndex(choices, "一年级")].value, "小学一年级");
  assert.equal(childContext.gradeLabel("初中一年级"), "七年级");
  assert.equal(childContext.gradeLabel("初中二年级"), "八年级");
  assert.equal(childContext.gradeLabel("初中三年级"), "九年级");
});

function fixture(items = [candidate("a")], request) {
  const calls = [], bar = { data: {}, setData(data) { Object.assign(this.data, data); } };
  const page = { data: { children: items.map((item) => ({ id: item.id, grade: item.current_grade })) },
    setData(data) { Object.assign(this.data, data); }, getTabBar: () => bar };
  let top = page;
  const app = { globalData: { familyId: "family-a", selectedChildId: "a", bootstrapState: "bound",
    currentMember: { id: "parent-1", role: "manager" } },
  async refreshBootstrap() { return { children: page.data.children }; } };
  const api = { async request(url, options = {}) {
    calls.push({ url, options });
    if (request) return request(url, options);
    if (url === "/children/grade-confirmations") return { school_year: 2026, can_confirm: true, items };
    return { child: { id: url.split("/")[2], grade: options.data.grade }, outcome: "confirmed" };
  } };
  const flow = createController(app, api, () => top);
  const event = (action, extra = {}) => flow.handle(top, { action, ...extra });
  return { flow, app, page, calls, bar, event, setTop(next) { top = next; } };
}

test("five independent dialogs put selected child first, later continues, tabs do not reset", async () => {
  const f = fixture(["b", "a", "c", "d", "e"].map((id) => candidate(id)));
  f.flow.foreground(); f.event("show"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "a");
  assert.equal(f.bar.data.gradeConfirmationVisible, true);
  f.event("later"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "b");
  f.event("hide"); f.event("show"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "b");
  for (const id of ["c", "d", "e"]) {
    f.event("later"); await tick(); assert.equal(f.page.data.gradeConfirmation.id, id);
  }
  f.event("later"); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
  assert.equal(f.bar.data.gradeConfirmationVisible, false);
  assert.equal(f.app.globalData.selectedChildId, "a");
  assert.equal(f.calls.length, 1, "稍后不写共享事实，也不重复读取候选");
  f.flow.background(); f.flow.foreground(); f.event("show"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "a");
  assert.equal(f.calls.length, 2);
});

test("new foreground waits for bootstrap; blocked input defers until a safe host", async () => {
  const f = fixture(); f.app.globalData.bootstrapState = "loading";
  f.flow.foreground(); f.event("show", { blocked: true }); await tick();
  assert.equal(f.calls.length, 0);
  f.app.globalData.bootstrapState = "bound"; f.flow.bootstrapChanged(); await tick();
  assert.equal(f.calls.length, 0);
  f.event("availability", { blocked: false }); await tick();
  f.event("choose", { index: 7 });
  f.event("availability", { blocked: true });
  assert.equal(f.page.data.gradeConfirmation, null);
  f.event("availability", { blocked: false }); await tick();
  assert.equal(f.page.data.gradeConfirmation.selected_grade, "小学五年级");
});

test("native picker lifecycle never starts a second academic-year session", async () => {
  const f = fixture(); f.flow.foreground(); f.event("show"); await tick();
  f.event("picker-open"); f.flow.background(); f.event("hide"); f.flow.foreground();
  f.event("choose", { index: 4 }); await tick();
  assert.equal(f.calls.length, 1);
  assert.equal(f.page.data.gradeConfirmation.selected_grade, "小学二年级");
  f.event("later"); f.event("show"); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
});

test("manual grade confirmation or archive prunes cached dialogs before returning from profile", async () => {
  const f = fixture([candidate("a"), candidate("b"), candidate("c")]);
  f.flow.foreground();
  f.flow.bootstrapChanged(["a", "b", "c"].map((id) => ({ id, grade_revision: 3, grade_confirmed_school_year: 2025 })));
  f.event("show"); await tick();
  f.event("choose", { index: 4 }); f.event("hide");
  f.flow.bootstrapChanged([
    { id: "a", grade_revision: 4, grade_confirmed_school_year: 2026 },
    { id: "c", grade_revision: 3, grade_confirmed_school_year: 2025 }
  ]);
  f.event("show"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "c");
  assert.equal(f.calls.length, 1, "档案同步不轮询候选，也不再核对已确认或归档的孩子");
});

test("restoring an archived child refreshes once at a safe host without repeating deferred children", async () => {
  let items = [candidate("a"), candidate("b")];
  const f = fixture(items, () => ({ school_year: 2026, can_confirm: true, items }));
  f.flow.foreground();
  const active = ["a", "b"].map((id) => ({ id, grade_revision: 3, grade_confirmed_school_year: 2024 }));
  f.flow.bootstrapChanged(active); f.event("show"); await tick();
  f.event("later"); await tick();
  f.event("choose", { index: 4 });
  f.event("hide");
  items = [...items, candidate("restored")];
  const restored = [...active, { id: "restored", active: true, grade_revision: 3, grade_confirmed_school_year: 2024 }];
  f.flow.bootstrapChanged(restored); await tick();
  assert.equal(f.calls.length, 1, "档案页不抢弹核对窗口");
  f.event("show"); await tick();
  assert.equal(f.calls.length, 2);
  assert.equal(f.page.data.gradeConfirmation.id, "b");
  assert.equal(f.page.data.gradeConfirmation.selected_grade, "小学二年级");
  f.event("later"); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "restored");
  f.event("later"); f.flow.bootstrapChanged(restored); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
  assert.equal(f.calls.length, 2, "不重弹已稍后孩子，也不在普通 bootstrap 同步时轮询");
});

test("a restored child appearing during an in-flight candidate read invalidates the old response", async () => {
  let resolveOld, reads = 0;
  const f = fixture([], () => {
    reads += 1;
    return reads === 1 ? new Promise((resolve) => { resolveOld = resolve; })
      : { school_year: 2026, can_confirm: true, items: [candidate("restored")] };
  });
  f.flow.foreground(); f.flow.bootstrapChanged([]); f.event("show"); await tick();
  f.flow.bootstrapChanged([{ id: "restored", active: true, grade_revision: 3, grade_confirmed_school_year: 2024 }]);
  resolveOld({ school_year: 2026, can_confirm: true, items: [] }); await tick();
  assert.equal(reads, 2);
  assert.equal(f.page.data.gradeConfirmation.id, "restored");
});

for (const change of ["archive", "manual-confirmation"]) {
  test(`${change} invalidates an older in-flight candidate response before returning from profile`, async () => {
    let resolveOld, reads = 0;
    const f = fixture(undefined, () => {
      reads += 1;
      return reads === 1 ? new Promise((resolve) => { resolveOld = resolve; })
        : { school_year: 2026, can_confirm: true, items: [] };
    });
    f.flow.foreground();
    f.flow.bootstrapChanged([{ id: "a", grade_revision: 3, grade_confirmed_school_year: 2025 }]);
    f.event("show"); await tick(); f.event("hide");
    f.flow.bootstrapChanged(change === "archive" ? []
      : [{ id: "a", grade_revision: 4, grade_confirmed_school_year: 2026 }]);
    resolveOld({ school_year: 2026, can_confirm: true, items: [candidate("a")] }); await tick();
    f.event("show"); await tick();
    assert.equal(reads, 2);
    assert.equal(f.page.data.gradeConfirmation, null);
    assert.equal(f.bar.data.gradeConfirmationVisible, false);
  });
}

test("report filters remain unobstructed when a late candidate read completes", async () => {
  const source = fs.readFileSync("apps/miniprogram/pages/reports/index.wxml", "utf8");
  const expression = source.match(/<grade-confirmation\b[^>]*blocked="{{(.*?)}}"/)[1];
  let resolveRead;
  const f = fixture(undefined, () => new Promise((resolve) => { resolveRead = resolve; }));
  const reportState = { loading: false, showChildSheet: false, inventoryExpanded: false, filterOpen: false };
  const availability = () => f.event("availability", { blocked: vm.runInNewContext(expression, reportState) });
  f.flow.foreground(); f.event("show"); await tick();
  reportState.filterOpen = true; availability();
  resolveRead({ school_year: 2026, can_confirm: true, items: [candidate("a")] }); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
  reportState.filterOpen = false; availability(); await tick();
  assert.equal(f.page.data.gradeConfirmation.id, "a");
  assert.equal(f.calls.length, 1);
});

test("duplicate submit is blocked, errors preserve input, retry submits the same parent choice", async () => {
  let rejectPost, resolvePost;
  const f = fixture(undefined, (url) => url.endsWith("grade-confirmations")
    ? { school_year: 2026, can_confirm: true, items: [candidate("a")] }
    : new Promise((resolve, reject) => { resolvePost = resolve; rejectPost = reject; }));
  f.flow.foreground(); f.event("show"); await tick(); f.event("choose", { index: 4 });
  const first = f.event("confirm"); f.event("confirm");
  assert.equal(f.page.data.gradeConfirmation.status, "saving");
  assert.equal(f.calls.filter((call) => call.options.method === "POST").length, 1);
  rejectPost(Error("synthetic offline")); await first;
  assert.equal(f.page.data.gradeConfirmation.selected_grade, "小学二年级");
  assert.match(f.page.data.gradeConfirmation.error, /保存失败/);
  const retry = f.event("confirm"); resolvePost({ child: { id: "a", grade: "小学二年级" } }); await retry;
  assert.equal(f.page.data.gradeConfirmation, null);
  assert.deepEqual(f.calls[1].options.data, f.calls[2].options.data);
});

test("conflict refresh shows server-confirmed fact without offering an overwrite", async () => {
  let reads = 0;
  const f = fixture(undefined, (url) => {
    if (url.endsWith("grade-confirmations")) return { school_year: 2026, can_confirm: true,
      items: reads++ === 0 ? [candidate("a")] : [] };
    throw Object.assign(Error("conflict"), { statusCode: 409 });
  });
  f.app.refreshBootstrap = async () => ({ children: [{ id: "a", grade: "小学四年级", active: true }] });
  f.flow.foreground(); f.event("show"); await tick();
  await f.event("confirm"); assert.equal(f.page.data.gradeConfirmation.status, "conflict");
  await f.event("confirm"); assert.equal(f.page.data.gradeConfirmation.status, "latest");
  assert.equal(f.page.data.gradeConfirmation.currentLabel, "四年级");
  await f.event("confirm"); assert.equal(f.page.data.gradeConfirmation, null);
  assert.equal(f.calls.filter((call) => call.options.method === "POST").length, 1);
});

test("viewer, family changes and late results cannot revive an old dialog", async () => {
  let resolveRead;
  const f = fixture(undefined, () => new Promise((resolve) => { resolveRead = resolve; }));
  f.flow.foreground(); f.event("show"); await tick();
  f.app.globalData.currentMember.role = "viewer"; f.flow.bootstrapChanged();
  resolveRead({ school_year: 2026, can_confirm: true, items: [candidate("a")] }); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
  assert.equal(f.calls.length, 1);
  f.app.globalData.currentMember.role = "editor"; f.app.globalData.familyId = "family-b";
  f.flow.bootstrapChanged(); await tick();
  f.flow.background(); resolveRead({ school_year: 2026, can_confirm: true, items: [candidate("b")] }); await tick();
  assert.equal(f.page.data.gradeConfirmation, null);
});

test("late submission cannot update a different family's visible children", async () => {
  let complete;
  const f = fixture(undefined, (url) => url.endsWith("grade-confirmations")
    ? { school_year: 2026, can_confirm: true, items: [candidate("a")] }
    : new Promise((resolve) => { complete = resolve; }));
  f.flow.foreground(); f.event("show"); await tick();
  const request = f.event("confirm");
  f.app.globalData.familyId = "family-b"; f.app.globalData.currentMember.role = "viewer";
  f.flow.bootstrapChanged(); complete({ child: { id: "a", grade: "初中三年级" } }); await request;
  assert.equal(f.page.data.children[0].grade, "小学二年级");
  assert.equal(f.page.data.gradeConfirmation, null);
});

test("production App lifecycle and five tab bridges wire the shared controller", async () => {
  let definition;
  const api = { request: async () => ({ state: "bound", family: { id: "family" },
    member: { role: "manager" }, children: [] }) };
  vm.runInNewContext(fs.readFileSync(path.resolve("apps/miniprogram/app.js"), "utf8"), {
    App(value) { definition = value; }, getCurrentPages: () => [],
    wx: { getStorageSync: () => "", setStorageSync() {} },
    require(name) {
      if (name === "./config") return { useCloud: false };
      if (name.endsWith("/api")) return api;
      return require(path.resolve("apps/miniprogram", name));
    }
  });
  definition.onLaunch({ path: "pages/today/index" }); definition.onShow(); await tick();
  assert.ok(definition.gradeConfirmation);
  definition.onHide();
  for (const name of ["today", "calendar", "records", "reports", "settings"]) {
    const { page, app } = loadPage(`pages/${name}/index.js`, async () => []);
    let called = false;
    app.gradeConfirmation = { handle(host, event) { called = host === page && event.action === "show"; } };
    page.onGradeConfirmation({ detail: { action: "show" } }); assert.equal(called, true);
  }
});

test("real edit form omits untouched grade and explicitly confirms picker choices", async () => {
  const calls = [];
  const child = { id: "a", name: "小满", grade: "小学二年级", grade_revision: 7, active: true, daily_budget_minutes: 15 };
  const { page, app } = loadPage("pages/child-edit/index.js", async (url, options = {}) => {
    calls.push({ url, options });
    if (url.includes("include_archived")) return [child];
    if (url.endsWith("dashboard")) return {};
    return child;
  });
  app.refreshBootstrap = async () => ({});
  page.data.mode = "edit"; page.data.childId = "a";
  await page.load(); await page.save();
  assert.equal(Object.hasOwn(calls.find((c) => c.options.method === "PATCH").options.data, "grade"), false);
  calls.length = 0; page.chooseGrade({ detail: { value: page.data.gradeIndex } }); await page.save();
  const data = calls.find((c) => c.options.method === "PATCH").options.data;
  assert.equal(data.grade, "小学二年级"); assert.equal(data.confirm_grade, true);
  assert.equal(data.expected_grade_revision, 7);
});

test("manual grade conflict preserves drafts and requires a fresh parent choice before retrying", async () => {
  const versions = [];
  const child = { id: "a", name: "小满", grade: "小学二年级", grade_revision: 3, active: true, daily_budget_minutes: 15 };
  const { page, app } = loadPage("pages/child-edit/index.js", async (url, options = {}) => {
    if (options.method === "PATCH") {
      versions.push(options.data.expected_grade_revision);
      if (versions.length === 1) {
        child.grade = "小学四年级"; child.grade_revision = 4;
        throw Object.assign(Error("conflict"), { code: "grade_confirmation_conflict", statusCode: 409 });
      }
      return child;
    }
    return url.includes("include_archived") ? [{ ...child }] : {};
  });
  app.refreshBootstrap = async () => ({});
  page.data.mode = "edit"; page.data.childId = "a"; await page.load();
  page.setName({ detail: { value: "家长保留的名字" } }); page.chooseBudget({ detail: { value: 3 } });
  page.chooseGrade({ detail: { value: 6 } }); await page.save();
  assert.equal(page.data.nameDraft, "家长保留的名字");
  assert.equal(page.data.budgetIndex, 3); assert.equal(page.data.gradeIndex, 6);
  assert.match(page.data.error, /四年级.*重新选择年级/);
  await page.save(); assert.deepEqual(versions, [3], "刷新不会自动用新版本覆盖他人结果");
  page.chooseGrade({ detail: { value: 6 } }); await page.save();
  assert.deepEqual(versions, [3, 4]);
});

test("a failed conflict refresh cannot be bypassed by reselecting the old grade", async () => {
  let reads = 0, writes = 0;
  const child = { id: "a", name: "小满", grade: "小学二年级", grade_revision: 3, active: true };
  const { page } = loadPage("pages/child-edit/index.js", async (url, options = {}) => {
    if (options.method === "PATCH") {
      writes += 1;
      throw Object.assign(Error("conflict"), { code: "grade_confirmation_conflict" });
    }
    if (url.includes("include_archived")) {
      reads += 1;
      if (reads === 2) throw Error("synthetic offline");
      return [{ ...child, grade_revision: reads === 1 ? 3 : 4 }];
    }
    return {};
  });
  page.data.mode = "edit"; page.data.childId = "a"; await page.load();
  page.chooseGrade({ detail: { value: 5 } }); await page.save();
  assert.match(page.data.error, /读取失败/);
  page.chooseGrade({ detail: { value: 5 } }); await page.save();
  assert.equal(writes, 1); assert.equal(reads, 3);
  assert.equal(page.data.gradeRevision, 4); assert.equal(page.data.gradeConflict, true);
});

test("component forwards native picker and foreground events after the host data update", async () => {
  let component; const events = [];
  vm.runInNewContext(fs.readFileSync("apps/miniprogram/components/grade-confirmation/index.js", "utf8"), {
    Component(value) { component = value; }
  });
  const view = { data: { blocked: false }, ...component.methods,
    triggerEvent(name, event) { events.push({ name, event }); } };
  component.lifetimes.attached.call(view);
  assert.equal(events.length, 0, "组件初始化不能同步重入父页setData");
  await tick();
  view.pickerOpen(); view.choose({ detail: { value: "3" } });
  view.pickerCancel(); component.pageLifetimes.hide.call(view); await tick();
  assert.deepEqual(events.map((e) => e.event.action), ["show", "picker-open", "choose", "picker-close", "hide"]);
});
