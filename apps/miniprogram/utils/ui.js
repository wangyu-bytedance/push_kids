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

/* 课外活动图标：关键字包含匹配，家长自己写的「少儿篮球班」也能命中；
   越具体的关键字排在前面，命中不了用默认星形图标。 */
const ACTIVITY_ICONS = [
  ["swim", ["游泳", "泳", "swim"]],
  ["pingpong", ["乒乓", "pingpong", "ping pong", "table tennis"]],
  ["basketball", ["篮球", "篮", "basketball"]],
  ["badminton", ["羽毛球", "羽球", "羽毛", "badminton"]],
  ["soccer", ["足球", "soccer", "football"]],
  ["tennis", ["网球", "tennis"]],
  ["chess", ["围棋", "象棋", "五子棋", "棋", "chess"]],
  ["piano", ["钢琴", "电子琴", "piano"]],
  ["music", ["提琴", "音乐", "声乐", "唱歌", "合唱", "吉他", "琴", "music", "violin"]],
  ["dance", ["舞蹈", "芭蕾", "舞", "dance", "ballet"]],
  ["martial", ["武术", "跆拳道", "空手道", "散打", "柔道", "拳", "击剑", "剑道"]],
  ["brush", ["书法", "毛笔", "硬笔", "练字", "写字"]],
  ["palette", ["绘画", "美术", "素描", "水彩", "国画", "画", "手工", "陶艺"]],
  ["robot", ["机器人", "乐高", "lego", "robot"]],
  ["code", ["编程", "代码", "scratch", "python", "code"]]
];
const ACTIVITY_ICON_FALLBACK = "star";

/* 返回图标基类名；tone 是 PKDS 色后缀（如 "pri"），留空取默认墨色。 */
function activityIcon(name, tone) {
  const key = String(name || "").trim().toLowerCase();
  let icon = ACTIVITY_ICON_FALLBACK;
  if (key) {
    const hit = ACTIVITY_ICONS.find((entry) => entry[1].some((word) => key.includes(word)));
    if (hit) icon = hit[0];
  }
  return tone ? `ico-${icon}-${tone}` : `ico-${icon}`;
}

module.exports = {
  subjectClass,
  subjectMark,
  activityIcon,
  confidence,
  feedbackLabel,
  monthDay,
  reviewReason,
  readPreference,
  writePreference
};
