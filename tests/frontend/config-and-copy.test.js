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
  assert.doesNotMatch(source("utils/api.js"), /run\.tcloudbase\.com|sh\.run\.tcloudbase\.com/);
  assert.doesNotMatch(appSource, /getStorageSync\(["']apiBaseUrl["']\)/);
  assert.doesNotMatch(settingsSource, /apiBaseUrl|saveApiUrl|开发环境服务地址|保存地址/);
});

test("parent-facing actions guide an unconfigured family without pretending the app failed", () => {
  const uiSource = userInterfaceSource();

  /* FEAT-005 起「添加孩子」是正式入口文案；这里只继续拦截会误导家长的旧说法。 */
  assert.doesNotMatch(uiSource, /保存孩子|孩子昵称|先添加一个孩子/);
  assert.match(uiSource, /学习档案/);
  assert.match(source("pages/settings/index.wxml"), /还没有学习档案/);
  assert.match(source("pages/settings/index.wxml"), /添加孩子/);
  assert.match(source("pages/today/index.wxml"), /记下今天学到的/);
  assert.match(source("pages/today/index.wxml"), /记录学习/);
  assert.match(source("pages/today/index.wxml"), /添加日程/);
  assert.doesNotMatch(source("pages/settings/index.wxml"), /新建档案|保存资料|保存设置/);
});

test("today review section starts collapsed even when there are no due reviews", () => {
  const script = source("pages/today/index.js");
  const template = source("pages/today/index.wxml");

  assert.match(script, /const DEFAULT_SECTIONS = \{ review: false, learning: false, activity: true \}/);
  assert.match(script, /if \(!counts\[section\] && section !== "review"\) return/);
  assert.match(template, /<view class="sec-body" wx:if="\{\{sections\.review\}\}">/);
  assert.doesNotMatch(template, /sections\.review \|\| !dashboard\.todo_count/);
});

test("mini program JavaScript parses before static copy assertions run", () => {
  const childProcess = require("node:child_process");
  const walk = (directory) => fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(fullPath) : (entry.name.endsWith(".js") ? [fullPath] : []);
  });
  for (const file of walk(miniProgramRoot)) childProcess.execFileSync(process.execPath, ["--check", file]);
});

test("settings separates defaults from explicitly added subjects and activities", () => {
  const settings = `${source("pages/settings/index.js")}\n${source("pages/settings/index.wxml")}`;
  assert.match(settings, /const BASIC_LEARNING = \["数学", "语文", "英语"\]/);
  assert.match(settings, /添加课外活动/);
  assert.match(settings, /自定义名称/);
  assert.doesNotMatch(source("pages/settings/index.wxml"), /辅导班/);
  assert.doesNotMatch(settings, /每日复习计划|budgetOptions|chooseBudget|daily_budget_minutes/);
});

test("key native controls fit their own grid cells without page-level horizontal scrolling", () => {
  const globalStyles = source("app.wxss");
  const calendar = source("pages/calendar/index.wxss");
  const reports = `${source("pages/reports/index.wxml")}\n${source("pages/reports/index.wxss")}`;
  const records = source("pages/records/index.wxml");
  const settings = source("pages/settings/index.wxss");
  assert.match(globalStyles, /\.page \{ width: 100%; max-width: 960rpx; margin: 0 auto; box-sizing: border-box/);
  assert.match(calendar, /repeat\(7,minmax\(0,1fr\)\)/);
  assert.match(settings, /aspect-ratio:1\/1/);
  assert.doesNotMatch(reports, /scroll-x/);
  assert.match(reports, /repeat\(3,minmax\(0,1fr\)\)/);
  assert.match(globalStyles, /\.action-row \{ display: grid; grid-template-columns: minmax\(0, 1fr\); width: 100%/);
  assert.match(records, /class="action-row submit-row"/);
});

test("custom tab bar keeps icon geometry and restores the active tab after direct page entry", () => {
  const app = JSON.parse(source("app.json"));
  const tabMarkup = source("custom-tab-bar/index.wxml");
  assert.equal(app.tabBar.custom, true);
  assert.match(tabMarkup, /<image class="tab-icon"/);
  assert.match(source("custom-tab-bar/index.wxss"), /width:40rpx;height:40rpx/);
  ["today", "calendar", "records", "reports", "settings"].forEach((page, selected) => {
    assert.match(source(`pages/${page}/index.js`), new RegExp(`setData\\(\\{ selected: ${selected} \\}\\)`));
  });
});
