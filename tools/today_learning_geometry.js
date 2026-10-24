// Official DevTools automation against the offline synthetic copy, never business writes.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const width = Number(process.argv[2]), port = Number(process.argv[3]);
const out = path.resolve(process.argv[4] || "docs/quality/evidence/today-learning-20261024/native");
const states = process.argv[5] ? process.argv[5].split(",") : ['empty','proposal','edit','long','loading','error','stale','pending','partial','viewer','record','remove'];
const selectors = [".study-region", ".study-region .s-t", ".study-card", ".study-card .study-title", ".study-region .btn", ".study-card .link-btn", ".study-progress", ".study-error-inline", ".study-error-inline .link-btn", ".study-label", ".study-title", ".study-meta", ".study-copy", ".study-source",
  ".study-sheet", ".study-top", ".study-close", ".study-body", ".study-actions", ".study-primary",
  ".study-secondary", ".study-quiet", ".study-input", ".study-textarea", ".study-picker",
  ".study-actions .study-primary", ".study-secondary-row .study-secondary", ".study-defer",
  ".study-proposal-heading", ".study-title-scroll", ".study-proposal-title", ".study-proposal-meta", ".study-close .ico",
  ".study-field-row", ".study-field-row .study-field-label", ".study-title-counter", ".study-title-error", "#study-title"];
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = (e) => { const m = JSON.parse(e.data); const resolve = pending.get(m.id); if (resolve) { pending.delete(m.id); resolve(m); } };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, (m) => { clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const fixture = `function(state){const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#today-learning');
  if(!c)throw Error('today-learning component missing');
  const proposal={id:'synthetic-proposal',version:1,title:'用积木表示十以内的加法',subject_id:'synthetic-subject',subject_name:'数学',estimated_minutes:12,
    instructions:'把两组积木合在一起，用一个加法算式表示。再改变一组积木的数量，说说算式有什么变化。',
    rationale:'参考已经确认的十以内加法，尝试换一种表示方法。',uncertainty:'只参考最近的记录，请家长核对是否适合。',sources:[{knowledge_id:'synthetic-k',name:'十以内加法'}]};
  const current={day:'2026-10-24',version:1,eligibility:'eligible',proposal,task:null,job:null};
  let sheet='proposal',canWrite=true,error='',extra={};
  if(['design','design-long','saving','approve-error'].includes(state)){
    proposal.title='用凑十法试算 8 + 7';
    proposal.instructions='取 8 个和 7 个小物件。从 7 个里拿出 2 个与 8 个凑成 10，再数剩下的 5 个。换一种摆法试一试。';
    proposal.rationale='已记录过“20 以内加法”。这次可以试着把其中的数凑成 10，换一种具体做法。';
    proposal.sources=[{knowledge_id:'synthetic-k',name:'20 以内加法'}];
  }
  if(state==='design-long')proposal.title='用小物件把 8 + 7、9 + 6 和 7 + 5 拆成十与几，再说说为什么两种摆法的总数一样';
  if(['max-title','max-title-scrolled'].includes(state))proposal.title='用小物件练习已经学过的加法'.repeat(10).slice(0,120);
  if(state==='max-title-scrolled')extra.geometryHeadingScroll=9999;
  if(state==='saving')extra={busy:true,busyAction:'approve'};
  if(state==='approve-error')error='暂时没能加入，请重试。建议内容已保留。';
  if(['pending','partial','viewer','record','remove'].includes(state)){
    current.eligibility='pending';current.task={id:'synthetic-task',version:1,content:proposal,last_partial_at:state==='partial'?'2026-10-24T01:00:00Z':null};current.proposal=null;
    sheet=state==='record'?'record':state==='remove'?'remove':'';
  }
  if(state==='viewer')canWrite=false;
  if(state==='edit'){sheet='edit';extra={editTitle:proposal.title,editInstructions:proposal.instructions,editMinutes:'12'};}
  if(state==='long'){proposal.title='长中文学习建议的完整标题'.repeat(8);proposal.instructions='把已经学过的加法用积木、画图和自己的语言各表示一次，请家长按实际情况调整。'.repeat(15);}
  if(state==='loading'){current.proposal=null;current.job={state:'running'};}
  if(state==='error'){current.proposal=null;current.job={state:'failed'};error='暂时未能准备建议，可以稍后重试。';}
  if(state==='stale'){current.proposal=null;current.stale=true;}
  if(state==='empty'){current.proposal=null;current.eligibility='no_history';sheet='';extra.note='先记下一项孩子已经学过的内容，之后可以在它的基础上小步延展。';}
  if(state.startsWith('title-')){
    proposal.title=['title-proposal','title-edit-default'].includes(state)?'用积木表示两组数相加':'用积木表示加法并说说两组数量合起来的变化';
    if(['title-legacy','title-edit-legacy'].includes(state))proposal.title='用小物件练习已经学过的加法'.repeat(10).slice(0,120);
    if(state==='title-card-max')sheet='';
    if(state==='title-edit-error')error='暂时没能保存，请重试。';
  }
  if(state.startsWith('card-')){
    const kind=state.slice(5);sheet='';current.proposal=null;
    proposal.title='用凑十法试算 8 + 7';
    proposal.instructions='取 8 个和 7 个小物件。从 7 个里拿出 2 个与 8 个凑成 10，再数剩下的 5 个。';
    if(['recent-new','warming-up','no-history','missing-grade','no-subject','disabled','inactive'].includes(kind))current.eligibility=kind.replaceAll('-','_');
    if(kind==='eligible-empty')current.can_regenerate=true;
    if(kind==='unknown-empty')current.eligibility='future-status';
    if(kind==='viewer-empty'){canWrite=false;current.proposal=proposal;}
    if(['proposal','proposal-long'].includes(kind))current.proposal=proposal;
    if(kind==='proposal-long')proposal.title='用小物件练习已经学过的加法'.repeat(10).slice(0,120);
    if(['task','partial','viewer-task','task-feature-off'].includes(kind)){
      current.eligibility=kind==='task-feature-off'?'disabled':'pending';
      current.task={id:'synthetic-task',version:1,content:proposal,last_partial_at:kind==='partial'?'2026-10-24T01:00:00Z':null};
      if(kind==='viewer-task')canWrite=false;
    }
    if(kind==='generating')current.job={state:'running'};
    if(kind==='generation-error')current.job={state:'failed'};
    if(kind==='stale')current.stale=true;
    if(kind==='recover-after-remove'){current.eligibility='recent_new';current.can_regenerate=true;}
    if(kind==='network-error'){current.eligibility='recent_new';error='学习建议暂时没加载出来，请稍后重试。';}
  }
  p.setData({canWrite,loading:false,error:'',showLearningSheet:!!sheet,'dashboard.show_guide':false,
    stablePlan:true,planCompleted:false,hero:{total:1,required:1,optional:0,minutes:3,ticks:[],note:'按自己的节奏，做一点就好。'}});
  c.applyGeometryFixture(JSON.stringify({current,canWrite,sheet,busy:false,busyAction:'',geometryHeadingScroll:0,error,actual:'用积木表示了两组加法',actualDate:'2026-10-24',actualTime:'10:00',focusActual:false,focusTitle:false,...extra}));
  if(state==='edit'||state.startsWith('title-edit-')){
    c.edit();
    if(state==='title-edit-over')c.field({currentTarget:{dataset:{field:'editTitle'}},detail:{value:proposal.title+'呀'}});
    if(state==='title-edit-empty')c.field({currentTarget:{dataset:{field:'editTitle'}},detail:{value:''}});
    if(state==='title-edit-unicode')c.field({currentTarget:{dataset:{field:'editTitle'}},detail:{value:'𠀀'.repeat(20)}});
    c.applyGeometryFixture(JSON.stringify({current,focusTitle:false,...(state==='title-edit-saving'?{busy:true,busyAction:'edit'}:{})}));
    sheet='edit';
  }
  p.learningModal({detail:{open:!!sheet}});wx.pageScrollTo({scrollTop:0,duration:0});return true;
}`;
async function capture(state) {
  const data = await call(`function(selectors){return new Promise(resolve=>{
    const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#today-learning'),q=wx.createSelectorQuery().in(c),i=wx.getSystemInfoSync();
    selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize','fontFamily','fontWeight','lineHeight','letterSpacing','borderRadius','paddingLeft','paddingRight','textAlign','justifyContent']}));
    q.selectViewport().scrollOffset();q.select('.study-title-scroll').scrollOffset();q.exec(rows=>{const nodes={};selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(n=>n.width&&n.height));
    const pageQuery=wx.createSelectorQuery();pageQuery.select('.pk-hero').boundingClientRect();pageQuery.select('.sec .s-t').fields({rect:true,size:true,computedStyle:['fontSize','fontFamily','fontWeight','lineHeight','letterSpacing']});
    pageQuery.select('.sec-bar').boundingClientRect();pageQuery.select('.sec').fields({rect:true,size:true,computedStyle:['marginTop']});
    pageQuery.exec(pageRows=>resolve({nodes,hero:pageRows[0],reviewHeading:pageRows[1],reviewBar:pageRows[2],reviewSection:pageRows[3],card:c.data.card,scrollLeft:(rows[selectors.length]||{}).scrollLeft||0,headingScrollTop:(rows[selectors.length+1]||{}).scrollTop||0,viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion},sheet:c.data.sheet,titleState:{value:c.data.editTitle,count:c.data.editTitleCount,error:c.data.titleError,busy:c.data.busy}}));});
  });}`, [selectors]);
  const errors=[],check=(ok,msg)=>{if(!ok)errors.push(msg);};
  check(data.viewport.width===width&&data.viewport.screenHeight==={320:568,390:844,430:932}[width],"wrong viewport");
  check(data.scrollLeft===0,"horizontal scrolling");
  const controls=new Set([".study-region .btn",".study-card .link-btn",".study-error-inline .link-btn",".study-primary",".study-secondary",".study-quiet",".study-close",".study-input",".study-textarea",".study-picker"]);
  for(const [selector,rects] of Object.entries(data.nodes))for(const r of rects){
    check(r.left>=-1&&r.right<=width+1,selector+" outside viewport");
    if(controls.has(selector))check(r.width>=43&&r.height>=43,selector+" below 44px");
    if(r.fontSize)check(parseFloat(r.fontSize)>=14,selector+" below 14px text");
  }
  for(const selector of [".study-sheet",".study-top",".study-close",".study-actions"])
    for(const r of data.nodes[selector]||[])check(r.top>=-1&&r.bottom<=data.viewport.height+1,selector+" hidden");
  const footer=data.nodes['.study-actions']?.[0],body=data.nodes['.study-body']?.[0];
  if(footer&&body){check(body.bottom<=footer.top+1,"body overlaps footer");check(body.height>=44,'body needs scrollable space');}
  const close=data.nodes['.study-close']?.[0];
  if(state==='max-title-scrolled'){
    const titleViewport=data.nodes['.study-title-scroll'][0],meta=data.nodes['.study-proposal-meta'][0];
    check(data.headingScrollTop>0||(titleViewport&&meta&&meta.bottom<=titleViewport.bottom+1),'maximum title must be fully visible or actually scroll');
  }
  if(close)check(Math.abs(close.width-44)<=1&&Math.abs(close.right-(width-width*32/750))<=1,'close width/alignment');
  if(['title-proposal','title-proposal-max'].includes(state)){
    const title=data.nodes['.study-proposal-title'][0];
    check(title&&parseFloat(title.fontSize)===20&&title.height<=59,'20 CJK title needs at most two normal-font lines');
  }
  if(state.startsWith('title-edit-')){
    const label=data.nodes['.study-field-row .study-field-label'][0],counter=data.nodes['.study-title-counter'][0],input=data.nodes['#study-title'][0];
    check(!!label&&!!counter&&!!input,'title field and counter missing');
    if(label&&counter&&input){
      check(counter.left-label.right>=7.9,'label/counter gap');
      check(counter.right<=input.right+1&&label.left>=input.left-1,'counter/label outside input width');
      check(Math.abs(counter.top-label.top)<=1,'counter must share label row');
    }
    const count=state==='title-edit-over'?21:state==='title-edit-empty'?0:state==='title-edit-legacy'?120:state==='title-edit-default'?Array.from('用积木表示两组数相加').length:20;
    check(data.titleState.count===count,'wrong code point count');
    const invalid=['title-edit-over','title-edit-empty','title-edit-legacy'].includes(state);
    check(!!data.titleState.error===invalid,'wrong title field error');
    check(data.nodes['.study-title-error'].length===(invalid?1:0),'field error missing or stale');
    for(const error of data.nodes['.study-title-error'])check(error.top>=input.bottom-1,'error must follow title field');
    check(data.titleState.busy===(state==='title-edit-saving'),'wrong saving state');
    if(state==='title-edit-legacy')check(data.titleState.value.length===120,'legacy title truncated');
    if(state==='title-edit-unicode')check(Array.from(data.titleState.value).length===20&&data.titleState.value.length===40,'non BMP input truncated');
  }
  for(const r of data.nodes['.study-actions .study-primary']||[])check(Math.abs(r.width-(footer.width-parseFloat(footer.paddingLeft)-parseFloat(footer.paddingRight)))<=1,'primary action must fill content width');
  const secondary=data.nodes['.study-secondary-row .study-secondary']||[];
  secondary.slice(1).forEach((r,i)=>{check(r.left-secondary[i].right>=7.9,'secondary action gap');check(Math.abs(r.width-secondary[i].width)<=1,'secondary equal width');});
  for(const r of data.nodes['.study-defer']||[])check(Math.abs(r.width-(footer.width-parseFloat(footer.paddingLeft)-parseFloat(footer.paddingRight)))<=1,'defer fills row');
  const primary=data.nodes['.study-primary']||[];
  if(state==='viewer')check(primary.length===0,"viewer has write action");
  if(state.startsWith('card-')){
    const kind=state.slice(5),region=data.nodes['.study-region'][0],heading=data.nodes['.study-region .s-t'][0],card=data.nodes['.study-card'][0];
    const hidden=['recent-new','warming-up','no-history','missing-grade','no-subject','disabled','inactive','eligible-empty','viewer-empty','unknown-empty','network-error'].includes(kind);
    check(hidden?!region:!!region,'card visibility');
    if(hidden&&kind!=='network-error'){
      check(!card&&!heading&&!data.nodes['.study-progress'].length,'empty region leaves no nodes');
      // Existing interactive sec-bar has a 44px touch floor on narrow devices.
      const expected=parseFloat(data.reviewSection.marginTop)+(data.reviewBar.height-data.reviewHeading.height)/2;
      check(Math.abs(data.reviewBar.top-data.hero.bottom-parseFloat(data.reviewSection.marginTop))<=1,'empty region shifts adjacent section');
      check(Math.abs(data.reviewHeading.top-data.hero.bottom-expected)<=1,'empty region leaves extra spacing');
    }
    if(heading)for(const key of ['fontSize','fontFamily','fontWeight','lineHeight','letterSpacing'])check(heading[key]===data.reviewHeading[key],'section typography differs: '+key);
    for(const title of data.nodes['.study-card .study-title']){
      check(parseFloat(title.fontSize)===16&&title.fontWeight==='600','content title typography');
      check(Math.abs(parseFloat(title.lineHeight)-22.4)<=1,'title line height');
      check(title.left>=card.left&&title.right<=card.right+1,'title outside card');
    }
    if(card)check(Math.abs(parseFloat(card.borderRadius)-40*width/750)<=1,'card radius');
    for(const button of data.nodes['.study-region .btn']){
      check(parseFloat(button.borderRadius)>=button.height/2,'button must be capsule');
      const parent=card||data.nodes['.study-progress'][0];
      check(Math.abs(button.width-(parent.width-parseFloat(parent.paddingLeft)-parseFloat(parent.paddingRight)-(card?2:0)))<=1,'card action must fill content width');
    }
    if(card)for(const selector of ['.study-card .study-title','.study-meta','.study-copy','.study-region .btn','.study-card .link-btn'])for(const node of data.nodes[selector])check(node.top>=card.top-1&&node.bottom<=card.bottom+1,'content outside card: '+selector);
    if(kind==='viewer-task')check(!data.nodes['.study-region .btn'].length&&!data.nodes['.study-card .link-btn'].length,'viewer task has write controls');
    for(const action of data.nodes['.study-card .link-btn'])check(action.textAlign==='center'&&action.justifyContent==='center','quiet task action must be centered');
    if(kind==='network-error')check(data.nodes['.study-error-inline'].length===1,'network error hidden');
  }
  let shot=await send('App.captureScreenshot');
  const bytes=Buffer.from((typeof shot==='string'?shot:shot.data||shot.base64).replace(/^data:image\/\w+;base64,/,''),'base64');
  fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,`${state}-${width}.png`),bytes);
  fs.writeFileSync(path.join(out,`${state}-${width}.json`),JSON.stringify({...data,state,errors,capturedAt:new Date().toISOString(),screenshotSha256:crypto.createHash('sha256').update(bytes).digest('hex')},null,2)+'\n');
  console.log(`${state}-${width}: ${errors.join('; ')||'PASS'}`);return errors.length;
}
async function main(){
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  try{
    if(!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}"))throw Error('Offline synthetic copy required');
    await call("function(){return new Promise(resolve=>wx.switchTab({url:'/pages/today/index',complete:()=>setTimeout(()=>resolve(true),400)}));}");
    let errors=0;
    for(const state of states){
      await call(fixture,[state]);await new Promise(resolve=>setTimeout(resolve,180));
      if(state==='card-proposal-long'){
        await call("function(){return new Promise(resolve=>{const c=getCurrentPages().slice(-1)[0].selectComponent('#today-learning');wx.createSelectorQuery().in(c).select('.study-region').boundingClientRect(rect=>wx.pageScrollTo({scrollTop:rect.top-8,duration:0,complete:()=>resolve(true)})).exec();});}");
        await new Promise(resolve=>setTimeout(resolve,180));
      }
      errors+=await capture(state);
    }
    await call("function(){const p=getCurrentPages().slice(-1)[0],c=p.selectComponent('#today-learning');c.close();return true;}");
    if(errors)throw Error(`${errors} native geometry assertions failed`);
  }finally{socket.close();}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;socket.close();});
