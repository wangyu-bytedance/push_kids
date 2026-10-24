const api = require("../../utils/api");
const { photoView, query } = require("./presentation");
const imports = require("./imports");
const photos = require("./photos");
const maps = require("./maps");

module.exports = function createController() { return {
  data: {
    loading: true, error: "", children: [], childId: "", childIndex: 0, child: null,
    archivedVisible: false, allChildren: [], hasArchivedChildren: false, canWrite: true, mode: "timeline",
    visits: [], nextCursor: null, summary: {}, loadingMore: false,
    drafts: [], draftsCursor: null, selectedCount: 0, sheet: "", sheetError: "", saving: false,
    aiEnabled: false, consented: false, photoConsent: false, importProgress: 0, hasPendingUpload: false,
    form: {}, editing: null, batchEdit: false, manual: false, placeResults: [],
    markers: [], mapMode: "auto", mapLatitude: 35, mapLongitude: 104, mapScale: 4,
    mapData: {}, mapError: false, playback: [], playbackIndex: 0, playing: false,
    playbackCursor: null, playbackRevision: null, currentPoint: null, polyline: [],
    placeVisits: [], placeCursor: null, loadingPlaceMore: false, placeWindow: 0, placeScrollTarget: "",
    photoList: [], photoCursor: null, photoIndex: 0
  },
  ...imports,
  ...photos,
  ...maps,
  onLoad(options) { this.requestedChild = options && options.child_id; },
  onShow() { this.hidden = false; this.load(); },
  onHide() {
    this.hidden = true; this.sequence = (this.sequence || 0) + 1;
    this.pausePlayback();
    if (this.pollTimer) clearTimeout(this.pollTimer);
    this.releasePreviews();
    this.setData({ loadingMore: false, loadingPlaceMore: false });
    if (!this.uploading) this.setData({ saving: false });
  },
  onUnload() { this.disposed = true; this.onHide(); },
  async onPullDownRefresh() { await this.load(); wx.stopPullDownRefresh(); },
  async onReachBottom() {
    if (!this.data.sheet && this.data.mode === "timeline" && this.data.visits.length < 100) await this.moreVisits();
  },
  async load() {
    const seq = (this.sequence || 0) + 1; this.sequence = seq;
    this.setData({ loading: true, error: "", loadingMore: false });
    try {
      const [profiles, preferences] = await Promise.all([
        api.request("/children?include_archived=true"), api.request("/footprints/preferences")
      ]);
      if (this.stale(seq)) return;
      const member = getApp().globalData.currentMember;
      const all = profiles.map((child) => ({ ...child, label: child.name + (child.active === false ? "（已归档）" : "") }));
      const selected = this.requestedChild || this.data.childId || getApp().globalData.selectedChildId;
      const chosen = all.find((child) => child.id === selected) || all.find((child) => child.active !== false) || all[0];
      const archivedVisible = this.data.archivedVisible || Boolean(chosen && chosen.active === false);
      const children = archivedVisible ? all : all.filter((child) => child.active !== false);
      this.setData({ allChildren: all, children, child: chosen || null, childId: chosen ? chosen.id : "",
        childIndex: Math.max(0, children.findIndex((child) => chosen && child.id === chosen.id)),
        archivedVisible, hasArchivedChildren: all.some((child) => child.active === false),
        canWrite: !member || member.role !== "viewer",
        aiEnabled: preferences.ai_enabled, consented: preferences.consented });
      this.notifyContext();
      if (chosen) await this.refresh(seq);
      if (!this.stale(seq)) this.setData({ loading: false });
    } catch (error) { if (!this.stale(seq)) this.handleError(error); }
  },
  stale(seq) { return this.hidden || seq !== this.sequence; },
  notifyContext() {
    if (this.data.embedded && this.triggerEvent) this.triggerEvent("contextchange", {
      children: this.data.children, childIndex: this.data.childIndex, child: this.data.child
    });
  },
  params(extra = {}) { return query({ child_id: this.data.childId, ...extra }); },
  async refresh(seq = this.sequence) {
    const [summary, visits] = await Promise.all([
      api.request(`/footprints/summary?${this.params()}`),
      api.request(`/footprints/visits?${this.params()}`)
    ]);
    if (this.stale(seq)) return;
    this.releasePreviews();
    this.setData({ summary, visits: visits.items, nextCursor: visits.next_cursor });
    this.fillPreviews(visits.items.flatMap((visit) => visit.photos), "visits", seq);
    if (this.data.mode !== "timeline") await this.loadMap();
  },
  handleError(error) {
    const denied = [401, 403, 404].includes(error.statusCode);
    this.setData({ loading: false, saving: false, loadingMore: false, error: error.message,
      ...(denied ? { visits: [], markers: [], drafts: [], childId: "", child: null, sheet: "" } : {}) });
    if (denied) { this.pausePlayback(); this.releasePreviews(); }
    if (denied) { this.setData({ children: [], allChildren: [], hasArchivedChildren: false }); this.notifyContext(); }
  },
  async moreVisits() {
    if (!this.data.nextCursor || this.data.loading || this.data.loadingMore || this.data.sheet || this.data.mode !== "timeline") return;
    const replace = this.data.visits.length >= 100;
    const seq = this.sequence; this.setData({ loadingMore: true });
    try {
      const result = await api.request(`/footprints/visits?${this.params({ cursor: this.data.nextCursor,
        limit: replace ? 20 : Math.min(20, 100 - this.data.visits.length) })}`);
      if (this.stale(seq)) return;
      // A response from the timeline must not reclaim a photo sheet's previews.
      // Keep this cursor retryable when the user has moved into another context.
      if (this.data.sheet || this.data.mode !== "timeline") return this.setData({ loadingMore: false });
      if (replace) this.releasePreviews();
      this.setData({ visits: replace ? result.items : [...this.data.visits, ...result.items], nextCursor: result.next_cursor, loadingMore: false });
      if (replace) this.scrollTimelineStart(seq);
      this.fillPreviews(result.items.flatMap((visit) => visit.photos), "visits", seq);
    } catch (error) {
      if (this.stale(seq)) return;
      if (this.data.sheet || this.data.mode !== "timeline") this.setData({ loadingMore: false });
      else this.handleError(error);
    }
  },
  scrollTimelineStart(seq) {
    if (!wx.createSelectorQuery || !wx.pageScrollTo) return;
    const query = wx.createSelectorQuery().in(this);
    query.select(".fp-timeline").boundingClientRect();
    query.selectViewport().scrollOffset();
    query.exec(([rect, viewport]) => {
      if (!this.stale(seq) && this.data.mode === "timeline" && rect && viewport)
        wx.pageScrollTo({ scrollTop: Math.max(0, rect.top + viewport.scrollTop), duration: 0 });
    });
  },
  async changeChild(event, children = this.data.children) {
    const index = Number(event.detail.value), child = children[index], seq = this.sequence;
    if (this.data.saving || !child) return;
    if (!(await this.allowDiscard()) || this.stale(seq)) return;
    this.pendingFiles = null;
    this.setData({ hasPendingUpload: false });
    this.onHide(); this.hidden = false;
    this.setData({ children, archivedVisible: this.data.archivedVisible || child.active === false,
      childIndex: index, childId: child.id, child, sheet: "", visits: [], drafts: [], markers: [] });
    this.requestedChild = child.id;
    await this.load();
  },
  chooseFootprintAction(items) {
    return new Promise((resolve) => wx.showActionSheet({ itemList: items,
      success: ({ tapIndex }) => resolve(tapIndex), fail: () => resolve(null) }));
  },
  async openFootprintActions() {
    if (this.nativeMenuOpen || this.data.saving || this.uploading || this.data.sheet || this.hidden) return;
    this.nativeMenuOpen = true;
    const seq = this.sequence, actions = [];
    if (this.data.canWrite) actions.push("足迹设置");
    if (this.data.allChildren.some((child) => child.active === false)) actions.push("已归档孩子");
    try {
      const index = actions.length === 1 ? 0 : actions.length ? await this.chooseFootprintAction(actions) : null;
      if (index === null || this.stale(seq) || this.data.sheet) return;
      if (actions[index] === "足迹设置") this.openSettings();
      else if (actions[index] === "已归档孩子") await this.showArchived();
    } finally { this.nativeMenuOpen = false; }
  },
  async showArchived() {
    if (this.archivePickerOpen || this.data.saving || this.uploading || this.hidden) return;
    const children = this.data.allChildren.filter((child) => child.active === false), seq = this.sequence;
    if (!children.length) return;
    this.archivePickerOpen = true;
    try {
      // Leave room for both page controls; every archive remains reachable.
      let offset = 0;
      while (!this.stale(seq)) {
        const rows = children.slice(offset, offset + 4), items = rows.map((child) => child.name);
        const previous = offset > 0 ? items.push("上一页") - 1 : -1;
        const next = offset + rows.length < children.length ? items.push("下一页") - 1 : -1;
        const index = await this.chooseFootprintAction(items);
        if (index === null || this.stale(seq)) return;
        if (index === previous) offset -= 4;
        else if (index === next) offset += 4;
        else if (rows[index]) return await this.changeChild({ detail: { value: this.data.allChildren.findIndex((child) => child.id === rows[index].id) } }, this.data.allChildren);
        else return;
      }
    } finally { this.archivePickerOpen = false; }
  },
  async changeMode(event) {
    this.pausePlayback();
    this.setData({ mode: event.currentTarget.dataset.mode, mapError: false });
    if (this.data.mode !== "timeline") await this.loadMap();
  },
  async closeSheet() {
    if (this.data.saving) return;
    if (!(await this.allowDiscard())) return;
    this.setData({ sheet: "", sheetError: "", editing: null, placeResults: [] });
    if (this.pollTimer) clearTimeout(this.pollTimer);
    await this.load();
  },
  async allowDiscard() {
    if (this.data.sheet !== "edit") return true;
    return new Promise((resolve) => wx.showModal({ title: "放弃未保存的修改？",
      content: "未保存的修改将丢失。", confirmText: "放弃修改",
      success: (result) => resolve(result.confirm), fail: () => resolve(false) }));
  },
  noop() {},
  releasePreviews() {
    this.previewSequence = (this.previewSequence || 0) + 1;
    (this.previewFiles || []).forEach(api.removePreview); this.previewFiles = [];
  },
  async fillPreviews(items, region, seq = this.sequence) {
    const generation = this.previewSequence || 0;
    const obsolete = () => this.stale(seq) || generation !== (this.previewSequence || 0);
    // Serial, bounded capability requests; no original image or GPS in client storage.
    for (const item of items.slice(0, 80)) {
      if (obsolete()) return;
      if (!item.has_display) continue;
      try {
        const capability = await api.request(`/footprints/photos/${item.id}/preview?${this.params({ size: "thumbnail" })}`);
        if (obsolete()) return;
        const url = await api.downloadPreview(capability);
        if (obsolete()) { api.removePreview(url); return; }
        this.previewFiles = [...(this.previewFiles || []), url];
        if (region === "visits") {
          const visits = this.data.visits.map((visit) => ({ ...visit, photos: visit.photos.map((photo) => photo.id === item.id ? { ...photo, previewUrl: url } : photo) }));
          this.setData({ visits });
        } else {
          this.setData({ [region]: this.data[region].map((photo) => photo.id === item.id ? { ...photo, previewUrl: url } : photo) });
        }
      } catch { /* The dated/place list remains usable if a thumbnail is unavailable. */ }
    }
  },
  decorateDrafts(rows) { return rows.map(photoView); }
}; };
