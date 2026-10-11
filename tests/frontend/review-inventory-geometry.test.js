const test = require("node:test");
const assert = require("node:assert/strict");
const { audit } = require("../../tools/review_inventory_geometry");

function rect(left, top, width, height) {
  return { left, right: left + width, top, bottom: top + height, width, height };
}

function fixture(view = "subject") {
  const time = view === "time";
  return {
    view, expectedWidth: 430, viewport: { width: 430, height: 932 },
    nodes: [
      [rect(0, 0, 430, 1200)], [rect(18, 85, 394, 50)],
      time ? [rect(22, 88, 189, 44), rect(219, 88, 189, 44)] : [],
      time ? [] : [rect(18, 85, 394, 50)], [], [],
      [rect(350, 400, 44, 44)], [rect(36, 400, 306, 90)],
      [rect(36, 400, 306, 24)], [rect(36, 428, 306, 21)], [],
      time ? [rect(18, 290, 394, 60)] : []
    ]
  };
}

test("native rectangle audit accepts the one-row time and single-control subject/count filters", () => {
  for (const view of ["time", "subject", "count"]) assert.deepEqual(audit(fixture(view), 430), [], view);
});

test("native rectangle audit catches broken selector width, gap and overflow", () => {
  const time = fixture("time");
  time.nodes[2][1] = rect(210, 88, 200, 44);
  assert.match(audit(time, 430).join("; "), /unequal widths/);
  assert.match(audit(time, 430).join("; "), /gap below 8px/);
  const subject = fixture("subject");
  subject.nodes[3][0] = rect(18, 85, 450, 50);
  assert.match(audit(subject, 430).join("; "), /outside row/);
});

test("native rectangle audit catches enlarged ellipsis and title collision", () => {
  const capture = fixture();
  capture.nodes[6][0] = rect(250, 400, 144, 44);
  assert.match(audit(capture, 430).join("; "), /must be 44×44px/);
  assert.match(audit(capture, 430).join("; "), /text clearance below 8px/);
});

test("native rectangle audit checks dropdown targets and anchored menu containment", () => {
  const capture = fixture("count");
  capture.nodes[4] = [rect(18, 140, 394, 260)];
  capture.nodes[5] = [rect(18, 140, 394, 48), rect(18, 188, 394, 48)];
  capture.nodes[10] = [rect(174, 452, 220, 160)];
  assert.deepEqual(audit(capture, 430), []);
  capture.nodes[5][0] = rect(18, 140, 394, 30);
  capture.nodes[10] = [rect(300, 410, 220, 160)];
  const errors = audit(capture, 430).join("; ");
  assert.match(errors, /filter option below 44px/);
  assert.match(errors, /outside viewport/);
  assert.match(errors, /overlaps trigger/);
});

test("native rectangle audit uses the actual trigger for an upward menu", () => {
  const capture = fixture("time");
  capture.nodes[6].push(rect(350, 600, 44, 44));
  capture.nodes[7].push(rect(36, 600, 306, 90));
  capture.nodes[8].push(rect(36, 600, 306, 24));
  capture.nodes[9].push(rect(36, 628, 306, 21));
  capture.nodes[10] = [rect(174, 430, 220, 156)];
  capture.menuTriggerIndex = 1;
  assert.deepEqual(audit(capture, 430), []);
  capture.nodes[10] = [rect(174, 620, 220, 156)];
  assert.match(audit(capture, 430).join("; "), /overlaps trigger/);
});
