const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");
const { localParts, toIso } = require("../../utils/date");
const childContext = require("../../utils/child-context");
const history = require("./history");

function shortDate(value) {
  const parts = value.split("-");
  return `${parts[1]}月${parts[2]}日`;
}

Page({
  data: {
    ...history.data,
    loading: true, error: "", children: [], childIndex: 0, childId: "",
    date: "", dateLabel: "", time: "", text: "", hasText: false, photos: [], saving: false, uploadProgress: 0,
    submissionKey: "", canWrite: true, today: "", backfill: false, timeOpen: false
  },
  onLoad() { const now = localParts(); this.setData({ date: now.date, dateLabel: shortDate(now.date), time: now.time, today: now.date, submissionKey: api.newIdempotencyKey("record-entry") }); },
  ...history.methods,
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 2 });
    this.hidden = false;
    this.load().then(() => { if (this.recordScroll && wx.pageScrollTo) wx.pageScrollTo({ scrollTop: this.recordScroll, duration: 0 }); });
  },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  toggleTime() { if (!this.data.saving) this.setData({ timeOpen: !this.data.timeOpen }); },
  onHide() { this.hidden = true; this.loadId = (this.loadId || 0) + 1; this.historyRequest = (this.historyRequest || 0) + 1; if (this.timer) clearTimeout(this.timer); },
  onUnload() { this.onHide(); },
  schedulePoll() {
    if (this.timer) clearTimeout(this.timer);
    if (!this.hidden && (!this.data.historyExpanded || this.data.historyView !== "confirmed") && this.data.pendingProcessing) this.timer = setTimeout(() => this.load(), 3500);
  },
  async load() {
    const loadId = (this.loadId || 0) + 1;
    this.loadId = loadId;
    if (this.timer) clearTimeout(this.timer);
    this.setData({ loading: true, error: "" });
    try {
      const profiles = await api.request("/children");
      if (loadId !== this.loadId) return;
      /* 这一页有未提交内容的确认流程，所以先解析、等家长决定后再落回全局态。 */
      const selection = childContext.resolveSelection(profiles, getApp().globalData.selectedChildId);
      const children = selection.children;
      if (!children.length) { this.clearHistory(); getApp().selectChild(""); return this.setData({ loading: false, children, childId: "" }); }
      let childIndex = selection.childIndex;
      let childId = selection.childId;
      if (this.data.childId && childId !== this.data.childId && (this.data.text || this.data.photos.length)) {
        const discard = !this.data.saving && await new Promise((resolve) => wx.showModal({ title: "切换孩子", content: "有尚未提交的内容，切换会放弃这些内容。是否继续？", success: (r) => resolve(r.confirm), fail: () => resolve(false) }));
        if (loadId !== this.loadId) return;
        if (discard) this.setData({ text: "", hasText: false, photos: [], submissionKey: api.newIdempotencyKey("record-entry") });
        else { childIndex = children.findIndex((c) => c.id === this.data.childId); if (childIndex < 0) throw new Error("当前学习档案已不可访问"); childId = this.data.childId; }
      }
      if (childId !== this.data.childId && this.clearHistory) { this.clearHistory(); this.restoreFilters(childId); }
      getApp().selectChild(childId);
      const member = getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      this.setData({ canWrite, historyExpanded: canWrite ? this.data.historyExpanded : true });
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
      this.setData({ text: "", hasText: false, photos: [], submissionKey: api.newIdempotencyKey("record-entry") });
    }
    getApp().selectChild(this.data.children[childIndex].id);
    await this.load();
  },
  setField(event) {
    if (this.data.saving) return;
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const next = { [field]: value, submissionKey: api.newIdempotencyKey(this.data.photos.length ? "photo-batch" : "manual") };
    if (field === "text") next.hasText = Boolean(value.trim());
    if (field === "date") { next.dateLabel = shortDate(value); next.backfill = value < this.data.today; }
    this.setData(next);
  },
  addPhotos() {
    if (this.data.saving) return;
    const remaining = 9 - this.data.photos.length;
    if (!remaining) return wx.showToast({ title: "最多 9 张", icon: "none" });
    if (typeof wx.chooseMedia !== "function") return wx.showToast({ title: "当前微信版本无法选择照片，可直接填写学习内容", icon: "none" });
    wx.chooseMedia({
      count: remaining,
      mediaType: ["image"],
      sourceType: ["camera", "album"],
      sizeType: ["compressed"],
      success: ({ tempFiles = [] }) => {
        const additions = tempFiles.map((item) => item && item.tempFilePath).filter(Boolean).slice(0, remaining);
        if (!additions.length) return;
        this.setData({ photos: this.data.photos.concat(additions), submissionKey: api.newIdempotencyKey("photo-batch") });
      },
      fail: (error) => {
        if (/cancel/i.test((error && error.errMsg) || "")) return;
        wx.showToast({ title: "暂时无法选择照片，可继续填写学习内容", icon: "none" });
      }
    });
  },
  removePhoto(event) { if (this.data.saving) return; const photos = this.data.photos.slice(); photos.splice(Number(event.currentTarget.dataset.index), 1); this.setData({ photos, submissionKey: api.newIdempotencyKey(photos.length ? "photo-batch" : "manual") }); },
  async save() {
    if (!this.data.childId || this.data.saving) return;
    if (!this.data.canWrite) return;
    const inputText = this.data.text.trim();
    const hasPhotos = this.data.photos.length > 0;
    if (!hasPhotos && !inputText) return wx.showToast({ title: "请添加学习照片或填写学习内容", icon: "none" });
    this.setData({ saving: true, uploadProgress: 0 });
    try {
      const occurredAt = toIso(this.data.date, this.data.time);
      let submitted;
      if (!hasPhotos) {
        submitted = await api.request("/submissions", { method: "POST", idempotencyKey: this.data.submissionKey, data: { child_id: this.data.childId, occurred_at: occurredAt, input_text: inputText, source: "manual" } });
      } else if (getApp().globalData.useCloud) {
        submitted = await cloudMedia.submitCloudPhotoBatch(
          this.data.photos,
          { child_id: this.data.childId, occurred_at: occurredAt, input_text: inputText },
          (progress) => this.setData({ uploadProgress: progress }),
          this.data.submissionKey
        );
      } else {
        const total = this.data.photos.length;
        const first = await api.uploadSubmission(this.data.photos[0], { child_id: this.data.childId, occurred_at: occurredAt, input_text: inputText, defer_analysis: "true" }, (progress) => this.setData({ uploadProgress: Math.round(progress / total) }), this.data.submissionKey);
        this.setData({ uploadProgress: Math.round(first.media_count / total * 100) });
        for (let index = first.media_count; index < total; index += 1) await api.appendSubmissionMedia(first.id, this.data.photos[index], (progress) => this.setData({ uploadProgress: Math.round((index + progress / 100) / total * 100) }));
        submitted = await api.request(`/submissions/${first.id}/finalize`, { method: "POST" });
      }
      const now = localParts();
      this.setData({ submittedId: submitted ? submitted.id : "" });
      this.setData({ saving: false, photos: [], text: "", hasText: false, uploadProgress: 0, date: now.date, dateLabel: shortDate(now.date), time: now.time, today: now.date, backfill: false, timeOpen: false, submissionKey: api.newIdempotencyKey("record-entry") });
      wx.showToast({ title: "已提交，正在整理", icon: "success" });
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none", duration: 2600 }); }
  }
});
