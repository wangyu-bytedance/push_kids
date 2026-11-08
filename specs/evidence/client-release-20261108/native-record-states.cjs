const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const file = path.resolve("tools/theme_native.js");
const original = fs.readFileSync(file, "utf8");
const start = original.indexOf("const geometry = ");
const end = original.indexOf("// Keep style reads separate", start);
const geometry = original.slice(original.indexOf("const headerGeometry = "), original.indexOf("const headingSelectors = "))
  .replace("const headerGeometry", "const geometry")
  .replace("'.record-type-title','.record-type-menu','.record-type-choice'", "'.record-type-title','.record-type-menu','.record-type-choice','.record-page','.pk-notice.err','.record-upload-glyph','.record-upload-art','.prog-line','.pf','.pcell:not(.add)','.pcell .rm','travel-diary'");
const source = (original.slice(0,start) + geometry + original.slice(end))
  .replace('headerBlend ? "header" : item.action || ""','"header"');
if (start < 0 || end < 0 || !geometry) throw Error("Expected selector bridge code not found");
const entry = new Module(file, module);
entry.filename = file;
entry.paths = Module._nodeModulePaths(path.dirname(file));
entry._compile(source, file);
