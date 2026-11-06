// Official DevTools native rectangles; requires prepare_travel_diary_native.py.
const fs = require("node:fs"), path = require("node:path"), crypto = require("node:crypto");
const width = Number(process.argv[2]), port = Number(process.argv[3] || 9586);
const out = path.resolve("docs/quality/evidence/travel-diary-e2e-20261025/native");
const socket = new WebSocket(`ws://127.0.0.1:${port}`), pending = new Map(); let sequence = 0;
socket.onmessage = ({ data }) => { const m = JSON.parse(data); pending.get(m.id)?.(m); };
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = String(++sequence), timer = setTimeout(() => { pending.delete(id); reject(Error(method + " timeout")); }, 15000);
    pending.set(id, m => { pending.delete(id); clearTimeout(timer); m.error ? reject(Error(JSON.stringify(m.error))) : resolve(m.result); });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
const call = async (functionDeclaration, args = []) => (await send("App.callFunction", { functionDeclaration, args })).result;
const selectors = [".fp-sheet", ".fp-sheet-head", ".fp-sheet-head .fp-place-title", ".fp-sheet-body", ".fp-sheet-footer", ".fp-sheet-footer .fp-button", ".fp-close", ".fp-text-button", ".fp-select", ".fp-input", ".fp-tab", ".fp-import", ".fp-draft", ".fp-edit-image", ".fp-field-error"];
const fixture = `function(state){const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary');p.pausePlayback();if(p.pollTimer)clearTimeout(p.pollTimer);
  const image='/assets/illustrations/record-camera.png',photo={id:'synthetic-2',import_id:'synthetic-import',version:2,state:'ready',job_state:'succeeded',has_display:false,local_date:null,dateLabel:'待补日期',placeLabel:'大连 · 合成地点的较长名称用于验证窄屏完整换行',statusLabel:'待核对',expiryLabel:'合成到期时间',previewUrl:image,selected:true,candidates:[]};
  const data={loading:false,error:'',canWrite:true,child:{id:'synthetic',name:'合成孩子',active:true},childId:'synthetic',mode:'timeline',sheet:'',sheetError:'',saving:false,selecting:false,dateOnly:false,manual:false,batchEdit:false,editConflict:false,keyboardHeight:0,photoConsent:false,aiEnabled:false,hasPendingUpload:false,missingDateCount:1,selectedCount:3,drafts:[photo,{...photo,id:'synthetic-1'},{...photo,id:'synthetic-0'}],form:{local_date:'',local_time:'',place_name:'合成测试地点',city:'大连',country:''},editing:photo,placeResults:[],photoList:[{...photo,local_date:'2020-01-01',dateLabel:'2020-01-01'}],photoIndex:0,hasPreviousPhotoPage:true,photoCursor:null,loadingPhoto:false,confirmCount:3,unlocatedCount:3,summary:{photos:3,places:1,cities:1},visits:[{id:'synthetic-visit',local_date:'2020-01-01',photo_count:3,place_name:'合成测试地点',photos:[{...photo,timeLabel:'时刻未知'}]}]};
  if(['consent','uploading'].includes(state)){data.sheet='consent';data.saving=state==='uploading';data.importProgress=67;data.photoConsent=data.saving;}
  if(['review-missing','review-ready','upload-error','processing-error'].includes(state)){data.sheet='review';if(state==='review-ready'){data.missingDateCount=0;data.drafts.forEach(p=>{p.local_date='2020-01-01';p.dateLabel='2020-01-01';});}if(state==='upload-error'){data.sheetError='上传中断，已上传照片保留';data.hasPendingUpload=true;}if(state==='processing-error'){data.drafts[0].job_state='failed';data.drafts[0].statusLabel='解析失败，可手动补充';}}
  if(['batch-date','edit','conflict','edit-keyboard'].includes(state)){data.sheet='edit';if(state==='batch-date'){data.batchEdit=true;data.dateOnly=true;data.editing=null;}if(state==='conflict'){data.editConflict=true;data.sheetError='其他家长已修改，请读取最新版本';}if(state==='edit-keyboard')data.keyboardHeight=210;}
  if(state==='confirm')data.sheet='confirm';if(state==='gallery-focused')data.sheet='photo';if(state==='readonly')data.canWrite=false;
  p.applyGeometryFixture(JSON.stringify(data));return true;}`;
async function capture(state) {
  await call(fixture, [state]);
  await new Promise(resolve => setTimeout(resolve, 120));
  const data = await call(`function(selectors){return new Promise(resolve=>{const p=getCurrentPages().slice(-1)[0].selectComponent('#travel-diary'),q=wx.createSelectorQuery().in(p),i=wx.getSystemInfoSync();selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true,computedStyle:['fontSize']}));q.selectViewport().scrollOffset();q.exec(rows=>{const nodes={};selectors.forEach((s,k)=>nodes[s]=(rows[k]||[]).filter(r=>r.width&&r.height));resolve({nodes,scrollLeft:rows[selectors.length]?.scrollLeft||0,viewport:{width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion},sheet:p.data.sheet,keyboardHeight:p.data.keyboardHeight});});});}`, [selectors]);
  const errors = [], check = (ok, message) => { if (!ok) errors.push(message); };
  check(data.viewport.width === width && data.viewport.screenHeight === { 320: 568, 390: 844, 430: 932 }[width], "viewport mismatch");
  check(data.scrollLeft === 0, "horizontal root scroll");
  for (const [selector, rows] of Object.entries(data.nodes)) for (const r of rows) {
    check(r.left >= -1 && r.right <= width + 1, selector + " horizontal overflow");
    if ([".fp-close", ".fp-text-button", ".fp-select", ".fp-input", ".fp-tab", ".fp-import", ".fp-sheet-footer .fp-button"].includes(selector)) check(r.width >= 43 && r.height >= 43, selector + " target below 44px");
    if (r.fontSize && selector !== ".fp-close") check(parseFloat(r.fontSize) >= 14, selector + " font below 14px");
  }
  const sheet = data.nodes[".fp-sheet"][0], footer = data.nodes[".fp-sheet-footer"][0], close = data.nodes[".fp-close"][0], title = data.nodes[".fp-sheet-head .fp-place-title"][0];
  if (sheet) {
    check(sheet.top >= -1 && footer.bottom <= data.viewport.height - data.keyboardHeight + 1, "sheet actions outside available window");
    check(title.right <= close.left - 7, "sheet title overlaps close");
    check(data.nodes[".fp-sheet-body"][0].height >= 44, "scroll body too short");
  }
  for (const r of data.nodes[".fp-sheet-footer .fp-button"]) check(r.height >= 47 && parseFloat(r.fontSize) >= 16, "primary dimensions");
  const shot = await send("App.captureScreenshot"), bytes = Buffer.from((typeof shot === "string" ? shot : shot.data || shot.base64).replace(/^data:image\/\w+;base64,/, ""), "base64");
  fs.mkdirSync(out, { recursive: true }); const name = `${state}-${width}`;
  fs.writeFileSync(path.join(out, name + ".png"), bytes);
  fs.writeFileSync(path.join(out, name + ".json"), JSON.stringify({ ...data, state, errors, capturedAt: new Date().toISOString(), screenshotSha256: crypto.createHash("sha256").update(bytes).digest("hex") }, null, 2) + "\n");
  console.log(name + ": " + (errors.join("; ") || "PASS")); return errors.length;
}
async function main() {
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  if (!await call("function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==='synthetic';}")) throw Error("Offline synthetic copy required");
  await call("function(){return new Promise(resolve=>wx.switchTab({url:'/pages/records/index',success:()=>resolve(true)}));}");
  await call("function(){return getCurrentPages().slice(-1)[0].selectRecordType({currentTarget:{dataset:{type:'travel'}}}).then(()=>true);}");
  let failures = 0;
  for (const state of ["consent", "uploading", "review-missing", "batch-date", "edit", "review-ready", "upload-error", "processing-error", "conflict", "confirm", "saved", "gallery-focused", "readonly", "edit-keyboard"]) failures += await capture(state);
  socket.close(); process.exitCode = failures ? 1 : 0;
}
main().catch(error => { console.error(error.message); socket.close(); process.exitCode = 1; });
