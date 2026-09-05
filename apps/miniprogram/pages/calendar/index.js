const api = require("../../utils/api");
const ui = require("../../utils/ui");
const { localParts } = require("../../utils/date");

const WEEK_LABELS = ["一", "二", "三", "四", "五", "六", "日"];
const WEEKDAY_FULL = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"];
const KIND_LABELS = { class: "课外活动", activity: "自主活动", other: "其他安排" };
const WEEK_CONCURRENCY = 3;

function dateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function weekFor(day, marks, todayKey) {
  const current = new Date(`${day}T12:00:00`);
  const selectedMonth = current.getMonth();
  const mondayOffset = (current.getDay() + 6) % 7;
  current.setDate(current.getDate() - mondayOffset);
  return Array.from({ length: 7 }, (_, index) => {
    const value = new Date(current);
    value.setDate(current.getDate() + index);
    const key = dateKey(value);
    return {
      key,
      day: value.getDate(),
      weekday: WEEK_LABELS[index],
      marked: !!(marks || {})[key],
      today: key === todayKey,
      dim: value.getMonth() !== selectedMonth
    };
  });
}

/* 卡面文案在 JS 里拼好，WXML 不做任何方法调用。 */
function decorateItem(item) {
  return {
    ...item,
    kind_label: KIND_LABELS[item.kind] || "其他安排",
    time_text: `${item.start_time}–${item.end_time}${item.repeat_weekly ? " · 每周重复" : " · 不重复"}`,
    action_text: item.past ? "补记这次练习" : "记录这次练习"
  };
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", multiChild: false,
    selectedDay: "", monthLabel: "", weekKicker: "", dayTitle: "", itemCount: 0, weekEmpty: false,
    week: [], items: [], showChildSheet: false,
    showEditor: false, editingId: "", eventName: "", eventKind: "class", eventDate: "",
    startTime: "18:00", endTime: "19:00", repeatWeekly: true, saving: false, eventKey: "", endError: ""
  },
  onLoad() { this.cache = {}; this.marks = {}; this.cacheChildId = ""; },
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 1 });
    const app = getApp();
    const shouldOpenCreate = app.globalData.openCalendarCreate;
    app.globalData.openCalendarCreate = false;
    this.load().then(() => { if (shouldOpenCreate && this.data.children.length) this.openCreate(); });
  },
  async load(options = {}) {
    const silent = options.silent === true;
    const generation = (this.loadGeneration || 0) + 1;
    this.loadGeneration = generation;
    this.cache = this.cache || {};
    this.marks = this.marks || {};
    const selectedDay = this.data.selectedDay || localParts().date;
    const todayKey = localParts().date;
    const [year, month] = selectedDay.split("-");
    const week = weekFor(selectedDay, this.marks, todayKey);
    const inThisWeek = week.some((item) => item.key === todayKey);
    const range = `${ui.monthDay(week[0].key)} – ${ui.monthDay(week[6].key)}`;
    this.setData({
      loading: !silent, error: "", selectedDay, week,
      monthLabel: `${year} 年 ${Number(month)} 月`,
      weekKicker: inThisWeek ? `本周 · ${range}` : range,
      dayTitle: `${ui.monthDay(selectedDay)} · ${WEEKDAY_FULL[new Date(`${selectedDay}T12:00:00`).getDay()]}`
    });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽",
        label: item.grade ? `${item.name} · ${item.grade}` : item.name
      }));
      if (generation !== this.loadGeneration) return;
      if (!children.length) return this.setData({ loading: false, children, items: [], itemCount: 0, multiChild: false });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      if (this.cacheChildId !== childId) { this.cache = {}; this.marks = {}; this.cacheChildId = childId; }
      const schedule = await api.request(`/children/${childId}/schedule?day=${selectedDay}`);
      if (generation !== this.loadGeneration) return;
      const items = (schedule.items || []).map(decorateItem);
      this.cache[selectedDay] = items;
      this.marks[selectedDay] = items.length > 0;
      this.setData({ loading: false, children, childIndex, childId, items, itemCount: items.length,
        multiChild: children.length > 1, week: weekFor(selectedDay, this.marks, todayKey) });
      this.fillWeek(childId, selectedDay, generation);
    } catch (error) {
      if (generation !== this.loadGeneration) return;
      /* 出错时保留已经渲染的当天安排，只在上方给一条可重试的说明。 */
      this.setData({ loading: false, error: error.message });
    }
  },
  /* 周内其余日期只用来点圆点和判断「整周为空」，并发上限 3，失败静默。 */
  async fillWeek(childId, selectedDay, generation) {
    const pending = this.data.week.map((item) => item.key).filter((key) => this.cache[key] === undefined);
    try {
      while (pending.length) {
        const batch = pending.splice(0, WEEK_CONCURRENCY);
        const results = await Promise.all(batch.map((key) => api.request(`/children/${childId}/schedule?day=${key}`)));
        if (generation !== this.loadGeneration || this.cacheChildId !== childId) return;
        batch.forEach((key, index) => {
          const items = ((results[index] || {}).items || []).map(decorateItem);
          this.cache[key] = items;
          this.marks[key] = items.length > 0;
        });
        this.publishWeek(selectedDay);
      }
      this.publishWeek(selectedDay);
    } catch {
      this.publishWeek(selectedDay);
    }
  },
  publishWeek(selectedDay) {
    const keys = this.data.week.map((item) => item.key);
    const known = keys.filter((key) => this.cache[key] !== undefined);
    const empty = known.length === keys.length && known.every((key) => !this.cache[key].length);
    this.setData({ week: weekFor(selectedDay, this.marks, localParts().date), weekEmpty: empty });
  },
  openChildSheet() { if (this.data.multiChild) this.setData({ showChildSheet: true }); },
  closeChildSheet() { this.setData({ showChildSheet: false }); },
  chooseChild(event) {
    const index = Number(event.currentTarget.dataset.index);
    getApp().selectChild(this.data.children[index].id);
    this.setData({ childIndex: index, showChildSheet: false, weekEmpty: false });
    this.load();
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  chooseDay(event) {
    const day = event.currentTarget.dataset.day;
    if (!day || day === this.data.selectedDay) return;
    const cached = this.cache ? this.cache[day] : undefined;
    if (cached) {
      /* 本周已缓存的日期直接切换，再静默刷新，避免整页重刷。 */
      this.setData({ selectedDay: day, items: cached, itemCount: cached.length });
      this.load({ silent: true });
      return;
    }
    this.setData({ selectedDay: day, items: [], itemCount: 0 });
    this.load();
  },
  chooseDate(event) { this.setData({ selectedDay: event.detail.value, weekEmpty: false }); this.load(); },
  shiftWeek(event) { this.shiftWeekBy(Number(event.currentTarget.dataset.offset)); },
  /* 切周只平移 7 天，选中的星期保持不变。 */
  shiftWeekBy(offset) {
    const value = new Date(`${this.data.selectedDay}T12:00:00`);
    value.setDate(value.getDate() + offset);
    this.setData({ selectedDay: dateKey(value), weekEmpty: false });
    this.load();
  },
  weekTouchStart(event) {
    const touch = event.touches[0];
    this.swipe = touch ? { x: touch.clientX, y: touch.clientY } : null;
  },
  weekTouchEnd(event) {
    const touch = event.changedTouches[0];
    if (!this.swipe || !touch) return;
    const deltaX = touch.clientX - this.swipe.x;
    const deltaY = touch.clientY - this.swipe.y;
    this.swipe = null;
    if (Math.abs(deltaX) < 60 || Math.abs(deltaX) <= Math.abs(deltaY)) return;
    this.shiftWeekBy(deltaX < 0 ? 7 : -7);
  },
  openCreate() {
    this.setData({ showEditor: true, editingId: "", eventName: "", eventKind: "class", eventDate: this.data.selectedDay,
      startTime: "18:00", endTime: "19:00", repeatWeekly: true, endError: "", eventKey: api.newIdempotencyKey("calendar") });
  },
  openEvent(event) {
    const item = this.data.items.find((row) => row.id === event.currentTarget.dataset.id);
    if (!item) return;
    if (item.source === "activity_schedule") {
      wx.switchTab({ url: "/pages/settings/index" });
      return;
    }
    this.setData({ showEditor: true, editingId: item.id, eventName: item.name, eventKind: item.kind, eventDate: item.day || this.data.selectedDay,
      startTime: item.start_time, endTime: item.end_time, repeatWeekly: item.repeat_weekly, endError: "", eventKey: "" });
  },
  closeEditor() { if (!this.data.saving) this.setData({ showEditor: false }); },
  setField(event) {
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const updates = { [field]: value };
    if (field === "startTime" || field === "endTime") {
      const start = field === "startTime" ? value : this.data.startTime;
      const end = field === "endTime" ? value : this.data.endTime;
      updates.endError = end <= start ? "结束时间要晚于开始时间" : "";
    }
    this.setData(updates);
  },
  chooseKind(event) { this.setData({ eventKind: event.currentTarget.dataset.kind }); },
  toggleRepeat(event) { this.setData({ repeatWeekly: event.detail.value }); },
  openSettings() { wx.switchTab({ url: "/pages/settings/index" }); },
  openActivity(event) { wx.navigateTo({ url: `/pages/activity/edit?subjectId=${event.currentTarget.dataset.subjectId}` }); },
  async saveEvent() {
    if (this.data.saving) return;
    if (!this.data.eventName.trim()) return wx.showToast({ title: "请填写日程名称", icon: "none" });
    if (this.data.endTime <= this.data.startTime) {
      this.setData({ endError: "结束时间要晚于开始时间" });
      return wx.showToast({ title: "结束时间需晚于开始时间", icon: "none" });
    }
    this.setData({ saving: true });
    const payload = { name: this.data.eventName.trim(), event_date: this.data.eventDate || this.data.selectedDay, start_time: this.data.startTime, end_time: this.data.endTime, kind: this.data.eventKind, repeat_weekly: this.data.repeatWeekly };
    try {
      if (this.data.editingId) await api.request(`/calendar-events/${this.data.editingId}`, { method: "PATCH", data: payload });
      else await api.request("/calendar-events", { method: "POST", idempotencyKey: this.data.eventKey, data: { ...payload, child_id: this.data.childId } });
      this.setData({ showEditor: false, saving: false, selectedDay: payload.event_date });
      this.cache = {};
      this.marks = {};
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async deleteEvent() {
    const confirmed = await new Promise((resolve) => wx.showModal({
      title: "删除这条日程？",
      content: "删除后它不会再出现在日程和今日；每周重复的安排会删除整个系列，已经记录的练习不受影响。",
      confirmText: "删除",
      confirmColor: "#A6423B",
      success: (result) => resolve(result.confirm)
    }));
    if (!confirmed) return;
    try {
      await api.request(`/calendar-events/${this.data.editingId}`, { method: "DELETE" });
      this.setData({ showEditor: false });
      this.cache = {};
      this.marks = {};
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  }
});
