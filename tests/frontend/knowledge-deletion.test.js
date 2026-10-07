const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { loadPage } = require("./harness");

function today(request) {
  const result = loadPage("pages/today/index.js", request);
  Object.assign(result.page.data, { childId: "child", canWrite: true });
  result.page.load = async () => { result.reloads = (result.reloads || 0) + 1; };
  return result;
}
const target = { detail: { knowledgeId: "knowledge-2", name: "年龄问题" } };

test("cloud bootstrap cannot expose delete before a writable membership is known", async () => {
  for (const role of ['viewer', 'manager', 'editor']) {
    let release;
    const calls = [];
    const { page, app } = loadPage('pages/today/index.js', async path => { calls.push(path); return []; },
      { globalData: { useCloud: true, currentMember: null } });
    app.refreshBootstrap = () => new Promise(resolve => { release = () => {
      app.globalData.currentMember = { role }; resolve();
    }; });
    page.onShow();
    assert.equal(page.data.canWrite, false);
    page.openDelete(target);
    assert.equal(page.data.deleteTarget, null);
    assert.equal(calls.length, 0);
    release();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(page.data.canWrite, role !== 'viewer');
    assert.deepEqual(calls, ['/children']);
  }
});

test("delete follows defer, uses a separate event, and requires confirmation", async () => {
  const xml = fs.readFileSync("apps/miniprogram/components/todo-card/index.wxml", "utf8");
  assert.ok(xml.indexOf('class="fb fb-delete"') > xml.indexOf('wx:for="{{view.actions}}"'));
  const calls = [];
  const { page } = today(async (...args) => { calls.push(args); });
  page.openDelete(target);
  assert.equal(page.data.deleteTarget.knowledgeId, "knowledge-2");
  assert.equal(calls.length, 0);
  page.cancelDelete();
  await page.confirmDelete();
  assert.equal(calls.length, 0);
  page.openDelete(target);
  await page.confirmDelete();
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "/children/child/knowledge/knowledge-2");
  assert.equal(calls[0][1].method, "DELETE");
  assert.equal(page.data.deleteTarget, null);
});

test("delete is pessimistic, blocks duplicate confirms and retains recoverable errors", async () => {
  let reject;
  const result = today(() => new Promise((_resolve, fail) => { reject = fail; }));
  const { page } = result;
  page.data.todoCards = [{ id: "original" }];
  page.openDelete(target);
  const saving = page.confirmDelete();
  await page.confirmDelete();
  page.cancelDelete();
  assert.equal(page.data.deleting, true);
  assert.equal(page.data.todoCards[0].id, "original");
  reject(new Error("网络异常")); await saving;
  assert.equal(page.data.deleting, false);
  assert.equal(page.data.deleteTarget.knowledgeId, "knowledge-2");
  assert.equal(page.data.deleteError, "网络异常");
  assert.equal(result.reloads, undefined);
});

test("viewer and late delete responses cannot mutate another child or hidden page", async () => {
  let release;
  const result = today(() => new Promise(resolve => { release = resolve; }));
  const { page } = result;
  page.data.canWrite = false;
  page.openDelete(target);
  assert.equal(page.data.deleteTarget, null);
  page.data.canWrite = true;
  page.openDelete(target);
  const saving = page.confirmDelete();
  page.onHide();
  page.data.childId = "other";
  release(); await saving;
  assert.equal(result.reloads, undefined);
  assert.equal(page.data.childId, "other");
  assert.equal(page.data.deleteTarget, null);
});

test("card emits the selected knowledge identity only for a writer", () => {
  const { page: component } = loadPage("components/todo-card/index.js", async () => {});
  Object.assign(component, component.methods);
  component.data.canWrite = true;
  const events = [];
  component.triggerEvent = (name, detail) => events.push({ name, detail });
  component.buildView({ items: [{ knowledge_id: "k2", review_id: "r2", knowledge_name: "年龄问题" }] });
  component.deleteRecord({ currentTarget: { dataset: { reviewId: "r2" } } });
  assert.equal(events[0].name, "delete");
  assert.equal(events[0].detail.knowledgeId, "k2");
  component.data.canWrite = false;
  component.deleteRecord({ currentTarget: { dataset: { reviewId: "r2" } } });
  assert.equal(events.length, 1);
});
