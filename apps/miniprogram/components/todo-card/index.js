const ui = require("../../utils/ui");

/* 「⋯」里的三种反馈都是家长的主观标记：顺序与文案固定，不含任何评分或掌握度含义。
   effect 描述 planning/domain.apply_feedback 的确定性结果，改策略时必须同步改这里。 */
const MORE_ACTIONS = [
  { action: "reinforce", icon: "ico-refresh-att", effect: "明天再出现一次" },
  { action: "partial", icon: "ico-list", effect: "间隔取一半，会更早再出现" },
  { action: "defer", icon: "ico-clock-mute", effect: "今天不再提醒，明天再来" }
];

Component({
  options: { addGlobalClass: true },
  properties: {
    canWrite: { type: Boolean, value: true },
    group: {
      type: Object,
      value: {},
      observer(value) { this.buildView(value); }
    }
  },
  data: { busyId: "", panelId: "", view: { items: [], actions: [] } },
  attached() { this.buildView(this.data.group); },
  methods: {
    /* WXML 里不允许出现方法调用，所有派生文案都在这里算好。 */
    buildView(group) {
      const source = group || {};
      const items = source.items || [];
      this.setData({
        busyId: "",
        panelId: "",
        view: {
          optional: !!source.optional,
          subjectClass: ui.subjectClass(source.subject_name, source.subject_kind),
          subjectMark: ui.subjectMark(source.subject_name),
          title: `${source.subject_name || "学习"} · ${source.review_method || "复习一遍"}`,
          meta: `${items.length} 个知识点 · 约 ${source.estimated_minutes || 0} 分钟`,
          status: source.optional ? "可选" : "建议完成",
          actions: MORE_ACTIONS.map((entry) => ({
            action: entry.action,
            icon: entry.icon,
            label: ui.feedbackLabel(entry.action),
            effect: entry.effect
          })),
          items: items.map((item) => ({
            reviewId: item.review_id,
            knowledgeId: item.knowledge_id || "",
            name: item.knowledge_name,
            sourceSummary: String(item.source_summary || "").trim(),
            sourceSubmissionId: item.source_submission_id || "",
            sourceImageIndex: Number.isInteger(item.source_image_index) && item.source_image_index >= 1 && item.source_image_index <= 9 ? item.source_image_index : 0,
            sourceOccurredOn: item.source_occurred_on || "",
            sourceDateLabel: ui.monthDay(item.source_occurred_on),
            canOpenSource: !!item.source_submission_id,
            done: !!(item.done || item.completed_at)
          }))
        }
      });
    },
    openSource(event) {
      const reviewId = event.currentTarget.dataset.reviewId;
      const item = this.data.view.items.find((entry) => entry.reviewId === reviewId);
      if (!item || !item.canOpenSource) return;
      this.triggerEvent("source", item);
    },
    /* 卡面只留「完成」，其余三种主观反馈就地展开，选项旁写明它会怎么改复习安排。 */
    openMore(event) {
      const reviewId = event.currentTarget.dataset.reviewId;
      this.setData({ panelId: this.data.panelId === reviewId ? "" : reviewId });
    },
    closePanel() {
      this.setData({ panelId: "" });
    },
    deleteRecord(event) {
      const item = this.data.view.items.find((entry) => entry.reviewId === event.currentTarget.dataset.reviewId);
      if (!this.data.canWrite || !item || !item.knowledgeId || this.data.busyId === item.reviewId) return;
      this.setData({ panelId: "" });
      this.triggerEvent("delete", item);
    },
    feedback(event) {
      this.sendFeedback(event.currentTarget.dataset.reviewId, event.currentTarget.dataset.action);
    },
    /* busyId 只做 pending 态；父页刷新或回滚都会重建视图并清空它。 */
    sendFeedback(reviewId, action) {
      if (!reviewId || !action || this.data.busyId === reviewId) return;
      this.setData({ busyId: reviewId, panelId: "" });
      this.triggerEvent("feedback", { reviewId, action });
    }
  }
});
