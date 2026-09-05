const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const miniProgramRoot = path.resolve(__dirname, "../../apps/miniprogram");

function source(relativePath) {
  return fs.readFileSync(path.join(miniProgramRoot, relativePath), "utf8");
}

function userInterfaceSource() {
  const files = [
    "pages/settings/index.js",
    "pages/settings/index.wxml",
    "pages/today/index.wxml",
    "pages/records/index.wxml",
    "pages/reports/index.wxml",
    "pages/calendar/index.wxml",
    "pages/activity/edit.js"
  ];
  return files.map(source).join("\n");
}

test("API base URL is build configuration and cannot be overridden from storage", () => {
  const config = require("../../apps/miniprogram/config");
  const appSource = source("app.js");
  const settingsSource = `${source("pages/settings/index.js")}\n${source("pages/settings/index.wxml")}`;

  assert.equal(config.useCloud, true);
  assert.equal(config.cloudEnv, "prod-d2g14rwoycac6b45d");
  assert.equal(config.cloudService, "flask-ik19");
  assert.equal(config.localApiBaseUrl, "http://127.0.0.1:8011/api/v1");
  assert.doesNotMatch(appSource, /getStorageSync\(["']apiBaseUrl["']\)/);
  assert.doesNotMatch(settingsSource, /apiBaseUrl|saveApiUrl|开发环境服务地址|保存地址/);
});

test("parent-facing actions describe learning profiles rather than adding or saving a child", () => {
  const uiSource = userInterfaceSource();

  assert.doesNotMatch(uiSource, /添加孩子|保存孩子|孩子昵称|先添加一个孩子/);
  assert.match(uiSource, /学习档案/);
  assert.match(source("pages/settings/index.wxml"), /学习档案由后台配置/);
  assert.doesNotMatch(source("pages/settings/index.wxml"), /新建档案|保存资料|保存设置/);
});
