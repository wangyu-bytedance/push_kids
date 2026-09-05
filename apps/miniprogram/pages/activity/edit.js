const api = require("../../utils/api");
const { localParts, toIso } = require("../../utils/date");

Page({
  data: { childId: "", subjects: [], subjectIndex: 0, subjectId: "", date: "", time: "", duration: 45, note: "", saving: false },
  onLoad(options) { const now = localParts(); this.setData({ date: now.date, time: now.time, subjectId: options.subjectId || "" }); this.load(); },
  async load() {
    try {
      const children = await api.request("/children");
      const childId = getApp().globalData.selectedChildId || (children[0] && children[0].id);
      if (!childId) throw new Error("请先建立学习档案");
      const all = await api.request(`/children/${childId}/subjects`);
      const subjects = all.filter((item) => item.kind === "activity");
      let subjectIndex = Math.max(0, subjects.findIndex((item) => item.id === this.data.subjectId));
      this.setData({ childId, subjects, subjectIndex, subjectId: subjects.length ? subjects[subjectIndex].id : "" });
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  setField(event) { this.setData({ [event.currentTarget.dataset.field]: event.detail.value }); },
  changeSubject(event) { const subjectIndex = Number(event.detail.value); this.setData({ subjectIndex, subjectId: this.data.subjects[subjectIndex].id }); },
  async save() {
    if (!this.data.subjectId) return wx.showToast({ title: "请先在设置添加活动科目", icon: "none" });
    this.setData({ saving: true });
    try {
      await api.request("/activity-records", { method: "POST", data: { child_id: this.data.childId, subject_id: this.data.subjectId, occurred_at: toIso(this.data.date, this.data.time), duration_minutes: Number(this.data.duration) || null, note: this.data.note || null } });
      wx.showToast({ title: "已记录", icon: "success" }); setTimeout(() => wx.navigateBack(), 400);
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none" }); }
  }
});
