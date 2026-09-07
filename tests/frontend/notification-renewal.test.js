const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const notifications = require("../../apps/miniprogram/utils/notifications");

/* 静默续订：家长在自然动作里顺手补一次一次性授权额度。
   这里守住三件事——够用就别打扰、没授权过就别突然弹、业务动作绝不能被它拖住。 */

const HOUR = 60 * 60 * 1000;
const NOW = 1_760_000_000_000;

function preference(overrides = {}) {
  return {
    type: "schedule_reminder",
    template_id: "tpl-schedule",
    enabled: true,
    subscription_status: "accepted",
    remaining_quota: 1,
    ...overrides
  };
}

function snapshot(overrides = {}) {
  return {
    channelAvailable: true,
    checkedAt: NOW - HOUR,
    preferences: [preference()],
    ...overrides
  };
}

/* 走真实 wx 存储路径的用例用真实时钟，否则固定时间戳一律会被判成过期快照。 */
function freshSnapshot(overrides = {}) {
  return snapshot({ checkedAt: Date.now(), ...overrides });
}

test("silent top-up only fires when a stored grant is running out", () => {
  assert.equal(notifications.silentTopUpPlan(snapshot(), NOW).reason, "ok");
  // 额度够用：绝不打扰
  assert.equal(
    notifications.silentTopUpPlan(
      snapshot({ preferences: [preference({ remaining_quota: 5 })] }),
      NOW
    ).reason,
    "enough"
  );
  // 长期模板不需要补
  assert.equal(
    notifications.silentTopUpPlan(
      snapshot({ preferences: [preference({ remaining_quota: -1 })] }),
      NOW
    ).reason,
    "long_term"
  );
  // 通道不可用 / 家长在微信里关掉了订阅总开关
  assert.equal(notifications.silentTopUpPlan(snapshot({ channelAvailable: false }), NOW).reason, "unavailable");
  assert.equal(notifications.silentTopUpPlan(snapshot({ blocked: true }), NOW).reason, "blocked");
  // 快照过旧时按未知处理，不拿旧额度去弹窗
  assert.equal(notifications.silentTopUpPlan(snapshot({ checkedAt: NOW - 12 * HOUR }), NOW).reason, "stale");
});

test("a parent who never granted anything is not ambushed by the dialog", () => {
  const never = snapshot({
    preferences: [preference({ subscription_status: "none", remaining_quota: 0 })]
  });
  assert.equal(notifications.silentTopUpPlan(never, NOW).reason, "never_granted");
  // 勾过"总是保持以上选择"后不会再弹窗，这时可以静默续
  assert.equal(notifications.silentTopUpPlan({ ...never, alwaysKeep: true }, NOW).reason, "ok");
});

test("cooldown is longer when the dialog is still visible to the parent", () => {
  const asked = snapshot({ lastAttemptAt: NOW - HOUR });
  assert.equal(notifications.silentTopUpPlan(asked, NOW).reason, "cooldown");
  // 无弹窗的静默续订冷却更短
  assert.equal(notifications.silentTopUpPlan({ ...asked, alwaysKeep: true }, NOW).reason, "ok");
  assert.equal(notifications.silentTopUpPlan({ ...asked, lastAttemptAt: NOW - 24 * HOUR }, NOW).reason, "ok");
});

test("top-up asks for the emptiest reminders first and never more than three", () => {
  const plan = notifications.silentTopUpPlan(
    snapshot({
      preferences: [
        preference({ type: "member_application", template_id: "tpl-apply", remaining_quota: 1 }),
        preference({ type: "schedule_reminder", template_id: "tpl-schedule", remaining_quota: 0 }),
        preference({ type: "review_digest", template_id: "tpl-digest", remaining_quota: 0 }),
        preference({ type: "extra_one", template_id: "tpl-extra", remaining_quota: 1 })
      ]
    }),
    NOW
  );
  assert.deepEqual(
    plan.targets.map((item) => item.type),
    ["schedule_reminder", "review_digest", "member_application"]
  );
});

test("WeChat's own subscription setting decides how aggressive we may be", () => {
  assert.deepEqual(
    notifications.readSubscriptionSetting(
      { subscriptionsSetting: { mainSwitch: true, itemSettings: { a: "accept", b: "accept" } } },
      ["a", "b"]
    ),
    { blocked: false, alwaysKeep: true }
  );
  // 只有部分模板勾了"总是保持"，仍会弹窗
  assert.deepEqual(
    notifications.readSubscriptionSetting(
      { subscriptionsSetting: { mainSwitch: true, itemSettings: { a: "accept" } } },
      ["a", "b"]
    ),
    { blocked: false, alwaysKeep: false }
  );
  // 主开关关掉：一次都不该试
  assert.deepEqual(
    notifications.readSubscriptionSetting({ subscriptionsSetting: { mainSwitch: false } }, ["a"]),
    { blocked: true, alwaysKeep: false }
  );
});

function loadRenew({ stored = freshSnapshot(), wx = {}, request } = {}) {
  const calls = [];
  const store = { "notification-renew-v1": stored };
  const asked = [];
  const stub =
    request ||
    (async (url, options = {}) => {
      calls.push({ url, options });
      return {
        channel: { available: true, reason: "", template_ids: ["tpl-schedule"], long_term: false },
        preferences: [
          {
            type: "schedule_reminder",
            template_id: "tpl-schedule",
            enabled: true,
            subscription_status: "accepted",
            remaining_quota: 4
          }
        ],
        last_sent_at: null
      };
    });
  const harness = loadPage("utils/renew.js", stub, {
    wx: {
      getStorageSync(key) { return store[key]; },
      setStorageSync(key, value) { store[key] = value; },
      requestSubscribeMessage(options) {
        asked.push(options.tmplIds);
        options.success({ "tpl-schedule": "accept" });
      },
      getSetting() {},
      ...wx
    }
  });
  return { renew: harness.exports, calls, asked, store };
}

test("a natural tap tops up the reminder balance and records the grant", async () => {
  const { renew, calls, asked, store } = loadRenew();

  assert.equal(renew.maybeTopUp(), true);
  assert.deepEqual(asked, [["tpl-schedule"]]);
  await new Promise((resolve) => setImmediate(resolve));

  const post = calls.find((call) => call.url === "/notifications/subscriptions");
  assert.ok(post, "授权结果必须回传服务端，否则额度只存在于微信侧");
  assert.deepEqual(JSON.parse(JSON.stringify(post.options.data)), {
    results: [{ type: "schedule_reminder", accepted: true, decision: "accept" }]
  });
  // 服务端返回的新额度立刻回写快照，下一次点击就不会再问
  assert.equal(store["notification-renew-v1"].preferences[0].remaining_quota, 4);
});

test("a declined dialog still starts the cooldown so the next tap stays quiet", () => {
  const { renew, asked, store } = loadRenew({
    wx: {
      requestSubscribeMessage(options) {
        asked.push(options.tmplIds);
        options.success({ "tpl-schedule": "reject" });
      }
    }
  });

  assert.equal(renew.maybeTopUp(), true);
  assert.ok(store["notification-renew-v1"].lastAttemptAt > 0);
  assert.equal(renew.maybeTopUp(), false);
});

test("an old WeChat build degrades to doing nothing", () => {
  const { renew, calls } = loadRenew({ wx: { requestSubscribeMessage: undefined } });
  assert.equal(renew.supported(), false);
  assert.equal(renew.maybeTopUp(), false);
  assert.deepEqual(calls, []);
});

test("hydrate refreshes a stale snapshot and skips a fresh one", async () => {
  const stale = loadRenew({ stored: snapshot({ checkedAt: NOW - 40 * HOUR }) });
  assert.equal(await stale.renew.hydrate(), true);
  assert.deepEqual(stale.calls.map((call) => call.url), ["/notifications/settings"]);

  const fresh = loadRenew({ stored: snapshot({ checkedAt: Date.now() }) });
  assert.equal(await fresh.renew.hydrate(), false);
  assert.deepEqual(fresh.calls, []);
});

test("a failed settings refresh never breaks the page that asked for it", async () => {
  const { renew } = loadRenew({
    stored: snapshot({ checkedAt: NOW - 40 * HOUR }),
    request: async () => { throw new Error("网络异常"); }
  });
  assert.equal(await renew.hydrate(), false);
});

test("finishing a review still completes even while the top-up dialog is open", async () => {
  const store = { "notification-renew-v1": freshSnapshot() };
  const asked = [];
  const calls = [];
  const dashboard = {
    child: { id: "child", name: "小雨" },
    todo_groups: [{ group_id: "g1", optional: false, items: [{ review_id: "r1", title: "分数" }] }],
    must_todo_groups: [],
    optional_todo_groups: [],
    learning_records: [],
    activities: [],
    minutes_planned: 0
  };
  const request = async (url) => {
    calls.push(url);
    if (url === "/children") return [{ id: "child", name: "小雨" }];
    if (url === "/reviews/r1/feedback") return { ok: true };
    if (url.startsWith("/children/child/dashboard")) return dashboard;
    return {};
  };
  const { page } = loadPage("pages/today/index.js", request, {
    wx: {
      getStorageSync(key) { return store[key]; },
      setStorageSync(key, value) { store[key] = value; },
      requestSubscribeMessage(options) {
        asked.push(options.tmplIds);
        /* 家长还停在弹窗上时，业务请求就应该已经发出去了。 */
      }
    }
  });
  page.data.childId = "child";
  page.data.dashboard = dashboard;

  await page.feedback({ detail: { reviewId: "r1", action: "complete" } });

  assert.deepEqual(asked, [["tpl-schedule"]]);
  assert.ok(calls.includes("/reviews/r1/feedback"), "续订不能吞掉家长真正点的那个动作");
});
