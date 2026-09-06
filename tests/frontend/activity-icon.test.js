const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ui = require("../../apps/miniprogram/utils/ui");

const miniProgramRoot = path.resolve(__dirname, "../../apps/miniprogram");
const iconStyles = fs.readFileSync(path.join(miniProgramRoot, "styles/icons.wxss"), "utf8");

test("built-in activities map to their own icon instead of one shared ball", () => {
  const catalog = {
    游泳: "ico-swim-pri",
    乒乓球: "ico-pingpong-pri",
    篮球: "ico-basketball-pri",
    羽毛球: "ico-badminton-pri",
    足球: "ico-soccer-pri",
    网球: "ico-tennis-pri",
    围棋: "ico-chess-pri",
    国际象棋: "ico-chess-pri",
    钢琴: "ico-piano-pri",
    小提琴: "ico-music-pri",
    舞蹈: "ico-dance-pri",
    武术: "ico-martial-pri",
    跆拳道: "ico-martial-pri",
    书法: "ico-brush-pri",
    绘画: "ico-palette-pri",
    编程: "ico-code-pri",
    机器人: "ico-robot-pri"
  };
  const used = new Set();
  Object.keys(catalog).forEach((name) => {
    assert.equal(ui.activityIcon(name, "pri"), catalog[name]);
    used.add(catalog[name]);
  });
  assert.ok(used.size >= 15);
});

test("parent-written activity names still match by keyword and fall back to a default icon", () => {
  assert.equal(ui.activityIcon("少儿篮球班", "pri"), "ico-basketball-pri");
  assert.equal(ui.activityIcon("游泳（周三）", "pri"), "ico-swim-pri");
  assert.equal(ui.activityIcon("Scratch 编程", "pri"), "ico-code-pri");
  assert.equal(ui.activityIcon("乐高机器人", "pri"), "ico-robot-pri");
  assert.equal(ui.activityIcon("画画", "pri"), "ico-palette-pri");
  assert.equal(ui.activityIcon("陶艺", "pri"), "ico-palette-pri");
  assert.equal(ui.activityIcon("空手道", "pri"), "ico-martial-pri");
  assert.equal(ui.activityIcon("陶笛演奏"), "ico-star");
  assert.equal(ui.activityIcon(""), "ico-star");
  assert.equal(ui.activityIcon(null, "pri"), "ico-star-pri");
});

test("every activity icon class exists in the generated stylesheet and no ball icon remains", () => {
  const names = ["swim", "pingpong", "basketball", "badminton", "soccer", "tennis", "chess",
    "piano", "music", "dance", "martial", "brush", "palette", "robot", "code", "star"];
  names.forEach((name) => assert.match(iconStyles, new RegExp(`\\.ico-${name}-pri \\{`)));
  assert.doesNotMatch(iconStyles, /\.ico-ball/);
  const templates = fs.readdirSync(path.join(miniProgramRoot, "pages"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(miniProgramRoot, "pages", entry.name, "index.wxml"))
    .filter((file) => fs.existsSync(file));
  templates.forEach((file) => assert.doesNotMatch(fs.readFileSync(file, "utf8"), /ico-ball/));
});
