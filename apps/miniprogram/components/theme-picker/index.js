const registry = require("../../presentation/theme/registry");
const { themeState } = require("../../presentation/theme/state");
const { withThemeComponent } = require("../../presentation/theme/adapters");

Component(withThemeComponent({
  options: { addGlobalClass: true },
  properties: { visible: Boolean },
  data: {
    selectedId: registry.DEFAULT_ID,
    currentId: registry.DEFAULT_ID,
    choices: registry.listThemes().map((t) => ({
      id: t.id, name: t.name, description: t.description, preview: t.assets.preview,
      style: "--tile-bg:" + t.tokens["pk-surface"] + ";--tile-ink:" + t.tokens["pk-ink"]
    }))
  },
  observers: {
    visible(open) {
      if (open) {
        const id = themeState.current().id;
        this.setData({ selectedId: id, currentId: id });
      }
    }
  },
  methods: {
    choose(event) {
      const id = event.currentTarget.dataset.id;
      if (registry.getTheme(id).id === id) this.setData({ selectedId: id });
    },
    apply() {
      if (this.data.selectedId === themeState.current().id) return;
      const result = themeState.setTheme(this.data.selectedId);
      this.triggerEvent("apply", result);
    },
    close() { this.triggerEvent("close"); },
    contain() {},
    imageFailed(event) {
      const index = Number(event.currentTarget.dataset.index);
      if (Number.isInteger(index) && this.data.choices[index]) this.setData({ ["choices[" + index + "].failed"]: true });
    }
  }
}));
