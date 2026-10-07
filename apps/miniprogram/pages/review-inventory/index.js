const api = require("../../utils/api");

function arrangementView(item) {
  const labels = {
    reviewed_today: "今日已完成", deferred_today: "今天已跳过",
    scheduled_today: "今日已安排", reserved: "家长已安排",
    not_due: "尚未到建议日", waiting: "等待安排",
    awaiting_daily_plan: "等待生成今日安排", unavailable: "暂无复习安排"
  };
  const current = Object.prototype.hasOwnProperty.call(labels, item.arrangement_state);
  const dateLabel = !current ? "计划日期" : item.scheduled_on ? "家长安排日期" : "建议复习日";
  const dateValue = !current ? item.due_date : (item.scheduled_on || item.suggested_review_on);
  return { ...item, dateText: dateValue ? `${dateLabel}：${dateValue}` : "",
    arrangementText: current ? labels[item.arrangement_state] : "安排状态待更新" };
}

function canWrite() {
  const context = getApp().globalData;
  return context.currentMember ? ["manager", "editor"].includes(context.currentMember.role) : !context.useCloud;
}

Page({
  data: {
    childId: "", view: "time", offset: 1, subjectId: "", count: null,
    views: [{ id: "time", label: "按时间" }, { id: "subject", label: "按科目" }, { id: "count", label: "按次数" }],
    counts: [0, 1, 2, 3], subjects: [], subjectCursor: null, subjectHasPrevious: false, subjectLoading: false, subjectError: "",
    items: [], total: 0, nextCursor: null, pageNumber: 1, loaded: false, loading: false, error: "",
    asOfDay: "", planDate: "", minutes: 0, budget: 0, overBudget: 0, canWrite: false,
    showCountSheet: false, countDraft: "", countError: "", target: null, deleting: false,
    saving: false, actionError: "", notice: "", conflict: false
  },
  onLoad(options) {
    this.familyAtLoad = getApp().globalData.familyId || "";
    this.setData({ childId: options.childId || getApp().globalData.selectedChildId || "" });
  },
  async onShow() {
    this.visible = true;
    const app = getApp();
    const showGeneration = this.showGeneration = (this.showGeneration || 0) + 1;
    try {
      if (app.globalData.useCloud && !app.globalData.currentMember) await app.refreshBootstrap();
      if (!this.visible || showGeneration !== this.showGeneration) return;
      const family = app.globalData.familyId || "";
      const child = app.globalData.selectedChildId || this.data.childId;
      if (family !== this.familyAtLoad || child !== this.data.childId) {
        this.setData({ childId: child, items: [], subjects: [], subjectId: "", total: 0,
          loaded: false, target: null, notice: "", showCountSheet: false });
      }
      this.familyAtLoad = family;
      this.setData({ canWrite: canWrite() });
      await this.reload();
    } catch (error) { if (this.visible && showGeneration === this.showGeneration) this.setData({ error: error.message, loading: false }); }
  },
  onHide() { this.visible = false; this.showGeneration = (this.showGeneration || 0) + 1; this.generation = (this.generation || 0) + 1; this.subjectGeneration = (this.subjectGeneration || 0) + 1; this.setData({ target: null, showCountSheet: false, saving: false }); },
  onUnload() { this.onHide(); },
  async onPullDownRefresh() { await this.reload(); wx.stopPullDownRefresh(); },
  context() { return `${getApp().globalData.familyId || ""}:${this.data.childId}:${getApp().globalData.selectedChildId || ""}`; },
  async reload() {
    this.currentCursor = null;
    this.setData({ pageNumber: 1, nextCursor: null, target: null, conflict: false });
    if (this.data.view === "subject" && !this.data.subjectId) await this.loadSubjects();
    else await this.loadItems();
  },
  async loadSubjects(cursor) {
    if (!this.data.childId) return;
    const generation = this.subjectGeneration = (this.subjectGeneration || 0) + 1;
    const context = this.context();
    this.setData({ subjectLoading: true, subjectError: "" });
    try {
      const result = await api.request(`/children/${this.data.childId}/review-inventory/subjects?limit=20${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`);
      if (!this.visible || generation !== this.subjectGeneration || context !== this.context() || this.data.view !== "subject") return;
      const selected = result.items.find(item => item.id === this.data.subjectId) || result.items[0];
      this.setData({ subjects: result.items, subjectCursor: result.next_cursor, subjectHasPrevious: !!cursor, subjectId: selected ? selected.id : "", subjectLoading: false });
      this.currentCursor = null;
      this.setData({ pageNumber: 1 });
      if (selected) await this.loadItems();
      else this.setData({ loaded: true, loading: false, items: [], total: 0, nextCursor: null });
    } catch (error) {
      if (this.visible && generation === this.subjectGeneration && context === this.context()) {
        this.setData({ subjectLoading: false, subjectError: error.code === "cursor_stale" ? "科目已有变化，请重新加载科目" : error.message });
      }
    }
  },
  firstSubjects() { return this.loadSubjects(); },
  nextSubjects() { if (!this.data.subjectLoading && this.data.subjectCursor) return this.loadSubjects(this.data.subjectCursor); },
  async loadItems(cursor = null, nextPage = 1) {
    if (!this.data.childId || (this.data.view === "subject" && !this.data.subjectId)) return;
    const generation = this.generation = (this.generation || 0) + 1;
    const context = this.context();
    const { view, offset, subjectId, count } = this.data;
    const query = [`view=${view}`, `offset=${offset}`, "limit=20"];
    if (view === "subject") query.push(`subject_id=${encodeURIComponent(subjectId)}`);
    if (view === "count" && count !== null) query.push(`review_count=${count}`);
    if (cursor) query.push(`cursor=${encodeURIComponent(cursor)}`);
    this.setData({ loading: true, error: "" });
    try {
      const result = await api.request(`/children/${this.data.childId}/review-inventory?${query.join("&")}`);
      if (!this.visible || generation !== this.generation || context !== this.context()) return;
      this.currentCursor = cursor;
      this.setData({ loaded: true, loading: false, items: result.items.map(arrangementView), total: result.total,
        nextCursor: result.next_cursor, pageNumber: nextPage, asOfDay: result.as_of_day,
        planDate: result.plan_date || "", minutes: result.planned_minutes || 0,
        budget: result.budget_minutes || 0, overBudget: result.over_budget_minutes || 0,
        canWrite: canWrite() && result.child_writable });
      if (view === "subject") this.setData({ subjects: this.data.subjects.map(subject =>
        subject.id === subjectId ? { ...subject, count: result.total } : subject) });
    } catch (error) {
      if (!this.visible || generation !== this.generation || context !== this.context()) return;
      this.setData({ loading: false, error: error.statusCode === 404 ? "当前孩子或科目已不可用，请返回报表重新选择" : error.message,
        conflict: error.statusCode === 409 });
    }
  },
  changeView(event) {
    if (this.data.saving) return;
    const view = event.currentTarget.dataset.id;
    if (view === this.data.view) return;
    this.generation = (this.generation || 0) + 1;
    this.subjectGeneration = (this.subjectGeneration || 0) + 1;
    this.setData({ view, items: [], total: 0, loaded: false, error: "", notice: "" });
    return this.reload();
  },
  selectDay(event) { this.setData({ offset: Number(event.currentTarget.dataset.offset), loaded: false, items: [] }); return this.reload(); },
  selectSubject(event) { this.setData({ subjectId: event.currentTarget.dataset.id, loaded: false, items: [], pageNumber: 1 }); return this.loadItems(); },
  selectCount(event) {
    const value = event.currentTarget.dataset.count;
    this.setData({ count: value === "all" ? null : Number(value), loaded: false, items: [] });
    return this.reload();
  },
  openCount() { this.setData({ showCountSheet: true, countDraft: this.data.count === null ? "" : String(this.data.count), countError: "" }); },
  closeCount() { this.setData({ showCountSheet: false, countError: "" }); },
  inputCount(event) { this.setData({ countDraft: event.detail.value, countError: "" }); },
  confirmCount() {
    const value = this.data.countDraft.trim();
    if (!/^\d+$/.test(value) || Number(value) > 2147483647) {
      this.setData({ countError: "请输入 0 至 2147483647 的整数" }); return;
    }
    this.setData({ count: Number(value), showCountSheet: false, loaded: false, items: [] });
    return this.reload();
  },
  nextPage() { if (!this.data.loading && this.data.nextCursor) return this.loadItems(this.data.nextCursor, this.data.pageNumber + 1); },
  retry() { return this.data.conflict ? this.reload() : this.loadItems(this.currentCursor, this.data.pageNumber); },
  openActions(event) {
    if (!this.data.canWrite || !canWrite() || this.data.loading) return;
    const target = this.data.items.find(item => item.knowledge_id === event.currentTarget.dataset.id);
    this.setData({ target: target || null, deleting: false, actionError: "", conflict: false });
    this.pendingRequest = null;
  },
  closeActions() { if (!this.data.saving) { this.pendingRequest = null; this.setData({ target: null, actionError: "", deleting: false }); } },
  askDelete() { if (!this.data.saving) this.setData({ deleting: true, actionError: "" }); },
  schedule(event) { return this.mutate(event.currentTarget.dataset.action); },
  confirmDelete() { if (this.data.deleting) return this.mutate("delete"); },
  async mutate(action) {
    const target = this.data.target;
    if (!target || this.data.saving || !this.data.canWrite || !canWrite() || this.data.conflict) return;
    if (action !== "delete" && !target.can_schedule) return;
    if (action === "day_after" && !target.in_tomorrow_plan) return;
    const generation = this.generation;
    const context = this.context();
    const child = this.data.childId;
    if (!this.pendingRequest || this.pendingRequest.action !== action) this.pendingRequest = { action, key: api.newIdempotencyKey("schedule") };
    this.setData({ saving: true, actionError: "" });
    try {
      const result = action === "delete"
        ? await api.request(`/children/${child}/knowledge/${target.knowledge_id}`, { method: "DELETE" })
        : await api.request(`/children/${child}/reviews/${target.review_id}/schedule`, { method: "POST",
          idempotencyKey: this.pendingRequest.key,
          data: { action, base_day: this.data.asOfDay, expected_version: target.state_version } });
      if (!this.visible || generation !== this.generation || context !== this.context()) return;
      const notice = action === "delete" ? "条目和相关复习历史、计划已删除" : `已安排到 ${result.due_date}，复习次数不变${result.over_budget_minutes ? `；当天超出日常预算 ${result.over_budget_minutes} 分钟` : ""}`;
      this.pendingRequest = null;
      this.setData({ target: null, saving: false, notice });
      await this.reload();
    } catch (error) {
      if (!this.visible || generation !== this.generation || context !== this.context()) return;
      const conflict = error.statusCode === 409 || error.statusCode === 404;
      this.setData({ saving: false, actionError: error.message, conflict,
        canWrite: error.statusCode === 403 ? false : this.data.canWrite });
    }
  },
  ignore() {}
});
