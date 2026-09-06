const api = require("../../utils/api");
const ui = require("../../utils/ui");
const childContext = require("../../utils/child-context");

const WEEKDAYS = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"];
const KIND_LABELS = { class: "课外活动", activity: "自主活动", other: "其他安排" };
/* 打开今日先看"今天要发生什么"：日程默认展开，复习与学习默认折叠，靠小标题上的数量摘要引导展开。 */
const DEFAULT_SECTIONS = { review: false, learning: false, activity: true };
const TODO_PREVIEW = 3;
const RING_TICKS = 12;

function dayLabel(iso) {
  const parts = String(iso || "").split("-");
  if (parts.length !== 3) return "";
  const value = new Date(`${iso}T12:00:00`);
  return `${Number(parts[1])} 月 ${Number(parts[2])} 日 ${WEEKDAYS[value.getDay()] || ""}`;
}

/* 安排环：12 个刻度只描述今天到期复习的构成（必做 / 有余力），不是完成率，也不是评价。
   项数超过刻度数时按比例折算，中心数字始终是真实项数。 */
function ringTicks(required, total) {
  const sum = Math.max(0, Number(total) || 0);
  const req = Math.min(Math.max(0, Number(required) || 0), sum);
  let filled = Math.min(RING_TICKS, sum);
  let reqTicks = req;
  if (sum > RING_TICKS) {
    filled = RING_TICKS;
    reqTicks = req ? Math.max(1, Math.round((RING_TICKS * req) / sum)) : 0;
  }
  const ticks = [];
  for (let index = 0; index < RING_TICKS; index += 1) {
    let cls = "idle";
    if (index < reqTicks) cls = "req";
    else if (index < filled) cls = "opt";
    ticks.push({ deg: Math.round((360 / RING_TICKS) * index), cls });
  }
  return ticks;
}

/* 折叠偏好只认三个布尔位，storage 里的脏数据一律按 DEFAULT_SECTIONS 回落。 */
function normalizeSections(value) {
  const source = value && typeof value === "object" ? value : {};
  const pick = (key) => (typeof source[key] === "boolean" ? source[key] : DEFAULT_SECTIONS[key]);
  return { review: pick("review"), learning: pick("learning"), activity: pick("activity") };
}

/* Todo 超过 3 张折叠；「有余力再做」小标题挂在第一张可选卡上。 */
function todoView(must, optional, expanded) {
  const all = (must || []).concat(optional || []);
  const shown = expanded ? all : all.slice(0, TODO_PREVIEW);
  return {
    cards: shown.map((group, index) => ({
      ...group,
      first_optional: !!group.optional && (index === 0 || !shown[index - 1].optional)
    })),
    hidden: expanded ? 0 : Math.max(0, all.length - TODO_PREVIEW)
  };
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", dashboard: null,
    sections: { ...DEFAULT_SECTIONS }, reviewReturn: null, reviewGroupId: "",
    reviewFocusText: "", dayLabel: "",
    hero: { required: 0, optional: 0, total: 0, minutes: 0, note: "", ticks: [] },
    todoCards: [], hiddenTodoCount: 0, todosExpanded: false, showChildSheet: false, multiChild: false, canAddChild: true,
    sectionMeta: { review: "", learning: "", activity: "" }
  },
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 0 });
    this.load();
  },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  async load() {
    const generation = (this.loadGeneration || 0) + 1;
    this.loadGeneration = generation;
    this.setData({ loading: true, error: "" });
    try {
      const profiles = await api.request("/children");
      if (generation !== this.loadGeneration) return;
      const app = getApp();
      const selection = childContext.syncSelection(app, profiles);
      const children = selection.children;
      const canAddChild = childContext.canAddChild(profiles);
      if (!children.length) {
        this.setData({ loading: false, children, dashboard: null, childId: "", multiChild: false, canAddChild });
        return;
      }
      const childIndex = selection.childIndex;
      const childId = selection.childId;
      const [dashboard, subjects] = await Promise.all([
        api.request(`/children/${childId}/dashboard`),
        api.request(`/children/${childId}/subjects`)
      ]);
      if (generation !== this.loadGeneration) return;
      const activitiesByName = Object.fromEntries(subjects.filter((item) => item.kind === "activity" && item.active).map((item) => [item.name, item.id]));
      dashboard.schedule_items = dashboard.schedule_items.map((item) => ({ ...item, subject_id: item.subject_id || activitiesByName[item.name] || "",
        kind_label: KIND_LABELS[item.kind] || "其他安排",
        time_text: `${item.start_time}–${item.end_time}${item.repeat_weekly ? " · 每周重复" : ""}`,
        action_text: item.past ? "补记这次练习" : "记录这次练习" }));
      dashboard.daily_summary.subjects = dashboard.daily_summary.subjects.map((item) => ({ ...item, summary_text: item.summaries.join("；"),
        subject_class: ui.subjectClass(item.subject_name), subject_mark: ui.subjectMark(item.subject_name) }));
      dashboard.must_todo_groups = dashboard.todo_groups.filter((item) => !item.optional);
      dashboard.optional_todo_groups = dashboard.todo_groups.filter((item) => item.optional);
      const scheduledSubjects = new Set(dashboard.schedule_items.map((item) => item.subject_id).filter(Boolean));
      dashboard.optional_activity_suggestions = dashboard.activity_suggestions.filter((item) => item.suggested && !scheduledSubjects.has(item.subject_id));
      dashboard.is_empty = !dashboard.todo_groups.length && !dashboard.daily_summary.record_count && !dashboard.schedule_items.length && !dashboard.optional_activity_suggestions.length;
      dashboard.show_guide = !dashboard.todo_groups.length && !dashboard.daily_summary.record_count;
      dashboard.activity_count = dashboard.schedule_items.length + dashboard.optional_activity_suggestions.length;
      const view = todoView(dashboard.must_todo_groups, dashboard.optional_todo_groups, this.data.todosExpanded);
      this.setData({ loading: false, children, childIndex, childId, dashboard,
        multiChild: selection.multiChild, canAddChild,
        dayLabel: dayLabel(dashboard.day),
        hero: {
          required: dashboard.required_todo_count || 0,
          optional: Math.max(0, (dashboard.todo_count || 0) - (dashboard.required_todo_count || 0)),
          total: dashboard.todo_count || 0,
          ticks: ringTicks(dashboard.required_todo_count, dashboard.todo_count),
          minutes: dashboard.estimated_minutes || 0,
          note: dashboard.todo_count > dashboard.required_todo_count
            ? `其中 ${dashboard.todo_count - dashboard.required_todo_count} 项是可选的 · 都是之前确认过的学习内容`
            : "都是之前确认过的学习内容"
        },
        sections: normalizeSections(ui.readPreference("todaySections", childId, DEFAULT_SECTIONS)),
        sectionMeta: {
          review: `${dashboard.todo_count} 项 · 约 ${dashboard.estimated_minutes} 分钟`,
          learning: `已确认 ${dashboard.daily_summary.record_count} 条`,
          activity: `${dashboard.activity_count} 项`
        },
        todoCards: view.cards, hiddenTodoCount: view.hidden });
      if (app.setTabBadge) app.setTabBadge("records", dashboard.pending_confirmation_count);
      const back = app.globalData.reviewReturn;
      if (back && back.childId === childId) {
        const ids = new Set(back.reviewIds);
        const target = dashboard.todo_groups.find((group) => group.items.some((item) => ids.has(item.review_id)));
        this.setData({ reviewReturn: back, reviewGroupId: target ? target.id : "", "sections.review": true,
          reviewFocusText: target ? "已定位这条学习记录的到期复习" : "这条记录当前没有待完成的到期复习" });
        if (target) this.expandTodos();
        delete app.globalData.reviewReturn;
        if (target && wx.pageScrollTo) wx.pageScrollTo({ selector: `#todo-group-${target.id}`, duration: 0 });
      } else if (this.data.reviewReturn && this.data.reviewReturn.childId !== childId) {
        this.setData({ reviewReturn: null, reviewGroupId: "", reviewFocusText: "" });
      }
    } catch (error) {
      if (generation !== this.loadGeneration) return;
      /* 出错时保留已加载到的内容，只在顶部加一条可重试的说明。 */
      this.setData({ loading: false, error: error.message });
    }
  },
  toggleSection(event) {
    const section = event.currentTarget.dataset.section;
    const dashboard = this.data.dashboard || {};
    const counts = {
      review: dashboard.todo_count,
      learning: dashboard.daily_summary ? dashboard.daily_summary.record_count : 0,
      activity: dashboard.activity_count
    };
    /* 待复习即使为空也遵循默认折叠；家长仍可主动展开查看空态说明。 */
    if (!counts[section] && section !== "review") return;
    const sections = { ...this.data.sections, [section]: !this.data.sections[section] };
    this.setData({ sections });
    ui.writePreference("todaySections", this.data.childId, sections);
  },
  expandTodos() {
    const dashboard = this.data.dashboard;
    if (!dashboard) return;
    const view = todoView(dashboard.must_todo_groups, dashboard.optional_todo_groups, true);
    this.setData({ todosExpanded: true, todoCards: view.cards, hiddenTodoCount: view.hidden });
  },
  openChildSheet() { if (this.data.children.length) this.setData({ showChildSheet: true }); },
  closeChildSheet() { this.setData({ showChildSheet: false }); },
  addChild() {
    this.setData({ showChildSheet: false });
    wx.navigateTo({ url: "/pages/child-edit/index?mode=create" });
  },
  async chooseChild(event) {
    const childIndex = Number(event.currentTarget.dataset.index);
    const childId = this.data.children[childIndex].id;
    getApp().selectChild(childId);
    this.setData({ childIndex, childId, showChildSheet: false, todosExpanded: false });
    await this.load();
  },
  async changeChild(event) {
    const childIndex = Number(event.detail.value);
    const childId = this.data.children[childIndex].id;
    getApp().selectChild(childId);
    this.setData({ childIndex, childId });
    await this.load();
  },
  recordLearning() { getApp().globalData.recordIntent = { childId: this.data.childId, view: "new" }; wx.switchTab({ url: "/pages/records/index" }); },
  addSchedule() { getApp().globalData.openCalendarCreate = true; wx.switchTab({ url: "/pages/calendar/index" }); },
  openCalendar() { wx.switchTab({ url: "/pages/calendar/index" }); },
  openPending() { getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "pending" }; wx.switchTab({ url: "/pages/records/index" }); },
  openLearningHistory(event) {
    const filters = { from: this.data.dashboard.day, to: this.data.dashboard.day };
    if (event.currentTarget.dataset.id) filters.subject_id = event.currentTarget.dataset.id;
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
      filters };
    wx.switchTab({ url: "/pages/records/index" });
  },
  returnToRecord() {
    if (!this.data.reviewReturn || this.data.reviewReturn.childId !== this.data.childId) return;
    wx.navigateTo({ url: `/pages/submission/confirm?id=${this.data.reviewReturn.submissionId}` });
  },
  openSettings() { wx.switchTab({ url: "/pages/settings/index" }); },
  openActivity(event) { wx.navigateTo({ url: `/pages/activity/edit?subjectId=${event.currentTarget.dataset.subjectId}` }); },
  async practice(event) {
    try {
      const reviewIds = event.detail.reviewIds.join(",");
      const result = await api.request(`/children/${this.data.childId}/practice-materials?review_ids=${reviewIds}`);
      wx.showModal({
        title: "带练提示",
        content: result.items.map((item, index) => `${index + 1}. ${item.prompt}`).join("\n") || "没有可用提示",
        showCancel: false
      });
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async feedback(event) {
    const { reviewId, action } = event.detail;
    this.feedbackRetryKeys = this.feedbackRetryKeys || {};
    const intent = `${reviewId}:${action}`;
    const idempotencyKey = this.feedbackRetryKeys[intent] || api.newIdempotencyKey("feedback");
    const previous = this.data.dashboard;
    const groups = previous.todo_groups
      .map((group) => ({ ...group, items: group.items.filter((item) => item.review_id !== reviewId) }))
      .filter((group) => group.items.length);
    const must = groups.filter((item) => !item.optional);
    const optional = groups.filter((item) => item.optional);
    const view = todoView(must, optional, this.data.todosExpanded);
    this.setData({
      "dashboard.todo_groups": groups,
      "dashboard.must_todo_groups": must,
      "dashboard.optional_todo_groups": optional,
      todoCards: view.cards,
      hiddenTodoCount: view.hidden
    });
    try {
      await api.request(`/reviews/${reviewId}/feedback`, { method: "POST", data: { action }, idempotencyKey });
      delete this.feedbackRetryKeys[intent];
      wx.showToast({ title: action === "complete" ? "已完成" : "计划已调整", icon: "success" });
      await this.load();
    } catch (error) {
      this.feedbackRetryKeys[intent] = idempotencyKey;
      const rollback = todoView(previous.must_todo_groups, previous.optional_todo_groups, this.data.todosExpanded);
      this.setData({ dashboard: previous, todoCards: rollback.cards, hiddenTodoCount: rollback.hidden });
      wx.showToast({ title: `${error.message}·刚才那条没保存成功`, icon: "none" });
    }
  }
});
