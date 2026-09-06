const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../../apps/miniprogram");
const source = (name) => fs.readFileSync(path.join(root, name), "utf8");

function loadApp() {
  let definition;
  const filename = path.join(root, "app.js");
  vm.runInNewContext(source("app.js"), {
    require(name) {
      if (name === "./config") return {
        useCloud: false, cloudEnv: "", cloudService: "", apiBasePath: "/api/v1",
        localFamilyId: "", localActorId: "actor", localApiBaseUrl: "http://localhost"
      };
      throw new Error(`unexpected require: ${name}`);
    },
    App(value) { definition = value; },
    getCurrentPages() { return []; },
    wx: { getStorageSync() { return ""; }, setStorageSync() {} }
  }, { filename });
  return definition;
}

function loadOnboarding(request, refreshBootstrap = async () => ({ state: "unbound" })) {
  let definition;
  const calls = [];
  const relaunches = [];
  const app = {
    globalData: {},
    refreshBootstrap,
    selectChild() {}
  };
  const filename = path.join(root, "pages/family-onboarding/index.js");
  vm.runInNewContext(source("pages/family-onboarding/index.js"), {
    require(_name) {
      return {
        request: async (requestPath, options = {}) => {
          calls.push({ path: requestPath, options });
          return request(requestPath, options);
        },
        newIdempotencyKey: () => "family-grade-key"
      };
    },
    Page(value) { definition = value; },
    getApp: () => app,
    wx: {
      showToast() {}, reLaunch({ url }) { relaunches.push(url); }, navigateTo() {},
      setClipboardData() {}, showModal() {}, stopPullDownRefresh() {}
    }
  }, { filename });
  const page = {
    ...definition,
    data: JSON.parse(JSON.stringify(definition.data)),
    setData(update, callback) {
      Object.assign(this.data, update);
      if (callback) callback();
    }
  };
  return { page, calls, relaunches };
}

test("ordinary launch enters the family bootstrap gate before business tabs", async () => {
  const app = JSON.parse(source("app.json"));
  const application = loadApp();
  let bootstrapCalls = 0;
  application.refreshBootstrap = async () => { bootstrapCalls += 1; };

  assert.equal(app.pages[0], "pages/family-onboarding/index");
  assert.ok(app.pages.includes("pages/family-join/index"));
  application.onLaunch({ path: "pages/family-onboarding/index" });
  await Promise.resolve();
  assert.equal(bootstrapCalls, 0);

  application.onLaunch({ path: "pages/family-join/index" });
  await Promise.resolve();
  assert.equal(bootstrapCalls, 0);

  application.onLaunch({ path: "pages/today/index" });
  await Promise.resolve();
  assert.equal(bootstrapCalls, 1);
  assert.doesNotMatch(source("utils/api.js"), /X-WX-OPENID|X-WX-APPID/);
});

test("family bootstrap states route without treating empty children or errors as no family", async () => {
  const unbound = loadOnboarding(async () => ({}), async () => ({ state: "unbound" }));
  await unbound.page.load();
  assert.equal(unbound.page.data.state, "unbound");
  assert.deepEqual(unbound.relaunches, []);

  const request = { id: "request-1", request_code: "123456" };
  const pending = loadOnboarding(async () => ({}), async () => ({ state: "pending", request }));
  await pending.page.load();
  assert.equal(pending.page.data.state, "pending");
  assert.equal(pending.page.data.request.id, "request-1");
  assert.deepEqual(pending.relaunches, []);

  const boundWithoutChildren = loadOnboarding(async () => ({}), async () => ({ state: "bound", children: [] }));
  await boundWithoutChildren.page.load();
  assert.deepEqual(boundWithoutChildren.relaunches, ["/pages/today/index"]);

  const failed = loadOnboarding(async () => ({}), async () => { throw new Error("暂时无法确认家庭状态"); });
  await failed.page.load();
  assert.equal(failed.page.data.state, "error");
  assert.equal(failed.page.data.error, "暂时无法确认家庭状态");
  assert.deepEqual(failed.relaunches, []);
});

test("family onboarding creates the family without attempting to create a child", async () => {
  const { page, calls } = loadOnboarding(async (requestPath) => {
    if (requestPath === "/families") return { family: { id: "family" }, children: [] };
    throw new Error(`unexpected path: ${requestPath}`);
  });
  page.setData({ familyName: "小芽的家", relationship: "妈妈", canSubmit: true });
  await page.submitFamily();

  const created = calls.find((call) => call.path === "/families");
  assert.equal(created.options.data.display_name, "小芽的家");
  assert.equal(created.options.data.relationship_label, "妈妈");
  assert.equal(Object.hasOwn(created.options.data, "child"), false);
  assert.doesNotMatch(source("pages/family-onboarding/index.wxml"), /孩子称呼|年级/);
});

test("join preview explains approval and does not expose family records", () => {
  const join = source("pages/family-join/index.wxml");
  const onboarding = source("pages/family-onboarding/index.wxml");

  assert.match(join, /加入前不会展示学习记录、照片或成员名单/);
  assert.match(join, /申请加入/);
  assert.match(onboarding, /AI 只提供可编辑建议/);
  assert.match(onboarding, /申请已发送/);
  const joinLogic = source("pages/family-join/index.js");
  assert.match(joinLogic, /request\("\/family-invites\/preview"/);
  assert.match(joinLogic, /data: \{ token: this\.token \}/);
  assert.doesNotMatch(joinLogic, /family-invites\/\$\{this\.token\}/);
});

test("manager pages expose explicit role choices and last-manager errors stay server-owned", () => {
  const requests = source("pages/family-requests/index.wxml");
  const members = source("pages/family-members/index.wxml");

  assert.match(requests, /仅查看/);
  assert.match(requests, /可记录/);
  assert.match(requests, /管理员/);
  assert.match(members, /邀请家人/);
  assert.match(source("pages/family-members/index.js"), /families\/current\/members/);
});

test("member management uses a detail sheet and never offers self removal", () => {
  const members = source("pages/family-members/index.wxml");
  const logic = source("pages/family-members/index.js");
  assert.match(members, /成员详情/);
  assert.match(members, /isManager && !selectedMember\.is_self/);
  assert.match(logic, /if \(!member \|\| member\.is_self\) return/);
  assert.doesNotMatch(members, /class="member-actions"/);
  assert.match(members, /class="member-list"/);
  assert.match(members, /<view class="member-row"/);
});

test("invite and approval UI uses request codes without displaying raw tokens", () => {
  const members = source("pages/family-members/index.wxml");
  const requests = source("pages/family-requests/index.wxml");
  const requestLogic = source("pages/family-requests/index.js");
  assert.doesNotMatch(members, /shareToken|邀请口令/);
  assert.match(requests, /申请码 \{\{item\.request_code\}\}/);
  assert.match(requestLogic, /确认同意申请/);
  assert.match(requestLogic, /if \(this\.data\.actingId\) return/);
});

test("an unavailable active-invite list stays non-blocking and does not add a false page warning", () => {
  const members = source("pages/family-members/index.wxml");
  const logic = source("pages/family-members/index.js");
  assert.match(logic, /let inviteListUnavailable = false/);
  assert.match(logic, /catch \{ inviteListUnavailable = true; \}/);
  assert.match(logic, /members, isManager, requests, invites, inviteListUnavailable/);
  assert.doesNotMatch(members, /有效邀请暂不可查看，不影响成员管理/);
  assert.match(members, /wx:if="\{\{members\.length\}\}"/);
  assert.doesNotMatch(members, /class="inline-status"/);
});

test("family actions use full-width semantic containers instead of shrinking native buttons", () => {
  const members = source("pages/family-members/index.wxml");
  const styles = source("pages/family-members/index.wxss");
  assert.match(members, /<view class="button invite-button/);
  assert.match(members, /<view class="request-entry"/);
  assert.match(styles, /grid-template-columns:minmax\(0,1fr\)/);
  assert.match(styles, /\.member-list\{width:100%/);
});

test("family mutations keep one idempotency key across a failed retry", () => {
  const onboarding = source("pages/family-onboarding/index.js");
  const join = source("pages/family-join/index.js");
  const members = source("pages/family-members/index.js");
  const requests = source("pages/family-requests/index.js");

  assert.match(onboarding, /idempotencyKey: this\.familyRequestKey/);
  assert.match(join, /idempotencyKey: this\.joinRequestKey/);
  assert.match(members, /idempotencyKey: this\.inviteRequestKey/);
  assert.match(requests, /this\.actionRetryKeys\[operation\] = idempotencyKey/);
  assert.match(requests, /idempotencyKey, data: \{ role \}/);
  assert.match(requests, /idempotencyKey, data: \{\}/);
});
