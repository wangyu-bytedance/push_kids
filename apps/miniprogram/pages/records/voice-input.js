const MAX_RECORDING_MS = 60000;

const SAFE_MESSAGES = {
  permission_denied: "需要麦克风权限，也可以继续手动填写",
  permission_unavailable: "暂时无法申请麦克风权限，可以继续手动填写",
  plugin_unavailable: "语音输入暂时不可用，可以继续手动填写",
  recognition_failed: "暂时没有转成文字，请重试或手动填写",
  no_speech: "没有听清，请靠近一些再试",
  permission_ready: "已允许麦克风，请重新按住"
};

function callWx(wxApi, method, options = {}) {
  return new Promise((resolve, reject) => {
    if (!wxApi || typeof wxApi[method] !== "function") {
      reject(new Error("unsupported"));
      return;
    }
    wxApi[method]({ ...options, success: resolve, fail: reject });
  });
}

async function preparePermissions(wxApi) {
  let prompted = false;
  if (typeof wxApi.getPrivacySetting === "function") {
    let privacy;
    try {
      privacy = await callWx(wxApi, "getPrivacySetting");
    } catch {
      return { status: "permission_unavailable" };
    }
    if (privacy && privacy.needAuthorization) {
      try {
        await callWx(wxApi, "requirePrivacyAuthorize");
        prompted = true;
      } catch {
        return { status: "permission_denied" };
      }
    }
  }

  let settings;
  try {
    settings = await callWx(wxApi, "getSetting");
  } catch {
    return { status: "permission_unavailable" };
  }
  if (!settings.authSetting || settings.authSetting["scope.record"] !== true) {
    try {
      await callWx(wxApi, "authorize", { scope: "scope.record" });
      prompted = true;
    } catch {
      return { status: "permission_denied" };
    }
  }
  return { status: prompted ? "permission_ready" : "ready" };
}

function createVoiceInputController(options = {}) {
  const wxApi = options.wxApi || wx;
  const loadPlugin = options.loadPlugin || (() => requirePlugin("WechatSI"));
  const onState = options.onState || (() => {});
  const onResult = options.onResult || (() => {});
  const onNotice = options.onNotice || (() => {});
  const getContextKey = options.getContextKey || (() => "");
  let state = "idle";
  let busy = false;
  let manager;
  let activeSession;
  let beginToken = 0;
  let sessionId = 0;
  let disposed = false;

  function emitState(nextState, nextBusy = nextState !== "idle") {
    state = nextState;
    busy = nextBusy;
    onState({ state, busy });
  }

  function notify(code) {
    onNotice({ code, message: SAFE_MESSAGES[code] || SAFE_MESSAGES.recognition_failed });
  }

  function releaseSession(session, noticeCode) {
    if (activeSession !== session) return;
    activeSession = undefined;
    emitState("idle", false);
    if (noticeCode) notify(noticeCode);
  }

  function bindManager() {
    if (manager) return manager;
    let plugin;
    try {
      plugin = loadPlugin();
      manager = plugin && plugin.getRecordRecognitionManager && plugin.getRecordRecognitionManager();
    } catch {
      manager = undefined;
    }
    if (!manager || typeof manager.start !== "function" || typeof manager.stop !== "function") {
      manager = undefined;
      return undefined;
    }
    manager.onStart = () => {};
    manager.onStop = (response = {}) => {
      const session = activeSession;
      if (!session) return;
      if (session.discard || disposed || session.contextKey !== getContextKey()) {
        releaseSession(session);
        return;
      }
      const result = typeof response.result === "string" ? response.result.trim() : "";
      releaseSession(session);
      if (!result) {
        notify("no_speech");
        return;
      }
      onResult({ text: result, contextKey: session.contextKey });
    };
    manager.onError = () => {
      const session = activeSession;
      if (!session) return;
      releaseSession(session, session.discard || disposed ? undefined : "recognition_failed");
    };
    return manager;
  }

  async function begin({ isGestureActive = () => true, contextKey = getContextKey() } = {}) {
    if (disposed || busy || activeSession) return { status: "busy" };
    const token = ++beginToken;
    emitState("requesting_permission", true);
    const permission = await preparePermissions(wxApi);
    if (disposed || token !== beginToken) return { status: "cancelled" };
    if (permission.status !== "ready") {
      emitState("idle", false);
      notify(permission.status);
      return permission;
    }
    if (!isGestureActive()) {
      emitState("idle", false);
      return { status: "cancelled" };
    }
    const recorder = bindManager();
    if (!recorder) {
      emitState("idle", false);
      notify("plugin_unavailable");
      return { status: "plugin_unavailable" };
    }
    const session = { id: ++sessionId, contextKey, discard: false };
    activeSession = session;
    emitState("holding", true);
    try {
      recorder.start({ duration: MAX_RECORDING_MS, lang: "zh_CN" });
    } catch {
      releaseSession(session, "recognition_failed");
      return { status: "recognition_failed" };
    }
    return { status: "started", sessionId: session.id };
  }

  function setCancelArmed(armed) {
    if (!activeSession || !["holding", "cancel_armed"].includes(state)) return;
    emitState(armed ? "cancel_armed" : "holding", true);
  }

  function stopActive(discard) {
    const session = activeSession;
    if (!session) return false;
    session.discard = discard;
    emitState(discard ? "idle" : "recognizing", true);
    try {
      manager.stop();
    } catch {
      releaseSession(session, discard ? undefined : "recognition_failed");
    }
    return true;
  }

  function finish() {
    if (state === "requesting_permission") {
      beginToken += 1;
      emitState("idle", false);
      return false;
    }
    if (state === "cancel_armed") return stopActive(true);
    if (state === "holding") return stopActive(false);
    return false;
  }

  function cancel() {
    beginToken += 1;
    if (state === "requesting_permission") emitState("idle", false);
    if (activeSession && state === "recognizing") {
      activeSession.discard = true;
      emitState("idle", true);
      return true;
    }
    if (activeSession) return stopActive(true);
    return false;
  }

  function dispose() {
    if (disposed) return;
    cancel();
    disposed = true;
    if (manager) {
      manager.onStart = () => {};
      manager.onStop = () => {};
      manager.onError = () => {};
    }
  }

  return {
    begin,
    cancel,
    dispose,
    finish,
    isBusy: () => busy,
    setCancelArmed,
    state: () => state
  };
}

module.exports = {
  MAX_RECORDING_MS,
  SAFE_MESSAGES,
  createVoiceInputController,
  preparePermissions
};
