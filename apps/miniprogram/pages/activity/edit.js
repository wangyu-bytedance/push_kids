const api = require("../../utils/api");
const ui = require("../../utils/ui");
const { localParts, toIso } = require("../../utils/date");
const childContext = require("../../utils/child-context");

const DURATION_MIN = 5;
const DURATION_MAX = 180;

Page({
  data: {
    loading: true, error: "", saveError: "", canWrite: true,
    childId: "", childName: "", kicker: "课外活动",
    subjects: [], subjectIndex: 0, subjectId: "", subjectName: "", iconClass: ui.activityIcon("", "pri"),
    date: "", time: "", today: "", duration: 45, durationText: "45 分钟",
    durationMin: DURATION_MIN, durationMax: DURATION_MAX,
    note: "", noteCount: 0, saving: false
  },
  onLoad(options) {
    const now = localParts();
    this.setData({ date: now.date, time: now.time, today: now.date, subjectId: options.subjectId || "" });
    this.load();
  },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const profiles = await api.request("/children");
      /* 选中的档案可能已被归档，统一回落到在用的第一个，避免写到读不到的孩子身上。 */
      const selection = childContext.syncSelection(getApp(), profiles);
      const childId = selection.childId;
      if (!childId) throw new Error("请先建立学习档案");
      const child = selection.children[selection.childIndex];
      const member = getApp().globalData.currentMember;
      const all = await api.request(`/children/${childId}/subjects`);
      const subjects = all.filter((item) => item.kind === "activity" && item.active !== false);
      const subjectIndex = Math.max(0, subjects.findIndex((item) => item.id === this.data.subjectId));
      const subjectName = subjects.length ? subjects[subjectIndex].name : "";
      this.setData({
        loading: false, childId,
        childName: child ? child.name : "",
        kicker: child ? `课外活动 · ${child.name}` : "课外活动",
        canWrite: !member || member.role !== "viewer",
        subjects, subjectIndex,
        subjectId: subjects.length ? subjects[subjectIndex].id : "",
        subjectName,
        iconClass: ui.activityIcon(subjectName, "pri")
      });
    } catch (error) {
      this.setData({ loading: false, error: error.message });
    }
  },
  setField(event) {
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const update = { [field]: value, saveError: "" };
    if (field === "duration") update.durationText = `${Number(value) || 0} 分钟`;
    if (field === "note") update.noteCount = String(value).length;
    this.setData(update);
  },
  changeSubject(event) {
    const subjectIndex = Number(event.detail.value);
    const subject = this.data.subjects[subjectIndex];
    this.setData({ subjectIndex, subjectId: subject.id, subjectName: subject.name,
      iconClass: ui.activityIcon(subject.name, "pri"), saveError: "" });
  },
  openSettings() { wx.switchTab({ url: "/pages/settings/index" }); },
  async save() {
    if (!this.data.canWrite) return wx.showToast({ title: "你是只读成员，改动请找管理员", icon: "none" });
    if (!this.data.subjectId) return this.setData({ saveError: "先在设置里添加一项课外活动。" });
    if (this.data.saving) return;
    this.setData({ saving: true, saveError: "" });
    try {
      await api.request("/activity-records", { method: "POST", data: {
        child_id: this.data.childId,
        subject_id: this.data.subjectId,
        occurred_at: toIso(this.data.date, this.data.time),
        duration_minutes: Number(this.data.duration) || null,
        note: this.data.note || null
      } });
      wx.showToast({ title: "已记录", icon: "success" });
      setTimeout(() => wx.navigateBack(), 400);
    } catch (error) {
      /* 失败时表单原样保留，只在吸底按钮上方给出可重试的说明。 */
      this.setData({ saving: false, saveError: `${error.message}，这次练习还没保存，可以再试一次。` });
    }
  }
});
