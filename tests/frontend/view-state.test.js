const test = require("node:test");
const assert = require("node:assert/strict");
const { resolveViewState, stateLabel } = require("../../apps/miniprogram/utils/view-state");

test("view state priority is honest", () => {
  assert.equal(resolveViewState({ loading: true, error: "bad", hasData: true }), "loading");
  assert.equal(resolveViewState({ loading: false, error: "bad", hasData: true }), "error");
  assert.equal(resolveViewState({ loading: false, error: "", hasData: false }), "empty");
  assert.equal(resolveViewState({ loading: false, error: "", hasData: true }), "content");
});

test("analysis states use named progress rather than fake percentages", () => {
  assert.equal(stateLabel("queued"), "等待分析");
  assert.equal(stateLabel("analyzing"), "正在分析");
  assert.equal(stateLabel("pending_confirmation"), "待家长确认");
});
