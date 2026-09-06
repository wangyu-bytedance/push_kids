const api = require("../../utils/api");

Page({
  data: {
    loading: true, error: "", family: null, children: [], members: [],
    mode: "", targetId: "", targetName: "", confirmationName: "",
    submitting: false, request: null
  },
  async onLoad() {
    const pendingId = wx.getStorageSync("activeDeletionRequestId") || "";
    if (pendingId) {
      this.setData({ loading: false });
      await this.loadRequest(pendingId);
      return;
    }
    await this.load();
  },
  onHide() { this.stopPolling(); },
  onUnload() { this.stopPolling(); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const bootstrap = await getApp().refreshBootstrap(false);
      if (bootstrap.state !== "bound") {
        wx.reLaunch({ url: "/pages/family-onboarding/index" });
        return;
      }
      if (!bootstrap.member || bootstrap.member.role !== "manager") {
        this.setData({ loading: false, error: "只有家庭管理员可以使用删除配置" });
        return;
      }
      const [children, members] = await Promise.all([
        api.request("/children?include_archived=true"),
        api.request("/families/current/members")
      ]);
      this.setData({ loading: false, family: bootstrap.family, children, members });
    } catch (error) {
      this.setData({ loading: false, error: error.message });
    }
  },
  chooseChild(event) {
    const child = this.data.children.find((item) => item.id === event.currentTarget.dataset.id);
    if (!child) return;
    this.requestKey = api.newIdempotencyKey("delete-child");
    this.setData({ mode: "child", targetId: child.id, targetName: child.name, confirmationName: "", error: "" });
  },
  chooseFamily() {
    if (this.data.members.length !== 1) return;
    this.requestKey = api.newIdempotencyKey("delete-family");
    this.setData({ mode: "family", targetId: this.data.family.id, targetName: this.data.family.display_name, confirmationName: "", error: "" });
  },
  setConfirmation(event) { this.setData({ confirmationName: event.detail.value, error: "" }); },
  cancelConfirmation() {
    if (this.data.submitting) return;
    this.setData({ mode: "", targetId: "", targetName: "", confirmationName: "", error: "" });
  },
  async submitDeletion() {
    if (this.data.submitting || this.data.confirmationName.trim() !== this.data.targetName.trim()) return;
    const path = this.data.mode === "family"
      ? "/families/current/deletion-requests"
      : `/children/${this.data.targetId}/deletion-requests`;
    this.setData({ submitting: true, error: "" });
    try {
      const request = await api.request(path, {
        method: "POST",
        idempotencyKey: this.requestKey,
        data: { confirmation_name: this.data.confirmationName.trim() }
      });
      wx.setStorageSync("activeDeletionRequestId", request.id);
      this.setData({ submitting: false, request });
      this.schedulePoll();
    } catch (error) {
      this.setData({ submitting: false, error: error.message });
    }
  },
  async loadRequest(requestId) {
    try {
      const request = await api.request(`/deletion-requests/${requestId}`, { actorOnly: true });
      this.setData({ loading: false, request, mode: request.target_type, error: "" });
      if (request.state === "succeeded") return this.finish(request.target_type);
      if (request.state === "queued" || request.state === "running") this.schedulePoll();
    } catch (error) {
      wx.removeStorageSync("activeDeletionRequestId");
      this.setData({ loading: false, request: null, error: error.message });
    }
  },
  schedulePoll() {
    this.stopPolling();
    const request = this.data.request;
    if (!request || (request.state !== "queued" && request.state !== "running")) return;
    this.pollTimer = setTimeout(() => this.loadRequest(request.id), 1500);
  },
  stopPolling() {
    if (this.pollTimer) clearTimeout(this.pollTimer);
    this.pollTimer = null;
  },
  async refreshRequest() {
    if (this.data.request) await this.loadRequest(this.data.request.id);
  },
  async retryRequest() {
    if (!this.data.request || this.data.submitting) return;
    this.setData({ submitting: true, error: "" });
    try {
      const request = await api.request(`/deletion-requests/${this.data.request.id}/retry`, { method: "POST", actorOnly: true });
      this.setData({ submitting: false, request });
      this.schedulePoll();
    } catch (error) {
      this.setData({ submitting: false, error: error.message });
    }
  },
  async finish(targetType) {
    this.stopPolling();
    wx.removeStorageSync("activeDeletionRequestId");
    if (targetType === "family") {
      getApp().globalData.familyId = "";
      getApp().selectChild("");
      await getApp().refreshBootstrap(false).catch(() => {});
      wx.reLaunch({ url: "/pages/family-onboarding/index" });
      return;
    }
    await getApp().refreshBootstrap(false).catch(() => {});
    wx.showToast({ title: "资料已清理", icon: "success" });
    wx.navigateBack();
  }
});
