const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "../../apps/miniprogram");
const source = (name) => fs.readFileSync(path.join(root, name), "utf8");

test("family onboarding is routed from the trusted bootstrap state", () => {
  const app = JSON.parse(source("app.json"));
  const appSource = source("app.js");

  assert.ok(app.pages.includes("pages/family-onboarding/index"));
  assert.ok(app.pages.includes("pages/family-join/index"));
  assert.match(appSource, /request\("\/me"/);
  assert.match(appSource, /result\.state !== "bound"/);
  assert.doesNotMatch(source("utils/api.js"), /X-WX-OPENID|X-WX-APPID/);
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

test("an unavailable active-invite list does not hide the member list", () => {
  const members = source("pages/family-members/index.wxml");
  const logic = source("pages/family-members/index.js");
  assert.match(logic, /let inviteListUnavailable = false/);
  assert.match(logic, /catch \{ inviteListUnavailable = true; \}/);
  assert.match(logic, /members, isManager, requests, invites, inviteListUnavailable/);
  assert.match(members, /有效邀请暂不可查看，不影响成员管理/);
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
