const api = require("../../utils/api");

Page({
  data: {
    loading: true, state: "unbound", mode: "choice", error: "", submitting: false,
    familyName: "", childName: "", grade: "小学", relationship: "妈妈", budget: 15
  },
  onLoad() { this.familyRequestKey = api.newIdempotencyKey("family"); this.load(); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const result = await getApp().refreshBootstrap(false);
      if (result.state === "bound") return wx.reLaunch({ url: "/pages/today/index" });
      this.setData({ loading: false, state: result.state, request: result.request || null });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  chooseCreate() { this.setData({ mode: "create", error: "" }); },
  backToChoice() { this.setData({ mode: "choice", error: "" }); },
  setField(event) {
    this.familyRequestKey = api.newIdempotencyKey("family");
    this.setData({ [event.currentTarget.dataset.field]: event.detail.value });
  },
  openJoin() { this.setData({ mode: "join" }); },
  openToken() {
    const token = (this.data.inviteToken || "").trim();
    if (!token) return this.setData({ error: "请输入邀请口令" });
    wx.navigateTo({ url: `/pages/family-join/index?token=${encodeURIComponent(token)}` });
  },
  async submitFamily() {
    const childName = this.data.childName.trim();
    const familyName = this.data.familyName.trim() || (childName ? `${childName}的家` : "");
    if (!childName || !familyName || !this.data.relationship.trim()) return this.setData({ error: "请完整填写家庭、孩子和关系信息" });
    this.setData({ submitting: true, error: "" });
    try {
      const result = await api.request("/families", {
        method: "POST", idempotencyKey: this.familyRequestKey, actorOnly: true,
        data: { display_name: familyName, relationship_label: this.data.relationship.trim(), child: { name: childName, grade: this.data.grade.trim() || null, daily_budget_minutes: Number(this.data.budget) } }
      });
      getApp().globalData.familyId = result.family.id;
      if (result.children.length) getApp().selectChild(result.children[0].id);
      wx.reLaunch({ url: "/pages/today/index" });
    } catch (error) { this.setData({ submitting: false, error: error.message }); }
  },
  async cancelRequest() {
    try { await api.request("/family-requests/current", { method: "DELETE", actorOnly: true }); await this.load(); }
    catch (error) { this.setData({ error: error.message }); }
  }
});
