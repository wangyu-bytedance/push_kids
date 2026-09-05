const api = require("../../utils/api");
const { stateLabel } = require("../../utils/view-state");

const emptyFilters = () => ({ q: "", subject_id: "", source: "", from: "", to: "", cancelled: false });
function day(iso) { return new Date(new Date(iso).getTime() + 8 * 3600000).toISOString().slice(0, 10); }
function query(filters) {
  return Object.entries(filters).filter(([, value]) => value !== "" && value !== false && value !== null && value !== undefined)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`).join("&");
}

module.exports = {
  data: {
    recordView: "new", historyView: "confirmed", historyItems: [], historyLoading: false,
    historyError: "", historyFilters: emptyFilters(), filterDraft: emptyFilters(),
    filterOpen: false, searchText: "", filterSubjects: [], filterSubjectIndex: 0,
    historyNext: null, historyPage: 1, pendingCount: 0, pendingProcessing: false, hasFilters: false, submittedId: ""
  },
  methods: {
    async consumeRecordIntent() {
      const app = getApp();
      const intent = app.globalData.recordIntent;
      if (!intent) return;
      delete app.globalData.recordIntent;
      if (intent.childId && intent.childId !== this.data.childId) return;
      this.recordScroll = 0;
      if (intent.view === "new") { this.setData({ recordView: this.data.canWrite ? "new" : "history" }); return; }
      this.historyCursors = [null];
      this.setData({ recordView: "history", historyView: intent.status || "confirmed",
        historyFilters: { ...emptyFilters(), ...(intent.filters || {}) }, searchText: "", historyPage: 1 });
    },
    async refreshHistory() {
      await this.consumeRecordIntent();
      if (this.data.recordView === "history") return this.fetchHistory();
      const child = this.data.childId;
      try {
        const result = await api.request(`/children/${child}/history?view=pending&limit=1`);
        if (!this.hidden && child === this.data.childId) this.setData({ pendingCount: result.pending_count, pendingProcessing: result.has_processing });
      } catch (error) {
        if (error.statusCode === 401 || error.statusCode === 403) this.clearHistory();
        if (!this.hidden && child === this.data.childId) this.setData({ error: error.message });
      }
    },
    clearHistory() {
      this.historyRequest = (this.historyRequest || 0) + 1;
      this.historyCursors = [null];
      this.recordScroll = 0;
      this.setData({ historyItems: [], historyFilters: emptyFilters(), searchText: "", filterOpen: false,
        filterSubjects: [], historyNext: null, historyPage: 1, pendingCount: 0, pendingProcessing: false, submittedId: "" });
    },
    async changeRecordView(event) {
      this.setData({ recordView: this.data.canWrite === false ? "history" : event.currentTarget.dataset.view });
      if (this.data.recordView === "history") await this.fetchHistory();
    },
    async openHistoryPending() {
      this.setData({ recordView: "history", historyView: "pending", historyFilters: emptyFilters(), searchText: "" });
      await this.fetchHistory(null, 1);
    },
    async changeHistoryView(event) {
      const view = event.currentTarget.dataset.view;
      if (view === this.data.historyView) return;
      const filters = { ...this.data.historyFilters, cancelled: false };
      if ((view === "confirmed") !== (this.data.historyView === "confirmed") && (filters.from || filters.to)) {
        filters.from = ""; filters.to = "";
        wx.showToast({ title: "日期含义已切换，请重新筛选", icon: "none" });
      }
      this.setData({ historyView: view, historyFilters: filters });
      await this.fetchHistory(null, 1);
    },
    async fetchHistory(cursor, page) {
      const generation = (this.historyRequest || 0) + 1;
      this.historyRequest = generation;
      const child = this.data.childId;
      if (!child) return;
      this.historyCursors = this.historyCursors || [null];
      const targetPage = page || this.data.historyPage;
      const targetCursor = cursor === undefined ? this.historyCursors[targetPage - 1] : cursor;
      this.setData({ historyLoading: true, historyError: "" });
      try {
        const params = query({ ...this.data.historyFilters, q: "", view: this.data.historyView, cursor: targetCursor, limit: 20 });
        const result = await api.request(`/children/${child}/history?${params}`, { historyQuery: this.data.historyFilters.q });
        if (generation !== this.historyRequest || child !== this.data.childId || this.hidden) return;
        const rows = result.items.map((item) => ({ ...item,
          label: item.subject_name || (item.source === "photo" ? "照片记录" : "文字记录"),
          stateLabel: stateLabel(item.state),
          day: day(this.data.historyView === "confirmed" ? item.occurred_at : item.created_at),
          learned: day(item.occurred_at), summaryPreview: (item.summary || "尚无整理内容").slice(0, 100)
        }));
        rows.forEach((item, i) => { item.showDay = i === 0 || rows[i - 1].day !== item.day; });
        this.historyCursors = this.historyCursors.slice(0, targetPage);
        this.historyCursors[targetPage - 1] = targetCursor || null;
        if (result.next_cursor) this.historyCursors[targetPage] = result.next_cursor;
        this.setData({ historyItems: rows, historyNext: result.next_cursor, historyPage: targetPage,
          pendingCount: result.pending_count, pendingProcessing: result.has_processing, historyLoading: false,
          hasFilters: Object.values(this.data.historyFilters).some(Boolean) });
        if (page) { this.recordScroll = 0; if (wx.pageScrollTo) wx.pageScrollTo({ scrollTop: 0, duration: 0 }); }
        if (this.schedulePoll) this.schedulePoll();
      } catch (error) {
        if (generation !== this.historyRequest || child !== this.data.childId || this.hidden) return;
        if ([401, 403, 404].includes(error.statusCode)) this.clearHistory();
        this.setData({ historyLoading: false, historyError: error.message });
      }
    },
    historyNextPage() { if (!this.data.historyLoading && this.data.historyNext) return this.fetchHistory(this.data.historyNext, this.data.historyPage + 1); },
    historyPreviousPage() { if (!this.data.historyLoading && this.data.historyPage > 1) return this.fetchHistory(this.historyCursors[this.data.historyPage - 2], this.data.historyPage - 1); },
    reloadHistory() { return this.fetchHistory(null, 1); },
    setHistorySearch(event) { this.setData({ searchText: event.detail.value }); },
    searchHistory() { this.setData({ "historyFilters.q": this.data.searchText.trim() }); return this.fetchHistory(null, 1); },
    clearHistoryFilters() { this.setData({ historyFilters: emptyFilters(), searchText: "" }); return this.fetchHistory(null, 1); },
    async openHistoryFilters() {
      this.setData({ filterDraft: { ...this.data.historyFilters }, filterOpen: true, filterError: "" });
      const child = this.data.childId;
      try {
        const subjects = await api.request(`/children/${child}/subjects`);
        if (child !== this.data.childId || !this.data.filterOpen || this.hidden) return;
        const items = [{ id: "", name: "全部科目" }].concat(subjects.filter((s) => s.kind === "learning"));
        this.setData({ filterSubjects: items, filterSubjectIndex: Math.max(0, items.findIndex((s) => s.id === this.data.filterDraft.subject_id)) });
      } catch (error) { if (child === this.data.childId) this.setData({ filterError: error.message }); }
    },
    closeHistoryFilters() { this.setData({ filterOpen: false }); },
    setHistoryFilter(event) { this.setData({ [`filterDraft.${event.currentTarget.dataset.field}`]: event.detail.value }); },
    chooseHistorySubject(event) {
      const index = Number(event.detail.value);
      this.setData({ filterSubjectIndex: index, "filterDraft.subject_id": this.data.filterSubjects[index].id });
    },
    chooseHistorySource(event) { this.setData({ "filterDraft.source": event.currentTarget.dataset.source }); },
    applyHistoryFilters() {
      const filters = this.data.filterDraft;
      if (filters.from && filters.to && filters.from > filters.to) return this.setData({ filterError: "开始日期不能晚于结束日期" });
      this.setData({ historyFilters: { ...filters }, filterOpen: false });
      return this.fetchHistory(null, 1);
    },
    openHistoryItem(event) { wx.navigateTo({ url: `/pages/submission/confirm?id=${event.currentTarget.dataset.id}` }); },
    openSubmitted() { if (this.data.submittedId) wx.navigateTo({ url: `/pages/submission/confirm?id=${this.data.submittedId}` }); },
    onPageScroll(event) { this.recordScroll = event.scrollTop; },
    stopPropagation() {}
  }
};
