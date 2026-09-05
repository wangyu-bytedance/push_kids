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
  assert.equal(instance.data.media[0].thumbnail, undefined);
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
