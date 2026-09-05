const test = require("node:test");
const assert = require("node:assert/strict");
const api = require("../../apps/miniprogram/utils/api");
const cloudMedia = require("../../apps/miniprogram/utils/cloud-media");

test("cloud requests use callContainer without a client family header", async () => {
  global.getApp = () => ({ globalData: {
    useCloud: true,
    cloudEnv: "prod-test",
    cloudService: "push-kids",
    apiBasePath: "/api/v1"
  } });
  let captured;
  global.wx = { cloud: { callContainer(options) {
    captured = options;
    options.success({ statusCode: 200, data: { ok: true } });
  } } };
  const result = await api.request("/children", { idempotencyKey: "stable-request-001" });
  assert.equal(result.ok, true);
  assert.equal(captured.path, "/api/v1/children");
  assert.equal(captured.config.env, "prod-test");
  assert.equal(captured.header["X-WX-SERVICE"], "push-kids");
  assert.equal(captured.header["X-Family-ID"], undefined);
  assert.equal(captured.header["Idempotency-Key"], "stable-request-001");
  delete global.getApp;
  delete global.wx;
});

test("cloud media upload uses the server-issued path and configured environment", async () => {
  global.getApp = () => ({ globalData: { useCloud: true, cloudEnv: "prod-test" } });
  let captured;
  global.wx = { cloud: { uploadFile(options) {
    captured = options;
    options.success({ fileID: "cloud://prod-test/staging/file.png" });
    return { onProgressUpdate(callback) { callback({ progress: 50 }); } };
  } } };
  let progress;
  const fileID = await cloudMedia.uploadObject(
    "wxfile://photo.png",
    "staging/server-issued.png",
    (value) => { progress = value; }
  );
  assert.equal(fileID, "cloud://prod-test/staging/file.png");
  assert.equal(captured.cloudPath, "staging/server-issued.png");
  assert.equal(captured.config.env, "prod-test");
  assert.equal(progress, 50);
  delete global.getApp;
  delete global.wx;
});
