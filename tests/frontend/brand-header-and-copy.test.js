const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const appRoot = path.resolve(__dirname, "../../apps/miniprogram");

function read(relativePath) {
  return fs.readFileSync(path.join(appRoot, relativePath), "utf8");
}

function measurePrimaryNavigation(wxMock) {
  let definition;
  vm.runInNewContext(read("components/primary-nav/index.js"), {
    Component(value) { definition = value; },
    console: { warn() {} },
    Math,
    Number,
    wx: wxMock
  });
  const data = { ...definition.data };
  definition.lifetimes.attached.call({ data, setData(value) { Object.assign(data, value); } });
  return data;
}

const TAB_PAGES = ["today", "calendar", "records", "reports", "settings"];
const TAB_TITLES = {
  today: "今天，也慢慢来",
  calendar: "这一周，心里有数",
  records: "一笔一画，都算数",
  reports: "一点一滴，看得见",
  settings: "按你们的节奏来"
};

test("primary tabs use one custom brand navigation and do not repeat the brand in page content", () => {
  const app = JSON.parse(read("app.json"));

  /* 深页仍继承这个原生标题；只有五个一级页逐页切换到 custom。 */
  assert.equal(app.window.navigationBarTitleText, "知芽");
  for (const page of TAB_PAGES) {
    const config = JSON.parse(read(`pages/${page}/index.json`));
    assert.equal(config.navigationBarTitleText, undefined, page);
    assert.equal(config.navigationStyle, "custom", page);
    assert.equal(config.usingComponents["primary-nav"], "/components/primary-nav/index", page);
    assert.equal(config.usingComponents["brand-head"], undefined, page);
  }

  const tabLabels = app.tabBar.list.map((item) => item.text);
  for (const page of TAB_PAGES) {
    const template = read(`pages/${page}/index.wxml`);
    assert.equal((template.match(/<primary-nav><\/primary-nav>/g) || []).length, 1, page);
    assert.doesNotMatch(template, /<brand-head/, page);
    assert.doesNotMatch(template, /under-brand/, page);
    assert.match(template, /<view class="pg-head">/, page);
    assert.match(template, new RegExp(`<text class="pg-title">${TAB_TITLES[page]}</text>`), page);
    for (const label of tabLabels) {
      assert.doesNotMatch(template, new RegExp(`<text class="pg-title">${label}</text>`), `${page}/${label}`);
    }
  }

  assert.equal(fs.existsSync(path.join(appRoot, "components/brand-head/index.wxml")), false);
  assert.equal(fs.existsSync(path.join(appRoot, "components/brand-head/index.js")), false);
});

test("primary navigation uses the generated icon and has safe platform geometry fallbacks", () => {
  const template = read("components/primary-nav/index.wxml");
  const script = read("components/primary-nav/index.js");
  const style = read("components/primary-nav/index.wxss");

  assert.match(template, /class="ico ico-sprout-pri sm primary-nav-mark"/);
  assert.match(template, /<text class="primary-nav-title">知芽<\/text>/);
  assert.match(template, /aria-label="知芽"/);
  assert.doesNotMatch(template, /<image/);
  assert.match(script, /addGlobalClass: true/);
  assert.match(script, /wx\.getWindowInfo/);
  assert.match(script, /wx\.getSystemInfoSync/);
  assert.match(script, /wx\.getMenuButtonBoundingClientRect/);
  assert.match(script, /FALLBACK_NAVIGATION_HEIGHT = 44/);
  assert.match(script, /pageLifetimes/);
  assert.match(style, /position: fixed/);
  assert.match(style, /var\(--pk-canvas\)/);
});

test("primary navigation derives safe geometry and falls back when platform APIs fail", () => {
  const measured = measurePrimaryNavigation({
    getWindowInfo() { return { statusBarHeight: 47, windowWidth: 390 }; },
    getMenuButtonBoundingClientRect() { return { top: 54, left: 296, height: 32 }; }
  });
  assert.deepEqual(
    { statusBarHeight: measured.statusBarHeight, navigationHeight: measured.navigationHeight, totalHeight: measured.totalHeight, sideInset: measured.sideInset },
    { statusBarHeight: 47, navigationHeight: 46, totalHeight: 93, sideInset: 102 }
  );

  const narrow = measurePrimaryNavigation({
    getWindowInfo() { return { statusBarHeight: 20, windowWidth: 320 }; },
    getMenuButtonBoundingClientRect() { return { top: 24, left: 223, height: 32 }; }
  });
  assert.equal(narrow.sideInset, 100);

  const fallback = measurePrimaryNavigation({
    getWindowInfo() { throw new Error("unavailable"); },
    getMenuButtonBoundingClientRect() { throw new Error("unavailable"); }
  });
  assert.deepEqual(
    { statusBarHeight: fallback.statusBarHeight, navigationHeight: fallback.navigationHeight, totalHeight: fallback.totalHeight, sideInset: fallback.sideInset },
    { statusBarHeight: 20, navigationHeight: 44, totalHeight: 64, sideInset: 88 }
  );
});

test("deep pages keep native navigation and primary-page context survives brand-row removal", () => {
  const app = JSON.parse(read("app.json"));
  const primaryPaths = new Set(TAB_PAGES.map((page) => `pages/${page}/index`));

  for (const pagePath of app.pages) {
    if (primaryPaths.has(pagePath)) continue;
    const config = JSON.parse(read(`${pagePath}.json`));
    assert.notEqual(config.navigationStyle, "custom", pagePath);
  }

  assert.match(read("pages/today/index.wxml"), /<text class="pg-context">\{\{dayLabel\}\}<\/text>/);
  assert.match(read("pages/calendar/index.wxml"), /<text class="pg-context">\{\{weekKicker\}\}<\/text>/);
  assert.match(read("pages/reports/index.wxml"), /<text class="pg-context">只统计已确认的学习<\/text>/);
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
