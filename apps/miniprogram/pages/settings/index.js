const api = require("../../utils/api");

const BASIC_LEARNING = ["数学", "语文", "英语"];
const LEARNING_CATALOG = ["科学", "道德与法治", "物理", "化学", "生物", "历史", "地理", "政治", "美术", "音乐", "体育", "劳动"];
const ACTIVITY_CATALOG = ["游泳", "乒乓球", "篮球", "羽毛球", "足球", "网球", "围棋", "国际象棋", "钢琴", "小提琴", "舞蹈", "武术", "跆拳道", "书法", "绘画", "编程", "机器人"];

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", subjects: [],
    baseLearning: [], addedLearning: [], addedActivities: [],
    showCatalog: false, catalogType: "learning", catalogTitle: "", catalogOptions: [], allCatalogOptions: [],
    catalogMode: "catalog", catalogQuery: "", selectedCatalogName: "", customCatalogName: "", addingCatalog: false,
    showSchedule: false, scheduleSubject: null, scheduleId: "",
    weekdayLabels: ["一", "二", "三", "四", "五", "六", "日"],
    weekdays: [], weekdaySelected: [false, false, false, false, false, false, false],
    startTime: "18:00", endTime: "19:00", flexible: false, scheduleSummary: "请选择至少一天", savingSchedule: false
  },
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 4 });
    this.load();
  },
  openFamily() { wx.navigateTo({ url: "/pages/family-members/index" }); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({ ...item, avatar: item.name ? item.name.charAt(0) : "芽" }));
      if (!children.length) return this.setData({ loading: false, children, subjects: [], baseLearning: [], addedLearning: [], addedActivities: [] });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const [subjects, scheduleData] = await Promise.all([
        api.request(`/children/${childId}/subjects`),
        api.request(`/children/${childId}/activity-schedules`)
      ]);
      const scheduleMap = Object.fromEntries(scheduleData.items.map((item) => [item.subject_id, item]));
      const activeLearning = subjects.filter((item) => item.kind === "learning" && item.active);
      const activeActivities = subjects.filter((item) => item.kind === "activity" && item.active);
      const byLearningName = Object.fromEntries(subjects.filter((item) => item.kind === "learning").map((item) => [item.name, item]));
      const baseLearning = BASIC_LEARNING.map((name) => ({ name, subject: byLearningName[name] || null, selected: Boolean(byLearningName[name] && byLearningName[name].active) }));
      const addedLearning = activeLearning.filter((item) => !BASIC_LEARNING.includes(item.name));
      const addedActivities = activeActivities.map((item) => {
        const schedule = scheduleMap[item.id] || null;
        return { ...item, short: item.name.charAt(0), schedule, scheduleLabel: schedule ? (schedule.weekdays.length ? "已设置固定时间" : "时间不固定") : "尚未设置时间" };
      });
      this.setData({ loading: false, children, childIndex, childId, subjects, baseLearning, addedLearning, addedActivities });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  async toggleBaseLearning(event) {
    const option = this.data.baseLearning[Number(event.currentTarget.dataset.index)];
    try {
      if (option.subject) await api.request(`/subjects/${option.subject.id}`, { method: "PATCH", data: { active: !option.selected } });
      else await api.request("/subjects", { method: "POST", data: { child_id: this.data.childId, name: option.name, kind: "learning" } });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  removeLearning(event) {
    const subject = this.data.addedLearning.find((item) => item.id === event.currentTarget.dataset.id);
    if (!subject) return;
    wx.showModal({ title: "移出在学科目？", content: `“${subject.name}”的历史学习记录会保留。`, confirmText: "移出", confirmColor: "#A94F48", success: async (result) => {
      if (!result.confirm) return;
      try { await api.request(`/subjects/${subject.id}`, { method: "PATCH", data: { active: false } }); await this.load(); }
      catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
    } });
  },
  openCatalog(event) {
    const type = event.currentTarget.dataset.type;
    const names = type === "activity" ? ACTIVITY_CATALOG : LEARNING_CATALOG;
    const activeNames = new Set(this.data.subjects.filter((item) => item.kind === type && item.active).map((item) => item.name));
    this.setData({
      showCatalog: true, catalogType: type,
      catalogTitle: type === "activity" ? "添加课外活动" : "添加其他科目",
      catalogMode: "catalog", catalogQuery: "",
      catalogOptions: names.map((name) => ({ name, added: activeNames.has(name) })),
      allCatalogOptions: names.map((name) => ({ name, added: activeNames.has(name) })),
      selectedCatalogName: "", customCatalogName: ""
    });
  },
  closeCatalog() { if (!this.data.addingCatalog) this.setData({ showCatalog: false }); },
  changeCatalogMode(event) {
    if (this.data.addingCatalog) return;
    this.setData({ catalogMode: event.currentTarget.dataset.mode, selectedCatalogName: "" });
  },
  filterCatalog(event) {
    const catalogQuery = event.detail.value.trim();
    this.setData({ catalogQuery, catalogOptions: this.data.allCatalogOptions.filter((item) => !catalogQuery || item.name.includes(catalogQuery)) });
  },
  chooseCatalog(event) {
    const option = this.data.catalogOptions[Number(event.currentTarget.dataset.index)];
    if (!option.added) this.setData({ selectedCatalogName: option.name, customCatalogName: "" });
  },
  setField(event) {
    const field = event.currentTarget.dataset.field;
    this.setData({ [field]: event.detail.value });
    if (field === "startTime" || field === "endTime") this.updateScheduleSummary();
  },
  async addCatalog() {
    const name = (this.data.customCatalogName.trim() || this.data.selectedCatalogName).trim();
    if (!name) return wx.showToast({ title: "请选择或输入名称", icon: "none" });
    const sameName = this.data.subjects.find((item) => item.name === name);
    if (sameName && sameName.kind !== this.data.catalogType) return wx.showToast({ title: "这个名称已用于其他类型", icon: "none" });
    this.setData({ addingCatalog: true });
    try {
      if (sameName) await api.request(`/subjects/${sameName.id}`, { method: "PATCH", data: { active: true } });
      else {
        const data = { child_id: this.data.childId, name, kind: this.data.catalogType };
        if (this.data.catalogType === "activity") data.color = "#D68C51";
        await api.request("/subjects", { method: "POST", data });
      }
      this.setData({ showCatalog: false, addingCatalog: false });
      await this.load();
    } catch (error) { this.setData({ addingCatalog: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  openActivitySchedule(event) {
    const item = this.data.addedActivities[Number(event.currentTarget.dataset.index)];
    const schedule = item.schedule;
    const weekdays = schedule ? schedule.weekdays : [];
    this.setData({
      showSchedule: true, scheduleSubject: item, scheduleId: schedule ? schedule.id : "", weekdays,
      weekdaySelected: Array.from({ length: 7 }, (_, index) => weekdays.includes(index)),
      startTime: schedule && schedule.start_time ? schedule.start_time.slice(0, 5) : "18:00",
      endTime: schedule && schedule.end_time ? schedule.end_time.slice(0, 5) : "19:00",
      flexible: Boolean(schedule && !schedule.weekdays.length),
      scheduleSummary: weekdays.length ? `每周${weekdays.map((day) => this.data.weekdayLabels[day]).join("、")} · ${schedule && schedule.start_time ? schedule.start_time.slice(0, 5) : "18:00"}–${schedule && schedule.end_time ? schedule.end_time.slice(0, 5) : "19:00"}` : "请选择至少一天"
    });
  },
  closeSchedule() { if (!this.data.savingSchedule) this.setData({ showSchedule: false }); },
  chooseScheduleMode(event) { this.setData({ flexible: event.currentTarget.dataset.mode === "flexible" }); },
  updateScheduleSummary() {
    const days = this.data.weekdays.map((day) => this.data.weekdayLabels[day]).join("、");
    this.setData({ scheduleSummary: days ? `每周${days} · ${this.data.startTime}–${this.data.endTime}` : "请选择至少一天" });
  },
  toggleWeekday(event) {
    const value = Number(event.currentTarget.dataset.value);
    const weekdays = this.data.weekdays.slice();
    const index = weekdays.indexOf(value);
    if (index >= 0) weekdays.splice(index, 1); else weekdays.push(value);
    weekdays.sort();
    this.setData({ weekdays, weekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.includes(day)) });
    this.updateScheduleSummary();
  },
  async saveSchedule() {
    if (!this.data.flexible && !this.data.weekdays.length) return wx.showToast({ title: "请选择活动日", icon: "none" });
    if (!this.data.flexible && this.data.endTime <= this.data.startTime) return wx.showToast({ title: "结束时间需晚于开始时间", icon: "none" });
    this.setData({ savingSchedule: true });
    const payload = { child_id: this.data.childId, subject_id: this.data.scheduleSubject.id, weekdays: this.data.flexible ? [] : this.data.weekdays, start_time: this.data.flexible ? null : this.data.startTime, end_time: this.data.flexible ? null : this.data.endTime, target_per_week: null };
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "PATCH", data: payload });
      else await api.request("/activity-schedules", { method: "POST", data: payload });
      this.setData({ showSchedule: false, savingSchedule: false });
      await this.load();
    } catch (error) { this.setData({ savingSchedule: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async removeActivity() {
    const confirmed = await new Promise((resolve) => wx.showModal({ title: "移除课外活动", content: `移除“${this.data.scheduleSubject.name}”及其日程？`, confirmText: "移除", confirmColor: "#A94F48", success: (result) => resolve(result.confirm) }));
    if (!confirmed) return;
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "DELETE" });
      await api.request(`/subjects/${this.data.scheduleSubject.id}`, { method: "PATCH", data: { active: false } });
      this.setData({ showSchedule: false });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  }
});
