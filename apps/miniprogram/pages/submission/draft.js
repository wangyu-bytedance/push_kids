/* PKDS-1.0 · 可编辑草稿（AI 草稿 / 人工录入）的共享逻辑。
   确认页与「待处理记录」页共用同一份数据与方法：家长在待确认页就能直接改、直接确认。
   多科目：一次上传可能混着几个科目，草稿按孩子已配置的科目分组，绝不合成「数学、语文」这种混合科目。 */

const api = require("../../utils/api");
const ui = require("../../utils/ui");
const renew = require("../../utils/renew");

/* 科目选择器最后一项：让家长自己写一个新科目名，仍需明确同意才会真的新增。 */
const NEW_SUBJECT_OPTION = "＋ 写一个新科目";

function emptyPoint() {
  return { name: "", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 };
}

/* WXML 不支持方法调用，草稿里的展示字段都在这里算好。 */
function pointView(point) {
  const conf = ui.confidence(point.confidence);
  const evidenceLabels = (point.direct_evidence || []).map(
    (evidence) => `${evidence.source === "image" ? "照片 " + evidence.image_index : "家长文字"}：${evidence.detail}`
  );
  return {
    ...point,
    subject_name: point.subject_name || "",
    confidence_label: conf ? conf.label : "请核对",
    confidence_tone: conf ? conf.tone : "",
    confidence_level: conf ? conf.level : 0,
    evidence_labels: evidenceLabels,
    evidence_text: evidenceLabels.join("　·　"),
    context_count: (point.context_used || []).length
  };
}

/* 科目选择项 = 已在学的科目 + 草稿里出现过但还没配置的科目 + 「写一个新科目」。 */
function subjectPicks(subjects, points) {
  const names = subjects.map((item) => item.name);
  (points || []).forEach((point) => {
    const name = (point.subject_name || "").trim();
    if (name && !names.includes(name)) names.push(name);
  });
  return names.concat([NEW_SUBJECT_OPTION]);
}

/* 按知识点上的科目名分组：一个科目一张卡、一条正式学习记录。
   分组顺序按第一次出现的位置，家长看到的顺序和知识点列表一致。 */
function buildGroups(points, subjects, consent) {
  const listed = {};
  subjects.forEach((item) => { listed[item.name] = item; });
  const order = [];
  const byName = {};
  (points || []).forEach((point, index) => {
    const name = (point.subject_name || "").trim();
    if (!byName[name]) {
      byName[name] = { subject_name: name, indexes: [], names: [] };
      order.push(name);
    }
    byName[name].indexes.push(index);
    if (point.name && point.name.trim()) byName[name].names.push(point.name.trim());
  });
  return order.map((name) => {
    const group = byName[name];
    const subject = listed[name];
    return {
      key: name || "_unset",
      subject_name: name,
      subject_id: subject ? subject.id : null,
      listed: !!subject,
      create_subject: !subject && !!(consent || {})[name],
      indexes: group.indexes,
      count: group.indexes.length,
      names_text: group.names.join("、"),
      mark: ui.subjectMark(name),
      mark_class: ui.subjectClass(name, "learning")
    };
  });
}

/* 提交前把草稿收成后端要的形状：先丢掉空知识点，再按过滤后的位置写 knowledge_indexes，
   这样服务端的分组与家长在界面上看到的完全一致。 */
function confirmPayload(proposal, subjects, consent, options) {
  const points = (proposal.knowledge_points || []).filter((item) => (item.name || "").trim());
  const groups = buildGroups(points, subjects, consent).map((group) => ({
    subject_id: group.subject_id,
    subject_name: group.subject_name,
    create_subject: group.create_subject,
    summary: null,
    knowledge_indexes: group.indexes
  }));
  return {
    manual_entry: !!(options || {}).manual,
    subject_id: groups.length === 1 ? groups[0].subject_id : null,
    create_subject: groups.length === 1 ? groups[0].create_subject : false,
    proposal: { ...proposal, subject_name: groups.length ? groups[0].subject_name : "", knowledge_points: points },
    groups
  };
}

module.exports = {
  NEW_SUBJECT_OPTION,
  pointView,
  buildGroups,
  subjectPicks,
  confirmPayload,
  data: {
    manual: false, saving: false, saveError: "", conflict: false, editing: false,
    proposal: null, subjects: [], subjectPicks: [], groups: [], subjectReview: false,
    consent: {}
  },
  methods: {
    /* 把 pending_confirmation 的草稿准备成可编辑状态；人工录入时给一份空草稿。 */
    async prepareDraft(submission, manual) {
      const subjects = (await api.request(`/children/${submission.child_id}/subjects`))
        .filter((item) => item.kind === "learning" && item.active !== false);
      const initial = manual ? {
        summary: (submission.input_text || "").length <= 500 ? (submission.input_text || "") : "",
        subject_name: "", subject_kind: "learning", source: "人工录入", uncertainties: [], todo_matches: [],
        knowledge_points: [emptyPoint()]
      } : (submission.proposal || { summary: "", subject_name: "", subject_kind: "learning", source: "照片", uncertainties: [], todo_matches: [], knowledge_points: [emptyPoint()] });
      /* 后端已按孩子的科目表把每个知识点路由好；旧草稿没有分点科目时回落到整批科目名。 */
      const points = (initial.knowledge_points.length ? initial.knowledge_points : [emptyPoint()])
        .map((point) => pointView({ ...point, subject_name: point.subject_name || initial.subject_name || "" }));
      const proposal = { ...initial, uncertainties: initial.uncertainties || [], todo_matches: initial.todo_matches || [], knowledge_points: points };
      this.setData({
        manual: !!manual, editing: true, proposal, subjects, consent: {},
        subjectPicks: subjectPicks(subjects, points),
        groups: buildGroups(points, subjects, {}),
        subjectReview: !manual && !!submission.subject_review_needed,
        saveError: "", conflict: false
      });
    },
    /* 每次改动知识点或科目后重算分组，界面上「科目归类」始终是提交时的真实分组。 */
    refreshGroups() {
      const points = this.data.proposal.knowledge_points;
      this.setData({
        groups: buildGroups(points, this.data.subjects, this.data.consent),
        subjectPicks: subjectPicks(this.data.subjects, points)
      });
    },
    setProposal(event) {
      this.setData({ [`proposal.${event.currentTarget.dataset.field}`]: event.detail.value });
    },
    clearAssociations(points) {
      return points.map((point) => ({ ...point, existing_knowledge_id: null }));
    },
    unlinkPoint(event) {
      this.setData({ [`proposal.knowledge_points[${Number(event.currentTarget.dataset.index)}].existing_knowledge_id`]: null });
    },
    setPoint(event) {
      const { index, field } = event.currentTarget.dataset;
      this.setData({ [`proposal.knowledge_points[${index}].${field}`]: field === "estimated_minutes" ? Number(event.detail.value) : event.detail.value });
      if (field === "name" || field === "category") {
        this.setData({ [`proposal.knowledge_points[${index}].existing_knowledge_id`]: null });
      }
      if (field === "name") this.refreshGroups();
    },
    /* 换科目会断开与已有知识点的关联：换了科目就不再是同一条复习进度。 */
    async movePointSubject(event) {
      const index = Number(event.currentTarget.dataset.index);
      const name = await this.pickedSubjectName(Number(event.detail.value));
      if (!name) return;
      const points = this.data.proposal.knowledge_points.map((point, position) => (
        position === index ? { ...point, subject_name: name, existing_knowledge_id: null } : point
      ));
      this.setData({ "proposal.knowledge_points": points });
      this.refreshGroups();
    },
    /* 整组换科目：识别出的新科目如果其实就是已有科目，一次点掉就好。 */
    async moveGroupSubject(event) {
      const group = this.data.groups[Number(event.currentTarget.dataset.group)];
      const name = await this.pickedSubjectName(Number(event.detail.value));
      if (!name || !group) return;
      const points = this.data.proposal.knowledge_points.map((point, position) => (
        group.indexes.includes(position) ? { ...point, subject_name: name, existing_knowledge_id: null } : point
      ));
      this.setData({ "proposal.knowledge_points": points });
      this.refreshGroups();
    },
    async pickedSubjectName(pickerIndex) {
      const picks = this.data.subjectPicks;
      const chosen = picks[pickerIndex];
      if (chosen !== NEW_SUBJECT_OPTION) return chosen || "";
      const typed = await new Promise((resolve) => wx.showModal({
        title: "写一个新科目",
        content: "",
        editable: true,
        placeholderText: "例如：科学",
        success: (result) => resolve(result.confirm ? String(result.content || "").trim() : ""),
        fail: () => resolve("")
      }));
      if (!typed) return "";
      if (typed.length > 40) { wx.showToast({ title: "科目名请写短一些", icon: "none" }); return ""; }
      return typed;
    },
    /* 新科目要不要真的加进科目表，由家长在这里回答，模型不能替家长决定。 */
    toggleCreateSubject(event) {
      const group = this.data.groups[Number(event.currentTarget.dataset.group)];
      if (!group) return;
      const consent = { ...this.data.consent, [group.subject_name]: !!event.detail.value };
      this.setData({ consent });
      this.refreshGroups();
    },
    addPoint() {
      const points = this.data.proposal.knowledge_points;
      if (points.length >= 20) return wx.showToast({ title: "最多 20 个知识点", icon: "none" });
      /* 新知识点默认跟着最后一个知识点的科目，家长少点一次。 */
      const last = points[points.length - 1];
      const next = points.concat([pointView({ ...emptyPoint(), subject_name: last ? last.subject_name : "" })]);
      this.setData({ "proposal.knowledge_points": next });
      this.refreshGroups();
    },
    removePoint(event) {
      const points = this.data.proposal.knowledge_points.slice();
      points.splice(Number(event.currentTarget.dataset.index), 1);
      this.setData({ "proposal.knowledge_points": points.length ? points : [pointView(emptyPoint())] });
      this.refreshGroups();
    },
    removeTodoMatch(event) {
      const matches = this.data.proposal.todo_matches.slice();
      matches.splice(Number(event.currentTarget.dataset.index), 1);
      this.setData({ "proposal.todo_matches": matches });
    },
    async confirmDraft() {
      if (this.data.saving || !this.data.proposal) return;
      const proposal = this.data.proposal;
      if (!String(proposal.summary || "").trim()) return wx.showToast({ title: "请补全学习总结", icon: "none" });
      const kept = proposal.knowledge_points.filter((item) => (item.name || "").trim());
      if (!kept.length) return wx.showToast({ title: "至少保留一个知识点", icon: "none" });
      const missing = kept.some((item) => !(item.subject_name || "").trim());
      if (missing) return wx.showToast({ title: "请为每个知识点选择科目", icon: "none" });
      this.setData({ saving: true, saveError: "" });
      /* 确认入库会生成复习计划，也就意味着之后要发提醒；趁这次点击手势把额度续上。 */
      renew.maybeTopUp();
      try {
        await this.postConfirm();
        wx.showToast({ title: "已确认入库", icon: "success" });
        this.setData({ saving: false, editing: false });
        if (this.afterConfirm) return this.afterConfirm();
      } catch (error) {
        this.setData({ saving: false, saveError: error.message, conflict: error.statusCode === 409 && error.code !== "consent_required" });
        if (!(error.code === "consent_required")) wx.showToast({ title: error.message, icon: "none" });
      }
    },
    /* 后端只在家长明确同意后才新增科目；没勾开关就走这一步补问一次。 */
    async postConfirm() {
      try {
        await api.request(`/submissions/${this.data.id}/confirm`, {
          method: "POST",
          data: confirmPayload(this.data.proposal, this.data.subjects, this.data.consent, { manual: this.data.manual })
        });
      } catch (error) {
        if (error.code !== "consent_required") throw error;
        const pending = this.data.groups.filter((group) => !group.listed && !group.create_subject);
        const target = pending[0];
        if (!target) throw error;
        const agreed = await new Promise((resolve) => wx.showModal({
          title: "要新增这个科目吗？",
          content: `「${target.subject_name}」还不在科目列表里。新增后这次的知识点会记到这个科目下，也可以改到已有科目。`,
          confirmText: "新增科目",
          success: (result) => resolve(result.confirm),
          fail: () => resolve(false)
        }));
        if (!agreed) {
          this.setData({ saveError: `「${target.subject_name}」还不在科目列表里，请新增科目或改到已有科目。` });
          throw error;
        }
        const consent = { ...this.data.consent, [target.subject_name]: true };
        this.setData({ consent });
        this.refreshGroups();
        return this.postConfirm();
      }
    },
    async cancelDraft() {
      const confirmed = await new Promise((resolve) => wx.showModal({
        title: "删除草稿",
        content: "这不会创建学习记录或复习任务。",
        confirmText: "删除草稿",
        confirmColor: "#A85742",
        success: (result) => resolve(result.confirm),
        fail: () => resolve(false)
      }));
      if (!confirmed) return;
      try {
        await api.request(`/submissions/${this.data.id}/cancel`, { method: "POST" });
        if (this.afterConfirm) return this.afterConfirm();
      } catch (error) { wx.showToast({ title: error.message, icon: "none" }); }
    }
  }
};
