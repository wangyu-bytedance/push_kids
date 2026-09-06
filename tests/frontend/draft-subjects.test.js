const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./harness");

/* 一次上传混了几个科目：草稿必须按孩子已配置的科目分组，
   绝不能出现「自定义：数学.语文、英语」这种混合科目。 */
const SUBJECTS = [
  { id: "math", name: "数学", kind: "learning" },
  { id: "chinese", name: "语文", kind: "learning" },
  { id: "swim", name: "游泳", kind: "activity" }
];

function pendingSubmission(points, extra = {}) {
  return {
    id: "sid", child_id: "child", state: "pending_confirmation", source: "photo", media_count: 3,
    occurred_at: "2026-09-05T10:00:00Z", created_at: "2026-09-05T11:00:00Z",
    proposal: { summary: "写了加法和生字", subject_name: points[0].subject_name, subject_kind: "learning",
      source: "照片", uncertainties: [], todo_matches: [], knowledge_points: points },
    ...extra
  };
}

function draftPage(entry, submission, onConfirm, options = {}) {
  const calls = [];
  const request = async (path, requestOptions) => {
    calls.push({ path, options: requestOptions });
    if (path.includes("/subjects")) return SUBJECTS;
    if (path.includes("/confirm")) return onConfirm ? onConfirm(requestOptions, calls) : {};
    if (path.includes("/history/")) return { record: null, records: [], knowledge: [], media: [] };
    return submission;
  };
  const loaded = loadPage(entry, request, options);
  return { ...loaded, calls };
}

test("a mixed photo batch splits into one group per configured subject", async () => {
  const { page } = draftPage("pages/submission/confirm.js", pendingSubmission([
    { name: "两位数加法", subject_name: "数学", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 },
    { name: "生字听写", subject_name: "语文", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 },
    { name: "进位", subject_name: "数学", category: "知识点", review_method: "口头回顾", estimated_minutes: 3 }
  ], { subject_review_needed: true }));
  page.data.id = "sid";
  await page.load();
  assert.equal(page.data.editing, true);
  assert.equal(page.data.subjectReview, true);
  /* 只有学习科目能进草稿：课外活动走活动入口。 */
  assert.equal(page.data.subjects.map((item) => item.name).join(","), "数学,语文");
  assert.equal(page.data.groups.map((item) => item.subject_name).join(","), "数学,语文");
  assert.equal(page.data.groups[0].indexes.join(","), "0,2");
  assert.equal(page.data.groups[1].indexes.join(","), "1");
  assert.equal(page.data.groups[0].subject_id, "math");
  assert.ok(page.data.groups.every((group) => group.listed));
  assert.equal(page.data.subjectPicks.at(-1), "＋ 写一个新科目");
});

test("confirmation sends one group per subject with positions that match the kept points", async () => {
  let payload;
  const { page } = draftPage("pages/submission/confirm.js", pendingSubmission([
    { name: "两位数加法", subject_name: "数学" },
    { name: "", subject_name: "数学" },
    { name: "生字听写", subject_name: "语文" }
  ]), (options) => { payload = options.data; return { record_id: "r1", records: [] }; });
  page.data.id = "sid";
  await page.load();
  await page.confirmDraft();
  assert.equal(payload.manual_entry, false);
  /* 空知识点先被丢掉，knowledge_indexes 按过滤后的位置写，和服务端分组完全对齐。 */
  assert.equal(payload.proposal.knowledge_points.length, 2);
  assert.equal(payload.groups.map((group) => group.subject_name).join(","), "数学,语文");
  assert.equal(payload.groups[0].knowledge_indexes.join(","), "0");
  assert.equal(payload.groups[1].knowledge_indexes.join(","), "1");
  assert.equal(payload.groups[0].subject_id, "math");
  assert.equal(payload.subject_id, null, "跨科目时不再用单一科目字段");
});

test("an unlisted subject is only created after the parent answers yes", async () => {
  const asked = [];
  let attempts = 0;
  const { page, calls } = draftPage("pages/submission/confirm.js", pendingSubmission([
    { name: "字母表", subject_name: "英语" }
  ]), (options) => {
    attempts += 1;
    if (!options.data.groups[0].create_subject) {
      const error = new Error("「英语」还不在科目列表里，要新增这个科目吗？");
      error.statusCode = 409;
      error.code = "consent_required";
      throw error;
    }
    return { record_id: "r1", records: [] };
  }, { wx: { showModal(params) { asked.push(params.title); params.success({ confirm: true }); } } });
  page.data.id = "sid";
  await page.load();
  assert.equal(page.data.groups[0].listed, false);
  assert.equal(page.data.groups[0].create_subject, false);
  await page.confirmDraft();
  assert.equal(attempts, 2, "第一次被服务端挡下，家长同意后才重试");
  assert.equal(asked.join(","), "要新增这个科目吗？");
  assert.equal(calls.at(-1).options.data.groups[0].create_subject, true);
  assert.equal(page.data.saveError, "");
});

test("declining the new subject writes nothing and keeps the draft editable", async () => {
  let attempts = 0;
  const { page } = draftPage("pages/submission/confirm.js", pendingSubmission([
    { name: "字母表", subject_name: "英语" }
  ]), () => {
    attempts += 1;
    const error = new Error("「英语」还不在科目列表里，要新增这个科目吗？");
    error.statusCode = 409;
    error.code = "consent_required";
    throw error;
  }, { wx: { showModal(params) { params.success({ confirm: false }); } } });
  page.data.id = "sid";
  await page.load();
  await page.confirmDraft();
  assert.equal(attempts, 1);
  assert.equal(page.data.editing, true);
  assert.equal(page.data.saving, false);
  assert.match(page.data.saveError, /英语/);
  /* 冲突提示只给「已被处理过」用，这里不能误报。 */
  assert.equal(page.data.conflict, false);
});

test("moving a whole group onto an existing subject drops the unlisted one", async () => {
  const { page } = draftPage("pages/submission/confirm.js", pendingSubmission([
    { name: "字母表", subject_name: "英文" },
    { name: "生字听写", subject_name: "语文" }
  ]));
  page.data.id = "sid";
  await page.load();
  assert.equal(page.data.groups[0].listed, false);
  page.toggleCreateSubject({ currentTarget: { dataset: { group: 0 } }, detail: { value: true } });
  assert.equal(page.data.groups[0].create_subject, true);
  await page.moveGroupSubject({ currentTarget: { dataset: { group: 0 } }, detail: { value: "0" } });
  assert.equal(page.data.groups.map((item) => item.subject_name).join(","), "数学,语文");
  assert.ok(page.data.groups.every((group) => group.listed));
});

test("a pending draft is editable in place on the record page without another hop", async () => {
  const navigations = [];
  const { page } = draftPage("pages/record-detail/index.js", pendingSubmission([
    { name: "两位数加法", subject_name: "数学" }
  ]), null, { wx: { navigateTo(params) { navigations.push(params.url); } } });
  page.data.id = "sid";
  await page.load();
  assert.equal(page.data.editing, true);
  assert.equal(page.data.proposal.summary, "写了加法和生字");
  assert.equal(page.data.groups.length, 1);
  assert.equal(navigations.length, 0, "待确认页直接编辑，不再跳转确认页");
});

test("a viewer cannot edit the pending draft in place", async () => {
  const { page } = draftPage("pages/record-detail/index.js", pendingSubmission([
    { name: "两位数加法", subject_name: "数学" }
  ]), null, { globalData: { currentMember: { role: "viewer" } } });
  page.data.id = "sid";
  await page.load();
  assert.equal(page.data.canWrite, false);
  assert.equal(page.data.editing, false);
  assert.equal(page.data.proposal, null);
});
