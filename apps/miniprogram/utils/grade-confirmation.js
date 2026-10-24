/* App-session coordinator. Only the server proposes grades or stores shared confirmation. */
const childContext = require("./child-context");
const CHOICES = childContext.gradeChoices().filter((item) => item.value !== "其他");

function createController(app, api, currentPage) {
  let active = false, scope = "", generation = 0, host = null, blocked = true;
  let loaded = false, loading = null, queue = [], draft = null, pickerOpen = false;
  let handled = new Set();
  let activeChildFacts = new Map(), membershipVersion = 0;
  function identity() {
    const data = app.globalData, member = data.currentMember;
    if (data.bootstrapState !== "bound" || !data.familyId) return "";
    if ((member && !["manager", "editor"].includes(member.role)) || (!member && data.useCloud)) return "";
    return `${data.familyId}:${member ? member.id || "" : "local"}:${member ? member.role : "manager"}`;
  }
  function visible() { return active && scope && host && host === currentPage() && !blocked && draft; }
  function paint() {
    if (!host) return;
    const view = visible() ? { ...draft, choices: CHOICES,
      currentLabel: childContext.gradeLabel(draft.current_grade),
      selectedLabel: childContext.gradeLabel(draft.selected_grade),
      index: CHOICES.findIndex((item) => item.value === draft.selected_grade),
      schoolYearLabel: `${draft.school_year}—${draft.school_year + 1} 学年`
    } : null;
    host.setData({ gradeConfirmation: view, gradeConfirmationVisible: !!view });
    const bar = host.getTabBar && host.getTabBar();
    if (bar) bar.setData({ gradeConfirmationVisible: !!view });
  }
  function invalidate() {
    generation += 1; queue = []; draft = null; loaded = false; loading = null;
    handled = new Set(); activeChildFacts = new Map(); membershipVersion = 0;
    pickerOpen = false; paint();
  }
  function syncIdentity() {
    const next = identity();
    if (next !== scope) { scope = next; invalidate(); }
  }
  function valid(token) { return active && token === generation && scope === identity() && !!scope; }
  function accept(result) {
    if (!result || !Number.isInteger(result.school_year) || !Array.isArray(result.items)
      || result.items.length > childContext.MAX_ACTIVE_CHILDREN
      || new Set(result.items.map((item) => item.id)).size !== result.items.length) throw Error("invalid_grade_candidates");
    if (!result.can_confirm) { queue = []; draft = null; loaded = true; return; }
    queue = result.items.map((item) => {
      if (!item.id || typeof item.name !== "string" || !Number.isInteger(item.revision)
        || !CHOICES.some((choice) => choice.value === item.suggested_grade)) throw Error("invalid_grade_candidate");
      return { ...item, school_year: result.school_year };
    }).filter((item) => !handled.has(`${item.id}:${item.school_year}`));
    const selected = app.globalData.selectedChildId;
    queue.sort((a, b) => Number(b.id === selected) - Number(a.id === selected));
    loaded = true;
  }
  async function read() {
    if (loading) return loading;
    const token = generation;
    loading = (async () => {
      try {
        let version;
        do {
          version = membershipVersion;
          try {
            const result = await api.request("/children/grade-confirmations");
            if (valid(token) && version === membershipVersion) {
              accept(result);
              if (draft) queue = queue.filter((item) => item.id !== draft.id);
            }
          } catch {
            if (valid(token) && version === membershipVersion) {
              loaded = true; console.warn("[grade_confirmation] candidate_read_failed");
            }
          }
        } while (valid(token) && version !== membershipVersion);
      } finally { if (token === generation) loading = null; }
    })();
    return loading;
  }
  async function pump() {
    syncIdentity();
    if (!active || !scope || !host || host !== currentPage() || blocked) { paint(); return; }
    if (!loaded) await read();
    if (!active || !scope || blocked || host !== currentPage()) return;
    if (!draft && queue.length) {
      const item = queue.shift();
      draft = { ...item, selected_grade: item.suggested_grade, status: "ready", error: "" };
    }
    paint();
  }
  function advance() {
    if (!draft || draft.status === "saving") return;
    handled.add(`${draft.id}:${draft.school_year}`); draft = null; pickerOpen = false;
    pump();
  }
  async function refreshConflict() {
    const token = generation, previous = draft;
    if (!previous) return;
    draft = { ...previous, status: "saving", error: "" }; paint();
    try {
      const [result, bootstrap] = await Promise.all([
        api.request("/children/grade-confirmations"), app.refreshBootstrap(false)
      ]);
      if (!valid(token) || draft.id !== previous.id) return;
      accept(result);
      const latest = (bootstrap.children || []).find((child) => child.id === previous.id);
      const pending = queue.find((item) => item.id === previous.id);
      queue = queue.filter((item) => item.id !== previous.id);
      if (pending) draft = { ...pending, selected_grade: pending.suggested_grade, status: "ready", error: "" };
      else if (latest && latest.active !== false) draft = { ...previous, current_grade: latest.grade,
        status: "latest", error: "" };
      else { draft = null; await pump(); }
      paint();
    } catch {
      if (valid(token) && draft) { draft = { ...previous, status: "conflict", error: "读取失败，请重试。" }; paint(); }
    }
  }
  async function submit() {
    syncIdentity();
    if (!visible() || draft.status === "saving") return;
    if (draft.status === "conflict") return refreshConflict();
    if (draft.status === "latest") return advance();
    const token = generation, previous = draft;
    draft = { ...previous, status: "saving", error: "" }; paint();
    try {
      const result = await api.request(`/children/${previous.id}/grade-confirmation`, { method: "POST",
        data: { school_year: previous.school_year, expected_grade_revision: previous.revision,
          grade: previous.selected_grade } });
      if (!valid(token)) return;
      if (host && result.child && Array.isArray(host.data.children)) {
        host.setData({ children: host.data.children.map((child) => child.id === result.child.id
          ? childContext.decorate({ ...child, ...result.child }) : child) });
      }
      draft = previous; advance();
      app.refreshBootstrap(false).catch(() => {});
    } catch (error) {
      if (!valid(token)) return;
      if ([401, 403, 404].includes(error.statusCode)) {
        invalidate(); scope = ""; app.refreshBootstrap(false).catch(() => {}); return;
      }
      draft = { ...previous, status: error.statusCode === 409 ? "conflict" : "ready",
        error: error.statusCode === 409 ? "年级已变化，请查看最新结果。" : "保存失败，请重试。" };
      paint();
    }
  }
  return {
    foreground() {
      if (active || pickerOpen) return;
      active = true; invalidate(); syncIdentity(); pump();
    },
    background() {
      if (pickerOpen) return;
      active = false; invalidate();
    },
    bootstrapChanged(children) {
      syncIdentity();
      if (Array.isArray(children)) {
        const nextFacts = new Map(children.filter((child) => child.active !== false && !child.deleting)
          .map((child) => [child.id, `${child.grade_revision}:${child.grade_confirmed_school_year}`]));
        const added = [...nextFacts.keys()].some((id) => !activeChildFacts.has(id));
        if (nextFacts.size !== activeChildFacts.size
          || [...nextFacts].some(([id, fact]) => activeChildFacts.get(id) !== fact)) membershipVersion += 1;
        if (added) loaded = false;
        activeChildFacts = nextFacts;
        const stillPending = (item) => children.some((child) => child.id === item.id
          && child.active !== false && !child.deleting && child.grade_revision === item.revision
          && child.grade_confirmed_school_year !== item.school_year);
        queue = queue.filter(stillPending);
        if (draft && draft.status !== "saving" && !stillPending(draft)) draft = null;
      }
      pump();
    },
    handle(page, event) {
      const action = event.action;
      if (action === "hide") {
        if (host === page && !pickerOpen) { blocked = true; paint(); host = null; }
        return;
      }
      if (["show", "availability"].includes(action)) {
        if (page !== currentPage()) return;
        if (host && host !== page) { blocked = true; paint(); }
        host = page; blocked = !!event.blocked;
        pump(); return;
      }
      syncIdentity();
      if (page !== host || !visible()) return;
      if (action === "picker-open") { if (draft.status === "ready") pickerOpen = true; return; }
      if (action === "picker-close" || action === "choose") pickerOpen = false;
      if (action === "choose" && draft.status === "ready" && CHOICES[event.index]) {
        draft.selected_grade = CHOICES[event.index].value; draft.error = ""; paint();
      }
      if (action === "later") advance();
      if (action === "confirm") return submit();
    }
  };
}

module.exports = { createController };
