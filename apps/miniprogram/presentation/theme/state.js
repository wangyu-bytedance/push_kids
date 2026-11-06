const registry = require("./registry");
const STORAGE_KEY = "pk.theme.v1";

function createThemeStore(platform) {
  let id = registry.DEFAULT_ID;
  let initialized = false, persisted = true, revision = 0;
  const consumers = new Set();
  function runtime() { return platform || (typeof wx === "undefined" ? null : wx); }
  function initialize() {
    if (initialized) return registry.getTheme(id);
    initialized = true;
    try {
      const api = runtime(), value = api && api.getStorageSync(STORAGE_KEY);
      if (value && value.version === 1 && typeof value.id === "string" && registry.getTheme(value.id).id === value.id) id = value.id;
    } catch {
      if (typeof console !== "undefined") console.warn("THEME_PREFERENCE_READ_FAILED");
    }
    return registry.getTheme(id);
  }
  return {
    initialize,
    current() { return initialize(); },
    setTheme(next) {
      initialize();
      if (typeof next !== "string" || registry.getTheme(next).id !== next || next === id) return { id, persisted };
      id = next;
      const change = ++revision;
      try {
        const api = runtime();
        if (!api || typeof api.setStorageSync !== "function") throw Error("NO_STORAGE");
        api.setStorageSync(STORAGE_KEY, { version: 1, id });
        persisted = true;
      } catch {
        persisted = false;
        if (typeof console !== "undefined") console.warn("THEME_PREFERENCE_WRITE_FAILED");
      }
      const result = { id, persisted }, value = registry.getTheme(id);
      for (const consumer of Array.from(consumers)) {
        if (change !== revision) break;
        if (!consumers.has(consumer)) continue;
        try { consumer(value); } catch {
          if (typeof console !== "undefined") console.warn("THEME_CONSUMER_UPDATE_FAILED");
        }
      }
      return result;
    },
    subscribe(consumer) {
      consumers.add(consumer);
      return () => consumers.delete(consumer);
    }
  };
}
const themeState = createThemeStore();
module.exports = { createThemeStore, themeState, STORAGE_KEY };
