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

  /* DREV-02 将档案面板动作收敛为「新建学习档案」；空态继续使用「建立学习档案」。 */
  assert.doesNotMatch(uiSource, /保存孩子|孩子昵称|先添加一个孩子/);
  assert.match(uiSource, /学习档案/);
  assert.match(source("pages/settings/index.wxml"), /还没有学习档案/);
  assert.match(source("pages/settings/index.wxml"), /建立学习档案/);
  assert.match(source("pages/settings/index.wxml"), /新建学习档案/);
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

test("today activity empty state does not repeat the schedule action", () => {
  const template = source("pages/today/index.wxml");

  assert.match(template, /<text class="et">今天没有活动安排<\/text>/);
  assert.doesNotMatch(template, /今天没有活动安排<\/text>\s*<view class="ea">/);
  assert.equal((template.match(/bindtap="addSchedule"/g) || []).length, 2);
  assert.match(template, /aria-label="添加日程" bindtap="addSchedule"/);
  assert.match(template, /aria-label="也可以先添加日程" bindtap="addSchedule"/);
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

test("record entry is unified and history is disclosed at the bottom", () => {
  const records = source("pages/records/index.wxml");
  const styles = source("pages/records/index.wxss");
  assert.doesNotMatch(records, /data-view="new"|data-mode="photo"|data-mode="text"/);
  assert.doesNotMatch(records, />拍照记录<|>文字记录</);
  assert.match(records, /id="record-history"/);
  assert.match(records, /aria-expanded="\{\{historyExpanded\}\}"/);
  assert.match(records, /可补充照片里不明显的内容，也可以直接写下今天学了什么。/);
  assert.match(records, /添加照片或文字后继续/);
  assert.match(records, />添加学习照片</);
  assert.match(records, />拍摄或从相册选择</);
  assert.equal((records.match(/bindtap="addPhotos"/g) || []).length, 2);
  assert.doesNotMatch(records, /bindtap="chooseCamera"|bindtap="chooseAlbum"/);
  assert.match(records, /class="pk-cta-bar record-cta"/);
  assert.match(styles, /\.record-cta\s*\{[^}]*bottom:\s*calc\(var\(--pk-tabbar-h\) \+ var\(--pk-s4\) \+ env\(safe-area-inset-bottom\)\)/s);
  assert.match(styles, /\.record-page\.sticky-cta\s*\{[^}]*padding-bottom:\s*calc\(376rpx \+ env\(safe-area-inset-bottom\)\)/s);
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
