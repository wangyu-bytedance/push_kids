const ui = require("../../utils/ui");

/* 「⋯」里的三种反馈都是家长的主观标记：顺序与文案固定，不含任何评分或掌握度含义。 */
const MORE_ACTIONS = ["reinforce", "partial", "defer"];

Component({
  options: { addGlobalClass: true },
  properties: {
    group: {
      type: Object,
      value: {},
      observer(value) { this.buildView(value); }
    }
  },
  data: { busyId: "", view: { items: [] } },
  attached() { this.buildView(this.data.group); },
  methods: {
    /* WXML 里不允许出现方法调用，所有派生文案都在这里算好。 */
    buildView(group) {
      const source = group || {};
      const items = source.items || [];
      const reasonSource = items.find((item) => ui.reviewReason(item));
      const reason = reasonSource ? ui.reviewReason(reasonSource) : "";
      if (items.length && !reason) {
        console.warn("todo-card: 这条复习没有可展示的来源信息，已省略「出现原因」", source.id || "");
      }
      this.setData({
        busyId: "",
        view: {
          optional: !!source.optional,
          subjectClass: ui.subjectClass(source.subject_name, source.subject_kind),
          subjectMark: ui.subjectMark(source.subject_name),
          title: `${source.subject_name || "学习"} · ${source.review_method || "复习一遍"}`,
          meta: `${items.length} 个知识点 · 约 ${source.estimated_minutes || 0} 分钟`,
          status: source.optional ? "可选" : "建议完成",
          reason: reason ? `出现原因：${reason}` : "",
          hint: "带练提示：可以先看一遍提示，再陪孩子过一遍",
          items: items.map((item) => ({
            reviewId: item.review_id,
            name: item.knowledge_name,
            done: !!(item.done || item.completed_at)
          }))
        }
      });
    },
    practice() {
      this.triggerEvent("practice", {
        reviewIds: (this.data.group.items || []).map((item) => item.review_id)
      });
    },
    /* 卡面只留「完成」，其余三种主观反馈收进原生 Action Sheet。 */
    openMore(event) {
      const reviewId = event.currentTarget.dataset.reviewId;
      wx.showActionSheet({
        itemList: MORE_ACTIONS.map((action) => ui.feedbackLabel(action)),
        success: (result) => {
          const action = MORE_ACTIONS[result.tapIndex];
          if (action) this.sendFeedback(reviewId, action);
        },
        fail: () => {}
      });
    },
    feedback(event) {
      this.sendFeedback(event.currentTarget.dataset.reviewId, event.currentTarget.dataset.action);
    },
    /* busyId 只做 pending 态；父页刷新或回滚都会重建视图并清空它。 */
    sendFeedback(reviewId, action) {
      if (!reviewId || !action || this.data.busyId === reviewId) return;
      this.setData({ busyId: reviewId });
      this.triggerEvent("feedback", { reviewId, action });
    }
  }
});
