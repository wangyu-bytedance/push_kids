const createController = require("./controller");
const { data, ...methods } = createController();

Component({
  options: { addGlobalClass: true },
  properties: { initialChildId: { type: String, value: "" }, menuOpen: { type: Boolean, value: false } },
  observers: {
    menuOpen(open) { if (open) this.pausePlayback(); },
    sheet(value) { this.triggerEvent("sheetchange", { open: Boolean(value) }); }
  },
  data: { ...data, embedded: true },
  methods: {
    ...methods,
    async canLeave() {
      if (this.data.saving || this.uploading) {
        wx.showToast({ title: "请等待本次操作完成", icon: "none" });
        return false;
      }
      return this.allowDiscard();
    }
  },
  lifetimes: {
    attached() {
      this.onLoad({ child_id: this.properties.initialChildId });
      this.onShow();
    },
    detached() { this.onUnload(); this.triggerEvent("sheetchange", { open: false }); }
  },
  pageLifetimes: {
    show() { if (this.hidden) this.onShow(); },
    hide() { this.onHide(); }
  }
});
