// Use the official SDK when a code-upload key has been configured.
const fs = require("node:fs");
const path = require("node:path");

async function main() {
  const [action, appid, projectPath, info, qr, version, desc] = process.argv.slice(2);
  const key = fs.realpathSync(process.env.WECHAT_MINIPROGRAM_CI_KEY_PATH);
  const root = path.resolve(__dirname, "../..");
  if (key === root || key.startsWith(root + path.sep) || !fs.statSync(key).isFile()) {
    throw Error("Code-upload key must be stored outside the workspace");
  }
  const ci = require("miniprogram-ci");
  const project = new ci.Project({ appid, type: "miniProgram", projectPath, privateKeyPath: key });
  const options = { project, setting: { useProjectConfig: true }, onProgressUpdate() {} };
  const result = action === "preview"
    ? await ci.preview({ ...options, qrcodeFormat: "image", qrcodeOutputDest: qr })
    : await ci.upload({ ...options, version, desc });
  const total = result.subPackageInfo?.find(item => item.name === "__FULL__")?.size;
  if (!Number.isSafeInteger(total) || total < 1) throw Error("Official package size unavailable");
  fs.writeFileSync(info, JSON.stringify({ size: { total } }), { mode: 0o600 });
}

main().catch(() => { process.exitCode = 1; });
