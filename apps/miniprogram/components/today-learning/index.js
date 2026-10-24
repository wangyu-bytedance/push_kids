const api = require("../../utils/api");

function titleState(value) {
  const title = value.trim(), editTitleCount = Array.from(title).length;
  const titleError = !title ? "请填写学习标题。" : editTitleCount > 20 ? "标题最多20字，请精简。" : /[\r\n\u2028\u2029]/.test(title) ? "标题请写成一行。" : "";
  return { editTitleCount, titleError };
}

function cardState(current, canWrite) {
  if (!current) return "";
  if (current.task) return "task";
  if (!canWrite || !(current.eligibility === "eligible" || current.can_regenerate)) return "";
  if (current.proposal) return "proposal";
  if (current.stale) return "stale";
  if (current.job && ["queued", "running"].includes(current.job.state)) return "generating";
  if (current.job && current.job.state === "failed") return "generation-error";
  if (current.can_regenerate && current.eligibility !== "eligible") return "recover";
  return "";
}

function today() {
  const date = new Date(Date.now() + 8 * 3600000);
  return date.toISOString().slice(0, 10);
}

Component({
  options: { addGlobalClass: true },
  properties: {
    childId: { type: String, observer() { this.reset(); if (this.data.childId) this.refresh(true); } },
    blocked: { type: Boolean, value: false, observer(value) {
      if (!value && this.visible !== false && this.data.childId) this.refresh(true);
    } },
    canWrite: { type: Boolean, value: false, observer(value) {
      this.setData({ card: cardState(this.data.current, value) });
      if (!value) {
        this.generation = (this.generation || 0) + 1;
        if (this.timer) clearTimeout(this.timer);
        this.setData({ loading: false, busy: false, busyAction: "" });
        if (this.data.sheet) this.setSheet("");
      }
    } }
  },
  data: { current: null, card: "", loading: false, error: "", sheet: "", busy: false, busyAction: "",
    editTitle: "", editTitleCount: 0, titleError: "", editInstructions: "", editMinutes: "", actual: "", actualDate: "", actualTime: "18:00",
    lockedActual: false, pollStopped: false, focusActual: false, focusTitle: false, restoreFocus: false },
  lifetimes: {
    attached() { if (this.data.childId && !this.data.loading) this.refresh(true); },
    detached() { this.hide(); }
  },
  pageLifetimes: {
    show() { this.visible = true; if (this.data.childId) this.refresh(true); },
    hide() { this.hide(); }
  },
  methods: {
    setCurrent(current, extra = {}) {
      this.setData({ ...extra, current, card: cardState(current, this.data.canWrite) });
    },
    reset() {
      const wasOpen = !!this.data.sheet;
      this.generation = (this.generation || 0) + 1;
      if (this.timer) clearTimeout(this.timer);
      this.visible = true; this.attempt = null; this.commandKeys = {}; this.pollCount = 0;
      this.setCurrent(null, { loading: false, error: "", busy: false, busyAction: "", sheet: "", lockedActual: false, pollStopped: false,
        editTitle: "", editTitleCount: 0, titleError: "", editInstructions: "", editMinutes: "", focusTitle: false });
      if (wasOpen) this.triggerEvent("modal", { open: false });
    },
    hide() {
      this.visible = false; this.generation = (this.generation || 0) + 1;
      if (this.timer) clearTimeout(this.timer);
      this.setData({ loading: false, busy: false, busyAction: "" });
      if (this.data.sheet) this.setSheet("");
    },
    path(suffix) { return `/children/${this.data.childId}/learning-suggestions${suffix}`; },
    scopeKey() {
      const data = getApp().globalData;
      return `${data.familyId || ""}:${(data.currentMember || {}).id || ""}:${(data.currentMember || {}).role || ""}`;
    },
    capture() { return { number: this.generation || 0, identity: this.scopeKey() }; },
    valid(generation, child) { return this.visible !== false && generation.number === (this.generation || 0) && generation.identity === this.scopeKey() && child === this.data.childId; },
    key(action) {
      this.commandKeys = this.commandKeys || {};
      if (!this.commandKeys[action]) this.commandKeys[action] = api.newIdempotencyKey(`study-${action}`);
      return this.commandKeys[action];
    },
    setSheet(sheet) {
      this.setData({ sheet, focusActual: sheet === "record", focusTitle: sheet === "edit", restoreFocus: !sheet });
      this.triggerEvent("modal", { open: !!sheet });
    },
    close() { if (!this.data.busy) this.setSheet(""); },
    noop() {},
    async refresh(automatic = false) {
      if (this.data.loading || !this.data.childId) return;
      const child = this.data.childId;
      const generation = this.capture();
      this.setData({ loading: true, error: "" });
      try {
        const current = await api.request(this.path("/current"));
        if (!this.valid(generation, child)) return;
        this.setCurrent(current, { loading: false });
        if (automatic && !this.data.blocked && this.data.canWrite && current.eligibility === "eligible") {
          const requestId = this.key(`prompt-${current.day}`);
          const claim = await api.request(this.path("/automatic-prompt"), { method: "POST", data: { request_id: requestId } });
          if (!this.valid(generation, child)) return;
          if (claim.current) this.setCurrent(claim.current);
          if (claim.can_auto_open && !this.data.blocked) {
            this.setSheet("proposal");
            api.request(this.path("/prompt-displayed"), { method: "POST", data: { prompt_on: claim.prompt_on, request_id: requestId } }).catch(() => {});
          }
        }
        this.poll();
      } catch (error) {
        if (!this.valid(generation, child)) return;
        if (error.statusCode === 404) this.setCurrent(null, { loading: false });
        else this.setData({ loading: false, error: error.message });
      }
    },
    poll() {
      if (this.timer) clearTimeout(this.timer);
      const job = this.data.current && this.data.current.job;
      if (!job || !["queued", "running"].includes(job.state) || this.visible === false) return;
      if ((this.pollCount || 0) >= 8) { this.setData({ pollStopped: true }); return; }
      const delay = [2000, 4000, 8000][Math.min(this.pollCount || 0, 2)];
      this.pollCount = (this.pollCount || 0) + 1;
      this.timer = setTimeout(() => this.refresh(false), delay);
    },
    retry() { this.pollCount = 0; this.setData({ pollStopped: false }); this.refresh(false); },
    open() {
      this.setSheet("proposal");
      if (!this.data.current.proposal && !this.data.current.task && !this.data.current.job) this.generate();
    },
    async command(action, suffix, data, method = "POST") {
      if (!this.data.canWrite || this.data.busy) return false;
      const child = this.data.childId; const generation = this.capture();
      this.setData({ busy: true, busyAction: action, error: "" });
      try {
        await api.request(this.path(suffix), { method, data, idempotencyKey: this.key(action) });
        if (!this.valid(generation, child)) return false;
        delete this.commandKeys[action]; this.pollCount = 0;
        this.setData({ busy: false, busyAction: "" });
        await this.refresh(false);
        return this.valid(generation, child);
      } catch (error) {
        if (this.valid(generation, child)) this.setData({ busy: false, busyAction: "", error: error.message });
        return false;
      }
    },
    async generate(event) {
      const current = this.data.current;
      if (!current || current.task) return;
      const replace = !!event && !!current.proposal;
      const ok = await this.command("generate", "/generate", { expected_version: current.version,
        replace_suggestion_id: replace ? current.proposal.id : null });
      if (ok) this.setSheet("proposal");
    },
    async approve() {
      const p = this.data.current.proposal;
      if (p && await this.command("approve", `/${p.id}/approve`, { expected_version: p.version })) this.setSheet("");
    },
    async defer() {
      const p = this.data.current.proposal;
      if (p && await this.command("defer", `/${p.id}/defer`, { expected_version: p.version })) this.setSheet("");
    },
    edit() {
      const p = this.data.current.proposal;
      this.setData({ editTitle: p.title, ...titleState(p.title), editInstructions: p.instructions, editMinutes: p.estimated_minutes ? String(p.estimated_minutes) : "" });
      this.setSheet("edit");
    },
    field(event) {
      const field = event.currentTarget.dataset.field;
      if (["editTitle", "editInstructions", "editMinutes", "actual", "actualDate", "actualTime"].includes(field)) this.setData({ [field]: event.detail.value, ...(field === "editTitle" ? titleState(event.detail.value) : {}) });
    },
    async saveEdit() {
      if (!this.data.canWrite || this.data.busy) return;
      const p = this.data.current.proposal;
      const validation = titleState(this.data.editTitle);
      if (validation.titleError) {
        const generation = this.capture(), child = this.data.childId;
        this.setData({ ...validation, focusTitle: false });
        wx.nextTick(() => { if (this.valid(generation, child) && this.data.sheet === "edit") this.setData({ focusTitle: true }); });
        return;
      }
      const minutes = this.data.editMinutes.trim();
      if (!this.data.editInstructions.trim() || (minutes && !/^[1-9]\d*$/.test(minutes))) {
        this.setData({ error: "请填写标题、具体内容，时长可留空或填正整数。" }); return;
      }
      if (await this.command("edit", `/${p.id}`, { expected_version: p.version, title: this.data.editTitle.trim(),
        instructions: this.data.editInstructions, estimated_minutes: minutes ? Number(minutes) : null }, "PATCH")) this.setSheet("proposal");
    },
    openRemove() { if (this.data.canWrite) this.setSheet("remove"); },
    async remove() {
      const task = this.data.current.task;
      if (await this.command("remove", `/tasks/${task.id}/remove`, { expected_version: task.version })) this.setSheet("proposal");
    },
    openRecord() {
      if (!this.data.canWrite) return;
      if (!this.attempt) this.setData({ actual: "", actualDate: today(), actualTime: "18:00", lockedActual: false });
      this.setSheet("record");
    },
    async record(event) {
      if (!this.data.canWrite || this.data.busy) return;
      const mode = event.currentTarget.dataset.mode;
      const points = this.data.actual.split(/\n/).map((s) => s.trim()).filter(Boolean);
      if (!points.length || points.length > 20 || points.some((s) => s.length > 120)) {
        this.setData({ error: "请只写实际学过的内容，每行一个知识点（最多120字），最多20行。" }); return;
      }
      const task = this.data.current.task;
      const child = this.data.childId; const generation = this.capture();
      const root = this.path("");
      const occurred = new Date(`${this.data.actualDate}T${this.data.actualTime}:00+08:00`);
      if (!Number.isFinite(occurred.getTime()) || occurred.getTime() > Date.now()) {
        this.setData({ error: "请选择已经发生的学习时间。" }); return;
      }
      this.setData({ busy: true, error: "" });
      if (!this.attempt) this.attempt = { task, child, mode, points, actual: this.data.actual, occurred: occurred.toISOString(), request: this.key("record") };
      const attempt = this.attempt;
      this.setData({ lockedActual: true });
      try {
        if (!attempt.intent) attempt.intent = await api.request(`${root}/tasks/${task.id}/record-intents`, {
          method: "POST", data: { expected_version: task.version, mode: attempt.mode, request_id: attempt.request } });
        if (!this.valid(generation, child)) return;
        if (!attempt.submission) attempt.submission = await api.request("/submissions", { method: "POST",
          idempotencyKey: attempt.intent.submission_idempotency_key,
          data: { child_id: child, occurred_at: attempt.occurred, input_text: attempt.actual, source: "manual" } });
        if (!this.valid(generation, child)) return;
        const latest = await api.request(`/submissions/${attempt.submission.id}`);
        if (!this.valid(generation, child)) return;
        if (latest.state !== "confirmed") await api.request(`/submissions/${attempt.submission.id}/confirm`, {
          method: "POST", data: { manual_entry: true, subject_id: task.content.subject_id, proposal: {
            summary: attempt.actual.slice(0, 500), subject_name: task.content.subject_name, subject_kind: "learning",
            source: "人工录入", uncertainties: [], todo_matches: [], knowledge_points: attempt.points.map((name) => ({
              name, category: "知识点", review_method: "口头回顾", estimated_minutes: 3, confidence: "high",
              subject_name: task.content.subject_name, direct_evidence: [{ source: "parent_text", detail: name }]
            })) } } });
        if (!this.valid(generation, child)) return;
        await api.request(`${root}/tasks/${task.id}/records`, { method: "POST", data: {
          intent_id: attempt.intent.id, submission_id: attempt.submission.id } });
        if (!this.valid(generation, child)) return;
        this.attempt = null; delete this.commandKeys.record;
        this.setData({ busy: false, lockedActual: false }); this.setSheet("");
        this.triggerEvent("recorded"); await this.refresh(false);
      } catch (error) {
        if (this.valid(generation, child)) this.setData({ busy: false, error: `${error.message}。重试会沿用本次记录。` });
      }
    }
  }
});
