const api = require("../../utils/api");
const { editValues, correction, photoView } = require("./presentation");

module.exports = {
  editDraft(event) {
    const photo = this.data.drafts.find((item) => item.id === event.currentTarget.dataset.id);
    if (!photo) return;
    if (this.pollTimer) clearTimeout(this.pollTimer);
    this.setData({ sheet: "edit", editing: photo, batchEdit: false, manual: false,
      form: editValues(photo), placeResults: photo.candidates || [], sheetError: "", returnSheet: "review" });
  },
  batchEdit() {
    if (!this.data.selectedCount) return this.setData({ sheetError: "请先选择要修改的照片" });
    this.setData({ sheet: "edit", editing: null, batchEdit: true, manual: false,
      form: editValues({}), placeResults: [], sheetError: "", returnSheet: "review" });
  },
  manualEntry() {
    if (!this.data.canWrite || !this.data.child || this.data.child.active === false) return;
    this.manualKey = api.newIdempotencyKey("footprint-manual");
    this.setData({ sheet: "edit", editing: null, batchEdit: false, manual: true,
      form: editValues({}), sheetError: "", placeResults: [], returnSheet: "" });
  },
  editField(event) {
    if (this.data.saving) return;
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const form = { ...this.data.form, [field]: value };
    if (field === "day_order") form.orderTouched = true;
    if (field === "place_name") Object.assign(form, { latitude: null, longitude: null, coordinate_system: null, precision: "unknown" });
    if (["local_date", "local_time"].includes(field)) form.offset_minutes = null;
    this.setData({ form });
  },
  clearCaptureField(event) {
    const field = event.currentTarget.dataset.field;
    if (this.data.saving || !["local_date", "local_time"].includes(field)) return;
    if (field === "local_date" && (this.data.manual || (this.data.editing || {}).state === "confirmed")) return;
    this.setData({ form: { ...this.data.form, [field]: "", offset_minutes: null } });
  },
  chooseCandidate(event) {
    const candidate = this.data.placeResults[Number(event.currentTarget.dataset.index)];
    if (candidate) this.setData({ form: { ...this.data.form, ...candidate }, placeResults: [] });
  },
  async searchPlaces() {
    const seq = this.sequence, form = this.data.form;
    if (!form.place_name || !(form.city || form.country)) return this.setData({ sheetError: "请填写地点名和所在城市或国家后查找" });
    try {
      const result = await api.request(`/footprints/places/search?${this.params({ keyword: form.place_name, region: form.city || form.country })}`);
      if (!this.stale(seq)) this.setData({ placeResults: result.items, sheetError: result.items.length ? "" : "暂未找到候选，可保留文字地点或在地图选点" });
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  choosePlace() {
    if (!wx.chooseLocation) return this.setData({ sheetError: "当前微信无法选点，请填写地点名称" });
    const seq = this.sequence;
    wx.chooseLocation({ latitude: this.data.form.coordinate_system === "gcj02" ? this.data.form.latitude : 35,
      longitude: this.data.form.coordinate_system === "gcj02" ? this.data.form.longitude : 104,
      success: (place) => {
        if (this.stale(seq)) return;
        this.setData({ form: { ...this.data.form, place_name: place.name || place.address,
          latitude: place.latitude, longitude: place.longitude, coordinate_system: "gcj02", precision: "poi" }, sheetError: "" });
      }, fail: () => { if (!this.stale(seq)) this.setData({ sheetError: "未选择地点，可继续手动填写" }); }
    });
  },
  async saveEdit() {
    if (this.data.saving) return;
    if ((this.data.manual || (this.data.editing && this.data.editing.state === "confirmed")) && !this.data.form.local_date) return this.setData({ sheetError: "请填写拍摄日期" });
    const seq = this.sequence; this.setData({ saving: true, sheetError: "" });
    try {
      const values = correction(this.data.form, this.data.batchEdit);
      if (this.data.manual) {
        await api.request("/footprints/manual", { method: "POST", idempotencyKey: this.manualKey,
          data: { child_id: this.data.childId, ...values } });
      } else {
        const selected = this.data.batchEdit ? this.data.drafts.filter((photo) => photo.selected) : [this.data.editing];
        for (const photo of selected) await api.request(`/footprints/photos/${photo.id}?${this.params()}`, {
          method: "PATCH", data: { version: photo.version, ...values }
        });
      }
      if (this.stale(seq)) return;
      const formal = this.data.editing && this.data.editing.state === "confirmed";
      this.setData({ saving: false, sheet: "", editing: null });
      if (formal) await this.refresh(seq);
      else await this.openDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ saving: false, sheetError: error.message }); }
  },
  async deletePhoto() {
    if (!this.data.editing || this.data.saving) return;
    const photo = this.data.editing;
    const confirmed = await new Promise((resolve) => wx.showModal({ title: "删除这张照片？",
      content: "删除后无法恢复，其他照片保留。",
      confirmText: "删除照片", success: (result) => resolve(result.confirm), fail: () => resolve(false) }));
    if (!confirmed) return;
    const seq = this.sequence; this.setData({ saving: true, sheetError: "" });
    try {
      await api.request(`/footprints/photos/${photo.id}?${this.params({ version: photo.version })}`, { method: "DELETE" });
      if (this.stale(seq)) return;
      this.setData({ saving: false, sheet: "", editing: null });
      if (photo.state === "confirmed") await this.refresh(seq); else await this.openDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ saving: false, sheetError: error.message }); }
  },
  async retryPhoto(event) {
    const photo = this.data.drafts.find((item) => item.id === event.currentTarget.dataset.id);
    const seq = this.sequence;
    try {
      await api.request(`/footprints/photos/${photo.id}/retry?${this.params({ version: photo.version })}`, { method: "POST" });
      if (!this.stale(seq)) await this.openDrafts();
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  async openVisit(event) {
    const id = event.currentTarget.dataset.id;
    const seq = this.sequence; this.pausePlayback();
    this.setData({ sheet: "photo", sheetError: "", photoList: [], photoIndex: 0 });
    try {
      const result = await api.request(`/footprints/visits/${id}/photos?${this.params()}`);
      if (this.stale(seq)) return;
      const photoList = result.items.map(photoView);
      this.photoPageCursors = [null]; this.photoPage = 0;
      this.setData({ photoList, photoCursor: result.next_cursor, photoVisitId: id, hasPreviousPhotoPage: false,
        editing: photoList[0] || null });
      this.fillPreviews(result.items, "photoList", seq);
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  async nextPhoto(event) {
    let index = this.data.photoIndex + Number(event.currentTarget.dataset.delta);
    const seq = this.sequence;
    try {
      if ((index >= this.data.photoList.length && this.data.photoCursor) || (index < 0 && this.photoPage > 0)) {
        const forward = index >= this.data.photoList.length;
        const page = this.photoPage + (forward ? 1 : -1);
        const cursor = forward ? this.data.photoCursor : this.photoPageCursors[page];
        const result = await api.request(`/footprints/visits/${this.data.photoVisitId}/photos?${this.params({ cursor })}`);
        if (this.stale(seq)) return;
        this.photoPageCursors[page] = cursor; this.photoPage = page;
        this.releasePreviews();
        this.setData({ photoList: result.items.map(photoView), photoCursor: result.next_cursor, hasPreviousPhotoPage: page > 0 });
        index = forward ? 0 : result.items.length - 1;
        this.fillPreviews(result.items, "photoList", seq);
      }
      if (index < 0) return;
      index = Math.min(index, this.data.photoList.length - 1);
      this.setData({ photoIndex: index, editing: this.data.photoList[index] });
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  },
  editFormal() {
    const photo = this.data.photoList[this.data.photoIndex];
    if (!photo || !this.data.canWrite) return;
    this.setData({ sheet: "edit", editing: photo, form: { ...editValues(photo),
      day_order: photo.day_order || 0, order_revision: photo.order_revision }, manual: false,
      batchEdit: false, placeResults: [], sheetError: "", returnSheet: "photo" });
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
      wx.previewImage({ urls: [url], current: url });
    } catch (error) { if (!this.stale(seq)) this.setData({ sheetError: error.message }); }
  }
};
