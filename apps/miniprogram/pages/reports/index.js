const api = require("../../utils/api");

function formatItems(items, kind) {
  return items.map((item) => ({
    ...item,
    dayLabel: item.day.slice(8),
    display: kind === "urgency" ? (item.has_items ? (item.passed ? "✓" : item.pending_count) : "") : ""
  }));
}

function chunks(items, days, kind) {
  const formatted = formatItems(items, kind);
  if (days !== 100) return [{ id: "0", items: formatted, label: `${formatted[0].day.slice(5)} 至 ${formatted[formatted.length - 1].day.slice(5)}` }];
  const sizes = [10, 30, 30, 30];
  let offset = 0;
  return sizes.map((size, index) => { const part = formatted.slice(offset, offset + size); offset += size; return { id: String(index), items: part, label: `${part[0].day.slice(5)} 至 ${part[part.length - 1].day.slice(5)}` }; });
}

Page({
  data: { loading: true, error: "", children: [], childIndex: 0, childId: "", days: 7, report: null, ranges: [7, 30, 100], urgencyChunks: [], activityChunks: [], lastChunkId: "0" },
  onShow() { this.load(); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const children = (await api.request("/children")).map((item) => ({
        ...item,
        avatar: item.name ? item.name.charAt(0) : "芽"
      }));
      if (!children.length) return this.setData({ loading: false, children, report: null });
      let childIndex = children.findIndex((item) => item.id === getApp().globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id; getApp().selectChild(childId);
      const report = await api.request(`/children/${childId}/report?days=${this.data.days}`);
      const maxSubject = Math.max(1, ...report.subjects.map((item) => item.occurrences));
      report.subjects = report.subjects.map((item) => ({ ...item, width: Math.max(5, Math.round(item.occurrences / maxSubject * 100)) }));
      const urgencyChunks = chunks(report.review_urgency, this.data.days, "urgency");
      const activityChunks = chunks(report.review_activity, this.data.days, "activity");
      this.setData({ loading: false, children, childIndex, childId, report, urgencyChunks, activityChunks, lastChunkId: String(urgencyChunks.length - 1) });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  changeChild(event) { getApp().selectChild(this.data.children[Number(event.detail.value)].id); this.load(); },
  changeRange(event) { this.setData({ days: Number(event.currentTarget.dataset.days) }); this.load(); }
});
