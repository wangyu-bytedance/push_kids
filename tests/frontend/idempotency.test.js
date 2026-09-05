const test = require("node:test");
const assert = require("node:assert/strict");
const api = require("../../apps/miniprogram/utils/api");

test("submission retry keys are stable-format and unique", () => {
  const first = api.newIdempotencyKey("manual");
  const second = api.newIdempotencyKey("manual");
  assert.match(first, /^manual-\d+-[a-z0-9]+$/);
  assert.notEqual(first, second);
});

test("request forwards an idempotency key without exposing it in payload", async () => {
  global.getApp = () => ({ globalData: { apiBaseUrl: "http://api.test", familyId: "family-a" } });
  let captured;
  global.wx = {
    request(options) {
      captured = options;
      options.success({ statusCode: 202, data: { id: "submission-1" } });
    }
  };

  const result = await api.request("/submissions", {
    method: "POST",
    idempotencyKey: "manual-stable-retry-001",
    data: { input_text: "数学进位加法" }
  });

  assert.equal(result.id, "submission-1");
  assert.equal(captured.header["Idempotency-Key"], "manual-stable-retry-001");
  assert.equal(captured.header["X-Family-ID"], "family-a");
  assert.deepEqual(captured.data, { input_text: "数学进位加法" });
  delete global.getApp;
  delete global.wx;
});

test("upload forwards the same retry key", async () => {
  global.getApp = () => ({ globalData: { apiBaseUrl: "http://api.test", familyId: "family-a" } });
  let captured;
  global.wx = {
    uploadFile(options) {
      captured = options;
      options.success({ statusCode: 202, data: JSON.stringify({ id: "submission-2" }) });
      return { onProgressUpdate() {} };
    }
  };

  const result = await api.uploadSubmission(
    "/tmp/homework.png",
    { child_id: "child-1" },
    null,
    "photo-stable-retry-001"
  );

  assert.equal(result.id, "submission-2");
  assert.equal(captured.header["Idempotency-Key"], "photo-stable-retry-001");
  delete global.getApp;
  delete global.wx;
});
