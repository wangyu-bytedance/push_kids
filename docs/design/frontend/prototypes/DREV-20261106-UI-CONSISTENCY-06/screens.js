const THEMES = [
  {id:'garden',name:'成长花园',fallback:'嫩芽',symbol:'sprout',tone:'#83a938',material:'纸雕花园 · 奶油纸面 · 叶片细节'},
  {id:'space',name:'星际探索',fallback:'小星球',symbol:'planet',tone:'#5c70db',material:'星际观测站 · 轨道与舷窗 · 探索机器人'},
  {id:'midnight',name:'深海夜色',fallback:'罗盘星',symbol:'compass',tone:'#243e46',material:'深海暗底 · 香槟细线 · 安静的海底轮廓'},
  {id:'ocean',name:'海洋风格',fallback:'贝壳',symbol:'shell',tone:'#32b5cf',material:'阳光浅海 · 读书鲸鱼 · 波浪与贝壳'},
  {id:'tech',name:'科技风格',fallback:'芯片',symbol:'chip',tone:'#27b9bb',material:'白银实验室 · 学习机器人 · 电路与模块'}
];
const qs = new URLSearchParams(location.search);
let currentTheme = THEMES.some(t=>t.id===qs.get('theme')) ? qs.get('theme') : 'garden';
paths.planet='M18 12a6 6 0 1 1-12 0 6 6 0 0 1 12 0ZM5 10c-3 1-4 3-3 4s6 1 12-1 9-4 8-5-3-1-5 0';
paths.compass='m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5L12 2ZM12 9v6m-3-3h6';
paths.shell='M6 18 3 11C0 1 24 1 21 11l-3 7H6ZM8 18 6 7m6 11V5m4 13 2-11M8 18v3h8v-3';
paths.chip='M6 6h12v12H6V6Zm3 3h6v6H9V9ZM9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4';
paths.ruler='m4 15 11-11 6 6L10 21l-6-6Zm9-9 2 2m-5 1 2 2m-5 1 2 2m-5 1 2 2';
const fallbackIcon=()=>icon(THEMES.find(t=>t.id===currentTheme).symbol);
const extras=[
 ['subject-edit','自定义科目','学习与安排','只填写名称；无预置时直接复用本主题默认图标。'],
 ['subject-picker','添加科目','学习与安排','选择预置或自定义，取消不写入数据。'],
 ['daily-presets','每日任务候选','学习与安排','候选只预填，保存前不会加入今日。'],
 ['review-feedback','复习反馈','学习与安排','由家长记录结果，AI不评分、不判断掌握。'],
 ['review-plan','调整复习计划','学习与安排','保留已有明天/后天操作，不任意改动规则。'],
 ['review-superseded','已替代条目','学习与安排','保留历史和承接关系，不提供恢复操作。'],
 ['record-type','切换记录类型','学习与安排','从记录标题切换学习记录和旅行日记。'],
 ['record-history','学习历史记录','学习与安排','历史位于报表内，保留筛选与分页。'],
 ['manual-input','手动录入','学习与安排','不依赖AI整理，家长填写并核对。'],
 ['processing-failed','整理失败','关键状态','保留原始材料，可重试或转为手动录入。'],
 ['photo-preview','原始照片预览','学习与安排','合成示例，不使用真实孩子照片。'],
 ['voice-recording','语音输入','关键状态','录入状态明确；文字进入草稿，仍需家长确认。'],
 ['travel-map','旅行地点','旅行与照片','示意地图与真实到访分开，标注示例性质。'],
 ['travel-playback','旅行回放','旅行与照片','按日期回看已确认到访，不制造移动轨迹。'],
 ['travel-upload','照片上传中','旅行与照片','实际张数进度，保留离开再继续入口。'],
 ['travel-upload-error','照片上传失败','旅行与照片','已成功的照片保留，只重试未完成项。'],
 ['travel-edit','修改时间与地点','旅行与照片','日期与地点可修正，表单保留输入。'],
 ['travel-confirm','确认旅行入档','旅行与照片','仅明确确认后成为正式到访记录。'],
 ['travel-settings','足迹设置','旅行与照片','AI地点候选是显式偏好，与图标回退无关。'],
 ['travel-detail','照片与到访详情','旅行与照片','已确认照片、时间、地点与修改入口。'],
 ['child-archive','归档确认','家庭与设置','归档保留已有记录，与永久清理区分。'],
 ['archive-list','已归档档案','家庭与设置','恢复入口清楚，不强迫删除记录。'],
 ['family-role','成员权限','家庭与设置','只读与可编辑的范围同时说明。'],
 ['notification-renew','提醒续订说明','家庭与设置','只有主动开启才启用，暂不开启仍可正常使用。'],
 ['theme-picker','界面风格','家庭与设置','五主题预览；原始风格保留，未重绘。'],
 ['family-delete','清空家庭确认','关键状态','与清理单个孩子分开，输入家庭名称确认。']
];
extras.forEach(s=>sceneDefs.push({id:s[0],title:s[1],group:s[2],note:s[3],number:String(sceneDefs.length+1).padStart(2,'0')}));
sceneDefs.find(s=>s.id==='settings-routines').note='查看设置下半页，添加入口在同主题内一致。';
sceneDefs.find(s=>s.id==='records').note='统一添加照片入口，标题切换记录类型；手动录入保持可达。';
sceneDefs.find(s=>s.id==='child').note='昵称与年级，归档单独分区；不显示可编辑复习预算。';
sceneDefs.find(s=>s.id==='review-inventory').note='参与复习与已替代分开；科目、次数、时间视图保持现有语义。';
window.DESIGN_SCENES=sceneDefs;
window.DESIGN_THEMES=THEMES;
const recordHeader=(travelMode=false)=>`<header class="page-head"><div><p class="eyebrow">${travelMode?'一起走过的地方':'把学过的，记下来'}</p><button type="button" class="title-switch" ${nav('record-type')}>${travelMode?'旅行日记':'学习记录'}${icon('down')}</button></div>${child()}</header>`;
const demoPhoto=()=>`<div class="thumb-placeholder">${icon('image')}<span class="small">合成照片示例</span></div>`;
const simpleDialog=(base,title,copy,yes,no='取消',next='saved')=>({...base,overlay:`<div class="dialog-mask"><section class="dialog" role="dialog" aria-modal="true" aria-label="${title}"><h2>${title}</h2><p>${copy}</p>${btn(yes,next)}${btn(no,base.tab||base.back||'settings','outline')}</section></div>`});
function settingsTheme(){
 return {tab:'settings',body:`${head('设置','小禾的学习与日常')}<section class="card"><div class="between mb"><h2>在学科目</h2><button type="button" class="text-btn" ${nav('subject-picker')}>管理</button></div><div class="subject-list">${[['语文','book'],['数学','ruler'],['思维拓展','fallback']].map(([name,sym])=>`<button type="button" ${nav('subject-edit')}><span class="subject-symbol" ${sym==='fallback'?'data-fallback="'+currentTheme+'"':''}>${sym==='fallback'?fallbackIcon():icon(sym)}</span><span>${name}</span>${sym==='fallback'?'<small>自定义</small>':''}</button>`).join('')}<button type="button" class="subject-add" ${nav('subject-picker')} aria-label="添加科目">${icon('plus')}</button></div></section><section class="card"><h2>课外活动</h2>${row('围棋','每周日 14:00–16:00','board','activity-schedule')}${row('游泳','每周日 17:00–18:00','swim','activity-schedule')}${add('添加课外活动','activity-schedule')}</section><section class="card" id="settings-daily"><div class="card-top"><h2>每日任务</h2><span class="meta">每天重复</span></div>${row('阅读','每天 20 分钟','book','daily-form')}${row('围棋','每天 30 分钟','board','daily-form')}${add('添加每日任务','daily-presets')}</section><section class="card"><h2>出行安排</h2><p class="page-desc">只显示在日程，不生成待办</p>${row('城市公园','11月8日 · 10:00–12:00','map','travel-plan')}${add('添加出行安排','travel-plan')}</section><section class="card">${row('孩子档案','小禾 · 二年级','sprout','child')}${row('家庭与成员','小禾的家 · 3 位成员','family','family-members')}${row('界面风格',THEMES.find(t=>t.id===currentTheme).name,'image','theme-picker')}${row('提醒设置','微信提醒已开启','bell','notifications')}${row('数据管理','归档或清理资料','archive','delete-settings')}</section>`};
}
function recordTheme(voice=false){
 return {tab:'records',...footer('提交整理','processing'),body:`${recordHeader()}<div class="record-time"><div class="between"><span>实际学习时间</span><button type="button" class="text-btn" data-demo="修改实际学习时间">11月6日 18:30 ${icon('down','sm')}</button></div></div><button type="button" class="upload-tile mt mb" style="width:100%" ${nav('photo-preview')}>${icon('camera')}<strong>添加学习照片</strong><span class="small">拍照或从相册选择</span></button><label class="field"><span class="field-label">补充文字</span><textarea class="input area voice-area" placeholder="今天学了什么？也可以直接用文字记录。">${voice?'':'今天练习了乘法口诀，用小积木表示3组，每组4个。'}</textarea></label><div class="voice-bar">${voice?`<span class="voice-bars" aria-hidden="true">${'<i></i>'.repeat(9)}</span><span class="small">松开，转成文字</span>`:'<span class="small">语音会转成可编辑文字</span>'}<button type="button" class="icon-btn" ${nav(voice?'records':'voice-recording')} aria-label="${voice?'结束语音示例':'语音输入'}">${icon('mic')}</button></div><div class="notice mt">${icon('edit')}<p>整理后先由你核对，确认后才成为正式记录。</p></div><button type="button" class="text-btn" ${nav('manual-input')}>直接手动录入 ${icon('arrow','sm')}</button>`};
}
function travelTheme(mode='timeline'){
 const timeline=`<div class="timeline-item"><div class="between mb"><strong>10月18日</strong><span class="small">杭州 · 西湖</span></div><button type="button" class="photo-card" style="width:100%;padding:0" ${nav('travel-detail')}><div class="photo landscape">${scenic()}</div><div class="copy"><strong>湖边走走</strong><p class="small">家长已确认 · 2 张照片</p></div></button></div><div class="timeline-item"><strong>10月4日</strong><p class="small mt8">苏州 · 拙政园 · 3 张照片</p><div class="photo landscape mt8">${scenic(1)}</div></div>`;
 const map=`<div class="map-preview" aria-label="到访地点示意图，不代表真实地理位置"><svg viewBox="0 0 350 260" aria-hidden="true"><path d="M-10 48C80 10 100 150 190 83s95 22 180-16M-10 170C90 120 141 230 225 160s80-32 130 0" fill="none" stroke="currentColor" opacity=".14" stroke-width="35"/><path d="M20 0 80 260M180 0 230 260M0 90l350 50" fill="none" stroke="currentColor" opacity=".12"/><circle cx="145" cy="154" r="12" fill="currentColor"/><circle cx="232" cy="86" r="9" fill="currentColor"/><text x="145" y="190" text-anchor="middle" fill="currentColor" font-size="16">杭州 · 2 个到访日</text><text x="232" y="58" text-anchor="middle" fill="currentColor" font-size="16">苏州</text></svg></div><p class="map-caption">合成地图示例 · 到访点按家长确认记录显示</p>`;
 return {tab:'records',body:`${recordHeader(true)}<div class="between mb"><button class="button compact" type="button" ${nav('travel-upload')}>${icon('plus','sm')} 导入照片</button><button class="icon-btn" type="button" ${nav('travel-settings')} aria-label="足迹设置">${icon('settings')}</button></div><div class="segmented">${[['timeline','时间线','travel'],['map','地点','travel-map'],['playback','回放','travel-playback']].map(([m,n,s])=>`<button type="button" class="${mode===m?'active':''}" ${nav(s)}>${n}</button>`).join('')}</div>${mode==='timeline'?`<div class="card green-card"><div class="between"><h3>待核对照片</h3>${tag('2 张','draft')}</div><button class="text-btn" type="button" ${nav('travel-review')}>继续核对时间与地点 ${icon('chevron','sm')}</button></div>${timeline}`:`${map}${mode==='playback'?`<div class="card mt"><div class="between"><strong>10月18日 · 杭州西湖</strong><span class="small">2 / 3</span></div><div class="flex mt">${btn('播放','','compact')}<input aria-label="回放进度" type="range" min="1" max="3" value="2" style="min-width:0;min-height:44px;flex:1"></div>${btn('查看这次的照片','travel-detail','outline mt')}</div>`:row('杭州 · 西湖','2 个到访日 · 5 张照片','pin','travel-detail')}`}`};
}
function inventoryTheme(superseded=false){
 return {back:'reports',body:`${head('复习条目','查看已有内容与安排',false)}<div class="segmented"><button type="button" class="${!superseded?'active':''}" ${nav('review-inventory')}>参与复习</button><button type="button" class="${superseded?'active':''}" ${nav('review-superseded')}>已替代</button></div><div class="subnav"><button class="active" type="button" data-select>按次数</button><button type="button" data-select>按科目</button>${!superseded?'<button type="button" data-select>按时间</button>':''}</div>${select('次数','全部次数')}<div class="between mb"><h2>${superseded?'1':'4'} 个知识条目</h2><span class="small">按科目分组</span></div><div class="card"><div class="between mb"><span class="flex"><span class="mark">${icon('ruler')}</span><h2>数学</h2></span>${tag(superseded?'已替代':'2 项',superseded?'neutral':'')}</div><h3>用乘法表示相同加数的和</h3><p class="small mt8">已复习 2 次 · 最近复习 11月4日</p>${superseded?`<p class="small mt8">后续复习由「用乘法解决生活问题」承接。</p><button class="text-btn" type="button" ${nav('record-detail')}>查看原学习记录 ${icon('chevron','sm')}</button>`:`<div class="between mt8"><span class="small">预计明天复习</span><button type="button" class="text-btn" ${nav('review-plan')}>调整计划</button></div><div class="divider"></div><h3>认识厘米和米</h3><p class="small mt8">已复习 1 次 · 最近复习 11月5日</p><button type="button" class="text-btn" ${nav('review-plan')}>调整计划 ${icon('chevron','sm')}</button>`}</div>${!superseded?`<div class="card">${row('语文','2 个知识条目','book','record-detail')}</div>`:notice('已替代条目保留历史，后续不再单独生成复习安排。')}`};
}
const originalScene=getScene;
getScene=function(id){
 switch(id){
 case 'delete-settings':{const s=cleanup();s.body=s.body.replace(row('清空当前家庭','删除家庭内全部孩子资料与记录','family','delete-confirm'),row('清空当前家庭','删除家庭内全部孩子资料与记录','family','family-delete'));return s;}
 case 'family-delete':return {back:'delete-settings',body:`${head('清空当前家庭','请仔细核对',false)}${notice('这会永久删除当前家庭内全部孩子资料与关联记录，清理后无法恢复。','error')}<div class="card"><div class="info-kv"><span>当前家庭</span><strong>小禾的家</strong></div><div class="info-kv"><span>清理范围</span><strong>全部孩子与记录</strong></div></div>${field('输入完整家庭名称「小禾的家」确认','','text','名称完全一致后才能继续。')}<button type="button" id="family-delete-final" class="button danger-button" disabled>永久清空当前家庭</button>${btn('保留资料，返回','delete-settings','outline mt')}`};
 case 'settings':return settingsTheme();
 case 'error':{const s=settingsTheme();s.body=s.body.replace('</header>','</header>'+notice('部分内容加载失败，已显示的内容会保留。','error')+btn('重新加载','settings','outline mb'));return s;}
 case 'child-switch':return sheetOver(settingsTheme(),'选择孩子',`${row('小禾','小学二年级 · 当前使用','sprout','settings')}${row('小满','幼儿园大班','sprout','settings')}${btn('管理孩子档案','child','outline mt')}${btn('查看已归档档案','archive-list','outline mt')}`);
 case 'grade':return sheetOver(getScene('child'),'小禾的年级',`${select('当前年级','小学二年级')}<div class="flex">${btn('稍后','child','outline')}${btn('确认年级','saved')}</div>`);
 case 'settings-routines':return {...settingsTheme(),scrollTarget:'settings-daily'};
 case 'saved':return {...settingsTheme(),toast:'已保存'};
 case 'records':return recordTheme();
 case 'voice-recording':return recordTheme(true);
 case 'travel':return travelTheme();
 case 'travel-map':return travelTheme('map');
 case 'travel-playback':return travelTheme('playback');
 case 'review-inventory':return inventoryTheme();
 case 'review-superseded':return inventoryTheme(true);
 case 'today':{const s=today();s.body=s.body.replaceAll('data-nav="record-detail"','data-nav="review-feedback"');return s;}
 case 'reports':{const s=reports();s.body=s.body.replace('data-nav="record-detail"','data-nav="record-history"');return s;}
 case 'child':return {back:'settings',...footer('保存档案','saved'),body:`${head('孩子档案','小禾',false)}<div class="flex mb"><span class="mark big">${icon('sprout')}</span><div><h2>小禾</h2><p class="small">正在使用的学习档案</p></div></div>${field('昵称','小禾')}${select('当前年级','小学二年级','grade')}<section class="archive-zone"><h2>档案管理</h2><p class="small mt8">归档后保留已有记录，需要时可以恢复。</p><button type="button" class="text-btn" ${nav('child-archive')}>归档此档案 ${icon('chevron','sm')}</button><div>${btn('查看已归档档案','archive-list','outline mt')}</div></section>`};
 case 'subject-edit':return {back:'settings',...defaultFooter(),body:`${head('自定义科目','小禾',false)}${field('科目名称','思维拓展')}<div class="card"><div class="flex"><span class="mark big" data-fallback="${currentTheme}">${fallbackIcon()}</span><div><h2>思维拓展</h2><p class="small">使用当前风格的默认图标</p></div></div></div><p class="small mt">科目名称可以自由填写，图标会自动匹配。</p>`};
 case 'subject-picker':return sheetOver(settingsTheme(),'添加科目',`<div class="selection-grid">${[['英语','book'],['科学','compass'],['美术','edit'],['音乐','bell']].map(([n,i])=>`<button type="button" ${nav('subject-edit')}>${icon(i)}${n}</button>`).join('')}</div>${btn('自定义科目','subject-edit','outline mt')}`);
 case 'daily-presets':return sheetOver(settingsTheme(),'添加每日任务',`<div class="selection-grid">${[['阅读','book'],['跳绳','clock'],['练字','edit'],['户外运动','sprout']].map(([n,i])=>`<button type="button" ${nav('daily-form')}>${icon(i)}${n}</button>`).join('')}</div>${btn('自定义任务','daily-form','outline mt')}<p class="small mt">先填写目标时长，保存后加入每日任务。</p>`);
 case 'review-feedback':return sheetOver(today(),'记录复习反馈',`${tag('数学','math')}<h3 class="mt">用乘法口诀解决生活问题</h3><p class="small mt8">按这次实际情况记录</p>${['记得清楚','有点模糊','需要再看看'].map((n,i)=>`<button type="button" class="review-choice ${i===1?'active':''}" data-choice><span class="check ${i===1?'checked':''}">${i===1?icon('check'):''}</span><span>${n}</span></button>`).join('')}${area('补充说明（选填）','','例如：举例时还需要提醒。')}${btn('保存这次反馈','notification-renew')}`);
 case 'review-plan':return sheetOver(inventoryTheme(),'调整复习计划',`<h3>用乘法表示相同加数的和</h3><p class="small mt8">已复习 2 次 · 预计明天复习</p>${btn('加入明天复习','saved','mt')}${btn('改到后天复习','saved','outline mt')}<div class="divider"></div><button type="button" class="text-btn danger-text" data-demo="删除条目确认">删除条目</button>`);
 case 'record-type':return sheetOver(recordTheme(),'记录类型',`${row('学习记录','记录实际学过的内容','book','records')}${row('旅行日记','照片与家长确认的到访','camera','travel')}`);
 case 'record-history':return {tab:'reports',body:`${head('学习记录','回看学过的内容')}<div class="segmented"><button type="button" class="active" data-select>全部</button><button type="button" data-select>待处理</button><button type="button" data-select>已确认</button></div>${select('科目','全部科目')}<div class="card">${row('练习乘法口诀','11月6日 18:30 · 数学 · 待确认','edit','confirm')}${row('用乘法解决生活问题','11月3日 18:30 · 数学 · 已确认','book','record-detail')}${row('区分形近字晴、睛','11月2日 19:00 · 语文 · 已确认','book','record-detail')}</div><div class="between mt"><button type="button" class="text-btn" disabled>上一页</button><span class="small">第 1 页</span><button type="button" class="text-btn" data-demo="下一页历史">下一页</button></div>${btn('返回报表','reports','outline mt')}`};
 case 'manual-input':return {back:'records',...footer('核对手动记录','manual-confirm'),body:`${head('手动录入','小禾 · 实际学过的内容',false)}${select('实际学习日期','2026年11月6日')}${select('科目','数学')}${area('本次学习总结','练习用乘法表示相同加数的和。')}${area('学过的具体内容','用3×4表示3组，每组4个，并求出总数12。')}<p class="small">下一步核对，确认后保存为正式学习记录。</p>`};
 case 'processing-failed':return {back:'records',body:`${head('整理未完成','材料已保留',false)}${notice('这次未能完成整理，请重试或直接手动录入。','error')}<div class="card"><h2>已提交的材料</h2><p class="small mt8">文字 1 段 · 11月6日 18:30</p><p class="mt">今天练习了乘法口诀，用小积木表示3组，每组4个。</p></div>${btn('重新整理','processing','mt')}${btn('转为手动录入','manual-input','outline mt')}${btn('返回记录页','records','outline mt')}`};
 case 'photo-preview':return {back:'records',body:`${head('照片预览','第 1 张 / 共 1 张',false)}<div class="full-photo">${icon('image')}</div><p class="small center mt">合成示例 · 实际界面显示家长选择的照片</p>${btn('继续补充文字','records','mt')}${btn('移除此照片','records','outline mt')}`};
 case 'travel-upload':return sheetOver(travelTheme(),'导入照片',`<div class="flex"><span class="spinner"></span><h3>已上传 2 张，共 3 张</h3></div><div class="preview-progress"><span></span></div><p class="small">上传完成后，核对拍摄日期与地点。</p>${btn('查看已上传照片','travel-review','outline mt')}`);
 case 'travel-upload-error':return sheetOver(travelTheme(),'导入照片',`${notice('第 3 张照片上传失败，已成功的 2 张会保留。','error')}<div class="info-kv"><span>已完成</span><strong>2 / 3 张</strong></div>${btn('重试未完成的照片','travel-upload','mt')}${btn('先核对已上传照片','travel-review','outline mt')}`);
 case 'travel-review':return {back:'travel',...footer('下一步：确认入档','travel-confirm','已选 2 张照片'),body:`${head('核对照片','2 / 3 · 核对时间与地点',false)}<div class="between mb"><button type="button" class="text-btn" data-demo="全选本页">全选本页</button><button type="button" class="text-btn" ${nav('travel-edit')}>批量修改</button></div>${[1,2].map((n)=>`<div class="card"><div class="photo-meta"><span class="check checked">${icon('check')}</span><div class="photo">${scenic(n%2)}</div><div><h3>10月18日 · 14:30</h3><p class="small">杭州 · ${n===1?'西湖':'北山街'}</p></div></div>${tag('待家长核对','draft')}<div><button type="button" class="text-btn" ${nav('travel-edit')}>核对照片 ${icon('chevron','sm')}</button></div></div>`).join('')}${notice('日期和地点请按真实情况核对。确认前不会生成正式到访记录。')}`};
 case 'travel-edit':return {back:'travel-review',...footer('保存修改','travel-review'),body:`${head('修改时间与地点','照片 1',false)}<div class="photo landscape mb">${scenic()}</div>${select('拍摄日期','2026年10月18日')}${select('当地时刻（选填）','14:30')}${select('地点','杭州 · 西湖')}${field('一句话记录（选填）','和小禾在湖边散步。')}<p class="small">已有日期和地点可按真实情况修正。</p>`};
 case 'travel-confirm':return {back:'travel-review',...footer('确认加入旅行日记','travel-detail'),body:`${head('确认入档','3 / 3 · 最后核对',false)}<div class="card"><div class="flex mb"><span class="mark big">${icon('pin')}</span><div><h2>小禾 · 2 张照片</h2><p class="small">10月18日 · 杭州</p></div></div><div class="photos-grid"><div class="photo landscape">${scenic()}</div><div class="photo landscape">${scenic(1)}</div></div></div><p class="muted mt">确认孩子在这些日期实际到访过所选地点。</p>${notice('确认后可在旅行日记中回看。')}`};
 case 'travel-settings':return sheetOver(travelTheme(),'足迹设置',`<button type="button" class="toggle-row" data-toggle><span class="grow"><strong>AI 地点候选</strong><span class="small" style="display:block">给出可编辑建议，入档前由家长核对。</span></span><span class="switch"></span></button>${btn('保存设置','travel','mt')}${btn('查看已归档孩子','archive-list','outline mt')}`);
 case 'travel-detail':return {back:'travel',body:`${head('照片与到访详情','小禾 · 家长已确认',false)}<div class="photo landscape" style="height:200px">${scenic()}</div><div class="card mt"><h2>杭州 · 西湖</h2><p class="mt8">和小禾在湖边散步。</p><div class="divider"></div><div class="info-kv"><span>拍摄日期</span><strong>10月18日 14:30</strong></div><div class="info-kv"><span>确认时间</span><strong>10月18日 20:15</strong></div></div>${btn('修改时间与地点','travel-edit','outline mt')}${btn('返回旅行日记','travel','outline mt')}`};
 case 'child-archive':return simpleDialog(getScene('child'),'归档小禾？','归档后暂停新增学习与安排，已有记录保留，需要时可以恢复。','确认归档','继续保留','archive-list');
 case 'archive-list':return {back:'settings',body:`${head('已归档档案','记录仍然保留',false)}<div class="card"><div class="flex"><span class="avatar">禾</span><div class="grow"><h2>小禾</h2><p class="small">小学二年级 · 已归档</p></div></div>${btn('恢复档案','child','outline mt')}${btn('查看已有旅行日记','travel','outline mt')}</div>${notice('恢复后可继续使用这个档案的学习和活动功能。')}`};
 case 'family-role':return sheetOver(members(),'外婆的权限',`<p class="small mb">权限用于当前家庭</p>${[['只读','可以查看家庭记录'],['可编辑','可以记录和修改学习、活动内容']].map(([n,d],i)=>`<button type="button" class="review-choice ${i===0?'active':''}" data-choice><span class="check ${i===0?'checked':''}">${i===0?icon('check'):''}</span><span><strong>${n}</strong><span class="small" style="display:block">${d}</span></span></button>`).join('')}${btn('保存权限','family-members','mt')}`);
 case 'notification-renew':return simpleDialog(today(),'开启提醒授权提示？','在记录复习反馈后，帮助你继续申请下一次提醒。只有你允许后，微信才会发送提醒。','开启','暂不开启','notifications');
 case 'theme-picker':return {back:'settings',body:`${head('界面风格','换一种陪伴的心情',false)}<button type="button" class="theme-card" data-demo="原始风格沿用当前产品，本轮不重绘"><span class="mark">${icon('sprout')}</span><span class="grow"><strong>原始风格</strong><span class="small" style="display:block">沿用当前界面</span></span></button>${THEMES.map(t=>`<button type="button" class="theme-card" data-theme-choice="${t.id}" aria-pressed="${currentTheme===t.id}"><span class="theme-thumb" data-theme="${t.id}"></span><span class="grow"><strong>${t.name}</strong><span class="small" style="display:block">${t.fallback} · 默认图标</span></span>${currentTheme===t.id?icon('check'):''}</button>`).join('')}`};
 default:return originalScene(id);
 }
};
formScenes.push('subject-edit','manual-input','travel-edit');
const baseRender=renderPhone;
renderPhone=function(id){
 const valid=sceneDefs.some(s=>s.id===id)?id:'settings';
 document.body.dataset.theme=currentTheme;
 baseRender(valid);
 document.querySelectorAll('.page-head').forEach(el=>el.insertAdjacentHTML('afterbegin',`<img class="hero-art" src="${THEME_ART[currentTheme]}" alt="">`));
 document.body.classList.toggle('is-detail',!['settings','settings-routines','today','calendar','records','reports','travel','travel-map','travel-playback','record-history','empty','loading','error','saved','voice-recording'].includes(valid));
 if(valid==='family-onboarding')document.querySelector('.content').insertAdjacentHTML('afterbegin','<div class="onboard-art" aria-hidden="true"></div>');
 document.querySelector('.onboard-art')?.insertAdjacentHTML('afterbegin',`<img class="hero-art" src="${THEME_ART[currentTheme]}" alt="">`);
 document.querySelectorAll('.theme-thumb').forEach(el=>el.innerHTML=`<img src="${THEME_ART[el.dataset.theme]}" alt="">`);
 document.querySelectorAll('.row[data-demo*="权限"]').forEach(el=>el.addEventListener('click',()=>renderPhone('family-role')));
 document.querySelectorAll('[data-theme-choice]').forEach(el=>el.addEventListener('click',()=>{currentTheme=el.dataset.themeChoice;renderPhone('theme-picker');if(parent!==window)parent.postMessage({type:'design-theme',theme:currentTheme},location.origin==='null'?'*':location.origin);}));
 const modal=document.querySelector('[role="dialog"]');if(modal)document.querySelector('.native-nav').inert=true;
 document.querySelectorAll('[data-toggle]').forEach(el=>el.setAttribute('aria-pressed',String(!el.querySelector('.switch')?.classList.contains('off'))));
 window.DESIGN_READY=true;
 window.ACTIVE_DESIGN={theme:currentTheme,scene:valid};
 if(valid==='family-delete'){const input=document.querySelector('input'),button=document.getElementById('family-delete-final');input.addEventListener('input',()=>button.disabled=input.value!=='小禾的家');button.addEventListener('click',()=>demoToast('确认状态示例，未清理任何资料'));}
};
window.setPreview=(theme,scene)=>{if(THEMES.some(t=>t.id===theme))currentTheme=theme;renderPhone(scene);};
window.addEventListener('message',e=>{if(parent!==window&&e.source===parent&&e.data?.type==='preview-command'&&THEMES.some(t=>t.id===e.data.theme)&&sceneDefs.some(s=>s.id===e.data.scene))window.setPreview(e.data.theme,e.data.scene);});
document.addEventListener('keydown',e=>{
 const modal=document.querySelector('[role="dialog"]');if(!modal)return;
 const focusable=[...modal.querySelectorAll('button:not(:disabled),input:not(:disabled),textarea,a[href]')].filter(n=>n.getClientRects().length);
 if(e.key==='Tab'&&focusable.length){const i=focusable.indexOf(document.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();focusable.at(-1).focus();}else if(!e.shiftKey&&i===focusable.length-1){e.preventDefault();focusable[0].focus();}}
 if(e.key==='Escape'){const close=modal.querySelector('[aria-label="关闭"]')||[...modal.querySelectorAll('button')].find(b=>/取消|继续保留|暂不开启|继续编辑/.test(b.textContent));close?.click();}
});
