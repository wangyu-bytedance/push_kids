// Native presentation matrix in the synthetic offline copy; never a release runner.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const registry = require("../apps/miniprogram/presentation/theme/registry");
const appConfig = require("../apps/miniprogram/app.json");
const width = Number(process.argv[2] || 390), port = Number(process.argv[3] || 9631);
const out = path.resolve("docs/quality/evidence/themes-20261106/native", String(width));
const only = process.argv.find((v) => v.startsWith("--only="))?.slice(7);
const caseFilter = process.argv.find((v) => v.startsWith("--case="))?.slice(7);
const themes = only ? registry.listThemes().filter((t) => t.id === only) : registry.listThemes();
const child = { id: "synthetic", name: "小满", label: "小满", avatar: "满", active: true,
  grade: "小学二年级", gradeLabel: "小学二年级", daily_budget_minutes: 15 };
const common = { loading: false, error: "", children: [child], child, childId: child.id, childIndex: 0,
  canWrite: true, isManager: true, multiChild: false, gradeConfirmation: null, gradeConfirmationVisible: false };
const fixtures = {
  "pages/today/index": { dayLabel: "11 月 6 日 星期五", dashboard: { day: "2026-11-06", show_guide: false,
    todo_count: 2, daily_tasks: { total_count: 1, items: [] }, daily_summary: { record_count: 1 },
    schedule_items: [], optional_activity_suggestions: [] },
    stablePlan: true, hero: { total: 2, required: 2, minutes: 15, ticks: [], note: "按自己的节奏，一点点来" },
    sections: { review: false, daily: false, learning: false, activity: false },
    sectionMeta: { review: "今天 2 项", daily: "阅读 20 分钟", learning: "已确认 1 条", activity: "今天没有安排" } },
  "pages/settings/index": { baseLearning: ["语文", "数学", "英语"].map((name) => ({ name, selected: true })),
    addedLearning: [{ id: "custom", name: "自然观察与科学探索", custom: true, canRemove: true }],
    addedActivities: [{ id: "chess", name: "围棋", iconClass: "chess", scheduleLabel: "每周日 14:00–16:00" },
      { id: "custom-activity", name: "自定义探索活动", iconClass: "default", scheduleLabel: "时间不固定" }],
    dailyTasks: [{ id: "reading", name: "阅读", minutes: 20 }], travelArrangements: [], archivedChildren: [],
    showThemePicker: false, themePersistFailed: false },
  "pages/calendar/index": { weekKicker: "11 月 2 日 – 11 月 8 日", dayTitle: "11 月 6 日 · 星期五", selectedDay: "2026-11-06",
    weeks: [], weekDays: [], weekdays: [], weekEmpty: false, itemCount: 1, conflictCount: 0,
    items: [{ id: "calendar-event", source: "calendar", name: "阅读时间", kind: "other", kind_label: "自主安排",
      start_time: "18:00", end_time: "18:30", time_text: "18:00–18:30", conflict_lines: [] }] },
  "pages/records/index": { recordType: "learning", inputText: "今天阅读了《小蝌蚪找妈妈》，认识了新的词语。", photos: [],
    selectedChildId: child.id, occurredDate: "2026-11-06", occurredTime: "18:30", saving: false, voiceState: "idle" },
  "pages/reports/index": { report: {}, days: 7, metrics: [
    { label: "学习记录", text: "12", ariaLabel: "学习记录 12 条", trend: { available: false } },
    { label: "复习反馈", text: "8", ariaLabel: "复习反馈 8 次", trend: { available: false } }],
    subjects: [], activityRows: [{ id: "custom", name: "自然观察", iconClass: "default", meta: "2 次 · 共 40 分钟" }],
    feedbackTotal: 8, urgencyPages: [], activityPages: [], isEmpty: false },
  "pages/footprints/index": { visits: [], summary: { total_visits: 0 }, mode: "timeline", sheet: "" },
  "pages/review-inventory/index": { loaded: true, items: [], groups: [], total: 0, minutes: 0, view: "time", error: "" },
  "pages/submission/confirm": { submission: { id: "draft", status: "pending_confirmation", input_text: "阅读了新的故事。",
    time_label: "11 月 6 日 18:30", submitted_label: "11 月 6 日 18:32", photos: [] },
    titleText: "一起确认今天的学习", statusLabel: "待确认", statusTone: "att", editable: true,
    draft: { subjects: [], learned_facts: [] }, subjects: [], cards: [], points: [], manual: true },
  "pages/record-detail/index": { submission: { id: "confirmed", status: "confirmed", source: "manual", input_text: "阅读了新的故事。",
    time_label: "11 月 6 日 18:30", submitted_label: "11 月 6 日 18:32", photos: [] },
    titleText: "今天的阅读记录", statusLabel: "已确认", statusTone: "", records: [], cards: [] },
  "pages/activity/edit": { subjectName: "自然观察与科学探索", iconClass: "default", subjectId: "custom",
    subjects: [{ id: "custom", name: "自然观察与科学探索" }], subjectIndex: 0, duration: 30, date: "2026-11-06", time: "18:30" },
  "pages/child-edit/index": { mode: "edit", title: "编辑学习档案", nameDraft: "小满", active: true, gradeIndex: 3, budgetIndex: 1 },
  "pages/family-onboarding/index": { state: "unbound", loading: false, error: "", familyName: "小满的家" },
  "pages/family-join/index": { code: "123456", relationship: "家人", familyName: "小满的家", error: "" },
  "pages/family-members/index": { family: { id: "synthetic-family", display_name: "小满的家" },
    members: [{ id: "synthetic-member", relationship_label: "妈妈", role_label: "管理员", is_self: true, role: "manager" }],
    requestCount: 1, requests: [], invite: null, canInvite: true },
  "pages/family-requests/index": { items: [{ id: "synthetic-request", relationship_label: "家人", status: "pending",
    time_label: "今天 09:30", applicant_label: "待加入的家人" }], canManage: true },
  "pages/delete-settings/index": { mode: "", request: null, family: { display_name: "小满的家" } },
  "pages/notifications/index": { supported: true, channelAvailable: true, heroReady: true, heroTitle: "重要的安排，会提前提醒",
    autoEnabled: true, autoSaving: false, items: [{ type: "review", label: "每晚复习", enabled: true,
      description: "每天 20:00，提醒查看复习安排" }], error: "", grantCount: 0 }
};
const shared = [
  { name: "loading", route: "pages/today/index", data: { ...common, loading: true, dashboard: null, children: [] } },
  { name: "empty", route: "pages/settings/index", data: { ...common, children: [], baseLearning: [], addedLearning: [], addedActivities: [] } },
  { name: "error", route: "pages/records/index", data: { ...common, error: "网络暂时不可用，已保留输入。请稍后重试。" } },
  { name: "readonly", route: "pages/family-members/index", data: { ...common, ...fixtures["pages/family-members/index"],
    canWrite: false, isManager: false, roleNote: "你在这个家庭是「只读成员」·可以查看家庭信息" } },
  { name: "disabled", route: "pages/settings/index", data: { ...common, ...fixtures["pages/settings/index"], showDailyTaskForm: true,
    dailyTaskName: "自然观察", dailyTaskMinutes: "20", savingDailyTask: true } },
  { name: "sheet", route: "pages/settings/index", data: { ...common, ...fixtures["pages/settings/index"] }, action: "picker" },
  { name: "dialog", route: "pages/settings/index", data: { ...common, ...fixtures["pages/settings/index"],
    gradeConfirmationVisible: true, gradeConfirmation: { name: "小满", currentLabel: "小学二年级", selectedLabel: "小学三年级",
      status: "ready", choices: [{ value: "小学三年级", label: "小学三年级" }], index: 0, schoolYearLabel: "2026—2027 学年" } } },
  { name: "long-copy", route: "pages/child-edit/index", data: { ...common, ...fixtures["pages/child-edit/index"], nameDraft: "这是一个用于小屏验证的较长孩子昵称",
    error: "暂时无法保存这次修改。你已填写的姓名、年级、每日复习预算和科目选择仍然保留，可以检查网络后重试。" } }
];
const socket = new WebSocket("ws://127.0.0.1:" + port), pending = new Map(); let seq = 0;
socket.onmessage = (event) => { const m = JSON.parse(event.data); const handler = pending.get(m.id);
  if (handler) { pending.delete(m.id); handler(m); } };
function send(method, params = {}) {
  return new Promise((resolve, reject) => { const id = String(++seq), timer = setTimeout(() => {
    pending.delete(id); reject(Error(method + " timed out")); }, method === "App.captureScreenshot" ? 4000 : 15000);
  pending.set(id, (m) => { clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
  socket.send(JSON.stringify({ id, method, params })); });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let lastRoute;
const unavailableScreenshotCases = new Set();
const navigationDiagnostics = [];
const geometry = `function(){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0], info=wx.getWindowInfo();
  const selectors=['.theme-page','.page','.theme-header','.pk-card','.btn','.theme-entry','.pk-sheet','.pk-cta-bar',
    '.pk-notice','.sk','.pk-empty','.grade-sheet','.grade-primary','.grade-secondary','.theme-picker-sheet',
    '.theme-picker-head','.theme-picker-foot','.theme-picker-close','.theme-choice','.record-type-title',
    '.hero-note','.manager-panel','.icon-btn','.add-entry'];
  function collect(host,label){return new Promise(done=>{const q=wx.createSelectorQuery().in(host);
    selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['backgroundColor','color','fontSize','fontFamily']}));
    q.exec(result=>done(selectors.flatMap((selector,i)=>(result[i]||[]).map(n=>({host:label,selector,...n})))));});}
  const hosts=[[p,'page']];
  const picker=getApp().getThemeFixturePicker();if(picker&&picker.data.visible)hosts.push([picker,'theme-picker']);
  ['theme-picker','#grade-confirmation','primary-nav','#today-learning','review-inventory','footprints-embedded'].forEach(s=>{
    const c=p.selectComponent(s);if(c)hosts.push([c,s]);});
  const bar=p.getTabBar&&p.getTabBar();if(bar)hosts.push([bar,'tab-bar']);
  Promise.all(hosts.map(h=>collect(h[0],h[1]))).then(rows=>resolve({route:p.route,theme:p.data.theme.id,
    viewport:{width:info.windowWidth,height:info.windowHeight,screenWidth:info.screenWidth,screenHeight:info.screenHeight},
    base_library:wx.getAppBaseInfo().SDKVersion,nodes:[].concat(...rows),
    source:'native wx.createSelectorQuery; synthetic fixtures; production WXML/WXSS exact; page loading lifecycles suppressed'}));
})}`;
async function navigate(route) {
  if (lastRoute === route) return;
  const current = await call("function(){const p=getCurrentPages().slice(-1)[0];return p&&p.route;}");
  if (current !== route) {
    const isTab = appConfig.tabBar.list.some((t) => t.pagePath === route);
    if (!isTab) {
      const depth = await call("function(){return getCurrentPages().length;}");
      if (depth > 1) await send("App.callWxMethod", { method: "navigateBack", args: [{ delta: depth - 1 }] });
    }
    try { await send("App.callWxMethod", {
      method: isTab ? "switchTab" : "navigateTo",
      args: [{ url: "/" + route }]
    }); }
    catch (error) {
      const observed = await call("function(){const p=getCurrentPages().slice(-1)[0];return p&&p.route;}");
      navigationDiagnostics.push({ route, observed, error: error.message });
      if (observed !== route) throw error;
    }
  }
  await pause(700);
  lastRoute = route;
}
async function capture(theme, item) {
  console.log("CAPTURE " + theme.id + " " + item.name);
  await navigate(item.route);
  await call("function(id,data,action){getApp().theme.setTheme(id);getApp().themeFixture(data);" +
    "const p=getCurrentPages().slice(-1)[0],bar=p.getTabBar&&p.getTabBar();" +
    "if(bar){const tabs=['pages/today/index','pages/calendar/index','pages/records/index','pages/reports/index','pages/settings/index'];" +
    "bar.setData({selected:tabs.indexOf(p.route)});}" +
    "if(action==='picker')p.openThemePicker();wx.pageScrollTo({scrollTop:0,duration:0});return true;}",
  [theme.id, item.data, item.action || ""]);
  await pause(140);
  const measured = await call(geometry);
  if (!measured || measured.viewport.screenWidth !== width || measured.viewport.screenHeight !== ({320:568,390:844,430:932})[width]
      || measured.route !== item.route || measured.theme !== theme.id)
    throw Error("Unexpected native viewport, route or theme: " + JSON.stringify(measured && { viewport: measured.viewport, route: measured.route, theme: measured.theme }));
  // A failed simulator screenshot must not discard successfully measured native nodes.
  const screenshotErrors = [];
  let png;
  if (unavailableScreenshotCases.has(item.name)) screenshotErrors.push("NOT_RUN: capture timed out for this scene; native geometry still measured");
  else {
    try { png = await send("App.captureScreenshot"); }
    catch (error) { screenshotErrors.push(error.message); unavailableScreenshotCases.add(item.name); }
  }
  const name = theme.id + "--" + item.name, bytes = png && Buffer.from(png.data, "base64");
  measured.screenshot = bytes ? name + ".png" : null;
  measured.screenshot_sha256 = bytes ? crypto.createHash("sha256").update(bytes).digest("hex") : null;
  measured.fixture = item.name; measured.category = item.category; measured.screenshot_errors = screenshotErrors;
  const required = { "state-loading": ".sk", "state-empty": ".pk-empty", "state-error": ".pk-notice",
    "state-readonly": ".hero-note", "state-disabled": ".pk-sheet", "state-sheet": ".theme-picker-sheet",
    "state-dialog": ".grade-sheet", "state-long-copy": ".pk-notice" }[item.name];
  measured.validation_errors = required && !measured.nodes.some((n) => n.selector === required)
    ? ["Expected state is absent: " + required] : [];
  measured.touch_errors = measured.nodes.filter((n) => [".btn", ".theme-picker-close", ".theme-choice", ".icon-btn", ".add-entry"].includes(n.selector)
    && (n.height < 43.5 || n.width < 43.5)).map((n) => ({ selector: n.selector, width: n.width, height: n.height }));
  if (measured.touch_errors.length) measured.validation_errors.push("Native control touch target below44px");
  measured.horizontal_overflow = measured.nodes.filter((n) => [".page", ".theme-picker-sheet", ".grade-sheet", ".pk-sheet"].includes(n.selector)
    && (n.left < -1 || n.right > width + 1)).map((n) => ({ selector: n.selector, left: n.left, right: n.right }));
  if (bytes) fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify(measured, null, 2) + "\n");
  return { name, route: item.route, category: item.category, nodes: measured.nodes.length,
    horizontal_overflow: measured.horizontal_overflow, validation_errors: measured.validation_errors,
    screenshot_errors: screenshotErrors, screenshot_sha256: measured.screenshot_sha256 };
}
async function run() {
  if (![320, 390, 430].includes(width)) throw Error("Expected one of the approved screen widths");
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  fs.mkdirSync(out, { recursive: true });
  const start = Date.now(), results = [], failures = [];
  const reportFile = path.join(out, "matrix" + (only ? "-" + only : "") + (caseFilter ? "-" + caseFilter : "") +
    ".json");
  const saveReport = () => fs.writeFileSync(reportFile, JSON.stringify({ width, themes: themes.map((t) => t.id),
    groups: results.length, elapsed_ms: Date.now() - start, results, failures, navigation_diagnostics: navigationDiagnostics,
    source_manifest_sha256: crypto.createHash("sha256").update(fs.readFileSync(path.join(out, "source-sha256.json"))).digest("hex") }, null, 2) + "\n");
  fs.copyFileSync("/private/tmp/push-kids-themes-native-20261106/theme-source-sha256.json", path.join(out, "source-sha256.json"));
  if (process.argv.includes("--actions")) {
    await navigate("pages/settings/index");
    await call("function(data){getApp().themeFixture(data);return true;}", [{ ...common, ...fixtures["pages/settings/index"] }]);
    const actions = [];
    for (let i = 0; i < themes.length; i++) {
      const result = await call(`async function(id,previous){
        const app=getApp(),p=getCurrentPages().slice(-1)[0];app.theme.setTheme(previous);
        p.setData({dailyTaskName:'未提交的自然观察',dailyTaskMinutes:'25'});
        const before=app.themeFixtureRequestCount();
        p.openThemePicker();await new Promise(r=>wx.nextTick(r));
        let picker=app.getThemeFixturePicker();picker.choose({currentTarget:{dataset:{id}}});
        const staged=app.theme.current().id===previous;
        picker.close();await new Promise(r=>wx.nextTick(r));
        const cancelled=!p.data.showThemePicker&&app.theme.current().id===previous;
        p.openThemePicker();await new Promise(r=>wx.nextTick(r));
        picker=app.getThemeFixturePicker();picker.choose({currentTarget:{dataset:{id}}});
        const started=Date.now();picker.apply();await new Promise(r=>wx.nextTick(r));
        const bar=p.getTabBar();return {id,staged,cancelled,current:app.theme.current().id,
          page:p.data.theme.id,picker:picker.data.theme.id,tab:bar.data.theme.id,
          closed:!p.data.showThemePicker&&!bar.data.themePickerVisible,
          draft:p.data.dailyTaskName,minutes:p.data.dailyTaskMinutes,
          preference:wx.getStorageSync('pk.theme.v1'),business_requests:app.themeFixtureRequestCount()-before,
          next_tick_ms:Date.now()-started,latency_scope:'native nextTick, not visible stability or real-device timing'};
      }`, [themes[i].id, themes[(i + 1) % themes.length].id]);
      if (!result.staged || !result.cancelled || !result.closed || result.current !== themes[i].id ||
          result.page !== result.current || result.picker !== result.current || result.tab !== result.current ||
          result.draft !== "未提交的自然观察" || result.minutes !== "25" || result.preference.id !== result.current || result.business_requests !== 0)
        throw Error("Native theme action contract failed: " + JSON.stringify(result));
      actions.push(result);
    }
    fs.writeFileSync(path.join(out, "actions.json"), JSON.stringify(actions, null, 2) + "\n");
    console.log("NATIVE_THEME_ACTIONS_PASS " + actions.length);return;
  }
  const allItems = [...appConfig.pages.map((route) => ({ name: route.replace(/^pages\//, "").replace(/\//g, "-"),
    category: "route", route, data: { ...common, ...fixtures[route] } })), ...shared.map((s) => ({ ...s, name: "state-" + s.name, category: "state" }))];
  const items = caseFilter ? allItems.filter((item) => caseFilter.split(",").includes(item.name)) : allItems;
  saveReport();
  // Keep each native route open while checking its themes; this bounds WebView churn.
  let consecutiveFailures = 0;
  matrixLoop: for (const item of items) {
    for (const theme of themes) {
      try { results.push(await capture(theme, item)); consecutiveFailures = 0; }
      catch (error) {
        failures.push({ theme: theme.id, name: item.name, error: error.message }); console.error(error.message);
        consecutiveFailures++;
      }
      saveReport();
      if (consecutiveFailures >= 3) { console.error("NATIVE_BRIDGE_UNAVAILABLE: remaining groups NOT_RUN"); break matrixLoop; }
    }
    console.log("NATIVE_CASE_CAPTURED " + width + " " + item.name + " " + themes.length);
  }
  console.log(JSON.stringify({ width, groups: results.length, failures, elapsed_ms: Date.now() - start,
    overflow_groups: results.filter((r) => r.horizontal_overflow.length).map((r) => r.name) }));
  if (failures.length || results.some((r) => r.validation_errors.length || r.horizontal_overflow.length || r.screenshot_errors.length)) process.exitCode = 1;
}
run().catch((error) => { console.error(error); process.exitCode = 1; }).finally(() => socket.close());
