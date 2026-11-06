const registry = require("../../presentation/theme/registry");
const glyphs = require("../../presentation/theme/glyphs");
const { themeState } = require("../../presentation/theme/state");

function iconStyle(name, tone, id) {
  const theme = registry.getTheme(id);
  const glyph = Object.prototype.hasOwnProperty.call(glyphs, name) ? name : theme.fallback;
  const color = registry.iconColor(id, tone);
  const body = glyphs[glyph].replace(/CURRENT/g, color);
  const svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='" + color +
    "' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>" + body + "</svg>";
  return 'background-image:url("data:image/svg+xml,' + encodeURIComponent(svg).replace(/'/g, "%27") + '")';
}
Component({
  options: { virtualHost: true, styleIsolation: "apply-shared" },
  properties: { name: { type: String, value: "default" }, tone: { type: String, value: "ink" }, size: String },
  data: { paintStyle: "" },
  observers: { "name,tone"() { this.paint(); } },
  lifetimes: {
    attached() {
      this.paint();
      this._unsubscribe = themeState.subscribe(() => this.paint());
    },
    detached() { if (this._unsubscribe) this._unsubscribe(); this._unsubscribe = null; }
  },
  methods: {
    paint() {
      const paintStyle = iconStyle(this.data.name, this.data.tone, themeState.current().id);
      if (this.data.paintStyle !== paintStyle) this.setData({ paintStyle });
    }
  }
});
module.exports = { iconStyle };
