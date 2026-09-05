const api = require("../../utils/api");

const REPORT_PAGE_SIZE = 30;

function formatItems(items, kind) {
  return items.map((item) => ({
    ...item,
    dayLabel: item.day.slice(8),
    display: kind === "urgency" ? (item.has_items ? (item.passed ? "✓" : item.pending_count) : "") : ""
  }));
}

function reportPages(items, kind) {
  const formatted = formatItems(items, kind);
  const result = [];
  for (let offset = 0; offset < formatted.length; offset += REPORT_PAGE_SIZE) {
    const part = formatted.slice(offset, offset + REPORT_PAGE_SIZE);
    result.push({
      id: String(offset / REPORT_PAGE_SIZE),
      pageNumber: offset / REPORT_PAGE_SIZE + 1,
      items: part,
      label: `${part[0].day.slice(5)} 至 ${part[part.length - 1].day.slice(5)}`
    });
  }
  return result;
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", days: 7,
    report: null, ranges: [7, 30, 100], urgencyPages: [], activityPages: [],
    urgencyPage: 0, activityPage: 0, urgencyPageLabel: "", activityPageLabel: ""
  },
  onShow() { this.load(); },
  async load() {
    const generation = (this.loadGeneration || 0) + 1;
    this.loadGeneration = generation;
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (generation !== this.loadGeneration) return;
      if (!children.length) return this.setData({ loading: false, children, report: null, urgencyPages: [], activityPages: [], urgencyPageLabel: "", activityPageLabel: "" });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const report = await api.request(`/children/${childId}/report?days=${this.data.days}`);
      if (generation !== this.loadGeneration) return;
      const maxSubject = Math.max(1, ...report.subjects.map((item) => item.occurrences));
      report.subjects = report.subjects.map((item) => ({ ...item, width: Math.max(5, Math.round(item.occurrences / maxSubject * 100)) }));
      const urgencyPages = reportPages(report.review_urgency, "urgency");
      const activityPages = reportPages(report.review_activity, "activity");
      this.setData({
        loading: false, children, childIndex, childId, report, urgencyPages, activityPages,
        urgencyPage: 0, activityPage: 0,
        urgencyPageLabel: urgencyPages.length ? urgencyPages[0].label : "",
        activityPageLabel: activityPages.length ? activityPages[0].label : ""
      });
    } catch (error) { if (generation === this.loadGeneration) this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  openSubjectHistory(event) {
    const report = this.data.report;
    if (!report) return;
    const dates = report.review_activity;
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
      filters: { subject_id: event.currentTarget.dataset.id, from: dates.length ? dates[0].day : "", to: dates.length ? dates[dates.length - 1].day : "" } };
    wx.switchTab({ url: "/pages/records/index" });
  },
  changeRange(event) {
    const days = Number(event.currentTarget.dataset.days);
    if (days === this.data.days) return;
    this.setData({ days, urgencyPage: 0, activityPage: 0 });
    this.load();
  },
  onUrgencyPageChange(event) {
    const urgencyPage = event.detail.current;
    this.setData({ urgencyPage, urgencyPageLabel: this.data.urgencyPages[urgencyPage].label });
  },
  onActivityPageChange(event) {
    const activityPage = event.detail.current;
    this.setData({ activityPage, activityPageLabel: this.data.activityPages[activityPage].label });
  },
  shiftReportPage(event) {
    const chart = event.currentTarget.dataset.chart;
    const offset = Number(event.currentTarget.dataset.offset);
    const pageKey = chart === "urgency" ? "urgencyPage" : "activityPage";
    const pages = chart === "urgency" ? this.data.urgencyPages : this.data.activityPages;
    const next = Math.max(0, Math.min(pages.length - 1, this.data[pageKey] + offset));
    const labelKey = chart === "urgency" ? "urgencyPageLabel" : "activityPageLabel";
    this.setData({ [pageKey]: next, [labelKey]: pages[next].label });
  }
});
