const BASE = {
  "pk-canvas": "#FAF7F0",
  "pk-canvas-deep": "#F3EFE4",
  "pk-surface": "#FFFDF8",
  "pk-surface-raised": "#FFFFFF",
  "pk-surface-warm": "#FDFBF5",
  "pk-surface-sunken": "#F3EFE4",
  "pk-primary": "#1F5B45",
  "pk-primary-strong": "#14402F",
  "pk-primary-pressed": "#103527",
  "pk-primary-mid": "#38826A",
  "pk-primary-tint": "#E4EDE6",
  "pk-primary-tint-2": "#D2E1D6",
  "pk-primary-wash": "#F0F5F0",
  "pk-primary-hairline": "#C3D8CA",
  "pk-sprout": "#7FA65C",
  "pk-sprout-bg": "#EDF2E2",
  "pk-sprout-line": "#D8E4C4",
  "pk-ink": "#22261F",
  "pk-ink-2": "#464E43",
  "pk-ink-3": "#79826F",
  "pk-ink-4": "#A6AD9C",
  "pk-ink-inv": "#FFFDF8",
  "pk-line": "#EBE5D7",
  "pk-line-soft": "#F1ECE0",
  "pk-line-strong": "#DDD6C4",
  "pk-attention": "#A9762A",
  "pk-attention-bg": "#F8EFDC",
  "pk-attention-line": "#E9D5AE",
  "pk-danger": "#A85742",
  "pk-danger-bg": "#F7E8E2",
  "pk-danger-line": "#E9CDC2",
  "pk-success": "#2F7A5B",
  "pk-success-bg": "#E4EDE6",
  "pk-info": "#4A6A7C",
  "pk-info-bg": "#E7EEF2",
  "pk-info-line": "#D4E1E8",
  "pk-sub-chinese": "#96671F",
  "pk-sub-chinese-bg": "#F5EBDA",
  "pk-sub-math": "#3F6379",
  "pk-sub-math-bg": "#E6EDF3",
  "pk-sub-english": "#565383",
  "pk-sub-english-bg": "#EDECF5",
  "pk-sub-activity": "#566E33",
  "pk-sub-activity-bg": "#E9F1E0",
  "pk-sub-other": "#96543F",
  "pk-sub-other-bg": "#F3E9E9",
  "pk-r-xs": "10rpx",
  "pk-r-sm": "16rpx",
  "pk-r-md": "24rpx",
  "pk-r-lg": "32rpx",
  "pk-r-xl": "40rpx",
  "pk-r-2xl": "52rpx",
  "pk-r-pill": "999rpx",
  "pk-s1": "8rpx",
  "pk-s2": "16rpx",
  "pk-s3": "24rpx",
  "pk-s4": "32rpx",
  "pk-s5": "40rpx",
  "pk-s6": "48rpx",
  "pk-s7": "64rpx",
  "pk-s8": "80rpx",
  "pk-gutter": "36rpx",
  "pk-border": "1rpx solid rgba(34, 38, 31, .06)",
  "pk-border-line": "1rpx solid var(--pk-line)",
  "pk-border-soft": "1rpx solid var(--pk-line-soft)",
  "pk-border-primary": "1rpx solid var(--pk-primary-hairline)",
  "pk-e0": "0 2rpx 4rpx rgba(34, 38, 31, .04)",
  "pk-e1": "0 2rpx 4rpx rgba(34, 38, 31, .04)",
  "pk-e2": "0 2rpx 4rpx rgba(34, 38, 31, .04), 0 20rpx 48rpx -28rpx rgba(34, 38, 31, .18)",
  "pk-e3": "0 4rpx 12rpx rgba(34, 38, 31, .05), 0 44rpx 88rpx -40rpx rgba(34, 38, 31, .26)",
  "pk-e-sheet": "0 -24rpx 80rpx -28rpx rgba(24, 28, 20, .44)",
  "pk-e-fab": "0 20rpx 44rpx -16rpx rgba(31, 91, 69, .66)",
  "pk-e-btn": "0 12rpx 32rpx -16rpx rgba(31, 91, 69, .7)",
  "pk-touch-min": "44px",
  "pk-cta-h": "96rpx",
  "pk-btn-md": "88rpx",
  "pk-btn-sm": "72rpx",
  "pk-row-min": "112rpx",
  "pk-tabbar-h": "108rpx",
  "pk-serif": "\"Songti SC\", \"Noto Serif SC\", \"Noto Serif CJK SC\", \"Source Han Serif SC\", \"STSong\", serif",
  "pk-sans": "-apple-system, BlinkMacSystemFont, \"PingFang SC\", \"Noto Sans SC\", \"Microsoft YaHei\", sans-serif",
  "pk-dur-fast": "140ms",
  "pk-dur-base": "240ms",
  "pk-dur-slow": "420ms",
  "pk-ease": "cubic-bezier(.22, .75, .24, 1)",
  "pk-ease-spring": "cubic-bezier(.34, 1.42, .5, 1)",
  "pk-ease-sheet": "cubic-bezier(.32, .72, 0, 1)",
  "canvas": "var(--pk-canvas)",
  "surface": "var(--pk-surface)",
  "surface-soft": "var(--pk-primary-tint)",
  "primary": "var(--pk-primary)",
  "primary-dark": "var(--pk-primary-strong)",
  "ink": "var(--pk-ink)",
  "muted": "var(--pk-ink-3)",
  "line": "var(--pk-line)",
  "warm": "var(--pk-attention-bg)",
  "warning": "var(--pk-attention)",
  "danger": "var(--pk-danger)"
};

// Presentation owns these roles. Pages consume roles; they never select palettes.
Object.assign(BASE, {
  "pk-page-background": "radial-gradient(ellipse 120% 40% at 50% -10%, rgba(255,255,255,.9) 0%, transparent 70%), var(--pk-canvas)",
  "pk-hero-background": "linear-gradient(120deg, #F7F4EA 0%, #EDF2E6 100%)",
  "pk-nav-bg": "var(--pk-canvas)", "pk-nav-ink": "var(--pk-primary)",
  "pk-header-ink": "var(--pk-ink)", "pk-header-muted": "var(--pk-ink-3)",
  "pk-on-primary": "#FFFDF8", "pk-on-danger": "#FFFFFF",
  "pk-overlay": "rgba(24,28,20,.44)", "pk-white-wash": "rgba(255,253,248,.9)",
  "pk-white-line": "rgba(255,253,248,.55)", "pk-soft-shadow": "rgba(34,38,31,.06)",
  "pk-sk-start": "rgba(34,38,31,.04)", "pk-sk-end": "rgba(34,38,31,.08)"
});
Object.assign(BASE, {
  "pk-photo-mask": "rgba(24,28,20,.62)", "pk-photo-ink": "#ffffff",
  "pk-native-danger": "#A85742",
  "pk-chart-1": "#E2EBE1", "pk-chart-2": "#C0D6C2", "pk-chart-3": "#86AF92",
  "pk-chart-4": "#1F5B45", "pk-neutral-fill": "rgba(34,38,31,.05)",
  "pk-add-icon": "var(--pk-primary)", "pk-map-route": "#1F5B45",
  "pk-text-muted": "#626D5C", "pk-attention-ink": "#80551D", "pk-success-ink": "#256347", "pk-danger-ink": "#87432F"
});

function palette(p) {
  return {
    "pk-canvas": p.canvas, "pk-canvas-deep": p.sunken,
    "pk-surface": p.surface, "pk-surface-raised": p.surface,
    "pk-surface-warm": p.surface, "pk-surface-sunken": p.sunken,
    "pk-primary": p.accent, "pk-primary-strong": p.strong,
    "pk-primary-pressed": p.strong, "pk-primary-mid": p.accent,
    "pk-primary-tint": p.tint, "pk-primary-tint-2": p.tint,
    "pk-primary-wash": p.wash, "pk-primary-hairline": p.line,
    "pk-ink": p.ink, "pk-ink-2": p.secondary, "pk-ink-3": p.secondary,
    "pk-ink-4": p.muted, "pk-ink-inv": p.onAccent, "pk-on-primary": p.onAccent,
    "pk-line": p.line, "pk-line-soft": p.line, "pk-line-strong": p.line,
    "pk-sprout": p.accent, "pk-sprout-bg": p.tint, "pk-sprout-line": p.line,
    "pk-sub-chinese": p.accent, "pk-sub-math": p.accent, "pk-sub-english": p.accent,
    "pk-sub-activity": p.accent, "pk-sub-other": p.accent,
    "pk-sub-chinese-bg": p.tint, "pk-sub-math-bg": p.tint, "pk-sub-english-bg": p.tint,
    "pk-sub-activity-bg": p.tint, "pk-sub-other-bg": p.tint,
    "pk-nav-bg": p.nav, "pk-nav-ink": p.headerInk,
    "pk-header-ink": p.headerInk, "pk-header-muted": p.headerMuted,
    "pk-page-background": "var(--pk-canvas)", "pk-hero-background": "var(--pk-primary-wash)",
    "pk-serif": BASE["pk-sans"], "pk-r-2xl": p.radius, "pk-r-xl": p.radius,
    "pk-white-wash": p.surface, "pk-white-line": p.line,
    "pk-border": "1rpx solid var(--pk-line)",
    "pk-soft-shadow": "transparent", "pk-e0": "none", "pk-e1": "none",
    "pk-e2": "none", "pk-e3": "none", "pk-e-btn": "none",
    "pk-e-fab": "0 8rpx 24rpx var(--pk-soft-shadow)",
    "pk-sk-start": p.sunken, "pk-sk-end": p.tint,
    "pk-chart-1": p.wash, "pk-chart-2": p.tint, "pk-chart-3": p.muted,
    "pk-chart-4": p.accent, "pk-neutral-fill": p.sunken, "pk-add-icon": p.onAccent,
    "pk-text-muted": p.secondary
  };
}

const definitions = [
  { id: "original", name: "原始风格", description: "纸面与松绿", fallback: "book", preview: "/assets/illustrations/record-books.png", tokens: {} },
  { id: "garden", name: "成长花园", description: "纸雕花园与嫩芽", fallback: "sprout", tokens: palette({
    canvas: "#eef2dc", surface: "#fffbee", sunken: "#f0efdb", accent: "#527a21", strong: "#375c21",
    tint: "#e2ecc3", wash: "#f2f5e4", ink: "#293f29", secondary: "#5d6c4b", muted: "#768564",
    line: "#e0e5c8", onAccent: "#ffffff", nav: "#f9f7e9", headerInk: "#233d29", headerMuted: "#445f3f", radius: "44rpx"
  }) },
  { id: "space", name: "星际探索", description: "星空与观测站", fallback: "planet", tokens: palette({
    canvas: "#dfe8fb", surface: "#f7faff", sunken: "#e6edfa", accent: "#405dd0", strong: "#3047a1",
    tint: "#e2e8ff", wash: "#edf2ff", ink: "#20355d", secondary: "#52658c", muted: "#7585a8",
    line: "#d4dff4", onAccent: "#ffffff", nav: "#192953", headerInk: "#ffffff", headerMuted: "#e3eaff", radius: "44rpx"
  }), lightChrome: true },
  { id: "midnight", name: "深海夜色", description: "静谧深海与金线", fallback: "compass", night: true, lightChrome: true, tokens: {
    ...palette({
      canvas: "#10262e", surface: "#1b343c", sunken: "#233f46", accent: "#e8c592", strong: "#edd4ad",
      tint: "#344a49", wash: "#243e43", ink: "#edf4f4", secondary: "#b3c6ca", muted: "#8ca6ad",
      line: "#3a535a", onAccent: "#21343a", nav: "#10262e", headerInk: "#f5f5ec", headerMuted: "#b3c8ce", radius: "28rpx"
    }),
    "pk-danger": "#ffb1a4", "pk-danger-bg": "#4a3439", "pk-danger-line": "#a76b68",
    "pk-danger-ink": "#ffb1a4",
    "pk-attention": "#e8c592", "pk-attention-bg": "#443e32", "pk-attention-line": "#8c785a",
    "pk-success": "#a8ddc0", "pk-success-bg": "#25483d",
    "pk-success-ink": "#a8ddc0", "pk-attention-ink": "#e8c592",
    "pk-info": "#acd9e7", "pk-info-bg": "#25434e", "pk-info-line": "#63818a",
    "pk-overlay": "rgba(2,12,18,.72)"
  } },
  { id: "ocean", name: "海洋风格", description: "阳光浅海与鲸鱼", fallback: "shell", tokens: palette({
    canvas: "#e2f5f8", surface: "#fafdff", sunken: "#e1f0f4", accent: "#087e9c", strong: "#086780",
    tint: "#d5f0f6", wash: "#edf8fa", ink: "#204454", secondary: "#526e7b", muted: "#7093a0",
    line: "#d3e9ef", onAccent: "#ffffff", nav: "#f2fbfd", headerInk: "#164554", headerMuted: "#275e6d", radius: "48rpx"
  }) },
  { id: "tech", name: "科技风格", description: "未来实验室与机器人", fallback: "chip", tokens: palette({
    canvas: "#eaf2f6", surface: "#ffffff", sunken: "#eaf2f6", accent: "#007d84", strong: "#005e68",
    tint: "#d9f4f3", wash: "#eff8fa", ink: "#193b49", secondary: "#506d79", muted: "#73919c",
    line: "#d4e7ed", onAccent: "#ffffff", nav: "#f5fafc", headerInk: "#173c49", headerMuted: "#456977", radius: "24rpx"
  }) }
];
const originalAssets = {
  learning: "/assets/illustrations/record-books.png", activity: "/assets/illustrations/settings-activity.png",
  daily: "/assets/illustrations/settings-daily.png", travel: "/assets/illustrations/settings-travel.png",
  calendar: "/assets/illustrations/calendar-still-life.png", report: "/assets/illustrations/report-growth.png",
  upload: "/assets/illustrations/record-camera.png"
};
const themes = definitions.map((item) => {
  const hero = item.id === "original" ? "" : `/assets/themes/${item.id}.jpg`;
  const tokens = Object.freeze({ ...BASE, ...item.tokens });
  const art = hero ? Object.fromEntries(Object.keys(originalAssets).map((role) => [role, hero])) : originalAssets;
  const assets = Object.freeze({ hero, preview: item.preview || hero, ...art });
  return Object.freeze({ ...item, tokens, assets, style: Object.entries(tokens).map(([key, value]) => `--${key}:${value}`).join(";"),
    classes: `pk-theme theme-${item.id}${item.id === "original" ? "" : " theme-illustrated"}`, chrome: Object.freeze({
      backgroundColor: tokens["pk-nav-bg"].startsWith("var(") ? tokens["pk-canvas"] : tokens["pk-nav-bg"],
      frontColor: item.lightChrome ? "#ffffff" : "#000000", backgroundTextStyle: item.lightChrome ? "light" : "dark"
    }) });
});
const DEFAULT_ID = "original";
function getTheme(id) { return themes.find((item) => item.id === id) || themes[0]; }
function listThemes() { return themes.slice(); }
function presentation(id) {
  const t = getTheme(id);
  return { id: t.id, name: t.name, classes: t.classes, style: t.style, assets: t.assets, fallback: t.fallback, night: !!t.night,
    colors: { primary: t.tokens["pk-primary"], line: t.tokens["pk-line"], ink: t.tokens["pk-ink"], surface: t.tokens["pk-surface"] } };
}
function iconColor(id, tone) {
  const t = getTheme(id);
  const roles = { primary: "pk-primary", inverse: "pk-on-primary", muted: "pk-ink-3", attention: "pk-attention", danger: "pk-danger", ink: "pk-ink-2", nav: "pk-nav-ink", action: "pk-add-icon" };
  const value = t.tokens[roles[tone] || roles.ink];
  const alias = /^var\(--([\w-]+)\)$/.exec(value);
  return alias ? t.tokens[alias[1]] : value;
}
module.exports = { DEFAULT_ID, getTheme, listThemes, presentation, iconColor, baseTokens: Object.freeze(BASE) };
