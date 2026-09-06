const api = require("../../utils/api");
const detail = require("../submission/detail");
const { friendlyTime } = require("../../utils/date");

/* 状态文案不暗示 AI 已经给出结论：只说明这条提交现在处于哪一步。 */
const STATUS_TEXT = {
  queued: "等待分析",
  analyzing: "正在分析",
  failed: "分析失败",
  pending_confirmation: "待家长确认",
  confirmed: "已确认",
  cancelled: "已取消"
};
const STATUS_TONE = {
  queued: "neutral",
  analyzing: "info",
  failed: "dan",
  pending_confirmation: "att",
  confirmed: "suc",
  cancelled: "neutral"
};

function titleOf(submission, view) {
  if (view && view.hasRecord && view.subjectName) return view.subjectName;
  if (submission.state === "failed") return "未识别科目";
  if (submission.source === "photo" || submission.media_count) return `${submission.media_count || 0} 张照片`;
  return "文字记录";
}

Page({
  data: {
    ...detail.data,
    id: "", loading: true, saving: false, error: "", submission: null, canWrite: true,
    statusTone: "neutral", titleText: ""
  },
  ...detail.methods,
  onLoad(options) {
    this.setData({ id: (options && options.id) || "" });
    this.load();
  },
  onShow() { const stale = this.hidden; this.hidden = false; if (stale) this.load(); },
  onHide() {
    this.hidden = true;
    this.loadRequest = (this.loadRequest || 0) + 1;
    if (this.timer) clearTimeout(this.timer);
  },
  onUnload() { this.onHide(); },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  async load() {
    const generation = (this.loadRequest || 0) + 1;
    this.loadRequest = generation;
    if (this.timer) clearTimeout(this.timer);
    this.setData({ error: "" });
    try {
      const submission = await api.request(`/submissions/${this.data.id}`);
      if (generation !== this.loadRequest) return;
      const member = typeof getApp === "function" && getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      this.setData({
        canWrite, readOnly: true,
        submission: { ...submission,
          time_label: friendlyTime(submission.occurred_at),
          submitted_label: friendlyTime(submission.created_at || submission.occurred_at) },
        statusLabel: STATUS_TEXT[submission.state] || "请下拉刷新状态",
        statusTone: STATUS_TONE[submission.state] || "neutral"
      });
      if (wx.setNavigationBarTitle) {
        wx.setNavigationBarTitle({ title: submission.state === "confirmed" ? "学习记录详情" : "待处理记录" });
      }
      await this.loadDetail();
      if (generation !== this.loadRequest) return;
      this.setData({ loading: false, titleText: titleOf(submission, this.data.detailView) });
      /* 已确认记录默认展开复习情况；复习日期来自后端确定性策略。 */
      if (this.data.detailView && this.data.detailView.hasRecord && !this.data.reviewsOpen) {
        this.setData({ reviewsOpen: true });
        await this.loadReviews();
      }
      if (generation !== this.loadRequest) return;
      if (!this.hidden && !submission.awaiting_upload && ["queued", "analyzing"].includes(submission.state)) {
        this.timer = setTimeout(() => this.load(), 3500);
      }
    } catch (error) {
      if (generation !== this.loadRequest) return;
      const gone = [401, 403, 404].includes(error.statusCode);
      this.setData({ loading: false, error: error.message,
        submission: gone ? null : this.data.submission,
        detail: gone ? null : this.data.detail,
        detailView: gone ? null : this.data.detailView,
        reviews: gone ? [] : this.data.reviews });
    }
  },
  /* 确认与人工录入都只在确认页发生，这里只负责把家长送过去。 */
  openConfirm() { wx.navigateTo({ url: `/pages/submission/confirm?id=${this.data.id}` }); },
  startManual() { wx.navigateTo({ url: `/pages/submission/confirm?id=${this.data.id}&manual=1` }); }
});
