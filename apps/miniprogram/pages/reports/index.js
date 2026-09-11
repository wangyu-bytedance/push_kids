const api = require("../../utils/api");
const ui = require("../../utils/ui");
const childContext = require("../../utils/child-context");

const REPORT_PAGE_SIZE = 30;
const RANGES = [7, 30, 100];
const TREND_KEYS = ["learning_records", "new_knowledge_items", "review_feedback_count", "activity_records"];
const TREND_WIDTH_RPX = 128;
const TREND_TOP_RPX = 6;
const TREND_BOTTOM_RPX = 42;

function dayNumber(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return null;
  const parts = value.split("-").map(Number);
  const result = Date.UTC(parts[0], parts[1] - 1, parts[2]);
  return new Date(result).toISOString().slice(0, 10) === value ? result / 86400000 : null;
}

/* 趋势字段来自新版服务端。任何结构、日期或合计不一致都整体降级，避免画出误导性的曲线。 */
function normalizeTrendBuckets(report, overview, days) {
  const trend = report && report.overview_trends;
  if (!trend || trend.timezone !== "Asia/Shanghai" || trend.aggregation !== "equal_time_sum"
      || !Array.isArray(trend.buckets) || trend.buckets.length !== 7) return null;
  const totals = Object.fromEntries(TREND_KEYS.map((key) => [key, 0]));
  let previousEnd = null;
  const buckets = [];
  for (const raw of trend.buckets) {
    const start = dayNumber(raw.start_day);
    const end = dayNumber(raw.end_day);
    if (start === null || end === null || start > end || (previousEnd !== null && start !== previousEnd + 1)) return null;
    const bucket = { start_day: raw.start_day, end_day: raw.end_day };
    for (const key of TREND_KEYS) {
      const value = raw[key];
      if (!Number.isInteger(value) || value < 0) return null;
      bucket[key] = value;
      totals[key] += value;
    }
    previousEnd = end;
    buckets.push(bucket);
  }
  if (TREND_KEYS.some((key) => totals[key] !== (Number(overview[key]) || 0))) return null;
  const expectedStarts = Array(7).fill(null);
  const expectedEnds = Array(7).fill(null);
  const rangeStart = dayNumber(buckets[0].start_day);
  for (let offset = 0; offset < days; offset += 1) {
    const index = Math.floor(offset * 7 / days);
    if (expectedStarts[index] === null) expectedStarts[index] = rangeStart + offset;
    expectedEnds[index] = rangeStart + offset;
  }
  if (buckets.some((bucket, index) => dayNumber(bucket.start_day) !== expectedStarts[index]
      || dayNumber(bucket.end_day) !== expectedEnds[index])) return null;
  return buckets;
}

function metricTrend(buckets, key, days) {
  if (!buckets) return { available: false, segments: [], dots: [], summary: `近 ${days} 天趋势数据暂不可用` };
  const values = buckets.map((bucket) => bucket[key]);
  const maximum = Math.max(...values);
  const xStep = TREND_WIDTH_RPX / (values.length - 1);
  const chartHeight = TREND_BOTTOM_RPX - TREND_TOP_RPX;
  const points = values.map((value, index) => ({
    x: index * xStep,
    y: maximum ? TREND_BOTTOM_RPX - value / maximum * chartHeight : TREND_BOTTOM_RPX,
    value
  }));
  const segments = points.slice(0, -1).map((point, index) => {
    const next = points[index + 1];
    const dx = next.x - point.x;
    const dy = next.y - point.y;
    return {
      id: String(index),
      style: `left:${point.x.toFixed(1)}rpx;top:${point.y.toFixed(1)}rpx;width:${Math.hypot(dx, dy).toFixed(1)}rpx;transform:rotate(${(Math.atan2(dy, dx) * 180 / Math.PI).toFixed(1)}deg)`
    };
  });
  const dots = points.map((point, index) => ({
    id: String(index),
    last: index === points.length - 1,
    tickStyle: `left:${point.x.toFixed(1)}rpx`,
    style: `left:${(point.x - 3).toFixed(1)}rpx;top:${(point.y - 3).toFixed(1)}rpx`
  }));
  return {
    available: true,
    segments,
    dots,
    summary: `近 ${days} 天分为 7 段，最高 ${maximum}，最近一段 ${values[values.length - 1]}`
  };
}

/* 报表只呈现客观事实：记了多少、复习反馈了多少、活动练了多少。
   正确率、掌握度、进步幅度、下一步该学什么都不属于这一页。 */
function metricCell(value, label, key, buckets, days) {
  const count = Number(value) || 0;
  const trend = metricTrend(buckets, key, days);
  return {
    label,
    text: count > 9999 ? "9999+" : String(count),
    zero: count === 0,
    tight: count >= 1000,
    trend,
    ariaLabel: `${label} ${count}，${trend.summary}`
  };
}

function localDay(value) {
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
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

/* 活动练习聚合由报表服务端统一计算，避免客户端用截断的历史明细重算。 */
function activityRows(report) {
  if (!report || !Array.isArray(report.activity_subjects)) return [];
  return report.activity_subjects.map((row) => ({
    id: row.subject_id,
    name: row.subject_name,
    count: Number(row.records) || 0,
    minutes: Number(row.minutes) || 0,
    lastDay: row.last_occurred_on,
    iconClass: ui.activityIcon(row.subject_name, "pri"),
    meta: Number(row.minutes)
      ? `${row.records} 次 · 共 ${row.minutes} 分钟 · 上次 ${row.last_occurred_on.slice(5)}`
      : `${row.records} 次 · 上次 ${row.last_occurred_on.slice(5)}`
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
      const report = await api.request(`/children/${childId}/report?days=${days}`);
      if (generation !== this.loadGeneration) return;
      const maxSubject = Math.max(1, ...report.subjects.map((item) => item.occurrences));
      const subjects = report.subjects.map((item) => ({
        ...item,
        width: Math.max(5, Math.round(item.occurrences / maxSubject * 100)),
        countText: `${item.occurrences} 条`
      }));
      const urgencyPages = reportPages(report.review_urgency, "urgency");
      const activityPages = reportPages(report.review_activity, "activity");
      const overview = report.overview;
      const trendBuckets = normalizeTrendBuckets(report, overview, days);
      this.setData({
        loading: false, children, childIndex, childId, multiChild: selection.multiChild, canAddChild,
        report, subjects, urgencyPages, activityPages, urgencyPage: 0, activityPage: 0,
        urgencyPageLabel: urgencyPages.length ? urgencyPages[0].label : "",
        activityPageLabel: activityPages.length ? activityPages[0].label : "",
        rangeLabel: `近 ${days} 天`,
        metrics: [
          metricCell(overview.learning_records, "学习记录", "learning_records", trendBuckets, days),
          metricCell(overview.new_knowledge_items, "新增知识", "new_knowledge_items", trendBuckets, days),
          metricCell(overview.review_feedback_count, "复习反馈", "review_feedback_count", trendBuckets, days),
          metricCell(overview.activity_records, "活动练习", "activity_records", trendBuckets, days)
        ],
        feedbackTotal: Number(overview.review_feedback_count) || 0,
        activityRows: activityRows(report),
        activityDetailFailed: !Array.isArray(report.activity_subjects),
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
