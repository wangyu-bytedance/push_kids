const fs=require('node:fs');
const ws=new WebSocket('ws://127.0.0.1:9420');const pending=new Map();let seq=0;
ws.onerror=()=>{console.log('CONNECTION_FAILED');process.exitCode=1;};
ws.onmessage=e=>{const m=JSON.parse(e.data);const cb=pending.get(m.id);if(cb){pending.delete(m.id);cb(m);}};
function send(method,params){return new Promise((resolve,reject)=>{const id=String(++seq),timer=setTimeout(()=>reject(Error('timeout')),15000);pending.set(id,m=>{clearTimeout(timer);m.error?reject(Error(method+': '+JSON.stringify(m.error))):resolve(m.result);});ws.send(JSON.stringify({id,method,params}));});}
ws.onopen=async()=>{try{
 await send('App.callWxMethod',{method:'switchTab',args:[{url:'/pages/settings/index'}]});
 const results=[];
 for(const state of ['content','catalog','form','error','pending','readonly','no-art','long-name']){
  await send('App.callFunction',{functionDeclaration:`function(state){const p=getCurrentPages().slice(-1)[0];if(!p.__settingsOriginal)p.__settingsOriginal={data:JSON.parse(JSON.stringify(p.data)),load:p.load};p.load=async function(){};
   const A=p.data.children.constructor,O=p.data.constructor;const copy=v=>{if(v===null||typeof v!=='object')return v;const r=Array.isArray(v)?new A():new O();Object.keys(v).forEach(k=>r[k]=copy(v[k]));return r;};
   const data={loading:false,error:'',canWrite:state!=='readonly',children:[{id:'synthetic',name:'示例',avatar:'示'}],childId:'synthetic',childIndex:0,showChildSheet:false,showCatalog:false,showSchedule:false,baseLearning:[{name:'数学',selected:true},{name:'语文',selected:true},{name:'英语',selected:false}],addedLearning:[],addedActivities:[{id:'synthetic-activity',name:'游泳',scheduleLabel:'每周六 · 15:00–16:00',iconClass:'ico-clock-pri'}],travelArrangements:[],dailyTasks:[{id:'synthetic-task',name:state==='long-name'?'这是用于验证三十字符任务名称在窄屏里完整换行显示的测试长名称':'阅读',target_minutes:20}],showDailyTaskForm:['form','error','pending'].includes(state),showDailyTaskCatalog:state==='catalog',dailyTaskName:'阅读',dailyTaskMinutes:'20',dailyTaskId:'',dailyTaskError:state==='error'?'保存失败，输入已保留，请重试':'',savingDailyTask:state==='pending',deletingDailyTask:false,learningArtFailed:state==='no-art',activityArtFailed:state==='no-art',dailyArtFailed:state==='no-art',travelArtFailed:state==='no-art'};
   return new Promise(resolve=>p.setData(copy(data),()=>{wx.pageScrollTo({scrollTop:0,duration:0});resolve(true);}));}`,args:[state]});
  await new Promise(r=>setTimeout(r,300));
  const r=await send('App.callFunction',{functionDeclaration:`function(){return new Promise(resolve=>{const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);const selectors=['.page','.subject-action','.daily-task-setting-row','.daily-task-setting-copy','.daily-task-candidate','.daily-task-form .pk-input','.daily-task-form-actions .btn','.pk-sheet','.settings-card-art'];selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true}));q.exec(groups=>{const i=wx.getSystemInfoSync();resolve({width:i.windowWidth,screenHeight:i.screenHeight,nodes:groups});});});}`,args:[]});
  const payload={state,...r.result}; const errors=[];
  for(const group of payload.nodes||[])for(const n of group||[])if(n.left < -1 || n.right >payload.width+1)errors.push('horizontal overflow');
  for(const index of [1,2,4,5,6])for(const n of payload.nodes[index]||[])if(n.width<43 || n.height<43)errors.push('touch target below44');
  if(!(payload.nodes[0]||[]).length)errors.push('page missing');
  if(!(payload.nodes[2]||[]).length)errors.push('task missing');
  if(state==='catalog'&&(payload.nodes[4]||[]).length!==4)errors.push('catalog missing');
  if(['form','error','pending'].includes(state)&&(payload.nodes[5]||[]).length!==2)errors.push('form missing');
  if(['form','error','pending'].includes(state)&&(payload.nodes[6]||[]).length!==2)errors.push('form actions missing');
  payload.errors=errors;fs.mkdirSync('docs/quality/evidence/settings-consistency-20261013',{recursive:true});fs.writeFileSync('docs/quality/evidence/settings-consistency-20261013/'+state+'-'+payload.width+'.json',JSON.stringify(payload,null,2));
  results.push({state,width:payload.width,errors});
 }
 console.log(JSON.stringify(results));if(results.some(r=>r.errors.length))process.exitCode=1;
}catch(e){console.log(e.message);process.exitCode=1;}finally{
 await send('App.callFunction',{functionDeclaration:`async function(){const p=getCurrentPages().slice(-1)[0],o=p.__settingsOriginal;if(o){p.load=o.load;delete p.__settingsOriginal;await p.load();p.setData({showDailyTaskForm:false,showDailyTaskCatalog:false,showChildSheet:false,learningArtFailed:false,activityArtFailed:false,travelArtFailed:false,dailyArtFailed:false});}return true;}`,args:[]}).catch(()=>{});ws.close();}};
