const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const appRoot = path.resolve(__dirname, "../../apps/miniprogram");

function read(relativePath) {
  return fs.readFileSync(path.join(appRoot, relativePath), "utf8");
}

const TAB_PAGES = ["today", "calendar", "records", "reports", "settings"];
const TAB_TITLES = {
  today: "今天，也慢慢来",
  calendar: "这一周，心里有数",
  records: "一笔一画，都算数",
  reports: "一点一滴，看得见",
  settings: "按你们的节奏来"
};

test("primary tabs show the app name in the native bar instead of repeating the tab label", () => {
  const app = JSON.parse(read("app.json"));

  assert.equal(app.window.navigationBarTitleText, "知芽");
  for (const page of TAB_PAGES) {
    const config = JSON.parse(read(`pages/${page}/index.json`));
    /* 页面不再覆盖标题：原生标题栏统一继承「知芽」，Tab 文案只出现在 TabBar 上。 */
    assert.equal(config.navigationBarTitleText, undefined, page);
    assert.equal(config.usingComponents["brand-head"], "/components/brand-head/index", page);
  }

  const tabLabels = app.tabBar.list.map((item) => item.text);
  for (const page of TAB_PAGES) {
    const template = read(`pages/${page}/index.wxml`);
    assert.match(template, /<brand-head/, page);
    assert.match(template, /<view class="pg-head under-brand">/, page);
    assert.match(template, new RegExp(`<text class="pg-title">${TAB_TITLES[page]}</text>`), page);
    for (const label of tabLabels) {
      assert.doesNotMatch(template, new RegExp(`<text class="pg-title">${label}</text>`), `${page}/${label}`);
    }
  }
});

test("brand head uses the generated line icon and the product name, never an emoji or bitmap", () => {
  const template = read("components/brand-head/index.wxml");
  const script = read("components/brand-head/index.js");

  assert.match(template, /class="ico ico-sprout-pri sm"/);
  assert.match(template, /<text class="brand-word">知芽<\/text>/);
  assert.doesNotMatch(template, /<image/);
  assert.match(script, /addGlobalClass: true/);
  assert.match(script, /kicker/);
});

test("primary surfaces do not explain affordances that the control already shows", () => {
  const surfaces = [
    "pages/today/index.wxml",
    "pages/calendar/index.wxml",
    "pages/records/index.wxml",
    "pages/reports/index.wxml",
    "pages/settings/index.wxml",
    "pages/submission/draft.wxml",
    "components/submission-materials/index.wxml"
  ].map(read).join("\n");

  /* 可点、可滑、可多选这类可供性由控件本身表达；提示语只保留后果、边界和权限说明。 */
  const removedHints = [
    "点击切换",
    "点击可查看原图",
    "可多选",
    "可下钻",
    "左右滑动查看",
    "按实际参与情况添加，可设置固定时间",
    "打开可以修改资料或归档",
    "打开或取消这个弹层都不会写入数据",
    "不在目录里，也可以按实际名称添加",
    "切换后所有页面同步",
    "开启后，之后每周的同一时间都会出现这条安排"
  ];
  for (const hint of removedHints) {
    assert.doesNotMatch(surfaces, new RegExp(hint), hint);
  }

  /* 与之相对，改变数据或产生正式记录的后果必须留下来。 */
  assert.match(read("pages/records/index.wxml"), /提交后会先生成待确认的草稿，确认后才进入学习档案。/);
  assert.match(read("pages/submission/draft.wxml"), /确认后会创建正式记录、知识点和复习计划。/);
  assert.match(read("pages/settings/index.wxml"), /只显示在日程，不生成待办/);
  assert.match(read("components/submission-materials/index.wxml"), /照片仅供你核对，不用于展示或分享。/);
});
