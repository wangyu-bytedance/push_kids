// Synthetic native-layout evidence only. Never invokes WeChat authorization or a provider.
const fs = require("node:fs");
const path = require("node:path");
const STATES = ["settings-off", "settings-enabled", "settings-cooldown", "settings-stopped",
  "settings-pending", "settings-loading", "settings-error", "settings-unavailable",
  "settings-partial", "settings-forbidden", "settings-empty", "settings-saving"];
const SELECTORS = [".page", ".auto-card", ".noti-row", ".noti-row .grow", ".noti-switch",
  ".grant-link", ".notice-hero .btn", ".auto-switch", ".icon-btn",
  ".auto-copy", ".r-s", ".noti-state .pill", ".n-txt", ".hero-note", ".help"];
const GUIDE_SELECTORS = [".renewal-sheet", ".renewal-body", ".renewal-actions",
  ".renewal-primary", ".renewal-secondary", ".renewal-title", ".renewal-copy"];
const FIXTURE = `function(state) {
  const p=getCurrentPages().slice(-1)[0];
  p.load=()=>Promise.resolve();
  if(state==='guide'||state==='today-quiet') {
    p.setData({loading:false,error:'',canWrite:true,renewalGuideSaving:false});
    p.setRenewalGuide(state==='guide');
    return true;
  }
  const labels=['复习提醒','日程提醒','家人加入申请'];
  const types=['review_digest','schedule_reminder','member_application'];
  const items=labels.map((label,i)=>({type:types[i],label,
    description:['每天提醒今天需要复习的内容','提前提醒你已安排的日程','有家人申请加入时通知管理员'][i],
    enabled:true,managersOnly:i===2,statusText:'需先明确同意当前模板',statusTone:'neutral',needsGrant:true}));
  let data={loading:false,error:'',supported:true,channelAvailable:true,channelReason:'',items,
    grantCount:3,granting:false,togglingType:'',lastSentLabel:'',deliveries:[],deliveriesError:'',
    autoEnabled:state!=='settings-off',autoSaving:false,heroTitle:'提醒需要补充次数',heroReady:false};
  if(state==='settings-enabled') {data.heroTitle='提醒已有可用次数';data.heroReady=true;data.grantCount=0;
    items.forEach(x=>Object.assign(x,{statusText:'可发送 1 次',statusTone:'suc',needsGrant:false}));}
  if(state==='settings-cooldown')items.forEach(x=>x.statusText='还需完成 4 条复习');
  if(state==='settings-stopped')items.forEach(x=>Object.assign(x,{statusText:'微信已记住拒绝',needsWxSettings:true}));
  if(state==='settings-pending') {data.heroTitle='提醒次数待确认';data.grantCount=0;items.forEach(x=>{x.statusText='次数待确认 · 登记待恢复';x.needsGrant=false;});}
  if(state==='settings-loading')Object.assign(data,{items:[],loading:true,grantCount:0});
  if(state==='settings-error')data.error='无法连接服务，请检查网络';
  if(state==='settings-unavailable')Object.assign(data,{channelAvailable:false,channelReason:'提醒服务暂不可用'});
  if(state==='settings-partial'){data.items=items.slice(0,2);data.grantCount=1;items[0].statusText='可发送 1 次';items[0].statusTone='suc';items[0].needsGrant=false;items[1].statusText='还需完成 4 条复习';}
  if(state==='settings-forbidden')Object.assign(data,{items:[],error:'当前家庭成员身份已失效',deliveries:[],grantCount:0,channelAvailable:false});
  if(state==='settings-empty'){Object.assign(data,{grantCount:0,heroTitle:'提醒尚未开启'});items.forEach(x=>Object.assign(x,{enabled:false,needsGrant:false,statusText:'已关闭'}));}
  if(state==='settings-saving')data.autoSaving=true;
  p.setData(data);return true;
}`;
const QUERY = `function(selectors,guide) {return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0],owner=guide?p.selectComponent('#renewal-guide'):p;
  const q=wx.createSelectorQuery().in(owner);
  selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize']}));
  q.exec(groups=>{const i=wx.getSystemInfoSync(),nodes={};selectors.forEach((s,k)=>nodes[s]=(groups[k]||[]).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height,fontSize:n.fontSize})));
    resolve({viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,fontScale:i.fontSizeSetting,baseLibrary:i.SDKVersion},nodes});});});}`;
function audit(capture) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  const {nodes, viewport} = capture;
  check(viewport.width === capture.expectedWidth, "incorrect native viewport");
  const controlSelectors = capture.state === "guide" ? [".renewal-primary", ".renewal-secondary"]
    : [".noti-switch", ".grant-link", ".notice-hero .btn", ".auto-switch", ".icon-btn"];
  for (const group of Object.values(nodes)) for (const node of group) {
    check(node.left >= -1 && node.right <= viewport.width + 1, "node outside horizontal viewport");
    if (node.fontSize && group !== nodes[".icon-btn"])
      check(parseFloat(node.fontSize) >= 14, "text below 14px");
  }
  for (const selector of controlSelectors) for (const node of nodes[selector] || []) {
    check(node.width >= 43 && node.height >= 43, `${selector}: target below 44px`);
  }
  if (capture.state === "guide") {
    const sheet=nodes[".renewal-sheet"]?.[0], actions=nodes[".renewal-actions"]?.[0];
    check(!!sheet && !!actions, "guide missing");
    // Today uses custom navigation: native rectangles cover the full screen including its header.
    if(sheet&&actions)check(sheet.top>=-1 && actions.bottom<=viewport.screenHeight+1,"guide actions outside native viewport");
    const primary=nodes[".renewal-primary"]?.[0],secondary=nodes[".renewal-secondary"]?.[0];
    if(primary&&secondary)check(secondary.top-primary.bottom>=9,"guide action gap below 10px");
  } else if(capture.state.startsWith("settings-")) {
    const copies=nodes[".noti-row .grow"]||[], switches=nodes[".noti-switch"]||[];
    copies.forEach((copy,i)=>{if(switches[i])check(copy.right<=switches[i].left-7,"text overlaps switch or lacks clearance");});
  }
  return errors;
}
async function main() {
  const [widthText, directory, onlyState] = process.argv.slice(2);
  const width=Number(widthText);
  if(![320,390,430].includes(width)||!directory)throw Error("usage: <320|390|430> <output-directory> [state]");
  const socket=new WebSocket(process.env.MINIPROGRAM_AUTOMATION_WS||"ws://127.0.0.1:9422");
  const pending=new Map();let seq=0;
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const id=String(++seq),timer=setTimeout(()=>{pending.delete(id);reject(Error(`${method} timed out`));},12000);
    pending.set(id,m=>{clearTimeout(timer);m.error?reject(Error(`${method}: ${JSON.stringify(m.error)}`)):resolve(m.result);});
    socket.send(JSON.stringify({id,method,params}));
  });
  socket.onmessage=e=>{const m=JSON.parse(e.data),cb=pending.get(m.id);if(cb){pending.delete(m.id);cb(m);}};
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  const call=(fn,args=[])=>send("App.callFunction",{functionDeclaration:fn,args});
  try {
    const safe=await call("function(){return getApp().globalData.useCloud===false;}");
    if(!safe.result)throw Error("requires isolated useCloud=false project");
    fs.mkdirSync(directory,{recursive:true});
    for(const state of onlyState?[onlyState]:[...STATES,"guide","today-quiet"]){
      const surface=state.startsWith("settings-")?"notifications":"today";
      const page=await send("App.getCurrentPage");
      if(page.path!==`pages/${surface}/index`){
        await send("App.callWxMethod",{method:surface==="today"?"switchTab":"navigateTo",args:[{url:`/pages/${surface}/index`}]});
        await new Promise(r=>setTimeout(r,400));
      }
      await call(FIXTURE,[state]);
      await new Promise(r=>setTimeout(r,200));
      const guide=state==="guide";
      const capture={...(await call(QUERY,[guide?GUIDE_SELECTORS:SELECTORS,guide])).result,
        expectedWidth:width,state,fixture:"synthetic native page; no grant/provider invocation"};
      const stem=path.join(directory,`${state}-${width}`);
      fs.writeFileSync(stem+".json",JSON.stringify(capture,null,2)+"\n");
      try {
        const shot=await send("App.screenshot");
        fs.writeFileSync(stem+".png",Buffer.from((shot.data||shot.base64).replace(/^data:image\/\w+;base64,/,""),"base64"));
      } catch { capture.screenshot="NOT_RUN: automation screenshot unavailable; CUA samples separate";
        fs.writeFileSync(stem+".json",JSON.stringify(capture,null,2)+"\n"); }
      const errors=audit(capture);
      if(errors.length)throw Error(`${state}: ${errors.join("; ")}`);
      console.log(`NATIVE_RENEWAL_GEOMETRY_VALID ${state} ${width}px`);
    }
  } finally { socket.close(); }
}
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
module.exports={audit};
