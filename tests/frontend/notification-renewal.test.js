const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const plain = (value) => JSON.parse(JSON.stringify(value));
const settle = async () => { for (let i = 0; i < 12; i += 1) await new Promise((resolve) => setImmediate(resolve)); };

function setup({ mode = "auto", callback = true, registerFailure = false } = {}) {
  const order = [];
  let native;
  let blocked = registerFailure;
  const view = { choice: mode === "onboarding" ? "unseen" : "enabled", version: 0, completion_cursor: 10,
    settings: { channel: { available: true }, preferences: [{ type: "review_digest", enabled: true,
      template_id: "tpl", remaining_quota: 0, previously_granted: true }] }, types: [] };
  const request = async (url, options = {}) => {
    order.push({ url, options });
    if (url === "/notifications/renewal") return view;
    if (url === "/notifications/grant-attempts") return { renewal: view,
      attempt: { attempt_id: "original-event", mode: options.data.mode, state: "prepared", bindings: [{ type: "review_digest", template_id: "tpl" }] } };
    if (url.endsWith("/result")) {
      if (blocked) { const error = new Error("网络未确认"); error.statusCode = 409; throw error; }
      view.settings.preferences[0].remaining_quota = options.data.results[0].decision === "accept" ? 1 : 0;
      return { state: "registered" };
    }
    return {};
  };
  const harness = loadPage("utils/notification-renewal.js", request, { globalData: { familyId: "family", currentMember: { id: "self" } },
    wx: { getSetting(options) { options.success({ subscriptionsSetting: { mainSwitch: true, itemSettings: { tpl: "accept" } } }); },
      requestSubscribeMessage(options) { order.push({ native: true }); native = options; if (callback) options.success({ tpl: "accept" }); },
      showToast() { throw new Error("automatic renewal must stay quiet"); },
      setStorageSync() { throw new Error("no business storage"); } } });
  const controller = harness.exports.createController();
  return { ...harness, controller, order, native: () => native, unblock() { blocked = false; } };
}

test("native grant starts synchronously before any request from the click", async () => {
  const { controller, order } = setup();
  await controller.refresh();
  order.length = 0;
  assert.equal(controller.complete(), true);
  assert.equal(order[0].native, true);
  await settle();
  const result = order.find((item) => item.url && item.url.endsWith("/result"));
  assert.deepEqual(plain(result.options.data.results), [{ type: "review_digest", decision: "accept" }]);
});

test("registration recovery uses the original event without a second WeChat request", async () => {
  const harness = setup({ registerFailure: true });
  await harness.controller.refresh();
  harness.controller.complete();
  await settle();
  assert.deepEqual(plain(harness.controller.pendingTypes()), ["review_digest"]);
  assert.equal(harness.controller.complete(), false);
  await settle(); // 本次点击触发的有界恢复结束后，再模拟网络恢复。
  harness.unblock();
  await harness.controller.refresh();
  assert.equal(harness.order.filter((item) => item.native).length, 1);
  assert.equal(harness.order.filter((item) => item.url && item.url.endsWith("/result")).every((item) => item.url.includes("original-event")), true);
  assert.deepEqual(plain(harness.controller.pendingTypes()), []);
});

test("late callback after identity change cannot register under the new family", async () => {
  const harness = setup({ callback: false });
  await harness.controller.refresh();
  harness.controller.complete();
  harness.app.globalData.familyId = "other-family";
  harness.native().success({ tpl: "accept" });
  await settle();
  assert.equal(harness.order.some((item) => item.url && item.url.endsWith("/result")), false);
});

test("global native lock prevents a second click until the callback", async () => {
  const harness = setup({ callback: false });
  await harness.controller.refresh();
  assert.equal(harness.controller.complete(), true);
  assert.equal(harness.controller.complete(), false);
  assert.equal(harness.order.filter((item) => item.native).length, 1);
  harness.native().fail({ errMsg: "requestSubscribeMessage:fail cancel" });
  await settle();
  const sent = harness.order.find((item) => item.url && item.url.endsWith("/result"));
  assert.equal(sent.options.data.results[0].decision, "cancel");
});

test("late native callback stays isolated after controller hide and a new identity show", async () => {
  const harness = setup({ callback: false });
  await harness.controller.refresh();
  harness.controller.complete();
  harness.controller.hide();
  harness.app.globalData.familyId = "new-family";
  harness.app.globalData.currentMember = { id: "new-member" };
  harness.controller.show();
  harness.native().success({ tpl: "accept" });
  await settle();
  assert.equal(harness.order.some((item) => item.url && item.url.endsWith("/result")), false);
});

test("expired candidates skip the gesture and never request WeChat asynchronously", async () => {
  const harness = setup();
  let elapsed = 0;
  harness.wx.getPerformance = () => ({ now: () => elapsed });
  await harness.controller.refresh();
  elapsed = 55001;
  assert.equal(harness.controller.complete(), false);
  await settle();
  assert.equal(harness.order.some((item) => item.native), false);
  assert.equal(harness.order.filter((item) => item.url === "/notifications/renewal").length, 2);
});

test("guide remains explicit and only its button can opt in", async () => {
  const harness = setup({ mode: "onboarding" });
  await harness.controller.refresh();
  assert.equal(harness.controller.guideReady(), true);
  assert.equal(harness.controller.complete(), false);
  assert.equal(harness.order.some((item) => item.native), false);
  assert.equal(harness.controller.enableFromGuide(), true);
  await settle();
  const sent = harness.order.find((item) => item.url && item.url.endsWith("/result"));
  assert.equal(sent.options.data.enable_renewal, true);
});

test("unknown and technical failures are never converted to permission", () => {
  const { exports } = loadPage("utils/notification-renewal.js", async () => ({}));
  const binding = [{ type: "review_digest", template_id: "tpl" }];
  for (const decision of ["accept", "reject", "ban", "filter"]) {
    assert.equal(exports.decisions({ tpl: decision }, binding)[0].decision, decision);
  }
  assert.equal(exports.decisions({}, binding)[0].decision, "unknown");
  assert.equal(exports.decisions(null, binding, { errMsg: "network fail" })[0].decision, "technical");
});

test("actual todo-card event reaches the synchronous renewal hook only for complete", async () => {
  const order = [];
  const { page } = loadPage("pages/today/index.js", async () => { order.push("feedback-request"); });
  page.setData({ canWrite: true, childId: "child", dashboard: { todo_groups: [], must_todo_groups: [], optional_todo_groups: [] } });
  page.renewalController = { complete() { order.push("native-hook"); }, refresh: async () => {}, guideReady: () => false };
  page.load = async () => {};
  const { page: component } = loadPage("components/todo-card/index.js", async () => ({}));
  const card = { ...component.methods, data: { canWrite: true, busyId: "", view: {} }, setData(value) { Object.assign(this.data, value); },
    triggerEvent(name, detail) { assert.equal(name, "feedback"); this.saving = page.feedback({ detail }); } };
  card.feedback({ currentTarget: { dataset: { reviewId: "review", action: "complete" } } });
  assert.deepEqual(order.slice(0, 2), ["native-hook", "feedback-request"]);
  await card.saving;
  order.length = 0;
  card.data.busyId = "";
  card.feedback({ currentTarget: { dataset: { reviewId: "other", action: "defer" } } });
  await card.saving;
  assert.deepEqual(order, ["feedback-request"]);
});
