const api = require("../../utils/api");
const childContext = require("../../utils/child-context");
const ui = require("../../utils/ui");

const BASIC_LEARNING = ["数学", "语文", "英语"];
const LEARNING_CATALOG = ["科学", "道德与法治", "物理", "化学", "生物", "历史", "地理", "政治", "美术", "音乐", "体育", "劳动"];
const ACTIVITY_CATALOG = ["游泳", "乒乓球", "篮球", "羽毛球", "足球", "网球", "围棋", "国际象棋", "钢琴", "小提琴", "舞蹈", "武术", "跆拳道", "书法", "绘画", "编程", "机器人"];
const WEEKDAY_LABELS = ["一", "二", "三", "四", "五", "六", "日"];

/* 只有 is_custom 的科目/活动允许移出或改安排，预置的三科只切换在学状态。 */
function isCustom(subject) {
  return subject.is_custom !== false;
}

function weekdayText(weekdays) {
  const names = [];
  weekdays.forEach((day) => { if (WEEKDAY_LABELS[day]) names.push(WEEKDAY_LABELS[day]); });
  return names.join("、");
}

function scheduleLabel(schedule) {
  if (!schedule) return "尚未设置时间";
  if (!schedule.weekdays.length) return "时间不固定";
  const days = weekdayText(schedule.weekdays);
  if (schedule.start_time && schedule.end_time) {
    return `每周${days} · ${schedule.start_time.slice(0, 5)}–${schedule.end_time.slice(0, 5)}`;
  }
  return `每周${days}`;
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", multiChild: false, showChildSheet: false,
    archivedChildren: [], canAddChild: true, isManager: true, childLimitHint: childContext.limitHint(),
    canWrite: true, subjects: [],
    baseLearning: [], addedLearning: [], addedActivities: [], togglingName: "", removingId: "",
    pendingRequests: 0, requestsLabel: "",
    showCatalog: false, catalogType: "learning", catalogTitle: "", catalogSub: "", catalogWord: "科目",
    catalogOptions: [], allCatalogOptions: [], catalogMode: "catalog", catalogQuery: "",
    selectedCatalogName: "", customCatalogName: "", addingCatalog: false, catalogError: "",
    showSchedule: false, scheduleSubject: null, scheduleId: "",
    weekdayLabels: WEEKDAY_LABELS,
    weekdays: [], weekdaySelected: [false, false, false, false, false, false, false],
    startTime: "18:00", endTime: "19:00", flexible: false, scheduleSummary: "请选择至少一天",
    savingSchedule: false, scheduleError: "", removingActivity: false
  },
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 4 });
    this.load();
  },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  openFamily() { wx.navigateTo({ url: "/pages/family-members/index" }); },
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
          baseLearning: [], addedLearning: [], addedActivities: [] });
      }
      const childId = selection.childId;
      const [subjects, scheduleData, pendingRequests] = await Promise.all([
        api.request(`/children/${childId}/subjects`),
        api.request(`/children/${childId}/activity-schedules`),
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
      this.setData({ loading: false, ...shared, childIndex: selection.childIndex, childId,
        subjects, baseLearning, addedLearning, addedActivities, togglingName: "", removingId: "",
        pendingRequests, requestsLabel: pendingRequests ? `${pendingRequests} 份申请` : "" });
    } catch (error) {
      /* 弱网时保留已加载的科目与活动，只在顶部给一条可重试的说明。 */
      if (this.loadGeneration !== generation) return;
      this.setData({ loading: false, error: error.message });
    }
  },
  openChildSheet() { if (this.data.multiChild) this.setData({ showChildSheet: true }); },
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
    wx.showModal({ title: `移出「${subject.name}」？`, content: "已有的学习记录会保留，只是不再出现在选项里。", confirmText: "移出", confirmColor: "#A6423B", success: async (result) => {
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
      catalogSub: type === "activity" ? "只选择已经开始参与的内容" : "只选择已经开始学习的内容",
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
    const weekdays = schedule ? schedule.weekdays : [];
    const startTime = schedule && schedule.start_time ? schedule.start_time.slice(0, 5) : "18:00";
    const endTime = schedule && schedule.end_time ? schedule.end_time.slice(0, 5) : "19:00";
    this.setData({
      showSchedule: true, scheduleSubject: item, scheduleId: schedule ? schedule.id : "", weekdays,
      weekdaySelected: Array.from({ length: 7 }, (_, index) => weekdays.includes(index)),
      startTime, endTime,
      flexible: Boolean(schedule && !schedule.weekdays.length),
      scheduleError: "", savingSchedule: false, removingActivity: false,
      scheduleSummary: weekdays.length
        ? `每周${weekdayText(weekdays)} ${startTime}–${endTime}，会自动出现在日程与今日活动。`
        : "请选择至少一天"
    });
  },
  closeSchedule() { if (!this.data.savingSchedule) this.setData({ showSchedule: false }); },
  chooseScheduleMode(event) { this.setData({ flexible: event.currentTarget.dataset.mode === "flexible", scheduleError: "" }); },
  updateScheduleSummary() {
    const days = weekdayText(this.data.weekdays);
    this.setData({ scheduleSummary: days
      ? `每周${days} ${this.data.startTime}–${this.data.endTime}，会自动出现在日程与今日活动。`
      : "请选择至少一天" });
  },
  toggleWeekday(event) {
    const value = Number(event.currentTarget.dataset.value);
    const weekdays = this.data.weekdays.slice();
    const index = weekdays.indexOf(value);
    if (index >= 0) weekdays.splice(index, 1); else weekdays.push(value);
    weekdays.sort();
    this.setData({ weekdays, weekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.includes(day)), scheduleError: "" });
    this.updateScheduleSummary();
  },
  async saveSchedule() {
    if (!this.guardWrite()) return;
    if (!this.data.flexible && !this.data.weekdays.length) return this.setData({ scheduleError: "请选择至少一天。" });
    if (!this.data.flexible && this.data.endTime <= this.data.startTime) return this.setData({ scheduleError: "结束时间要晚于开始时间。" });
    this.setData({ savingSchedule: true, scheduleError: "" });
    const payload = { child_id: this.data.childId, subject_id: this.data.scheduleSubject.id, weekdays: this.data.flexible ? [] : this.data.weekdays, start_time: this.data.flexible ? null : this.data.startTime, end_time: this.data.flexible ? null : this.data.endTime, target_per_week: null };
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "PATCH", data: payload });
      else await api.request("/activity-schedules", { method: "POST", data: payload });
      this.setData({ showSchedule: false, savingSchedule: false });
      wx.showToast({ title: "已保存安排", icon: "success" });
      await this.load();
    } catch (error) {
      this.setData({ savingSchedule: false, scheduleError: `${error.message}，安排还没保存，可以再试一次。` });
    }
  },
  async removeActivity() {
    if (!this.guardWrite()) return;
    const confirmed = await new Promise((resolve) => wx.showModal({ title: `移除「${this.data.scheduleSubject.name}」？`, content: "已有的练习记录会保留，只是不再出现在活动列表和日程里。", confirmText: "移除", confirmColor: "#A6423B", success: (result) => resolve(result.confirm) }));
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
  }
});
