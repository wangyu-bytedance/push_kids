const test = require("node:test");
const assert = require("node:assert/strict");

global.getApp = () => ({ globalData: { apiBaseUrl: "http://localhost", familyId: "family-test" } });
const { normalizedError } = require("../../apps/miniprogram/utils/api");

test("API errors preserve stable backend message", () => {
  assert.equal(normalizedError({ data: { error: { message: "没有找到" } } }), "没有找到");
});

test("validation errors are understandable", () => {
  assert.equal(normalizedError({ data: { detail: [{ msg: "Field required" }] } }), "Field required");
});
