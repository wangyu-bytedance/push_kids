/* Design candidate only: render current pages and remove the decorative arc in copies. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { createRequire } = require("node:module");
const { createHash } = require("node:crypto");
const { chromium } = require("/Users/bytedance/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const ROOT = path.resolve(__dirname, "../../../../..");
const DREV = path.basename(__dirname);
const SPEC = "specs/active/BUG-030-HERO-BACKGROUND-ARC.md#BUG-SPEC-20261021-HERO-ARC-01";
const VIEWPORTS = [[320, 568], [390, 844], [430, 932]];
const GROUPS = {
  "UI-001": ["today", "today-guide", "records", "reports", "calendar", "settings"],
  "UI-009": ["family-members"],
  "UI-011": ["notifications-ready", "notifications-neutral"]
};
const sha = (file) => createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const relative = (file) => path.relative(ROOT, file);
const arc = /\.pk-hero::after\s*\{[^}]*\}/g;

async function main() {
  for (const ui of Object.keys(GROUPS)) {
    const file = path.join(ROOT, "docs/design/frontend/snapshots", ui, DREV, "APPROVAL.md");
    if (fs.existsSync(file) && fs.readFileSync(file, "utf8").includes("- Status: APPROVED")) {
      throw new Error("Approved snapshots are immutable; create another DREV.");
    }
  }
  const renderer = path.join(ROOT, "tools/preview/render.js");
  const originalRequire = createRequire(renderer);
  const fixtures = { ...originalRequire("./fixtures.js") };
  const notifications = {
    page: "pages/notifications", tabBar: null,
    data: {
      loading: false, error: "", supported: true, channelAvailable: true, channelReason: "",
      items: [], grantCount: 0, granting: false, togglingType: "", lastSentLabel: "",
      deliveries: [], deliveriesError: "", autoEnabled: false, autoSaving: false,
      heroTitle: "提醒已准备好", heroReady: true
    }
  };
  fixtures["notifications-ready"] = notifications;
  fixtures["notifications-neutral"] = {
    ...notifications, data: { ...notifications.data, heroReady: false, heroTitle: "提醒次数待补充" }
  };
  const designRequire = Object.assign(
    (name) => name === "./fixtures.js" ? fixtures : originalRequire(name),
    originalRequire
  );
  vm.runInNewContext(fs.readFileSync(renderer, "utf8"), {
    require: designRequire,
    __dirname: path.dirname(renderer), global,
    process: { argv: [process.execPath, renderer, ...Object.values(GROUPS).flat()] },
    console: { log() {} }
  }, { filename: renderer });
  const browser = await chromium.launch({ channel: "chrome" });
  const audits = [];
  let comparisonImages;
  try {
    for (const [ui, states] of Object.entries(GROUPS)) {
      const output = path.join(ROOT, "docs/design/frontend/snapshots", ui, DREV);
      fs.mkdirSync(output, { recursive: true });
      const sources = [], rows = [];
      for (const state of states) {
        for (const [width, height] of VIEWPORTS) {
          const original = path.join(ROOT, "dist/ui-preview", `${state}-${width}.html`);
          let html = fs.readFileSync(original, "utf8");
          if (!html.match(arc)) throw new Error(`Missing source arc: ${state}`);
          html = html.replace(/src="([^"]+\.png)"/g, (_, reference) => {
            const file = path.resolve(path.dirname(original), reference);
            return `src="data:image/png;base64,${fs.readFileSync(file).toString("base64")}"`;
          });
          const beforeHtml = html;
          html = html.replace(arc, "").replace("右上角一抹嫩芽光，右下角一道年轮弧线", "右上角一抹嫩芽光");
          const source = path.join(__dirname, `${state}-${width}x${height}.html`);
          fs.writeFileSync(source, html);
          sources.push(source);
          const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
          const errors = [], externalRequests = [];
          page.on("pageerror", (error) => errors.push(String(error)));
          await page.route("**/*", (route) => {
            const url = route.request().url();
            if (/^https?:/.test(url)) { externalRequests.push(url); return route.abort(); }
            return route.continue();
          });
          await page.setContent(beforeHtml);
          await page.evaluate(() => document.fonts.ready);
          const measure = () => page.locator(".pk-hero").evaluateAll((nodes) => nodes.map((node) => {
            const r = node.getBoundingClientRect();
            return { x: r.x, y: r.y, width: r.width, height: r.height };
          }));
          const before = await measure();
          const beforeArc = await page.locator(".pk-hero").first().evaluate((node) => getComputedStyle(node, "::after").content);
          let beforeImage;
          if (state === "today" && width === 390) beforeImage = await page.locator(".pk-hero").first().screenshot();
          await page.goto(`file://${source}`);
          await page.evaluate(() => document.fonts.ready);
          const after = await measure();
          const afterArc = await page.locator(".pk-hero").evaluateAll((nodes) => nodes.map((node) => getComputedStyle(node, "::after").content));
          const invalidImages = await page.locator("img").evaluateAll((nodes) => nodes.filter((node) => !node.complete || !node.naturalWidth).length);
          if (!before.length || JSON.stringify(before) !== JSON.stringify(after) || beforeArc !== '""' || afterArc.some((value) => value !== "none") || invalidImages || errors.length || externalRequests.length) {
            throw new Error(JSON.stringify({ state, width, before, after, beforeArc, afterArc, invalidImages, errors, externalRequests }));
          }
          const png = path.join(output, `${state}-${width}x${height}.png`);
          await page.screenshot({ path: png });
          rows.push(`| ${path.basename(png)} | ${state} | ${width}x${height} | 1x | ${sha(png)} | HTML design candidate; not native acceptance |`);
          if (beforeImage) comparisonImages = [beforeImage, await page.locator(".pk-hero").first().screenshot()];
          if (state === "settings") {
            await page.locator(".pk-hero").last().scrollIntoViewIfNeeded();
            const lower = path.join(output, `settings-lower-${width}x${height}.png`);
            await page.screenshot({ path: lower });
            rows.push(`| ${path.basename(lower)} | settings-lower | ${width}x${height} | 1x | ${sha(lower)} | HTML design candidate; not native acceptance |`);
          }
          audits.push({ ui, state, width, height, before, after, beforeArc, afterArc, invalidImages, errors, externalRequests });
          await page.close();
        }
      }
      const sourcePaths = sources.map(relative).join("; ");
      const hashes = sources.map((file) => `${relative(file)}=${sha(file)}`).join("; ");
      fs.writeFileSync(path.join(output, "APPROVAL.md"), `# 去除背景细弧线候选\n\n- Status: AWAITING_APPROVAL\n- UI ID: ${ui}\n- Design Revision: ${DREV}\n- Task Spec path and revision: ${SPEC}\n- Frontend baseline revision: FDB-20260913-04\n- Frontend engineering revision: FEC-20261007-NATIVE-GEOMETRY-02\n- Approved by: pending\n- Approved at: pending\n- Approval evidence: pending specific Spec and DREV confirmation\n- Frontend spec path: ${relative(path.join(__dirname, "FRONTEND-SPEC.md"))}\n- Editable design source path(s): ${sourcePaths}\n- Editable source SHA-256: ${hashes}\n- Superseded by: N/A\n\n## Export manifest\n\n| File | Viewport/state | CSS viewport | Scale/DPR | SHA-256 | Notes |\n|---|---|---|---|---|---|\n${rows.join("\n")}\n`);
    }
    const comparison = path.join(__dirname, "comparison.html");
    fs.writeFileSync(comparison, `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>body{margin:0;padding:24px;background:#F6F3EB;font:16px system-ui;color:#283B30}h1{font-size:20px;margin:0 0 24px}.pair{display:flex;gap:24px}.pair section{width:352px}h2{font-size:16px;font-weight:500;margin:0 0 12px}img{display:block;width:352px;height:auto}</style><h1>背景细弧线清理 · 设计预览</h1><div class="pair">${comparisonImages.map((data, index) => `<section><h2>${index ? "修改后：去掉细弧线" : "当前：右下角有细弧线"}</h2><img src="data:image/png;base64,${data.toString("base64")}"></section>`).join("")}</div></html>`);
    const page = await browser.newPage({ viewport: { width: 776, height: 400 }, deviceScaleFactor: 1 });
    await page.goto(`file://${comparison}`);
    await page.screenshot({ path: path.join(__dirname, "comparison.png"), fullPage: true });
    await page.close();
    fs.writeFileSync(path.join(__dirname, "render-audit.json"), JSON.stringify(audits, null, 2) + "\n");
    console.log(`Design only: ${audits.length} viewport/state pairs, unchanged hero geometry, arc absent; 30 PNG exports. Production unchanged.`);
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
