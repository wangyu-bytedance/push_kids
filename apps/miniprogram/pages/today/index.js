const api = require("../../utils/api");

Page({
  data: { loading: true, error: "", children: [], childIndex: 0, childId: "", dashboard: null, sections: { review: true, learning: true, activity: true }, reviewReturn: null, reviewGroupId: "", reviewFocusText: "" },
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
      if (!children.length) {
        this.setData({ loading: false, children, dashboard: null, childId: "" });
        return;
      }
      const app = getApp();
      let childIndex = children.findIndex((item) => item.id === app.globalData.selectedChildId);
      if (childIndex < 0) childIndex = 0;
      const childId = children[childIndex].id;
      app.selectChild(childId);
      const dashboard = await api.request(`/children/${childId}/dashboard`);
      if (generation !== this.loadGeneration) return;
      dashboard.daily_summary.subjects = dashboard.daily_summary.subjects.map((item) => ({ ...item, summary_text: item.summaries.join("；") }));
      dashboard.must_todo_groups = dashboard.todo_groups.filter((item) => !item.optional);
      dashboard.optional_todo_groups = dashboard.todo_groups.filter((item) => item.optional);
      const scheduledSubjects = new Set(dashboard.schedule_items.map((item) => item.subject_id).filter(Boolean));
      dashboard.optional_activity_suggestions = dashboard.activity_suggestions.filter((item) => item.suggested && !scheduledSubjects.has(item.subject_id));
      dashboard.is_empty = !dashboard.todo_groups.length && !dashboard.daily_summary.record_count && !dashboard.schedule_items.length && !dashboard.optional_activity_suggestions.length;
      dashboard.show_guide = !dashboard.todo_groups.length && !dashboard.daily_summary.record_count;
      this.setData({ loading: false, children, childIndex, childId, dashboard });
      const back = app.globalData.reviewReturn;
      if (back && back.childId === childId) {
        const ids = new Set(back.reviewIds);
        const target = dashboard.todo_groups.find((group) => group.items.some((item) => ids.has(item.review_id)));
        this.setData({ reviewReturn: back, reviewGroupId: target ? target.id : "", "sections.review": true,
          reviewFocusText: target ? "已定位这条学习记录的到期复习" : "这条记录当前没有待完成的到期复习" });
        delete app.globalData.reviewReturn;
        if (target && wx.pageScrollTo) wx.pageScrollTo({ selector: `#todo-group-${target.id}`, duration: 0 });
      } else if (this.data.reviewReturn && this.data.reviewReturn.childId !== childId) {
        this.setData({ reviewReturn: null, reviewGroupId: "", reviewFocusText: "" });
      }
    } catch (error) {
      if (generation !== this.loadGeneration) return;
      this.setData({ loading: false, error: error.message });
    }
  },
  toggleSection(event) {
    const section = event.currentTarget.dataset.section;
    this.setData({ [`sections.${section}`]: !this.data.sections[section] });
  },
  async changeChild(event) {
    const childIndex = Number(event.detail.value);
    const childId = this.data.children[childIndex].id;
    getApp().selectChild(childId);
    this.setData({ childIndex, childId });
    await this.load();
  },
  recordLearning() { getApp().globalData.recordIntent = { childId: this.data.childId, view: "new" }; wx.switchTab({ url: "/pages/records/index" }); },
  addSchedule() { getApp().globalData.openCalendarCreate = true; wx.switchTab({ url: "/pages/calendar/index" }); },
  openPending() { getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "pending" }; wx.switchTab({ url: "/pages/records/index" }); },
  openLearningHistory(event) {
    getApp().globalData.recordIntent = { childId: this.data.childId, view: "history", status: "confirmed",
      filters: { subject_id: event.currentTarget.dataset.id, from: this.data.dashboard.day, to: this.data.dashboard.day } };
    wx.switchTab({ url: "/pages/records/index" });
  },
  returnToRecord() {
    if (!this.data.reviewReturn || this.data.reviewReturn.childId !== this.data.childId) return;
    wx.navigateTo({ url: `/pages/submission/confirm?id=${this.data.reviewReturn.submissionId}` });
  },
  openSettings() { wx.switchTab({ url: "/pages/settings/index" }); },
  openActivity(event) { wx.navigateTo({ url: `/pages/activity/edit?subjectId=${event.currentTarget.dataset.subjectId}` }); },
  async practice(event) {
    try {
      const reviewIds = event.detail.reviewIds.join(",");
      const result = await api.request(`/children/${this.data.childId}/practice-materials?review_ids=${reviewIds}`);
      wx.showModal({
        title: "带练提示",
        content: result.items.map((item, index) => `${index + 1}. ${item.prompt}`).join("\n") || "没有可用提示",
        showCancel: false
      });
    } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
  },
  async feedback(event) {
    const { reviewId, action } = event.detail;
    this.feedbackRetryKeys = this.feedbackRetryKeys || {};
    const intent = `${reviewId}:${action}`;
    const idempotencyKey = this.feedbackRetryKeys[intent] || api.newIdempotencyKey("feedback");
    const previous = this.data.dashboard;
    const groups = previous.todo_groups
      .map((group) => ({ ...group, items: group.items.filter((item) => item.review_id !== reviewId) }))
      .filter((group) => group.items.length);
    this.setData({
      "dashboard.todo_groups": groups,
      "dashboard.must_todo_groups": groups.filter((item) => !item.optional),
      "dashboard.optional_todo_groups": groups.filter((item) => item.optional)
    });
    try {
      await api.request(`/reviews/${reviewId}/feedback`, { method: "POST", data: { action }, idempotencyKey });
      delete this.feedbackRetryKeys[intent];
      wx.showToast({ title: action === "complete" ? "已完成" : "计划已调整", icon: "success" });
      await this.load();
    } catch (error) {
      this.feedbackRetryKeys[intent] = idempotencyKey;
      this.setData({ dashboard: previous });
      wx.showToast({ title: error.message, icon: "none" });
    }
  }
});
