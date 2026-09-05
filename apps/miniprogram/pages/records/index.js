const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");
const { localParts, toIso } = require("../../utils/date");
const { stateLabel } = require("../../utils/view-state");

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", mode: "photo",
    date: "", time: "", text: "", photos: [], saving: false, uploadProgress: 0,
    submissionKey: "", submissions: []
  },
  onLoad() { const now = localParts(); this.setData({ date: now.date, time: now.time, submissionKey: api.newIdempotencyKey("photo-batch") }); },
  onShow() { this.load(); },
  onHide() { if (this.timer) clearTimeout(this.timer); },
  async load() {
    if (this.timer) clearTimeout(this.timer);
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (!children.length) return this.setData({ loading: false, children, submissions: [] });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const submissions = await api.request(`/submissions?child_id=${childId}`);
      const pending = submissions
        .filter((item) => item.state !== "confirmed" && item.state !== "cancelled")
        .map((item) => ({
          ...item,
          state_label: item.can_finalize_upload ? "照片已保存，可继续分析" : stateLabel(item.state)
        }));
      this.setData({ loading: false, children, childIndex, childId, submissions: pending });
      if (pending.some((item) => (item.state === "queued" && !item.can_finalize_upload) || item.state === "analyzing")) this.timer = setTimeout(() => this.load(), 3500);
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { const childIndex = Number(event.detail.value); getApp().selectChild(this.data.children[childIndex].id); this.load(); },
  changeMode(event) { this.setData({ mode: event.currentTarget.dataset.mode, submissionKey: api.newIdempotencyKey(event.currentTarget.dataset.mode) }); },
  setField(event) { this.setData({ [event.currentTarget.dataset.field]: event.detail.value, submissionKey: api.newIdempotencyKey(this.data.mode) }); },
  chooseCamera() { this.choosePhotos(["camera"]); },
  chooseAlbum() { this.choosePhotos(["album"]); },
  choosePhotos(sourceType) {
    const remaining = 9 - this.data.photos.length;
    if (!remaining) return wx.showToast({ title: "最多 9 张", icon: "none" });
    wx.chooseMedia({ count: remaining, mediaType: ["image"], sourceType, sizeType: ["compressed"], success: ({ tempFiles }) => { const additions = tempFiles.map((item) => item.tempFilePath); this.setData({ photos: this.data.photos.concat(additions), submissionKey: api.newIdempotencyKey("photo-batch") }); } });
  },
  removePhoto(event) { const photos = this.data.photos.slice(); photos.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ photos, submissionKey: api.newIdempotencyKey("photo-batch") }); },
  confirm(event) { wx.navigateTo({ url: `/pages/submission/confirm?id=${event.currentTarget.dataset.id}` }); },
  openSubmission(event) {
    const item = this.data.submissions.find((row) => row.id === event.currentTarget.dataset.id);
    if (item && item.state === "pending_confirmation") this.confirm(event);
  },
  async retry(event) { try { await api.request(`/submissions/${event.currentTarget.dataset.id}/retry`, { method: "POST" }); await this.load(); } catch (error) { wx.showToast({ title: error.message, icon: "none" }); } },
  async finalizePending(event) {
    try {
      await api.request(`/submissions/${event.currentTarget.dataset.id}/finalize`, { method: "POST" });
      wx.showToast({ title: "已继续分析", icon: "success" });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async cancelSubmission(event) {
    try {
      await api.request(`/submissions/${event.currentTarget.dataset.id}/cancel`, { method: "POST" });
      await this.load();
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async save() {
    if (!this.data.childId || this.data.saving) return;
    if (this.data.mode === "text" && !this.data.text.trim()) return wx.showToast({ title: "请填写学习内容", icon: "none" });
    if (this.data.mode === "photo" && !this.data.photos.length) return wx.showToast({ title: "请添加学习照片", icon: "none" });
    this.setData({ saving: true, uploadProgress: 0 });
    try {
      const occurredAt = toIso(this.data.date, this.data.time);
      if (this.data.mode === "text") {
        await api.request("/submissions", { method: "POST", idempotencyKey: this.data.submissionKey, data: { child_id: this.data.childId, occurred_at: occurredAt, input_text: this.data.text.trim(), source: "manual" } });
      } else if (getApp().globalData.useCloud) {
        await cloudMedia.submitCloudPhotoBatch(
          this.data.photos,
          { child_id: this.data.childId, occurred_at: occurredAt, input_text: this.data.text.trim() },
          (progress) => this.setData({ uploadProgress: progress }),
          this.data.submissionKey
        );
      } else {
        const total = this.data.photos.length;
        const first = await api.uploadSubmission(this.data.photos[0], { child_id: this.data.childId, occurred_at: occurredAt, input_text: this.data.text.trim(), defer_analysis: "true" }, (progress) => this.setData({ uploadProgress: Math.round(progress / total) }), this.data.submissionKey);
        this.setData({ uploadProgress: Math.round(first.media_count / total * 100) });
        for (let index = first.media_count; index < total; index += 1) await api.appendSubmissionMedia(first.id, this.data.photos[index], (progress) => this.setData({ uploadProgress: Math.round((index + progress / 100) / total * 100) }));
        await api.request(`/submissions/${first.id}/finalize`, { method: "POST" });
      }
      const now = localParts();
      this.setData({ saving: false, photos: [], text: "", uploadProgress: 0, date: now.date, time: now.time, submissionKey: api.newIdempotencyKey(this.data.mode) });
      wx.showToast({ title: "已提交", icon: "success" });
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none", duration: 2600 }); }
  }
});
