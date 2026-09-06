/* WXML/WXSS 近似渲染器：把小程序页面渲染成静态 HTML，供三档视口截图走查。
   仅用于设计验收，不参与构建；表达式用真 JS 求值，组件视图直接调用组件自身的 buildView，
   因此除了排版引擎（WebView vs 小程序渲染层）之外，与真机结构一致。

   用法：node tools/preview/render.js [页面名...]     输出 dist/ui-preview/<page>-<width>.html
*/

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const APP = path.join(ROOT, "apps", "miniprogram");
const OUT = path.join(ROOT, "dist", "ui-preview");
const WIDTHS = [320, 390, 430];

/* 标签保持小程序原名（HTML 自定义元素），这样 WXSS 里的 `view.on`、`.seg > view`
   这类标签选择器在预览里也能命中，避免出现只在预览中失效的样式。 */
const TAG_MAP = {
  block: "fragment", image: "img", textarea: "textarea", input: "input", button: "button",
  view: "view", text: "text", "scroll-view": "scroll-view", swiper: "swiper",
  "swiper-item": "swiper-item", picker: "picker", "cover-view": "cover-view",
  navigator: "navigator", label: "label", slider: "slider", switch: "switch",
  radio: "radio", checkbox: "checkbox", form: "form", icon: "icon", progress: "progress"
};
const VOID_TAGS = new Set(["img", "input"]);

/* ---------------- WXML parser ---------------- */
const TOKEN = /<!--[\s\S]*?-->|<\/([A-Za-z][\w-]*)\s*>|<([A-Za-z][\w-]*)((?:"[^"]*"|'[^']*'|[^>])*?)(\/?)>/g;

function parseAttrs(raw) {
  const attrs = {};
  const re = /([A-Za-z_:@][\w:.\-]*)\s*=\s*"([^"]*)"|([A-Za-z_:@][\w:.\-]*)/g;
  let m;
  while ((m = re.exec(raw))) {
    if (m[1]) attrs[m[1]] = m[2];
    else if (m[3]) attrs[m[3]] = "";
  }
  return attrs;
}

function parse(source) {
  const root = { tag: "#root", attrs: {}, children: [] };
  const stack = [root];
  let cursor = 0;
  let m;
  TOKEN.lastIndex = 0;
  while ((m = TOKEN.exec(source))) {
    const text = source.slice(cursor, m.index);
    if (text.trim()) stack[stack.length - 1].children.push({ tag: "#text", value: text });
    cursor = m.index + m[0].length;
    if (m[0].startsWith("<!--")) continue;
    if (m[1]) { if (stack.length > 1) stack.pop(); continue; }
    const node = { tag: m[2], attrs: parseAttrs(m[3] || ""), children: [] };
    stack[stack.length - 1].children.push(node);
    if (!m[4]) stack.push(node);
  }
  const tail = source.slice(cursor);
  if (tail.trim()) root.children.push({ tag: "#text", value: tail });
  return root;
}

/* ---------------- expression evaluation ---------------- */
const cache = new Map();
function evaluate(expression, scope) {
  let fn = cache.get(expression);
  if (!fn) {
    fn = new Function("scope", `with (scope) { return (${expression}); }`);
    cache.set(expression, fn);
  }
  try { return fn(scope); } catch { return undefined; }
}

function interpolate(raw, scope) {
  if (!raw.includes("{{")) return raw;
  return raw.replace(/\{\{([\s\S]+?)\}\}/g, (_, expression) => {
    const value = evaluate(expression, scope);
    if (value === undefined || value === null || value === false) return "";
    if (value === true) return "true";
    return String(value);
  });
}

function truthy(raw, scope) {
  const match = /^\s*\{\{([\s\S]+)\}\}\s*$/.exec(raw);
  return !!evaluate(match ? match[1] : JSON.stringify(raw), scope);
}

function listOf(raw, scope) {
  const match = /^\s*\{\{([\s\S]+)\}\}\s*$/.exec(raw);
  const value = match ? evaluate(match[1], scope) : undefined;
  return Array.isArray(value) ? value : [];
}

/* ---------------- templates (<import> / <template>) ---------------- */
const templates = {};

function collectTemplates(tree, dir) {
  tree.children.forEach((node) => {
    if (node.tag === "#text") return;
    if ((node.tag === "import" || node.tag === "include") && node.attrs.src) {
      const file = path.resolve(dir, node.attrs.src);
      if (fs.existsSync(file)) {
        const sub = parse(fs.readFileSync(file, "utf8"));
        collectTemplates(sub, path.dirname(file));
      }
      return;
    }
    if (node.tag === "template" && node.attrs.name) templates[node.attrs.name] = node;
    collectTemplates(node, dir);
  });
}

/* ---------------- components ---------------- */
function loadComponent(name) {
  const dir = path.join(APP, "components", name);
  const jsPath = path.join(dir, "index.js");
  if (!fs.existsSync(jsPath)) return null;
  let options = null;
  global.Component = (value) => { options = value; };
  global.wx = global.wx || { getStorageSync: () => ({}), setStorageSync: () => {} };
  delete require.cache[require.resolve(jsPath)];
  require(jsPath);
  return { options, tree: parse(fs.readFileSync(path.join(dir, "index.wxml"), "utf8")) };
}

function componentScope(component, props) {
  const state = JSON.parse(JSON.stringify(component.options.data || {}));
  const host = {
    data: state,
    setData(patch) {
      Object.entries(patch).forEach(([key, value]) => {
        if (!key.includes(".")) { state[key] = value; return; }
        const parts = key.split(".");
        let node = state;
        parts.slice(0, -1).forEach((part) => { node = node[part] = node[part] || {}; });
        node[parts[parts.length - 1]] = value;
      });
    },
    triggerEvent() {}
  };
  Object.entries(props).forEach(([key, value]) => { state[key] = value; });
  const methods = component.options.methods || {};
  if (methods.buildView) methods.buildView.call(host, props.group);
  return state;
}

/* ---------------- render ---------------- */
function renderChildren(children, scope, sink) {
  let branch = null;
  children.forEach((node) => {
    if (node.tag === "#text") { sink.push(interpolate(node.value, scope)); return; }
    const attrs = node.attrs;
    if ("wx:if" in attrs) { branch = truthy(attrs["wx:if"], scope); if (!branch) return; }
    else if ("wx:elif" in attrs) { if (branch) return; branch = truthy(attrs["wx:elif"], scope); if (!branch) return; }
    else if ("wx:else" in attrs) { if (branch) return; branch = true; }
    else branch = null;
    if ("wx:for" in attrs) {
      const itemKey = attrs["wx:for-item"] || "item";
      const indexKey = attrs["wx:for-index"] || "index";
      listOf(attrs["wx:for"], scope).forEach((entry, index) => {
        renderNode(node, { ...scope, [itemKey]: entry, [indexKey]: index }, sink);
      });
      return;
    }
    renderNode(node, scope, sink);
  });
}

function renderNode(node, scope, sink) {
  if (node.tag === "import" || node.tag === "wxs") return;
  if (node.tag === "template") {
    if (node.attrs.name) return;
    const target = templates[interpolate(node.attrs.is || "", scope)];
    if (!target) return;
    const raw = node.attrs.data || "";
    const match = /^\s*\{\{([\s\S]+)\}\}\s*$/.exec(raw);
    const data = match ? evaluate(`({${match[1]}})`, scope) : {};
    renderChildren(target.children, { ...(data || {}) }, sink);
    return;
  }
  const component = COMPONENTS[node.tag];
  if (component) {
    const props = {};
    Object.entries(node.attrs).forEach(([key, raw]) => {
      if (key.startsWith("wx:") || key.startsWith("bind") || key === "id") return;
      const match = /^\s*\{\{([\s\S]+)\}\}\s*$/.exec(raw);
      props[key.replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = match ? evaluate(match[1], scope) : raw;
    });
    const childScope = componentScope(component, props);
    const className = interpolate(node.attrs.class || "", scope);
    sink.push(`<div class="${className}">`);
    renderChildren(component.tree.children, childScope, sink);
    sink.push("</div>");
    return;
  }
  const tag = TAG_MAP[node.tag] || "div";
  if (tag === "fragment") { renderChildren(node.children, scope, sink); return; }
  const parts = [];
  Object.entries(node.attrs).forEach(([key, raw]) => {
    if (key.startsWith("wx:") || key.startsWith("bind") || key.startsWith("catch")) return;
    let value = interpolate(raw, scope);
    if (key === "src" && value.startsWith("/")) value = `../../apps/miniprogram${value}`;
    if (key === "class" || key === "style" || key === "src" || key === "id") parts.push(`${key}="${value}"`);
    else if (key === "placeholder") parts.push(`placeholder="${value}"`);
    else if (key === "value" && (tag === "input" || tag === "textarea")) parts.push(`value="${value}"`);
    else if (key === "mode") parts.push('style="object-fit:contain"');
    else parts.push(`data-${key.replace(/[^\w-]/g, "-")}="${value}"`);
  });
  const valueAttr = tag === "textarea" ? interpolate(node.attrs.value || "", scope) : "";
  sink.push(`<${tag} ${parts.filter((part) => !(tag === "textarea" && part.startsWith("value="))).join(" ")}>`);
  if (!VOID_TAGS.has(tag)) {
    if (valueAttr) sink.push(valueAttr);
    renderChildren(node.children, scope, sink);
    sink.push(`</${tag}>`);
  }
}

/* ---------------- styles ---------------- */
function readStyle(file, seen = new Set()) {
  if (!fs.existsSync(file) || seen.has(file)) return "";
  seen.add(file);
  return fs.readFileSync(file, "utf8").replace(/@import\s+"([^"]+)"\s*;/g, (_, ref) =>
    readStyle(path.resolve(path.dirname(file), ref), seen));
}

function styleSheet(files, width) {
  const scale = width / 750;
  return files
    .map((file) => readStyle(file))
    .join("\n")
    .replace(/@import[^;]+;/g, "")
    .replace(/([\d.]+)rpx/g, (_, value) => `${(Number(value) * scale).toFixed(3)}px`)
    .replace(/env\(safe-area-inset-bottom\)/g, "0px")
    .replace(/(^|[};\s])page\s*\{/g, "$1.page-root {");
}

/* ---------------- pages ---------------- */
const FIXTURES = require("./fixtures.js");
const COMPONENTS = { "todo-card": loadComponent("todo-card") };

function renderPage(name, width) {
  const fixture = FIXTURES[name];
  const pageDir = path.join(APP, fixture.page);
  const entry = fixture.name || "index";
  const tree = parse(fs.readFileSync(path.join(pageDir, `${entry}.wxml`), "utf8"));
  collectTemplates(tree, pageDir);
  const sink = [];
  renderChildren(tree.children, { ...fixture.data }, sink);
  const tabSink = [];
  if (fixture.tabBar) {
    const tabTree = parse(fs.readFileSync(path.join(APP, "custom-tab-bar", "index.wxml"), "utf8"));
    renderChildren(tabTree.children, fixture.tabBar, tabSink);
  }
  const extra = (fixture.styles || []).map((file) => path.join(APP, file));
  const css = styleSheet([
    path.join(APP, "styles", "tokens.wxss"),
    path.join(APP, "styles", "atoms.wxss"),
    path.join(APP, "styles", "icons.wxss"),
    path.join(APP, "app.wxss"),
    path.join(APP, "custom-tab-bar", "index.wxss"),
    path.join(APP, "components", "todo-card", "index.wxss"),
    ...extra,
    path.join(pageDir, `${entry}.wxss`)
  ], width);
  const scale = width / 750;
  const rpx = (html) => html.replace(/([\d.]+)rpx/g, (_, value) => `${(Number(value) * scale).toFixed(3)}px`);
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>${name} @${width}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }
view, scroll-view, swiper, swiper-item, picker, cover-view, navigator, form, slider, progress { display: block; }
text, icon { display: inline; }
swiper { overflow: hidden; }
slider { height: 44px; background: linear-gradient(var(--pk-line-strong), var(--pk-line-strong)) center/100% 4px no-repeat; }
body { width: ${width}px; }
.page-root { position: relative; width: ${width}px; min-height: 100vh; display: block; }
button, input, textarea { font: inherit; color: inherit; border: 0; background: none; outline: none; resize: none; }
${css}
</style></head><body><div class="page-root">
${rpx(sink.join(""))}
${rpx(tabSink.join(""))}
</div></body></html>`;
}

function main() {
  const names = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(FIXTURES);
  fs.mkdirSync(OUT, { recursive: true });
  names.forEach((name) => {
    WIDTHS.forEach((width) => {
      const file = path.join(OUT, `${name}-${width}.html`);
      fs.writeFileSync(file, renderPage(name, width));
      console.log(`PREVIEW ${path.relative(ROOT, file)}`);
    });
  });
}

main();
