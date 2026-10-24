Component({
  properties: { view: { type: Object, value: null }, blocked: Boolean },
  observers: { blocked() { if (this.hostVisible) this.schedule("availability"); } },
  lifetimes: { attached() { this.hostVisible = true; this.schedule("show"); }, detached() { this.hostVisible = false; this.schedule("hide"); } },
  pageLifetimes: {
    show() { this.hostVisible = true; this.schedule("show"); },
    hide() { this.hostVisible = false; this.schedule("hide"); }
  },
  methods: {
    schedule(action) {
      // Property/lifecycle callbacks run during the host's setData. Notify after that update.
      Promise.resolve().then(() => {
        if (action === "hide" || this.hostVisible) this.send(action);
      });
    },
    send(action, extra = {}) { this.triggerEvent("action", { action, blocked: !!this.data.blocked, ...extra }); },
    confirm() { this.send("confirm"); },
    later() { this.send("later"); },
    pickerOpen() { this.send("picker-open"); },
    pickerCancel() { this.send("picker-close"); },
    choose(event) { this.send("choose", { index: Number(event.detail.value) }); },
    contain() {}
  }
});
