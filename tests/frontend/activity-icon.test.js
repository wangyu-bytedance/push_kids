const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ui = require("../../apps/miniprogram/utils/ui");

const miniProgramRoot = path.resolve(__dirname, "../../apps/miniprogram");
const glyphs = require("../../apps/miniprogram/presentation/theme/glyphs");
const themes = require("../../apps/miniprogram/presentation/theme/registry").listThemes();

test("built-in activities map to their own icon instead of one shared ball", () => {
  const catalog = {
    游泳: "swim",
    乒乓球: "pingpong",
    篮球: "basketball",
    羽毛球: "badminton",
    足球: "soccer",
    网球: "tennis",
    围棋: "chess",
    国际象棋: "chess",
    钢琴: "piano",
    小提琴: "music",
    舞蹈: "dance",
    武术: "martial",
    跆拳道: "martial",
    书法: "brush",
    绘画: "palette",
    编程: "code",
    机器人: "robot"
  };
  const used = new Set();
  Object.keys(catalog).forEach((name) => {
    assert.equal(ui.activityIcon(name, "pri"), catalog[name]);
    used.add(catalog[name]);
  });
  assert.ok(used.size >= 15);
});

test("parent-written activity names still match by keyword and fall back to a default icon", () => {
  assert.equal(ui.activityIcon("少儿篮球班", "pri"), "basketball");
  assert.equal(ui.activityIcon("游泳（周三）", "pri"), "swim");
  assert.equal(ui.activityIcon("Scratch 编程", "pri"), "code");
  assert.equal(ui.activityIcon("乐高机器人", "pri"), "robot");
  assert.equal(ui.activityIcon("画画", "pri"), "palette");
  assert.equal(ui.activityIcon("陶艺", "pri"), "palette");
  assert.equal(ui.activityIcon("空手道", "pri"), "martial");
  assert.equal(ui.activityIcon("陶笛演奏"), "default");
  assert.equal(ui.activityIcon(""), "default");
  assert.equal(ui.activityIcon(null, "pri"), "default");
});

test("every activity icon class exists in the generated stylesheet and no ball icon remains", () => {
  const names = ["swim", "pingpong", "basketball", "badminton", "soccer", "tennis", "chess",
    "piano", "music", "dance", "martial", "brush", "palette", "robot", "code", "default"];
  names.filter((name) => name !== "default").forEach((name) => assert.equal(typeof glyphs[name], "string"));
  themes.forEach((theme) => assert.equal(typeof glyphs[theme.fallback], "string"));
  assert.equal(glyphs.ball, undefined);
  const templates = fs.readdirSync(path.join(miniProgramRoot, "pages"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(miniProgramRoot, "pages", entry.name, "index.wxml"))
    .filter((file) => fs.existsSync(file));
  templates.forEach((file) => assert.doesNotMatch(fs.readFileSync(file, "utf8"), /ico-ball/));
});
