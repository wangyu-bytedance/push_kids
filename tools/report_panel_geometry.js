#!/usr/bin/env node
// Synthetic UI fixtures only. Persist rectangles, never family content or identifiers.
const fs = require("node:fs");
const path = require("node:path");
const { audit: inventoryAudit } = require("./review_inventory_geometry");
const inventorySelectors = [".inventory-page", ".filter-row", ".segment", ".filter-trigger", ".filter-panel", ".filter-option", ".more", ".item-main", ".item-title", ".item-meta", ".action-menu", ".group-toggle"];
const pageSelectors = ["#report-history", "#report-edit-plan", ".history-toggle", ".disclosure-footer", ".h-status-choice", ".s-filter", ".h-record-row", ".disclosure-action", ".disclosure-heading"];

async function connect() {
  const socket = new WebSocket(process.env.MINIPROGRAM_AUTOMATION_WS || "ws://127.0.0.1:9420");
  let id = 0;
  const pending = new Map();
  socket.onmessage = e => { const m = JSON.parse(e.data); pending.get(m.id)?.(m); };
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const key = String(++id);
    const timer = setTimeout(() => { pending.delete(key); reject(Error(`${method} timed out`)); }, 12000);
    pending.set(key, m => { clearTimeout(timer); pending.delete(key); if (m.error) reject(Error(JSON.stringify(m.error))); else resolve(m.result); });
    socket.send(JSON.stringify({ id: key, method, params }));
  });
  return { socket, send };
}

const SETUP = `function(state) {
 const p=getCurrentPages().slice(-1)[0];
 if(!p.__panelOriginal) p.__panelOriginal={data:JSON.parse(JSON.stringify(p.data)),load:p.load};
 const nativeArray=p.data.children.constructor,nativeObject=p.data.constructor;
 const copy=value=>{if(value===null||typeof value!=='object')return value;const result=Array.isArray(value)?new nativeArray():new nativeObject();Object.keys(value).forEach(key=>result[key]=copy(value[key]));return result;};
 const setData=(data,callback)=>p.setData(copy(data),callback);
 p.load=async function(){};p.loadId=(p.loadId||0)+1;p.historyRequest=(p.historyRequest||0)+1;
 if(p.timer)clearTimeout(p.timer);
 const history=state==='history'||state==='both'||state==='pending'||state==='error'||state==='empty';
 const plan=!['collapsed','history','pending','error','empty'].includes(state);
 const row={rowKey:'fixture-record',submission_id:'fixture',isPending:false,showDay:true,dayText:'10月12日 · 昨天',mark:'语',markClass:'chinese',label:'语文 · 用于检查长中文标题换行与相邻按钮间距的示例记录',summaryPreview:'课文朗读、生字与词语练习，长内容应在当前容器内自然换行。',source:'manual',sourceLabel:'文字录入',knowledgeLabel:'3个知识点',state:'confirmed',stateLabel:'已确认',stateTone:'success'};
 if(state==='pending')Object.assign(row,{isPending:true,state:'pending_confirmation',stateLabel:'等待确认',stateTone:'attention',learnedText:'10月12日'});
 return new Promise(resolve=>setData({children:[{id:'fixture-child',name:'示例孩子',avatar:'示'}],childId:'fixture-child',childIndex:0,multiChild:false,report:{overview:{}},isEmpty:false,loading:false,error:'',metrics:[],subjects:[{id:'fixture-subject',name:'语文',width:80,countText:'12次'}],activityRows:[],rangeLabel:'近30天',historyExpanded:history,inventoryExpanded:plan,historyLoading:false,historyError:state==='error'?'测试读取失败':'',historyItems:state==='empty'?[]:[row],historyPage:1,historyNext:null,historyView:state==='pending'?'pending':'confirmed',pendingCount:2,canWrite:true,filterOpen:false,hasFilters:false,searchText:''},()=>resolve(true)));
}`;
const PLAN = `function(state) {
 const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#inventory-component');if(!c)return false;
 const nativeArray=c.data.items.constructor,nativeObject=c.data.constructor;
 const copy=value=>{if(value===null||typeof value!=='object')return value;const result=Array.isArray(value)?new nativeArray():new nativeObject();Object.keys(value).forEach(key=>result[key]=copy(value[key]));return result;};
 const setData=(data,callback)=>c.setData(copy(data),callback);
 c.generation=(c.generation||0)+1;c.showGeneration=(c.showGeneration||0)+1;c.subjectGeneration=(c.subjectGeneration||0)+1;
 const entry={knowledge_id:'fixture-knowledge',knowledge_name:'用于验证长中文标题不会遮挡调整按钮的课文朗读与生字书写知识条目',reviewCountText:'已复习2次',lastReviewText:'最近10月11日',compactDateText:'建议10月14日',arrangementText:'尚未手动调整',can_schedule:true};
 const view=state.startsWith('subject')?'subject':state.startsWith('count')?'count':'time';
 return new Promise(resolve=>setData({view,offset:1,loaded:true,loading:false,error:'',items:state==='plan-empty'?[]:[entry],groups:state==='plan-empty'?[]:[{key:'fixture-group',name:'语文',mark:'语',tone:'chinese',expanded:true,entries:[entry]}],total:1,minutes:3,canWrite:state!=='readonly',tomorrowLabel:'明天 · 10/14',dayAfterLabel:'后天 · 10/15',pickerOpen:state.endsWith('filter'),subjects:[{id:'fixture-subject',name:'语文',count:1}],subjectId:'fixture-subject',selectedSubjectName:'语文',count:null,countLabel:'全部',actionMenuId:'',actionMenuGroup:'',actionMenuAbove:false,notice:'',saving:false},()=>resolve(true)));
}`;
const QUERY = `function(pageSelectors,inventorySelectors) {return new Promise(resolve=>{
 const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#inventory-component');
 const query=(owner,selectors)=>new Promise(done=>{const q=owner.createSelectorQuery();selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true}));q.exec(groups=>done(groups.map(g=>(g||[]).map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height})))));});
 Promise.all([query(p,pageSelectors),c?query(c,inventorySelectors):null]).then(([nodes,inventory])=>{const i=wx.getSystemInfoSync();resolve({viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting},nodes,inventory,view:c&&c.data.view});});
});}`;

function audit(payload, width) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  check(Math.abs(payload.viewport.width - width) <= 1, "viewport width mismatch");
  check(payload.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport height mismatch");
  check(payload.nodes[0].length === 1 && payload.nodes[1].length === 1 && payload.nodes[2].length === 2, "required report nodes missing");
  const historyOpen=["history","both","error","empty","pending"].includes(payload.state);
  const planOpen=!["collapsed","history","error","empty","pending"].includes(payload.state);
  check(payload.nodes[3].length === Number(historyOpen)+Number(planOpen), "footer mounting mismatch");
  check(payload.nodes[4].length === (historyOpen?3:0), "history status tabs missing");
  check(Boolean(payload.inventory) === planOpen, "plan mounting mismatch");
  for (const nodes of payload.nodes) for (const r of nodes) check(r.left >= -1 && r.right <= width + 1, "page node outside viewport");
  for (const index of [2, 3, 4, 5, 6]) for (const r of payload.nodes[index]) check(r.height >= 44 && r.width >= 44, "target below 44px");
  const [history, plan] = payload.nodes;
  if (history[0] && plan[0]) check(history[0].bottom <= plan[0].top + 1, "sections overlap");
  const actions = payload.nodes[7], headings = payload.nodes[8];
  headings.forEach((r, i) => check(r.right + 4 <= actions[i]?.left, "title/action overlap"));
  if (payload.inventory) {
    if (payload.state !== "readonly" && payload.state !== "plan-empty") errors.push(...inventoryAudit({view:payload.view,viewport:payload.viewport,nodes:payload.inventory},width));
    else for (const group of payload.inventory) for (const r of group) check(r.left >= -1 && r.right <= width + 1, "readonly/empty outside viewport");
  }
  return errors;
}

async function main() {
  const [mode, widthText, out] = process.argv.slice(2);
  if (mode === "audit") {
    for (const file of process.argv.slice(3)) { const p=JSON.parse(fs.readFileSync(file)); const errors=audit(p,p.expectedWidth); if(errors.length)throw Error(errors.join("; ")); }
    return;
  }
  if (mode !== "capture" || !out) throw Error("usage: capture <width> <output-directory> | audit <json>...");
  const width = Number(widthText), { socket, send } = await connect();
  try {
    const current = await send("App.getCurrentPage");
    if (current.path !== "pages/reports/index") await send("App.callWxMethod",{method:"switchTab",args:[{url:"/pages/reports/index"}]});
    await new Promise(resolve=>setTimeout(resolve,800));
    const states=["collapsed","history","plan","both","subject-filter","count-filter","menu","readonly","error","empty","pending","plan-empty"];
    fs.mkdirSync(out,{recursive:true});
    for (const state of states) {
      await send("App.callFunction",{functionDeclaration:SETUP,args:[state]});
      await new Promise(resolve=>setTimeout(resolve,250));
      await send("App.callFunction",{functionDeclaration:PLAN,args:[state]});
      await new Promise(resolve=>setTimeout(resolve,200));
      if (state === "menu") {
        await send("App.callFunction",{functionDeclaration:"function(){const p=getCurrentPages().slice(-1)[0];return new Promise(resolve=>wx.pageScrollTo({selector:'#report-edit-plan',offsetTop:-140,duration:0,success:resolve}));}",args:[]});
        await new Promise(resolve=>setTimeout(resolve,150));
        await send("App.callFunction",{functionDeclaration:"function(){return getCurrentPages().slice(-1)[0].selectComponent('#inventory-component').openActions({currentTarget:{dataset:{id:'fixture-knowledge'}}});}",args:[]});
        await new Promise(resolve=>setTimeout(resolve,250));
      }
      const result=await send("App.callFunction",{functionDeclaration:QUERY,args:[pageSelectors,inventorySelectors]});
      const payload={...result.result,state,expectedWidth:width,fixture:"synthetic"};
      fs.writeFileSync(path.join(out,`${state}-${width}.json`),JSON.stringify(payload,null,2)+"\n");
      const errors=audit(payload,width);if(errors.length)throw Error(`${state}: ${errors.join("; ")}`);
      console.log(`REPORT_PANEL_GEOMETRY_VALID ${state} ${width}px`);
      if(process.env.REPORT_PANEL_PREVIEW_STATE===state){
        await send("App.callFunction",{functionDeclaration:"function(state){wx.pageScrollTo({selector:state==='history'?'#report-history':'#report-edit-plan',offsetTop:-60,duration:0});return true;}",args:[state]});
        await new Promise(resolve=>setTimeout(resolve,15000));
      }
    }
  } finally {
    await send("App.callFunction",{functionDeclaration:"function(){const p=getCurrentPages().slice(-1)[0],o=p.__panelOriginal;if(o){const A=p.data.children.constructor,O=p.data.constructor;const copy=v=>{if(v===null||typeof v!=='object')return v;const r=Array.isArray(v)?new A():new O();Object.keys(v).forEach(k=>r[k]=copy(v[k]));return r;};p.load=o.load;p.setData(copy(o.data));delete p.__panelOriginal;}return true;}",args:[]}).catch(()=>{});
    socket.close();
  }
}
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
module.exports={audit};
