const api = require("../../utils/api");
const childContext = require("../../utils/child-context");

const BUDGET_OPTIONS = [10, 15, 20, 30, 45, 60];
const PRESET_SUBJECTS = ["语文", "数学", "英语"];
const GRADE_OPTIONS = ["暂不填写"].concat(childContext.GRADE_OPTIONS);

function budgetIndex(minutes) {
  const index = BUDGET_OPTIONS.indexOf(Number(minutes));
  return index < 0 ? BUDGET_OPTIONS.indexOf(15) : index;
}

function gradeIndex(grade) {
  const index = GRADE_OPTIONS.indexOf(grade || "");
  return index < 0 ? 0 : index;
}

Page({
  data: {
    mode: "create", childId: "", loading: false, error: "", saving: false, working: false,
    title: "新建学习档案", isManager: true, active: true,
    nameDraft: "", gradeOptions: GRADE_OPTIONS, gradeIndex: 0,
    budgetOptions: BUDGET_OPTIONS, budgetIndex: budgetIndex(15),
    presetSubjects: PRESET_SUBJECTS.map((name) => ({ name, selected: false })),
    limitReached: false, limitHint: childContext.limitHint()
  },
  onLoad(query = {}) {
    const mode = query.mode === "edit" ? "edit" : "create";
    const member = getApp().globalData.currentMember;
    this.setData({
      mode,
      childId: query.child_id || "",
      title: mode === "edit" ? "学习档案" : "新建学习档案",
      isManager: !member || member.role === "manager"
    });
    wx.setNavigationBarTitle({ title: this.data.title });
    this.load();
  },
  async load() {
    this.setData({ loading: true, error: "" });
    try {
      /* 归档档案也要能打开编辑页，否则家长没有恢复入口。 */
      const children = await api.request("/children?include_archived=true");
      if (this.data.mode === "create") {
        return this.setData({
          loading: false,
          limitReached: !childContext.canAddChild(children)
        });
      }
      const child = children.find((item) => item.id === this.data.childId);
      if (!child) {
        return this.setData({ loading: false, error: "这个学习档案已经不存在了" });
      }
      this.setData({
        loading: false,
        active: child.active !== false,
        nameDraft: child.name,
        gradeIndex: gradeIndex(child.grade),
        budgetIndex: budgetIndex(child.daily_budget_minutes)
      });
    } catch (error) {
      this.setData({ loading: false, error: error.message });
    }
  },
  setName(event) { this.setData({ nameDraft: event.detail.value, error: "" }); },
  chooseGrade(event) { this.setData({ gradeIndex: Number(event.detail.value) }); },
  chooseBudget(event) { this.setData({ budgetIndex: Number(event.detail.value) }); },
  togglePreset(event) {
    const index = Number(event.currentTarget.dataset.index);
    const presetSubjects = this.data.presetSubjects.map((item, position) => (
      position === index ? { ...item, selected: !item.selected } : item
    ));
    this.setData({ presetSubjects });
  },
  formPayload() {
    const grade = this.data.gradeIndex === 0 ? null : GRADE_OPTIONS[this.data.gradeIndex];
    return {
      name: this.data.nameDraft.trim(),
      grade,
      daily_budget_minutes: BUDGET_OPTIONS[this.data.budgetIndex]
    };
  },
  async save() {
    if (this.data.saving) return;
    const payload = this.formPayload();
    if (!payload.name) return this.setData({ error: "请填写孩子的名字，切换档案时要靠它区分。" });
    this.setData({ saving: true, error: "" });
    try {
      if (this.data.mode === "edit") {
        await api.request(`/children/${this.data.childId}`, { method: "PATCH", data: payload });
        wx.showToast({ title: "已保存", icon: "success" });
      } else {
        const selected = this.data.presetSubjects.filter((item) => item.selected).map((item) => item.name);
        const created = await api.request("/children", {
          method: "POST",
          data: { ...payload, subject_names: selected }
        });
        /* 新建后直接切到这个孩子，家长下一步大概率就是给他记录。 */
        getApp().selectChild(created.id);
        wx.showToast({ title: "档案已建立", icon: "success" });
      }
      this.setData({ saving: false });
      await getApp().refreshBootstrap(false).catch(() => {});
      wx.navigateBack();
    } catch (error) {
      /* 失败时保留表单内容，家长可以直接改名字再试。 */
      this.setData({ saving: false, error: `${error.message}。刚才填的内容还在，可以修改后再试。` });
    }
  },
  async archive() {
    if (this.data.working) return;
    const confirmed = await new Promise((resolve) => wx.showModal({
      title: `归档「${this.data.nameDraft}」？`,
      content: "归档后这个孩子不再出现在切换列表里，已有的学习记录、复习安排和报表都会保留，随时可以恢复。",
      confirmText: "归档",
      confirmColor: "#A85742",
      success: (result) => resolve(result.confirm)
    }));
    if (!confirmed) return;
    await this.lifecycle("archive", "已归档");
  },
  async restore() {
    if (this.data.working) return;
    await this.lifecycle("restore", "已恢复");
  },
  async lifecycle(action, toast) {
    this.setData({ working: true, error: "" });
    try {
      const child = await api.request(`/children/${this.data.childId}/${action}`, { method: "POST" });
      this.setData({ working: false, active: child.active !== false });
      wx.showToast({ title: toast, icon: "success" });
      /* 归档会改变全家的切换列表，回落交给 app 统一处理。 */
      await getApp().refreshBootstrap(false).catch(() => {});
      wx.navigateBack();
    } catch (error) {
      this.setData({ working: false, error: error.message });
    }
  }
});
