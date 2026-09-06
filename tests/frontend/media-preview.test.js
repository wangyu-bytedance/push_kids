const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

/* utils/api.js 只依赖 getApp/wx，直接在裸 VM 里加载，避免拉起整页。 */
function loadApi({ globalData, wx = {} }) {
  const file = path.resolve("apps/miniprogram/utils/api.js");
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(file, "utf8"), {
    module,
    require() { return {}; },
    wx,
    getApp: () => ({ globalData })
  }, { filename: file });
  return module.exports;
}

test("cloud preview uses the server-signed https url instead of downloadFile", async () => {
  let downloaded = false;
  const api = loadApi({
    globalData: { useCloud: true, familyId: "family" },
    wx: { downloadFile() { downloaded = true; } }
  });
  const url = await api.downloadPreview({ url: "https://cdn.example.com/a.jpg?sign=1", download_path: "/submissions/s/media/m" });
  assert.equal(url, "https://cdn.example.com/a.jpg?sign=1");
  assert.equal(downloaded, false);
});

test("cloud preview without an https capability fails instead of hitting the container", async () => {
  const api = loadApi({ globalData: { useCloud: true, familyId: "family" }, wx: {} });
  await assert.rejects(() => api.downloadPreview({ url: "", download_path: "/submissions/s/media/m" }), /重试/);
});

test("local preview downloads with identity headers and keeps the temp file", async () => {
  let seen = null;
  const api = loadApi({
    globalData: { useCloud: false, apiBaseUrl: "http://127.0.0.1:8000/api/v1", localActorId: "actor" },
    wx: { downloadFile(options) { seen = options; options.success({ statusCode: 200, tempFilePath: "wxfile://tmp/a.jpg" }); } }
  });
  const file = await api.downloadPreview({ download_path: "/submissions/s/media/m" });
  assert.equal(file, "wxfile://tmp/a.jpg");
  assert.equal(seen.url, "http://127.0.0.1:8000/api/v1/submissions/s/media/m");
  assert.equal(seen.header["X-Debug-Actor"], "actor");
});

test("removePreview only unlinks local temp files", () => {
  const unlinked = [];
  const api = loadApi({
    globalData: { useCloud: true },
    wx: { getFileSystemManager: () => ({ unlink({ filePath }) { unlinked.push(filePath); } }) }
  });
  api.removePreview("https://cdn.example.com/a.jpg");
  api.removePreview("");
  api.removePreview("wxfile://tmp/a.jpg");
  assert.equal(unlinked.join(","), "wxfile://tmp/a.jpg");
});
