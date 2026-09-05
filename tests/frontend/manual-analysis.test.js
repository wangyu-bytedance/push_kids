const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function confirmation(request) {
  let page;
  vm.runInNewContext(fs.readFileSync("apps/miniprogram/pages/submission/confirm.js", "utf8"), {
    require(name) { return name.includes("api") ? { request } : { friendlyTime: (value) => value }; },
    Page(value) { page = value; }, wx: { showToast() {}, navigateBack() {} }, setTimeout() {}
  });
  page.setData = (updates) => {
    for (const [path, value] of Object.entries(updates)) {
      const parts = path.replace(/\[(\d+)\]/g, ".$1").split(".");
      let target = page.data;
      for (const part of parts.slice(0, -1)) target = target[part];
      target[parts.at(-1)] = value;
    }
  };
  return page;
}

test("manual form handles failed AI, retains full original text and filters activities", async () => {
  const original = "学".repeat(501);
  const page = confirmation(async (path) => path.includes("subjects") ? [
    { id: "math", name: "数学", kind: "learning" }, { id: "swim", name: "游泳", kind: "activity" }
  ] : { state: "failed", child_id: "child", input_text: original, occurred_at: "2026-09-05" });
  page.data.manual = true;
  await page.load();
  assert.equal(page.data.error, "");
  assert.equal(page.data.submission.input_text, original);
  assert.equal(page.data.proposal.summary, "");
  assert.equal(page.data.subjects.length, 1);
  assert.equal(page.data.proposal.source, "人工录入");
  assert.equal(page.data.proposal.todo_matches.length, 0);
});

test("manual save bypasses analysis, blocks duplicate click and retains form on failure", async () => {
  let rejectSave;
  const calls = [];
  const page = confirmation(async (path, options) => {
    calls.push({ path, options });
    return new Promise((resolve, reject) => { rejectSave = reject; });
  });
  page.data.id = "original";
  page.data.manual = true;
  page.data.proposal = { summary: "练习加法", subject_name: "数学", knowledge_points: [{ name: "加法" }], todo_matches: [] };
  const saving = page.confirm();
  await page.confirm();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].path, "/submissions/original/confirm");
  assert.equal(calls[0].options.data.manual_entry, true);
  rejectSave(new Error("服务暂时不可用"));
  await saving;
  assert.equal(page.data.proposal.summary, "练习加法");
  assert.equal(page.data.saveError, "服务暂时不可用");
  assert.equal(page.data.saving, false);
});

test("editing a matched concept or subject clears the old identity", () => {
  const page = confirmation(async () => ({}));
  page.data.proposal = { knowledge_points: [{ name: "加法", existing_knowledge_id: "known" }], todo_matches: [{ review_id: "review" }] };
  page.setPoint({ currentTarget: { dataset: { index: 0, field: "name" } }, detail: { value: "除法" } });
  assert.equal(page.data.proposal.knowledge_points[0].existing_knowledge_id, null);
  page.data.subjects = [{ name: "英语" }];
  page.changeSubject({ detail: { value: "0" } });
  assert.equal(page.data.proposal.todo_matches.length, 0);
  assert.equal(page.data.proposal.subject_kind, "learning");
});
