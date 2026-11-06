// Native geometry in the task-owned offline copy. No production transport or business writes.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9631);
const screenshot = process.argv.includes("--screenshots");
const copyCleanup = process.argv.includes("--copy-cleanup");
const onlyHost = process.argv.find((value) => value.startsWith("--host="))?.split("=")[1];
const output = path.resolve(process.argv.find((value) => value.startsWith("--output="))?.slice(9)
  || (copyCleanup ? "docs/quality/evidence/workday-copy-20261105/native" : "docs/quality/evidence/china-workday-20261105/native"));
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = (event) => {
  const message = JSON.parse(event.data), handler = pending.get(message.id);
  if (handler) { pending.delete(message.id); handler(message); }
};
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => {
      pending.delete(id); reject(Error(`${method} timed out`));
    }, 8000);
    pending.set(id, (message) => {
      clearTimeout(timer); message.error ? reject(Error(JSON.stringify(message.error))) : resolve(message.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const fixture = `function(host,state){
  const p=getCurrentPages().slice(-1)[0],a=getApp();a.gradeConfirmation=null;
  p.setData({loading:false,error:'',gradeConfirmationVisible:false,gradeConfirmation:null,
    children:[{id:'synthetic',name:'合成孩子',label:'合成孩子',avatar:'合',active:true}],
    childId:'synthetic',childIndex:0,canWrite:true,saving:false,eventError:'',workdayWarning:''});
  if(host==='settings'){
    let schedule={id:'synthetic-schedule',workday_only:true,time_slots:[],start_time:'18:00:00',end_time:'19:00:00'};
    if(state==='weekly'||state==='perday')schedule={id:'synthetic-schedule',workday_only:false,time_slots:[
      {weekday:1,start_time:'18:00',end_time:'19:00'},
      {weekday:3,start_time:state==='perday'?'18:30':'18:00',end_time:state==='perday'?'19:30':'19:00'}]};
    p.setData({addedActivities:[{id:'synthetic-subject',name:'英语辅导课',schedule}]});
    p.openActivitySchedule({currentTarget:{dataset:{index:0}}});
    if(state==='flexible')p.chooseScheduleMode({currentTarget:{dataset:{mode:'flexible'}}});
    if(state==='readonly')p.setData({canWrite:false});
    if(state==='saving')p.setData({savingSchedule:true});
    if(state==='error')p.setData({scheduleError:'保存失败，请稍后重试。已保留你的输入。'});
    if(state==='coverage')p.setData({workdayWarning:'工作日数据待更新：当前仅覆盖至2026年，超出范围的安排暂不显示，也不会发送提醒。'});
  }else{
    p.setData({selectedDay:'2026-01-04',items:[{id:'synthetic-event',source:'calendar',name:'阅读时间',kind:'other',
      day:'2026-01-04',event_date:'2026-01-01',start_time:'18:00',end_time:'19:00',repeat_weekly:false,workday_only:true}]});
    p.openEvent({currentTarget:{dataset:{id:'synthetic-event'}}});
    if(state==='once'||state==='weekly')p.chooseRepeatMode({currentTarget:{dataset:{mode:state}}});
    if(state==='create')p.setData({editingId:''});
    if(state==='readonly')p.setData({canWrite:false});
    if(state==='saving')p.setData({saving:true});
    if(state==='error')p.setData({eventError:'保存失败，请稍后重试。已保留你的输入。'});
    if(state==='coverage')p.setData({workdayWarning:'工作日数据待更新：当前仅覆盖至2026年，超出范围的安排暂不显示，也不会发送提醒。'});
  }
  return true;
}`;
const copyFixture = `function(host,state){
  const p=getCurrentPages().slice(-1)[0],a=getApp();a.gradeConfirmation=null;
  const apply=value=>host==='today'?p.applyGeometryFixture(JSON.stringify(value)):p.applyWorkdayFixture(JSON.stringify(value));
  apply({loading:false,error:'',gradeConfirmationVisible:false,gradeConfirmation:null,
    children:[{id:'synthetic',name:'合成孩子',label:'合成孩子',avatar:'合',active:true}],
    childId:'synthetic',childIndex:0,canWrite:true,saving:false,eventError:'',workdayWarning:'',
    showChildSheet:false});
  const warning={code:'workday_calendar_coverage_missing',coverage_end:'2026-12-31'};
  if(host==='settings'){
    apply({addedActivities:[{id:'synthetic-subject',name:'英语辅导课',schedule:{
      id:'synthetic-schedule',workday_only:true,time_slots:[],start_time:'18:00:00',end_time:'19:00:00'}}]});
    p.openActivitySchedule({currentTarget:{dataset:{index:0}}});
  }else if(host==='calendar'){
    apply({selectedDay:'2027-01-04',dayTitle:'1 月 4 日 · 星期一',weekEmpty:false,
      workdayWarning:state.includes('coverage')?'工作日安排待更新':'',showEditor:false,
      items:state==='partial-coverage'?[{id:'synthetic-event',name:'游泳',kind:'activity',source:'calendar',
        start_time:'16:00',end_time:'17:00',kind_label:'自主活动',time_text:'16:00–17:00',conflict_lines:[]}]:[],
      itemCount:state==='partial-coverage'?1:0,conflictCount:0});
    if(state==='create'){
      p.openCreate();p.chooseRepeatMode({currentTarget:{dataset:{mode:'workday'}}});
      apply({eventName:'阅读时间'});
    }else if(state==='edit'){
      apply({items:[{id:'synthetic-event',source:'calendar',name:'阅读时间',kind:'other',
        day:'2027-01-04',event_date:'2026-11-05',start_time:'18:00',end_time:'19:00',
        repeat_weekly:false,workday_only:true}]});
      p.openEvent({currentTarget:{dataset:{id:'synthetic-event'}}});
    }
  }else{
    const items=state==='partial-coverage'?[{id:'synthetic-activity',name:'游泳',kind:'activity',
      start_time:'16:00',end_time:'17:00',time_text:'16:00–17:00',kind_label:'自主活动',past:false}]:[];
    apply({dashboard:{day:'2027-01-04',todo_count:0,pending_confirmation_count:0,analyzing_count:0,
      failed_count:0,show_guide:false,schedule_items:items,optional_activity_suggestions:[],
      activity_count:items.length,workday_calendar_warning:warning,daily_tasks:{total_count:0},
      daily_summary:{record_count:0}},dayLabel:'1 月 4 日 星期一',stablePlan:true,
      planCompleted:false,hero:{total:0,required:0,note:''},sections:{review:false,daily:false,learning:false,activity:true},
      sectionMeta:{review:'今天 0 项',daily:'还未设置',learning:'已确认 0 条',activity:'工作日安排待更新'}});
  }
  return true;
}`;
const geometry = `function(){return new Promise(resolve=>{
  const p=getCurrentPages().slice(-1)[0],i=wx.getWindowInfo(),q=wx.createSelectorQuery().in(p);
  const selectors=['.pk-sheet','.sheet-head','.sheet-body','.sheet-foot','.schedule-mode','.repeat-mode',
    '.schedule-mode > view','.repeat-mode > view','.sheet-foot .btn','.pk-picker','.workday-rule .n-txt','.err-text',
    '.workday-status','.workday-status .n-txt','.sheet-body .pk-notice','.pk-empty','.sec-body','.tl-card','.page'];
  selectors.forEach(selector=>q.selectAll(selector).fields({rect:true,size:true,computedStyle:['fontSize','lineHeight']}));
  q.exec(result=>resolve({route:p.route,viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,pixelRatio:i.pixelRatio},
    base_library:wx.getAppBaseInfo().SDKVersion,
    nodes:selectors.flatMap((selector,index)=>(result[index]||[]).map(rect=>({selector,...rect}))),
    mode:{workday:p.data.workdayOnly,weekly:p.data.repeatWeekly,flexible:p.data.flexible},
    source:'native wx.createSelectorQuery; synthetic fixtures; production WXML/WXSS exact'}));
})}`;
async function run() {
  if (![320, 390, 430].includes(width)) throw Error("Expected 320, 390 or 430");
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  fs.mkdirSync(output, { recursive: true });
  let failures = 0;
  let screenshotFailure = "";
  for (const host of onlyHost ? [onlyHost] : (copyCleanup ? ["settings", "calendar", "today"] : ["settings", "calendar"])) {
    await call("function(host){return new Promise((resolve,reject)=>wx.switchTab({url:'/pages/'+host+'/index',success:()=>resolve(true),fail:e=>reject(Error(e.errMsg))}));}", [host]);
    const routeDeadline = Date.now() + 10000;
    while (!await call("function(host){const p=getCurrentPages().slice(-1)[0];return !!p&&p.route==='pages/'+host+'/index';}", [host])) {
      if (Date.now() >= routeDeadline) throw Error(`Native page not ready: ${host}`);
      await pause(100);
    }
    const states = copyCleanup
      ? (host === "settings" ? ["workday", "coverage"] : host === "calendar"
        ? ["create", "edit", "coverage", "partial-coverage"] : ["coverage", "partial-coverage"])
      : host === "settings" ? ["workday", "weekly", "perday", "flexible", "readonly", "saving", "error", "coverage"]
        : ["workday", "create", "once", "weekly", "readonly", "saving", "error", "coverage"];
    for (const state of states) {
      await call(copyCleanup ? copyFixture : fixture, [host, state]); await pause(100);
      if (copyCleanup && host !== "settings" && state.includes("coverage")) {
        await call("function(){wx.pageScrollTo({selector:'.workday-status',offsetTop:-120,duration:0});return true;}");
        await pause(100);
      }
      const data = await call(geometry), errors = [];
      if (data.viewport.width !== width || data.viewport.screenHeight !== {320:568,390:844,430:932}[width]) errors.push("wrong viewport");
      if (!data.nodes.length) errors.push("missing native nodes");
      for (const node of data.nodes) {
        if (node.left < -1 || node.right > width + 1) errors.push(`horizontal overflow: ${node.selector}`);
        if ([".schedule-mode > view", ".repeat-mode > view", ".pk-picker"].includes(node.selector)
          && (node.width < 44 || node.height < 44)) errors.push(`target below 44px: ${node.selector}`);
        if (node.selector === ".workday-rule .n-txt" && parseFloat(node.fontSize) < 14) errors.push("rule below 14px");
        if ((node.selector === ".workday-status .n-txt" || (host === "today" && node.selector === ".workday-status"))
          && parseFloat(node.fontSize) < 14) errors.push("status below 14px");
        if (node.selector === ".sheet-foot .btn") {
          if (node.height < 44 || node.width < 44) errors.push("save target below 44px");
          if (node.top < 0 || node.bottom > data.viewport.height) errors.push("save target outside viewport");
        }
      }
      if (copyCleanup) {
        const count = (selector) => data.nodes.filter((node) => node.selector === selector).length;
        if (count(".workday-rule .n-txt")) errors.push("removed rule still rendered");
        if (host === "settings" && count(".sheet-body .pk-notice") !== 1) errors.push("expected only time summary in settings");
        if (host === "calendar" && ["create", "edit"].includes(state) && count(".sheet-body .pk-notice")) errors.push("editor still has notes");
        if (state.includes("coverage") && host !== "settings") {
          if (count(".workday-status") !== 1) errors.push("unknown status missing or duplicated");
          if (count(".pk-empty")) errors.push("unknown rendered as empty");
          if (host === "today" && state === "coverage" && count(".sec-body")) errors.push("empty activity body remains");
          if (state === "partial-coverage" && count(".tl-card") !== 1) errors.push("known item missing");
        }
      }
      data.errors = errors; data.state = state; data.host = host;
      data.screenshot_status = "NOT_RUN";
      const stem = path.join(output, `${host}-${state}-${width}`);
      if (screenshot && !screenshotFailure) {
        try {
          const shot = await send("App.captureScreenshot");
          const bytes = Buffer.from(shot.data, "base64");
          fs.writeFileSync(stem + ".png", bytes);
          data.screenshot_sha256 = crypto.createHash("sha256").update(bytes).digest("hex");
          data.screenshot_status = "CAPTURED_REQUIRES_VISUAL_REVIEW";
        } catch (error) { screenshotFailure = error.message; data.screenshot_status = "FAIL: " + screenshotFailure; }
      } else if (screenshotFailure) {
        data.screenshot_status = "NOT_RUN_AFTER_CAPTURE_FAILURE: " + screenshotFailure;
      }
      fs.writeFileSync(stem + ".json", JSON.stringify(data, null, 2) + "\n");
      failures += errors.length;
      console.log(`${host}/${state}/${width}: ${errors.length ? errors.join(';') : 'GEOMETRY_PASS'}; ${data.screenshot_status}`);
    }
  }
  socket.close(); if (failures) process.exitCode = 1;
}
run().catch((error) => { console.error(error.message); socket.close(); process.exitCode = 1; });
