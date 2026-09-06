/* PKDS-1.0 视图辅助：科目色、复习出现原因、置信度文案、折叠与区间偏好持久化。
   这里只做纯展示映射，不做任何业务判断。 */

const SUBJECT_CLASSES = ["s-chinese", "s-math", "s-english", "s-activity", "s-other"];
const SUBJECT_FIXED = { 语文: "s-chinese", 数学: "s-math", 英语: "s-english" };

const CONFIDENCE = {
  high: { label: "识别可靠", level: 3, tone: "high" },
  medium: { label: "请核对", level: 2, tone: "medium" },
  low: { label: "不确定", level: 1, tone: "low" }
};

const FEEDBACK_LABELS = {
  complete: "完成",
  reinforce: "需要加强",
  partial: "只做了一部分",
  defer: "今天先跳过"
};

/* 自定义科目按名称首字符取固定色，保证同一科目每次渲染颜色一致。 */
function subjectClass(name, kind) {
  if (kind === "activity") return "s-activity";
  const key = String(name || "").trim();
  if (!key) return "s-other";
  if (SUBJECT_FIXED[key]) return SUBJECT_FIXED[key];
  let hash = 0;
  for (let index = 0; index < key.length; index += 1) hash = (hash * 31 + key.charCodeAt(index)) % 997;
  return SUBJECT_CLASSES[hash % SUBJECT_CLASSES.length];
}

function subjectMark(name) {
  const key = String(name || "").trim();
  return key ? key.charAt(0) : "学";
}

function confidence(value) {
  return CONFIDENCE[value] || null;
}

function feedbackLabel(action) {
  return FEEDBACK_LABELS[action] || "";
}

function monthDay(iso) {
  const parts = String(iso || "").slice(0, 10).split("-");
  if (parts.length !== 3) return "";
  return `${Number(parts[1])} 月 ${Number(parts[2])} 日`;
}

/* 复习待办的「出现原因」。后端只给结构化字段，中文由这里拼装；
   来源缺失时返回空串，调用方不渲染该块（历史数据可能补不上来源）。 */
function reviewReason(item) {
  if (!item) return "";
  const round = Number(item.review_round) > 0 ? Number(item.review_round) : 0;
  const day = monthDay(item.source_occurred_on);
  const interval = Number(item.interval_days);
  if (!day && !round) return "";
  const pieces = [];
  if (day) pieces.push(`${day}确认的学习记录`);
  if (round) pieces.push(`今天第 ${round} 次复习`);
  if (interval > 0) pieces.push(`距上次 ${interval} 天`);
  return pieces.length ? `${pieces.join("，")}。` : "";
}

/* 折叠、区间等纯界面偏好按孩子维度记忆，读写失败一律回落到默认值。 */
function readPreference(scope, childId, fallback) {
  try {
    const all = wx.getStorageSync("uiPreferences") || {};
    const value = ((all[scope] || {})[childId || "_"]);
    return value === undefined ? fallback : value;
  } catch {
    return fallback;
  }
}

function writePreference(scope, childId, value) {
  try {
    const all = wx.getStorageSync("uiPreferences") || {};
    const bucket = all[scope] || {};
    bucket[childId || "_"] = value;
    all[scope] = bucket;
    wx.setStorageSync("uiPreferences", all);
  } catch {
    /* 偏好丢失不影响主流程 */
  }
}

module.exports = {
  subjectClass,
  subjectMark,
  confidence,
  feedbackLabel,
  monthDay,
  reviewReason,
  readPreference,
  writePreference
};
