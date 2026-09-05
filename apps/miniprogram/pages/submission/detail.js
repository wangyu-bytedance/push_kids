const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");
const { friendlyTime } = require("../../utils/date");

const actions = { complete: "已完成本次复习", partial: "部分完成", reinforce: "需要加强", defer: "稍后复习" };
function formatReview(item) {
  return { ...item, feedback: item.feedback.map((f) => ({ ...f, label: actions[f.action] || f.action, time: friendlyTime(f.occurred_at) })) };
}

module.exports = {
  data: { readOnly: false, detail: null, reviewsOpen: false, reviews: [], reviewsLoading: false, reviewsError: "", hasDue: false, statusLabel: "", actionError: "", conflict: false },
  methods: {
    async loadDetail() {
      const generation = this.loadRequest;
      const sid = this.data.id, child = this.data.submission.child_id;
      const detail = await api.request(`/children/${child}/history/${sid}`);
      if (this.hidden || generation !== this.loadRequest) return;
      this.setData({ detail });
    },
    async toggleReviews() {
      this.setData({ reviewsOpen: !this.data.reviewsOpen });
      if (this.data.reviewsOpen) await this.loadReviews();
    },
    async loadReviews(event) {
      if (this.data.reviewsLoading) return;
      const id = event && event.currentTarget.dataset.id;
      const current = id && this.data.reviews.find((r) => r.review_id === id);
      this.setData({ reviewsLoading: true, reviewsError: "" });
      try {
        const suffix = current ? `?review_id=${id}&before=${current.next_before}` : "";
        const result = await api.request(`/children/${this.data.submission.child_id}/history/${this.data.id}/reviews${suffix}`);
        if (this.hidden) return;
        const incoming = result.items.map(formatReview);
        // One bounded page per knowledge; earlier pages replace the displayed three feedbacks.
        const reviews = current ? this.data.reviews.map((r) => r.review_id === id ? incoming[0] : r) : incoming;
        this.setData({ reviews, hasDue: reviews.some((r) => r.is_due), reviewsLoading: false });
      } catch (error) {
        if (this.hidden) return;
        if ([401, 403, 404].includes(error.statusCode)) this.setData({ detail: null, reviews: [], submission: null, error: error.message });
        this.setData({ reviewsLoading: false, reviewsError: error.message });
      }
    },
    goReview() {
      const app = getApp();
      app.selectChild(this.data.submission.child_id);
      app.globalData.reviewReturn = { childId: this.data.submission.child_id, submissionId: this.data.id,
        reviewIds: this.data.reviews.filter((r) => r.is_due).map((r) => r.review_id) };
      wx.switchTab({ url: "/pages/today/index" });
    },
    async startManual() { this.setData({ manual: true }); await this.load(); },
    async runDraftAction(event) {
      if (this.data.saving) return;
      const action = event.currentTarget.dataset.action;
      if (!["retry", "finalize", "cancel"].includes(action)) return;
      if (action === "cancel") {
        const confirmed = await new Promise((resolve) => wx.showModal({ title: "取消这条提交", content: "取消后停止分析并清理上传照片；不会创建学习记录。", success: (r) => resolve(r.confirm), fail: () => resolve(false) }));
        if (!confirmed) return;
      }
      this.setData({ saving: true, actionError: "" });
      try { await api.request(`/submissions/${this.data.id}/${action}`, { method: "POST" }); await this.load(); }
      catch (error) { this.setData({ actionError: error.message }); }
      finally { this.setData({ saving: false }); }
    },
    async resumePhotos() {
      if (this.data.saving) return;
      const draft = this.data.submission;
      this.setData({ saving: true, actionError: "" });
      try {
        const paths = await new Promise((resolve, reject) => wx.chooseMedia({ count: 9 - draft.media_count,
          mediaType: ["image"], sourceType: ["album", "camera"], sizeType: ["compressed"],
          success: ({ tempFiles }) => resolve(tempFiles.map((f) => f.tempFilePath)), fail: reject }));
        if (getApp().globalData.useCloud) await cloudMedia.uploadDraftPhotos(draft, paths, null, draft.upload_batch_key || `resume-${draft.id}`);
        else {
          for (const path of paths) await api.appendSubmissionMedia(draft.id, path);
          await api.request(`/submissions/${draft.id}/finalize`, { method: "POST" });
        }
        await this.load();
      } catch (error) { if (!String(error.errMsg || "").includes("cancel")) this.setData({ actionError: error.message || "上传未完成，可重试补传" }); }
      finally { this.setData({ saving: false }); }
    }
  }
};
