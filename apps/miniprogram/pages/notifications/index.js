const api = require("../../utils/api");
const notifications = require("../../utils/notifications");

/* 提醒设置：开关走服务端偏好，"能不能发到微信"由微信授权决定。
   这两件事必须分开显示，否则家长会把"开关是开的"误当成"一定会收到"。 */
Page({
  data: {
    loading: true,
    error: "",
    supported: true,
    channelAvailable: false,
    channelReason: "",
    longTerm: false,
    items: [],
    grantCount: 0,
    reserveTotal: 0,
    reserveLow: false,
    canTopUp: false,
    granting: false,
    togglingType: "",
    lastSentLabel: "",
    deliveries: [],
    deliveriesError: ""
  },
  onLoad() {
    /* 老版本微信没有订阅消息接口：诚实降级，不让家长点了才报错。 */
    this.setData({ supported: typeof wx.requestSubscribeMessage === "function" });
  },
  onShow() { this.load(); },
  onPullDownRefresh() {
    this.load().then(() => { if (wx.stopPullDownRefresh) wx.stopPullDownRefresh(); });
  },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const settings = await api.request("/notifications/settings");
      this.render(settings);
      this.setData({ loading: false });
    } catch (error) {
      this.setData({ loading: false, error: error.message });
      return;
    }
    /* 最近发送只是解释用的，读不到不影响开关本身。 */
    try {
      const list = await api.request("/notifications/deliveries");
      this.setData({
        deliveries: list.map((item) => notifications.describeDelivery(item)),
        deliveriesError: ""
      });
    } catch (error) {
      this.setData({ deliveries: [], deliveriesError: error.message });
    }
  },
  render(settings) {
    const channel = settings.channel || {};
    const available = channel.available === true;
    const preferences = settings.preferences || [];
    const items = preferences.map((item) => {
      const status = notifications.statusOf(item, available);
      const quota = Number(item.remaining_quota);
      return {
        type: item.type,
        label: item.label,
        description: item.description,
        icon: notifications.typeIcon(item.type),
        enabled: item.enabled,
        managersOnly: item.managers_only,
        templateId: item.template_id || "",
        statusText: status.text,
        statusTone: status.tone,
        needsGrant: status.needsGrant,
        /* 已经开启但额度有限时，家长仍需要一个"再存几条"的入口。 */
        canTopUp: !status.needsGrant && item.enabled && !!item.template_id && quota !== -1
      };
    });
    const reserve = notifications.reserveOf(preferences, available);
    this.setData({
      channelAvailable: available,
      channelReason: channel.reason || "",
      longTerm: channel.long_term === true,
      items,
      grantCount: notifications.grantTargets(preferences, available).length,
      reserveTotal: reserve.total,
      reserveLow: reserve.low,
      canTopUp: reserve.canTopUp,
      lastSentLabel: notifications.lastSentLabel(settings.last_sent_at)
    });
    this.pending = preferences;
  },
  async toggle(event) {
    const type = event.currentTarget.dataset.type;
    const enabled = event.detail.value === true;
    const item = this.data.items.find((entry) => entry.type === type);
    if (!item || this.data.togglingType) return;
    this.setData({ togglingType: type, error: "" });
    try {
      const settings = await api.request("/notifications/preferences", {
        method: "PATCH",
        data: { type, enabled }
      });
      this.render(settings);
      this.setData({ togglingType: "" });
      if (!enabled) return wx.showToast({ title: "已关闭这类提醒", icon: "none" });
      const refreshed = this.data.items.find((entry) => entry.type === type);
      if (refreshed && refreshed.needsGrant) {
        return wx.showToast({ title: "还需要微信授权", icon: "none" });
      }
      wx.showToast({ title: "已开启", icon: "success" });
    } catch (error) {
      /* 失败时把开关拨回服务端的真实状态，不留下一个假的"已开启"。 */
      const index = this.data.items.findIndex((entry) => entry.type === type);
      const updates = { togglingType: "", error: error.message };
      if (index >= 0) updates[`items[${index}].enabled`] = item.enabled;
      this.setData(updates);
    }
  },
  /* 微信要求订阅授权必须在用户点击的同一次手势里发起，所以这里第一行就调它，
     不能先 await 任何网络请求。
     微信当前只提供一次性模板：一次同意买一条提醒，多次同意可以累积，
     所以"补额度"和"首次授权"走同一条路径，只是选谁不一样。 */
  requestGrant(event) {
    if (this.data.granting) return;
    if (!this.data.supported) {
      return wx.showModal({
        title: "当前微信版本不支持",
        content: "更新微信到最新版本后就可以开启提醒。在此之前，打开小程序仍能看到全部日程和复习。",
        showCancel: false,
        confirmText: "知道了"
      });
    }
    const dataset = (event && event.currentTarget && event.currentTarget.dataset) || {};
    const single = dataset.type;
    const source = this.pending || [];
    let targets;
    if (single) {
      targets = source.filter((item) => item.type === single && item.template_id);
    } else if (dataset.mode === "topup") {
      targets = notifications.topUpTargets(source, this.data.channelAvailable);
    } else {
      targets = notifications.grantTargets(source, this.data.channelAvailable);
    }
    if (!targets.length) return;
    const templateIds = targets.map((item) => item.template_id);
    this.setData({ granting: true, error: "" });
    wx.requestSubscribeMessage({
      tmplIds: templateIds,
      success: (response) => this.saveGrant(notifications.resultsFromWx(response, targets)),
      fail: () => this.setData({
        granting: false,
        error: "微信没有返回授权结果，可以再试一次"
      })
    });
  },
  async saveGrant(results) {
    if (!results.length) return this.setData({ granting: false });
    try {
      const settings = await api.request("/notifications/subscriptions", {
        method: "POST",
        data: { results }
      });
      this.render(settings);
      this.setData({ granting: false });
      const accepted = notifications.acceptedCount(results);
      /* 报数不报"已开启"：一次性模板下家长真正关心的是又攒了几条。 */
      if (accepted) {
        return wx.showToast({ title: `已存入 ${accepted} 条提醒`, icon: "success" });
      }
      wx.showToast({ title: "微信里没有同意，额度没有增加", icon: "none" });
    } catch (error) {
      this.setData({ granting: false, error: error.message });
    }
  },
  explain() {
    wx.showModal({
      title: "关于提醒",
      content:
        "微信只允许小程序使用一次性订阅模板：你每同意一次，就存下一条提醒额度，可以重复存。" +
        "发出一条就扣一条，额度用完这一页会提示你再存。提醒里只写孩子的名字、时间和要做的事，" +
        "不做评价，也不预测该学什么。是否送达由微信决定，重要安排请以小程序里的日程为准。",
      showCancel: false,
      confirmText: "知道了"
    });
  }
});
