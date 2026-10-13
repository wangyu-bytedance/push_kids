const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { audit } = require("../../tools/report_panel_geometry");

function captured(state, width = 320) {
  return JSON.parse(fs.readFileSync(path.join(__dirname, "../../docs/quality/evidence/report-panels-20261013", `${state}-${width}.json`)));
}

test("report panel audit accepts all captured native states and rejects absent rendered sections", () => {
  for (const width of [320, 390, 430]) {
    for (const state of ["collapsed", "history", "plan", "both", "subject-filter", "count-filter", "menu", "readonly", "error", "empty", "pending", "plan-empty"]) {
      assert.deepEqual(audit(captured(state, width), width), []);
    }
  }
  const missing = captured("history");
  missing.nodes = missing.nodes.map(() => []);
  assert.ok(audit(missing, 320).includes("required report nodes missing"));
});

test("report panel audit rejects clipped footer, enlarged adjustment, and overlapping copy", () => {
  const footer = captured("both");
  footer.nodes[3][0].height = 30;
  assert.ok(audit(footer, 320).includes("target below 44px"));
  const action = captured("plan");
  action.inventory[6][0].width = 60;
  assert.ok(audit(action, 320).some(error => error.includes("must be 44×44px")));
  const title = captured("history");
  title.nodes[8][0].right = title.nodes[7][0].left + 1;
  assert.ok(audit(title, 320).includes("title/action overlap"));
});

test("report panel audit rejects missing embedded content and off-screen menu", () => {
  const plan = captured("plan");
  plan.inventory = null;
  assert.ok(audit(plan, 320).includes("plan mounting mismatch"));
  const menu = captured("menu");
  menu.inventory[10][0].bottom = menu.viewport.height + 10;
  assert.ok(audit(menu, 320).some(error => error.includes("outside viewport")));
});
