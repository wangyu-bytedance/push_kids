const api = require("../../utils/api");
const { friendlyTime } = require("../../utils/date");
const detail = require("./detail");

Page({
  data: { ...detail.data, id: "", loading: true, saving: false, error: "", saveError: "", manual: false, submission: null, proposal: null, subjects: [], subjectIndex: -1 },
  ...detail.methods,
  onLoad(options) { this.setData({ id: options.id, manual: options.manual === "1" }); this.load(); },
  onHide() { this.hidden = true; this.loadRequest = (this.loadRequest || 0) + 1; if (this.detailTimer) clearTimeout(this.detailTimer); },
  onUnload() { this.onHide(); },
  onShow() { const refresh = this.hidden && this.data.readOnly; this.hidden = false; if (refresh) this.load(); },
  async load() {
    const generation = (this.loadRequest || 0) + 1;
    this.loadRequest = generation;
    this.setData({ error: "", conflict: false });
    try {
      const submission = await api.request(`/submissions/${this.data.id}`);
      if (generation !== this.loadRequest) return;
      const allowed = this.data.manual ? ["queued", "analyzing", "failed", "pending_confirmation"] : ["pending_confirmation"];
      const member = typeof getApp === "function" && getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      const readOnly = !allowed.includes(submission.state) || !canWrite;
      this.setData({ submission: { ...submission, time_label: friendlyTime(submission.occurred_at), submitted_label: friendlyTime(submission.created_at || submission.occurred_at) }, readOnly, canWrite,
        statusLabel: { queued: submission.awaiting_upload ? "等待上传照片" : "等待分析", analyzing: "正在分析", failed: "分析失败", pending_confirmation: "待确认", confirmed: "已确认", cancelled: "已取消" }[submission.state] || "请刷新状态" });
      if (wx.setNavigationBarTitle) wx.setNavigationBarTitle({ title: readOnly ? "学习记录" : "确认学习内容" });
      if (readOnly) {
        this.setData({ proposal: null, subjects: [], reviews: [], reviewsOpen: false, hasDue: false });
        if (this.loadDetail) await this.loadDetail();
        if (generation === this.loadRequest) {
          this.setData({ loading: false });
          if (this.detailTimer) clearTimeout(this.detailTimer);
          if (!this.hidden && !submission.awaiting_upload && ["queued", "analyzing"].includes(submission.state)) this.detailTimer = setTimeout(() => this.load(), 3500);
        }
        return;
      }
      const subjects = (await api.request(`/children/${submission.child_id}/subjects`)).filter((item) => item.kind === "learning" && item.active !== false);
      const initial = this.data.manual ? {
        summary: (submission.input_text || "").length <= 500 ? (submission.input_text || "") : "",
        subject_name: "", subject_kind: "learning", source: "人工录入", uncertainties: [], todo_matches: [],
        knowledge_points: [{ name: "", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 }]
      } : submission.proposal;
      const subjectIndex = subjects.findIndex((item) => item.name === initial.subject_name);
      const proposal = { ...initial, knowledge_points: initial.knowledge_points.map((point) => ({
        ...point,
        confidence_label: { high: "较明确", medium: "请核对", low: "不确定，请重点核对" }[point.confidence] || "请核对",
        evidence_labels: (point.direct_evidence || []).map((evidence) => `${evidence.source === "image" ? "照片 " + evidence.image_index : "家长文字"}：${evidence.detail}`)
      })) };
      if (generation === this.loadRequest) this.setData({ loading: false, proposal, subjects, subjectIndex });
    } catch (error) {
      if (generation === this.loadRequest) this.setData({ loading: false, error: error.message, detail: null, submission: null, reviews: [] });
    }
  },
  setProposal(event) {
    const field = event.currentTarget.dataset.field;
    this.setData({ [`proposal.${field}`]: event.detail.value });
    if (field === "subject_name") { this.setData({ subjectIndex: -1 }); this.clearAssociations(); }
  },
  clearAssociations() { this.setData({ "proposal.knowledge_points": this.data.proposal.knowledge_points.map((point) => ({ ...point, existing_knowledge_id: null })), "proposal.todo_matches": [] }); },
  unlinkPoint(event) { this.setData({ [`proposal.knowledge_points[${Number(event.currentTarget.dataset.index)}].existing_knowledge_id`]: null }); },
  setPoint(event) {
    const { index, field } = event.currentTarget.dataset;
    this.setData({ [`proposal.knowledge_points[${index}].${field}`]: field === "estimated_minutes" ? Number(event.detail.value) : event.detail.value });
    if (field === "name" || field === "category") this.setData({ [`proposal.knowledge_points[${index}].existing_knowledge_id`]: null });
  },
  changeSubject(event) { const subjectIndex = Number(event.detail.value); this.setData({ subjectIndex, "proposal.subject_name": this.data.subjects[subjectIndex].name, "proposal.subject_kind": "learning" }); this.clearAssociations(); },
  addPoint() { const points = this.data.proposal.knowledge_points.concat([{ name: "", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 }]); this.setData({ "proposal.knowledge_points": points }); },
  removePoint(event) { const points = this.data.proposal.knowledge_points.slice(); points.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ "proposal.knowledge_points": points }); },
  removeTodoMatch(event) { const matches = this.data.proposal.todo_matches.slice(); matches.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ "proposal.todo_matches": matches }); },
  async confirm() {
    if (this.data.saving || this.data.readOnly) return;
    const proposal = this.data.proposal;
    if (!proposal.summary.trim() || !proposal.subject_name.trim()) return wx.showToast({ title: "请补全总结和科目", icon: "none" });
    proposal.knowledge_points = proposal.knowledge_points.filter((item) => item.name.trim());
    if (!proposal.knowledge_points.length) return wx.showToast({ title: "至少保留一个知识点", icon: "none" });
    this.setData({ saving: true, saveError: "" });
    try {
      await api.request(`/submissions/${this.data.id}/confirm`, { method: "POST", data: { manual_entry: this.data.manual, subject_id: this.data.subjectIndex >= 0 ? this.data.subjects[this.data.subjectIndex].id : null, proposal } });
      wx.showToast({ title: "已确认入库", icon: "success" });
      setTimeout(() => wx.navigateBack(), 500);
    } catch (error) { this.setData({ saving: false, saveError: error.message, conflict: error.statusCode === 409 }); wx.showToast({ title: error.message, icon: "none" }); }
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
