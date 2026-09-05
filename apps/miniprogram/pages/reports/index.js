const api = require("../../utils/api");
const ui = require("../../utils/ui");

const REPORT_PAGE_SIZE = 30;
const RANGES = [7, 30, 100];

/* 报表只呈现客观事实：记了多少、复习反馈了多少、活动练了多少。
   正确率、掌握度、进步幅度、下一步该学什么都不属于这一页。 */
function metricCell(value, label) {
  const count = Number(value) || 0;
  return {
    label,
    text: count > 9999 ? "9999+" : String(count),
    zero: count === 0,
    tight: count >= 1000
  };
}

/* 圆点档位、色块档位、日期刻度、读法说明全部在这里算好，WXML 不做任何方法调用。 */
function formatItems(items, kind) {
  return items.map((item) => {
    const dayLabel = item.day.slice(8);
    const dayText = item.day.slice(5);
    if (kind === "urgency") {
      const pending = Number(item.pending_count) || 0;
      return {
        ...item,
        dayLabel,
        display: item.passed ? "" : String(pending),
        dotClass: item.passed ? "pass" : `l${Number(item.level) || 0}`,
        reading: item.passed ? `${dayText} 当天到期的复习都已完成` : `${dayText} 待复习 ${pending} 个知识点`
      };
    }
    const count = Number(item.count) || 0;
    return {
      ...item,
      dayLabel,
      display: "",
      boxClass: `h${Number(item.level) || 0}`,
      reading: `${dayText} 记录了 ${count} 次复习反馈`
    };
  });
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

/* 活动练习按活动聚合成「n 次 · 上次 mm-dd」，只统计选中区间内的记录。 */
function activityRows(detail, startDay) {
  if (!detail || detail.failed) return [];
  const index = {};
  const rows = [];
  detail.records.forEach((record) => {
    const day = String(record.occurred_at || "").slice(0, 10);
    const name = detail.names[record.subject_id];
    if (!day || !name || (startDay && day < startDay)) return;
    let row = index[record.subject_id];
    if (!row) {
      row = { id: record.subject_id, name, count: 0, lastDay: day, minutes: 0 };
      index[record.subject_id] = row;
      rows.push(row);
    }
    row.count += 1;
    row.minutes += Number(record.duration_minutes) || 0;
    if (day > row.lastDay) row.lastDay = day;
  });
  rows.sort((left, right) => right.count - left.count);
  return rows.map((row) => ({
    ...row,
    meta: row.minutes
      ? `${row.count} 次 · 共 ${row.minutes} 分钟 · 上次 ${row.lastDay.slice(5)}`
      : `${row.count} 次 · 上次 ${row.lastDay.slice(5)}`
  }));
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", multiChild: false, showChildSheet: false,
    days: 7, ranges: RANGES, rangeLabel: "近 7 天", report: null, metrics: [], isEmpty: false,
    subjects: [], activityRows: [], activityDetailFailed: false, feedbackTotal: 0,
    urgencyPages: [], activityPages: [], urgencyPage: 0, activityPage: 0,
    urgencyPageLabel: "", activityPageLabel: ""
  },
  onShow() {
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar) tabBar.setData({ selected: 3 });
    const days = this.rememberedRange(getApp().globalData.selectedChildId);
    if (days !== this.data.days) this.setData({ days, rangeLabel: `近 ${days} 天`, urgencyPage: 0, activityPage: 0 });
    this.load();
  },
  async onPullDownRefresh() {
    await this.load();
    if (wx.stopPullDownRefresh) wx.stopPullDownRefresh();
  },
  /* 区间选择按孩子维度记忆；storage 里的脏数据一律回落到近 7 天。 */
  rememberedRange(childId) {
    const stored = Number(ui.readPreference("reportRange", childId, 7));
    return RANGES.indexOf(stored) >= 0 ? stored : 7;
  },
  /* 活动明细是补充信息，读不到时报表主体照常展示。 */
  async loadActivityDetail(childId) {
    try {
      const [subjects, records] = await Promise.all([
        api.request(`/children/${childId}/subjects`),
        api.request(`/children/${childId}/activity-records`)
      ]);
      const names = {};
      subjects.forEach((item) => { if (item.kind === "activity") names[item.id] = item.name; });
      return { names, records, failed: false };
    } catch {
      return { names: {}, records: [], failed: true };
    }
  },
  async load() {
    const generation = (this.loadGeneration || 0) + 1;
    this.loadGeneration = generation;
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽",
        label: item.grade ? `${item.name} · ${item.grade}` : item.name
      }));
      if (generation !== this.loadGeneration) return;
      if (!children.length) {
        this.setData({ loading: false, children, multiChild: false, report: null, metrics: [], subjects: [],
          activityRows: [], urgencyPages: [], activityPages: [], urgencyPageLabel: "", activityPageLabel: "" });
        return;
      }
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      getApp().selectChild(childId);
      const days = this.data.days;
      const [report, detail] = await Promise.all([
        api.request(`/children/${childId}/report?days=${days}`),
        this.loadActivityDetail(childId)
      ]);
      if (generation !== this.loadGeneration) return;
      const maxSubject = Math.max(1, ...report.subjects.map((item) => item.occurrences));
      const subjects = report.subjects.map((item) => ({
        ...item,
        width: Math.max(5, Math.round(item.occurrences / maxSubject * 100)),
        countText: `${item.occurrences} 条`
      }));
      const urgencyPages = reportPages(report.review_urgency, "urgency");
      const activityPages = reportPages(report.review_activity, "activity");
      const startDay = report.review_activity.length ? report.review_activity[0].day : "";
      const overview = report.overview;
      this.setData({
        loading: false, children, childIndex, childId, multiChild: children.length > 1,
        report, subjects, urgencyPages, activityPages, urgencyPage: 0, activityPage: 0,
        urgencyPageLabel: urgencyPages.length ? urgencyPages[0].label : "",
        activityPageLabel: activityPages.length ? activityPages[0].label : "",
        rangeLabel: `近 ${days} 天`,
        metrics: [
          metricCell(overview.learning_records, "学习记录"),
          metricCell(overview.new_knowledge_items, "新增知识"),
          metricCell(overview.review_feedback_count, "复习反馈"),
          metricCell(overview.activity_records, "活动练习")
        ],
        feedbackTotal: Number(overview.review_feedback_count) || 0,
        activityRows: activityRows(detail, startDay),
        activityDetailFailed: detail.failed,
        isEmpty: !overview.learning_records && !overview.new_knowledge_items
          && !overview.review_feedback_count && !overview.activity_records
      });
    } catch (error) {
      /* 弱网时保留上一次读到的统计，只在顶部给一条可重试的说明。 */
      if (generation === this.loadGeneration) this.setData({ loading: false, error: error.message });
    }
  },
  openChildSheet() { if (this.data.multiChild) this.setData({ showChildSheet: true }); },
  closeChildSheet() { this.setData({ showChildSheet: false }); },
  chooseChild(event) {
    const childIndex = Number(event.currentTarget.dataset.index);
    const childId = this.data.children[childIndex].id;
    getApp().selectChild(childId);
    const days = this.rememberedRange(childId);
    this.setData({ childIndex, childId, days, rangeLabel: `近 ${days} 天`, showChildSheet: false,
      urgencyPage: 0, activityPage: 0 });
    this.load();
  },
  changeRange(event) {
    const days = Number(event.currentTarget.dataset.days);
    if (days === this.data.days) return;
    ui.writePreference("reportRange", this.data.childId, days);
    this.setData({ days, rangeLabel: `近 ${days} 天`, urgencyPage: 0, activityPage: 0 });
    this.load();
  },
  openSubjectHistory(event) {
    const report = this.data.report;
    if (!report) return;
    const dates = report.review_activity;
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
      filters: { subject_id: event.currentTarget.dataset.id, from: dates.length ? dates[0].day : "", to: dates.length ? dates[dates.length - 1].day : "" } };
    wx.switchTab({ url: "/pages/records/index" });
  },
  goRecord() {
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "new" };
    wx.switchTab({ url: "/pages/records/index" });
  },
  openSettings() { wx.switchTab({ url: "/pages/settings/index" }); },
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
