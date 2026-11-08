// Native presentation matrix in the synthetic offline copy; never a release runner.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const registry = require("../apps/miniprogram/presentation/theme/registry");
const appConfig = require("../apps/miniprogram/app.json");
const { current, legacy, byBaseline } = require("./frontend_viewports.json");
const currentViewports = byBaseline[current];
const captureViewports = { ...byBaseline[legacy], ...currentViewports };
if (process.argv.includes("--list-viewports")) {
  for (const [width, height] of Object.entries(currentViewports)) console.log(`${width}x${height}`);
  process.exit(0);
}
const width = Number(process.argv[2] || Object.keys(currentViewports)[0]), port = Number(process.argv[3] || 9631);
if (!Object.hasOwn(captureViewports, width)) {
  throw Error(`Expected width ${Object.keys(currentViewports).join(" or ")} (320 for legacy capture)`);
}
const outputRoot = process.argv.find((v) => v.startsWith("--output="))?.slice(9) || "dist/theme-native";
const project = process.argv.find((v) => v.startsWith("--project="))?.slice(10) || "/private/tmp/push-kids-themes-native-20261106";
const out = path.resolve(outputRoot, String(width));
const only = process.argv.find((v) => v.startsWith("--only="))?.slice(7);
const caseFilter = process.argv.find((v) => v.startsWith("--case="))?.slice(7);
const headerBlend = process.argv.includes("--header-blend");
const childHeading = process.argv.includes("--child-heading");
const headerCapture = headerBlend || childHeading;
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
// Opt-in DREV09 states extend the frozen Spec08 matrix without rewriting it.
const recordScene = (name, data) => ({ name: "refine-" + name, category: "refinement",
  route: "pages/records/index", data: { ...common, ...fixtures["pages/records/index"],
    date: "2026-11-07", time: "18:30", text: "保留的学习草稿", hasText: true, ...data } });
const refinement = [
  recordScene("menu", { recordTypeOpen: true }),
  recordScene("long-name", { children: [{ ...child, name: "用于三视口检查的较长孩子昵称" }], recordTypeOpen: true }),
  recordScene("media-failure", { themeArtFailed: true, uploadArtFailed: true }),
  recordScene("travel", { recordType: "travel", travelChildren: [child], travelChildIndex: 0, travelChildId: child.id }),
  recordScene("photos", { photos: ["/assets/illustrations/record-books.png"] }),
  recordScene("uploading", { photos: ["/assets/illustrations/record-books.png"], saving: true, uploadProgress: 45 }),
  recordScene("upload-error", { photos: ["/assets/illustrations/record-books.png"], error: "上传暂未完成，照片与文字仍保留。" })
];
const headerScenarios = [
  ["today", "today/index"], ["reports", "reports/index"], ["records", "records/index"],
  ["calendar", "calendar/index"], ["settings", "settings/index"], ["activity", "activity/edit"],
  ["detail", "record-detail/index"], ["confirm", "submission/confirm", { readOnly: true }],
  ["create", "family-onboarding/index", { mode: "create" }],
  ["invite", "family-onboarding/index", { mode: "join" }],
  ["join", "family-join/index"], ["requests", "family-requests/index"],
  ["notifications", "notifications/index"], ["cleanup", "delete-settings/index"],
  ["cleanup-confirm", "delete-settings/index", { mode: "child", targetName: "小满" }],
  ["image-failure", "reports/index", { themeArtFailed: true }],
  ["long-title", "delete-settings/index", { mode: "child", targetName: "用于检查长标题换行的孩子昵称需要完整显示" }],
  ["record-menu", "records/index", { recordTypeOpen: true }]
].map(([name, suffix, extra]) => {
  const route = "pages/" + suffix;
  return { name, route, category: "header-blend", data: { ...common, ...fixtures[route], ...extra } };
});
const anotherChild = { ...child, id: "another", name: "小秋", label: "小秋", avatar: "秋" };
const childChoices = [child, anotherChild];
const childHeadingScenarios = [
  ["today", "today"], ["calendar", "calendar"], ["records", "records"],
  ["travel", "records", { recordType: "travel", travelChildren: childChoices, travelChildIndex: 0 }],
  ["reports", "reports"], ["settings", "settings"], ["footprints", "footprints"],
  ["empty", "today", { children: [], dashboard: null }],
  ["single", "calendar", { children: [child], multiChild: false }],
  ["long-name", "reports", { children: [{ ...child, name: "一个用于窄屏检查的很长的孩子昵称" }, anotherChild] }],
  ["record-menu", "records", { recordTypeOpen: true }],
  ["record-saving", "records", { saving: true }],
  ["missing-art", "reports", { themeArtFailed: true, introArtFailed: true }],
  ["calendar-no-spot", "calendar", { introArtFailed: true }],
  ["readonly", "settings", { canWrite: false, isManager: false }]
].map(([name, suffix, extra]) => {
  const route = "pages/" + suffix + "/index";
  const data = { ...common, ...fixtures[route], children: childChoices, multiChild: true, ...extra };
  return { name, route, category: "child-heading", data };
});
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
    '.hero-note','.manager-panel','.icon-btn','.add-entry','.report-intro .pg-title',
    '.theme-header-art','.record-heading-content','.record-type-menu','.record-upload-glyph','.record-upload-art'];
  function collect(host,label){return new Promise(done=>{const q=wx.createSelectorQuery().in(host);
    selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['backgroundColor','color','fontSize','fontFamily','lineHeight']}));
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
// Keep style reads separate from bounds. DevTools can reject computedStyle on the selector bridge.
const headerGeometry = `function(){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0], info=wx.getWindowInfo();
  const selectors=['.theme-header','.theme-header-art','.theme-header-content','.theme-header .pg-title',
    '.theme-header .screen-heading','.theme-header .rec-title','.theme-header .child-chip',
    '.record-type-title','.record-type-menu','.record-type-choice','.theme-heading-row',
    '.theme-heading-title','.theme-heading-row .child-chip','.theme-heading-row .chip-nm',
    '.theme-heading-row .chev','.theme-heading-title .pg-title','.theme-header-spot','.pg-context'];
  const query=wx.createSelectorQuery();
  selectors.forEach(s=>query.selectAll(s).boundingClientRect());
  query.exec(groups=>resolve({route:p.route,theme:p.data.theme.id,base_library:wx.getAppBaseInfo().SDKVersion,
    viewport:{width:info.windowWidth,height:info.windowHeight,screenWidth:info.screenWidth,screenHeight:info.screenHeight},
    nodes:selectors.flatMap((selector,i)=>(groups[i]||[]).map(({left,right,top,bottom,width,height})=>
      ({host:'page',selector,left,right,top,bottom,width,height}))),
    source:'native selector bounds and DevTools Element.getStyles; isolated fixture, production WXML/WXSS exact'}));
})}`;
const headingSelectors = [".theme-header .pg-title", ".theme-header .screen-heading",
  ".theme-header .rec-title", ".record-type-title"];
async function readHeaderStyles() {
  const { pageId } = await send("App.getCurrentPage");
  const styles = {};
  const names = ["background-color", "border-top-left-radius", "border-top-width", "box-shadow",
    "font-size", "line-height", "color"];
  for (const selector of [".theme-header", ...headingSelectors]) {
    const { elements } = await send("Page.getElements", { pageId, selector });
    if (!elements.length) continue;
    const { elementId } = elements[0];
    const result = await send("Element.getStyles", { pageId, elementId, names });
    styles[selector] = Object.fromEntries(names.map((name, i) => [name, result.styles[i]]));
  }
  return styles;
}

function validateHeader(measured, theme, item) {
  const errors = [];
  const node = (selector) => measured.nodes.find((entry) => entry.selector === selector);
  const frame = node(".theme-header");
  const art = node(".theme-header-art");
  const content = node(".theme-header-content");
  const title = headingSelectors.map(node).find(Boolean);
  const inViewport = (entry) => entry.left >= -1 && entry.right <= measured.viewport.width + 1;
  const shell = measured.styles[".theme-header"];
  if (!frame || !title || !shell) return ["Page header or heading is missing"];
  if (shell["background-color"] !== "rgba(0, 0, 0, 0)" ||
    (shell["border-top-left-radius"] && parseFloat(shell["border-top-left-radius"]) !== 0) ||
    (shell["border-top-width"] && parseFloat(shell["border-top-width"]) !== 0) ||
    (shell["box-shadow"] && shell["box-shadow"] !== "none")) errors.push("Header still has card framing");
  if (Boolean(art) !== Boolean(theme.assets.hero && !item.data.themeArtFailed)) errors.push("Unexpected artwork presence");
  if (art && (!inViewport(art) || Math.abs(art.width - measured.viewport.width) > 1 ||
    Math.abs(art.height - art.width * 304 / 780) > 1 ||
    (content ? Math.abs(art.top - content.top) > 1 : art.top < title.bottom - 1)))
    errors.push("Artwork alignment or natural aspect ratio differs from the design");
  if (!inViewport(frame) || !inViewport(title) || title.bottom > frame.bottom + 1) errors.push("Heading exceeds its frame");
  if (item.route === "pages/reports/index") {
    const style = measured.styles[title.selector];
    if (parseFloat(style["font-size"]) !== 24 || title.height > parseFloat(style["line-height"]) + 1)
      errors.push("Report title must fit a single 24px line");
  }
  if (item.name === "long-title" && title.height <= parseFloat(measured.styles[title.selector]["line-height"]) + 1)
    errors.push("Long heading must wrap");
  if (item.name === "record-menu") {
    const menu = node(".record-type-menu");
    if (!menu || !inViewport(menu) || menu.top < title.bottom - 1) errors.push("Record menu must fit below its trigger");
  }
  for (const entry of measured.nodes.filter((n) => [".theme-header .child-chip", ".record-type-title", ".record-type-choice"].includes(n.selector))) {
    if (entry.height < 43.5 || entry.width < 43.5 || !inViewport(entry)) errors.push("Header control is too small or out of bounds");
  }
  return errors;
}
function validateChildHeading(measured, theme, item) {
  const errors = item.name === "footprints" ? [] : validateHeader(measured, theme, item);
  const all = (selector) => measured.nodes.filter((entry) => entry.selector === selector);
  const [row] = all(".theme-heading-row");
  const [title] = all(".theme-heading-title");
  const chips = all(".theme-heading-row .child-chip");
  const chip = chips[0];
  if (!row || !title || row.left < -1 || row.right > measured.viewport.width + 1) {
    errors.push("Shared title row is missing or exceeds the viewport");
    return errors;
  }
  if (chips.length !== (item.name === "empty" ? 0 : 1)) errors.push("Unexpected number of child selectors");
  if (chip && (Math.abs(chip.right - row.right) > 1 || Math.abs(chip.top - row.top) > 1 ||
      chip.left < title.right || chip.height < 43.5 || chip.width < 43.5)) {
    errors.push("Child selector is not at the top-right of the title row");
  }
  const [name] = all(".theme-heading-row .chip-nm");
  if (item.name === "long-name" && (!chip || !name || name.right > chip.right || name.height > 24)) {
    errors.push("Long child name must stay within a single chip line");
  }
  if (item.name === "single" && all(".theme-heading-row .chev").length) errors.push("Single child shows a switch arrow");
  const showSpot = !theme.assets.hero && !item.data.introArtFailed &&
    ["pages/calendar/index", "pages/reports/index"].includes(item.route);
  if (all(".theme-header-spot").length !== Number(showSpot)) errors.push("Unexpected spot background presence");
  return errors;
}
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
    "if(action==='picker')p.openThemePicker();if(action!=='header')wx.pageScrollTo({scrollTop:0,duration:0});return true;}",
  [theme.id, item.data, headerCapture ? "header" : item.action || ""]);
  await pause(140);
  const measured = await call(headerCapture ? headerGeometry : geometry);
  if (!measured || measured.viewport.screenWidth !== width || measured.viewport.screenHeight !== captureViewports[width]
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
  const title = measured.nodes.find((n) => n.host === "page" && n.selector === ".report-intro .pg-title");
  if (item.route === "pages/reports/index" && (!title || Math.abs(parseFloat(title.fontSize) - 24) > .5 ||
      title.height > parseFloat(title.lineHeight) + 1 || title.left < -1 || title.right > width + 1))
    measured.validation_errors.push("Fixed report title must remain a full 24px line");
  const banner = measured.nodes.find((n) => n.host === "page" && n.selector === ".theme-header-art");
  if (item.route === "pages/records/index" && theme.assets.hero && !item.data.themeArtFailed && !banner)
    measured.validation_errors.push("Expected record banner is absent");
  if (banner && (Math.abs(banner.height - banner.width * 304 / 780) > 1 || banner.left < -1 || banner.right > width + 1))
    measured.validation_errors.push("Record banner must retain its natural ratio inside the viewport");
  if (item.name === "refine-menu" || item.name === "refine-long-name") {
    const menu = measured.nodes.find((n) => n.host === "page" && n.selector === ".record-type-menu");
    if (!menu || menu.left < -1 || menu.right > width + 1) measured.validation_errors.push("Record menu must be visible inside the viewport");
  }
  measured.touch_errors = measured.nodes.filter((n) => [".btn", ".theme-picker-close", ".theme-choice", ".icon-btn", ".add-entry"].includes(n.selector)
    && (n.height < 43.5 || n.width < 43.5)).map((n) => ({ selector: n.selector, width: n.width, height: n.height }));
  if (measured.touch_errors.length) measured.validation_errors.push("Native control touch target below44px");
  measured.horizontal_overflow = measured.nodes.filter((n) => [".page", ".theme-picker-sheet", ".grade-sheet", ".pk-sheet"].includes(n.selector)
    && (n.left < -1 || n.right > width + 1)).map((n) => ({ selector: n.selector, left: n.left, right: n.right }));
  if (headerCapture) {
    measured.styles = await readHeaderStyles();
    measured.validation_errors = childHeading
      ? validateChildHeading(measured, theme, item) : validateHeader(measured, theme, item);
  }
  if (bytes) fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify(measured, null, 2) + "\n");
  return { name, route: item.route, category: item.category, nodes: measured.nodes.length,
    horizontal_overflow: measured.horizontal_overflow, validation_errors: measured.validation_errors,
    screenshot_errors: screenshotErrors, screenshot_sha256: measured.screenshot_sha256 };
}
async function tapElement(selector, index = 0) {
  const { pageId } = await send("App.getCurrentPage");
  const { elements } = await send("Page.getElements", { pageId, selector });
  if (!elements[index]) throw Error("Native tap target missing: " + selector);
  await send("Element.tap", { pageId, elementId: elements[index].elementId });
  await pause(250);
}
async function childSheetActions() {
  const rows = [];
  for (const suffix of ["today", "calendar", "reports", "settings"]) {
    const route = "pages/" + suffix + "/index";
    await navigate(route);
    for (const theme of themes) {
      await call(`function(id,data){
        const app=getApp(),p=getCurrentPages().slice(-1)[0];
        app.theme.setTheme(id);app.selectChild(data.childId);app.themeFixture(data);
        p.load=async()=>{};return true;
      }`, [theme.id, { ...common, ...fixtures[route], children: childChoices, multiChild: true, showChildSheet: false }]);
      const observe = () => call(`function(){
        const p=getCurrentPages().slice(-1)[0],w=wx.getWindowInfo();
        return {open:p.data.showChildSheet,index:p.data.childIndex,id:getApp().globalData.selectedChildId,
          theme:p.data.theme.id,width:w.screenWidth,height:w.screenHeight};
      }`);
      await tapElement(".theme-heading-row .child-chip");
      const open = await observe();
      await tapElement(".child-sheet .icon-btn");
      const cancel = await observe();
      await tapElement(".theme-heading-row .child-chip");
      await tapElement(".child-sheet .rowitem", 1);
      const select = await observe();
      const row = { route, theme: theme.id, open, cancel, select };
      if ([open, cancel, select].some((step) =>
        step.theme !== theme.id || step.width !== width || step.height !== captureViewports[width]) ||
        !open.open || cancel.open || cancel.index !== 0 || cancel.id !== child.id ||
        select.open || select.index !== 1 || select.id !== anotherChild.id) {
        throw Error("Native child sheet flow failed: " + JSON.stringify(row));
      }
      rows.push(row);
      fs.writeFileSync(path.join(out, "child-sheet-actions.json"), JSON.stringify(rows, null, 2) + "\n");
    }
  }
  console.log("NATIVE_CHILD_SHEET_ACTIONS_PASS " + rows.length);
}
async function recordMenuActions() {
  await navigate("pages/records/index");
  async function tap(selector, index) {
    await tapElement(selector, index);
    return call("function(){const p=getCurrentPages().slice(-1)[0],w=wx.getWindowInfo();" +
      "return {type:p.data.recordType,open:p.data.recordTypeOpen,theme:p.data.theme.id,width:w.screenWidth,height:w.screenHeight};}");
  }
  const rows = [];
  for (const theme of themes) {
    await call("function(id,data){const p=getCurrentPages().slice(-1)[0];p.pageVisible=true;" +
      "getApp().theme.setTheme(id);getApp().themeFixture(data);return true;}",
    [theme.id, { ...common, ...fixtures["pages/records/index"], recordTypeOpen: false }]);
    await pause(180);
    const open = await tap(".record-type-title");
    const dismiss = await tap(".record-type-dismiss");
    const reopen = await tap(".record-type-title");
    const travel = await tap(".record-type-choice", 1);
    const embedded = childHeading ? await call(`function(){
      const page=getCurrentPages().slice(-1)[0],view=page.selectComponent('#travel-diary');
      if(!view)return {present:false,extraChildHeading:false};
      return new Promise(resolve=>{
        const query=wx.createSelectorQuery().in(view);
        query.select('.fp-embedded').boundingClientRect();
        query.select('.theme-heading-row').boundingClientRect();
        query.exec(([host,heading])=>resolve({present:!!host,extraChildHeading:!!heading}));
      });
    }`) : undefined;
    const reopenTravel = await tap(".record-type-title");
    const learning = await tap(".record-type-choice");
    const result = { theme: theme.id, open, dismiss, reopen, travel, embedded, reopenTravel, learning };
    const steps = [open, dismiss, reopen, travel, reopenTravel, learning];
    if (steps.some((step) => step.theme !== theme.id || step.width !== width || step.height !== captureViewports[width]) ||
      !open.open || dismiss.open || !reopen.open || travel.open || travel.type !== "travel" ||
      (childHeading && (!embedded.present || embedded.extraChildHeading)) ||
      !reopenTravel.open || learning.open || learning.type !== "learning")
      throw Error("Native record menu flow failed: " + JSON.stringify(result));
    rows.push(result);
    fs.writeFileSync(path.join(out, "header-record-actions.json"), JSON.stringify(rows, null, 2) + "\n");
  }
  console.log("NATIVE_RECORD_MENU_ACTIONS_PASS " + rows.length);
}
async function run() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  fs.mkdirSync(out, { recursive: true });
  const start = Date.now(), results = [], failures = [];
  const matrixKind = childHeading ? "-child-heading" : headerBlend ? "-headers" : "";
  const reportFile = path.join(out, "matrix" + matrixKind + (only ? "-" + only : "") + (caseFilter ? "-" + caseFilter : "") +
    ".json");
  const saveReport = () => fs.writeFileSync(reportFile, JSON.stringify({ width, themes: themes.map((t) => t.id),
    groups: results.length, elapsed_ms: Date.now() - start, results, failures, navigation_diagnostics: navigationDiagnostics,
    source_manifest_sha256: crypto.createHash("sha256").update(fs.readFileSync(path.join(out, "source-sha256.json"))).digest("hex") }, null, 2) + "\n");
  fs.copyFileSync(path.join(project, "theme-source-sha256.json"), path.join(out, "source-sha256.json"));
  if (process.argv.includes("--child-sheet-actions")) {
    await childSheetActions();
    return;
  }
  if (process.argv.includes("--header-actions")) {
    await recordMenuActions();
    return;
  }
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
  const allItems = childHeading ? childHeadingScenarios : headerBlend ? headerScenarios : [...appConfig.pages.map((route) => ({ name: route.replace(/^pages\//, "").replace(/\//g, "-"),
    category: "route", route, data: { ...common, ...fixtures[route] } })), ...shared.map((s) => ({ ...s, name: "state-" + s.name, category: "state" })),
    ...(process.argv.includes("--refinement") ? refinement : [])];
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
