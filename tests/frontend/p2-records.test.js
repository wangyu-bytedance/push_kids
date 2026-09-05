const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

test("confirmation derives readable low-confidence and evidence labels", async () => {
  let page;
  const proposal = { subject_name: "数学", uncertainties: ["题目不完整"], knowledge_points: [{
    name: "分数", confidence: "low", direct_evidence: [{ source: "image", image_index: 1, detail: "题目标题" }]
  }] };
  vm.runInNewContext(fs.readFileSync("apps/miniprogram/pages/submission/confirm.js", "utf8"), {
    require(name) { return name.includes("api") ? { request: async (path) => path.includes("/subjects") ? [] : {
      state: "pending_confirmation", child_id: "child", occurred_at: "2026-09-05T10:00:00Z", proposal
    } } : { friendlyTime: (value) => value }; },
    Page(value) { page = value; }, wx: {}
  });
  page.setData = (value) => Object.assign(page.data, value);
  await page.load();
  const point = page.data.proposal.knowledge_points[0];
  assert.equal(point.confidence_label, "不确定，请重点核对");
  assert.equal(point.evidence_labels[0], "照片 1：题目标题");
  assert.equal(page.data.proposal.uncertainties[0], "题目不完整");
});

test("cloud resume uploads and claims into the existing draft before finalizing", async () => {
  const calls = [];
  const exports = { exports: {} };
  vm.runInNewContext(fs.readFileSync("apps/miniprogram/utils/cloud-media.js", "utf8"), {
    module: exports,
    require() { return { async request(path, options) {
      calls.push({ path, options });
      if (path === "/media/upload-tickets") return { ticket_id: "ticket", cloud_path: "staging/synthetic" };
      return {};
    } }; },
    getApp: () => ({ globalData: { cloudEnv: "synthetic" } }),
    wx: {
      getFileInfo(options) { options.success({ size: 100 }); },
      getImageInfo(options) { options.success({ type: "png" }); },
      cloud: { uploadFile(options) { options.success({ fileID: "cloud://synthetic/file" }); return { onProgressUpdate() {} }; } }
    }
  });
  await exports.exports.uploadDraftPhotos({ id: "original", media_count: 8 }, ["local-photo"], null, "stable-key");
  assert.deepEqual(calls.map((item) => item.path), ["/media/upload-tickets", "/media/claims", "/submissions/original/finalize"]);
  assert.equal(calls[0].options.data.submission_id, "original");
  assert.equal(calls[0].options.idempotencyKey, "stable-key-media-8");
});
