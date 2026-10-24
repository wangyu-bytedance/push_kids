Component({
  properties: { visible: Boolean, saving: Boolean },
  methods: {
    enable() { if (!this.data.saving) this.triggerEvent("enable"); },
    decline() { if (!this.data.saving) this.triggerEvent("decline"); },
    contain() {}
  }
});
