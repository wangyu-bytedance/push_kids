const api = require("../../utils/api");

/* 与首次引导保持同一套称谓选项：家长选完就能提交，选「其他」再展开自由输入。 */
const RELATIONS = ["妈妈", "爸爸", "奶奶", "爷爷", "外婆", "外公", "其他"];

Page({
  data: {
    loading: true, error: "", preview: null, relationship: "", submitting: false, applied: false,
    relations: RELATIONS, relationIndex: -1, relationText: "请选择", customRelation: false,
    requestCode: "", submitHint: "选择你与孩子的关系后就可以提交", canSubmit: false, tokenMissing: false
  },
  onLoad(options) {
    this.token = decodeURIComponent(options.token || "");
    this.joinRequestKey = api.newIdempotencyKey("join");
    this.load();
  },
  async load() {
    if (!this.token) return this.setData({ loading: false, tokenMissing: true, error: "邀请口令缺失" });
    this.setData({ loading: true, error: "" });
    try {
      const preview = await api.request("/family-invites/preview", { method: "POST", actorOnly: true, data: { token: this.token } });
      this.setData({
        loading: false,
        preview: {
          ...preview,
          childLabel: preview.child_names.join("、"),
          childCount: preview.child_names.length,
          mark: preview.family_name ? preview.family_name.charAt(0) : "家"
        }
      });
    }
    catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  chooseRelation(event) {
    this.joinRequestKey = api.newIdempotencyKey("join");
    const relationIndex = Number(event.detail.value);
    const custom = RELATIONS[relationIndex] === "其他";
    this.setData({
      relationIndex,
      customRelation: custom,
      relationText: RELATIONS[relationIndex],
      relationship: custom ? "" : RELATIONS[relationIndex]
    }, () => this.syncSubmitState());
  },
  setRelationship(event) {
    this.joinRequestKey = api.newIdempotencyKey("join");
    this.setData({ relationship: event.detail.value }, () => this.syncSubmitState());
  },
  syncSubmitState() {
    const ready = !!String(this.data.relationship || "").trim();
    this.setData({ canSubmit: ready, submitHint: ready ? "" : "选择你与孩子的关系后就可以提交" });
  },
  async apply() {
    if (this.data.submitting) return;
    if (!this.data.relationship.trim()) return this.setData({ error: "请先选择你与孩子的关系" });
    this.setData({ submitting: true, error: "" });
    try {
      const request = await api.request("/family-requests", { method: "POST", actorOnly: true, idempotencyKey: this.joinRequestKey, data: { token: this.token, relationship_label: this.data.relationship.trim() } });
      this.setData({ submitting: false, applied: true, requestCode: request.request_code });
      wx.showToast({ title: "申请已发送", icon: "success" });
    } catch (error) { this.setData({ submitting: false, error: error.message }); }
  },
  copyRequestCode() {
    if (!this.data.requestCode) return;
    wx.setClipboardData({ data: this.data.requestCode, success: () => wx.showToast({ title: "申请码已复制", icon: "success" }) });
  },
  goPending() { wx.reLaunch({ url: "/pages/family-onboarding/index" }); },
  goBack() { wx.navigateBack({ fail: () => wx.reLaunch({ url: "/pages/family-onboarding/index" }) }); }
});
