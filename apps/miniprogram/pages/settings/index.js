const api = require("../../utils/api");

const LEARNING = ["语文", "数学", "英语", "科学", "道德与法治", "物理", "化学", "生物", "历史", "地理", "政治", "美术", "音乐", "体育", "劳动"];
const ACTIVITIES = ["游泳", "乒乓球", "篮球", "羽毛球", "足球", "网球", "围棋", "国际象棋", "钢琴", "小提琴", "舞蹈", "武术", "跆拳道", "书法", "绘画", "编程", "机器人"];

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", subjects: [],
    learningOptions: [], activityOptions: [], budgetOptions: [10, 15, 20, 30],
    customName: "", showCustom: false, showSchedule: false, scheduleSubject: null,
    weekdayLabels: ["一", "二", "三", "四", "五", "六", "日"],
    scheduleId: "", weekdays: [], weekdaySelected: [false, false, false, false, false, false, false], startTime: "18:00", endTime: "19:00", flexible: false,
    savingSchedule: false, scheduleNeedsRollback: false
  },
  onShow() { this.load(); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (!children.length) return this.setData({ loading: false, children, subjects: [] });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const [subjects, scheduleData] = await Promise.all([api.request(`/children/${childId}/subjects`), api.request(`/children/${childId}/activity-schedules`)]);
      const scheduleMap = Object.fromEntries(scheduleData.items.map((item) => [item.subject_id, item]));
      const byName = Object.fromEntries(subjects.map((item) => [item.name, item]));
      const learningOptions = LEARNING.map((name) => ({ name, short: name.length > 2 ? name.slice(0, 1) : name, subject: byName[name] || null, selected: Boolean(byName[name] && byName[name].active) }));
      const activityOptions = ACTIVITIES.map((name) => {
        const subject = byName[name] || null;
        const schedule = subject ? scheduleMap[subject.id] || null : null;
        return {
          name,
          short: name.slice(0, 1),
          subject,
          selected: Boolean(subject && subject.active),
          schedule,
          scheduleLabel: schedule ? (schedule.weekdays.length ? "已安排" : "时间不固定") : "点击设置"
        };
      });
      this.setData({ loading: false, children, childIndex, childId, subjects, learningOptions, activityOptions });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  async chooseBudget(event) {
    const value = Number(event.currentTarget.dataset.value);
    const child = this.data.children[this.data.childIndex];
    if (child.daily_budget_minutes === value) return;
    const previous = child.daily_budget_minutes;
    this.setData({ [`children[${this.data.childIndex}].daily_budget_minutes`]: value });
    try { await api.request(`/children/${child.id}`, { method: "PATCH", data: { daily_budget_minutes: value } }); }
    catch (error) { this.setData({ [`children[${this.data.childIndex}].daily_budget_minutes`]: previous }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async toggleLearning(event) {
    const option = this.data.learningOptions[Number(event.currentTarget.dataset.index)];
    try {
      if (option.subject) await api.request(`/subjects/${option.subject.id}`, { method: "PATCH", data: { active: !option.selected } });
      else await api.request("/subjects", { method: "POST", data: { child_id: this.data.childId, name: option.name, kind: "learning" } });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async chooseActivity(event) {
    const option = this.data.activityOptions[Number(event.currentTarget.dataset.index)];
    try {
      let subject = option.subject;
      if (!subject) subject = await api.request("/subjects", { method: "POST", data: { child_id: this.data.childId, name: option.name, kind: "activity", color: "#D68C51" } });
      else if (!option.selected) await api.request(`/subjects/${subject.id}`, { method: "PATCH", data: { active: true } });
      const schedule = option.schedule;
      const weekdays = schedule ? schedule.weekdays : [];
      this.setData({ showSchedule: true, scheduleSubject: subject, scheduleId: schedule ? schedule.id : "", scheduleNeedsRollback: !option.selected, weekdays, weekdaySelected: Array.from({ length: 7 }, (_, index) => weekdays.indexOf(index) >= 0), startTime: schedule && schedule.start_time ? schedule.start_time.slice(0, 5) : "18:00", endTime: schedule && schedule.end_time ? schedule.end_time.slice(0, 5) : "19:00", flexible: Boolean(schedule && !schedule.weekdays.length) });
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  toggleCustom() { this.setData({ showCustom: !this.data.showCustom }); },
  setField(event) { this.setData({ [event.currentTarget.dataset.field]: event.detail.value }); },
  async addCustom() {
    if (!this.data.customName.trim()) return;
    try { await api.request("/subjects", { method: "POST", data: { child_id: this.data.childId, name: this.data.customName.trim(), kind: "learning" } }); this.setData({ customName: "", showCustom: false }); await this.load(); }
    catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async closeSchedule() {
    if (this.data.savingSchedule) return;
    this.setData({ showSchedule: false });
    if (this.data.scheduleNeedsRollback && this.data.scheduleSubject) {
      try { await api.request(`/subjects/${this.data.scheduleSubject.id}`, { method: "PATCH", data: { active: false } }); await this.load(); }
      catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
    }
  },
  toggleFlexible(event) { this.setData({ flexible: event.detail.value }); },
  toggleWeekday(event) { const value = Number(event.currentTarget.dataset.value); const weekdays = this.data.weekdays.slice(); const index = weekdays.indexOf(value); if (index >= 0) weekdays.splice(index, 1); else weekdays.push(value); weekdays.sort(); this.setData({ weekdays, weekdaySelected: Array.from({ length: 7 }, (_, day) => weekdays.indexOf(day) >= 0) }); },
  async saveSchedule() {
    if (!this.data.flexible && !this.data.weekdays.length) return wx.showToast({ title: "请选择练习日", icon: "none" });
    if (!this.data.flexible && this.data.endTime <= this.data.startTime) return wx.showToast({ title: "结束时间需晚于开始时间", icon: "none" });
    this.setData({ savingSchedule: true });
    const payload = { child_id: this.data.childId, subject_id: this.data.scheduleSubject.id, weekdays: this.data.flexible ? [] : this.data.weekdays, start_time: this.data.flexible ? null : this.data.startTime, end_time: this.data.flexible ? null : this.data.endTime, target_per_week: null };
    try {
      if (this.data.scheduleId) await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "PATCH", data: payload });
      else await api.request("/activity-schedules", { method: "POST", data: payload });
      this.setData({ showSchedule: false, savingSchedule: false, scheduleNeedsRollback: false }); await this.load();
    } catch (error) { this.setData({ savingSchedule: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async removeActivity() {
    if (!this.data.scheduleId) return this.closeSchedule();
    try {
      await api.request(`/activity-schedules/${this.data.scheduleId}`, { method: "DELETE" });
      this.setData({ showSchedule: false, scheduleNeedsRollback: false });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  }
});
