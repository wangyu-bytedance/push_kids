let selectedReviewScene=sceneDefs.some(s=>s.id===qs.get('page'))?qs.get('page'):'today';
let reviewWidth=390,reviewHeight=844;
const themeInfo=()=>THEMES.find(t=>t.id===currentTheme);
const exportRoot='../../snapshots/UI-001/DREV-20261106-UI-CONSISTENCY-06/';
function renderGallery(){
 document.body.className='gallery-view';
 document.body.removeAttribute('data-theme');
 document.getElementById('app').innerHTML=`<div class="gallery-shell"><header class="gallery-header"><div><div class="gallery-kicker">ZHIYA / FIVE WORLDS / FULL INTERFACE REVIEW</div><h1>每一种陪伴，都有自己的世界。</h1><p>成长花园、星际探索、深海夜色、海洋与科技。原始风格保留现状。</p></div><div class="gallery-total">5 套主题 × ${sceneDefs.length} 个页面与状态<br>覆盖全部 17 条页面路由</div></header><nav class="theme-tabs" aria-label="主题">${THEMES.map(t=>`<button type="button" data-review-theme="${t.id}" aria-pressed="${currentTheme===t.id}" class="${currentTheme===t.id?'active':''}"><span class="theme-dot" style="--dot:${t.tone}"></span>${t.name}</button>`).join('')}</nav><select class="mobile-scene" aria-label="选择预览页面">${sceneDefs.map(s=>`<option value="${s.id}" ${s.id===selectedReviewScene?'selected':''}>${s.number} · ${s.title}</option>`).join('')}</select><div class="gallery-body"><nav class="scene-menu" aria-label="页面与状态">${['主页面','学习与安排','旅行与照片','家庭与设置','关键状态'].map(g=>`<section class="scene-group"><h2>${g}</h2>${sceneDefs.filter(s=>s.group===g).map(s=>`<a class="scene-link ${s.id===selectedReviewScene?'active':''}" href="?theme=${currentTheme}&page=${s.id}" data-review-scene="${s.id}"><span>${s.number}</span>${s.title}</a>`).join('')}</section>`).join('')}</nav><div class="preview-column"><div class="viewport-switch" aria-label="预览尺寸">${[[320,568],[390,844],[430,932]].map(([w,h])=>`<button type="button" data-size="${w},${h}" class="${w===reviewWidth?'active':''}">${w} × ${h}</button>`).join('')}</div><div class="device-wrap"><iframe title="知芽主题交互预览" src="?scene=${selectedReviewScene}&theme=${currentTheme}" width="${reviewWidth}" height="${reviewHeight}"></iframe></div><p class="preview-caption">页面可滚动，底部导航与表单流程可点击</p></div><aside class="review-aside"><section><div class="gallery-kicker" id="theme-material"></div><h2 id="page-title"></h2><p id="page-note"></p><div class="fallback-chip" id="fallback-note"></div></section><section><strong>查看整套设计</strong><div><a id="main-board" target="_blank">五个主页面总览 ↗</a></div><div><a id="all-board" target="_blank">全部页面与状态 ↗</a></div><div><a id="open-screen" target="_blank">单独打开当前页面 ↗</a></div></section><section><strong>本轮评审范围</strong><p>统一内容、操作顺序和表单状态；保留各主题的插画、材质、图标与卡片细节。</p><p>所有姓名、数值、照片与地图均为合成示例。保存、确认、删除只演示界面。</p></section></aside></div><footer class="gallery-footer">DESIGN-002-SPEC-06 · DREV-20261106-UI-CONSISTENCY-06 · 设计评审稿<br>原始风格未重绘。HTML预览不代表小程序已经实现换肤或通过原生、真机验收。</footer></div>`;
 document.querySelectorAll('[data-review-theme]').forEach(b=>b.addEventListener('click',()=>{currentTheme=b.dataset.reviewTheme;syncReview(true);}));
 document.querySelectorAll('[data-review-scene]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();selectedReviewScene=a.dataset.reviewScene;syncReview(true);}));
 document.querySelector('.mobile-scene').addEventListener('change',e=>{selectedReviewScene=e.target.value;syncReview(true);});
 document.querySelectorAll('[data-size]').forEach(b=>b.addEventListener('click',()=>{[reviewWidth,reviewHeight]=b.dataset.size.split(',').map(Number);layoutDevice();document.querySelectorAll('[data-size]').forEach(v=>v.classList.toggle('active',v===b));}));
 const frame=document.querySelector('iframe');frame.addEventListener('load',layoutDevice);
 window.addEventListener('resize',layoutDevice);
 window.addEventListener('message',e=>{
  if(e.source!==frame.contentWindow)return;
  if(e.data?.type==='design-scene'&&sceneDefs.some(s=>s.id===e.data.scene)){selectedReviewScene=e.data.scene;syncReview(false);}
  if(e.data?.type==='design-theme'&&THEMES.some(t=>t.id===e.data.theme)){currentTheme=e.data.theme;syncReview(false);}
 });
 syncReview(false);layoutDevice();window.DESIGN_READY=true;
}
function layoutDevice(){
 const frame=document.querySelector('iframe'),wrap=document.querySelector('.device-wrap');if(!frame)return;
 const available=document.querySelector('.preview-column').clientWidth-18;
 const scale=Math.min(1,available/reviewWidth);
 frame.width=reviewWidth;frame.height=reviewHeight;
 frame.style.cssText=`width:${reviewWidth}px;height:${reviewHeight}px;max-width:none;transform:scale(${scale});transform-origin:top left`;
 wrap.style.cssText=`width:${reviewWidth*scale+16}px;height:${reviewHeight*scale+16}px;padding:7px;overflow:hidden`;
}
function syncReview(navigate){
 const t=themeInfo(),s=sceneDefs.find(x=>x.id===selectedReviewScene);
 document.querySelectorAll('[data-review-theme]').forEach(b=>{b.classList.toggle('active',b.dataset.reviewTheme===currentTheme);b.setAttribute('aria-pressed',String(b.dataset.reviewTheme===currentTheme));});
 document.querySelectorAll('[data-review-scene]').forEach(a=>{a.classList.toggle('active',a.dataset.reviewScene===selectedReviewScene);a.setAttribute('aria-current',a.dataset.reviewScene===selectedReviewScene?'page':'false');});
 document.querySelector('.mobile-scene').value=selectedReviewScene;
 document.getElementById('theme-material').textContent=t.material;
 document.getElementById('page-title').textContent=s.title;
 document.getElementById('page-note').textContent=s.note;
 document.getElementById('fallback-note').innerHTML=icon(t.symbol)+`未预置图标：${t.fallback}`;
 document.getElementById('main-board').href=`?board=main&theme=${currentTheme}`;
 document.getElementById('all-board').href=`?board=all&theme=${currentTheme}`;
 document.getElementById('open-screen').href=`?scene=${selectedReviewScene}&theme=${currentTheme}`;
 if(navigate)document.querySelector('iframe').contentWindow.postMessage({type:'preview-command',theme:currentTheme,scene:selectedReviewScene},'*');
 const url=new URL(location.href);url.search=`?theme=${currentTheme}&page=${selectedReviewScene}`;history.replaceState({},'',url);
}
function renderBoard(mode){
 document.body.className='board-view';
 const mains=['today','calendar','records','reports','settings'];
 const items=mode==='overview'?['today','settings'].flatMap(s=>THEMES.map(t=>({theme:t.id,scene:s,label:t.name+' · '+sceneDefs.find(v=>v.id===s).title}))):(mode==='all'?sceneDefs.map(s=>s.id):mains).map(s=>({theme:currentTheme,scene:s,label:sceneDefs.find(v=>v.id===s).number+' · '+sceneDefs.find(v=>v.id===s).title}));
 const title=mode==='overview'?'五种世界，同一份陪伴。':themeInfo().name+' · '+(mode==='all'?'全部页面与关键状态':'五个主页面');
 document.getElementById('app').innerHTML=`<header class="board-head"><div class="gallery-kicker">ZHIYA / DESIGN REVIEW 06</div><h1>${title}</h1><p>${mode==='overview'?'成长花园 / 星际探索 / 深海夜色 / 海洋风格 / 科技风格':'全部页面可在交互评审页按主题、页面和尺寸切换'} · 390 × 844</p></header><main class="board-grid">${items.map(x=>`<section class="board-item"><h2>${x.label}</h2><a href="?scene=${x.scene}&theme=${x.theme}"><img src="${exportRoot}${x.theme}/${x.scene}-390x844.png" alt="${x.label}" loading="eager"></a></section>`).join('')}</main>`;
 window.DESIGN_READY=true;
}
if(qs.has('board'))renderBoard(qs.get('board'));else if(currentScene)renderPhone(currentScene);else renderGallery();
