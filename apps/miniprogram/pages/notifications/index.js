const api = require("../../utils/api");
const notifications = require("../../utils/notifications");
const renewal = require("../../utils/notification-renewal");

function currentScope() {
  const data = getApp().globalData;
  return `${data.familyId || ""}:${(data.currentMember || {}).id || data.localActorId || ""}`;
}

const STATUS_TEXT = {
  ready: "下次完成复习时尝试补充", off: "自动补充未开启", needs_consent: "需先明确同意当前模板",
  disabled: "已关闭", pending: "授权结果待确认", remembered_reject: "微信已记住拒绝",
  main_switch_off: "微信提醒总开关已关闭", ban: "微信暂不允许此模板", filter: "微信过滤了此模板",
  unavailable: "暂不可用"
};

Page({
  data: {
    loading: true, error: "", supported: true, channelAvailable: false, channelReason: "",
    items: [], grantCount: 0, granting: false, togglingType: "", lastSentLabel: "",
    deliveries: [], deliveriesError: "", autoEnabled: false, autoSaving: false,
    heroTitle: "提醒状态待更新", heroReady: false
  },
  onLoad() { this.setData({ supported: typeof wx.requestSubscribeMessage === "function" }); },
  onShow() { if (this.controller) this.controller.show(); this.load(); },
  onHide() { if (this.controller) this.controller.hide(); this.loadGeneration = (this.loadGeneration || 0) + 1; },
  onUnload() { this.onHide(); },
  onPullDownRefresh() {
    this.load().then(() => { if (wx.stopPullDownRefresh) wx.stopPullDownRefresh(); });
  },
  ensureController() {
    if (!this.controller) this.controller = renewal.createController((view) => this.renderRenewal(view));
    return this.controller;
  },
  async load() {
    const token = (this.loadGeneration || 0) + 1;
    this.loadGeneration = token;
    const scope = currentScope();
    const alive = () => token === this.loadGeneration && scope === currentScope();
    this.setData({ loading: true, error: "", autoSaving: false, togglingType: "" });
    const history = api.request("/notifications/deliveries").then((list) => {
      if (alive()) this.setData({ deliveries: list.map(notifications.describeDelivery), deliveriesError: "" });
    }).catch((error) => {
      if (alive()) this.setData({ deliveriesError: error.message });
    });
    try {
      await this.ensureController().refresh("manual");
      if (alive()) this.setData({ loading: false });
    } catch (error) {
      if (alive()) this.setData({ loading: false, error: error.message,
        ...(error.statusCode === 403 ? { items: [], grantCount: 0, channelAvailable: false, deliveries: [] } : {}),
        heroTitle: "提醒状态待更新", heroReady: false });
    }
    await history;
  },
  renderRenewal(view) {
    if (!view || !view.settings) return;
    const settings = view.settings;
    const channel = settings.channel || {};
    const available = channel.available === true;
    const byType = Object.fromEntries(view.types.map((item) => [item.type, item]));
    const pendingTypes = this.controller ? this.controller.pendingTypes() : [];
    const items = settings.preferences.map((item) => {
      const state = byType[item.type] || {};
      const ready = this.controller && this.controller.ready(item.type);
      const waiting = pendingTypes.includes(item.type);
      let text = STATUS_TEXT[state.status] || "状态待确认";
      if (state.status === "has_quota") text = item.remaining_quota === -1 ? "长期授权有效" : `可发送 ${item.remaining_quota} 次`;
      if (state.status === "cooldown") text = `还需完成 ${state.cooldown_remaining} 条复习`;
      if (state.status === "pending" && ready) text = "待微信授权";
      if (waiting) text = "次数待确认 · 登记待恢复";
      return { type: item.type, label: item.label, description: item.description,
        enabled: item.enabled, managersOnly: item.managers_only, statusText: text,
        statusTone: state.status === "has_quota" && !waiting ? "suc" : "neutral",
        needsGrant: item.enabled && item.remaining_quota === 0 && !!item.template_id && !waiting,
        grantReady: ready && !waiting,
        needsWxSettings: ["remembered_reject", "main_switch_off"].includes(state.status) };
    });
    const hasQuota = items.some((item) => item.statusTone === "suc");
    const uncertain = pendingTypes.length || items.some((item) => item.statusText === "授权结果待确认");
    const grantCount = items.filter((item) => item.needsGrant).length;
    this.setData({ items, channelAvailable: available, channelReason: channel.reason || "",
      autoEnabled: view.choice === "enabled", granting: !!(this.controller && this.controller.busy()), grantCount,
      heroReady: available && hasQuota && !uncertain,
      heroTitle: uncertain ? "提醒次数待确认" : hasQuota ? "提醒已有可用次数" : grantCount ? "提醒需要补充次数" : "提醒尚未开启",
      lastSentLabel: notifications.lastSentLabel(settings.last_sent_at) });
  },
  async toggle(event) {
    const type = event.currentTarget.dataset.type;
    const item = this.data.items.find((entry) => entry.type === type);
    if (!item || this.data.togglingType || this.data.error) return;
    const token = this.loadGeneration;
    this.setData({ togglingType: type });
    try {
      await api.request("/notifications/preferences", { method: "PATCH", data: { type, enabled: event.detail.value === true } });
      if (token !== this.loadGeneration) return;
      await this.controller.refresh("manual");
    } catch (error) {
      if (token !== this.loadGeneration) return;
      const index = this.data.items.findIndex((entry) => entry.type === type);
      this.setData({ error: error.message, [`items[${index}].enabled`]: item.enabled });
    } finally { if (token === this.loadGeneration) this.setData({ togglingType: "" }); }
  },
  async toggleAuto(event) {
    if (this.data.autoSaving || this.data.error) return;
    const token = this.loadGeneration;
    this.setData({ autoSaving: true });
    const original = this.data.autoEnabled;
    try {
      await this.ensureController().setChoice(event.detail.value === true);
      if (token !== this.loadGeneration) return;
      await this.controller.refresh("manual");
    } catch (error) { if (token === this.loadGeneration) this.setData({ error: error.message, autoEnabled: original }); }
    finally { if (token === this.loadGeneration) this.setData({ autoSaving: false }); }
  },
  requestGrant(event) {
    if (!this.data.supported) return wx.showModal({ title: "当前微信版本不支持", content: "更新微信后再开启提醒。", showCancel: false });
    if (this.data.error || !this.data.channelAvailable || this.data.granting) return;
    const type = event && event.currentTarget && event.currentTarget.dataset.type;
    if (this.ensureController().grant(type)) this.setData({ granting: true });
  },
  openWxSettings() {
    if (typeof wx.openSetting === "function") wx.openSetting({ withSubscriptions: true,
      success: () => this.load() });
  },
  explain() {
    wx.showModal({ title: "关于提醒", content: "每次同意增加一次发送额度，不是永久订阅。自动补充仅在你点击完成复习时尝试；微信仍可能弹窗。普通拒绝或取消后，完成10条复习再询问。可随时关闭，提醒由微信尽力送达。", showCancel: false });
  }
});
