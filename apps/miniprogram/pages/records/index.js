const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");
const { localParts, toIso } = require("../../utils/date");
const history = require("./history");

Page({
  data: {
    ...history.data,
    loading: true, error: "", children: [], childIndex: 0, childId: "", mode: "photo",
    date: "", time: "", text: "", photos: [], saving: false, uploadProgress: 0,
    submissionKey: "", canWrite: true
  },
  onLoad() { const now = localParts(); this.setData({ date: now.date, time: now.time, submissionKey: api.newIdempotencyKey("photo-batch") }); },
  ...history.methods,
  onShow() { this.hidden = false; this.load().then(() => { if (this.recordScroll && wx.pageScrollTo) wx.pageScrollTo({ scrollTop: this.recordScroll, duration: 0 }); }); },
  onHide() { this.hidden = true; this.loadId = (this.loadId || 0) + 1; this.historyRequest = (this.historyRequest || 0) + 1; if (this.timer) clearTimeout(this.timer); },
  onUnload() { this.onHide(); },
  schedulePoll() {
    if (this.timer) clearTimeout(this.timer);
    if (!this.hidden && (this.data.recordView !== "history" || this.data.historyView !== "confirmed") && this.data.pendingProcessing) this.timer = setTimeout(() => this.load(), 3500);
  },
  async load() {
    const loadId = (this.loadId || 0) + 1;
    this.loadId = loadId;
    if (this.timer) clearTimeout(this.timer);
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (loadId !== this.loadId) return;
      if (!children.length) { this.clearHistory(); return this.setData({ loading: false, children, childId: "" }); }
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      let childId = children[childIndex].id;
      if (this.data.childId && childId !== this.data.childId && (this.data.text || this.data.photos.length)) {
        const discard = !this.data.saving && await new Promise((resolve) => wx.showModal({ title: "切换孩子", content: "有尚未提交的内容，切换会放弃这些内容。是否继续？", success: (r) => resolve(r.confirm), fail: () => resolve(false) }));
        if (loadId !== this.loadId) return;
        if (discard) this.setData({ text: "", photos: [], submissionKey: api.newIdempotencyKey("photo-batch") });
        else { childIndex = children.findIndex((c) => c.id === this.data.childId); if (childIndex < 0) throw new Error("当前学习档案已不可访问"); childId = this.data.childId; }
      }
      if (childId !== this.data.childId && this.clearHistory) this.clearHistory();
      getApp().selectChild(childId);
      const member = getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      this.setData({ canWrite });
      if (!canWrite) this.setData({ recordView: "history" });
      if (loadId !== this.loadId) return;
      this.setData({ loading: false, children, childIndex, childId });
      if (this.refreshHistory) await this.refreshHistory();
      this.schedulePoll();
    } catch (error) {
      if (loadId !== this.loadId) return;
      if ([401, 403, 404].includes(error.statusCode)) { this.clearHistory(); this.setData({ children: [], childId: "" }); }
      this.setData({ loading: false, error: error.message });
    }
  },
  async changeChild(event) {
    if (this.data.saving) return wx.showToast({ title: "请等待本次上传结束", icon: "none" });
    const childIndex = Number(event.detail.value);
    if (childIndex === this.data.childIndex) return;
    if (this.data.text || this.data.photos.length) {
      const discard = await new Promise((resolve) => wx.showModal({ title: "切换孩子", content: "当前填写内容尚未提交。切换会放弃这些内容，是否继续？", success: (result) => resolve(result.confirm), fail: () => resolve(false) }));
      if (!discard) return;
      this.setData({ text: "", photos: [], submissionKey: api.newIdempotencyKey("photo-batch") });
    }
    getApp().selectChild(this.data.children[childIndex].id);
    await this.load();
  },
  changeMode(event) { if (!this.data.saving) this.setData({ mode: event.currentTarget.dataset.mode, submissionKey: api.newIdempotencyKey(event.currentTarget.dataset.mode) }); },
  setField(event) { if (!this.data.saving) this.setData({ [event.currentTarget.dataset.field]: event.detail.value, submissionKey: api.newIdempotencyKey(this.data.mode) }); },
  chooseCamera() { this.choosePhotos(["camera"]); },
  chooseAlbum() { this.choosePhotos(["album"]); },
  choosePhotos(sourceType) {
    if (this.data.saving) return;
    const remaining = 9 - this.data.photos.length;
    if (!remaining) return wx.showToast({ title: "最多 9 张", icon: "none" });
    wx.chooseMedia({ count: remaining, mediaType: ["image"], sourceType, sizeType: ["compressed"], success: ({ tempFiles }) => { const additions = tempFiles.map((item) => item.tempFilePath); this.setData({ photos: this.data.photos.concat(additions), submissionKey: api.newIdempotencyKey("photo-batch") }); } });
  },
  removePhoto(event) { if (this.data.saving) return; const photos = this.data.photos.slice(); photos.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ photos, submissionKey: api.newIdempotencyKey("photo-batch") }); },
  async save() {
    if (!this.data.childId || this.data.saving) return;
    if (!this.data.canWrite) return;
    if (this.data.mode === "text" && !this.data.text.trim()) return wx.showToast({ title: "请填写学习内容", icon: "none" });
    if (this.data.mode === "photo" && !this.data.photos.length) return wx.showToast({ title: "请添加学习照片", icon: "none" });
    this.setData({ saving: true, uploadProgress: 0 });
    try {
      const occurredAt = toIso(this.data.date, this.data.time);
      let submitted;
      if (this.data.mode === "text") {
        submitted = await api.request("/submissions", { method: "POST", idempotencyKey: this.data.submissionKey, data: { child_id: this.data.childId, occurred_at: occurredAt, input_text: this.data.text.trim(), source: "manual" } });
      } else if (getApp().globalData.useCloud) {
        submitted = await cloudMedia.submitCloudPhotoBatch(
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
        submitted = await api.request(`/submissions/${first.id}/finalize`, { method: "POST" });
      }
      const now = localParts();
      this.setData({ submittedId: submitted ? submitted.id : "" });
      this.setData({ saving: false, photos: [], text: "", uploadProgress: 0, date: now.date, time: now.time, submissionKey: api.newIdempotencyKey(this.data.mode) });
      wx.showToast({ title: "已提交", icon: "success" });
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none", duration: 2600 }); }
  }
});
