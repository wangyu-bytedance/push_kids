const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function material(api, wx = {}) {
  let definition;
  vm.runInNewContext(fs.readFileSync("apps/miniprogram/components/submission-materials/index.js", "utf8"), {
    Component(value) { definition = value; }, require() { return api; }, wx
  });
  const instance = { ...definition.methods, data: { ...definition.data, childId: "child", submissionId: "sid" } };
  instance.setData = (updates) => {
    for (const [key, value] of Object.entries(updates)) {
      const parts = key.replace(/\[(\d+)\]/g, ".$1").split(".");
      let target = instance.data;
      for (const part of parts.slice(0, -1)) target = target[part];
      target[parts.at(-1)] = value;
    }
  };
  return { instance, definition };
}

test("materials stay lazy, bound download concurrency and clean all temporary previews", async () => {
  const calls = [], removed = [];
  let inFlight = 0, maximum = 0;
  const { instance, definition } = material({
    async request(url) {
      calls.push(url);
      return url.includes("/history/") ? { input_text: "完整原文", media: [1, 2, 3].map((i) => ({ id: String(i), available: true })) } : { url: `https://fixture.invalid/${calls.length}` };
    },
    async downloadPreview(capability) { inFlight += 1; maximum = Math.max(maximum, inFlight); await Promise.resolve(); inFlight -= 1; return capability.url; },
    removePreview(path) { removed.push(path); }
  }, { downloadFile() {} });
  assert.equal(calls.length, 0);
  await instance.load();
  assert.equal(maximum, 2);
  assert.equal(instance.paths.length, 3);
  assert.equal(instance.data.text, "完整原文");
  definition.lifetimes.detached.call(instance);
  assert.equal(removed.length, 3);
  assert.equal(instance.data.text, "");
  assert.equal(instance.data.media.length, 0);
});

test("late photo completion after leaving is deleted and cannot populate another view", async () => {
  let release;
  let started;
  const downloading = new Promise((resolve) => { started = resolve; });
  const removed = [];
  const { instance, definition } = material({
    async request(url) { return url.includes("/history/") ? { media: [{ id: "photo", available: true }] } : { url: "https://fixture.invalid" }; },
    downloadPreview() { return new Promise((resolve) => { release = resolve; started(); }); },
    removePreview(path) { removed.push(path); }
  }, { downloadFile() {} });
  const loading = instance.load();
  await downloading;
  definition.pageLifetimes.hide.call(instance);
  release("temporary-file"); await loading;
  assert.deepEqual(removed, ["temporary-file"]);
  assert.equal(instance.data.media.length, 0);
});

test("permission loss clears original material and preview URLs", async () => {
  const removed = [];
  const { instance } = material({
    async request() { const error = new Error("权限已失效"); error.statusCode = 403; throw error; },
    removePreview(path) { removed.push(path); }
  });
  instance.paths = ["old-private-file"]; instance.data.text = "旧原文";
  await instance.load();
  assert.equal(instance.data.text, "");
  assert.equal(instance.data.error, "权限已失效");
  assert.deepEqual(removed, ["old-private-file"]);
});

test("embedded materials open and load immediately while keeping ordinary cards lazy", () => {
  const { instance, definition } = material({ removePreview() {} });
  let loads = 0;
  instance.load = () => { loads += 1; };

  definition.observers["submissionId, defaultOpen, submissionState, embedded, childId, exactSource, highlightIndex"].call(
    instance, "sid", false, "confirmed", true
  );

  assert.equal(instance.data.open, true);
  assert.equal(loads, 1);
});

test("exact sources download and preview only the matching original index, including an unavailable predecessor", async () => {
  const calls = [], downloads = [], previews = [];
  const { instance } = material({
    async request(url) {
      calls.push(url);
      return url.includes('/history/') ? { source: 'photo', input_text: '其他原文', media: [
        { id: 'a1', index: 1, available: false }, { id: 'a2', index: 2, available: true },
        ...[3, 4, 5, 6, 7, 8, 9].map(index => ({ id: `a${index}`, index, available: true }))
      ] } : { url: 'private-a2' };
    },
    async downloadPreview(value) { downloads.push(value.url); return value.url; },
    removePreview() {}
  }, { previewImage(value) { previews.push(value); } });
  Object.assign(instance.data, { exactSource: true, highlightIndex: 2, submissionId: 'A' });
  await instance.load();
  assert.equal(instance.data.media.length, 1);
  assert.equal(instance.data.media[0].index, 2);
  assert.equal(instance.data.text, '');
  await instance.preview({ currentTarget: { dataset: { id: 'a3' } } });
  await instance.preview({ currentTarget: { dataset: { id: 'a2' } } });
  assert.deepEqual(calls, ['/children/child/history/A', '/submissions/A/media/a2/preview?child_id=child', '/submissions/A/media/a2/preview?child_id=child']);
  assert.equal(downloads.length, 2);
  assert.deepEqual(Array.from(previews[0].urls), ['private-a2']);
});

test("unknown and invalid indices never load another image or mixed batch text", async () => {
  for (const index of [undefined, null, 0, -1, 10, true, '2', 3]) {
    const calls = [];
    const { instance } = material({
      async request(url) { calls.push(url); return { source: 'photo', input_text: '其他内容', media: [{ id: 'a2', index: 2, available: true }] }; },
      removePreview() {}
    });
    Object.assign(instance.data, { exactSource: true, highlightIndex: index });
    await instance.load();
    assert.equal(calls.length, 1);
    assert.equal(instance.data.media.length, 0);
    assert.equal(instance.data.text, '');
    assert.equal(instance.data.unknownSource, true);
  }
});

test("exact source preserves manual text and unavailable target without replacing it", async () => {
  const { instance } = material({ async request() { return { source: 'manual', input_text: '家长原文', media: [] }; }, removePreview() {} });
  instance.data.exactSource = true;
  await instance.load();
  assert.equal(instance.data.text, '家长原文');
  assert.equal(instance.data.unknownSource, false);
});

test("changing index within a submission invalidates a late thumbnail", async () => {
  let release, started;
  const waiting = new Promise(resolve => { started = resolve; });
  const removed = [];
  const { instance, definition } = material({
    async request(url) { return url.includes('/history/') ? { source: 'photo', media: [1, 2].map(i => ({ id: `a${i}`, index: i, available: true })) } : { url }; },
    downloadPreview(value) {
      if (value.url.includes('/a1/')) return new Promise(resolve => { release = resolve; started(); });
      return Promise.resolve('a2-preview');
    },
    removePreview(value) { removed.push(value); }
  });
  Object.assign(instance.data, { exactSource: true, highlightIndex: 1 });
  const first = instance.load();
  await waiting;
  instance.data.highlightIndex = 2;
  const observer = Object.values(definition.observers)[0];
  observer.call(instance, 'sid', true, 'confirmed', true);
  await new Promise(resolve => setImmediate(resolve));
  release('late-a1'); await first;
  assert.equal(instance.data.media[0].index, 2);
  assert.equal(instance.data.media[0].thumbnail, 'a2-preview');
  assert.ok(removed.includes('late-a1'));
});

test("exact source errors never request a substitute photo and network failure can retry", async () => {
  for (const statusCode of [403, 410, 503]) {
    let failing = true;
    const previews = [];
    const { instance } = material({
      async request(url) {
        if (url.includes('/history/')) return { source: 'photo', media: [1, 2, 3].map(index => ({ id: `a${index}`, index, available: true })) };
        previews.push(url);
        if (failing) throw Object.assign(new Error('读取失败'), { statusCode });
        return { url: 'target-only' };
      },
      async downloadPreview() { return 'target-only'; }, removePreview() {}
    });
    Object.assign(instance.data, { exactSource: true, highlightIndex: 2 });
    await instance.load();
    assert.equal(instance.data.error, '读取失败');
    assert.equal(previews.length, 1);
    assert.ok(previews.every(url => url.includes('/media/a2/')));
    if (statusCode === 403) assert.equal(instance.data.media.length, 0);
    if (statusCode === 410) assert.equal(instance.data.media[0].unavailable, true);
    failing = false;
    await instance.load();
    assert.equal(instance.data.media[0].thumbnail, 'target-only');
    assert.equal(instance.data.error, '');
  }
});

test("hiding clears downloaded private media and ignores late platform preview failure", async () => {
  let fail;
  const removed = [];
  const { instance, definition } = material({
    async request(url) { return url.includes('/history/') ? { media: [{ id: 'a2', index: 2, available: true }] } : {}; },
    async downloadPreview() { return 'private-file'; }, removePreview(path) { removed.push(path); }
  }, { previewImage(value) { fail = value.fail; } });
  Object.assign(instance.data, { exactSource: true, highlightIndex: 2 });
  await instance.load();
  await instance.preview({ currentTarget: { dataset: { id: 'a2' } } });
  definition.pageLifetimes.hide.call(instance);
  fail();
  assert.equal(instance.paths.length, 0);
  assert.equal(instance.data.media.length, 0);
  assert.equal(instance.data.error, '');
  assert.ok(removed.includes('private-file'));
});
