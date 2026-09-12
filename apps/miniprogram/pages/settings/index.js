const api = require("../../utils/api");
const childContext = require("../../utils/child-context");
const ui = require("../../utils/ui");

const BASIC_LEARNING = ["数学", "语文", "英语"];
const LEARNING_CATALOG = ["科学", "道德与法治", "物理", "化学", "生物", "历史", "地理", "政治", "美术", "音乐", "体育", "劳动"];
const ACTIVITY_CATALOG = ["游泳", "乒乓球", "篮球", "羽毛球", "足球", "网球", "围棋", "国际象棋", "钢琴", "小提琴", "舞蹈", "武术", "跆拳道", "书法", "绘画", "编程", "机器人"];
const WEEKDAY_LABELS = ["一", "二", "三", "四", "五", "六", "日"];
const TRAVEL_PRESETS = ["上学", "放学", "接送", "自定义"];
/* 携带能力标识后服务端才会对本客户端返回 mixed-time 数据，否则遇到多组时间会 fail-closed 返回 409。 */
const WEEKLY_SLOTS_CAPABILITY = "weekly-time-slots-v1";

/* 只有 is_custom 的科目/活动允许移出或改安排，预置的三科只切换在学状态。 */
function isCustom(subject) {
  return subject.is_custom !== false;
}

function weekdayText(weekdays) {
  const names = [];
  weekdays.forEach((day) => { if (WEEKDAY_LABELS[day]) names.push(WEEKDAY_LABELS[day]); });
  return names.join("、");
}

function hhmm(value) {
  return value ? value.slice(0, 5) : value;
}

/* 把 canonical time_slots 按相同起止时间自动分组，展示层紧凑但编辑层仍逐星期展开。 */
function groupSlots(slots) {
  const groups = [];
  (slots || []).slice().sort((a, b) => a.weekday - b.weekday).forEach((slot) => {
    const start = hhmm(slot.start_time);
    const end = hhmm(slot.end_time);
    const last = groups[groups.length - 1];
    if (last && last.start === start && last.end === end) last.weekdays.push(slot.weekday);
    else groups.push({ start, end, weekdays: [slot.weekday] });
  });
  return groups;
}

/* 相同时间合并成「周一、二、五 18:00–19:00；周三 19:00–20:00」这样的一行摘要。 */
function slotsSummary(slots) {
  const groups = groupSlots(slots);
  if (!groups.length) return "";
  return groups.map((group) => `${weekdayText(group.weekdays)} ${group.start}–${group.end}`).join("；");
}

/* 编辑草稿：每个已选星期恰好一行，保留各自时间；派生 slots 用于校验与提交。 */
function rowsFromSlots(slots) {
  return (slots || []).slice().sort((a, b) => a.weekday - b.weekday).map((slot) => ({
    weekday: slot.weekday, label: `周${WEEKDAY_LABELS[slot.weekday]}`,
    start: hhmm(slot.start_time), end: hhmm(slot.end_time)
  }));
}

/* 从当前草稿派生 canonical slots：统一时间用同一对起止，分别设置用逐星期各自的时间。 */
function stateSlots(weekdays, perDay, dayRows, startTime, endTime) {
  if (perDay) {
    return dayRows.slice().sort((a, b) => a.weekday - b.weekday)
      .map((row) => ({ weekday: row.weekday, start_time: row.start, end_time: row.end }));
  }
  return weekdays.slice().sort((a, b) => a - b)
    .map((weekday) => ({ weekday, start_time: startTime, end_time: endTime }));
}

/* 保留已有星期的时间，新增星期继承传入的统一时间上下文。 */
function buildDayRows(weekdays, prevRows, inheritStart, inheritEnd) {
  const prev = {};
  (prevRows || []).forEach((row) => { prev[row.weekday] = row; });
  return weekdays.slice().sort((a, b) => a - b).map((weekday) => {
    const existing = prev[weekday];
    return {
      weekday, label: `周${WEEKDAY_LABELS[weekday]}`,
      start: existing ? existing.start : inheritStart,
      end: existing ? existing.end : inheritEnd
    };
  });
}

function scheduleLabel(schedule) {
  if (!schedule) return "尚未设置时间";
  const slots = schedule.time_slots || [];
  if (!slots.length) return "时间不固定";
  return `每周${slotsSummary(slots)}`;
}

function travelLabel(item) {
  return `每周${slotsSummary(item.time_slots || [])}`;
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", multiChild: false, showChildSheet: false,
    archivedChildren: [], canAddChild: true, isManager: true, childLimitHint: childContext.limitHint(),
    canWrite: true, subjects: [],
    baseLearning: [], addedLearning: [], addedActivities: [], togglingName: "", removingId: "",
    pendingRequests: 0, requestsLabel: "",
    showCatalog: false, catalogType: "learning", catalogTitle: "", catalogWord: "科目",
    catalogOptions: [], allCatalogOptions: [], catalogMode: "catalog", catalogQuery: "",
    selectedCatalogName: "", customCatalogName: "", addingCatalog: false, catalogError: "",
    showSchedule: false, scheduleSubject: null, scheduleId: "",
    weekdayLabels: WEEKDAY_LABELS,
    weekdays: [], weekdaySelected: [false, false, false, false, false, false, false],
    startTime: "18:00", endTime: "19:00", flexible: false, scheduleSummary: "请选择至少一天",
    perDay: false, dayRows: [], scheduleGroups: [],
    savingSchedule: false, scheduleError: "", removingActivity: false,
    travelArrangements: [], travelPresets: TRAVEL_PRESETS, showTravelEditor: false,
    editingTravelId: "", travelName: "", travelPreset: "", travelWeekdays: [],
    travelWeekdaySelected: [false, false, false, false, false, false, false],
    travelStartTime: "07:30", travelEndTime: "08:10", travelError: "", travelEndError: false,
    travelPerDay: false, travelDayRows: [], travelGroups: [],
    savingTravel: false, deletingTravel: false, travelKey: ""
  },
  async onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 4 });
    await this.load();
    const app = getApp();
    const travelId = app.globalData.openTravelArrangementId;
    app.globalData.openTravelArrangementId = "";
    if (travelId) this.openTravelById(travelId);
  },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  openFamily() { wx.navigateTo({ url: "/pages/family-members/index" }); },
  openDeleteSettings() { wx.navigateTo({ url: "/pages/delete-settings/index" }); },
  openNotifications() { wx.navigateTo({ url: "/pages/notifications/index" }); },
  openAbout() {
    wx.showModal({
      title: "关于知芽",
      content: "AI 只负责整理草稿，是否成为正式记录由你确认。复习日期由固定规则安排，不做打分，也不预测该学什么。",
      showCancel: false,
      confirmText: "知道了"
    });
  },
  /* 待审批数量只是入口上的提示，读不到就不显示。 */
  async loadPendingRequests(member) {
    if (member && member.role !== "manager") return 0;
    try {
      const requests = await api.request("/families/current/requests");
      return requests.filter((item) => item.status === "pending").length;
    } catch {
      return 0;
    }
  },
  async load() {
    /* 切换孩子会重新进入 load，用代际号丢弃上一轮迟到的响应，避免串档。 */
    const generation = (this.loadGeneration || 0) + 1;
    this.loadGeneration = generation;
    this.setData({ loading: true, error: "" });
    try {
      /* 一次取全量档案：切换列表只放在用的，已归档的单独列出来供恢复。 */
      const profiles = await api.request("/children?include_archived=true");
      if (this.loadGeneration !== generation) return;
      const active = profiles.filter((item) => item.active !== false);
      const archivedChildren = childContext.decorateAll(profiles.filter((item) => item.active === false));
      const selection = childContext.syncSelection(getApp(), active);
      const member = getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      const isManager = !member || member.role === "manager";
      const shared = {
        children: selection.children, multiChild: selection.multiChild,
        archivedChildren, canAddChild: childContext.canAddChild(active), canWrite, isManager
      };
      if (!selection.children.length) {
        return this.setData({ loading: false, ...shared, childIndex: 0, childId: "", subjects: [],
          baseLearning: [], addedLearning: [], addedActivities: [], travelArrangements: [] });
      }
      const childId = selection.childId;
      const [subjects, scheduleData, travelData, pendingRequests] = await Promise.all([
        api.request(`/children/${childId}/subjects`),
        api.request(`/children/${childId}/activity-schedules`, { capabilities: WEEKLY_SLOTS_CAPABILITY }),
        api.request(`/children/${childId}/travel-arrangements`, { capabilities: WEEKLY_SLOTS_CAPABILITY }),
        this.loadPendingRequests(member)
      ]);
      if (this.loadGeneration !== generation) return;
      const scheduleMap = {};
      scheduleData.items.forEach((item) => { scheduleMap[item.subject_id] = item; });
      const activeLearning = subjects.filter((item) => item.kind === "learning" && item.active);
      const activeActivities = subjects.filter((item) => item.kind === "activity" && item.active);
      const byLearningName = {};
      subjects.forEach((item) => { if (item.kind === "learning") byLearningName[item.name] = item; });
      const baseLearning = BASIC_LEARNING.map((name) => ({
        name,
        subject: byLearningName[name] || null,
        selected: Boolean(byLearningName[name] && byLearningName[name].active)
      }));
      const addedLearning = activeLearning.filter((item) => !BASIC_LEARNING.includes(item.name)).map((item) => ({
        ...item,
        custom: isCustom(item) && !LEARNING_CATALOG.includes(item.name),
        canRemove: isCustom(item)
      }));
      const addedActivities = activeActivities.map((item) => {
        const schedule = scheduleMap[item.id] || null;
        return { ...item, short: item.name.charAt(0), schedule, scheduleLabel: scheduleLabel(schedule),
          iconClass: ui.activityIcon(item.name, "pri"),
          custom: isCustom(item) && !ACTIVITY_CATALOG.includes(item.name) };
      });
      const travelArrangements = (travelData.items || []).map((item) => ({
        ...item,
        scheduleLabel: travelLabel(item),
        marker: item.name.charAt(0) || "行"
      }));
      this.setData({ loading: false, ...shared, childIndex: selection.childIndex, childId,
        subjects, baseLearning, addedLearning, addedActivities, togglingName: "", removingId: "",
        travelArrangements,
        pendingRequests, requestsLabel: pendingRequests ? `${pendingRequests} 份申请` : "" });
    } catch (error) {
      /* 弱网时保留已加载的科目与活动，只在顶部给一条可重试的说明。 */
      if (this.loadGeneration !== generation) return;
      this.setData({ loading: false, error: error.message });
    }
  },
  openChildSheet() { if (this.data.children.length) this.setData({ showChildSheet: true }); },
  closeChildSheet() { this.setData({ showChildSheet: false }); },
  chooseChild(event) {
    const childIndex = Number(event.currentTarget.dataset.index);
    getApp().selectChild(this.data.children[childIndex].id);
    this.setData({ childIndex, showChildSheet: false });
    this.load();
  },
  /* 新建与编辑走同一个表单页，避免两处重复维护名字与时长的校验文案。 */
  addChild() {
    if (!this.guardWrite()) return;
    if (!this.data.canAddChild) return wx.showToast({ title: this.data.childLimitHint, icon: "none" });
    this.setData({ showChildSheet: false });
    wx.navigateTo({ url: "/pages/child-edit/index?mode=create" });
  },
  editChild(event) {
    if (!this.guardWrite()) return;
    const childId = event.currentTarget.dataset.id || this.data.childId;
    if (!childId) return;
    this.setData({ showChildSheet: false });
    wx.navigateTo({ url: `/pages/child-edit/index?mode=edit&child_id=${childId}` });
  },
  guardWrite() {
    if (this.data.canWrite) return true;
    wx.showToast({ title: "你是只读成员，改动请找管理员", icon: "none" });
    return false;
  },
  async toggleBaseLearning(event) {
    if (!this.guardWrite()) return;
    const option = this.data.baseLearning[Number(event.currentTarget.dataset.index)];
    if (this.data.togglingName) return;
    this.setData({ togglingName: option.name });
    try {
      if (option.subject) await api.request(`/subjects/${option.subject.id}`, { method: "PATCH", data: { active: !option.selected } });
      else await api.request("/subjects", { method: "POST", data: { child_id: this.data.childId, name: option.name, kind: "learning" } });
      wx.showToast({ title: option.selected ? `已移出${option.name}` : `已加入${option.name}`, icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ togglingName: "" });
      wx.showToast({ title: error.message, icon: "none" });
    }
  },
  removeLearning(event) {
    if (!this.guardWrite()) return;
    const subject = this.data.addedLearning.find((item) => item.id === event.currentTarget.dataset.id);
    if (!subject) return;
    wx.showModal({ title: `移出「${subject.name}」？`, content: "已有的学习记录会保留，只是不再出现在选项里。", confirmText: "移出", confirmColor: "#A85742", success: async (result) => {
      if (!result.confirm) return;
      this.setData({ removingId: subject.id });
      try {
        await api.request(`/subjects/${subject.id}`, { method: "PATCH", data: { active: false } });
        wx.showToast({ title: "已移出", icon: "success" });
        await this.load();
      } catch (error) {
        this.setData({ removingId: "" });
        wx.showToast({ title: error.message, icon: "none" });
      }
    } });
  },
  openCatalog(event) {
    const type = event.currentTarget.dataset.type;
    const names = type === "activity" ? ACTIVITY_CATALOG : LEARNING_CATALOG;
    const activeNames = new Set(this.data.subjects.filter((item) => item.kind === type && item.active).map((item) => item.name));
    const options = names.map((name) => ({ name, added: activeNames.has(name) }));
    this.setData({
      showCatalog: true, catalogType: type,
      catalogTitle: type === "activity" ? "添加课外活动" : "添加其他科目",
      catalogWord: type === "activity" ? "课外活动" : "科目",
      catalogMode: "catalog", catalogQuery: "", catalogError: "",
      catalogOptions: options, allCatalogOptions: options,
      selectedCatalogName: "", customCatalogName: ""
    });
  },
  closeCatalog() { if (!this.data.addingCatalog) this.setData({ showCatalog: false }); },
  changeCatalogMode(event) {
    if (this.data.addingCatalog) return;
    this.setData({ catalogMode: event.currentTarget.dataset.mode, selectedCatalogName: "", catalogError: "" });
  },
  filterCatalog(event) {
    const catalogQuery = event.detail.value.trim();
    this.setData({ catalogQuery, catalogOptions: this.data.allCatalogOptions.filter((item) => !catalogQuery || item.name.includes(catalogQuery)) });
  },
  chooseCatalog(event) {
    const option = this.data.catalogOptions[Number(event.currentTarget.dataset.index)];
    if (!option.added) this.setData({ selectedCatalogName: option.name, customCatalogName: "", catalogError: "" });
  },
  setField(event) {
    const field = event.currentTarget.dataset.field;
    this.setData({ [field]: event.detail.value });
    if (field === "customCatalogName") this.setData({ catalogError: "" });
    if (field === "startTime" || field === "endTime") this.updateScheduleSummary();
    if (field === "travelName" || field === "travelStartTime" || field === "travelEndTime") {
      const start = field === "travelStartTime" ? event.detail.value : this.data.travelStartTime;
      const end = field === "travelEndTime" ? event.detail.value : this.data.travelEndTime;
      this.setData({ travelError: "", travelEndError: end <= start });
      if (field !== "travelName") this.updateTravelSummary();
    }
  },
  async addCatalog() {
    if (!this.guardWrite()) return;
    const name = (this.data.customCatalogName.trim() || this.data.selectedCatalogName).trim();
    if (!name) return this.setData({ catalogError: "请先选择或输入一个名称。" });
    const sameName = this.data.subjects.find((item) => item.name === name);
    if (sameName && sameName.kind !== this.data.catalogType) return this.setData({ catalogError: "这个名称已用于其他类型。" });
    this.setData({ addingCatalog: true, catalogError: "" });
    try {
      if (sameName) await api.request(`/subjects/${sameName.id}`, { method: "PATCH", data: { active: true } });
      else {
        const data = { child_id: this.data.childId, name, kind: this.data.catalogType };
        if (this.data.catalogType === "activity") data.color = "#D68C51";
        await api.request("/subjects", { method: "POST", data });
      }
      this.setData({ showCatalog: false, addingCatalog: false });
      wx.showToast({ title: `已添加${name}`, icon: "success" });
      await this.load();
    } catch (error) {
      /* 失败时保留弹层与已选内容，就地给出重试说明。 */
      this.setData({ addingCatalog: false, catalogError: `${error.message}，可以再试一次。` });
    }
  },
  openActivitySchedule(event) {
    const item = this.data.addedActivities[Number(event.currentTarget.dataset.index)];
    const schedule = item.schedule;
    const slots = (schedule && schedule.time_slots) || [];
    const weekdays = slots.map((slot) => slot.weekday).sort((a, b) => a - b);
    const groups = groupSlots(slots);
    const perDay = groups.length > 1;
    const startTime = groups.length ? groups[0].start : "18:00";
    const endTime = groups.length ? groups[0].end : "19:00";
    this.setData({
      showSchedule: true, scheduleSubject: item, scheduleId: schedule ? schedule.id : "", weekdays,
      weekdaySelected: Array.from({ length: 7 }, (_, index) => weekdays.includes(index)),
      startTime, endTime, perDay, dayRows: rowsFromSlots(slots),
      flexible: Boolean(schedule && !slots.length),
      scheduleError: "", savingSchedule: false, removingActivity: false
    });
    this.updateScheduleSummary();
  },
  closeSchedule() { if (!this.data.savingSchedule) this.setData({ showSchedule: false }); },
  chooseScheduleMode(event) { this.setData({ flexible: event.currentTarget.dataset.mode === "flexible", scheduleError: "" }); },
  /* 派生分组摘要与提示文案，编辑层始终按星期展开，只有摘要按相同时间合并。 */
  updateScheduleSummary() {
    const slots = stateSlots(this.data.weekdays, this.data.perDay, this.data.dayRows, this.data.startTime, this.data.endTime);
    this.setData({
      scheduleGroups: groupSlots(slots),
      scheduleSummary: slots.length
        ? `每周${slotsSummary(slots)}，会自动出现在日程与今日活动。`
        : "请选择至少一天"
    });
  },
  toggleWeekday(event) {
    const value = Number(event.currentTarget.dataset.value);
    const weekdays = this.data.weekdays.slice();
    const index = weekdays.indexOf(value);
    if (index >= 0) weekdays.splice(index, 1); else weekdays.push(value);
    weekdays.sort((a, b) => a - b);
    const update = { weekdays, weekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.includes(day)), scheduleError: "" };
    if (this.data.perDay) {
      /* 新星期继承统一时间上下文；分别设置无上下文时用排序最前一行的时间。 */
      const source = this.data.dayRows[0] || {};
      update.dayRows = buildDayRows(weekdays, this.data.dayRows, source.start || this.data.startTime, source.end || this.data.endTime);
    }
    this.setData(update);
    this.updateScheduleSummary();
  },
  /* 「某些日期时间不同」开关：展开=逐星期各设一行，收起=合并回统一时间。 */
  toggleSchedulePerDay() {
    if (!this.data.perDay) {
      const dayRows = buildDayRows(this.data.weekdays, this.data.dayRows, this.data.startTime, this.data.endTime);
      this.setData({ perDay: true, dayRows, scheduleError: "" });
      return this.updateScheduleSummary();
    }
    const groups = groupSlots(stateSlots(this.data.weekdays, true, this.data.dayRows, "", ""));
    const first = this.data.dayRows[0];
    if (groups.length > 1 && first) {
      return wx.showModal({
        title: "合并为同一时间？",
        content: `各天时间不同，合并后所有已选日期都将使用周${WEEKDAY_LABELS[first.weekday]}的 ${first.start}–${first.end}。`,
        confirmText: "合并", confirmColor: "#A85742",
        success: (result) => {
          if (!result.confirm) return;
          this.setData({ perDay: false, startTime: first.start, endTime: first.end, scheduleError: "" });
          this.updateScheduleSummary();
        }
      });
    }
    const update = { perDay: false, scheduleError: "" };
    if (first) { update.startTime = first.start; update.endTime = first.end; }
    this.setData(update);
    this.updateScheduleSummary();
  },
  setDayTime(event) {
    const { index, field } = event.currentTarget.dataset;
    const dayRows = this.data.dayRows.slice();
    dayRows[Number(index)] = { ...dayRows[Number(index)], [field]: event.detail.value };
    this.setData({ dayRows, scheduleError: "" });
    this.updateScheduleSummary();
  },
  async saveSchedule() {
    if (!this.guardWrite()) return;
    const flexible = this.data.flexible;
    if (!flexible && !this.data.weekdays.length) return this.setData({ scheduleError: "请选择至少一天。" });
    const slots = flexible ? [] : stateSlots(this.data.weekdays, this.data.perDay, this.data.dayRows, this.data.startTime, this.data.endTime);
    const bad = slots.find((slot) => slot.end_time <= slot.start_time);
    if (bad) return this.setData({ scheduleError: `周${WEEKDAY_LABELS[bad.weekday]}的结束时间要晚于开始时间。` });
    this.setData({ savingSchedule: true, scheduleError: "" });
    const payload = { child_id: this.data.childId, subject_id: this.data.scheduleSubject.id, time_slots: slots, target_per_week: null };
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "PATCH", data: payload, capabilities: WEEKLY_SLOTS_CAPABILITY });
      else await api.request("/activity-schedules", { method: "POST", data: payload, capabilities: WEEKLY_SLOTS_CAPABILITY });
      this.setData({ showSchedule: false, savingSchedule: false });
      wx.showToast({ title: "已保存安排", icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ savingSchedule: false, scheduleError: `${error.message}，安排还没保存，可以再试一次。` });
    }
  },
  async removeActivity() {
    if (!this.guardWrite()) return;
    const confirmed = await new Promise((resolve) => wx.showModal({ title: `移除「${this.data.scheduleSubject.name}」？`, content: "已有的练习记录会保留，只是不再出现在活动列表和日程里。", confirmText: "移除", confirmColor: "#A85742", success: (result) => resolve(result.confirm) }));
    if (!confirmed) return;
    this.setData({ removingActivity: true, scheduleError: "" });
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "DELETE" });
      await api.request(`/subjects/${this.data.scheduleSubject.id}`, { method: "PATCH", data: { active: false } });
      this.setData({ showSchedule: false, removingActivity: false });
      wx.showToast({ title: "已移除", icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ removingActivity: false, scheduleError: `${error.message}，这项活动还在，可以再试一次。` });
    }
  },
  openTravelCreate() {
    if (!this.guardWrite()) return;
    this.setData({
      showTravelEditor: true, editingTravelId: "", travelName: "上学", travelPreset: "上学",
      travelWeekdays: [0, 1, 2, 3, 4],
      travelWeekdaySelected: [true, true, true, true, true, false, false],
      travelStartTime: "07:30", travelEndTime: "08:10", travelError: "", travelEndError: false,
      travelPerDay: false, travelDayRows: [], travelGroups: [],
      savingTravel: false, deletingTravel: false,
      travelKey: api.newIdempotencyKey("travel")
    });
    this.updateTravelSummary();
  },
  openTravel(event) {
    if (!this.guardWrite()) return;
    this.openTravelById(event.currentTarget.dataset.id);
  },
  openTravelById(travelId) {
    const item = this.data.travelArrangements.find((row) => row.id === travelId);
    if (!item) return;
    const slots = item.time_slots || [];
    const weekdays = slots.map((slot) => slot.weekday).sort((a, b) => a - b);
    const groups = groupSlots(slots);
    const perDay = groups.length > 1;
    this.setData({
      showTravelEditor: true, editingTravelId: item.id, travelName: item.name,
      travelPreset: TRAVEL_PRESETS.includes(item.name) ? item.name : "自定义",
      travelWeekdays: weekdays,
      travelWeekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.includes(day)),
      travelStartTime: groups.length ? groups[0].start : "07:30",
      travelEndTime: groups.length ? groups[0].end : "08:10",
      travelPerDay: perDay, travelDayRows: rowsFromSlots(slots),
      travelError: "", travelEndError: false, savingTravel: false, deletingTravel: false, travelKey: ""
    });
    this.updateTravelSummary();
  },
  closeTravelEditor() {
    if (!this.data.savingTravel && !this.data.deletingTravel) this.setData({ showTravelEditor: false });
  },
  chooseTravelPreset(event) {
    const preset = event.currentTarget.dataset.name;
    const update = { travelPreset: preset, travelError: "" };
    if (preset !== "自定义") update.travelName = preset;
    else if (TRAVEL_PRESETS.includes(this.data.travelName)) update.travelName = "";
    this.setData(update);
  },
  /* 出行摘要同样按相同时间自动合并展示。 */
  updateTravelSummary() {
    const slots = stateSlots(this.data.travelWeekdays, this.data.travelPerDay, this.data.travelDayRows, this.data.travelStartTime, this.data.travelEndTime);
    this.setData({ travelGroups: groupSlots(slots) });
  },
  toggleTravelWeekday(event) {
    const value = Number(event.currentTarget.dataset.value);
    const weekdays = this.data.travelWeekdays.slice();
    const index = weekdays.indexOf(value);
    if (index >= 0) weekdays.splice(index, 1); else weekdays.push(value);
    weekdays.sort((a, b) => a - b);
    const update = {
      travelWeekdays: weekdays,
      travelWeekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.includes(day)),
      travelError: ""
    };
    if (this.data.travelPerDay) {
      const source = this.data.travelDayRows[0] || {};
      update.travelDayRows = buildDayRows(weekdays, this.data.travelDayRows, source.start || this.data.travelStartTime, source.end || this.data.travelEndTime);
    }
    this.setData(update);
    this.updateTravelSummary();
  },
  toggleTravelPerDay() {
    if (!this.data.travelPerDay) {
      const travelDayRows = buildDayRows(this.data.travelWeekdays, this.data.travelDayRows, this.data.travelStartTime, this.data.travelEndTime);
      this.setData({ travelPerDay: true, travelDayRows, travelError: "" });
      return this.updateTravelSummary();
    }
    const groups = groupSlots(stateSlots(this.data.travelWeekdays, true, this.data.travelDayRows, "", ""));
    const first = this.data.travelDayRows[0];
    if (groups.length > 1 && first) {
      return wx.showModal({
        title: "合并为同一时间？",
        content: `各天时间不同，合并后所有已选日期都将使用周${WEEKDAY_LABELS[first.weekday]}的 ${first.start}–${first.end}。`,
        confirmText: "合并", confirmColor: "#A85742",
        success: (result) => {
          if (!result.confirm) return;
          this.setData({ travelPerDay: false, travelStartTime: first.start, travelEndTime: first.end, travelError: "", travelEndError: false });
          this.updateTravelSummary();
        }
      });
    }
    const update = { travelPerDay: false, travelError: "" };
    if (first) { update.travelStartTime = first.start; update.travelEndTime = first.end; }
    this.setData(update);
    this.updateTravelSummary();
  },
  setTravelDayTime(event) {
    const { index, field } = event.currentTarget.dataset;
    const travelDayRows = this.data.travelDayRows.slice();
    travelDayRows[Number(index)] = { ...travelDayRows[Number(index)], [field]: event.detail.value };
    this.setData({ travelDayRows, travelError: "" });
    this.updateTravelSummary();
  },
  async saveTravel() {
    if (!this.guardWrite() || this.data.savingTravel) return;
    const name = this.data.travelName.trim();
    if (!name) return this.setData({ travelError: "请填写出行安排名称。" });
    if (!this.data.travelWeekdays.length) return this.setData({ travelError: "请至少选择一天。" });
    const slots = stateSlots(this.data.travelWeekdays, this.data.travelPerDay, this.data.travelDayRows, this.data.travelStartTime, this.data.travelEndTime);
    const bad = slots.find((slot) => slot.end_time <= slot.start_time);
    if (bad) {
      return this.setData({
        travelError: this.data.travelPerDay ? `周${WEEKDAY_LABELS[bad.weekday]}的结束时间要晚于开始时间。` : "结束时间要晚于开始时间。",
        travelEndError: !this.data.travelPerDay
      });
    }
    const payload = { name, time_slots: slots };
    this.setData({ savingTravel: true, travelError: "" });
    try {
      if (this.data.editingTravelId) {
        await api.request(`/travel-arrangements/${this.data.editingTravelId}`, { method: "PATCH", data: payload, capabilities: WEEKLY_SLOTS_CAPABILITY });
      } else {
        await api.request("/travel-arrangements", { method: "POST", data: { ...payload, child_id: this.data.childId }, idempotencyKey: this.data.travelKey, capabilities: WEEKLY_SLOTS_CAPABILITY });
      }
      this.setData({ showTravelEditor: false, savingTravel: false });
      wx.showToast({ title: "已保存出行安排", icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ savingTravel: false, travelError: `${error.message}，安排还没保存，可以再试一次。` });
    }
  },
  async deleteTravel() {
    if (!this.guardWrite() || !this.data.editingTravelId) return;
    const confirmed = await new Promise((resolve) => wx.showModal({
      title: `删除「${this.data.travelName}」？`,
      content: "删除后不会再出现在日程里，其他活动和学习记录不受影响。",
      confirmText: "删除", confirmColor: "#A6423B",
      success: (result) => resolve(result.confirm)
    }));
    if (!confirmed) return;
    this.setData({ deletingTravel: true, travelError: "" });
    try {
      await api.request(`/travel-arrangements/${this.data.editingTravelId}`, { method: "DELETE" });
      this.setData({ showTravelEditor: false, deletingTravel: false });
      wx.showToast({ title: "已删除", icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ deletingTravel: false, travelError: `${error.message}，这项安排还在，可以再试一次。` });
    }
  }
});
