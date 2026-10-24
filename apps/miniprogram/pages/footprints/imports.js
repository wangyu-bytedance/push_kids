const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");

module.exports = {
  async beginImport() {
    if (this.data.saving || this.uploading || !this.data.canWrite || !this.data.child || this.data.child.active === false) return;
    this.setData({ sheet: "consent", photoConsent: false, sheetError: "" });
  },
  consentChange(event) { this.setData({ photoConsent: event.detail.value.includes("photos") }); },
  aiChange(event) { this.setData({ aiEnabled: event.detail.value }); },
  async choosePhotos() {
    if (!this.data.photoConsent || this.data.saving) return this.setData({ sheetError: "请先同意照片时间和位置处理，或手动记录" });
    const seq = this.sequence;
    try {
      await api.request("/footprints/preferences", { method: "PATCH", data: { ai_enabled: this.data.aiEnabled, consented: true } });
      if (this.stale(seq)) return;
      const selected = await new Promise((resolve, reject) => {
        if (!wx.chooseMedia) return reject(new Error("请更新微信后从相册选择照片"));
        const sdk = typeof wx.getAppBaseInfo === "function" ? wx.getAppBaseInfo().SDKVersion : "2.10.0";
        const parts = sdk.split(".").map(Number);
        const count = parts[0] > 2 || (parts[0] === 2 && parts[1] >= 25) ? 20 : 9;
        wx.chooseMedia({ count, mediaType: ["image"], sourceType: ["album"], sizeType: ["original"],
          success: resolve, fail: (error) => reject(new Error(String(error.errMsg).includes("cancel") ? "已取消选图" : "无法打开相册，请检查授权")) });
      });
      if (this.stale(seq)) return;
      this.pendingFiles = selected.tempFiles.map((file) => file.tempFilePath);
      this.setData({ hasPendingUpload: true });
      this.pendingBatchKey = api.newIdempotencyKey("footprint-import");
      await this.uploadBatch();
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message, saving: false }); }
  },
  async uploadBatch() {
    if (this.data.saving || this.uploading || !this.pendingFiles || !this.pendingFiles.length) return;
    this.uploading = true;
    const seq = this.sequence; this.setData({ saving: true, sheetError: "", importProgress: 0 });
    try {
      const batch = await api.request("/footprints/imports", { method: "POST", idempotencyKey: this.pendingBatchKey,
        data: { child_id: this.data.childId, count: this.pendingFiles.length, consented: true } });
      this.pendingImportId = batch.id;
      for (let index = 0; index < this.pendingFiles.length; index += 1) {
        if (this.stale(seq)) return;
        const photo = batch.photos[index];
        if (!photo.received_at) {
          const path = this.pendingFiles[index];
          const metadata = await cloudMedia.imageMetadata(path);
          if (metadata.byteSize > 10 * 1024 * 1024) throw new Error("单张照片不能超过10MB，请缩小后重试");
          if (getApp().globalData.useCloud) {
            const ticket = await api.request(`/footprints/photos/${photo.id}/upload-ticket?${this.params()}`, { method: "POST" });
            const fileId = await cloudMedia.uploadObject(path, ticket.cloud_path);
            await api.request(`/footprints/photos/${photo.id}/claim?${this.params()}`, { method: "POST", data: { file_id: fileId } });
          } else await api.uploadFootprint(photo.id, this.data.childId, path);
        }
        if (!this.stale(seq)) this.setData({ importProgress: Math.round((index + 1) / this.pendingFiles.length * 100) });
      }
      this.pendingFiles = null;
      if (!this.stale(seq)) { this.setData({ saving: false, hasPendingUpload: false }); await this.openDrafts(); }
    } catch (error) { if (!this.stale(seq)) { this.setData({ saving: false, sheetError: error.message }); await this.openDrafts(true); } }
    finally {
      this.uploading = false;
      if (!this.disposed) this.setData({ saving: false });
    }
  },
  async openDrafts(preserveError = false) {
    if (!this.data.canWrite || this.data.saving) return;
    const seq = this.sequence;
    this.pausePlayback();
    this.draftPaging = false;
    this.setData({ sheet: "review", sheetError: preserveError ? this.data.sheetError : "", selectedCount: 0 });
    try {
      const result = await api.request(`/footprints/drafts?${this.params()}`);
      if (this.stale(seq) || this.data.sheet !== "review") return;
      this.setData({ drafts: this.decorateDrafts(result.items), draftsCursor: result.next_cursor });
      this.fillPreviews(result.items, "drafts", seq);
      this.pollDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  pollDrafts() {
    if (this.pollTimer) clearTimeout(this.pollTimer);
    if (this.hidden || this.draftPaging || this.data.sheet !== "review") return;
    if (this.data.drafts.some((photo) => ["queued", "running"].includes(photo.job_state))) {
      this.pollTimer = setTimeout(() => this.refreshDrafts(), 2500);
    }
  },
  async refreshDrafts() {
    if (this.hidden || this.draftPaging || this.data.sheet !== "review" || this.data.saving) return;
    const seq = this.sequence;
    try {
      const result = await api.request(`/footprints/drafts?${this.params()}`);
      if (this.stale(seq) || this.draftPaging || this.data.sheet !== "review") return;
      const chosen = new Set(this.data.drafts.filter((photo) => photo.selected).map((photo) => photo.id));
      const drafts = this.decorateDrafts(result.items).map((photo) => ({ ...photo, selected: chosen.has(photo.id) }));
      const previous = new Map(this.data.drafts.map((photo) => [photo.id, photo]));
      drafts.forEach((photo) => { photo.previewUrl = (previous.get(photo.id) || {}).previewUrl || ""; });
      this.setData({ drafts, selectedCount: drafts.filter((photo) => photo.selected).length, draftsCursor: result.next_cursor });
      this.fillPreviews(drafts.filter((photo) => !photo.previewUrl), "drafts", seq);
      this.pollDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  async moreDrafts() {
    if (!this.data.draftsCursor || this.data.saving) return;
    if (this.data.drafts.length >= 100) return this.setData({ sheetError: "请先整理当前照片，再读取下一页" });
    const seq = this.sequence;
    this.draftPaging = true;
    if (this.pollTimer) clearTimeout(this.pollTimer);
    try {
      const result = await api.request(`/footprints/drafts?${this.params({ cursor: this.data.draftsCursor })}`);
      if (!this.stale(seq) && this.data.sheet === "review") this.setData({ drafts: [...this.data.drafts, ...this.decorateDrafts(result.items)], draftsCursor: result.next_cursor });
      if (!this.stale(seq)) this.fillPreviews(result.items, "drafts", seq);
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  selectDraft(event) {
    const id = event.currentTarget.dataset.id;
    const drafts = this.data.drafts.map((photo) => photo.id === id ? { ...photo, selected: !photo.selected } : photo);
    if (drafts.filter((photo) => photo.selected).length > 20) return this.setData({ sheetError: "每次最多确认20条，可分批继续" });
    this.setData({ drafts, selectedCount: drafts.filter((photo) => photo.selected).length });
  },
  selectAll() {
    const selected = !this.data.selectedCount;
    const drafts = this.data.drafts.map((photo, index) => ({ ...photo, selected: selected && index < 20 }));
    this.setData({ drafts, selectedCount: drafts.filter((photo) => photo.selected).length });
  },
  askConfirm() {
    const selected = this.data.drafts.filter((photo) => photo.selected);
    if (!selected.length) return this.setData({ sheetError: "请先选择要入档的照片" });
    if (selected.some((photo) => !photo.local_date || (!photo.has_display && !photo.is_manual))) {
      return this.setData({ sheetError: "请补充拍摄日期，并等待展示图处理成功；其他照片可以先确认" });
    }
    this.setData({ sheet: "confirm", sheetError: "", confirmCount: selected.length,
      unlocatedCount: selected.filter((photo) => photo.latitude === null || photo.latitude === undefined).length });
  },
  async confirmSelected() {
    if (this.data.saving) return;
    const seq = this.sequence;
    this.setData({ saving: true, sheetError: "" });
    try {
      const batches = {};
      this.data.drafts.filter((photo) => photo.selected).forEach((photo) => {
        (batches[photo.import_id] ||= []).push({ id: photo.id, version: photo.version });
      });
      for (const [id, selected] of Object.entries(batches)) {
        await api.request(`/footprints/imports/${id}/confirm?${this.params()}`, { method: "POST",
          data: { photos: selected, confirm_actual_visit: true } });
      }
      if (this.stale(seq)) return;
      this.setData({ saving: false, sheet: "", selectedCount: 0 });
      wx.showToast({ title: "已入档", icon: "success" });
      await this.refresh(seq);
    } catch (error) { if (!this.stale(seq)) this.setData({ saving: false, sheetError: error.message + "；已成功的条目保留，可刷新继续核对" }); }
  },
  backToReview() { this.setData({ sheet: "review", sheetError: "" }); },
  openSettings() { this.setData({ sheet: "settings", sheetError: "" }); },
  async saveSettings() {
    if (this.data.saving) return;
    const seq = this.sequence; this.setData({ saving: true, sheetError: "" });
    try {
      await api.request("/footprints/preferences", { method: "PATCH", data: { ai_enabled: this.data.aiEnabled, consented: true } });
      if (!this.stale(seq)) this.setData({ saving: false, sheet: "" });
    } catch (error) { if (!this.stale(seq)) this.setData({ saving: false, sheetError: error.message }); }
  }
};
