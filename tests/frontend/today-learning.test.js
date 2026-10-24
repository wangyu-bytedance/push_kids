const test = require("node:test"), assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const initial = () => ({ day: "2026-10-24", version: 1, eligibility: "eligible", task: null, proposal: null, job: null });
function setup(request, canWrite = true, options = {}) {
  const harness = loadPage("components/today-learning/index.js", request, { ...options, wx: { nextTick(fn) { fn(); }, ...options.wx }, globalData: { familyId: "family", currentMember: { id: "parent", role: canWrite ? "manager" : "viewer" } } });
  const c = harness.page;
  Object.assign(c, c.methods);
  c.triggerEvent = () => {};
  c.data.childId = "child"; c.data.canWrite = canWrite; c.reset();
  return { ...harness, c };
}

test("empty snapshots hide the whole region without starting a request", () => {
  let requests = 0;
  const { c } = setup(async () => { requests += 1; return initial(); });
  for (const eligibility of ["disabled", "inactive", "no_history", "missing_grade", "no_subject", "warming_up", "recent_new", "unknown", "eligible"]) {
    c.setCurrent({ ...initial(), eligibility, can_regenerate: eligibility === "eligible" });
    assert.equal(c.data.card, "", eligibility);
  }
  c.setCurrent(null);
  assert.equal(c.data.card, ""); assert.equal(requests, 0);
});

test("task wins over qualification and proposal while unapproved content needs write permission", () => {
  const { c } = setup(async () => initial());
  const proposal = { id: "proposal", title: "具体建议" }, task = { id: "task" };
  for (const eligibility of ["disabled", "recent_new", "pending", "unknown"]) {
    c.setCurrent({ ...initial(), eligibility, proposal, task });
    assert.equal(c.data.card, "task", eligibility);
    c.data.canWrite = false; c.properties.canWrite.observer.call(c, false);
    assert.equal(c.data.card, "task", "viewer retains approved task");
    c.data.canWrite = true;
  }
  c.setCurrent({ ...initial(), proposal }); assert.equal(c.data.card, "proposal");
  c.setCurrent({ ...initial(), proposal, eligibility: "disabled" }); assert.equal(c.data.card, "");
  c.setCurrent({ ...initial(), proposal });
  c.data.canWrite = false; c.properties.canWrite.observer.call(c, false);
  assert.equal(c.data.card, "");
  c.data.canWrite = true; c.properties.canWrite.observer.call(c, true);
  assert.equal(c.data.card, "proposal");
});

test("only actionable progress and recovery retain an entry and never write on projection", () => {
  let writes = 0;
  const { c } = setup(async () => { writes += 1; return initial(); });
  const cases = [
    [{ job: { state: "queued" } }, "generating"],
    [{ job: { state: "running" } }, "generating"],
    [{ job: { state: "failed" } }, "generation-error"],
    [{ stale: true }, "stale"],
    [{ eligibility: "recent_new", can_regenerate: true }, "recover"],
    [{ eligibility: "warming_up", can_regenerate: true }, "recover"],
    [{ eligibility: "eligible", can_regenerate: true }, ""],
    [{ job: { state: "unknown" } }, ""]
  ];
  for (const [snapshot, expected] of cases) {
    c.data.canWrite = true; c.setCurrent({ ...initial(), ...snapshot });
    assert.equal(c.data.card, expected);
    c.data.canWrite = false; c.properties.canWrite.observer.call(c, false);
    assert.equal(c.data.card, "", "viewer has no unapproved entry");
  }
  assert.equal(writes, 0);
});

test("hidden eligible card still claims automatic prompt, and failed reads retain content and retry", async () => {
  let fail = false, claims = 0;
  const proposal = { id: "proposal", title: "实际建议" };
  const { c } = setup(async (url) => {
    if (fail) throw Error("网络暂时不可用");
    if (url.endsWith("/automatic-prompt")) { claims += 1; return { can_auto_open: false, current: { ...initial(), proposal } }; }
    return initial();
  });
  await c.refresh(true);
  assert.equal(claims, 1); assert.equal(c.data.card, "proposal");
  fail = true; await c.refresh(false);
  assert.equal(c.data.card, "proposal"); assert.match(c.data.error, /网络/);
  fail = false; await c.refresh(false);
  assert.equal(c.data.card, ""); assert.equal(c.data.error, "");
  c.reset(); assert.equal(c.data.current, null); assert.equal(c.data.card, "");
});

test("viewer and claimed shared prompt cannot consume another automatic display", async () => {
  let writes = 0;
  const { c } = setup(async (url, options = {}) => {
    if (options.method === "POST") { writes += 1; return { can_auto_open: false }; }
    return initial();
  }, false);
  await c.refresh(true); assert.equal(writes, 0); assert.equal(c.data.sheet, "");
  c.data.canWrite = true; await c.refresh(true);
  assert.equal(writes, 1); assert.equal(c.data.sheet, "");
});

test("identity changes and hidden pages discard late results", async () => {
  let resolve;
  const { c, app } = setup(() => new Promise((done) => { resolve = done; }));
  const loading = c.refresh(false);
  app.globalData.familyId = "another-family"; resolve(initial()); await loading;
  assert.equal(c.data.current, null);
  c.reset(); const second = c.refresh(false); c.hide(); resolve(initial()); await second;
  assert.equal(c.data.current, null); assert.equal(c.data.loading, false);
});

test("generation polling is bounded and stops when hidden", () => {
  const { c, timers } = setup(async () => initial());
  c.data.current = { ...initial(), job: { state: "running" } };
  for (let i = 0; i < 9; i += 1) c.poll();
  assert.equal(c.pollCount, 8); assert.equal(c.data.pollStopped, true);
  c.hide(); assert.equal(timers.size, 0);
});

test("other parent dialogs defer the automatic prompt without consuming its claim", async () => {
  let claims = 0;
  const { c } = setup(async (_url, options = {}) => {
    if (options.method === "POST") { claims += 1; return { can_auto_open: false }; }
    return initial();
  });
  c.data.blocked = true;
  await c.refresh(true);
  assert.equal(claims, 0); assert.equal(c.data.sheet, "");
  c.data.blocked = false;
  await c.refresh(true);
  assert.equal(claims, 1);
});

test("losing edit permission keeps confirmed tasks readable", async () => {
  const task = { id: "approved-task", state: "planned" };
  const { c } = setup(async () => ({ ...initial(), eligibility: "pending", task }));
  c.data.canWrite = false;
  c.properties.canWrite.observer.call(c, false);
  await c.refresh(true);
  assert.equal(c.data.current.task.id, task.id);
  assert.notEqual(c.visible, false);
});

test("approval only calls approval endpoint and retains its idempotency key", async () => {
  const calls = [];
  const { c } = setup(async (url, options = {}) => { calls.push({ url, options }); return initial(); });
  c.data.current = { ...initial(), proposal: { id: "proposal", version: 3 } };
  await c.approve();
  assert.equal(calls[0].url, "/children/child/learning-suggestions/proposal/approve");
  assert.equal(calls[0].options.data.expected_version, 3);
  assert.ok(calls[0].options.idempotencyKey);
  assert.equal(calls.some((x) => x.url.includes("/submissions")), false);
});

test("invalid suggestion titles preserve input, focus the field and send zero requests", async () => {
  let writes = 0;
  const { c } = setup(async () => { writes += 1; return initial(); });
  const proposal = { id: "proposal", version: 1, title: "用积木表示加法", instructions: "摆出两组积木", estimated_minutes: 12 };
  c.setCurrent({ ...initial(), proposal });
  for (const title of ["", "  ", "题".repeat(21), "题".repeat(120), "活动\n步骤", "活动\u2028步骤"]) {
    c.edit(); c.field({ currentTarget: { dataset: { field: "editTitle" } }, detail: { value: title } });
    await c.saveEdit();
    assert.equal(c.data.editTitle, title); assert.ok(c.data.titleError);
    assert.equal(c.data.focusTitle, true); assert.equal(c.data.sheet, "edit");
  }
  assert.equal(writes, 0);
});

test("suggestion title counter counts code points and trims only edges before saving", async () => {
  const calls = [], proposal = { id: "proposal", version: 1, title: "用积木表示加法", instructions: "摆出两组积木" };
  const { c } = setup(async (url, options = {}) => {
    calls.push({ url, options });
    return { ...initial(), proposal: { ...proposal, title: "𠀀".repeat(20) } };
  });
  c.setCurrent({ ...initial(), proposal }); c.edit();
  c.field({ currentTarget: { dataset: { field: "editTitle" } }, detail: { value: "  " + "𠀀".repeat(20) + "  " } });
  assert.equal(c.data.editTitleCount, 20); assert.equal(c.data.titleError, "");
  await c.saveEdit();
  assert.equal(calls[0].options.method, "PATCH"); assert.equal(calls[0].options.data.title, "𠀀".repeat(20));
  assert.equal(c.data.current.proposal.title, "𠀀".repeat(20)); assert.equal(c.data.sheet, "proposal");
});

test("legacy suggestion title is retained in edit and must be shortened by the parent", async () => {
  const calls = [], proposal = { id: "proposal", version: 1, title: "题".repeat(120), instructions: "原学习内容" };
  const { c } = setup(async (url, options = {}) => { calls.push({ url, options }); return { ...initial(), proposal }; });
  c.setCurrent({ ...initial(), proposal }); c.edit();
  assert.equal(c.data.editTitle, proposal.title); assert.equal(c.data.editTitleCount, 120); assert.ok(c.data.titleError);
  await c.saveEdit(); assert.equal(calls.length, 0);
  c.field({ currentTarget: { dataset: { field: "editTitle" } }, detail: { value: "家长精简的标题" } });
  assert.equal(c.data.titleError, ""); await c.saveEdit();
  assert.equal(calls[0].options.data.title, "家长精简的标题");
  assert.equal(calls[0].options.data.instructions, "原学习内容");
});

test("suggestion edit pending blocks close and duplicate save, failure retains draft and retry key", async () => {
  let reject, fail = true, generated = 0; const keys = [];
  const proposal = { id: "proposal", version: 1, title: "用积木表示加法", instructions: "原学习内容", estimated_minutes: 12 };
  const { c } = setup(async (_url, options = {}) => {
    if (options.method === "PATCH") { keys.push(options.idempotencyKey); if (fail) return new Promise((_resolve, rejectRequest) => { reject = rejectRequest; }); }
    return { ...initial(), proposal };
  }, true, { api: { newIdempotencyKey: () => `edit-key-${++generated}` } });
  c.setCurrent({ ...initial(), proposal }); c.edit();
  c.field({ currentTarget: { dataset: { field: "editTitle" } }, detail: { value: "换个情境表示加法" } });
  const saving = c.saveEdit(); c.close(); await c.saveEdit();
  assert.equal(keys.length, 1); assert.equal(c.data.sheet, "edit"); assert.equal(c.data.busy, true);
  reject(Error("保存失败")); await saving;
  assert.equal(c.data.editTitle, "换个情境表示加法"); assert.equal(c.data.editInstructions, "原学习内容");
  assert.equal(c.data.editMinutes, "12"); assert.equal(c.data.sheet, "edit"); assert.match(c.data.error, /保存失败/);
  fail = false; await c.saveEdit(); assert.equal(keys[0], keys[1]); assert.equal(c.data.sheet, "proposal");
  assert.equal(generated, 1);
  c.edit(); await c.saveEdit(); assert.equal(generated, 2); assert.notEqual(keys[2], keys[1]);
  c.reset(); assert.equal(c.data.editTitleCount, 0); assert.equal(c.data.titleError, "");
});

test("queued title error focus cannot affect a reset or hidden child context", async () => {
  const ticks = [];
  const { c } = setup(async () => initial(), true, { wx: { nextTick(fn) { ticks.push(fn); } } });
  for (const invalidate of [() => c.reset(), () => c.hide()]) {
    c.reset(); c.setCurrent({ ...initial(), proposal: { id: "proposal", title: "题".repeat(21), instructions: "实际内容" } });
    c.edit(); await c.saveEdit(); assert.equal(c.data.focusTitle, false);
    invalidate(); ticks.shift()(); assert.equal(c.data.focusTitle, false);
  }
});

test("confirmed actual content retries the same intent and never reconfirms", async () => {
  const calls = []; let failLink = true;
  const task = { id: "task", version: 2, content: { subject_id: "math", subject_name: "数学" } };
  const { c } = setup(async (url, options = {}) => {
    calls.push({ url, options });
    if (url.endsWith("/record-intents")) return { id: "intent", submission_idempotency_key: "stable-server-key" };
    if (url === "/submissions") return { id: "submission" };
    if (url === "/submissions/submission") return { state: "confirmed" };
    if (url.endsWith("/records") && options.method === "POST" && failLink) { failLink = false; throw Error("network"); }
    return { ...initial(), eligibility: "pending", task };
  });
  c.data.current = { ...initial(), task };
  c.data.actual = "实际只学了这一点"; c.data.actualDate = "2026-01-01"; c.data.actualTime = "10:00";
  const event = { currentTarget: { dataset: { mode: "partial" } } };
  await c.record(event); assert.equal(c.data.lockedActual, true); assert.ok(c.attempt);
  await c.record(event);
  assert.equal(calls.filter((x) => x.url.endsWith("/record-intents")).length, 1);
  assert.equal(calls.filter((x) => x.url === "/submissions").length, 1);
  assert.equal(calls.some((x) => x.url.endsWith("/confirm")), false);
  assert.equal(calls.find((x) => x.url.endsWith("/record-intents")).options.data.mode, "partial");
  assert.equal(calls.find((x) => x.url === "/submissions").options.data.input_text, "实际只学了这一点");
  assert.equal(c.attempt, null);
});

test("pending approval prevents duplicate or close and a failed retry keeps proposal and key", async () => {
  let rejectApproval, count = 0;
  const keys = [], proposal = { id: "proposal", version: 3, title: "保持这项建议" };
  const { c } = setup(async (url, options = {}) => {
    if (url.endsWith("/approve")) {
      count += 1; keys.push(options.idempotencyKey);
      if (count === 1) return new Promise((_resolve, reject) => { rejectApproval = reject; });
      return {};
    }
    return { ...initial(), eligibility: "pending", task: { id: "approved-task" } };
  });
  c.data.current = { ...initial(), proposal }; c.setSheet("proposal");
  const pending = c.approve();
  assert.equal(c.data.busy, true); assert.equal(c.data.busyAction, "approve");
  c.close(); await c.approve(); assert.equal(count, 1); assert.equal(c.data.sheet, "proposal");
  rejectApproval(Error("暂时无法连接")); await pending;
  assert.equal(c.data.busy, false); assert.equal(c.data.busyAction, "");
  assert.equal(c.data.current.proposal.title, proposal.title); assert.equal(c.data.sheet, "proposal");
  assert.match(c.data.error, /暂时无法连接/);
  await c.approve();
  assert.equal(keys[0], keys[1]); assert.equal(c.data.sheet, "");
});

test("unknown review selection and viewer cannot emit feedback", () => {
  const harness = loadPage("components/todo-card/index.js", async () => ({}));
  const c = harness.page; Object.assign(c, c.methods);
  let events = 0; c.triggerEvent = () => { events += 1; };
  c.data.canWrite = true;
  c.buildView({ items: [{ review_id: "future", selection_kind: "new-unknown-kind" }] });
  c.sendFeedback("future", "complete"); assert.equal(events, 0);
  c.data.canWrite = false; c.sendFeedback("other", "complete"); assert.equal(events, 0);
});
