const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const [mode, widthText, host = "embedded"] = process.argv.slice(2);
const width = Number(widthText);
if (!["baseline", "fixed", "show"].includes(mode) || ![320,390,430].includes(width)
    || !["embedded","standalone"].includes(host)) throw Error("invalid collector arguments");
const out = path.join("/Users/bytedance/Documents/push_kids/docs/quality/evidence/report-footer-tips-20261101",
  mode, host, String(width));
const socket = new WebSocket("ws://127.0.0.1:9612");
const pending = new Map();
let sequence = 0;
socket.onmessage = ({data}) => {
  const message = JSON.parse(data);
  pending.get(message.id)?.(message);
};
function send(method, params = {}) {
  return new Promise((resolve,reject) => {
    const id = String(++sequence);
    const timer = setTimeout(() => { pending.delete(id); reject(Error(method+" timed out")); },12000);
    pending.set(id, message => {
      clearTimeout(timer); pending.delete(id);
      message.error ? reject(Error(method+": "+message.error.message)) : resolve(message.result);
    });
    socket.send(JSON.stringify({id,method,params}));
  });
}
const call = async (functionDeclaration,args=[]) =>
  (await send("App.callFunction",{functionDeclaration,args})).result;
const setup = `function(host){
  const p=getCurrentPages().slice(-1)[0];
  if(host==='standalone')return true;
  p.loadGeneration=(p.loadGeneration||0)+1;p.historyRequest=(p.historyRequest||0)+1;
  const A=p.data.children.constructor,O=p.data.constructor;
  const copy=v=>{if(v===null||typeof v!=='object')return v;const r=Array.isArray(v)?new A():new O();
    Object.keys(v).forEach(k=>r[k]=copy(v[k]));return r;};
  return new Promise(resolve=>p.setData(copy({children:[{id:'synthetic',name:'合成孩子',active:true}],
    childId:'synthetic',childIndex:0,multiChild:false,report:{overview:{}},metrics:[],subjects:[],
    activityRows:[],activityDetailFailed:false,isEmpty:false,loading:false,error:'',
    historyExpanded:false,inventoryExpanded:true,canWrite:true}),
    ()=>wx.nextTick(()=>resolve(true))));
}`;
const fixture = `function(host,json){
  const current=getCurrentPages().slice(-1)[0],
    p=host==='embedded'?current.selectComponent('#inventory-component'):current;
  if(!p)throw Error('inventory component missing');
  const A=p.data.items.constructor,O=p.data.constructor;
  const copy=v=>{if(v===null||typeof v!=='object')return v;const r=Array.isArray(v)?new A():new O();
    Object.keys(v).forEach(k=>r[k]=copy(v[k]));return r;};
  p.generation=(p.generation||0)+1;p.showGeneration=(p.showGeneration||0)+1;
  p.subjectGeneration=(p.subjectGeneration||0)+1;
  return new Promise(resolve=>p.setData(copy(JSON.parse(json)),()=>wx.nextTick(()=>resolve(true))));
}`;
const selectors = [".inventory-page",".inventory-pagination",
  ".inventory-page-button",
  ".inventory-page-label",".subject-pager",".subject-pager .inventory-page-button",
  ".inventory-feedback",".inventory-feedback-text",".notice",".item-main",".more",".action-menu",
  ".error",".readonly"];
const query = `function(host,selectors){return new Promise(resolve=>{
  const current=getCurrentPages().slice(-1)[0],
    p=host==='embedded'?current.selectComponent('#inventory-component'):current,
    q=wx.createSelectorQuery().in(p),info=wx.getSystemInfoSync();
  selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,properties:['disabled'],
    computedStyle:['display','fontSize','lineHeight','textAlign','backgroundColor','paddingLeft',
      'paddingRight','paddingTop','paddingBottom','borderRadius','boxShadow']}));
  q.selectViewport().scrollOffset();q.exec(rows=>{
    const nodes={};selectors.forEach((s,i)=>nodes[s]=rows[i]||[]);
    resolve({nodes,scroll:rows[selectors.length],viewport:{width:info.windowWidth,
      height:info.windowHeight,screenHeight:info.screenHeight,dpr:info.pixelRatio,baseLibrary:info.SDKVersion},
      view:p.data.view,pageNumber:p.data.pageNumber,loading:p.data.loading,
      canWrite:p.data.canWrite,notice:p.data.notice});
  });
});}`;
function dataFor(view,state) {
  const entry = {knowledge_id:"synthetic-knowledge",knowledge_name:"识听并指读重复 catch、hit、kick、jump、run、throw 六个动作类英语单词",
    subject_id:"english",subject_name:"英语",review_status:"normal",
    reviewCountText:"已复习1次",lastReviewText:"上次10月31日",
    compactDateText:"建议11月3日",arrangementText:"今日已完成",can_schedule:true,state_version:1};
  return {view,reviewStatus:"normal",childId:"synthetic",subjectId:"english",
    offset:1,count:null,countLabel:"全部",views:[{id:"time",label:"按时间"},{id:"subject",label:"按科目"},{id:"count",label:"按次数"}],
    loaded:true,loading:state==="loading",saving:false,error:state==="error"?"读取失败，请重试":"",
    items:[entry],groups:[{key:"english",name:"英语",mark:"英",tone:"english",expanded:true,entries:[entry]}],
    total:42,minutes:3,budget:10,overBudget:state==="budget"?5:0,
    asOfDay:"2026-11-01",tomorrowLabel:"明天 11月2日",dayAfterLabel:"后天 11月3日",
    selectedSubjectName:"英语",subjects:[{id:"english",name:"英语",count:42},{id:"math",name:"数学",count:18}],
    subjectCursor:"synthetic-subject-cursor",subjectHasPrevious:false,subjectLoading:false,subjectError:"",
    pickerOpen:state==="subject-menu",
    pageNumber:state==="long-page"?123456789:["middle","last","loading"].includes(state)?2:1,
    nextCursor:state==="last"?null:"synthetic-next",
    canWrite:state!=="readonly",deleting:false,target:null,conflict:false,showCountInput:false,
    actionError:"",actionMenuId:state==="action-menu"?"synthetic-knowledge":"",
    actionMenuGroup:state==="action-menu"?"english":"",actionMenuAbove:false,
    notice:state==="deleted"?"条目和相关复习历史、计划已删除":
      state==="long-notice"?"已安排到 2026-11-03，复习次数不变；当天超出日常预算 10 分钟":""};
}
function audit(payload,state) {
  const errors = [], check=(ok,msg)=>{if(!ok)errors.push(msg);}, n=payload.nodes;
  const pager=n[selectors[1]].slice(-1)[0],buttons=n[selectors[2]].slice(-2),label=n[selectors[3]][0];
  check(buttons.length===2&&!!pager&&!!label,"pagination nodes absent");
  if (buttons.length===2 && label && pager) {
    const [a,b]=buttons;
    check(Math.abs(a.top-b.top)<=1,"pagination buttons on different rows");
    check(Math.abs(a.width-b.width)<=1,"pagination unequal button widths");
    check(Math.min(a.height,b.height)>=43.9,"pagination target below 44px");
    check(Math.min(parseFloat(a.fontSize),parseFloat(b.fontSize))>=14,"pagination font below 14px");
    check(Math.abs((label.left+label.right-pager.left-pager.right)/2)<=1,"page label not centered");
    check(label.left-a.right>=7.9&&b.left-label.right>=7.9,"pagination gap below 8px");
    check(buttons.every(r=>r.left>=-1&&r.right<=width+1),"pagination horizontal overflow");
    for (const r of buttons) {
      check(r.boxShadow==="none","pagination unexpected shadow");
      if(r.disabled)check(r.backgroundColor==="rgba(0, 0, 0, 0)"||r.backgroundColor==="transparent",
        "disabled pagination has nontransparent background");
    }
  }
  if(["deleted","long-notice","budget"].includes(state)) {
    const containers=n[".inventory-feedback"],texts=n[".inventory-feedback-text"];
    check(containers.length===1&&texts.length===1,"dedicated feedback nodes absent");
    for(let i=0;i<containers.length;i++) {
      const a=containers[i],t=texts[i];
      check(parseFloat(a.paddingLeft)===16&&parseFloat(a.paddingRight)===16,"feedback horizontal padding");
      check(parseFloat(a.paddingTop)===12&&parseFloat(a.paddingBottom)===12,"feedback vertical padding");
      if(t){
        check(t.left-a.left>=15.9&&a.right-t.right>=15.9,"feedback text horizontal clearance");
        check(t.top-a.top>=11.9&&a.bottom-t.bottom>=11.9,"feedback text vertical clearance");
        check(t.textAlign==="left"&&parseFloat(t.fontSize)>=14,"feedback font or alignment");
      }
      check(a.left>=-1&&a.right<=width+1,"feedback horizontal overflow");
    }
  }
  if(state==="subject-menu") {
    const [a,b]=n[".subject-pager .inventory-page-button"];
    check(!!a&&!!b,"subject pager missing");
    if(a&&b){
      check(Math.abs(a.top-b.top)<=1&&Math.abs(a.width-b.width)<=1,"subject pager row/width");
      check(b.left-a.right>=7.9&&Math.min(a.height,b.height)>=43.9,"subject pager gap/target");
    }
  }
  if(state==="readonly")check(n[".more"].length===0&&n[".readonly"].length===1,"readonly management action");
  if(state==="error")check(n[".error"].length>0,"error disappeared");
  if(state==="action-menu") {
    const r=n[".action-menu"][0];
    check(!!r,"action menu absent");
    if(r)check(r.left>=-1&&r.right<=width+1,"action menu horizontal overflow");
  }
  return errors;
}
async function capture(view,state) {
  await call(fixture,[host,JSON.stringify(dataFor(view,state))]);
  await call(`function(host,selector){return new Promise(resolve=>{
    const c=getCurrentPages().slice(-1)[0],p=host==='embedded'?c.selectComponent('#inventory-component'):c,
      q=wx.createSelectorQuery().in(p);
    q.selectAll(selector).boundingClientRect();q.selectViewport().scrollOffset();
    q.exec(([rows,s])=>{
      const r=rows?.slice(-1)[0];
      wx.pageScrollTo({scrollTop:Math.max(0,s.scrollTop+(r?r.top:0)-90),duration:0,
        complete:()=>wx.nextTick(()=>resolve(true))});
    });
  });}`,[host,["deleted","long-notice","budget"].includes(state)
    ?mode==="baseline"?".notice":".inventory-feedback":state==="subject-menu"?".filter-row":state==="action-menu"?".item":".inventory-pagination"]);
  const payload=await call(query,[host,selectors]);
  if(payload.viewport.width!==width||payload.viewport.screenHeight!=={320:568,390:844,430:932}[width])
    throw Error("viewport changed: "+JSON.stringify(payload.viewport));
  const errors=audit(payload,state);
  fs.mkdirSync(out,{recursive:true});
  const name=view+"-"+state;
  let screenshotSha256=null;
  if(!process.env.NATIVE_SKIP_SCREENSHOTS) {
    const shot=await send("App.captureScreenshot");
    const bytes=Buffer.from((typeof shot==="string"?shot:shot.data||shot.base64).replace(/^data:image\/\w+;base64,/,""),"base64");
    fs.writeFileSync(path.join(out,name+".png"),bytes);
    screenshotSha256=crypto.createHash("sha256").update(bytes).digest("hex");
  }
  fs.writeFileSync(path.join(out,name+".json"),JSON.stringify({...payload,host,state,errors,
    scope:"isolated synthetic data; real production WXML/WXSS; not physical device/cloud acceptance",
    screenshotSha256,screenshotStatus:screenshotSha256?"PASS":"NOT_RUN",
    capturedAt:new Date().toISOString()},null,2)+"\n");
  console.log(host+" "+width+" "+name+": "+(errors.join("; ")||"PASS"));
  return errors;
}
async function main(){
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error("automation handshake timeout")),12000);
    socket.onopen=()=>{clearTimeout(timer);resolve();};
    socket.onerror=()=>{clearTimeout(timer);reject(Error("automation unavailable"));};
  });
  const runtime=await call(`function(){const i=wx.getSystemInfoSync();return {
    offline:getApp().globalData.useCloud===false,synthetic:getApp().globalData.familyId==='synthetic',
    width:i.windowWidth,screenHeight:i.screenHeight};}`);
  if(!runtime.offline||!runtime.synthetic||runtime.width!==width||runtime.screenHeight!=={320:568,390:844,430:932}[width])
    throw Error("offline/viewport precondition: "+JSON.stringify(runtime));
  const url=host==="embedded"?"/pages/reports/index":"/pages/review-inventory/index?childId=synthetic";
  await send("App.callWxMethod",{method:host==="embedded"?"switchTab":"navigateTo",args:[{url}]});
  await call(setup,[host]);
  await call(`function(host){return new Promise(resolve=>wx.nextTick(()=>resolve(host==='embedded'
    ?!!getCurrentPages().slice(-1)[0].selectComponent('#inventory-component'):true)));}`,[host]);
  const cases=mode==="baseline"?[["time","first"],["subject","first"],["count","first"],["subject","deleted"],["subject","subject-menu"]]
    :["time","subject","count"].flatMap(view=>["first","middle","last","loading","long-page","action-menu"].map(state=>[view,state]))
      .concat([["subject","deleted"],["subject","long-notice"],["time","budget"],["subject","subject-menu"],["subject","readonly"],["subject","error"]]);
  let failures=0;
  for(const [view,state]of cases) failures+=(await capture(view,state)).length;
  fs.writeFileSync(path.join(out,"summary.json"),JSON.stringify({mode,host,width,cases:cases.length,failures},null,2)+"\n");
  if(mode==="fixed"&&failures)process.exitCode=1;
}
main().catch(error=>{console.error(error.message);process.exitCode=1;}).finally(()=>socket.close());
