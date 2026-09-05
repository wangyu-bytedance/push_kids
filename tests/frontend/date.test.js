const test = require("node:test");
const assert = require("node:assert/strict");
const { localParts, toIso, monthKey, friendlyTime } = require("../../apps/miniprogram/utils/date");

test("local date parts are padded", () => {
  assert.deepEqual(localParts(new Date(2026, 0, 2, 3, 4)), { date: "2026-01-02", time: "03:04" });
});

test("date and time convert to a valid ISO instant", () => {
  assert.match(toIso("2026-08-30", "09:15"), /^2026-08-30T/);
});

test("month and friendly labels are stable", () => {
  assert.equal(monthKey(new Date(2026, 7, 30)), "2026-08");
  assert.match(friendlyTime("2026-08-30T01:15:00.000Z"), /8月30日/);
});
