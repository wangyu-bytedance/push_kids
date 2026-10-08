const test = require("node:test");
const assert = require("node:assert/strict");
const { audit } = require("../../tools/review_inventory_geometry");

function rect(left, top, width, height, paddingRight = "0px") {
  return { left, right: left + width, top, bottom: top + height, width, height, paddingRight };
}

function fixture(view = "count") {
  const columns = view === "time" ? 2 : 3;
  const count = view === "time" ? 2 : view === "subject" ? 4 : 6;
  const cellWidth = columns === 2 ? 184 : 120;
  const choices = Array.from({ length: count }, (_, index) =>
    rect(20 + (index % columns) * (cellWidth + 8), 160 + Math.floor(index / columns) * 52, cellWidth, 44));
  return {
    view, expectedWidth: 430, viewport: { width: 430, height: 932 },
    nodes: [
      [rect(0, 0, 430, 1200)], [rect(12, 160, 406, view === "time" ? 52 : 104)], choices,
      [rect(350, 400, 44, 44)], [rect(38, 400, 356, 24, "54px")],
      [rect(38, 428, 356, 21, "54px")], []
    ]
  };
}

test("native rectangle audit accepts two/three columns and a partial row", () => {
  for (const view of ["time", "subject", "count"]) {
    assert.deepEqual(audit(fixture(view), 430), [], view);
  }
});

test("native rectangle audit catches overlapping chips and a stretched ellipsis", () => {
  const capture = fixture();
  capture.nodes[2][1] = rect(135, 160, 120, 44);
  capture.nodes[3][0] = rect(250, 400, 144, 44);
  assert.match(audit(capture, 430).join("; "), /horizontal gap below 8px/);
  assert.match(audit(capture, 430).join("; "), /must be 44×44px/);
});

test("native rectangle audit catches partial-row drift and text under the action", () => {
  const capture = fixture("subject");
  capture.nodes[2][3] = rect(34, 212, 120, 44);
  capture.nodes[4][0].paddingRight = "0px";
  assert.match(audit(capture, 430).join("; "), /column misaligned/);
  assert.match(audit(capture, 430).join("; "), /title clearance below 8px/);
});

test("native rectangle audit checks the anchored menu against viewport and trigger", () => {
  const capture = fixture("time");
  capture.nodes[6] = [rect(160, 452, 238, 180)];
  assert.deepEqual(audit(capture, 430), []);
  capture.nodes[6] = [rect(300, 410, 238, 180)];
  assert.match(audit(capture, 430).join("; "), /outside viewport/);
  assert.match(audit(capture, 430).join("; "), /overlaps trigger/);
  capture.nodes[6] = [rect(160, 800, 238, 180)];
  assert.match(audit(capture, 430).join("; "), /outside viewport/);
});
