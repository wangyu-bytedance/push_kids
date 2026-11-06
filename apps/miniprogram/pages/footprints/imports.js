const api = require("../../utils/api");
const cloudMedia = require("../../utils/cloud-media");

module.exports = {
  async beginImport() {
    if (this.data.saving || this.data.selecting || this.uploading || !this.data.canWrite || !this.data.child || this.data.child.active === false) return;
    if (this.pendingFiles && this.pendingFiles.length) return this.openDrafts();
    return this.choosePhotos();
  },
  aiChange(event) { this.setData({ aiEnabled: event.detail.value }); },
  async choosePhotos() {
    if (this.data.saving || this.data.selecting) return;
    const context = this.operationContext(), seq = this.sequence;
    let selectionError = "";
    this.pausePlayback();
    this.setData({ selecting: true, error: "", importError: "", sheetError: "" });
    try {
      const selected = await new Promise((resolve, reject) => {
        if (!wx.chooseMedia) return reject(new Error("请更新微信后从相册选择照片"));
        const sdk = typeof wx.getAppBaseInfo === "function" ? wx.getAppBaseInfo().SDKVersion : "2.10.0";
        const parts = sdk.split(".").map(Number);
        const count = parts[0] > 2 || (parts[0] === 2 && parts[1] >= 25) ? 20 : 9;
        wx.chooseMedia({ count, mediaType: ["image"], sourceType: ["album"], sizeType: ["original"],
          success: resolve, fail: (error) => {
            const cancelled = String(error.errMsg).includes("cancel"), failure = new Error(cancelled ? "" : "无法打开相册，请检查授权");
            failure.cancelled = cancelled; reject(failure);
          } });
      });
      if (!this.operationCurrent(context)) return;
      if (!selected.tempFiles || !selected.tempFiles.length) return;
      this.pendingFiles = selected.tempFiles.map((file) => file.tempFilePath);
      this.setData({ hasPendingUpload: true });
      this.pendingBatchKey = api.newIdempotencyKey("footprint-import");
      this.setData({ selecting: false });
      await this.uploadBatch();
    } catch (error) { selectionError = error.cancelled ? "" : error.message; }
    finally { if (this.operationCurrent(context)) {
      this.setData({ selecting: false });
      if (!this.hidden && seq !== this.sequence && !this.data.sheet) await this.load();
      if (this.operationCurrent(context) && selectionError) this.setData({ importError: selectionError });
    } }
  },
  async uploadBatch() {
    if (this.data.saving || this.uploading || !this.pendingFiles || !this.pendingFiles.length) return;
    this.uploading = true;
    const context = this.operationContext(); this.setData({ saving: true, sheet: "uploading", sheetError: "",
      importProgress: 0, importCompleted: 0, importCount: this.pendingFiles.length });
    try {
      const batch = await api.request("/footprints/imports", { method: "POST", idempotencyKey: this.pendingBatchKey,
        data: { child_id: this.data.childId, count: this.pendingFiles.length, consented: true } });
      if (!this.operationCurrent(context)) return;
      this.pendingImportId = batch.id;
      for (let index = 0; index < this.pendingFiles.length; index += 1) {
        if (!this.operationCurrent(context)) return;
        const photo = batch.photos[index];
        if (!photo.received_at) {
          const path = this.pendingFiles[index];
          const metadata = await cloudMedia.imageMetadata(path);
          if (!this.operationCurrent(context)) return;
          if (metadata.byteSize > 10 * 1024 * 1024) throw new Error("单张照片不能超过10MB，请缩小后重试");
          if (getApp().globalData.useCloud) {
            const ticket = await api.request(`/footprints/photos/${photo.id}/upload-ticket?${this.params()}`, { method: "POST" });
            if (!this.operationCurrent(context)) return;
            const fileId = await cloudMedia.uploadObject(path, ticket.cloud_path);
            if (!this.operationCurrent(context)) return;
            await api.request(`/footprints/photos/${photo.id}/claim?${this.params()}`, { method: "POST", data: { file_id: fileId } });
          } else await api.uploadFootprint(photo.id, this.data.childId, path);
        }
        if (this.operationCurrent(context)) this.setData({ importCompleted: index + 1,
          importProgress: Math.round((index + 1) / this.pendingFiles.length * 100) });
      }
      if (!this.operationCurrent(context)) return;
      this.pendingFiles = null;
      this.setData({ saving: false, hasPendingUpload: false, sheet: "review" });
      if (!this.hidden) await this.openDrafts();
    } catch (error) { if (this.operationCurrent(context)) {
      this.setData({ saving: false, sheet: "upload-error", sheetError: error.message });
    } }
    finally {
      this.uploading = false;
      if (this.operationCurrent(context)) this.setData({ saving: false });
    }
  },
  async openDrafts(preserveError = false, preserveSelection = false) {
    if (!this.data.canWrite || this.data.saving) return;
    const seq = this.sequence;
    this.pausePlayback();
    const chosen = new Set(preserveSelection ? this.data.drafts.filter(photo => photo.selected).map(photo => photo.id) : []);
    const size = preserveSelection ? Math.min(100, Math.max(20, this.data.drafts.length)) : 20;
    const confirm = preserveSelection && this.data.sheet === "confirm";
    this.draftPaging = false; this.releasePreviews();
    this.setData({ sheet: "review", sheetError: preserveError ? this.data.sheetError : "" });
    try {
      let items = [], cursor = null;
      do {
        const result = await api.request(`/footprints/drafts?${this.params({ cursor })}`);
        if (this.stale(seq) || this.data.sheet !== "review") return;
        items = [...items, ...result.items]; cursor = result.next_cursor;
      } while (cursor && items.length < size);
      this.setDrafts(this.decorateDrafts(items).map(photo => ({ ...photo, selected: chosen.has(photo.id) })), cursor);
      if (confirm && this.data.selectedCount && !this.data.missingDateCount) this.askConfirm();
      this.fillPreviews(items, "drafts", seq);
      this.pollDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  setDrafts(drafts, cursor = this.data.draftsCursor) {
    const selected = drafts.filter(photo => photo.selected);
    this.setData({ drafts, draftsCursor: cursor, selectedCount: selected.length,
      missingDateCount: selected.filter(photo => !photo.local_date).length });
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
      this.setDrafts(drafts, result.next_cursor);
      this.fillPreviews(drafts.filter((photo) => !photo.previewUrl), "drafts", seq);
      this.pollDrafts();
    } catch (error) { if (!this.stale(seq)) { this.setData({ sheetError: error.message }); this.pollDrafts(); } }
  },
  async moreDrafts() {
    if (!this.data.draftsCursor || this.data.saving) return;
    if (this.data.drafts.length >= 100) return this.setData({ sheetError: "请先整理当前照片，再读取下一页" });
    const seq = this.sequence;
    this.draftPaging = true;
    if (this.pollTimer) clearTimeout(this.pollTimer);
    try {
      const result = await api.request(`/footprints/drafts?${this.params({ cursor: this.data.draftsCursor })}`);
      if (!this.stale(seq) && this.data.sheet === "review") this.setDrafts([...this.data.drafts, ...this.decorateDrafts(result.items)], result.next_cursor);
      if (!this.stale(seq)) this.fillPreviews(result.items, "drafts", seq);
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  selectDraft(event) {
    if (this.data.saving) return;
    const id = event.currentTarget.dataset.id;
    const drafts = this.data.drafts.map((photo) => photo.id === id ? { ...photo, selected: !photo.selected } : photo);
    if (drafts.filter((photo) => photo.selected).length > 20) return this.setData({ sheetError: "每次最多确认20条，可分批继续" });
    this.setDrafts(drafts);
  },
  selectAll() {
    if (this.data.saving) return;
    const selected = !this.data.selectedCount;
    const drafts = this.data.drafts.map((photo, index) => ({ ...photo, selected: selected && index < 20 }));
    this.setDrafts(drafts);
  },
  askConfirm() {
    if (this.data.saving) return;
    const selected = this.data.drafts.filter((photo) => photo.selected);
    if (!selected.length) return this.setData({ sheetError: "请先选择要入档的照片" });
    if (selected.some(photo => !photo.local_date)) return this.batchEdit(true);
    if (selected.some(photo => !photo.has_display && !photo.is_manual))
      return this.setData({ sheetError: "请等待照片处理完成，或先取消选择处理失败的照片" });
    this.setData({ sheet: "confirm", sheetError: "", confirmCount: selected.length,
      unlocatedCount: selected.filter((photo) => photo.latitude === null || photo.latitude === undefined).length });
  },
  async confirmSelected() {
    if (this.data.saving) return;
    const context = this.operationContext();
    this.setData({ saving: true, sheetError: "" });
    try {
      const batches = {};
      this.data.drafts.filter((photo) => photo.selected).forEach((photo) => {
        (batches[photo.import_id] ||= []).push({ id: photo.id, version: photo.version });
      });
      for (const [id, selected] of Object.entries(batches)) {
        if (!this.operationCurrent(context)) return;
        await api.request(`/footprints/imports/${id}/confirm?${this.params()}`, { method: "POST",
          data: { photos: selected, confirm_actual_visit: true } });
        if (!this.operationCurrent(context)) return;
        const done = new Set(selected.map(photo => photo.id));
        this.setDrafts(this.data.drafts.filter(photo => !done.has(photo.id)));
        this.setData({ confirmCount: this.data.selectedCount });
      }
      if (!this.operationCurrent(context)) return;
      this.setData({ saving: false, sheet: "", selectedCount: 0, missingDateCount: 0 });
      wx.showToast({ title: "已入档", icon: "success" });
      if (!this.hidden) await this.refresh();
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, sheetError: error.message + "；已成功的条目保留，请返回核对后继续" }); }
  },
  backToReview() { return this.openDrafts(false, true); },
  openSettings() { this.setData({ sheet: "settings", sheetError: "" }); },
  async saveSettings() {
    if (this.data.saving) return;
    const context = this.operationContext(), seq = this.sequence;
    this.setData({ saving: true, sheetError: "" });
    try {
      await api.request("/footprints/preferences", { method: "PATCH", data: { ai_enabled: this.data.aiEnabled, consented: true } });
      if (this.operationCurrent(context)) {
        this.setData({ saving: false, sheet: "" });
        if (!this.hidden && seq !== this.sequence) await this.load();
      }
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, sheetError: error.message }); }
  }
};
