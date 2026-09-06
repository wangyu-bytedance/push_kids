const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../../apps/miniprogram");

function loadPage(request) {
  let definition;
  const calls = [];
  const storage = {};
  const navigations = [];
  const app = {
    globalData: { familyId: "family", selectedChildId: "child" },
    refreshBootstrap: async () => ({
      state: "bound",
      family: { id: "family", display_name: "小芽的家" },
      member: { role: "manager" },
      children: []
    }),
    selectChild(id) { this.globalData.selectedChildId = id; }
  };
  const filename = path.join(root, "pages/delete-settings/index.js");
  vm.runInNewContext(fs.readFileSync(filename, "utf8"), {
    require() {
      return {
        newIdempotencyKey: () => "delete-request-key",
        request: async (requestPath, options = {}) => {
          calls.push({ path: requestPath, options });
          return request(requestPath, options);
        }
      };
    },
    Page(value) { definition = value; },
    getApp: () => app,
    setTimeout() { return 1; },
    clearTimeout() {},
    wx: {
      getStorageSync(key) { return storage[key] || ""; },
      setStorageSync(key, value) { storage[key] = value; },
      removeStorageSync(key) { delete storage[key]; },
      reLaunch(options) { navigations.push(options.url); },
      navigateBack() { navigations.push("back"); },
      showToast() {}
    }
  }, { filename });
  const page = {
    ...definition,
    data: JSON.parse(JSON.stringify(definition.data)),
    setData(update) { Object.assign(this.data, update); }
  };
  return { page, calls, storage, navigations, app };
}

test("delete settings keeps the entry neutral and danger at final confirmation", () => {
  const settings = fs.readFileSync(path.join(root, "pages/settings/index.wxml"), "utf8");
  const page = fs.readFileSync(path.join(root, "pages/delete-settings/index.wxml"), "utf8");
  assert.match(settings, /删除配置/);
  assert.match(settings, /wx:if="\{\{isManager\}\}"/);
  assert.doesNotMatch(settings, /rowitem danger/);
  assert.match(page, /确认永久清理/);
  assert.match(page, /btn danger/);
});

test("canceling the confirmation performs no write", () => {
  const { page, calls } = loadPage(async () => []);
  page.setData({ mode: "child", targetId: "child", targetName: "小芽", confirmationName: "小芽" });
  page.cancelConfirmation();
  assert.equal(calls.length, 0);
  assert.equal(page.data.mode, "");
});

test("child deletion uses exact-name confirmation and persists only the request id", async () => {
  const { page, calls, storage } = loadPage(async (requestPath) => {
    if (requestPath === "/children/child/deletion-requests") {
      return { id: "request-1", target_type: "child", state: "queued" };
    }
    throw new Error(`unexpected path: ${requestPath}`);
  });
  page.setData({ mode: "child", targetId: "child", targetName: "小芽", confirmationName: "小芽" });
  page.requestKey = "delete-request-key";
  await page.submitDeletion();

  assert.equal(calls[0].options.data.confirmation_name, "小芽");
  assert.equal(calls[0].options.idempotencyKey, "delete-request-key");
  assert.equal(storage.activeDeletionRequestId, "request-1");
});

test("family cleanup success clears family and child context before onboarding", async () => {
  const { page, app, storage, navigations } = loadPage(async () => ({}));
  storage.activeDeletionRequestId = "request-family";
  await page.finish("family");

  assert.equal(app.globalData.familyId, "");
  assert.equal(app.globalData.selectedChildId, "");
  assert.equal(storage.activeDeletionRequestId, undefined);
  assert.deepEqual(navigations, ["/pages/family-onboarding/index"]);
});
