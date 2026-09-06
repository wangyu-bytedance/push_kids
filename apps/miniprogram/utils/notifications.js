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
  not_authorized: "还没拿到微信授权，需要重新点一次开启",
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
    return {
      text: Number(preference.remaining_quota) === -1 ? "已开启" : "已开启 · 本次一条",
      tone: "suc",
      needsGrant: false
    };
  }
  if (preference.subscription_status === "expired") {
    return { text: "上一条已用完", tone: "att", needsGrant: true };
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

/* wx.requestSubscribeMessage 的返回是「模板 ID → accept/reject/ban/filter」，
   只有 accept 算授权；其余一律按未授权回传，绝不替用户乐观解释。 */
function resultsFromWx(response, requested) {
  const results = [];
  (requested || []).forEach((item) => {
    const decision = String((response || {})[item.template_id] || "");
    results.push({ type: item.type, accepted: decision === "accept" });
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
  statusOf,
  grantTargets,
  resultsFromWx,
  acceptedCount,
  describeDelivery,
  lastSentLabel
};
