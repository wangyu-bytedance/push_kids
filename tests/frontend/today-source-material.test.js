const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const root = "apps/miniprogram";
const read = (path) => fs.readFileSync(`${root}/${path}`, "utf8");

function todoCard() {
  let definition;
  const ui = {
    subjectClass() { return "s-math"; },
    subjectMark() { return "数"; },
    feedbackLabel(action) { return action; },
    monthDay() { return "9 月 7 日"; }
  };
  vm.runInNewContext(read("components/todo-card/index.js"), {
    Component(value) { definition = value; },
    require() { return ui; }
  });
  const events = [];
  const instance = {
    ...definition.methods,
    data: { ...definition.data },
    setData(update) { Object.assign(this.data, update); },
    triggerEvent(name, detail) { events.push({ name, detail }); }
  };
  return { instance, events };
}

test("todo card projects evidence and emits the exact knowledge source", () => {
  const { instance, events } = todoCard();
  instance.buildView({
    id: "math:review",
    subject_name: "数学",
    review_method: "变式练习",
    estimated_minutes: 3,
    items: [{
      review_id: "review-1",
      knowledge_name: "根据数量关系列加减混合算式",
      source_summary: "根据人物年龄差求妈妈的年龄。",
      source_submission_id: "submission-1",
      source_image_index: 2,
      source_occurred_on: "2026-09-07"
    }]
  });

  const item = instance.data.view.items[0];
  assert.equal(item.sourceSummary, "根据人物年龄差求妈妈的年龄。");
  assert.equal(item.sourceImageIndex, 2);
  assert.equal(item.canOpenSource, true);
  assert.equal(instance.data.view.reason, undefined);
  assert.equal(instance.data.view.hint, undefined);

  instance.openSource({ currentTarget: { dataset: { reviewId: "review-1" } } });
  assert.equal(events[0].name, "source");
  assert.equal(events[0].detail.sourceSubmissionId, "submission-1");
  assert.equal(events[0].detail.sourceImageIndex, 2);
});

test("today source material UI replaces appearance reason and practice prompt", () => {
  const card = read("components/todo-card/index.wxml");
  const cardScript = read("components/todo-card/index.js");
  const cardStyle = read("components/todo-card/index.wxss");
  const today = read("pages/today/index.wxml");
  const todayScript = read("pages/today/index.js");

  assert.match(card, /原题提示：\{\{item\.sourceSummary\}\}/);
  assert.match(card, /查看原始内容/);
  assert.doesNotMatch(card, /出现原因|带练提示|bindtap="practice"/);
  assert.doesNotMatch(cardScript, /practice-materials|triggerEvent\("practice"/);
  assert.match(cardStyle, /\.btn\.sm\.act-done\s*\{[^}]*height:\s*64rpx;[^}]*min-height:\s*64rpx/s);
  assert.match(cardStyle, /\.act-done-hit\s*\{[^}]*min-height:\s*88rpx/s);
  assert.match(today, /bindsource="openSourceSheet"/);
  assert.match(today, /<text class="sheet-title">原始学习内容<\/text>/);
  assert.match(today, /submission-materials[^>]*embedded="\{\{true\}\}"/);
  assert.doesNotMatch(todayScript, /\/practice-materials|title:\s*"带练提示"/);
  assert.match(todayScript, /onHide\(\)\s*\{\s*this\.closeSourceSheet\(\)/s);
  assert.match(todayScript, /showSourceSheet:\s*false,\s*sourceSheet:\s*null/);
});
