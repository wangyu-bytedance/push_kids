const api = require("../../utils/api");
const { editValues, correction, photoView } = require("./presentation");

module.exports = {
  editDraft(event) {
    if (this.data.saving || this.data.selecting) return;
    const photo = this.data.drafts.find((item) => item.id === event.currentTarget.dataset.id);
    if (!photo) return;
    if (this.pollTimer) clearTimeout(this.pollTimer);
    this.editCompleted = new Set();
    this.setData({ sheet: "edit", editing: photo, batchEdit: false, dateOnly: false, editConflict: false,
      form: editValues(photo), placeResults: photo.candidates || [], sheetError: "", returnSheet: "review" });
    this.fillPreviews([photo], "editing");
  },
  batchEdit(dateOnly = false) {
    if (this.data.saving || this.data.selecting) return;
    if (!this.data.selectedCount) return this.setData({ sheetError: "请先选择要修改的照片" });
    if (this.pollTimer) clearTimeout(this.pollTimer);
    this.editCompleted = new Set();
    this.editTargets = this.data.drafts.filter(photo => photo.selected && (dateOnly !== true || !photo.local_date)).map(photo => photo.id);
    this.setData({ sheet: "edit", editing: null, batchEdit: true, dateOnly: dateOnly === true, editConflict: false,
      form: editValues({}), placeResults: [], sheetError: "", returnSheet: "review" });
  },
  editField(event) {
    if (this.data.saving || this.data.selecting) return;
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const form = { ...this.data.form, [field]: value };
    if (field === "day_order") form.orderTouched = true;
    if (field === "place_name") Object.assign(form, { latitude: null, longitude: null, coordinate_system: null, precision: "unknown" });
    if (["local_date", "local_time"].includes(field)) form.offset_minutes = null;
    this.setData({ form });
    this.editCompleted = new Set();
  },
  clearCaptureField(event) {
    const field = event.currentTarget.dataset.field;
    if (this.data.saving || !["local_date", "local_time"].includes(field)) return;
    if (field === "local_date" && (this.data.editing || {}).state === "confirmed") return;
    this.setData({ form: { ...this.data.form, [field]: "", offset_minutes: null } });
    this.editCompleted = new Set();
  },
  chooseCandidate(event) {
    if (this.data.saving || this.data.selecting) return;
    const candidate = this.data.placeResults[Number(event.currentTarget.dataset.index)];
    if (candidate) { this.editCompleted = new Set(); this.setData({ form: { ...this.data.form, ...candidate }, placeResults: [] }); }
  },
  async searchPlaces() {
    if (this.data.saving || this.data.selecting) return;
    const seq = this.sequence, form = this.data.form;
    if (!form.place_name || !(form.city || form.country)) return this.setData({ sheetError: "请填写地点名和所在城市或国家后查找" });
    try {
      const result = await api.request(`/footprints/places/search?${this.params({ keyword: form.place_name, region: form.city || form.country })}`);
      if (!this.stale(seq) && this.data.sheet === "edit") this.setData({ placeResults: result.items, sheetError: result.items.length ? "" : "暂未找到候选，可保留文字地点或在地图选点" });
    } catch (error) { if (!this.stale(seq) && this.data.sheet === "edit") this.setData({ sheetError: error.message }); }
  },
  choosePlace() {
    if (this.data.saving || this.data.selecting) return;
    if (!wx.chooseLocation) return this.setData({ sheetError: "当前微信无法选点，请填写地点名称" });
    const context = this.operationContext();
    this.setData({ selecting: true });
    wx.chooseLocation({ latitude: this.data.form.coordinate_system === "gcj02" ? this.data.form.latitude : 35,
      longitude: this.data.form.coordinate_system === "gcj02" ? this.data.form.longitude : 104,
      success: (place) => {
        if (!this.operationCurrent(context) || this.data.sheet !== "edit") return;
        this.editCompleted = new Set();
        this.setData({ form: { ...this.data.form, place_name: place.name || place.address,
          latitude: place.latitude, longitude: place.longitude, coordinate_system: "gcj02", precision: "poi" }, sheetError: "" });
      }, fail: (error) => { if (this.operationCurrent(context) && !String(error.errMsg).includes("cancel")) this.setData({ sheetError: "未选择地点，可继续手动填写" }); },
      complete: () => { if (this.operationCurrent(context)) {
        this.setData({ selecting: false });
        if (!this.hidden && this.data.editing) this.fillPreviews([this.data.editing], "editing");
      } }
    });
  },
  async saveEdit() {
    if (this.data.saving || this.data.selecting || this.data.editConflict) return;
    if ((this.data.dateOnly || (this.data.editing && this.data.editing.state === "confirmed")) && !this.data.form.local_date) return this.setData({ sheetError: "请填写拍摄日期" });
    const context = this.operationContext(); this.setData({ saving: true, sheetError: "" });
    try {
      const values = this.data.dateOnly ? { local_date: this.data.form.local_date } : correction(this.data.form, this.data.batchEdit);
      const selected = this.data.batchEdit ? this.data.drafts.filter(photo => (this.editTargets || []).includes(photo.id)) : [this.data.editing];
      this.editCompleted ||= new Set();
      for (const photo of selected) {
        if (!this.operationCurrent(context)) return;
        if (this.editCompleted.has(photo.id)) continue;
        const updated = await api.request(`/footprints/photos/${photo.id}?${this.params()}`, {
          method: "PATCH", data: { version: photo.version, ...values }
        });
        if (!this.operationCurrent(context)) return;
        this.editCompleted.add(photo.id);
        this.setDrafts(this.data.drafts.map(row => row.id === photo.id ? { ...row, ...photoView(updated), selected: row.selected } : row));
        if (this.data.editing && this.data.editing.id === photo.id) this.setData({ editing: { ...this.data.editing, ...updated } });
      }
      if (!this.operationCurrent(context)) return;
      const formal = this.data.editing && this.data.editing.state === "confirmed";
      this.setData({ saving: false, sheet: formal ? "" : "review", editing: null, keyboardHeight: 0 });
      if (this.hidden) return;
      if (formal) await this.refresh();
      else await this.openDrafts(false, true);
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, editConflict: error.statusCode === 409, sheetError: error.message }); }
  },
  async refreshEditVersions() {
    if (this.data.saving || this.data.selecting) return;
    const context = this.operationContext(); this.setData({ saving: true });
    try {
      const ids = this.data.batchEdit ? this.editTargets : [this.data.editing.id];
      for (const id of ids.slice(0, 20)) {
        const photo = await api.request(`/footprints/photos/${id}?${this.params()}`);
        if (!this.operationCurrent(context)) return;
        this.setDrafts(this.data.drafts.map(row => row.id === id ? { ...photoView(photo), selected: row.selected } : row));
        if (this.data.editing && this.data.editing.id === id) this.setData({ editing: photoView(photo) });
      }
      if (this.operationCurrent(context)) this.setData({ saving: false, editConflict: false, sheetError: "已读取最新版本，填写内容保留，请核对后保存" });
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, sheetError: error.message }); }
  },
  async deletePhoto() {
    if (!this.data.editing || this.data.saving) return;
    const photo = this.data.editing, context = this.operationContext();
    const confirmed = await new Promise((resolve) => wx.showModal({ title: "删除这张照片？",
      content: "删除后无法恢复，其他照片保留。",
      confirmText: "删除照片", success: (result) => resolve(result.confirm), fail: () => resolve(false) }));
    if (!confirmed || !this.operationCurrent(context)) return;
    this.setData({ saving: true, sheetError: "" });
    try {
      await api.request(`/footprints/photos/${photo.id}?${this.params({ version: photo.version })}`, { method: "DELETE" });
      if (!this.operationCurrent(context)) return;
      this.setData({ saving: false, sheet: "", editing: null });
      if (this.hidden) return;
      if (photo.state === "confirmed") await this.refresh(); else await this.openDrafts(false, true);
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, sheetError: error.message }); }
  },
  async retryPhoto(event) {
    if (this.data.saving) return;
    const photo = this.data.drafts.find((item) => item.id === event.currentTarget.dataset.id);
    if (!photo) return;
    const context = this.operationContext(); this.setData({ saving: true });
    try {
      await api.request(`/footprints/photos/${photo.id}/retry?${this.params({ version: photo.version })}`, { method: "POST" });
      if (!this.operationCurrent(context)) return;
      this.setData({ saving: false });
      if (!this.hidden) await this.openDrafts(false, true);
    } catch (error) { if (this.operationCurrent(context)) this.setData({ saving: false, sheetError: error.message }); }
  },
  async openVisit(event) {
    const { id, photoId } = event.currentTarget.dataset;
    const seq = this.sequence; this.pausePlayback();
    const request = this.galleryRequest = (this.galleryRequest || 0) + 1;
    this.releasePreviews();
    this.setData({ sheet: "photo", sheetError: "", photoList: [], photoIndex: 0, photoVisitId: id, loadingPhoto: true });
    try {
      const result = await api.request(`/footprints/visits/${id}/photos?${this.params({ focus_photo_id: photoId })}`);
      if (this.stale(seq) || this.data.sheet !== "photo" || request !== this.galleryRequest) return;
      const photoList = result.items.map(photoView);
      this.setData({ photoList, photoCursor: result.next_cursor, photoPreviousCursor: result.previous_cursor,
        hasPreviousPhotoPage: !!result.previous_cursor, loadingPhoto: false, editing: photoList[0] || null });
      this.fillPreviews(result.items, "photoList", seq);
    } catch (error) { if (!this.stale(seq) && this.data.sheet === "photo" && request === this.galleryRequest) this.setData({ loadingPhoto: false, sheetError: error.message }); }
  },
  async nextPhoto(event) {
    if (this.data.loadingPhoto) return;
    let index = this.data.photoIndex + Number(event.currentTarget.dataset.delta);
    const seq = this.sequence, request = this.galleryRequest;
    try {
      if ((index >= this.data.photoList.length && this.data.photoCursor) || (index < 0 && this.data.photoPreviousCursor)) {
        const forward = index >= this.data.photoList.length;
        const cursor = forward ? this.data.photoCursor : this.data.photoPreviousCursor;
        this.setData({ loadingPhoto: true });
        const result = await api.request(`/footprints/visits/${this.data.photoVisitId}/photos?${this.params({ cursor })}`);
        if (this.stale(seq) || this.data.sheet !== "photo" || request !== this.galleryRequest) return;
        this.releasePreviews();
        this.setData({ photoList: result.items.map(photoView), photoCursor: result.next_cursor, photoPreviousCursor: result.previous_cursor,
          hasPreviousPhotoPage: !!result.previous_cursor, loadingPhoto: false });
        index = forward ? 0 : result.items.length - 1;
        this.fillPreviews(result.items, "photoList", seq);
      }
      if (index < 0) return;
      index = Math.min(index, this.data.photoList.length - 1);
      this.setData({ photoIndex: index, editing: this.data.photoList[index] });
    } catch (error) { if (!this.stale(seq) && this.data.sheet === "photo" && request === this.galleryRequest) this.setData({ loadingPhoto: false, sheetError: error.message }); }
  },
  editFormal() {
    const photo = this.data.photoList[this.data.photoIndex];
    if (!photo || !this.data.canWrite) return;
    this.editCompleted = new Set();
    this.setData({ sheet: "edit", editing: photo, dateOnly: false, editConflict: false, form: { ...editValues(photo),
      day_order: photo.day_order || 0, order_revision: photo.order_revision },
      batchEdit: false, placeResults: [], sheetError: "", returnSheet: "photo" });
    this.fillPreviews([photo], "editing");
  },
  async previewCurrent() {
    const photo = this.data.photoList[this.data.photoIndex];
    if (!photo || !photo.has_display) return;
    const seq = this.sequence;
    try {
      const capability = await api.request(`/footprints/photos/${photo.id}/preview?${this.params()}`);
      const url = await api.downloadPreview(capability);
      if (this.stale(seq)) { api.removePreview(url); return; }
      this.previewFiles = [...(this.previewFiles || []), url];
      this.viewerFile = url;
      wx.previewImage({ urls: [url], current: url });
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  previewFailed(event) {
    const { id, region } = event.currentTarget.dataset;
    if (region === "editing" && this.data.editing && this.data.editing.id === id) this.setData({ editing: { ...this.data.editing, previewUrl: "" } });
    else if (["drafts", "photoList"].includes(region)) this.setData({ [region]: this.data[region].map(photo => photo.id === id ? { ...photo, previewUrl: "" } : photo) });
  },
  retryEditingPreview() {
    if (this.data.editing) this.fillPreviews([this.data.editing], "editing");
  }
};
