// The authenticated wxcloud transport reads authoritative fields omitted by version:list.
const fs = require("node:fs");
const path = require("node:path");

async function state(env, service) {
  const executable = process.env.PATH.split(path.delimiter)
    .map(dir => path.join(dir, "wxcloud")).find(file => fs.existsSync(file));
  if (!executable) throw Error("wxcloud unavailable");
  const packageDir = path.resolve(fs.realpathSync(executable), "../..");
  const { DescribeCloudBaseRunServer, DescribeCloudBaseRunServers } = require(path.join(packageDir, "lib/api"));
  require(path.join(packageDir, "lib/api/common")).setApiCommonParameters({ region: "ap-shanghai" });
  const params = { EnvId: env, ServerName: service, Offset: 0, Limit: 100 };
  const [detail, overview] = await Promise.all([
    DescribeCloudBaseRunServer(params), DescribeCloudBaseRunServers(params),
  ]);
  const target = overview.CloudBaseRunServerSet.find(item => item.ServerName === service);
  const { ServerName, VersionItems, TotalCount } = detail;
  if (ServerName !== service || !target || !Array.isArray(VersionItems) ||
      TotalCount !== VersionItems.length) throw Error("Invalid cloud state");
  return {
    status: target.Status, public: target.IsPublic,
    versions: VersionItems.map(version => ({
      version: version.VersionName, status: version.Status, flow: version.FlowRatio,
      replicas: version.CurrentReplicas, remark: /^pk-[0-9a-z-]+$/.test(version.Remark) ? version.Remark : "",
    })),
  };
}

async function smoke(port, env, service) {
  const socket = new WebSocket("ws://127.0.0.1:" + port);
  try {
    return await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(Error("Native smoke timed out")), 30000);
      const done = (callback, value) => { clearTimeout(timer); callback(value); };
      socket.onerror = () => done(reject, Error("Native automation unavailable"));
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.id !== "readonly-release") return;
        if (Array.isArray(message.result?.result)) done(resolve, message.result.result);
        else done(reject, Error("Invalid native smoke response"));
      };
      socket.onopen = () => socket.send(JSON.stringify({
        id: "readonly-release", method: "App.callFunction",
        params: { args: [env, service], functionDeclaration: `async function(env,service){
          const data=getApp().globalData;
          if(!data.useCloud||data.cloudEnv!==env||data.cloudService!==service)return null;
          const get=path=>new Promise(resolve=>wx.cloud.callContainer({
            config:{env},path,method:'GET',header:{'X-WX-SERVICE':service},
            success:resolve,fail:()=>resolve({statusCode:0}),
          }));
          const paths=[['live','/health/live'],['ready','/health/ready'],
            ['me','/api/v1/me'],['children','/api/v1/children']];
          const responses=await Promise.all(paths.map(([,path])=>get(path)));
          const rows=paths.map(([route],i)=>({route,status:responses[i].statusCode}));
          const profiles=responses[3].data;
          const child=Array.isArray(profiles)&&profiles[0];
          if(!child||!child.id)return rows;
          const base='/api/v1/children/'+encodeURIComponent(child.id);
          const day=new Date(Date.now()+8*3600000).toISOString().slice(0,10);
          const childrenPaths=[['today','/dashboard'],['calendar','/schedule?day='+day],['report','/report?days=7']];
          return rows.concat(await Promise.all(childrenPaths.map(async([route,suffix])=>({
            route,status:(await get(base+suffix)).statusCode,
          }))));
        }` },
      }));
    });
  } finally {
    socket.close();
  }
}

const [mode, ...args] = process.argv.slice(2);
Promise.resolve().then(() => (mode === "state" ? state(...args) : smoke(...args)))
  .then(result => process.stdout.write(JSON.stringify(result) + "\n"))
  .catch(() => { process.exitCode = 1; });
