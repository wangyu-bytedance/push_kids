const api = require("../../utils/api");
const ui = require("../../utils/ui");
const { stateLabel } = require("../../utils/view-state");
const { localParts } = require("../../utils/date");

const emptyFilters = () => ({ q: "", subject_id: "", source: "", from: "", to: "", cancelled: false });
function day(iso) { return new Date(new Date(iso).getTime() + 8 * 3600000).toISOString().slice(0, 10); }
function query(filters) {
  return Object.entries(filters).filter(([, value]) => value !== "" && value !== false && value !== null && value !== undefined)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`).join("&");
}

/* 状态色只表达「这条提交走到哪一步」，不表达任何学习评价。 */
const STATE_TONE = { confirmed: "suc", pending_confirmation: "att", failed: "dan", analyzing: "info", queued: "neutral", cancelled: "neutral" };

function dayLabel(value, today, yesterday) {
  if (value === today) return `今天 · ${ui.monthDay(value)}`;
  if (value === yesterday) return `昨天 · ${ui.monthDay(value)}`;
  return ui.monthDay(value);
}

/* WXML 不支持方法调用，列表卡片的展示字段全部在这里算好。 */
function rowView(item, view) {
  const name = item.subject_name || "";
  const label = name || (item.source === "photo" ? "照片记录" : "文字记录");
  return {
    ...item,
    label,
    mark: ui.subjectMark(name || label),
    markClass: ui.subjectClass(name, item.subject_kind),
    stateLabel: stateLabel(item.state),
    stateTone: STATE_TONE[item.state] || "neutral",
    isPending: item.state !== "confirmed" && item.state !== "cancelled",
    working: item.state === "queued" || item.state === "analyzing",
    sourceLabel: item.source === "photo" ? `照片 ${item.media_count || 0} 张` : "文字记录",
    knowledgeLabel: item.record_id ? `${item.knowledge_count || 0} 个知识点` : "",
    day: day(view === "confirmed" ? item.occurred_at : item.created_at),
    dayText: "",
    learned: day(item.occurred_at),
    learnedText: `学习于 ${ui.monthDay(day(item.occurred_at))}`,
    summaryPreview: (item.summary || "尚无整理内容").slice(0, 100)
  };
}

module.exports = {
  data: {
    recordView: "new", historyView: "confirmed", historyItems: [], historyLoading: false,
    historyError: "", historyFilters: emptyFilters(), filterDraft: emptyFilters(),
    filterOpen: false, searchText: "", filterSubjects: [], filterSubjectIndex: 0,
    historyNext: null, historyPage: 1, pendingCount: 0, pendingProcessing: false, hasFilters: false, submittedId: "",
    filterError: "", sourceOptions: [{ value: "", label: "全部" }, { value: "photo", label: "照片" }, { value: "text", label: "文字" }]
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
        if (!this.hidden && child === this.data.childId) this.setData({
          pendingCount: Number(result.pending_count || 0),
          pendingProcessing: Boolean(result.has_processing)
        });
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
    /* 筛选条件按孩子记忆，纯界面偏好，读写失败一律回落到「不筛选」。 */
    restoreFilters(childId) {
      const saved = ui.readPreference("recordFilters", childId, null) || {};
      const filters = { ...emptyFilters(), ...saved };
      this.setData({ historyFilters: filters, searchText: filters.q || "",
        hasFilters: Object.values(filters).some(Boolean) });
    },
    rememberFilters() {
      ui.writePreference("recordFilters", this.data.childId, this.data.historyFilters);
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
        const today = localParts().date;
        const yesterday = localParts(new Date(Date.now() - 86400000)).date;
        const rows = result.items.map((item) => rowView(item, this.data.historyView));
        rows.forEach((item, i) => {
          item.showDay = i === 0 || rows[i - 1].day !== item.day;
          item.dayText = dayLabel(item.day, today, yesterday);
        });
        this.historyCursors = this.historyCursors.slice(0, targetPage);
        this.historyCursors[targetPage - 1] = targetCursor || null;
        if (result.next_cursor) this.historyCursors[targetPage] = result.next_cursor;
        this.setData({ historyItems: rows, historyNext: result.next_cursor, historyPage: targetPage,
          pendingCount: result.pending_count, pendingProcessing: result.has_processing, historyLoading: false,
          hasFilters: Object.values(this.data.historyFilters).some(Boolean) });
        /* 记录页拿到的待处理数最新，顺手把 TabBar 徽标对齐，避免和今日页不一致。 */
        const app = typeof getApp === "function" && getApp();
        if (app && app.setTabBadge) app.setTabBadge("records", result.pending_count);
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
    searchHistory() { this.setData({ "historyFilters.q": this.data.searchText.trim() }); this.rememberFilters(); return this.fetchHistory(null, 1); },
    clearHistoryFilters() {
      this.setData({ historyFilters: emptyFilters(), searchText: "", filterOpen: false });
      this.rememberFilters();
      return this.fetchHistory(null, 1);
    },
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
    resetHistoryFilters() { this.setData({ filterDraft: emptyFilters(), filterSubjectIndex: 0, filterError: "" }); },
    applyHistoryFilters() {
      const filters = this.data.filterDraft;
      if (filters.from && filters.to && filters.from > filters.to) return this.setData({ filterError: "开始日期不能晚于结束日期" });
      this.setData({ historyFilters: { ...filters }, searchText: filters.q || this.data.searchText, filterOpen: false });
      this.rememberFilters();
      return this.fetchHistory(null, 1);
    },
    /* 列表只负责跳详情：入档与确认都发生在详情 / 确认页。 */
    openHistoryItem(event) { wx.navigateTo({ url: `/pages/record-detail/index?id=${event.currentTarget.dataset.id}` }); },
    openSubmitted() { if (this.data.submittedId) wx.navigateTo({ url: `/pages/record-detail/index?id=${this.data.submittedId}` }); },
    onPageScroll(event) { this.recordScroll = event.scrollTop; },
    stopPropagation() {}
  }
};
