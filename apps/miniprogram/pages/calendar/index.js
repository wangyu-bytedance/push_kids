const api = require("../../utils/api");
const { localParts } = require("../../utils/date");

function dateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function weekFor(day) {
  const current = new Date(`${day}T12:00:00`);
  const mondayOffset = (current.getDay() + 6) % 7;
  current.setDate(current.getDate() - mondayOffset);
  return Array.from({ length: 7 }, (_, index) => {
    const value = new Date(current);
    value.setDate(current.getDate() + index);
    return { key: dateKey(value), day: value.getDate(), weekday: "一二三四五六日"[index] };
  });
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", selectedDay: "",
    week: [], items: [], showEditor: false, editingId: "", eventName: "", eventKind: "class",
    startTime: "18:00", endTime: "19:00", repeatWeekly: true, saving: false, eventKey: ""
  },
  onShow() { this.load(); },
  async load() {
    const selectedDay = this.data.selectedDay || localParts().date;
    this.setData({ loading: true, error: "", selectedDay, week: weekFor(selectedDay) });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (!children.length) return this.setData({ loading: false, children, items: [] });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const schedule = await api.request(`/children/${childId}/schedule?day=${selectedDay}`);
      this.setData({ loading: false, children, childIndex, childId, items: schedule.items });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  chooseDay(event) { this.setData({ selectedDay: event.currentTarget.dataset.day }); this.load(); },
  openCreate() {
    this.setData({ showEditor: true, editingId: "", eventName: "", eventKind: "class", startTime: "18:00", endTime: "19:00", repeatWeekly: true, eventKey: api.newIdempotencyKey("calendar") });
  },
  openEvent(event) {
    const item = this.data.items.find((row) => row.id === event.currentTarget.dataset.id);
    if (!item) return;
    if (item.source === "activity_schedule") {
      wx.switchTab({ url: "/pages/settings/index" });
      return;
    }
    this.setData({ showEditor: true, editingId: item.id, eventName: item.name, eventKind: item.kind, startTime: item.start_time, endTime: item.end_time, repeatWeekly: item.repeat_weekly, eventKey: "" });
  },
  closeEditor() { if (!this.data.saving) this.setData({ showEditor: false }); },
  setField(event) { this.setData({ [event.currentTarget.dataset.field]: event.detail.value }); },
  chooseKind(event) { this.setData({ eventKind: event.currentTarget.dataset.kind }); },
  toggleRepeat(event) { this.setData({ repeatWeekly: event.detail.value }); },
  async saveEvent() {
    if (this.data.saving) return;
    if (!this.data.eventName.trim()) return wx.showToast({ title: "请填写日程名称", icon: "none" });
    if (this.data.endTime <= this.data.startTime) return wx.showToast({ title: "结束时间需晚于开始时间", icon: "none" });
    this.setData({ saving: true });
    const payload = { name: this.data.eventName.trim(), event_date: this.data.selectedDay, start_time: this.data.startTime, end_time: this.data.endTime, kind: this.data.eventKind, repeat_weekly: this.data.repeatWeekly };
    try {
      if (this.data.editingId) await api.request(`/calendar-events/${this.data.editingId}`, { method: "PATCH", data: payload });
      else await api.request("/calendar-events", { method: "POST", idempotencyKey: this.data.eventKey, data: { ...payload, child_id: this.data.childId } });
      this.setData({ showEditor: false, saving: false });
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async deleteEvent() {
    const confirmed = await new Promise((resolve) => wx.showModal({ title: "删除日程", content: "每周重复日程会删除整个系列。", success: (result) => resolve(result.confirm) }));
    if (!confirmed) return;
    try { await api.request(`/calendar-events/${this.data.editingId}`, { method: "DELETE" }); this.setData({ showEditor: false }); await this.load(); }
    catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  }
});
