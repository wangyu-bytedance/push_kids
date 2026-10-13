const controller = require("../../pages/review-inventory/controller");

const methods = Object.fromEntries(Object.entries(controller).filter(([name]) =>
  !["data", "onLoad", "onShow", "onHide", "onUnload", "onPullDownRefresh"].includes(name)));

Component({
  options: { styleIsolation: "apply-shared" },
  properties: { contextChildId: { type: String, value: "" }, embedded: { type: Boolean, value: false } },
  data: { ...controller.data },
  methods,
  lifetimes: {
    attached() {
      controller.onLoad.call(this, { childId: this.properties.contextChildId });
      return controller.onShow.call(this);
    },
    detached() {
      this.visible = false;
      this.showGeneration = (this.showGeneration || 0) + 1;
      this.generation = (this.generation || 0) + 1;
      this.subjectGeneration = (this.subjectGeneration || 0) + 1;
    }
  }
});
