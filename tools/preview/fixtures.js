/* 预览用假数据：字段与后端 dashboard 契约一致，只为设计走查提供典型内容长度与边界。 */

function ringTicks(required, total, count = 12) {
  const sum = Math.max(0, total);
  const req = Math.min(Math.max(0, required), sum);
  let filled = Math.min(count, sum);
  let reqTicks = req;
  if (sum > count) {
    filled = count;
    reqTicks = req ? Math.max(1, Math.round((count * req) / sum)) : 0;
  }
  return Array.from({ length: count }, (_, index) => ({
    deg: Math.round((360 / count) * index),
    cls: index < reqTicks ? "req" : index < filled ? "opt" : "idle"
  }));
}

const children = [
  { id: "c1", name: "小满", grade: "三年级", avatar: "小", label: "小满 · 三年级" },
  { id: "c2", name: "小暑", grade: "一年级", avatar: "小", label: "小暑 · 一年级" }
];

function group(id, subject, method, minutes, optional, items) {
  return {
    id, subject_id: id, subject_name: subject, review_method: method,
    estimated_minutes: minutes, optional,
    items: items.map((entry, index) => ({
      review_id: `${id}-${index}`, knowledge_name: entry[0],
      source_occurred_on: entry[1], review_round: entry[2], interval_days: entry[3],
      done: !!entry[4]
    }))
  };
}

const todoGroups = [
  group("g1", "语文", "听写 + 讲一遍", 12, false, [
    ["《望庐山瀑布》默写", "2026-08-30", 2, 3],
    ["生字：瀑、炉、疑", "2026-08-30", 2, 3, true]
  ]),
  group("g2", "数学", "口算 10 题", 8, false, [["两位数进位加法", "2026-09-03", 1, 1]]),
  group("g3", "英语", "跟读课文", 10, true, [["Unit 2 单词表", "2026-08-25", 3, 7]])
];

const dashboard = {
  day: "2026-09-06",
  todo_count: 4, required_todo_count: 3, estimated_minutes: 26,
  pending_confirmation_count: 2, analyzing_count: 1, failed_count: 0,
  todo_groups: todoGroups,
  must_todo_groups: todoGroups.filter((item) => !item.optional),
  optional_todo_groups: todoGroups.filter((item) => item.optional),
  daily_summary: {
    record_count: 2,
    subjects: [
      { subject_id: "s1", subject_name: "语文", subject_class: "s-chinese", subject_mark: "语", summary_text: "古诗《望庐山瀑布》；生字 3 个" },
      { subject_id: "s2", subject_name: "数学", subject_class: "s-math", subject_mark: "数", summary_text: "两位数进位加法练习 12 题" }
    ]
  },
  schedule_items: [
    { id: "a1", name: "游泳课", kind: "class", kind_label: "课外活动", start_time: "17:30", end_time: "18:30", time_text: "17:30–18:30 · 每周重复", subject_id: "sub-swim", action_text: "记录这次练习", past: false },
    { id: "a2", name: "钢琴练习", kind: "activity", kind_label: "自主活动", start_time: "08:00", end_time: "08:30", time_text: "08:00–08:30", subject_id: "sub-piano", action_text: "补记这次练习", past: true }
  ],
  optional_activity_suggestions: [
    { schedule_id: "s9", subject_id: "sub-run", subject_name: "跳绳", message: "这周还没有记录，今天有 20 分钟空档" }
  ],
  activity_count: 3,
  show_guide: false, is_empty: false
};

const base = {
  loading: false, error: "", children, childIndex: 0, childId: "c1", multiChild: true,
  dayLabel: "9 月 6 日 星期日",
  sections: { review: true, learning: true, activity: true },
  sectionMeta: { review: "4 项 · 约 26 分钟", learning: "已确认 2 条", activity: "3 项" },
  reviewReturn: null, reviewGroupId: "", reviewFocusText: "", showChildSheet: false,
  todosExpanded: true, hiddenTodoCount: 0,
  todoCards: todoGroups.map((item, index) => ({
    ...item,
    first_optional: !!item.optional && (index === 0 || !todoGroups[index - 1].optional)
  })),
  hero: {
    required: 3, optional: 1, total: 4, minutes: 26,
    ticks: ringTicks(3, 4),
    note: "其中 1 项是可选的 · 都是之前确认过的学习内容"
  },
  dashboard
};

const tabBar = { selected: 0, badges: { records: 2 }, tabs: [
  { pagePath: "/pages/today/index", text: "今日", icon: "today" },
  { pagePath: "/pages/calendar/index", text: "日程", icon: "calendar" },
  { pagePath: "/pages/records/index", text: "记录", icon: "records", center: true },
  { pagePath: "/pages/reports/index", text: "报表", icon: "reports" },
  { pagePath: "/pages/settings/index", text: "设置", icon: "settings" }
] };

const guide = JSON.parse(JSON.stringify(base));
guide.dashboard.show_guide = true;
guide.dashboard.todo_count = 0;
guide.dashboard.required_todo_count = 0;
guide.dashboard.todo_groups = [];
guide.dashboard.must_todo_groups = [];
guide.dashboard.optional_todo_groups = [];
guide.dashboard.daily_summary = { record_count: 0, subjects: [] };
guide.dashboard.schedule_items = [];
guide.dashboard.optional_activity_suggestions = [];
guide.dashboard.activity_count = 0;
guide.dashboard.pending_confirmation_count = 0;
guide.dashboard.analyzing_count = 0;
guide.todoCards = [];
guide.sectionMeta = { review: "0 项", learning: "还没有记录", activity: "0 项" };
guide.hero = { required: 0, optional: 0, total: 0, minutes: 0, ticks: ringTicks(0, 0), note: "" };

const sheet = JSON.parse(JSON.stringify(base));
sheet.showChildSheet = true;

/* ---------------- 记录页（新增记录 · 拍照模式空态） ---------------- */
const records = {
  loading: false, error: "", children, childIndex: 0, childId: "c1", canWrite: true,
  recordView: "new", mode: "photo", photos: [], saving: false, uploadProgress: 0,
  text: "", date: "2026-09-06", dateLabel: "09月06日", time: "19:20", today: "2026-09-06",
  timeOpen: false, backfill: false, pendingCount: 2, submittedId: "", history: [],
  historyView: "confirmed", historyLoading: false, filterDraft: {}, filterSubjects: []
};


/* ---------------- 历史记录（D4/D5：待处理 + 已确认混排） ---------------- */
const historyItems = [
  { submission_id: "h1", showDay: true, dayText: "今天 · 9 月 6 日", isPending: true, state: "pending_confirmation",
    stateTone: "att", stateLabel: "草稿待确认", label: "语文", sourceLabel: "拍照记录",
    knowledgeLabel: "2 个知识点", learnedText: "学习时间 19:20", working: false, source: "photo" },
  { submission_id: "h2", showDay: false, dayText: "", isPending: true, state: "analyzing",
    stateTone: "neutral", stateLabel: "正在整理", label: "待识别", sourceLabel: "拍照记录",
    knowledgeLabel: "", learnedText: "提交 19:26", working: true, source: "photo" },
  { submission_id: "h3", showDay: false, dayText: "", isPending: true, state: "failed",
    stateTone: "dan", stateLabel: "没整理出来", label: "待处理", sourceLabel: "拍照记录",
    knowledgeLabel: "", learnedText: "提交 18:40", working: false, source: "photo" },
  { submission_id: "h4", showDay: true, dayText: "昨天 · 9 月 5 日", isPending: false, state: "confirmed",
    stateTone: "pri", stateLabel: "已确认", label: "数学", sourceLabel: "文字记录", knowledgeLabel: "1 个知识点",
    summaryPreview: "练了两位数进位加法 12 道，错了 2 道，重点是十位进位。", mark: "数", markClass: "s-math", source: "text" },
  { submission_id: "h5", showDay: false, dayText: "", isPending: false, state: "confirmed",
    stateTone: "pri", stateLabel: "已确认", label: "英语", sourceLabel: "拍照记录", knowledgeLabel: "1 个知识点",
    summaryPreview: "跟读 Unit 2 课文，圈出了 6 个不熟的单词。", mark: "英", markClass: "s-english", source: "photo" }
];

const recordsHistory = {
  ...records, recordView: "history", searchText: "", hasFilters: false, historyView: "confirmed",
  historyItems, historyLoading: false, historyPage: 1, historyNext: true, historyError: "",
  pendingProcessing: true, pendingCount: 2, filterOpen: false,
  historyFilters: { q: "", from: "", to: "", subject_id: "", source: "", cancelled: false },
  filterDraft: { q: "", from: "", to: "", subject_id: "", source: "", cancelled: false },
  filterSubjects: [], filterSubjectIndex: 0, filterError: "",
  sourceOptions: [{ value: "", label: "全部" }, { value: "photo", label: "照片" }, { value: "text", label: "文字" }]
};

/* ---------------- 确认页（AI 草稿待确认） ---------------- */
const confirmDraft = {
  loading: false, error: "", saveError: "", saving: false, readOnly: false, manual: false,
  id: "sub-1", conflict: false,
  submission: { id: "sub-1", child_id: "c1", state: "awaiting_confirmation", time_label: "9 月 6 日 19:20", submitted_label: "9 月 6 日 19:22", media_count: 2, input_text: "" },
  subjects: [{ id: "s1", name: "语文" }, { id: "s2", name: "数学" }],
  editing: true, consent: { 书法: true }, subjectReview: true,
  subjectPicks: ["语文", "数学", "书法（新增）"],
  /* 一次拍到多个科目：按科目分组，未在列表里的科目要家长显式同意才新增 */
  groups: [
    { key: "语文", subject_name: "语文", subject_id: "s1", listed: true, create_subject: false, count: 2,
      names_text: "《望庐山瀑布》默写、生字：瀑、炉、疑", mark: "语", mark_class: "s-chinese" },
    { key: "书法", subject_name: "书法", subject_id: null, listed: false, create_subject: true, count: 1,
      names_text: "毛笔横画", mark: "书", mark_class: "s-default" }
  ],
  proposal: {
    summary: "复习了《望庐山瀑布》，重点是「疑是银河落九天」的默写和三个生字，另外练了一页毛笔横画。",
    subject_name: "语文", source: "语文作业本 P12",
    uncertainties: ["第 2 张照片有一行字被手挡住了"],
    knowledge_points: [
      { name: "《望庐山瀑布》默写", subject_name: "语文", category: "古诗", review_method: "默写一遍", estimated_minutes: 6, confidence: "high", confidence_tone: "high", confidence_label: "识别可靠", confidence_level: 3, evidence_text: "照片第 1 张有整首诗的抄写", context_count: 2, existing_knowledge_id: "k1" },
      { name: "生字：瀑、炉、疑", subject_name: "语文", category: "生字", review_method: "听写", estimated_minutes: 4, confidence: "low", confidence_tone: "low", confidence_label: "不确定", confidence_level: 1, evidence_text: "", context_count: 0, existing_knowledge_id: "" },
      { name: "毛笔横画", subject_name: "书法", category: "笔画", review_method: "临写一行", estimated_minutes: 5, confidence: "mid", confidence_tone: "mid", confidence_label: "一般", confidence_level: 2, evidence_text: "第 3 张照片是一页横画练习", context_count: 0, existing_knowledge_id: "" }
    ],
    todo_matches: [{ review_id: "r1", knowledge_name: "两位数进位加法", evidence: "第 2 张照片右下角有 12 道口算" }]
  }
};

/* ---------------- 报表页（近 30 天） ---------------- */
function days(count, kind) {
  return Array.from({ length: count }, (_, index) => {
    const day = `2026-08-${String((index % 30) + 1).padStart(2, "0")}`;
    if (kind === "urgency") {
      const pending = (index * 7) % 9;
      return { day, dayLabel: day.slice(8), display: pending ? String(pending) : "", passed: !pending, dotClass: pending ? `l${Math.min(3, Math.ceil(pending / 3))}` : "pass", reading: "" };
    }
    const level = (index * 3) % 5;
    return { day, dayLabel: day.slice(8), boxClass: `h${level}`, reading: "" };
  });
}

/* 报表概览只用固定评审数据；几何与生产页相同，预览不会把 mock 注入运行时。 */
function reportTrend(values) {
  const width = 128;
  const top = 6;
  const bottom = 42;
  const maximum = Math.max(...values);
  const points = values.map((value, index) => ({
    x: index * width / 6,
    y: maximum ? bottom - value / maximum * (bottom - top) : bottom
  }));
  return {
    available: true,
    segments: points.slice(0, -1).map((point, index) => {
      const next = points[index + 1];
      const dx = next.x - point.x;
      const dy = next.y - point.y;
      return { id: String(index), style: `left:${point.x.toFixed(1)}rpx;top:${point.y.toFixed(1)}rpx;width:${Math.hypot(dx, dy).toFixed(1)}rpx;transform:rotate(${(Math.atan2(dy, dx) * 180 / Math.PI).toFixed(1)}deg)` };
    }),
    dots: points.map((point, index) => ({
      id: String(index), last: index === 6, tickStyle: `left:${point.x.toFixed(1)}rpx`,
      style: `left:${(point.x - 3).toFixed(1)}rpx;top:${(point.y - 3).toFixed(1)}rpx`
    }))
  };
}

const reports = {
  loading: false, error: "", children, childIndex: 0, multiChild: true, showChildSheet: false,
  days: 30, ranges: [7, 30, 100], report: { day: "2026-09-06" }, isEmpty: false,
  rangeLabel: "近 30 天", feedbackTotal: 41, activityDetailFailed: false,
  metrics: [
    { label: "学习记录", text: "24", zero: false, tight: false, trend: reportTrend([2, 5, 3, 6, 2, 1, 5]), ariaLabel: "学习记录 24，近 30 天分为 7 段" },
    { label: "新增知识", text: "62", zero: false, tight: false, trend: reportTrend([5, 12, 8, 14, 9, 6, 8]), ariaLabel: "新增知识 62，近 30 天分为 7 段" },
    { label: "复习反馈", text: "41", zero: false, tight: false, trend: reportTrend([3, 4, 9, 8, 4, 7, 6]), ariaLabel: "复习反馈 41，近 30 天分为 7 段" },
    { label: "活动练习", text: "9", zero: false, tight: false, trend: reportTrend([0, 2, 0, 1, 3, 1, 2]), ariaLabel: "活动练习 9，近 30 天分为 7 段" }
  ],
  urgencyPage: 0, urgencyPageLabel: "08-01 至 08-30",
  urgencyPages: [{ id: "0", pageNumber: 1, items: days(30, "urgency"), label: "08-01 至 08-30" }],
  activityPage: 0, activityPageLabel: "08-01 至 08-30",
  activityPages: [{ id: "0", pageNumber: 1, items: days(30, "activity"), label: "08-01 至 08-30" }],
  subjects: [
    { id: "s1", name: "语文", width: 100, countText: "12 条" },
    { id: "s2", name: "数学", width: 66, countText: "8 条" },
    { id: "s3", name: "英语", width: 33, countText: "4 条" }
  ],
  activityRows: [
    { id: "a1", name: "游泳", meta: "5 次 · 上次 09-03" },
    { id: "a2", name: "钢琴", meta: "4 次 · 上次 09-05" }
  ]
};


/* ---------------- 日程（Tab 2） ---------------- */
const weekDays = ["一", "二", "三", "四", "五", "六", "日"].map((weekday, index) => ({
  key: `2026-08-3${index}`, weekday, day: 31 + index - 3, today: index === 6, dim: index > 6,
  marked: [0, 2, 3, 6].includes(index)
}));
weekDays[3].key = "2026-09-06";

const calendar = {
  loading: false, error: "", children, childIndex: 0, childId: "c1", multiChild: true,
  selectedDay: "2026-09-06", monthLabel: "2026 年 9 月", weekKicker: "这一周 3 项固定安排",
  dayTitle: "今天 · 9 月 6 日", itemCount: 3, weekEmpty: false,
  week: weekDays.slice(0, 7).map((item, index) => ({ ...item, key: index === 3 ? "2026-09-06" : item.key })),
  items: [
    { id: "e1", start_time: "17:30", end_time: "18:30", name: "游泳课", kind: "class", kind_label: "课外活动",
      time_text: "17:30–18:30 · 每周重复", past: false, subject_id: "s4", action_text: "记录这次练习" },
    { id: "e2", start_time: "08:00", end_time: "08:30", name: "钢琴练习", kind: "activity", kind_label: "自主活动",
      time_text: "08:00–08:30 · 不重复", past: true, subject_id: "s5", action_text: "补记这次练习" },
    { id: "e3", start_time: "20:00", end_time: "20:20", name: "亲子共读", kind: "other", kind_label: "其他安排",
      time_text: "20:00–20:20 · 每周重复", past: false, subject_id: "", action_text: "" }
  ],
  showChildSheet: false, showEditor: false, editingId: "", eventName: "", eventKind: "class",
  eventDate: "2026-09-06", startTime: "18:00", endTime: "19:00", repeatWeekly: true, saving: false, endError: ""
};

const calendarEditor = { ...calendar, showEditor: true, editingId: "", eventName: "乒乓球", eventKind: "class" };

/* ---------------- 学习设置（Tab 5） ---------------- */
const settings = {
  loading: false, error: "", children, childIndex: 0, childId: "c1", multiChild: true, showChildSheet: false,
  canWrite: true, togglingName: "", removingId: "", requestsLabel: "1 条待处理",
  baseLearning: [
    { name: "语文", selected: true }, { name: "数学", selected: true }, { name: "英语", selected: true },
    { name: "科学", selected: false }, { name: "道德与法治", selected: false }, { name: "音乐", selected: false }
  ],
  addedLearning: [{ id: "s7", name: "书法", custom: true, canRemove: true }],
  addedActivities: [
    { id: "s4", name: "游泳", scheduleLabel: "每周三、六 17:30–18:30" },
    { id: "s5", name: "钢琴", scheduleLabel: "还没有固定时间" }
  ],
  showCatalog: false, showSchedule: false
};


/* ---------------- 记录详情（D7：已确认的正式记录） ---------------- */
const recordDetail = {
  loading: false, saving: false, error: "", actionError: "", canWrite: true, id: "sub-9",
  statusTone: "pri", statusLabel: "已确认", titleText: "语文",
  submission: { id: "sub-9", child_id: "c1", state: "confirmed", awaiting_upload: false, media_count: 2,
    can_finalize_upload: false, time_label: "9 月 5 日 19:20", submitted_label: "9 月 5 日 19:26" },
  detailView: {
    hasRecord: true, isActivity: false, subjectName: "语文", subjectClass: "s-chinese",
    summary: "复习了《望庐山瀑布》，重点是「疑是银河落九天」的默写和三个生字。",
    knowledgeCount: 2,
    knowledge: [
      { id: "k1", name: "《望庐山瀑布》默写", category: "古诗", confLabel: "识别可靠", confTone: "high", confLevel: 3,
        evidence: "照片第 1 张有整首诗的抄写" },
      { id: "k2", name: "生字：瀑、炉、疑", category: "生字", confLabel: "一般", confTone: "mid", confLevel: 2, evidence: "" }
    ]
  },
  reviewsOpen: true, reviewsLoading: false, reviewsError: "", hasDue: true,
  reviews: [
    { review_id: "r1", name: "《望庐山瀑布》默写", statusTone: "att", statusText: "今天到期",
      feedbackText: "9 月 3 日：完成了一半，间隔已取一半", next_before: "" },
    { review_id: "r2", name: "生字：瀑、炉、疑", statusTone: "neutral", statusText: "9 月 12 日再复习",
      feedbackText: "9 月 5 日：完成", next_before: "1" }
  ]
};


/* ---------------- 课外活动打点（记录这次练习） ---------------- */
const activityEdit = {
  loading: false, error: "", saveError: "", canWrite: true,
  childId: "c1", childName: "小满", kicker: "游泳 · 课外活动",
  subjects: [{ id: "s4", name: "游泳" }, { id: "s5", name: "钢琴" }], subjectIndex: 0, subjectId: "s4", subjectName: "游泳",
  date: "2026-09-06", time: "17:30", today: "2026-09-06",
  duration: 45, durationText: "45 分钟", durationMin: 10, durationMax: 180,
  note: "自由泳换气练了 20 分钟，教练说手臂动作稳定了。", noteCount: 24, saving: false
};


/* ---------------- 首次进入（A1 选择路径 / A2 建家庭） ---------------- */
const onboardingBase = {
  loading: false, state: "unbound", mode: "choice", error: "", submitting: false,
  familyName: "", childName: "", grade: "三年级", relationship: "妈妈", budget: 15,
  grades: ["一年级", "二年级", "三年级"], relations: ["妈妈", "爸爸", "其他"], gradeIndex: 2, relationIndex: 0,
  customRelation: false, familyPlaceholder: "不填时使用「孩子称呼」的家",
  canSubmit: false, submitHint: "填写孩子称呼后就可以创建",
  inviteToken: "", tokenError: "", request: null, refreshing: false, canceling: false
};

const onboardingCreate = { ...onboardingBase, mode: "create", childName: "小满", canSubmit: true, submitHint: "" };


/* ---------------- 家庭与成员 ---------------- */
const familyMembers = {
  loading: false, error: "", isManager: true, sharing: false, shareReady: true, sharePath: "", copying: false,
  family: { display_name: "小满的家" }, roleNote: "", requestCount: 1, requestText: "1 条申请等你确认",
  invites: [{ id: "i1", expiryLabel: "明天 19:20" }],
  members: [
    { id: "m1", avatar: "妈", relationship_label: "妈妈", roleText: "管理员 · 可记录与确认", is_self: true },
    { id: "m2", avatar: "爸", relationship_label: "爸爸", roleText: "家长 · 可记录与确认", is_self: false },
    { id: "m3", avatar: "奶", relationship_label: "奶奶", roleText: "只读成员 · 只能查看", is_self: false }
  ],
  requests: [], inviteListUnavailable: false,
  showMember: false, selectedMember: null, relationshipDraft: "", roleOptions: ["管理员", "家长", "只读成员"],
  roleIndex: 1, savingMember: false, sheetError: ""
};

module.exports = {
  today: { page: "pages/today", data: base, tabBar },
  "today-guide": { page: "pages/today", data: guide, tabBar },
  "today-sheet": { page: "pages/today", data: sheet, tabBar },
  records: { page: "pages/records", data: records, tabBar: { ...tabBar, selected: 2 } },
  confirm: { page: "pages/submission", name: "confirm", data: confirmDraft, tabBar: null, styles: ["components/submission-materials/index.wxss"] },
  reports: { page: "pages/reports", data: reports, tabBar: { ...tabBar, selected: 3 } },
  calendar: { page: "pages/calendar", data: calendar, tabBar: { ...tabBar, selected: 1 } },
  "calendar-editor": { page: "pages/calendar", data: calendarEditor, tabBar: { ...tabBar, selected: 1 } },
  settings: { page: "pages/settings", data: settings, tabBar: { ...tabBar, selected: 4 } },
  "records-history": { page: "pages/records", data: recordsHistory, tabBar: { ...tabBar, selected: 2 } },
  "record-detail": { page: "pages/record-detail", data: recordDetail, tabBar: null,
    styles: ["components/submission-materials/index.wxss", "pages/submission/detail.wxss"] },
  "activity-edit": { page: "pages/activity", name: "edit", data: activityEdit, tabBar: null },
  onboarding: { page: "pages/family-onboarding", data: onboardingBase, tabBar: null },
  "onboarding-create": { page: "pages/family-onboarding", data: onboardingCreate, tabBar: null },
  "family-members": { page: "pages/family-members", data: familyMembers, tabBar: null }
};
