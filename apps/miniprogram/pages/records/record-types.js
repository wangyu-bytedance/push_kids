// Closed list: new record domains require their own Spec and lifecycle contract.
const { decorate } = require("../../utils/child-context");

module.exports = {
  data: { recordType: "learning", recordTypeOpen: false, recordSwitching: false,
    travelChildId: "", travelChildren: [], travelChildIndex: 0, travelOverlayOpen: false },
  methods: {
    travelView() { return this.selectComponent && this.selectComponent("#travel-diary"); },
    syncRecordOverlay() {
      const bar = this.getTabBar && this.getTabBar();
      if (bar) bar.setData({ recordOverlayVisible: this.pageVisible !== false && this.data.travelOverlayOpen });
    },
    openRecordTypes() {
      if (this.data.saving) return wx.showToast({ title: "请等待本次操作完成", icon: "none" });
      this.setData({ recordTypeOpen: !this.data.recordTypeOpen });
      this.syncRecordOverlay();
    },
    closeRecordTypes() { this.setData({ recordTypeOpen: false }); this.syncRecordOverlay(); },
    keepRecordTypesOpen() {},
    async selectRecordType(event) {
      const type = event.currentTarget.dataset.type;
      if (!["learning", "travel"].includes(type) || this.data.recordSwitching || this.data.saving) return;
      this.closeRecordTypes();
      if (type === this.data.recordType) return this.closeRecordTypes();
      const generation = this.typeSwitchSequence || 0;
      this.setData({ recordSwitching: true });
      try {
        if (this.data.recordType === "travel") {
          const view = this.travelView();
          if (view && !(await view.canLeave())) return;
        }
        if (generation !== (this.typeSwitchSequence || 0) || this.pageVisible === false) return;
        if (type === "travel") {
          this.stopLearning();
          this.setData({ recordType: type, recordTypeOpen: false, travelOverlayOpen: false, travelChildId: this.data.childId,
            travelChildren: [], travelChildIndex: 0 });
          if (wx.pageScrollTo) wx.pageScrollTo({ scrollTop: 0, duration: 0 });
        } else {
          this.setData({ recordType: type, recordTypeOpen: false, travelOverlayOpen: false });
          this.onShow();
        }
      } finally {
        this.setData({ recordSwitching: false }); this.syncRecordOverlay();
        // A newer explicit learning entry may have arrived while the old guard was pending.
        if (generation !== (this.typeSwitchSequence || 0) && this.pageVisible === true &&
          this.data.recordType === "travel" && getApp().globalData.recordIntent) this.onShow();
      }
    },
    travelContextChanged(event) {
      if (this.data.recordType !== "travel") return;
      this.setData({ travelChildren: event.detail.children.map((child) => ({ ...decorate(child), label: child.label })), travelChildIndex: event.detail.childIndex });
    },
    travelOverlayChanged(event) {
      this.setData({ travelOverlayOpen: Boolean(event.detail.open) });
      this.syncRecordOverlay();
    },
    changeTravelChild(event) { const view = this.travelView(); if (view) return view.changeChild(event); },
    onPageScroll(event) {
      if (this.data.recordTypeOpen) this.closeRecordTypes();
      if (this.data.recordType === "learning") this.recordScroll = event.scrollTop;
    },
    onReachBottom() { const view = this.travelView(); if (this.data.recordType === "travel" && view) return view.onReachBottom(); }
  }
};
