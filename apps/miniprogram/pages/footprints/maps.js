const api = require("../../utils/api");

module.exports = {
  async loadMap(bounds) {
    this.pausePlayback();
    const seq = this.sequence, mode = this.data.mode;
    const requestId = (this.mapRequest || 0) + 1; this.mapRequest = requestId;
    try {
      if (mode === "playback") {
        const result = await api.request(`/footprints/playback?${this.params()}`);
        if (this.stale(seq) || requestId !== this.mapRequest) return;
        this.setData({ playback: result.items, playbackIndex: 0, playbackCursor: result.next_cursor,
          playbackRevision: result.revision, mapData: { needs_conversion: result.needs_conversion || 0 }, mapError: false });
        this.focusPlayback(0); return;
      }
      const extra = { mode: bounds ? "auto" : this.data.mapMode };
      if (bounds) Object.assign(extra, { west: bounds[0], south: bounds[1], east: bounds[2], north: bounds[3] });
      const result = await api.request(`/footprints/map?${this.params(extra)}`);
      if (this.stale(seq) || requestId !== this.mapRequest) return;
      const markers = result.items.map((point) => ({ id: point.id, latitude: point.latitude, longitude: point.longitude,
        iconPath: "/assets/tab-records-active.png", width: 28, height: 28,
        callout: { content: point.label || "照片拍摄位置", display: "ALWAYS", color: "#1F5B45", fontSize: 14, padding: 8, borderRadius: 8 } }));
      const box = result.bounds;
      result.items = result.items.map((point) => ({ ...point,
        worldX: 5 + (point.longitude + 180) / 360 * 90,
        worldY: 18 + (90 - point.latitude) / 180 * 62 }));
      this.setData({ mapData: result, markers, mapLatitude: (box[1] + box[3]) / 2,
        mapLongitude: (box[0] + box[2]) / 2, mapScale: this.scaleFor(box), mapError: false });
    } catch (error) { if (!this.stale(seq) && requestId === this.mapRequest) this.setData({ mapError: true, error: error.message }); }
  },
  scaleFor(box) { return Math.max(3, Math.min(17, Math.floor(Math.log2(360 / Math.max(box[2] - box[0], box[3] - box[1], .002))) + 1)); },
  async mapScope(event) { this.setData({ mapMode: event.currentTarget.dataset.scope }); await this.loadMap(); },
  async mapTap(event) {
    if (this.data.mode === "playback") return;
    const point = (this.data.mapData.items || []).find((item) => item.id === Number(event.detail.markerId));
    if (!point) return;
    if (!point.place_key) { this.setData({ mapMode: "auto" }); return this.loadMap(point.bounds); }
    const seq = this.sequence;
    try {
      const result = await api.request(`/footprints/visits?${this.params({ place: point.place_key })}`);
      if (!this.stale(seq)) this.setData({ sheet: "place", placeVisits: result.items, placeCursor: result.next_cursor,
        placeKey: point.place_key, sheetError: "", loadingPlaceMore: false, placeWindow: 0, placeScrollTarget: "" });
    } catch (error) { if (!this.stale(seq)) this.setData({ error: error.message }); }
  },
  worldPointTap(event) { return this.mapTap({ detail: { markerId: event.currentTarget.dataset.id } }); },
  mapRegionChange(event) {
    if ((event.type !== "end" && (event.detail || {}).type !== "end") || !["drag", "scale", "gesture"].includes(event.causedBy || (event.detail || {}).causedBy) || this.data.mode !== "lit") return;
    const seq = this.sequence;
    if (!wx.createMapContext) return;
    wx.createMapContext("footprint-map", this).getRegion({ success: (region) => {
      if (!this.stale(seq)) this.loadMap([region.southwest.longitude, region.southwest.latitude,
        region.northeast.longitude, region.northeast.latitude]);
    } });
  },
  async morePlaceVisits() {
    if (!this.data.placeCursor || this.data.loadingPlaceMore || this.data.sheet !== "place") return;
    const seq = this.sequence, place = this.data.placeKey, replace = this.data.placeVisits.length >= 100;
    this.setData({ loadingPlaceMore: true, sheetError: "" });
    try {
      const result = await api.request(`/footprints/visits?${this.params({ place, cursor: this.data.placeCursor,
        limit: replace ? 20 : Math.min(20, 100 - this.data.placeVisits.length) })}`);
      if (this.stale(seq) || this.data.sheet !== "place" || place !== this.data.placeKey) return;
      const window = this.data.placeWindow + 1;
      this.setData({ placeVisits: replace ? result.items : [...this.data.placeVisits, ...result.items],
        placeCursor: result.next_cursor, loadingPlaceMore: false,
        ...(replace ? { placeWindow: window, placeScrollTarget: `fp-place-start-${window}` } : {}) });
    } catch (error) {
      if (!this.stale(seq) && this.data.sheet === "place" && place === this.data.placeKey)
        this.setData({ sheetError: error.message, loadingPlaceMore: false });
    }
  },
  mapFailed() { this.pausePlayback(); this.setData({ mapError: true, error: "地图暂时无法显示，仍可通过时间线查看所有回忆" }); },
  focusPlayback(index) {
    const point = this.data.playback[index];
    if (!point) return this.setData({ currentPoint: null, markers: [], polyline: [] });
    // Each step changes the actual native map camera, including overseas steps.
    const previous = this.data.playback[Math.max(0, index - 1)];
    this.setData({ playbackIndex: index, currentPoint: point, mapLatitude: point.latitude,
      mapLongitude: point.longitude, mapScale: 10,
      markers: [{ id: 1, latitude: point.latitude, longitude: point.longitude,
        iconPath: "/assets/tab-records-active.png", width: 32, height: 32 }],
      polyline: index ? [{ points: [previous, point].map((item) => ({ latitude: item.latitude, longitude: item.longitude })),
        color: "#1F5B45", width: 2, dottedLine: true }] : [] });
  },
  pausePlayback() { if (this.playTimer) clearTimeout(this.playTimer); this.playTimer = null; this.setData({ playing: false }); },
  togglePlayback() {
    if (this.data.playing) return this.pausePlayback();
    if (!this.data.playback.length) return;
    if (this.data.playbackIndex >= this.data.playback.length - 1) this.focusPlayback(0);
    this.setData({ playing: true }); this.schedulePlayback();
  },
  schedulePlayback() {
    if (!this.data.playing || this.hidden) return;
    this.playTimer = setTimeout(() => {
      const next = this.data.playbackIndex + 1;
      if (next >= this.data.playback.length) return this.pausePlayback();
      this.focusPlayback(next); this.schedulePlayback();
    }, 2200);
  },
  seekPlayback(event) { this.pausePlayback(); this.focusPlayback(Number(event.detail.value)); },
  async nextPlaybackPage() {
    if (!this.data.playbackCursor) return;
    this.pausePlayback(); const seq = this.sequence;
    try {
      const result = await api.request(`/footprints/playback?${this.params({ cursor: this.data.playbackCursor, revision: this.data.playbackRevision })}`);
      if (this.stale(seq)) return;
      this.setData({ playback: result.items, playbackCursor: result.next_cursor }); this.focusPlayback(0);
    } catch (error) { if (!this.stale(seq)) this.setData({ error: error.message }); }
  }
};
