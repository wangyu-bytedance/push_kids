const api = require("../../utils/api");

/* 年级与关系都只是家庭内部的展示标签，用原生 picker 收敛输入，避免自由文本写脏数据。 */
const GRADES = ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "其他"];
const RELATIONS = ["妈妈", "爸爸", "奶奶", "爷爷", "外婆", "外公", "其他"];
const DEFAULT_GRADE_INDEX = 2;

Page({
  data: {
    loading: true, state: "unbound", mode: "choice", error: "", submitting: false,
    familyName: "", childName: "", grade: GRADES[DEFAULT_GRADE_INDEX], relationship: RELATIONS[0], budget: 15,
    grades: GRADES, relations: RELATIONS, gradeIndex: DEFAULT_GRADE_INDEX, relationIndex: 0, customRelation: false,
    familyPlaceholder: "不填时使用「孩子称呼」的家", canSubmit: false, submitHint: "填写孩子称呼后就可以创建",
    inviteToken: "", tokenError: "", request: null, refreshing: false, canceling: false
  },
  onLoad() { this.familyRequestKey = api.newIdempotencyKey("family"); this.load(); },
  onPullDownRefresh() { this.load().finally(() => wx.stopPullDownRefresh()); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const result = await getApp().refreshBootstrap(false);
      if (result.state === "bound") return wx.reLaunch({ url: "/pages/today/index" });
      this.setData({ loading: false, state: result.state, request: result.request || null });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  chooseCreate() { this.setData({ mode: "create", error: "" }); },
  backToChoice() { this.setData({ mode: "choice", error: "", tokenError: "" }); },
  setField(event) {
    this.familyRequestKey = api.newIdempotencyKey("family");
    const field = event.currentTarget.dataset.field;
    const value = event.detail.value;
    const patch = { [field]: value, error: "" };
    if (field === "childName") {
      const name = String(value).trim();
      patch.familyPlaceholder = name ? `不填时使用「${name}的家」` : "不填时使用「孩子称呼」的家";
    }
    if (field === "inviteToken") patch.tokenError = "";
    this.setData(patch, () => this.syncSubmitState());
  },
  /* 主按钮的可用性与缺什么的说明都在 js 里算好，WXML 只做渲染。 */
  syncSubmitState() {
    const hasChild = !!this.data.childName.trim();
    const hasRelation = !!String(this.data.relationship || "").trim();
    this.setData({
      canSubmit: hasChild && hasRelation,
      submitHint: hasChild ? (hasRelation ? "" : "还需要填写你与孩子的关系") : "填写孩子称呼后就可以创建"
    });
  },
  chooseGrade(event) {
    this.familyRequestKey = api.newIdempotencyKey("family");
    const gradeIndex = Number(event.detail.value);
    this.setData({ gradeIndex, grade: GRADES[gradeIndex] });
  },
  /* 选「其他」时展开自由输入，保留家长自己写称谓的能力。 */
  chooseRelation(event) {
    this.familyRequestKey = api.newIdempotencyKey("family");
    const relationIndex = Number(event.detail.value);
    const custom = RELATIONS[relationIndex] === "其他";
    this.setData({
      relationIndex,
      customRelation: custom,
      relationship: custom ? "" : RELATIONS[relationIndex]
    }, () => this.syncSubmitState());
  },
  openJoin() { this.setData({ mode: "join", error: "", tokenError: "" }); },
  openToken() {
    /* 口令区分大小写，不做任何大小写转换；页面与日志都不回显口令内容。 */
    const token = (this.data.inviteToken || "").trim();
    if (!token) return this.setData({ tokenError: "请粘贴家人发来的邀请口令，口令区分大小写" });
    wx.navigateTo({ url: `/pages/family-join/index?token=${encodeURIComponent(token)}` });
  },
  async submitFamily() {
    /* 按钮在未满足条件时是 disabled 样式，这里再兜一层，避免误触发写请求。 */
    if (this.data.submitting || !this.data.canSubmit) return;
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
      wx.showToast({ title: "家庭已建立", icon: "success" });
      wx.reLaunch({ url: "/pages/today/index" });
    } catch (error) { this.setData({ submitting: false, error: error.message }); }
  },
  /* 等待确认态：显式的刷新入口，避免家长以为页面卡住。 */
  async refreshStatus() {
    if (this.data.refreshing) return;
    this.setData({ refreshing: true });
    await this.load();
    this.setData({ refreshing: false });
    if (this.data.state === "pending" && !this.data.error) wx.showToast({ title: "还在等待确认", icon: "none" });
  },
  copyRequestCode() {
    const code = this.data.request ? this.data.request.request_code : "";
    if (!code) return;
    wx.setClipboardData({ data: code, success: () => wx.showToast({ title: "申请码已复制", icon: "success" }) });
  },
  cancelRequest() {
    if (this.data.canceling) return;
    wx.showModal({
      title: "撤回这次申请？",
      content: "撤回后管理员就看不到这条申请了，你可以重新用邀请口令再申请一次。",
      confirmText: "撤回申请", confirmColor: "#A85742",
      success: async (result) => {
        if (!result.confirm) return;
        this.setData({ canceling: true, error: "" });
        try {
          await api.request("/family-requests/current", { method: "DELETE", actorOnly: true });
          this.setData({ canceling: false, mode: "choice" });
          wx.showToast({ title: "申请已撤回", icon: "success" });
          await this.load();
        } catch (error) { this.setData({ canceling: false, error: error.message }); }
      }
    });
  }
});
