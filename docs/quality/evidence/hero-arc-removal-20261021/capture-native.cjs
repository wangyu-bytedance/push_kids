const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname, '../../../..');
const width=Number(process.argv[2]);
if(![320,390,430].includes(width))throw Error('Expected width 320,390,430');
const out=path.join(ROOT,'docs/quality/evidence/hero-arc-removal-20261021/native');
fs.mkdirSync(out,{recursive:true});
const selectors=['.pk-hero','.btn','.child-chip','.hero-line','.hero-note','.settings-card-art','.record-intro-art','.calendar-intro-art','.report-intro-art'];
const cases=[['today','today'],['today','guide'],['records','records'],['calendar','calendar'],['reports','reports'],['settings','settings'],['family-members','family-members'],['notifications','notifications-ready'],['notifications','neutral']];
const socket=new WebSocket('ws://127.0.0.1:9443');
let seq=0;const pending=new Map();
socket.onmessage=e=>{const m=JSON.parse(e.data),cb=pending.get(m.id);if(cb){pending.delete(m.id);cb(m);}};
const send=(method,params={})=>new Promise((resolve,reject)=>{const id=String(++seq),timer=setTimeout(()=>{pending.delete(id);reject(Error(method+' timeout'));},method==='App.captureScreenshot'?10000:15000);pending.set(id,m=>{clearTimeout(timer);m.error?reject(Error(method+' failed '+JSON.stringify(m.error))):resolve(m.result);});socket.send(JSON.stringify({id,method,params}));});
const call=(functionDeclaration,args=[])=>send('App.callFunction',{functionDeclaration,args});
async function shot(name){try{const result=await send('App.captureScreenshot'),base64=typeof result==='string'?result:result.data||result.base64;const bytes=Buffer.from(base64.replace(/^data:image\/\w+;base64,/,''),'base64'),file=path.join(out,`${name}-${width}.png`);fs.writeFileSync(file,bytes);return {file:path.basename(file),sha256:crypto.createHash('sha256').update(bytes).digest('hex')};}catch{return {file:'NOT_RUN',reason:'native screenshot API timed out or failed; numeric geometry retained'};}}
async function main(){
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
 try{
  if(!(await call('function(){return getApp().globalData.useCloud===false&&getApp().globalData.familyId==="synthetic";}')).result)throw Error('Isolated project required');
  const viewport=(await call('function(){const i=wx.getSystemInfoSync();return {width:i.windowWidth,height:i.windowHeight,screenHeight:i.screenHeight,dpr:i.pixelRatio,baseLibrary:i.SDKVersion,fontScale:i.fontSizeSetting};}')).result;
  if(viewport.width!==width||viewport.screenHeight!=={320:568,390:844,430:932}[width])throw Error('Wrong native viewport '+JSON.stringify(viewport));
  for(const [surface,state] of cases){
   const prior=path.join(out,`${state}-${width}.json`);
   if(fs.existsSync(prior)&&JSON.parse(fs.readFileSync(prior)).screenshot.file!=='NOT_RUN'&&surface!=='settings'){console.log(`NATIVE_RETAINED ${state} ${width}`);continue;}
   const wanted=`pages/${surface}/index`;
   if((await send('App.getCurrentPage')).path!==wanted){
    await call('function(method,url){return new Promise((resolve,reject)=>wx[method]({url,success:()=>resolve(true),fail:()=>reject(Error("native fixture navigation failed"))}));}',[['today','records','calendar','reports','settings'].includes(surface)?'switchTab':'navigateTo','/'+wanted]);
    for(let i=0;i<25;i++){if((await send('App.getCurrentPage')).path===wanted)break;await new Promise(r=>setTimeout(r,100));}
   }
   await call('function(state){getCurrentPages().slice(-1)[0].applyArcFixture(state);return true;}',[state==='guide'||state==='neutral'?state:'normal']);
   await call('function(){wx.pageScrollTo({scrollTop:0,duration:0});return true;}');
   await new Promise(r=>setTimeout(r,200));
   const geometry=(await call('function(selectors){return new Promise(resolve=>{const p=getCurrentPages().slice(-1)[0],q=wx.createSelectorQuery().in(p);selectors.forEach(s=>q.selectAll(s).fields({rect:true,size:true}));q.selectViewport().scrollOffset();q.exec(results=>{const nodes={};selectors.forEach((s,k)=>nodes[s]=(results[k]||[]).map(n=>({left:n.left,right:n.right,top:n.top,bottom:n.bottom,width:n.width,height:n.height})));resolve({nodes,scrollLeft:results[selectors.length].scrollLeft});});});}',[selectors])).result;
   const heroes=geometry.nodes['.pk-hero'];
   if(heroes.length!==(surface==='settings'?4:1))throw Error(state+' missing heroes: '+heroes.length);
   if(Math.abs(geometry.scrollLeft)>1||heroes.some(r=>r.left < -1 ||r.right>width+1||r.width<=0||r.height<=0))throw Error(state+' geometry invalid');
   const screenshot=await shot(state);
   fs.writeFileSync(path.join(out,`${state}-${width}.json`),JSON.stringify({state,surface,viewport,geometry,screenshot,fixture:'isolated synthetic presentation; unchanged production WXML/WXSS; no business/provider call'},null,2)+'\n');
   if(surface==='settings'){
    await call('function(top){wx.pageScrollTo({scrollTop:top,duration:0});return true;}',[heroes.at(-1).top-40]);
    await new Promise(r=>setTimeout(r,200));
    const lower=await shot('settings-lower');
    fs.writeFileSync(path.join(out,`settings-lower-${width}.json`),JSON.stringify({state:'settings-lower',viewport,screenshot:lower},null,2)+'\n');
   }
   console.log(`NATIVE_CAPTURED ${state} ${width}`);
  }
 }finally{socket.close();}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;socket.close();});
