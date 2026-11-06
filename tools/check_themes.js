// Theme contracts and resource evidence derive from the production registry.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "../apps/miniprogram");
const registry = require(path.join(root, "presentation/theme/registry"));
const glyphs = require(path.join(root, "presentation/theme/glyphs"));
const config = require(path.join(root, "app.json"));
function files(dir) { return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(dir, e.name); return e.isDirectory() ? files(p) : [p]; }); }
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
function luminance(hex) {
  const rgb = hex.slice(1).match(/../g).map((s) => parseInt(s, 16) / 255)
    .map((v) => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
}
function contrast(a, b) { const x = luminance(a), y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
const themes = registry.listThemes(), checks = [];
assert.equal(new Set(themes.map((t) => t.id)).size, themes.length);
assert.equal(themes.length, 6);
for (const t of themes) {
  const keys = Object.keys(registry.baseTokens);
  assert.deepEqual(Object.keys(t.tokens).sort(), keys.sort());
  for (const [key, value] of Object.entries(t.tokens)) {
    assert.equal(typeof value, "string", t.id + ":" + key);
    for (const match of value.matchAll(/var\(--([\w-]+)\)/g)) assert.ok(match[1] in t.tokens, key + ":" + match[1]);
  }
  for (const resource of Object.values(t.assets)) if (resource) {
    assert.match(resource, /^\/assets\/[\w/.-]+$/);
    assert.ok(fs.existsSync(path.join(root, resource)));
  }
  assert.equal(typeof glyphs[t.fallback], "string");
  const payload = Buffer.byteLength(JSON.stringify({ theme: registry.presentation(t.id), themeArtFailed: false }));
  assert.ok(payload <= 32768, t.id + " payload");
  assert.ok(Buffer.byteLength(JSON.stringify({ version: 1, id: t.id })) <= 256);
  const pairs = [["body", "pk-ink", "pk-surface"], ["secondary", "pk-ink-2", "pk-surface"],
    ["muted text", "pk-text-muted", "pk-surface"], ["primary button", "pk-on-primary", "pk-primary"],
    ["danger", "pk-danger-ink", "pk-danger-bg"], ["attention", "pk-attention-ink", "pk-attention-bg"],
    ["success", "pk-success-ink", "pk-success-bg"]];
  const ratios = pairs.map(([role, a, b]) => ({ role, ratio: Number(contrast(t.tokens[a], t.tokens[b]).toFixed(2)) }));
  ratios.forEach((r) => assert.ok(r.ratio >= 4.5, t.id + ":" + r.role + " " + r.ratio));
  checks.push({ id: t.id, theme_setData_bytes: payload, contrast: ratios });
}
for (const route of config.pages) {
  assert.match(read(route + ".js"), /Page\(withThemePage\(/, route);
  assert.match(read(route + ".wxml"), /class="\{\{theme.classes\}\} theme-page" style="\{\{theme.style\}\}"/, route);
}
const sourceFiles = files(root);
for (const p of sourceFiles.filter((p) => p.endsWith(".js"))) {
  const text = fs.readFileSync(p, "utf8");
  if (/^Component\(/m.test(text) && !p.includes("/theme-icon/")) {
    assert.match(text, /Component\(withThemeComponent\(/, p);
    assert.match(fs.readFileSync(p.replace(/\.js$/, ".wxml"), "utf8"), /\{\{theme.style\}\}/, p);
  }
  if (p.includes("/presentation/theme/")) assert.doesNotMatch(text, /require\(["'][^"']*(?:utils|pages|api|config)/, p);
  assert.doesNotMatch(text, /(?:global|wx)\.(?:Page|Component)\s*=/, p);
}
for (const p of sourceFiles.filter((p) => p.endsWith(".wxss") && !p.endsWith("/tokens.wxss")))
  assert.doesNotMatch(fs.readFileSync(p, "utf8"), /#[a-f\d]{3,8}\b|rgba?\(/i, p);
const assets = files(path.join(root, "assets/themes")).map((p) => ({
  path: path.relative(root, p), bytes: fs.statSync(p).size, sha256: crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex") }));
const assetBytes = assets.reduce((n, a) => n + a.bytes, 0), sourceBytes = sourceFiles.reduce((n, p) => n + fs.statSync(p).size, 0);
const baseTree = execFileSync("git", ["ls-tree", "-rl", "HEAD", "apps/miniprogram"], { cwd: path.resolve(__dirname, ".."), encoding: "utf8" });
const baselineBytes = baseTree.trim().split("\n").reduce((n, line) => n + Number(line.split(/\s+/)[3]), 0);
assert.ok(assetBytes <= 150000); assert.ok(sourceBytes <= 1500000);
assert.ok(sourceBytes - baselineBytes <= 230000); assert.ok(sourceBytes - baselineBytes - assetBytes <= 80000);
const report = { registry: "apps/miniprogram/presentation/theme/registry.js", themes: checks, assets, asset_bytes: assetBytes,
  source_bytes: sourceBytes, baseline_bytes: baselineBytes, net_growth_bytes: sourceBytes - baselineBytes,
  non_asset_net_growth_bytes: sourceBytes - baselineBytes - assetBytes,
  matrix: { routes: config.pages.length * themes.length * 3, shared_states: 8 * themes.length * 3 },
  native_color_exceptions: ["pk-native-danger: platform modal palette", "pk-map-route: platform basemap overlay", "activity color: stable persisted domain metadata"] };
const target = path.resolve(__dirname, "../docs/quality/evidence/themes-20261106/contracts.json");
fs.writeFileSync(target, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ status: "PASS", themes: themes.length, assetBytes, sourceBytes, netGrowth: sourceBytes - baselineBytes }));
