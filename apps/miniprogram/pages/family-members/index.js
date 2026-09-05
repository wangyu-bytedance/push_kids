const api = require("../../utils/api");

const ROLE_LABELS = { viewer: "仅查看", editor: "可共同记录", manager: "管理员" };
const ROLE_OPTIONS = [
  { value: "viewer", label: "仅查看" },
  { value: "editor", label: "可共同记录" },
  { value: "manager", label: "管理员" }
];

Page({
  data: {
    loading: true, error: "", family: null, members: [], requests: [], invites: [], inviteListUnavailable: false,
    isManager: false, sharing: false, shareReady: false, sharePath: "", requestCount: 0,
    showMember: false, selectedMember: null, relationshipDraft: "", roleOptions: ROLE_OPTIONS,
    roleIndex: 0, savingMember: false
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
      const members = memberItems.map((item) => ({ ...item, avatar: item.relationship_label.charAt(0), roleLabel: ROLE_LABELS[item.role] || item.role }));
      const invites = inviteItems.map((item) => ({ ...item, expiryLabel: String(item.expires_at).replace("T", " ").slice(0, 16) }));
      this.setData({ loading: false, family: bootstrap.family, members, isManager, requests, invites, inviteListUnavailable, requestCount: requests.length });
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
      this.setData({ sharing: false, shareReady: true, sharePath: invite.share_path });
      await this.load();
      wx.showToast({ title: "邀请已准备好", icon: "success" });
    } catch (error) { this.setData({ sharing: false, error: error.message }); }
  },
  onShareAppMessage(event) {
    if (event.from !== "button" || !this.data.shareReady || !this.data.sharePath) return { title: "家庭学习记录" };
    return { title: `邀请你加入${this.data.family ? this.data.family.display_name : "家庭"}`, path: this.data.sharePath };
  },
  revokeInvite(event) {
    const id = event.currentTarget.dataset.id;
    wx.showModal({ title: "撤销邀请？", content: "使用这条邀请提交但还未审批的申请也会失效。", confirmText: "撤销", confirmColor: "#A94F48", success: async (result) => {
      if (!result.confirm) return;
      try { await api.request(`/families/current/invites/${id}`, { method: "DELETE" }); await this.load(); }
      catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
    } });
  },
  openMember(event) {
    const member = this.data.members.find((item) => item.id === event.currentTarget.dataset.id);
    if (!member) return;
    this.setData({ showMember: true, selectedMember: member, relationshipDraft: member.relationship_label, roleIndex: Math.max(0, ROLE_OPTIONS.findIndex((item) => item.value === member.role)) });
  },
  closeMember() { if (!this.data.savingMember) this.setData({ showMember: false }); },
  setRelationship(event) { this.setData({ relationshipDraft: event.detail.value }); },
  chooseRole(event) { this.setData({ roleIndex: Number(event.detail.value) }); },
  async saveMember() {
    if (!this.data.isManager || !this.data.selectedMember) return;
    const relationship = this.data.relationshipDraft.trim();
    if (!relationship) return wx.showToast({ title: "请填写关系称谓", icon: "none" });
    const nextRole = ROLE_OPTIONS[this.data.roleIndex].value;
    if (!this.data.selectedMember.is_self && nextRole !== this.data.selectedMember.role) {
      const confirmed = await new Promise((resolve) => wx.showModal({ title: "确认更改权限", content: `将“${relationship}”的权限改为“${ROLE_LABELS[nextRole]}”？`, success: (result) => resolve(result.confirm) }));
      if (!confirmed) return;
    }
    this.setData({ savingMember: true });
    try {
      const data = { relationship_label: relationship };
      if (!this.data.selectedMember.is_self) data.role = nextRole;
      await api.request(`/families/current/members/${this.data.selectedMember.id}`, { method: "PATCH", data });
      this.setData({ savingMember: false, showMember: false });
      await this.load();
    } catch (error) { this.setData({ savingMember: false }); wx.showToast({ title: error.message, icon: "none" }); }
  },
  removeSelectedMember() {
    const member = this.data.selectedMember;
    if (!member || member.is_self) return;
    wx.showModal({ title: "移除家庭成员？", content: "移除后，对方将不能继续查看或记录这个家庭的内容，历史记录会保留。", confirmText: "移除", confirmColor: "#A94F48", success: async (result) => {
      if (!result.confirm) return;
      try { await api.request(`/families/current/members/${member.id}`, { method: "DELETE" }); this.setData({ showMember: false }); await this.load(); }
      catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
    } });
  }
});
