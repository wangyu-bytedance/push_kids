const api = require("../../utils/api");
const { friendlyTime } = require("../../utils/date");

Page({
  data: { id: "", loading: true, saving: false, error: "", submission: null, proposal: null, subjects: [], subjectIndex: -1 },
  onLoad(options) { this.setData({ id: options.id }); this.load(); },
  async load() {
    try {
      const submission = await api.request(`/submissions/${this.data.id}`);
      if (submission.state !== "pending_confirmation") throw new Error("这条记录当前不在待确认状态");
      const subjects = await api.request(`/children/${submission.child_id}/subjects`);
      const subjectIndex = subjects.findIndex((item) => item.name === submission.proposal.subject_name);
      this.setData({ loading: false, submission: { ...submission, time_label: friendlyTime(submission.occurred_at) }, proposal: submission.proposal, subjects, subjectIndex });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  setProposal(event) { this.setData({ [`proposal.${event.currentTarget.dataset.field}`]: event.detail.value }); },
  setPoint(event) { const { index, field } = event.currentTarget.dataset; this.setData({ [`proposal.knowledge_points[${index}].${field}`]: field === "estimated_minutes" ? Number(event.detail.value) : event.detail.value }); },
  changeSubject(event) { const subjectIndex = Number(event.detail.value); this.setData({ subjectIndex, "proposal.subject_name": this.data.subjects[subjectIndex].name }); },
  addPoint() { const points = this.data.proposal.knowledge_points.concat([{ name: "", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 }]); this.setData({ "proposal.knowledge_points": points }); },
  removePoint(event) { const points = this.data.proposal.knowledge_points.slice(); points.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ "proposal.knowledge_points": points }); },
  removeTodoMatch(event) { const matches = this.data.proposal.todo_matches.slice(); matches.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ "proposal.todo_matches": matches }); },
  async confirm() {
    const proposal = this.data.proposal;
    if (!proposal.summary.trim() || !proposal.subject_name.trim()) return wx.showToast({ title: "请补全总结和科目", icon: "none" });
    proposal.knowledge_points = proposal.knowledge_points.filter((item) => item.name.trim());
    if (!proposal.knowledge_points.length) return wx.showToast({ title: "至少保留一个知识点", icon: "none" });
    this.setData({ saving: true });
    try {
      await api.request(`/submissions/${this.data.id}/confirm`, { method: "POST", data: { subject_id: this.data.subjectIndex >= 0 ? this.data.subjects[this.data.subjectIndex].id : null, proposal } });
      wx.showToast({ title: "已确认入库", icon: "success" });
      setTimeout(() => wx.navigateBack(), 500);
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  async cancelDraft() {
    const confirmed = await new Promise((resolve) => wx.showModal({
      title: "删除草稿",
      content: "这不会创建学习记录或复习任务。",
      success: (result) => resolve(result.confirm)
    }));
    if (!confirmed) return;
    try {
      await api.request(`/submissions/${this.data.id}/cancel`, { method: "POST" });
      wx.navigateBack();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  }
});
