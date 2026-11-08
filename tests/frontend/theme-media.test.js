const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const app = require("../../apps/miniprogram/app.json");
const registry = require("../../apps/miniprogram/presentation/theme/registry");

test("upload decoration has its own local media role rather than reusing the page banner", () => {
  for (const theme of registry.listThemes()) {
    const presentation = registry.presentation(theme.id);
    if (theme.id === "original") {
      assert.equal(presentation.assets.upload, "/assets/illustrations/record-camera.png");
    } else {
      assert.equal(presentation.assets.upload, "", theme.id + " uses the semantic camera glyph");
      assert.match(presentation.assets.hero, /^\/assets\/themes\/[a-z]+\.jpg$/);
    }
  }
});

test("themed page headers use one decorative layer and do not inherit card framing", () => {
  const root = path.resolve(__dirname, "../../apps/miniprogram");
  const tabs = new Set(app.tabBar.list.map((tab) => tab.pagePath));
  const artInclude = '<include src="../../presentation/theme/header-art.wxml" />';
  const coveredTabs = [];
  let hostedHeaders = 0;
  for (const route of app.pages) {
    const source = fs.readFileSync(path.join(root, route + ".wxml"), "utf8");
    const headers = [...source.matchAll(/<view class="([^"]*\btheme-header\b[^"]*)"[^>]*>/g)]
      .filter((match) => match[1].split(/\s+/).includes("theme-header"));
    if (!headers.length) continue;
    const isTab = tabs.has(route);
    if (isTab) coveredTabs.push(route);
    hostedHeaders += headers.length;
    for (const [, classes] of headers) {
      assert.ok(!classes.split(/\s+/).includes("pk-hero"), route + " has card framing");
      assert.equal(classes.includes("theme-header--overlay"), isTab, route + " heading layout");
    }
    assert.equal(source.split(artInclude).length - 1, headers.length, route + " shared artwork");
    assert.doesNotMatch(source, /src="\{\{theme\.assets\.hero\}\}"/, route + " duplicated artwork");
  }
  assert.deepEqual(new Set(coveredTabs), tabs);
  assert.equal(hostedHeaders, 15);
  const media = fs.readFileSync(path.join(root, "presentation/theme/header-art.wxml"), "utf8");
  assert.match(media, /wx:if="\{\{theme\.assets\.hero && !themeArtFailed\}\}"/);
  assert.match(media, /mode="widthFix".*binderror="onThemeIllustrationError"/);
  assert.match(media, /aria-hidden="\{\{true\}\}"/);
});
