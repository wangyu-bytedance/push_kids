const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const notifications = require("../../apps/miniprogram/utils/notifications");

function payload() {
  return { choice: "enabled", version: 1, completion_cursor: 6,
    settings: { channel: { available: true, reason: "" }, last_sent_at: "2026-09-05T19:00:00",
      preferences: [
        { type: "review_digest", label: "复习提醒", description: "每天19点", enabled: true, template_id: "tpl-digest", remaining_quota: 1 },
        { type: "schedule_reminder", label: "日程提醒", enabled: true, template_id: "tpl-schedule", remaining_quota: 0 }
      ] },
    types: [{ type: "review_digest", status: "has_quota", cooldown_remaining: 10 },
      { type: "schedule_reminder", status: "cooldown", cooldown_remaining: 4 }] };
}

function screen({ view = payload(), history = [], writeError = false, wx = {} } = {}) {
  const calls = [];
  const request = async (url, options = {}) => {
    calls.push({ url, options });
    if (url === "/notifications/deliveries") { if (history instanceof Error) throw history; return history; }
    if (writeError && options.method === "PATCH") throw new Error("网络异常");
    if (url === "/notifications/grant-attempts") return { attempt: null, renewal: view };
    return view;
  };
  const harness = loadPage("pages/notifications/index.js", request, { wx });
  return { ...harness, calls };
}

test("settings separate opt-in, current quota and per-type cooldown", async () => {
  const { page } = screen();
  page.onLoad();
  await page.load();
  assert.equal(page.data.loading, false);
  assert.equal(page.data.autoEnabled, true);
  assert.equal(page.data.items[0].statusText, "可发送 1 次");
  assert.equal(page.data.items[1].statusText, "还需完成 4 条复习");
  assert.equal(page.data.grantCount, 1);
  assert.equal(page.data.lastSentLabel, "09-05 19:00");
});

test("failed preference and automatic-choice writes retain the server value", async () => {
  const { page } = screen({ writeError: true });
  await page.load();
  await page.toggle({ currentTarget: { dataset: { type: "review_digest" } }, detail: { value: false } });
  assert.equal(page.data.items[0].enabled, true);
  assert.equal(page.data.error, "网络异常");
  page.setData({ error: "" });
  await page.toggleAuto({ detail: { value: false } });
  assert.equal(page.data.autoEnabled, true);
  assert.equal(page.data.autoSaving, false);
});

test("pending, unavailable and empty states never claim ready", async () => {
  const view = payload();
  view.types = view.types.map((item) => ({ ...item, status: "pending" }));
  const { page } = screen({ view });
  await page.load();
  assert.equal(page.data.heroTitle, "提醒次数待确认");
  assert.equal(page.data.heroReady, false);
  view.settings.channel.available = false;
  await page.load();
  assert.equal(page.data.channelAvailable, false);
});

test("old WeChat client gets a manual upgrade explanation", async () => {
  const modals = [];
  const { page, calls } = screen({ wx: { showModal(options) { modals.push(options); } } });
  page.onLoad(); await page.load(); page.requestGrant();
  assert.equal(modals.length, 1);
  assert.match(modals[0].content, /更新微信/);
  assert.equal(calls.some((item) => item.url.endsWith("/result")), false);
});

test("history failure is isolated from settings", async () => {
  const { page } = screen({ history: new Error("读取失败") });
  await page.load();
  assert.equal(page.data.items.length, 2);
  assert.equal(page.data.deliveriesError, "读取失败");
  assert.equal(page.data.error, "");
});

test("delivery reasons keep real failures actionable", () => {
  const row = notifications.describeDelivery({ type: "schedule_reminder", state: "skipped",
    scheduled_at: "2026-09-06T17:00:00", result_code: "template_field_missing" });
  assert.equal(row.stateText, "未发送");
  assert.equal(row.stateTone, "neutral");
  assert.match(row.reason, /模板/);
  assert.match(row.reason, /重新排队/);
});

module.exports = { payload };
