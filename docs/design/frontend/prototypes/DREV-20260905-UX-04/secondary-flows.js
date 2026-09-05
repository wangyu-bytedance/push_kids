/* Secondary flows use only the review prototype's local state. */
const catalogNames = {
  subject: ['科学','道德与法治','物理','化学','生物','历史','地理','政治','美术','音乐','体育','劳动'],
  activity: ['游泳','乒乓球','篮球','羽毛球','足球','网球','围棋','国际象棋','钢琴','小提琴','舞蹈','武术','跆拳道','书法','绘画','编程','机器人']
};
state.catalogMode = 'catalog';
state.activityConfigs = {'游泳':{days:[2],start:'18:00',end:'19:00',flexible:false}};
function openCatalog(kind,keep=false){
  state.catalogKind=kind;
  if(!keep){state.catalogMode='catalog';state.selectedChip='';state.catalogQuery='';}
  const subject=kind==='subject', label=subject?'科目':'课外活动';
  sheet(`添加${label}`,`<p class="helper catalog-intro">只添加孩子已经开始${subject?'学习':'参与'}的内容。</p><div class="segmented catalog-modes"><button class="${state.catalogMode==='catalog'?'active':''}" data-action="catalog-mode" data-value="catalog">从目录选择</button><button class="${state.catalogMode==='custom'?'active':''}" data-action="catalog-mode" data-value="custom">自定义名称</button></div><div class="catalog-body">${state.catalogMode==='catalog'?`<label class="searchbox catalog-search">${icon('search')}<input id="catalog-search" type="search" placeholder="搜索${label}" aria-label="搜索${label}"></label><div id="catalog-items"></div>`:`<label class="field"><span class="field-label">${label}名称</span><input id="custom-name" maxlength="20" placeholder="例如：${subject?'自然观察':'陶艺'}" value="${esc(state.catalogCustom||'')}"></label><p class="helper">不在目录里，也可以按实际名称添加。</p>`}</div><div class="sheet-footer"><div id="form-error" class="error-text" role="alert"></div><button class="primary" id="catalog-submit" data-action="save-${kind}" ${state.selectedChip||state.catalogMode==='custom'&&state.catalogCustom?'':'disabled'}>添加${label}</button></div>`);
  const panel=document.querySelector('.sheet');panel.classList.add('catalog-sheet');panel.classList.toggle('custom-mode',state.catalogMode==='custom');
  if(state.catalogMode==='catalog')renderCatalogItems();
}
function renderCatalogItems(){
  const subject=state.catalogKind==='subject',existing=first()?[]:(subject?state.extras:state.activities);
  const filtered=catalogNames[state.catalogKind].filter(name=>!state.catalogQuery||name.includes(state.catalogQuery));
  document.getElementById('catalog-items').innerHTML=filtered.length?`<div class="catalog-choices">${filtered.map(name=>`<button class="catalog-choice ${existing.includes(name)?'already':''} ${state.selectedChip===name?'selected':''}" data-action="catalog-pick" data-value="${name}" aria-pressed="${state.selectedChip===name}" ${existing.includes(name)?'disabled':''}><span>${name}</span><span class="catalog-status">${existing.includes(name)?'已添加':state.selectedChip===name?icon('check'):icon('plus')}</span></button>`).join('')}</div>`:`<div class="inline-empty" style="padding:30px 0">没有找到这个名称<br><button class="link" data-action="catalog-mode" data-value="custom">使用自定义名称</button></div>`;
}
function openActivitySchedule(name='游泳',keep=false){
  state.scheduleName=name;
  if(!keep){const current=state.activityConfigs[name]||{days:[],start:'18:00',end:'19:00',flexible:true};state.scheduleDraft={...current,days:[...current.days]};}
  const d=state.scheduleDraft;
  sheet(`${esc(name)}安排`,`<p class="helper catalog-intro">固定安排会显示在日程与今日。</p><div class="segmented catalog-modes"><button class="${!d.flexible?'active':''}" data-action="schedule-mode" data-value="fixed">固定时间</button><button class="${d.flexible?'active':''}" data-action="schedule-mode" data-value="flexible">时间不固定</button></div><div class="catalog-body">${d.flexible?`<div class="flexible-note">${icon('calendar')}<h3>按实际参与情况记录</h3><p>暂不生成固定日程，<br>参加后仍可以记录这次练习。</p></div>`:`<div class="field-label">每周哪几天 <small>可多选</small></div><div class="weekday-choices">${[...'一二三四五六日'].map((day,i)=>`<button class="weekday-choice ${d.days.includes(i)?'selected':''}" data-action="schedule-day" data-value="${i}" aria-label="周${day}" aria-pressed="${d.days.includes(i)}">${day}</button>`).join('')}</div><div class="schedule-times"><label class="field"><span class="field-label">开始时间</span><input id="schedule-start" type="time" value="${d.start}"></label><span class="schedule-to">—</span><label class="field"><span class="field-label">结束时间</span><input id="schedule-end" type="time" value="${d.end}"></label></div><p class="schedule-summary">${d.days.length?'每周'+d.days.map(i=>'一二三四五六日'[i]).join('、'):'请选择至少一天'} · ${d.start}–${d.end}</p>`}<button class="remove-activity" data-action="remove-activity-prompt">移除这项活动</button></div><div class="sheet-footer"><div id="form-error" class="error-text" role="alert"></div>${primary('保存安排','save-activity-schedule')}</div>`);
  document.querySelector('.sheet').classList.add('catalog-sheet','schedule-sheet');
}
function rememberScheduleTimes(){const start=document.getElementById('schedule-start'),end=document.getElementById('schedule-end');if(start)state.scheduleDraft.start=start.value;if(end)state.scheduleDraft.end=end.value;}
function activityDescription(name){const config=state.activityConfigs?.[name];return !config||config.flexible?'未设固定时间':`每周${config.days.map(i=>'一二三四五六日'[i]).join('、')} · ${config.start}–${config.end}`;}
document.addEventListener('click',e=>{
  const target=e.target.closest('[data-action]');if(!target||target.disabled)return;const a=target.dataset.action,v=target.dataset.value;
  if(a==='catalog-mode'){state.catalogCustom=document.getElementById('custom-name')?.value||state.catalogCustom||'';state.catalogMode=v;state.selectedChip='';openCatalog(state.catalogKind,true);}
  if(a==='catalog-pick'){state.selectedChip=v;renderCatalogItems();const button=document.getElementById('catalog-submit');button.disabled=false;button.textContent=`添加「${v}」`;}
  if(a==='schedule-mode'){rememberScheduleTimes();state.scheduleDraft.flexible=v==='flexible';openActivitySchedule(state.scheduleName,true);}
  if(a==='schedule-day'){rememberScheduleTimes();const days=state.scheduleDraft.days;state.scheduleDraft.days=days.includes(Number(v))?days.filter(d=>d!==Number(v)):[...days,Number(v)].sort((a,b)=>a-b);openActivitySchedule(state.scheduleName,true);}
  if(a==='save-activity-schedule'){rememberScheduleTimes();const d=state.scheduleDraft;if(!d.flexible&&(!d.days.length||!d.start||!d.end||d.end<=d.start)){document.getElementById('form-error').textContent=!d.days.length?'请至少选择一天。':'结束时间需要晚于开始时间。';return;}state.activityConfigs[state.scheduleName]={...d,days:[...d.days]};closeSheet();render();toast('安排已保存到演示状态');}
  if(a==='remove-activity-prompt')sheet(`移除${esc(state.scheduleName)}？`,`<p class="helper">移除后不再显示固定安排，已记录的练习内容会保留。</p><div class="actions"><button class="secondary" data-action="close">取消</button><button class="danger" data-action="remove-activity-confirm">移除活动</button></div>`);
  if(a==='remove-activity-confirm'){state.activities=state.activities.filter(name=>name!==state.scheduleName);delete state.activityConfigs[state.scheduleName];closeSheet();render();toast('已移出演示列表');}
});
document.addEventListener('input',e=>{
  if(e.target.id==='catalog-search'){state.catalogQuery=e.target.value.trim();renderCatalogItems();}
  if(e.target.id==='custom-name'&&document.getElementById('catalog-submit')){state.catalogCustom=e.target.value.trim();document.getElementById('catalog-submit').disabled=!state.catalogCustom;}
});
// Explicit preview URLs allow reproducible screenshots of secondary states.
render();
if(params.get('dialog')==='subject')openCatalog('subject');
if(params.get('dialog')==='activity')openCatalog('activity');
if(params.get('dialog')==='schedule')openActivitySchedule('游泳');
