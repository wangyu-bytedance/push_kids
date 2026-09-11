const FALLBACK_STATUS_BAR_HEIGHT = 20;
const FALLBACK_NAVIGATION_HEIGHT = 44;
const FALLBACK_SIDE_INSET = 88;

function finiteNumber(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function readWindowInfo() {
  try {
    if (typeof wx.getWindowInfo === "function") return wx.getWindowInfo();
    if (typeof wx.getSystemInfoSync === "function") return wx.getSystemInfoSync();
  } catch (error) {
    console.warn("primary-nav: 无法读取窗口尺寸，已使用安全回退", error && error.errMsg ? error.errMsg : "");
  }
  return {};
}

function readMenuButtonRect() {
  try {
    if (typeof wx.getMenuButtonBoundingClientRect === "function") {
      return wx.getMenuButtonBoundingClientRect() || {};
    }
  } catch (error) {
    console.warn("primary-nav: 无法读取胶囊尺寸，已使用安全回退", error && error.errMsg ? error.errMsg : "");
  }
  return {};
}

function measureNavigation() {
  const windowInfo = readWindowInfo();
  const menuButton = readMenuButtonRect();
  const statusBarHeight = Math.max(0, finiteNumber(windowInfo.statusBarHeight, FALLBACK_STATUS_BAR_HEIGHT));
  const windowWidth = Math.max(0, finiteNumber(windowInfo.windowWidth, 0));
  const menuTop = finiteNumber(menuButton.top, -1);
  const menuLeft = finiteNumber(menuButton.left, -1);
  const menuHeight = finiteNumber(menuButton.height, 0);
  const hasValidMenu = menuTop >= statusBarHeight && menuLeft > 0 && menuHeight > 0;
  const measuredHeight = hasValidMenu ? (menuTop - statusBarHeight) * 2 + menuHeight : FALLBACK_NAVIGATION_HEIGHT;
  const navigationHeight = measuredHeight >= 36 && measuredHeight <= 64
    ? Math.round(measuredHeight)
    : FALLBACK_NAVIGATION_HEIGHT;
  const capsuleInset = hasValidMenu && windowWidth > menuLeft
    ? windowWidth - menuLeft + 8
    : FALLBACK_SIDE_INSET;
  const maxSideInset = windowWidth > 0 ? Math.max(0, (windowWidth - 120) / 2) : FALLBACK_SIDE_INSET;
  const sideInset = Math.round(Math.min(capsuleInset, maxSideInset));

  return {
    statusBarHeight: Math.round(statusBarHeight),
    navigationHeight,
    totalHeight: Math.round(statusBarHeight + navigationHeight),
    sideInset
  };
}

Component({
  options: { addGlobalClass: true },
  data: {
    statusBarHeight: FALLBACK_STATUS_BAR_HEIGHT,
    navigationHeight: FALLBACK_NAVIGATION_HEIGHT,
    totalHeight: FALLBACK_STATUS_BAR_HEIGHT + FALLBACK_NAVIGATION_HEIGHT,
    sideInset: FALLBACK_SIDE_INSET
  },
  lifetimes: {
    attached() {
      this.setData(measureNavigation());
    }
  },
  pageLifetimes: {
    resize() {
      this.setData(measureNavigation());
    }
  }
});
