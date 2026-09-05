const config = require("./config");

App({
  globalData: {
    useCloud: config.useCloud,
    cloudEnv: config.cloudEnv,
    cloudService: config.cloudService,
    apiBasePath: config.apiBasePath,
    familyId: config.localFamilyId,
    selectedChildId: "",
    apiBaseUrl: config.localApiBaseUrl
  },
  onLaunch() {
    if (config.useCloud) wx.cloud.init({ env: config.cloudEnv });
    this.globalData.selectedChildId = wx.getStorageSync("selectedChildId") || "";
  },
  selectChild(childId) {
    this.globalData.selectedChildId = childId;
    wx.setStorageSync("selectedChildId", childId);
  }
});
