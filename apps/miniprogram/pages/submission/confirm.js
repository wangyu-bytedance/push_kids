const api = require("../../utils/api");
const { friendlyTime } = require("../../utils/date");
const detail = require("./detail");
const draft = require("./draft");

const STATUS_TONE = { failed: "dan", pending_confirmation: "att", confirmed: "suc", cancelled: "neutral" };

/* 深链入口：人工录入、以及旧版「查看并确认」链接仍可用。
   编辑与确认的逻辑全部来自 draft.js，和待确认页上的就地编辑完全一致。 */
Page({
  data: { ...detail.data, ...draft.data, id: "", loading: true, error: "", submission: null },
  ...detail.methods,
  ...draft.methods,
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
        statusLabel: { queued: submission.awaiting_upload ? "等待上传照片" : "等待分析", analyzing: "正在分析", failed: "分析失败", pending_confirmation: "待家长确认", confirmed: "已确认", cancelled: "已取消" }[submission.state] || "请刷新状态",
        statusTone: STATUS_TONE[submission.state] || "neutral",
        titleText: submission.source === "photo" || submission.media_count ? `${submission.media_count || 0} 张照片` : "文字记录" });
      if (wx.setNavigationBarTitle) wx.setNavigationBarTitle({ title: readOnly ? "学习记录" : "确认学习内容" });
      if (readOnly) {
        this.setData({ editing: false, proposal: null, subjects: [], groups: [], reviews: [], reviewsOpen: false, hasDue: false });
        if (this.loadDetail) await this.loadDetail();
        if (generation === this.loadRequest) {
          const view = this.data.detailView;
          this.setData({ loading: false, titleText: view && view.hasRecord && view.subjectName ? view.subjectName : this.data.titleText });
          if (this.detailTimer) clearTimeout(this.detailTimer);
          if (!this.hidden && !submission.awaiting_upload && ["queued", "analyzing"].includes(submission.state)) this.detailTimer = setTimeout(() => this.load(), 3500);
        }
        return;
      }
      await this.prepareDraft(this.data.submission, this.data.manual);
      if (generation === this.loadRequest) this.setData({ loading: false });
    } catch (error) {
      if (generation === this.loadRequest) this.setData({ loading: false, error: error.message, detail: null, submission: null, reviews: [] });
    }
  },
  /* 确认或删除草稿后回到来处：列表页 onShow 会重新拉取，状态不会停在旧值。 */
  afterConfirm() { setTimeout(() => wx.navigateBack(), 400); },
  /* 草稿保持不动：只是离开页面，没有确认就不会生成任何正式记录。 */
  keepDraft() {
    wx.showToast({ title: "草稿已保留，未生成记录", icon: "none" });
    setTimeout(() => wx.navigateBack(), 600);
  }
});
