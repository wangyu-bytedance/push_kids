const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");
const notifications = require("../../apps/miniprogram/utils/notifications");

const PREFERENCES = [
  {
    type: "member_application",
    label: "家人加入申请",
    description: "有人申请加入家庭时通知管理员",
    enabled: true,
    managers_only: true,
    template_id: "tpl-apply",
    subscription_status: "accepted",
    remaining_quota: 1
  },
  {
    type: "schedule_reminder",
    label: "课前一小时提醒",
    description: "日程开始前一小时提醒全家",
    enabled: true,
    managers_only: false,
    template_id: "tpl-schedule",
    subscription_status: "none",
    remaining_quota: 0
  },
  {
    type: "review_digest",
    label: "每天 19:00 复习提醒",
    description: "汇总当天还没复习的内容",
    enabled: false,
    managers_only: false,
    template_id: "tpl-digest",
    subscription_status: "none",
    remaining_quota: 0
  }
];

/* 页面在 VM 里运行，跨 realm 的数组/对象无法与本 realm 的字面量做引用级比较。 */
function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

function settingsPayload(overrides = {}) {
  return {
    channel: {
      available: true,
      reason: "",
      template_ids: ["tpl-apply", "tpl-schedule", "tpl-digest"],
      long_term: false
    },
    preferences: PREFERENCES.map((item) => ({ ...item })),
    last_sent_at: "2026-09-05T19:00:00",
    ...overrides
  };
}

function loadNotifications({ settings = settingsPayload(), deliveries = [], wx = {} } = {}) {
  const calls = [];
  const request = async (url, options = {}) => {
    calls.push({ url, options });
    if (url === "/notifications/deliveries") {
      if (deliveries instanceof Error) throw deliveries;
      return deliveries;
    }
    const payload = typeof settings === "function" ? settings(url, options) : settings;
    if (payload instanceof Error) throw payload;
    return payload;
  };
  const harness = loadPage("pages/notifications/index.js", request, { wx });
  return { ...harness, calls };
}

test("settings load separates the on/off switch from the WeChat grant state", async () => {
  const { page } = loadNotifications();
  page.onLoad();
  await page.load();

  assert.equal(page.data.loading, false);
  assert.equal(page.data.channelAvailable, true);
  assert.equal(page.data.items.length, 3);

  const [apply, schedule, digest] = page.data.items;
  // 有额度的一次性授权：已开启，但如实说明只够一条
  assert.equal(apply.statusText, "已开启 · 仅剩 1 条");
  assert.equal(apply.needsGrant, false);
  // 一次性模板可以重复授权攒额度，所以已开启的类别也要有"再存"入口
  assert.equal(apply.canTopUp, true);
  // 开着但没授权：必须提示需要授权，不能显示成已开启
  assert.equal(schedule.statusText, "待微信授权");
  assert.equal(schedule.needsGrant, true);
  // 关着的类别不催授权，也不催攒额度
  assert.equal(digest.statusText, "已关闭");
  assert.equal(digest.needsGrant, false);
  assert.equal(digest.canTopUp, false);
  assert.equal(page.data.grantCount, 1);
  // 余额只统计真正能发出去的条数：申请提醒 1 条
  assert.equal(page.data.reserveTotal, 1);
  assert.equal(page.data.reserveLow, true);
  assert.equal(page.data.canTopUp, true);
  assert.equal(page.data.lastSentLabel, "09-05 19:00");
});

test("a failed preference write rolls the switch back instead of faking success", async () => {
  const { page } = loadNotifications({
    settings: (url) => {
      if (url === "/notifications/preferences") return new Error("网络异常");
      return settingsPayload();
    }
  });
  await page.load();
  assert.equal(page.data.items[2].enabled, false);

  await page.toggle({ currentTarget: { dataset: { type: "review_digest" } }, detail: { value: true } });

  assert.equal(page.data.items[2].enabled, false);
  assert.equal(page.data.error, "网络异常");
  assert.equal(page.data.togglingType, "");
});

test("granting posts only WeChat's own decisions and refuses to invent an accept", async () => {
  let subscribeArgs = null;
  const { page, calls } = loadNotifications({
    wx: {
      requestSubscribeMessage(options) {
        subscribeArgs = options;
        options.success({ errMsg: "ok", "tpl-schedule": "reject" });
      }
    }
  });
  page.onLoad();
  await page.load();

  page.requestGrant();
  await new Promise((resolve) => setImmediate(resolve));

  assert.deepEqual(plain(subscribeArgs.tmplIds), ["tpl-schedule"]);
  const post = calls.find((call) => call.url === "/notifications/subscriptions");
  assert.deepEqual(plain(post.options.data), {
    results: [{ type: "schedule_reminder", accepted: false, decision: "reject" }]
  });
  assert.equal(page.data.granting, false);
});

test("topping up asks again for the types with the least remaining quota", async () => {
  let subscribeArgs = null;
  const toasts = [];
  const { page, calls } = loadNotifications({
    settings: settingsPayload({
      preferences: [
        { ...PREFERENCES[0], remaining_quota: 4 },
        { ...PREFERENCES[1], subscription_status: "accepted", remaining_quota: 1 },
        { ...PREFERENCES[2], enabled: true, subscription_status: "accepted", remaining_quota: 2 }
      ]
    }),
    wx: {
      showToast(options) { toasts.push(options); },
      requestSubscribeMessage(options) {
        subscribeArgs = options;
        options.success({
          errMsg: "ok",
          "tpl-schedule": "accept",
          "tpl-digest": "accept",
          "tpl-apply": "reject"
        });
      }
    }
  });
  page.onLoad();
  await page.load();

  // 全部已授权时不再显示"去授权"，但仍要能补额度
  assert.equal(page.data.grantCount, 0);
  assert.equal(page.data.canTopUp, true);
  assert.equal(page.data.reserveTotal, 7);
  assert.equal(page.data.reserveLow, false);

  page.requestGrant({ currentTarget: { dataset: { mode: "topup" } } });
  await new Promise((resolve) => setImmediate(resolve));

  // 少的排前面：1 条 → 2 条 → 4 条，一次最多 3 个模板
  assert.deepEqual(plain(subscribeArgs.tmplIds), ["tpl-schedule", "tpl-digest", "tpl-apply"]);
  const post = calls.find((call) => call.url === "/notifications/subscriptions");
  assert.deepEqual(plain(post.options.data.results), [
    { type: "schedule_reminder", accepted: true, decision: "accept" },
    { type: "review_digest", accepted: true, decision: "accept" },
    { type: "member_application", accepted: false, decision: "reject" }
  ]);
  // 报的是"又攒了几条"，不是含糊的"已开启"
  assert.match(toasts[toasts.length - 1].title, /已存入 2 条/);
});

test("a WeChat failure surfaces an actionable message and clears the pending flag", async () => {
  const { page, calls } = loadNotifications({
    wx: { requestSubscribeMessage(options) { options.fail({ errMsg: "fail" }); } }
  });
  page.onLoad();
  await page.load();

  page.requestGrant();

  assert.equal(page.data.granting, false);
  assert.match(page.data.error, /再试一次/);
  assert.equal(calls.some((call) => call.url === "/notifications/subscriptions"), false);
});

test("an unavailable channel asks for nothing and explains itself", async () => {
  const { page } = loadNotifications({
    settings: settingsPayload({
      channel: { available: false, reason: "当前部署未配置模板", template_ids: [], long_term: false }
    })
  });
  page.onLoad();
  await page.load();

  assert.equal(page.data.channelAvailable, false);
  assert.equal(page.data.channelReason, "当前部署未配置模板");
  assert.equal(page.data.grantCount, 0);
  assert.deepEqual(page.data.items.map((item) => item.statusText), ["暂不可用", "暂不可用", "暂不可用"]);
});

test("an old WeChat client is told to upgrade instead of hitting a missing API", async () => {
  const modals = [];
  const { page, calls } = loadNotifications({
    wx: { showModal(options) { modals.push(options); } }
  });
  page.onLoad();
  await page.load();

  assert.equal(page.data.supported, false);
  page.requestGrant();

  assert.equal(modals.length, 1);
  assert.match(modals[0].content, /更新微信/);
  assert.equal(calls.some((call) => call.url === "/notifications/subscriptions"), false);
});

test("delivery history keeps failures visible with a reason", async () => {
  const { page } = loadNotifications({
    deliveries: [
      {
        type: "schedule_reminder",
        state: "failed",
        headline: "小雨 18:00 游泳课",
        detail: "出发前记得带泳镜",
        scheduled_at: "2026-09-06T17:00:00",
        sent_at: null,
        result_code: "not_authorized"
      }
    ]
  });
  await page.load();

  assert.equal(page.data.deliveries.length, 1);
  const [row] = page.data.deliveries;
  assert.equal(row.stateText, "发送失败");
  assert.equal(row.stateTone, "dan");
  assert.equal(row.timeLabel, "09-06 17:00");
  assert.match(row.reason, /微信授权/);
});

test("a broken template mapping is explained instead of shown as a bare skip", () => {
  const row = notifications.describeDelivery({
    type: "schedule_reminder",
    state: "skipped",
    headline: "小雨 18:00 游泳课",
    detail: "1 小时后开始",
    scheduled_at: "2026-09-06T17:00:00",
    sent_at: null,
    result_code: "template_field_missing"
  });

  assert.equal(row.stateText, "未发送");
  assert.equal(row.stateTone, "neutral");
  /* 家长这边没有可操作项，所以只说清"不是你的问题、修好会重排"。 */
  assert.match(row.reason, /模板/);
  assert.match(row.reason, /重新排队/);
});

test("unreadable delivery history never blocks the switches", async () => {
  const { page } = loadNotifications({ deliveries: new Error("读取失败") });
  await page.load();

  assert.equal(page.data.items.length, 3);
  assert.deepEqual(plain(page.data.deliveries), []);
  assert.equal(page.data.deliveriesError, "读取失败");
  assert.equal(page.data.error, "");
});

test("only an explicit accept counts as authorized", () => {
  const requested = [
    { type: "schedule_reminder", template_id: "a" },
    { type: "review_digest", template_id: "b" },
    { type: "member_application", template_id: "c" }
  ];
  const results = notifications.resultsFromWx({ a: "accept", b: "ban", c: "filter" }, requested);
  assert.deepEqual(results, [
    { type: "schedule_reminder", accepted: true, decision: "accept" },
    { type: "review_digest", accepted: false, decision: "ban" },
    { type: "member_application", accepted: false, decision: "filter" }
  ]);
  assert.equal(notifications.acceptedCount(results), 1);
  // 微信没给结论时不编一个：decision 留空，服务端按最保守的方式处理
  assert.deepEqual(notifications.resultsFromWx({}, [requested[0]]), [
    { type: "schedule_reminder", accepted: false, decision: "" }
  ]);
});

test("revoked and refused states each get their own recovery wording", () => {
  const revoked = notifications.statusOf(
    { enabled: true, template_id: "t", subscription_status: "revoked", remaining_quota: 0 }, true
  );
  assert.equal(revoked.needsGrant, true);
  assert.equal(revoked.text, "需要重新开启");

  const rejected = notifications.statusOf(
    { enabled: true, template_id: "t", subscription_status: "rejected", remaining_quota: 0 }, true
  );
  assert.equal(rejected.tone, "dan");
  assert.equal(rejected.needsGrant, true);

  const longTerm = notifications.statusOf(
    { enabled: true, template_id: "t", subscription_status: "accepted", remaining_quota: -1 }, true
  );
  assert.equal(longTerm.text, "已开启");
  assert.equal(longTerm.needsGrant, false);
});

test("grant batches stay within WeChat's three-template limit", () => {
  const many = ["a", "b", "c", "d"].map((id) => ({
    type: `type-${id}`, enabled: true, template_id: id, subscription_status: "none", remaining_quota: 0
  }));
  assert.equal(notifications.grantTargets(many, true).length, 3);
  assert.equal(notifications.grantTargets(many, false).length, 0);
  assert.equal(notifications.topUpTargets(many, true).length, 3);
  assert.equal(notifications.topUpTargets(many, false).length, 0);
});

test("a long-term template never asks the parent to stockpile messages", () => {
  const longTerm = [{
    type: "review_digest",
    enabled: true,
    template_id: "t",
    subscription_status: "accepted",
    remaining_quota: -1
  }];
  assert.equal(notifications.quotaLabel(longTerm[0]), "长期有效");
  assert.deepEqual(notifications.topUpTargets(longTerm, true), []);
  const reserve = notifications.reserveOf(longTerm, true);
  assert.equal(reserve.unlimited, true);
  assert.equal(reserve.low, false);
  assert.equal(reserve.canTopUp, false);
});
