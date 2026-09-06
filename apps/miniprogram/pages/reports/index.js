const api = require("../../utils/api");
const ui = require("../../utils/ui");
const childContext = require("../../utils/child-context");

const REPORT_PAGE_SIZE = 30;
const RANGES = [7, 30, 100];
/* 吸顶区间条约 100rpx（12+72+16），再留 24rpx 余量，页内定位后标题不会贴边或被盖住。 */
const SCROLL_MARGIN_RPX = 124;

/* 4 个概览指标各自的落点：学习记录跨 Tab 去历史列表，其余三个在本页定位到对应区块。 */
const METRIC_TARGETS = {
  learning: { section: "", action: "看这段时间已确认的学习记录", empty: "这段时间还没有已确认的学习记录" },
  knowledge: { section: "#sec-subjects", action: "看科目学习记录分布", empty: "这段时间还没有新增知识" },
  feedback: { section: "#sec-feedback", action: "看复习活跃度", empty: "这段时间还没有复习反馈" },
  activity: { section: "#sec-activities", action: "看课外活动投入", empty: "这段时间还没有活动练习" }
};

/* 报表只呈现客观事实：记了多少、复习反馈了多少、活动练了多少。
   正确率、掌握度、进步幅度、下一步该学什么都不属于这一页。 */
function metricCell(value, label, target) {
  const count = Number(value) || 0;
  const meta = METRIC_TARGETS[target];
  return {
    label,
    target,
    text: count > 9999 ? "9999+" : String(count),
    zero: count === 0,
    tight: count >= 1000,
    actionable: count > 0,
    hint: meta.empty,
    ariaLabel: count > 0 ? `${label} ${count}，${meta.action}` : `${label} 0，${meta.empty}`
  };
}

function localDay(value) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
}

/* rpx 换 px：滚动接口只认 px，窗口宽度取不到时按 375 基准估算。 */
function rpxToPx(value) {
  let width = 0;
  try {
    const info = (wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync()) || {};
    width = Number(info.windowWidth) || 0;
  } catch {
    width = 0;
  }
  return value * (width || 375) / 750;
}

/* 报表区间换算成历史列表的 from/to：服务端已给出逐日序列时用它的首尾，口径与图表完全一致。 */
function rangeFilters(report, days) {
  const dates = report && report.review_activity ? report.review_activity : [];
  if (dates.length) return { from: dates[0].day, to: dates[dates.length - 1].day };
  const to = new Date();
  const from = new Date(to.getTime() - (Math.max(1, Number(days) || 1) - 1) * 86400000);
  return { from: localDay(from), to: localDay(to) };
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
    iconClass: ui.activityIcon(row.name, "pri"),
    meta: row.minutes
      ? `${row.count} 次 · 共 ${row.minutes} 分钟 · 上次 ${row.lastDay.slice(5)}`
      : `${row.count} 次 · 上次 ${row.lastDay.slice(5)}`
  }));
}

Page({
  data: {
    loading: true, error: "", children: [], childIndex: 0, childId: "", multiChild: false, showChildSheet: false, canAddChild: true,
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
      const profiles = await api.request("/children");
      if (generation !== this.loadGeneration) return;
      const selection = childContext.syncSelection(getApp(), profiles);
      const children = selection.children;
      const canAddChild = childContext.canAddChild(profiles);
      if (!children.length) {
        this.setData({ loading: false, children, multiChild: false, canAddChild, report: null, metrics: [], subjects: [],
          activityRows: [], urgencyPages: [], activityPages: [], urgencyPageLabel: "", activityPageLabel: "" });
        return;
      }
      const childIndex = selection.childIndex;
      const childId = selection.childId;
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
        loading: false, children, childIndex, childId, multiChild: selection.multiChild, canAddChild,
        report, subjects, urgencyPages, activityPages, urgencyPage: 0, activityPage: 0,
        urgencyPageLabel: urgencyPages.length ? urgencyPages[0].label : "",
        activityPageLabel: activityPages.length ? activityPages[0].label : "",
        rangeLabel: `近 ${days} 天`,
        metrics: [
          metricCell(overview.learning_records, "学习记录", "learning"),
          metricCell(overview.new_knowledge_items, "新增知识", "knowledge"),
          metricCell(overview.review_feedback_count, "复习反馈", "feedback"),
          metricCell(overview.activity_records, "活动练习", "activity")
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
  openChildSheet() { if (this.data.children.length) this.setData({ showChildSheet: true }); },
  closeChildSheet() { this.setData({ showChildSheet: false }); },
  addChild() {
    this.setData({ showChildSheet: false });
    wx.navigateTo({ url: "/pages/child-edit/index?mode=create" });
  },
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
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
      filters: { subject_id: event.currentTarget.dataset.id, ...rangeFilters(report, this.data.days) } };
    wx.switchTab({ url: "/pages/records/index" });
  },
  /* 指标为 0 时不跳到空页面，只说明这段时间没有对应记录。 */
  openMetric(event) {
    const target = event.currentTarget.dataset.target;
    const metric = this.data.metrics.find((item) => item.target === target);
    if (!metric) return;
    if (!metric.actionable) {
      wx.showToast({ title: metric.hint, icon: "none" });
      return;
    }
    if (target === "learning") {
      getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
        filters: rangeFilters(this.data.report, this.data.days) };
      wx.switchTab({ url: "/pages/records/index" });
      return;
    }
    this.scrollToSection(METRIC_TARGETS[target].section);
  },
  /* 页内定位用 boundingClientRect + scrollOffset，兼容性比 selector 直跳更稳。 */
  scrollToSection(selector) {
    if (!selector || !wx.createSelectorQuery) return;
    const query = wx.createSelectorQuery();
    query.select(selector).boundingClientRect();
    query.selectViewport().scrollOffset();
    query.exec((result) => {
      const rect = result && result[0];
      const viewport = result && result[1];
      if (!rect || !viewport) return;
      const margin = rpxToPx(SCROLL_MARGIN_RPX);
      const scrollTop = Math.max(0, rect.top + viewport.scrollTop - margin);
      wx.pageScrollTo({ scrollTop, duration: 200 });
    });
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
