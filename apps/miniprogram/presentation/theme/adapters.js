const registry = require("./registry");
const { themeState } = require("./state");

function chrome(host) {
  if (typeof wx === "undefined" || typeof getCurrentPages === "undefined") return;
  const pages = getCurrentPages();
  if (pages[pages.length - 1] !== host) return;
  const t = themeState.current();
  const ignore = () => {};
  if (wx.setBackgroundColor) wx.setBackgroundColor({ backgroundColor: t.tokens["pk-canvas"], fail: ignore });
  if (wx.setBackgroundTextStyle) wx.setBackgroundTextStyle({ textStyle: t.chrome.backgroundTextStyle, fail: ignore });
  if (wx.setNavigationBarColor) wx.setNavigationBarColor({
    frontColor: t.chrome.frontColor, backgroundColor: t.chrome.backgroundColor, animation: { duration: 0 }, fail: ignore
  });
}
function paint(host, page) {
  const t = themeState.current();
  if (!host.data.theme || host.data.theme.id !== t.id || host.data.theme.style !== t.style) {
    host.setData({ theme: registry.presentation(t.id), themeArtFailed: false });
  }
  if (page) chrome(host);
}
function connect(host, page) {
  if (!host._themeUnsubscribe) host._themeUnsubscribe = themeState.subscribe(() => paint(host, page));
  paint(host, page);
}
function disconnect(host) {
  if (host._themeUnsubscribe) host._themeUnsubscribe();
  host._themeUnsubscribe = null;
}
function begin(original, page) {
  return function(...args) {
    connect(this, page);
    return original && original.apply(this, args);
  };
}
function end(original) {
  return function(...args) {
    try { return original && original.apply(this, args); }
    finally { disconnect(this); }
  };
}
function illustrationFailure() { this.setData({ themeArtFailed: true }); }
function withThemePage(definition) {
  return {
    ...definition,
    data: { ...definition.data, theme: registry.presentation(themeState.current().id), themeArtFailed: false },
    onThemeIllustrationError: illustrationFailure,
    onLoad: begin(definition.onLoad, true),
    onShow: begin(definition.onShow, true),
    onUnload: end(definition.onUnload)
  };
}
function withThemeComponent(definition) {
  return {
    ...definition,
    data: { ...definition.data, theme: registry.presentation(themeState.current().id), themeArtFailed: false },
    methods: { ...definition.methods, onThemeIllustrationError: illustrationFailure },
    lifetimes: { ...definition.lifetimes,
      attached: begin((definition.lifetimes && definition.lifetimes.attached) || definition.attached, false),
      detached: end((definition.lifetimes && definition.lifetimes.detached) || definition.detached) },
    pageLifetimes: { ...definition.pageLifetimes, show: begin(definition.pageLifetimes && definition.pageLifetimes.show, false) }
  };
}
module.exports = { withThemePage, withThemeComponent };
