const api = require("../../utils/api");

const ROLE_LABELS = { viewer: "仅查看", editor: "可共同记录", manager: "管理员" };
const ROLE_DETAILS = { viewer: "不能修改记录", editor: "可记录与确认", manager: "可编辑与管理成员" };
const ROLE_OPTIONS = [
  { value: "viewer", label: "仅查看", text: "仅查看 · 不能修改记录" },
  { value: "editor", label: "可共同记录", text: "可共同记录 · 可记录与确认" },
  { value: "manager", label: "管理员", text: "管理员 · 可编辑与管理成员" }
];

/* 后端给的是 ISO 时间串，这里只做展示用的截断，不参与任何判断。 */
function timeLabel(value) {
  const text = String(value || "").replace("T", " ");
  return text.length >= 16 ? text.slice(5, 16) : text;
}

Page({
  data: {
    loading: true, error: "", family: null, members: [], requests: [], invites: [], inviteListUnavailable: false,
    isManager: false, sharing: false, shareReady: false, sharePath: "", requestCount: 0,
    showMember: false, selectedMember: null, relationshipDraft: "", roleOptions: ROLE_OPTIONS,
    roleIndex: 0, savingMember: false, sheetError: "", requestText: "", roleNote: "", copying: false
  },
  onShow() { this.load(); },
  onPullDownRefresh() { this.load().finally(() => wx.stopPullDownRefresh()); },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      const bootstrap = await getApp().refreshBootstrap(false);
      if (bootstrap.state !== "bound") return wx.reLaunch({ url: "/pages/family-onboarding/index" });
      const isManager = bootstrap.member.role === "manager";
      const work = [api.request("/families/current/members")];
      if (isManager) work.push(api.request("/families/current/requests"));
      const [memberItems, requests = []] = await Promise.all(work);
      let inviteItems = [];
      let inviteListUnavailable = false;
      if (isManager) {
        try { inviteItems = await api.request("/families/current/invites"); }
        catch { inviteListUnavailable = true; }
      }
      /* 角色文案、首字头像、时间文案都在这里算好，WXML 只做渲染。 */
      const members = memberItems.map((item) => ({
        ...item,
        avatar: item.relationship_label.charAt(0),
        roleLabel: ROLE_LABELS[item.role] || item.role,
        roleText: `${ROLE_LABELS[item.role] || item.role} · ${ROLE_DETAILS[item.role] || "由管理员设置"}`
      }));
      const invites = inviteItems.map((item) => ({ ...item, expiryLabel: timeLabel(item.expires_at) }));
      const selfRole = bootstrap.member.role;
      this.setData({ loading: false, family: bootstrap.family, members, isManager, requests, invites, inviteListUnavailable, requestCount: requests.length,
        requestText: requests.length ? `${requests.length} 份申请等待确认` : "暂时没有等待确认的申请",
        roleNote: `你在这个家庭是「${ROLE_LABELS[selfRole] || selfRole}」·${ROLE_DETAILS[selfRole] || "由管理员设置"}` });
    } catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  openRequests() { wx.navigateTo({ url: "/pages/family-requests/index" }); },
  async createInvite() {
    if (this.data.sharing) return;
    this.setData({ sharing: true, error: "" });
    if (!this.inviteRequestKey) this.inviteRequestKey = api.newIdempotencyKey("invite");
    try {
      const invite = await api.request("/families/current/invites", { method: "POST", idempotencyKey: this.inviteRequestKey, data: { expires_in_hours: 24 } });
      this.inviteRequestKey = api.newIdempotencyKey("invite");
      /* 口令只留在内存里供复制使用：不写入 data、不上屏、不打日志。 */
      this.inviteSecret = invite.token || "";
      this.setData({ sharing: false, shareReady: true, sharePath: invite.share_path });
      await this.load();
      wx.showToast({ title: "邀请已准备好", icon: "success" });
    } catch (error) { this.setData({ sharing: false, error: error.message }); }
  },
  copyInvite() {
    if (!this.inviteSecret) return wx.showToast({ title: "请先重新生成邀请", icon: "none" });
    wx.setClipboardData({
      data: this.inviteSecret,
      success: () => wx.showToast({ title: "邀请已复制", icon: "success" }),
      fail: () => wx.showToast({ title: "复制失败，可以改用微信邀请", icon: "none" })
    });
  },
  onShareAppMessage(event) {
    if (event.from !== "button" || !this.data.shareReady || !this.data.sharePath) return { title: "家庭学习记录" };
    return { title: `邀请你加入${this.data.family ? this.data.family.display_name : "家庭"}`, path: this.data.sharePath };
  },
  revokeInvite(event) {
    const id = event.currentTarget.dataset.id;
    wx.showModal({ title: "撤销邀请？", content: "使用这条邀请提交但还未审批的申请也会失效。", confirmText: "撤销", confirmColor: "#A6423B", success: async (result) => {
      if (!result.confirm) return;
      try { await api.request(`/families/current/invites/${id}`, { method: "DELETE" }); wx.showToast({ title: "邀请已撤销", icon: "success" }); await this.load(); }
      catch (error) { this.setData({ error: error.message }); wx.showToast({ title: error.message, icon: "none" }); }
    } });
  },
  openMember(event) {
    const member = this.data.members.find((item) => item.id === event.currentTarget.dataset.id);
    if (!member) return;
    this.setData({ showMember: true, sheetError: "", selectedMember: member, relationshipDraft: member.relationship_label, roleIndex: Math.max(0, ROLE_OPTIONS.findIndex((item) => item.value === member.role)) });
  },
  closeMember() { if (!this.data.savingMember) this.setData({ showMember: false, sheetError: "" }); },
  setRelationship(event) { this.setData({ relationshipDraft: event.detail.value, sheetError: "" }); },
  chooseRole(event) { this.setData({ roleIndex: Number(event.detail.value), sheetError: "" }); },
  async saveMember() {
    if (!this.data.isManager || !this.data.selectedMember || this.data.savingMember) return;
    const relationship = this.data.relationshipDraft.trim();
    if (!relationship) return this.setData({ sheetError: "请填写这位家人的称谓，家庭内会用它区分成员" });
    const nextRole = ROLE_OPTIONS[this.data.roleIndex].value;
    if (!this.data.selectedMember.is_self && nextRole !== this.data.selectedMember.role) {
      const confirmed = await new Promise((resolve) => wx.showModal({ title: "确认更改权限", content: `将“${relationship}”的权限改为“${ROLE_LABELS[nextRole]}·${ROLE_DETAILS[nextRole]}”？`, success: (result) => resolve(result.confirm) }));
      if (!confirmed) return;
    }
    this.setData({ savingMember: true, sheetError: "" });
    try {
      const data = { relationship_label: relationship };
      if (!this.data.selectedMember.is_self) data.role = nextRole;
      await api.request(`/families/current/members/${this.data.selectedMember.id}`, { method: "PATCH", data });
      this.setData({ savingMember: false, showMember: false });
      wx.showToast({ title: "已保存", icon: "success" });
      await this.load();
    } catch (error) { this.setData({ savingMember: false, sheetError: `${error.message}·刚才的修改没有保存，可以直接重试` }); }
  },
  removeSelectedMember() {
    const member = this.data.selectedMember;
    if (!member || member.is_self) return;
    wx.showModal({ title: "移除这位家人？", content: `移除后，“${member.relationship_label}”不能再查看或记录这个家庭的内容，已有的学习记录会保留。此操作不可撤销。`, confirmText: "移除", confirmColor: "#A6423B", success: async (result) => {
      if (!result.confirm) return;
      this.setData({ savingMember: true, sheetError: "" });
      try {
        await api.request(`/families/current/members/${member.id}`, { method: "DELETE" });
        this.setData({ savingMember: false, showMember: false });
        wx.showToast({ title: "已移除", icon: "success" });
        await this.load();
      }
      catch (error) { this.setData({ savingMember: false, sheetError: `${error.message}·这位家人还在家庭里，可以稍后重试` }); }
    } });
  }
});
