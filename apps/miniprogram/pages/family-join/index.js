const api = require("../../utils/api");

Page({
  data: { loading: true, error: "", preview: null, relationship: "", submitting: false, applied: false },
  onLoad(options) {
    this.token = decodeURIComponent(options.token || "");
    this.joinRequestKey = api.newIdempotencyKey("join");
    this.load();
  },
  async load() {
    if (!this.token) return this.setData({ loading: false, error: "邀请口令缺失" });
    this.setData({ loading: true, error: "" });
    try {
      const preview = await api.request("/family-invites/preview", { method: "POST", actorOnly: true, data: { token: this.token } });
      this.setData({ loading: false, preview: { ...preview, childLabel: preview.child_names.join("、") } });
    }
    catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  setRelationship(event) {
    this.joinRequestKey = api.newIdempotencyKey("join");
    this.setData({ relationship: event.detail.value });
  },
  async apply() {
    if (!this.data.relationship.trim()) return this.setData({ error: "请填写你与孩子的关系" });
    this.setData({ submitting: true, error: "" });
    try {
      const request = await api.request("/family-requests", { method: "POST", actorOnly: true, idempotencyKey: this.joinRequestKey, data: { token: this.token, relationship_label: this.data.relationship.trim() } });
      this.setData({ submitting: false, applied: true, requestCode: request.request_code });
    } catch (error) { this.setData({ submitting: false, error: error.message }); }
  },
  goPending() { wx.reLaunch({ url: "/pages/family-onboarding/index" }); }
});
