const api = require("../../utils/api");

/* 角色文案集中在这里：WXML 只渲染，不做拼装。 */
const ROLE_OPTIONS = [
  { value: "viewer", label: "仅查看", text: "仅查看 · 不能修改记录" },
  { value: "editor", label: "可共同记录", text: "可共同记录 · 可记录与确认" },
  { value: "manager", label: "管理员", text: "管理员 · 可编辑与管理成员" }
];
const ROLE_LABELS = { viewer: "仅查看", editor: "可共同记录", manager: "管理员" };

/* 后端给的是 ISO 时间串，这里只做展示截断，不参与任何判断。 */
function timeLabel(value) {
  const text = String(value || "").replace("T", " ");
  return text.length >= 16 ? text.slice(5, 16) : text;
}

Page({
  data: {
    loading: true, error: "", requests: [], actingId: "", isManager: true,
    roleOptions: ROLE_OPTIONS, roleNote: ""
  },
  onShow() { this.load(); },
  onUnload() { if (this.resultTimer) clearTimeout(this.resultTimer); },
  onPullDownRefresh() { this.load().finally(() => wx.stopPullDownRefresh()); },
  async load() {
    if (this.resultTimer) { clearTimeout(this.resultTimer); this.resultTimer = null; }
    this.setData({ loading: true, error: "" });
    try {
      const bootstrap = await getApp().refreshBootstrap(false);
      if (bootstrap.state !== "bound") return wx.reLaunch({ url: "/pages/family-onboarding/index" });
      const isManager = bootstrap.member.role === "manager";
      if (!isManager) {
        /* 只读/协作成员不该看到审批入口，这里诚实降级而不是让他点了报错。 */
        return this.setData({ loading: false, isManager: false, requests: [], actingId: "",
          roleNote: `你在这个家庭是「${ROLE_LABELS[bootstrap.member.role] || bootstrap.member.role}」，加入申请由管理员确认。` });
      }
      /* 展示字段（时间、首字头像、默认权限选项）在这里算好。 */
      const requests = (await api.request("/families/current/requests")).map((item) => ({
        ...item,
        createdLabel: timeLabel(item.created_at),
        avatar: String(item.relationship_label || "申").charAt(0),
        roleIndex: 1,
        roleValue: ROLE_OPTIONS[1].value,
        roleText: ROLE_OPTIONS[1].text,
        resultText: "",
        rowError: ""
      }));
      this.setData({ loading: false, isManager: true, requests, actingId: "", roleNote: "" });
    }
    catch (error) { this.setData({ loading: false, error: error.message }); }
  },
  chooseRole(event) {
    const index = Number(event.currentTarget.dataset.index);
    const pick = ROLE_OPTIONS[Number(event.detail.value)] || ROLE_OPTIONS[0];
    this.setData({
      [`requests[${index}].roleIndex`]: ROLE_OPTIONS.indexOf(pick),
      [`requests[${index}].roleValue`]: pick.value,
      [`requests[${index}].roleText`]: pick.text,
      [`requests[${index}].rowError`]: ""
    });
  },
  copyCode(event) {
    const code = event.currentTarget.dataset.code;
    wx.setClipboardData({
      data: String(code || ""),
      success: () => wx.showToast({ title: "申请码已复制", icon: "success" }),
      fail: () => wx.showToast({ title: "复制失败，可手动核对", icon: "none" })
    });
  },
  async approve(event) {
    if (this.data.actingId) return;
    const index = Number(event.currentTarget.dataset.index);
    const item = this.data.requests[index];
    if (!item) return;
    const role = item.roleValue;
    const confirmed = await new Promise((resolve) => wx.showModal({
      title: "确认同意申请",
      content: `申请码 ${item.request_code}\n关系称谓：${item.relationship_label}\n授权为：${ROLE_LABELS[role]}\n同意后，对方可以看到这个家庭所有孩子的学习记录和照片。`,
      confirmText: "确认同意",
      success: (result) => resolve(result.confirm)
    }));
    if (!confirmed) return;
    await this.decide("approve", index, role);
  },
  reject(event) {
    if (this.data.actingId) return;
    const index = Number(event.currentTarget.dataset.index);
    const item = this.data.requests[index];
    if (!item) return;
    wx.showModal({ title: "拒绝这次申请？", content: `拒绝后，“${item.relationship_label}”不会获得这个家庭内容的访问权限。对方可以重新申请。`, confirmText: "拒绝", confirmColor: "#A85742", success: async (result) => {
      if (!result.confirm) return;
      await this.decide("reject", index, "");
    } });
  },
  /* 写操作三态统一走这里：pending 就地 loading，成功就地留结果 2 秒，失败保留卡片并给重试入口。 */
  async decide(kind, index, role) {
    const item = this.data.requests[index];
    if (!item) return;
    const id = item.id;
    if (!this.actionRetryKeys) this.actionRetryKeys = {};
    const operation = kind === "approve" ? `approve:${id}:${role}` : `reject:${id}`;
    const idempotencyKey = this.actionRetryKeys[operation] || api.newIdempotencyKey(kind);
    this.actionRetryKeys[operation] = idempotencyKey;
    this.setData({ actingId: id, error: "", [`requests[${index}].rowError`]: "" });
    try {
      if (kind === "approve") await api.request(`/family-requests/${id}/approve`, { method: "POST", idempotencyKey, data: { role } });
      else await api.request(`/family-requests/${id}/reject`, { method: "POST", idempotencyKey, data: {} });
      delete this.actionRetryKeys[operation];
      this.setData({
        actingId: "",
        [`requests[${index}].resultText`]: kind === "approve" ? `已同意加入 · ${ROLE_LABELS[role]}` : "已拒绝这次申请"
      });
      wx.showToast({ title: kind === "approve" ? "已同意加入" : "已拒绝申请", icon: "success" });
      this.resultTimer = setTimeout(() => { this.resultTimer = null; this.load(); }, 2000);
    }
    catch (error) {
      this.setData({
        actingId: "",
        [`requests[${index}].rowError`]: `${error.message}·这条申请还在等待处理，可以直接重试`
      });
    }
  }
});
