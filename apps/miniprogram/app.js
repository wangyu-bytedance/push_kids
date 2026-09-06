const config = require("./config");

App({
  globalData: {
    useCloud: config.useCloud,
    cloudEnv: config.cloudEnv,
    cloudService: config.cloudService,
    apiBasePath: config.apiBasePath,
    familyId: config.localFamilyId,
    localActorId: config.localActorId,
    selectedChildId: "",
    bootstrapState: "loading",
    openCalendarCreate: false,
    currentMember: null,
    tabBadges: { records: 0 },
    apiBaseUrl: config.localApiBaseUrl
  },
  onLaunch(options = {}) {
    if (config.useCloud) wx.cloud.init({ env: config.cloudEnv });
    this.globalData.selectedChildId = wx.getStorageSync("selectedChildId") || "";
    const isJoinLaunch = options.path === "pages/family-join/index";
    if ((!config.useCloud || wx.cloud.callContainer) && !isJoinLaunch) {
      this.refreshBootstrap(true).catch(() => {});
    }
  },
  async refreshBootstrap(redirect = false) {
    const api = require("./utils/api");
    try {
      const result = await api.request("/me", { actorOnly: true });
      this.globalData.bootstrapState = result.state;
      this.globalData.currentMember = result.member || null;
      if (result.family) this.globalData.familyId = result.family.id;
      if (result.children && result.children.length && !this.globalData.selectedChildId) {
        this.selectChild(result.children[0].id);
      }
      if (redirect && result.state !== "bound" && wx.reLaunch) {
        wx.reLaunch({ url: "/pages/family-onboarding/index" });
      }
      return result;
    } catch (error) {
      this.globalData.bootstrapState = "error";
      throw error;
    }
  },
  selectChild(childId) {
    this.globalData.selectedChildId = childId;
    wx.setStorageSync("selectedChildId", childId);
  },
  setTabBadge(key, count) {
    const value = Number(count) > 0 ? Number(count) : 0;
    if (this.globalData.tabBadges[key] === value) return;
    this.globalData.tabBadges[key] = value;
    const pages = getCurrentPages();
    const current = pages[pages.length - 1];
    const bar = current && current.getTabBar && current.getTabBar();
    if (bar && bar.syncBadges) bar.syncBadges();
  }
});
