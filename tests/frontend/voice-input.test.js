const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { loadPage } = require("./harness");
const {
  MAX_RECORDING_MS,
  createVoiceInputController
} = require("../../apps/miniprogram/pages/records/voice-input");

function authorizedWx(overrides = {}) {
  return {
    getSetting({ success }) { success({ authSetting: { "scope.record": true } }); },
    ...overrides
  };
}

function fakePlugin() {
  const manager = {
    starts: [],
    stops: 0,
    start(options) { this.starts.push(options); },
    stop() { this.stops += 1; }
  };
  return { manager, plugin: { getRecordRecognitionManager: () => manager } };
}

function controllerFixture(options = {}) {
  const states = [];
  const notices = [];
  const results = [];
  const plugin = options.plugin || fakePlugin();
  let contextKey = options.contextKey || "child-a";
  const controller = createVoiceInputController({
    wxApi: options.wxApi || authorizedWx(),
    loadPlugin: () => plugin.plugin,
    getContextKey: () => contextKey,
    onState: (value) => states.push(value),
    onNotice: (value) => notices.push(value),
    onResult: (value) => results.push(value)
  });
  return { controller, states, notices, results, manager: plugin.manager, setContext: (value) => { contextKey = value; } };
}

test("authorized hold starts one 60-second Mandarin recognition and appends only final text", async () => {
  const fixture = controllerFixture();
  const result = await fixture.controller.begin({ contextKey: "child-a", isGestureActive: () => true });

  assert.equal(result.status, "started");
  assert.deepEqual(fixture.manager.starts, [{ duration: MAX_RECORDING_MS, lang: "zh_CN" }]);
  assert.equal(fixture.controller.state(), "holding");
  fixture.controller.finish();
  assert.equal(fixture.controller.state(), "recognizing");
  fixture.manager.onStop({ result: "  今天练习了乘法  ", tempFilePath: "must-not-be-used" });
  assert.deepEqual(fixture.results, [{ text: "今天练习了乘法", contextKey: "child-a" }]);
  assert.equal(fixture.controller.state(), "idle");
});

test("first microphone authorization completes without auto-start and requires a new hold", async () => {
  let granted = false;
  let authorizeCalls = 0;
  const fixture = controllerFixture({
    wxApi: authorizedWx({
      getSetting({ success }) { success({ authSetting: { "scope.record": granted } }); },
      authorize({ scope, success }) {
        assert.equal(scope, "scope.record");
        authorizeCalls += 1;
        granted = true;
        success({});
      }
    })
  });

  const first = await fixture.controller.begin({ isGestureActive: () => true });
  assert.equal(first.status, "permission_ready");
  assert.equal(authorizeCalls, 1);
  assert.equal(fixture.manager.starts.length, 0);
  assert.equal(fixture.notices.at(-1).code, "permission_ready");

  const second = await fixture.controller.begin({ isGestureActive: () => true });
  assert.equal(second.status, "started");
  assert.equal(fixture.manager.starts.length, 1);
});

test("privacy and microphone prompts can complete together but never start the released gesture", async () => {
  let privacyGranted = false;
  let recordGranted = false;
  const fixture = controllerFixture({
    wxApi: {
      getPrivacySetting({ success }) { success({ needAuthorization: !privacyGranted }); },
      requirePrivacyAuthorize({ success }) { privacyGranted = true; success({}); },
      getSetting({ success }) { success({ authSetting: { "scope.record": recordGranted } }); },
      authorize({ success }) { recordGranted = true; success({}); }
    }
  });

  const first = await fixture.controller.begin({ isGestureActive: () => false });
  assert.equal(first.status, "permission_ready");
  assert.equal(fixture.manager.starts.length, 0);
  const second = await fixture.controller.begin({ isGestureActive: () => true });
  assert.equal(second.status, "started");
});

test("an ended gesture cannot start recording when the asynchronous setting check returns", async () => {
  let resolveSetting;
  let touching = true;
  const fixture = controllerFixture({
    wxApi: authorizedWx({ getSetting({ success }) { resolveSetting = success; } })
  });

  const pending = fixture.controller.begin({ isGestureActive: () => touching });
  touching = false;
  fixture.controller.finish();
  resolveSetting({ authSetting: { "scope.record": true } });
  assert.equal((await pending).status, "cancelled");
  assert.equal(fixture.manager.starts.length, 0);
});

test("permission denial exposes only safe copy and leaves manual input available", async () => {
  const fixture = controllerFixture({
    wxApi: authorizedWx({
      getSetting({ success }) { success({ authSetting: {} }); },
      authorize({ fail }) { fail({ errMsg: "private platform detail" }); }
    })
  });

  const result = await fixture.controller.begin({ isGestureActive: () => true });
  assert.equal(result.status, "permission_denied");
  assert.equal(fixture.manager.starts.length, 0);
  assert.equal(fixture.notices[0].code, "permission_denied");
  assert.doesNotMatch(fixture.notices[0].message, /private platform detail/);
});

test("duplicate gestures are rejected while a recording or cancelled stop is draining", async () => {
  const fixture = controllerFixture();
  await fixture.controller.begin({ isGestureActive: () => true });
  assert.equal((await fixture.controller.begin({ isGestureActive: () => true })).status, "busy");
  fixture.controller.setCancelArmed(true);
  fixture.controller.finish();
  assert.equal(fixture.manager.stops, 1);
  assert.equal((await fixture.controller.begin({ isGestureActive: () => true })).status, "busy");
  fixture.manager.onStop({ result: "discard me" });
  assert.equal(fixture.results.length, 0);
  assert.equal((await fixture.controller.begin({ isGestureActive: () => true })).status, "started");
});

test("cancel, context changes, disposal, empty speech and plugin errors never leak transcript data", async () => {
  const fixture = controllerFixture();
  await fixture.controller.begin({ isGestureActive: () => true });
  fixture.controller.cancel();
  fixture.manager.onStop({ result: "cancelled child content", tempFilePath: "private-path" });
  assert.equal(fixture.results.length, 0);

  await fixture.controller.begin({ isGestureActive: () => true, contextKey: "child-a" });
  fixture.controller.finish();
  fixture.setContext("child-b");
  fixture.manager.onStop({ result: "wrong child content" });
  assert.equal(fixture.results.length, 0);

  await fixture.controller.begin({ isGestureActive: () => true, contextKey: "child-b" });
  fixture.controller.finish();
  fixture.manager.onStop({ result: "   " });
  assert.equal(fixture.notices.at(-1).code, "no_speech");

  await fixture.controller.begin({ isGestureActive: () => true, contextKey: "child-b" });
  fixture.manager.onError({ errMsg: "raw provider secret", errCode: -30013 });
  assert.equal(fixture.notices.at(-1).code, "recognition_failed");
  assert.doesNotMatch(fixture.notices.at(-1).message, /raw provider secret/);

  await fixture.controller.begin({ isGestureActive: () => true, contextKey: "child-b" });
  fixture.controller.dispose();
  fixture.manager.onStop({ result: "late disposed content" });
  assert.equal(fixture.results.length, 0);
});

test("hiding during recognition discards the result without issuing a duplicate stop", async () => {
  const fixture = controllerFixture();
  await fixture.controller.begin({ isGestureActive: () => true });
  fixture.controller.finish();
  assert.equal(fixture.manager.stops, 1);
  fixture.controller.cancel();
  assert.equal(fixture.manager.stops, 1);
  fixture.manager.onStop({ result: "late after hide" });
  assert.equal(fixture.results.length, 0);
  assert.equal(fixture.controller.isBusy(), false);
});

test("record page appends transcript once, preserves existing text and protects the 4000-character boundary", () => {
  const toasts = [];
  const { page } = loadPage("pages/records/index.js", async () => ({}), {
    wx: { showToast: (value) => toasts.push(value), getSystemInfoSync: () => ({ windowWidth: 375 }) }
  });
  page.onLoad();
  page.data.childId = "child";

  page.appendVoiceResult("第一段", "child");
  assert.equal(page.data.text, "第一段");
  page.appendVoiceResult("第二段", "child");
  assert.equal(page.data.text, "第一段\n第二段");
  assert.equal(toasts.at(-1).title, "已转成文字，请检查");

  page.data.text = "现".repeat(3999);
  page.appendVoiceResult("不能直接加入", "child");
  assert.equal(page.data.text, "现".repeat(3999));
  assert.equal(page.data.voiceOverflowText, "不能直接加入");
  assert.equal(page.data.voiceOverflowOpen, true);

  page.setVoiceOverflow({ detail: { value: "一" } });
  page.applyVoiceOverflow();
  assert.equal(page.data.text, "现".repeat(3999));
  assert.equal(page.data.voiceOverflowOpen, true);

  page.data.text = "现".repeat(3998);
  page.applyVoiceOverflow();
  assert.equal(page.data.text, `${"现".repeat(3998)}\n一`);
  assert.equal(page.data.voiceOverflowOpen, false);
});

test("record page ignores a transcript for another child and blocks submit while voice work is active", async () => {
  const calls = [];
  const toasts = [];
  const { page } = loadPage("pages/records/index.js", async (...args) => { calls.push(args); return {}; }, {
    wx: { showToast: (value) => toasts.push(value), getSystemInfoSync: () => ({ windowWidth: 375 }) }
  });
  page.onLoad();
  page.data.childId = "child-a";
  page.data.text = "手动内容";
  page.data.hasText = true;

  page.appendVoiceResult("另一个孩子的内容", "child-b");
  assert.equal(page.data.text, "手动内容");
  page.data.voiceBusy = true;
  await page.save();
  assert.equal(calls.length, 0);
  assert.equal(toasts.at(-1).title, "请先结束本次语音输入");
});

test("record page cancels voice work when the child context disappears", async () => {
  let cancels = 0;
  const { page } = loadPage("pages/records/index.js", async (url) => {
    assert.equal(url, "/children");
    return [];
  });
  page.voiceController = { cancel() { cancels += 1; } };
  page.data.childId = "child";

  await page.load();
  assert.equal(cancels, 1);
  assert.equal(page.data.childId, "");
});

test("record page wires hold, upward cancel threshold, release and plugin callback end to end", async () => {
  const plugin = fakePlugin();
  const toasts = [];
  const { page } = loadPage("pages/records/index.js", async () => ({}), {
    requirePlugin: () => plugin.plugin,
    wx: {
      getSystemInfoSync: () => ({ windowWidth: 375 }),
      getSetting({ success }) { success({ authSetting: { "scope.record": true } }); },
      showToast: (value) => toasts.push(value)
    }
  });
  page.onLoad();
  page.data.childId = "child";

  page.voiceTouchStart({ touches: [{ clientY: 200 }] });
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(page.data.voiceState, "holding");
  assert.equal(plugin.manager.starts.length, 1);

  page.voiceTouchMove({ touches: [{ clientY: 150 }] });
  assert.equal(page.data.voiceState, "cancel_armed");
  page.voiceTouchMove({ touches: [{ clientY: 170 }] });
  assert.equal(page.data.voiceState, "holding");
  page.voiceTouchEnd();
  assert.equal(page.data.voiceState, "recognizing");
  assert.equal(plugin.manager.stops, 1);

  plugin.manager.onStop({ result: "朗读课文第三段" });
  assert.equal(page.data.text, "朗读课文第三段");
  assert.equal(page.data.voiceState, "idle");
  assert.equal(toasts.at(-1).title, "已转成文字，请检查");
});

test("record page keeps the mic inside the compact input and declares only the approved plugin", () => {
  const root = path.resolve(__dirname, "../../apps/miniprogram");
  const markup = fs.readFileSync(path.join(root, "pages/records/index.wxml"), "utf8");
  const styles = fs.readFileSync(path.join(root, "pages/records/index.wxss"), "utf8");
  const adapter = fs.readFileSync(path.join(root, "pages/records/voice-input.js"), "utf8");
  const app = JSON.parse(fs.readFileSync(path.join(root, "app.json"), "utf8"));

  assert.match(markup, /voice-input-shell[\s\S]*voice-touch/);
  assert.match(markup, /按住录音，松开转成文字，上滑取消/);
  assert.doesNotMatch(markup, /切换语音|开始录音|停止录音/);
  assert.match(styles, /\.text-input\s*\{[^}]*height:\s*184rpx/s);
  assert.match(styles, /\.voice-touch\s*\{[^}]*width:\s*88rpx;[^}]*height:\s*88rpx/s);
  assert.deepEqual(app.plugins, { WechatSI: { version: "0.3.1", provider: "wx069ba97219f66d99" } });
  assert.doesNotMatch(adapter, /console\.|tempFilePath|setStorage|uploadFile/);
});
