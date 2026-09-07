/* 静默续订：把"再存几条提醒"挂到家长本来就会点的动作上。

   微信只给一次性订阅模板，一次同意买一条提醒，而弹窗必须在用户点击的同一次手势里发起。
   如果只靠设置页手动补，额度总会在家长不知情时用完。这里的做法是：
   页面进来时先把服务端的额度快照缓存到本地，家长点确认/反馈/保存日程时，第一行同步做决策，
   够用就什么都不做，不够才顺手弹一次微信授权，业务动作照常继续执行。

   它只补额度，不决定能不能发、也不改任何学习记录或复习计划——那些都在服务端。 */

const api = require("./api");
const notifications = require("./notifications");

const KEY = "notification-renew-v1";
/* 快照只要够新到能算出额度就行；比这更旧就重新拉一次，不拿旧数据去弹窗。 */
const REFRESH_AFTER_MS = 30 * 60 * 1000;

function supported() {
  return typeof wx.requestSubscribeMessage === "function";
}

function now() {
  return Date.now();
}

function readState() {
  try {
    return wx.getStorageSync(KEY) || {};
  } catch {
    return {};
  }
}

function writeState(next) {
  try {
    wx.setStorageSync(KEY, next);
  } catch {
    /* 存不下就退化成"这次不续"，不影响任何业务动作。 */
  }
}

function templateIdsOf(preferences) {
  return (preferences || []).map((item) => item.template_id).filter((id) => !!id);
}

/* 记录一份服务端事实的快照。额度、状态、模板都来自服务端，本地只加时间戳和冷却记录。 */
function remember(settings, extra) {
  const channel = (settings || {}).channel || {};
  const preferences = ((settings || {}).preferences || []).map((item) => ({
    type: item.type,
    template_id: item.template_id || "",
    enabled: item.enabled === true,
    subscription_status: item.subscription_status || "",
    remaining_quota: Number(item.remaining_quota) || 0
  }));
  const state = readState();
  writeState({
    ...state,
    channelAvailable: channel.available === true,
    preferences,
    checkedAt: now(),
    ...(extra || {})
  });
}

function probeSubscriptionSetting() {
  if (typeof wx.getSetting !== "function") return;
  wx.getSetting({
    withSubscriptions: true,
    success: (setting) => {
      const state = readState();
      const read = notifications.readSubscriptionSetting(setting, templateIdsOf(state.preferences));
      writeState({ ...state, blocked: read.blocked, alwaysKeep: read.alwaysKeep });
    },
    fail: () => {}
  });
}

/* 页面 onShow 调用：异步刷新快照，不阻塞渲染，也不打扰家长。 */
function hydrate(force) {
  if (!supported()) return Promise.resolve(false);
  const state = readState();
  if (!force && state.checkedAt && now() - Number(state.checkedAt) < REFRESH_AFTER_MS) {
    return Promise.resolve(false);
  }
  return api
    .request("/notifications/settings")
    .then((settings) => {
      remember(settings);
      probeSubscriptionSetting();
      return true;
    })
    .catch(() => false);
}

function report(accepted) {
  if (!accepted) return;
  /* 让位给业务动作自己的提示：稍后再说明这次续了几条。 */
  setTimeout(() => {
    wx.showToast({ title: `已续存 ${accepted} 条提醒`, icon: "none" });
  }, 1200);
}

function submit(results) {
  return api
    .request("/notifications/subscriptions", { method: "POST", data: { results } })
    .then((settings) => {
      remember(settings);
      report(notifications.acceptedCount(results));
      return true;
    })
    .catch(() => false);
}

/* 必须放在点击处理函数的第一行：一旦 await 过任何请求，微信就会拒绝这次订阅调用。
   返回是否真的发起了弹窗，仅供测试和调用方判断，业务动作不应依赖它。 */
function maybeTopUp() {
  if (!supported()) return false;
  const state = readState();
  const plan = notifications.silentTopUpPlan(state, now());
  if (!plan.targets.length) return false;
  /* 先记冷却再弹窗：家长这次没同意，也不该在下一次点击时又被问一遍。 */
  writeState({ ...state, lastAttemptAt: now() });
  wx.requestSubscribeMessage({
    tmplIds: plan.targets.map((item) => item.template_id),
    success: (response) => submit(notifications.resultsFromWx(response, plan.targets)),
    fail: () => {}
  });
  return true;
}

/* 设置页手动授权后调用：更新快照并占用一次冷却，避免紧接着又静默弹一次。 */
function noteManualGrant(settings) {
  remember(settings, { lastAttemptAt: now() });
  probeSubscriptionSetting();
}

module.exports = { hydrate, maybeTopUp, remember, noteManualGrant, supported, KEY };
