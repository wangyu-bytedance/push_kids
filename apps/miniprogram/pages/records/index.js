const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");
const { localParts, toIso } = require("../../utils/date");
const childContext = require("../../utils/child-context");
const history = require("./history");
const { createVoiceInputController } = require("./voice-input");

function shortDate(value) {
  const parts = value.split("-");
  return `${parts[1]}月${parts[2]}日`;
}

Page({
  data: {
    ...history.data,
    loading: true, error: "", children: [], childIndex: 0, childId: "",
    date: "", dateLabel: "", time: "", text: "", hasText: false, photos: [], saving: false, uploadProgress: 0,
    submissionKey: "", canWrite: true, today: "", backfill: false, timeOpen: false,
    voiceState: "idle", voiceBusy: false, voiceOverflowText: "", voiceOverflowOpen: false,
    introArtFailed: false, uploadArtFailed: false
  },
  onIllustrationError(event) {
    const art = event.currentTarget.dataset.art;
    if (art === "intro") this.setData({ introArtFailed: true });
    if (art === "upload") this.setData({ uploadArtFailed: true });
  },
  onLoad() {
    const now = localParts();
    let windowWidth = 375;
    if (typeof wx.getSystemInfoSync === "function") {
      const system = wx.getSystemInfoSync();
      windowWidth = system.windowWidth || windowWidth;
    }
    this.voiceCancelThreshold = 80 * windowWidth / 750;
    this.voiceController = createVoiceInputController({
      wxApi: wx,
      getContextKey: () => this.data.childId,
      onState: ({ state, busy }) => this.setData({ voiceState: state, voiceBusy: busy }),
      onResult: ({ text, contextKey }) => this.appendVoiceResult(text, contextKey),
      onNotice: (notice) => this.showVoiceNotice(notice)
    });
    this.setData({ date: now.date, dateLabel: shortDate(now.date), time: now.time, today: now.date, submissionKey: api.newIdempotencyKey("record-entry") });
  },
  ...history.methods,
  async consumeRecordIntent() {
    const app = getApp();
    const intent = app.globalData.recordIntent;
    if (intent && intent.view === "history") {
      delete app.globalData.recordIntent;
      app.globalData.historyIntent = intent;
      wx.switchTab({ url: "/pages/reports/index" });
      return;
    }
    return history.methods.consumeRecordIntent.call(this);
  },
  openHistoryPending() {
    getApp().globalData.historyIntent = { childId: this.data.childId, view: "history", status: "pending" };
    wx.switchTab({ url: "/pages/reports/index" });
  },
  openHistoryInReports() {
    getApp().globalData.historyIntent = { childId: this.data.childId, view: "history", status: "confirmed" };
    wx.switchTab({ url: "/pages/reports/index" });
  },
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
  onHide() {
    this.hidden = true;
    this.loadId = (this.loadId || 0) + 1;
    this.historyRequest = (this.historyRequest || 0) + 1;
    this.voiceGestureActive = false;
    if (this.voiceController) this.voiceController.cancel();
    if (this.timer) clearTimeout(this.timer);
  },
  onUnload() {
    this.onHide();
    if (this.voiceController) this.voiceController.dispose();
  },
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
      if (!children.length) {
        if (this.voiceController) this.voiceController.cancel();
        this.clearHistory();
        getApp().selectChild("");
        return this.setData({ loading: false, children, childId: "" });
      }
      let childIndex = selection.childIndex;
      let childId = selection.childId;
      if (this.data.childId && childId !== this.data.childId && (this.data.text || this.data.photos.length || this.data.voiceOverflowText)) {
        const discard = !this.data.saving && await new Promise((resolve) => wx.showModal({ title: "切换孩子", content: "有尚未提交的内容，切换会放弃这些内容。是否继续？", success: (r) => resolve(r.confirm), fail: () => resolve(false) }));
        if (loadId !== this.loadId) return;
        if (discard) this.setData({ text: "", hasText: false, photos: [], voiceOverflowText: "", voiceOverflowOpen: false, submissionKey: api.newIdempotencyKey("record-entry") });
        else { childIndex = children.findIndex((c) => c.id === this.data.childId); if (childIndex < 0) throw new Error("当前学习档案已不可访问"); childId = this.data.childId; }
      }
      if (this.data.childId && childId !== this.data.childId && this.voiceController) this.voiceController.cancel();
      if (childId !== this.data.childId && this.clearHistory) { this.clearHistory(); this.restoreFilters(childId); }
      getApp().selectChild(childId);
      const member = getApp().globalData.currentMember;
      const canWrite = !member || member.role !== "viewer";
      if (!canWrite && this.voiceController) this.voiceController.cancel();
      this.setData({ canWrite, historyExpanded: false });
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
    if (this.data.text || this.data.photos.length || this.data.voiceOverflowText) {
      const discard = await new Promise((resolve) => wx.showModal({ title: "切换孩子", content: "当前填写内容尚未提交。切换会放弃这些内容，是否继续？", success: (result) => resolve(result.confirm), fail: () => resolve(false) }));
      if (!discard) return;
      this.setData({ text: "", hasText: false, photos: [], voiceOverflowText: "", voiceOverflowOpen: false, submissionKey: api.newIdempotencyKey("record-entry") });
    }
    this.voiceGestureActive = false;
    if (this.voiceController) this.voiceController.cancel();
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
  voiceTouchStart(event) {
    if (this.data.saving || !this.data.canWrite || !this.voiceController) return;
    const touch = event.touches && event.touches[0];
    this.voiceStartY = touch ? touch.clientY : 0;
    this.voiceGestureActive = true;
    this.voiceController.begin({
      contextKey: this.data.childId,
      isGestureActive: () => this.voiceGestureActive
    });
  },
  voiceTouchMove(event) {
    if (!this.voiceGestureActive || !this.voiceController) return;
    const touch = event.touches && event.touches[0];
    if (!touch) return;
    this.voiceController.setCancelArmed(this.voiceStartY - touch.clientY >= this.voiceCancelThreshold);
  },
  voiceTouchEnd() {
    if (!this.voiceGestureActive || !this.voiceController) return;
    this.voiceGestureActive = false;
    this.voiceController.finish();
  },
  voiceTouchCancel() {
    this.voiceGestureActive = false;
    if (this.voiceController) this.voiceController.cancel();
  },
  showVoiceNotice({ code, message }) {
    if (code !== "permission_denied") {
      wx.showToast({ title: message, icon: "none", duration: 2400 });
      return;
    }
    wx.showModal({
      title: "需要麦克风权限",
      content: "允许麦克风后才能使用语音输入，也可以继续手动填写。",
      confirmText: "去设置",
      cancelText: "继续手填",
      success: ({ confirm }) => {
        if (confirm && typeof wx.openSetting === "function") wx.openSetting({});
      }
    });
  },
  appendVoiceResult(result, contextKey) {
    if (!result || contextKey !== this.data.childId) return;
    const next = this.data.text ? `${this.data.text}\n${result}` : result;
    if (next.length > 4000) {
      this.setData({ voiceOverflowText: result, voiceOverflowOpen: true });
      wx.showToast({ title: "内容超过 4000 字，请先精简", icon: "none" });
      return;
    }
    this.setData({
      text: next,
      hasText: Boolean(next.trim()),
      submissionKey: api.newIdempotencyKey(this.data.photos.length ? "photo-batch" : "manual")
    });
    wx.showToast({ title: "已转成文字，请检查", icon: "none" });
  },
  setVoiceOverflow(event) {
    this.setData({ voiceOverflowText: event.detail.value });
  },
  applyVoiceOverflow() {
    const result = this.data.voiceOverflowText.trim();
    const next = this.data.text && result ? `${this.data.text}\n${result}` : (result || this.data.text);
    if (!result) return wx.showToast({ title: "请先编辑待加入文字", icon: "none" });
    if (next.length > 4000) return wx.showToast({ title: "仍超过 4000 字，请继续精简", icon: "none" });
    this.setData({
      text: next,
      hasText: Boolean(next.trim()),
      voiceOverflowText: "",
      voiceOverflowOpen: false,
      submissionKey: api.newIdempotencyKey(this.data.photos.length ? "photo-batch" : "manual")
    });
  },
  discardVoiceOverflow() {
    this.setData({ voiceOverflowText: "", voiceOverflowOpen: false });
  },
  async save() {
    if (!this.data.childId || this.data.saving) return;
    if (!this.data.canWrite) return;
    if (this.data.voiceBusy || (this.voiceController && this.voiceController.isBusy())) return wx.showToast({ title: "请先结束本次语音输入", icon: "none" });
    if (this.data.voiceOverflowOpen) return wx.showToast({ title: "请先处理待加入的语音文字", icon: "none" });
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
      this.setData({ saving: false, photos: [], text: "", hasText: false, voiceOverflowText: "", voiceOverflowOpen: false, uploadProgress: 0, date: now.date, dateLabel: shortDate(now.date), time: now.time, today: now.date, backfill: false, timeOpen: false, submissionKey: api.newIdempotencyKey("record-entry") });
      wx.showToast({ title: "已提交，正在整理", icon: "success" });
      await this.load();
    } catch (error) { this.setData({ saving: false }); wx.showToast({ title: error.message, icon: "none", duration: 2600 }); }
  }
});
