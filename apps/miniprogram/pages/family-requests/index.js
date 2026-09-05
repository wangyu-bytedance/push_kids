const api = require("../../utils/api");

Page({
  data: { loading: true, error: "", requests: [], actingId: "" },
  onShow() { this.load(); },
  onPullDownRefresh() { this.load().finally(() => wx.stopPullDownRefresh()); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const requests = (await api.request("/families/current/requests")).map((item) => ({ ...item, createdLabel: String(item.created_at).replace("T", " ").slice(0, 16) }));
      this.setData({ loading: false, requests, actingId: "" });
    }
    catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  async approve(event) {
    const { id, role } = event.currentTarget.dataset;
    if (this.data.actingId) return;
    const item = this.data.requests.find((request) => request.id === id);
    const labels = { viewer: "仅查看", editor: "可共同记录", manager: "管理员" };
    const confirmed = await new Promise((resolve) => wx.showModal({ title: "确认同意申请", content: `申请码 ${item ? item.request_code : ""}\n关系称谓：${item ? item.relationship_label : ""}\n授权为：${labels[role]}`, confirmText: "确认同意", success: (result) => resolve(result.confirm) }));
    if (!confirmed) return;
    if (!this.actionRetryKeys) this.actionRetryKeys = {};
    const operation = `approve:${id}:${role}`;
    const idempotencyKey = this.actionRetryKeys[operation] || api.newIdempotencyKey("approve");
    this.actionRetryKeys[operation] = idempotencyKey;
    this.setData({ actingId: id, error: "" });
    try { await api.request(`/family-requests/${id}/approve`, { method: "POST", idempotencyKey, data: { role } }); delete this.actionRetryKeys[operation]; await this.load(); }
    catch (error) { this.setData({ actingId: "", error: error.message }); }
  },
  reject(event) {
    if (this.data.actingId) return;
    const id = event.currentTarget.dataset.id;
    wx.showModal({ title: "拒绝这次申请？", content: "对方不会获得家庭内容访问权限。", confirmColor: "#A94F48", success: async (result) => {
      if (!result.confirm) return;
      if (!this.actionRetryKeys) this.actionRetryKeys = {};
      const operation = `reject:${id}`;
      const idempotencyKey = this.actionRetryKeys[operation] || api.newIdempotencyKey("reject");
      this.actionRetryKeys[operation] = idempotencyKey;
      this.setData({ actingId: id });
      try { await api.request(`/family-requests/${id}/reject`, { method: "POST", idempotencyKey, data: {} }); delete this.actionRetryKeys[operation]; await this.load(); }
      catch (error) { this.setData({ actingId: "", error: error.message }); }
    } });
  }
});
