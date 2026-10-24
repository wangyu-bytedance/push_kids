// Drives only the offline synthetic copy; native choices are made in DevTools UI.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const mode = process.argv[2], label = process.argv[3], port = Number(process.argv[4] || 9572);
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = ({ data }) => { const m = JSON.parse(data); pending.get(m.id)?.(m); };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, (m) => { pending.delete(id); clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  // Enter travel through the real record-type dropdown before observing it.
  if (mode === "actions") {
    await call("function(){const c=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');c.openFootprintActions();return true;}");
  } else if (mode !== "capture" && mode !== "inspect") throw Error("Unknown mode");
  const state = await call(`function(){const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#travel-diary'),i=wx.getSystemInfoSync();return {
    childId:c.data.childId,childName:c.data.child&&c.data.child.name,active:c.data.child&&c.data.child.active,
    hasArchivedChildren:c.data.hasArchivedChildren,canWrite:c.data.canWrite,sheet:c.data.sheet,aiEnabled:c.data.aiEnabled,
    sheetError:c.data.sheetError,nativeMenuOpen:Boolean(c.nativeMenuOpen),archivePickerOpen:Boolean(c.archivePickerOpen),
    width:i.windowWidth,screenHeight:i.screenHeight};}`);
  if (mode === "capture") {
    if (!/^[a-z0-9-]+$/.test(label || "")) throw Error("Synthetic evidence label required");
    const shot = await send("App.captureScreenshot"), bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
    const out = path.resolve("docs/quality/evidence/footprints-minimal-20261024/interactions"); fs.mkdirSync(out, { recursive: true });
    fs.writeFileSync(path.join(out, label + ".png"), bytes);
    fs.writeFileSync(path.join(out, label + ".json"), JSON.stringify({ ...state, capturedAt: new Date().toISOString(), screenshot: label + ".png", screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  }
  console.log(JSON.stringify(state)); socket.close();
}
main().catch((error) => { console.error(error.message); socket.close(); process.exitCode = 1; });
