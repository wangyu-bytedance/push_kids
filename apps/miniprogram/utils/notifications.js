/* 提醒设置的纯展示策略：把服务端的通道/授权/投递状态翻译成家长看得懂的一句话。
   这里不做任何判断性业务逻辑，也不决定能不能发——那是服务端的事。 */

const TYPE_LABELS = {
  member_application: "家人加入申请",
  schedule_reminder: "课前一小时提醒",
  review_digest: "每天 19:00 复习提醒"
};

const STATE_TEXT = {
  pending: "排队中",
  sending: "正在发送",
  sent: "已发送",
  skipped: "未发送",
  failed: "发送失败",
  cancelled: "已取消"
};

const STATE_TONE = { sent: "suc", failed: "dan", skipped: "neutral", cancelled: "neutral" };

/* 服务端结果码 → 家长能据此行动的解释。缺失的码不编故事，只显示状态本身。 */
const RESULT_TEXT = {
  ok: "微信已收到这条提醒",
  not_authorized: "微信授权额度已用完，需要再存一次提醒",
  member_disabled: "这类提醒当时是关闭的",
  channel_unavailable: "当时提醒服务不可用，恢复后会重新排队",
  template_field_missing: "提醒模板缺少内容，已跳过；修好配置后会重新排队",
  no_destination: "还没记录到你的微信接收信息",
  user_refused: "你在微信里选择了不再接收，需要重新开启",
  destination_unreadable: "接收信息失效，请重新开启一次提醒",
  transport_error: "网络不稳定，稍后会自动重试",
  rate_limited: "微信限流，稍后会自动重试",
  lease_expired: "多次重试后仍未成功",
  source_changed: "对应的日程或申请已经变化",
  member_departed: "你已不在这个家庭"
};

/* 图标只取自已有图标集，不为通知新增视觉资产。 */
const TYPE_ICONS = {
  member_application: "ico-family-pri",
  schedule_reminder: "ico-clock-pri",
  review_digest: "ico-book-pri"
};

function typeLabel(type) {
  return TYPE_LABELS[type] || "提醒";
}

function typeIcon(type) {
  return TYPE_ICONS[type] || "ico-info-pri";
}

/* 一条偏好是否还能真的送到：开着、有模板、微信授权还有额度。 */
function isAuthorized(preference) {
  if (!preference) return false;
  if (preference.subscription_status !== "accepted") return false;
  const quota = Number(preference.remaining_quota);
  return quota === -1 || quota > 0;
}

/* 微信当前只给到一次性模板：一次授权买一条，多次授权可以攒。
   这里把"还能发几条"说成家长能算的数，而不是抽象的"已开启"。 */
function quotaLabel(preference) {
  const quota = Number((preference || {}).remaining_quota);
  if (quota === -1) return "长期有效";
  if (quota <= 0) return "已用完";
  return `还能发 ${quota} 条`;
}

/* 状态胶囊：先说最需要家长处理的事，其次才是"已开启"。 */
function statusOf(preference, channelAvailable) {
  if (!channelAvailable) return { text: "暂不可用", tone: "neutral", needsGrant: false };
  if (!preference.enabled) return { text: "已关闭", tone: "neutral", needsGrant: false };
  if (!preference.template_id) return { text: "暂不可用", tone: "neutral", needsGrant: false };
  if (preference.subscription_status === "rejected") {
    return { text: "微信里已拒收", tone: "dan", needsGrant: true };
  }
  if (preference.subscription_status === "revoked") {
    return { text: "需要重新开启", tone: "att", needsGrant: true };
  }
  if (isAuthorized(preference)) {
    const quota = Number(preference.remaining_quota);
    if (quota === -1) return { text: "已开启", tone: "suc", needsGrant: false };
    /* 只剩一条时说明"发完就要再授权"，避免家长以为一直会有。 */
    return {
      text: quota > 1 ? `已开启 · ${quotaLabel(preference)}` : "已开启 · 仅剩 1 条",
      tone: quota > 1 ? "suc" : "att",
      needsGrant: false
    };
  }
  if (preference.subscription_status === "expired") {
    return { text: "额度已用完", tone: "att", needsGrant: true };
  }
  return { text: "待微信授权", tone: "att", needsGrant: true };
}

/* 微信一次最多带 3 个模板；这里按界面顺序取还需要授权的那几个。 */
function grantTargets(preferences, channelAvailable) {
  if (!channelAvailable) return [];
  const targets = [];
  (preferences || []).forEach((item) => {
    const status = statusOf(item, true);
    if (status.needsGrant && item.template_id) targets.push(item);
  });
  return targets.slice(0, 3);
}

/* 攒额度：一次性模板可以重复授权累积，所以已开启的类别也允许再存。
   缺额度最多的排前面，一次最多带 3 个模板。 */
function topUpTargets(preferences, channelAvailable) {
  if (!channelAvailable) return [];
  const candidates = (preferences || []).filter(
    (item) => item.enabled && item.template_id && Number(item.remaining_quota) !== -1
  );
  const ordered = candidates
    .map((item, index) => ({ item, index, quota: Math.max(0, Number(item.remaining_quota) || 0) }))
    .sort((a, b) => (a.quota === b.quota ? a.index - b.index : a.quota - b.quota));
  return ordered.slice(0, 3).map((entry) => entry.item);
}

/* 提醒余额概览：总条数 + 是否已经少到需要提醒家长补一次。 */
function reserveOf(preferences, channelAvailable) {
  const items = (preferences || []).filter((item) => item.enabled && item.template_id);
  let total = 0;
  let unlimited = false;
  items.forEach((item) => {
    const quota = Number(item.remaining_quota);
    if (quota === -1) unlimited = true;
    else if (isAuthorized(item)) total += quota;
  });
  const canTopUp = channelAvailable && topUpTargets(items, channelAvailable).length > 0;
  /* 每天最多一条复习提醒，所以 3 条大约够撑两三天，低于这个数就该提示补一次。 */
  return { total, unlimited, canTopUp, low: !unlimited && total < 3 };
}

/* 静默续订的判断规则。微信要求订阅弹窗必须在点击手势里发起，所以这里只做"能不能续、续哪几个"
   的纯计算：输入是本地缓存的快照，输出是可以立刻带进 wx.requestSubscribeMessage 的目标。
   门槛写得保守：家长没有在设置页授权过就不打扰；勾过"总是保持"时不会弹窗，才允许更勤快一点。 */
const SNAPSHOT_MAX_AGE_MS = 6 * 60 * 60 * 1000;
const COOLDOWN_MS = 12 * 60 * 60 * 1000;
const SILENT_COOLDOWN_MS = 30 * 60 * 1000;

function hasGrantedBefore(preferences) {
  return (preferences || []).some(
    (item) =>
      item.subscription_status === "accepted" ||
      item.subscription_status === "expired" ||
      Number(item.remaining_quota) > 0
  );
}

function silentTopUpPlan(snapshot, now) {
  const state = snapshot || {};
  const preferences = state.preferences || [];
  const at = Number(now) || 0;
  if (state.blocked === true) return { targets: [], reason: "blocked" };
  if (state.channelAvailable !== true) return { targets: [], reason: "unavailable" };
  /* 快照太旧就先不打扰：宁可少续一次，也不要按过期的额度去弹窗。 */
  if (!state.checkedAt || at - Number(state.checkedAt) > SNAPSHOT_MAX_AGE_MS) {
    return { targets: [], reason: "stale" };
  }
  const reserve = reserveOf(preferences, true);
  if (reserve.unlimited) return { targets: [], reason: "long_term" };
  if (!reserve.low) return { targets: [], reason: "enough" };
  /* 第一次授权属于设置页的知情选择，不在日常点击里突然弹出来。 */
  if (!hasGrantedBefore(preferences) && state.alwaysKeep !== true) {
    return { targets: [], reason: "never_granted" };
  }
  const cooldown = state.alwaysKeep === true ? SILENT_COOLDOWN_MS : COOLDOWN_MS;
  if (state.lastAttemptAt && at - Number(state.lastAttemptAt) < cooldown) {
    return { targets: [], reason: "cooldown" };
  }
  const targets = topUpTargets(preferences, true);
  if (!targets.length) return { targets: [], reason: "no_target" };
  return { targets, reason: "ok" };
}

/* wx.getSetting({ withSubscriptions: true }) 只回传家长勾过"总是保持以上选择"的模板。
   勾过就意味着后续调用不再弹窗，可以更频繁地续；主开关关掉则一次都不该试。 */
function readSubscriptionSetting(setting, templateIds) {
  const box = (setting || {}).subscriptionsSetting || {};
  if (box.mainSwitch === false) return { blocked: true, alwaysKeep: false };
  const items = box.itemSettings || {};
  const ids = (templateIds || []).filter((id) => !!id);
  const alwaysKeep = ids.length > 0 && ids.every((id) => items[id] === "accept");
  return { blocked: false, alwaysKeep };
}

/* wx.requestSubscribeMessage 的返回是「模板 ID → accept/reject/ban/filter」，
   只有 accept 算授权；其余一律按未授权回传，绝不替用户乐观解释。
   原始结论一起回传：reject 只是这次不同意，ban/filter 才是真的收不到。 */
function resultsFromWx(response, requested) {
  const results = [];
  (requested || []).forEach((item) => {
    const decision = String((response || {})[item.template_id] || "");
    const known = ["accept", "reject", "ban", "filter"].indexOf(decision) >= 0;
    results.push({
      type: item.type,
      accepted: decision === "accept",
      decision: known ? decision : ""
    });
  });
  return results;
}

function acceptedCount(results) {
  return (results || []).filter((item) => item.accepted).length;
}

/* 投递记录的一行文案。时间只做展示截断，不参与任何判断。 */
function describeDelivery(item) {
  const stamp = String(item.sent_at || item.scheduled_at || "").replace("T", " ");
  /* 成功且无异常时不再重复解释一遍，只有需要家长知道原因的结果才展开。 */
  const explained = item.state === "sent" && (!item.result_code || item.result_code === "ok");
  return {
    typeLabel: typeLabel(item.type),
    headline: item.headline || typeLabel(item.type),
    detail: item.detail || "",
    stateText: STATE_TEXT[item.state] || item.state,
    stateTone: STATE_TONE[item.state] || "att",
    timeLabel: stamp.length >= 16 ? stamp.slice(5, 16) : stamp,
    reason: explained ? "" : RESULT_TEXT[item.result_code] || ""
  };
}

function lastSentLabel(value) {
  const stamp = String(value || "").replace("T", " ");
  if (!stamp) return "";
  return stamp.length >= 16 ? stamp.slice(5, 16) : stamp;
}

module.exports = {
  typeLabel,
  typeIcon,
  isAuthorized,
  quotaLabel,
  statusOf,
  grantTargets,
  topUpTargets,
  reserveOf,
  silentTopUpPlan,
  readSubscriptionSetting,
  resultsFromWx,
  acceptedCount,
  describeDelivery,
  lastSentLabel
};
