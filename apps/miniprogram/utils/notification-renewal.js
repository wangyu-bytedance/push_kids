/* 通知专用控制器：服务器持有开关/计数/额度，内存仅保存短租约与尚未登记的真实回调。
   每次原生授权都必须从按钮的同步调用链进入；恢复只登记原事件。 */
const api = require("./api");

let nativeBusy = false;
const pending = new Map(); // 当前进程至多3类；离开身份后绝不以新身份提交。

function now() {
  const performance = typeof wx.getPerformance === "function" && wx.getPerformance();
  return performance && typeof performance.now === "function" ? performance.now() : Date.now();
}

function identity() {
  const data = getApp().globalData;
  return `${data.familyId || ""}:${(data.currentMember || {}).id || data.localActorId || ""}`;
}

function deviceSettings() {
  return new Promise((resolve) => {
    if (typeof wx.getSetting !== "function") return resolve(null);
    wx.getSetting({ withSubscriptions: true,
      success: (value) => resolve(value.subscriptionsSetting || null), fail: () => resolve(null) });
  });
}

function decisions(response, bindings, failure) {
  return bindings.map((item) => {
    const value = response && response[item.template_id];
    let decision = ["accept", "reject", "ban", "filter"].includes(value) ? value : "unknown";
    // errMsg是未受信任输入，仅识别明确的取消；不把网络/API失败冒充拒绝。
    if (failure) decision = /\bcancel\b/i.test(String(failure.errMsg || "")) ? "cancel" : "technical";
    return { type: item.type, decision };
  });
}

function createController(onChange = () => {}) {
  let scope = identity();
  let generation = 0;
  let active = true;
  let view = null;
  let observed = null;
  let observedAt = 0;
  let prepared = [];
  let refreshing = null;

  function current(token) { return active && scope === identity() && token === generation; }
  function emit() { if (active && scope === identity()) onChange(view); }
  function remember(attempt, body) {
    if (scope !== identity()) return;
    if (pending.size >= 3 && !pending.has(attempt.attempt_id)) return;
    pending.set(attempt.attempt_id, { scope, body });
  }
  async function recover() {
    for (const [id, entry] of pending) {
      if (entry.scope !== identity()) continue;
      // 最多两次有界恢复；超时保留同一ID，下一次页面进入再恢复。
      for (let retry = 0; retry < 2; retry += 1) {
        try {
          const state = await api.request(`/notifications/grant-attempts/${id}/result`, {
            method: "POST", data: entry.body
          });
          if (entry.scope !== identity()) return;
          if (state.state === "registered") pending.delete(id);
          break;
        } catch (error) {
          if (error.statusCode && error.statusCode < 500) break;
          if (retry === 0) await new Promise((resolve) => setTimeout(resolve, 250));
        }
      }
    }
  }
  async function refresh(mode = "auto") {
    if (refreshing && refreshing.generation === generation) return refreshing.promise;
    const token = generation;
    const run = async () => {
      await recover();
      if (!current(token)) return null;
      const [next, device] = await Promise.all([
        api.request("/notifications/renewal"), deviceSettings()
      ]);
      if (!current(token)) return null;
      view = next;
      observed = device;
      observedAt = now();
      // 到期且本进程确认未调用的预备记录，可安全释放；丢失进程则交给服务端显示未知。
      const expired = prepared.filter((item) => now() >= item.localExpiry || item.choiceVersion !== view.version);
      prepared = prepared.filter((item) => now() < item.localExpiry && item.choiceVersion === view.version);
      expired.forEach((item) => remember(item, { results: item.bindings.map((binding) => ({ type: binding.type, decision: "technical" })) }));
      if (expired.length) await recover();
      if (!current(token)) return null;
      emit();
      if (!device || typeof device.mainSwitch !== "boolean" || typeof wx.requestSubscribeMessage !== "function") return view;
      const settings = view.settings;
      if (!settings || !settings.channel.available) return view;
      const selectedMode = mode === "manual" ? "manual" : view.choice === "unseen" ? "onboarding" : "auto";
      const waitingTypes = new Set([...pending.values()].filter((entry) => entry.scope === identity())
        .flatMap((entry) => entry.body.results.map((item) => item.type)));
      const items = settings.preferences.filter((item) => item.enabled && item.template_id && item.remaining_quota === 0
        && !waitingTypes.has(item.type)
        && (selectedMode !== "onboarding" || item.previously_granted));
      const remembered = {};
      items.forEach((item) => {
        const value = (device.itemSettings || {})[item.template_id];
        if (["accept", "reject"].includes(value)) remembered[item.type] = value;
      });
      // 设置页逐类预备，既可单独补充，也可在一个微信调用中合并最多3类。
      const batches = selectedMode === "manual" ? items.map((item) => [item]) : [items];
      for (const batch of batches) {
        if (!batch.length || !current(token)) continue;
        if (prepared.some((item) => item.mode === selectedMode && item.bindings.some((binding) => batch.some((entry) => binding.type === entry.type)))) continue;
        const startedAt = now();
        const result = await api.request("/notifications/grant-attempts", {
          method: "POST", idempotencyKey: api.newIdempotencyKey("grant"),
          data: { mode: selectedMode, types: batch.map((item) => item.type), expected_version: view.version,
            main_switch: device.mainSwitch, remembered }
        });
        if (!current(token)) return null;
        view = result.renewal;
        if (result.attempt && result.attempt.state === "prepared") {
          // 使用请求起点的单调经过时间限制租约，避免客户端墙钟与服务端时差。
          prepared.push({ ...result.attempt, localExpiry: startedAt + 55000, choiceVersion: view.version });
        }
      }
      emit();
      return view;
    };
    const slot = { generation, promise: run().catch((error) => {
      if (current(token)) observed = null; // 查询失败后，旧候选不能继续触发原生申请。
      throw error;
    }).finally(() => { if (refreshing === slot) refreshing = null; }) };
    refreshing = slot;
    return slot.promise;
  }
  function invoke(mode, type) {
    if (!active || scope !== identity() || nativeBusy || typeof wx.requestSubscribeMessage !== "function") return false;
    if (!observed || now() - observedAt >= 55000) { refresh(mode).catch(() => {}); return false; }
    if (observed.mainSwitch !== true) return false;
    if (!view || (mode === "auto" && view.choice !== "enabled") || (mode === "onboarding" && view.choice !== "unseen")) return false;
    const selected = prepared.filter((item) => item.mode === mode && now() < item.localExpiry
      && item.choiceVersion === view.version
      && (!type || item.bindings.some((binding) => binding.type === type)));
    if (!selected.length) { refresh(mode).catch(() => {}); return false; }
    const bindings = selected.flatMap((item) => item.bindings);
    if ([...pending.values()].some((entry) => entry.scope === identity()
      && entry.body.results.some((item) => bindings.some((binding) => binding.type === item.type)))) return false;
    if (!view.settings.channel.available || bindings.some((binding) => !view.settings.preferences.some((item) => item.type === binding.type && item.enabled && item.remaining_quota === 0))) return false;
    if (bindings.some((item) => (observed.itemSettings || {})[item.template_id] === "reject")) return false;
    nativeBusy = true;
    const invocationScope = scope;
    let settled = false;
    prepared = prepared.filter((item) => !selected.includes(item));
    const finish = (response, failure) => {
      if (settled) return;
      settled = true;
      nativeBusy = false;
      if (invocationScope !== identity()) return;
      selected.forEach((attempt) => remember(attempt, {
        results: decisions(response, attempt.bindings, failure), enable_renewal: mode === "onboarding"
      }));
      emit();
      recover().then(() => refresh(mode === "manual" ? "manual" : "auto")).catch(() => {});
    };
    // 手势关键点：本函数到此没有await，也没有业务网络请求。
    try {
      wx.requestSubscribeMessage({ tmplIds: bindings.map((item) => item.template_id),
        success: (response) => finish(response, null), fail: (error) => finish(null, error) });
    } catch (error) { finish(null, error); }
    // 不等待started，原生调用已在其之前发出；回调可能比started更早，服务端需幂等。
    selected.forEach((attempt) => api.request(`/notifications/grant-attempts/${attempt.attempt_id}/started`, { method: "POST" }).catch(() => {}));
    return true;
  }
  return {
    refresh,
    complete() { return invoke("auto"); },
    grant(type) { return invoke("manual", type); },
    enableFromGuide() { return invoke("onboarding"); },
    guideReady() { return active && scope === identity() && view && view.choice === "unseen"
      && prepared.some((item) => item.mode === "onboarding" && now() < item.localExpiry); },
    async setChoice(enabled) {
      if (!view || scope !== identity()) throw new Error("提醒状态待更新，请稍后再试");
      const token = generation;
      const next = await api.request("/notifications/renewal", { method: "PATCH", idempotencyKey: api.newIdempotencyKey("renewal"),
        data: { choice: enabled ? "enabled" : "disabled", expected_version: view.version } });
      if (!current(token)) return;
      view = next;
      emit();
    },
    view: () => view,
    busy: () => nativeBusy,
    pendingTypes() { return [...pending.values()].filter((entry) => entry.scope === identity())
      .flatMap((entry) => entry.body.results.map((item) => item.type)); },
    ready(type) { return prepared.some((item) => item.mode === "manual" && now() < item.localExpiry
      && (!type || item.bindings.some((binding) => binding.type === type))); },
    hide() {
      prepared.forEach((attempt) => remember(attempt, { results: attempt.bindings.map((binding) => ({ type: binding.type, decision: "technical" })) }));
      prepared = [];
      recover().catch(() => {});
      active = false; generation += 1;
    },
    show() {
      active = true;
      if (scope !== identity()) { scope = identity(); prepared = []; view = null; observed = null; }
      for (const [id, entry] of pending) if (entry.scope !== identity()) pending.delete(id);
      generation += 1;
    }
  };
}

module.exports = { createController, decisions };
