const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createRequire} = require('node:module');
const {createHash} = require('node:crypto');
const ROOT = path.resolve(__dirname, '../../../..');
const DREV = 'DREV-20261021-HERO-ARC-REMOVAL-01';
const renderer = path.join(ROOT, 'tools/preview/render.js');
const originalRequire = createRequire(renderer);
const fixtures = {...originalRequire('./fixtures.js')};
const notifications = {page:'pages/notifications',tabBar:null,data:{loading:false,error:'',supported:true,channelAvailable:true,channelReason:'',items:[],grantCount:0,granting:false,togglingType:'',lastSentLabel:'',deliveries:[],deliveriesError:'',autoEnabled:false,autoSaving:false,heroTitle:'提醒已准备好',heroReady:true}};
fixtures['notifications-ready'] = notifications;
fixtures['notifications-neutral'] = {...notifications,data:{...notifications.data,heroReady:false,heroTitle:'提醒次数待补充'}};
const designRequire = Object.assign(name=>name==='./fixtures.js'?fixtures:originalRequire(name),originalRequire);
vm.runInNewContext(fs.readFileSync(renderer,'utf8'),{require:designRequire,__dirname:path.dirname(renderer),global,process:{argv:[process.execPath,renderer]},console:{log(){}}},{filename:renderer});
const normalize = text=>text.replaceAll('右上角一抹嫩芽光，右下角一道年轮弧线','右上角一抹嫩芽光').replace(/<style>([\s\S]*?)<\/style>/g,(_,css)=>'<style>'+css.replace(/\n{2,}/g,'\n')+'</style>');
const sha = bytes=>createHash('sha256').update(bytes).digest('hex');
const records=[];
const sourceDir=path.join(ROOT,'docs/design/frontend/prototypes',DREV);
for(const file of fs.readdirSync(sourceDir).filter(name=>/-(320x568|390x844|430x932)\.html$/.test(name))) {
  const match=file.match(/^(.*)-(\d+)x(\d+)\.html$/), state=match[1],width=Number(match[2]),height=Number(match[3]);
  const preview=path.join(ROOT,'dist/ui-preview',`${state}-${width}.html`);
  const current=normalize(fs.readFileSync(preview,'utf8').replace(/src="([^"]+\.png)"/g,(_,reference)=>`src="data:image/png;base64,${fs.readFileSync(path.resolve(path.dirname(preview),reference)).toString('base64')}"`));
  const approved=normalize(fs.readFileSync(path.join(sourceDir,file),'utf8'));
  if(current!==approved) throw Error(`Current production preview differs from approved candidate: ${file}`);
  if(current.includes('.pk-hero::after'))throw Error(`Arc remains: ${file}`);
  records.push({state,width,height,approvedHtml: file,normalizedHtmlSha256:sha(current),matchesApproved:true});
}
const allRendered=fs.readdirSync(path.join(ROOT,'dist/ui-preview')).filter(name=>/-(320|390|430)\.html$/.test(name));
for(const file of allRendered)if(fs.readFileSync(path.join(ROOT,'dist/ui-preview',file),'utf8').includes('.pk-hero::after'))throw Error(`Arc remains in rendered page ${file}`);
const evidenceDir=path.join(ROOT,'docs/quality/evidence/hero-arc-removal-20261021');
fs.mkdirSync(evidenceDir,{recursive:true});
fs.writeFileSync(path.join(evidenceDir,'approved-parity.json'),JSON.stringify({matches:records.length,records},null,2)+'\n');
const native='/private/tmp/push-kids-hero-arc-native-20261021';
const appSource=path.join(ROOT,'apps/miniprogram');
fs.cpSync(appSource,native,{recursive:true});
const names=['today','records','calendar','reports','settings','family-members','notifications-ready'];
const pages=names.map(name=>fixtures[name].page+'/index');
const appConfig=JSON.parse(fs.readFileSync(path.join(appSource,'app.json'),'utf8'));
appConfig.pages=pages;
delete appConfig.plugins;
fs.writeFileSync(path.join(native,'app.json'),JSON.stringify(appConfig,null,2));
fs.writeFileSync(path.join(native,'app.js'),'App({globalData:{useCloud:false,familyId:"synthetic",selectedChildId:"synthetic",currentMember:{role:"manager"}}});\n');
fs.writeFileSync(path.join(native,'utils/api.js'),'exports.request=()=>Promise.reject(Error("isolated: no business API"));exports.newIdempotencyKey=()=>"synthetic";\n');
for(const name of names){
 const fixture=fixtures[name],extra={normal:fixtures[name].data,...(name==='today'?{guide:fixtures['today-guide'].data}:name==='notifications-ready'?{neutral:fixtures['notifications-neutral'].data}:{})};
 fs.writeFileSync(path.join(native,fixture.page,'index.js'),'const variants='+JSON.stringify(extra)+';Page({data:'+JSON.stringify(fixture.data)+',applyArcFixture(name){this.setData(variants[name]||{});}});\n');
}
const project=JSON.parse(fs.readFileSync(path.join(appSource,'project.config.json'),'utf8'));
project.projectname='hero-arc-native-20261021';
project.libVersion='3.17.4';
project.setting.lazyloadPlaceholderEnable=false;
fs.writeFileSync(path.join(native,'project.config.json'),JSON.stringify(project,null,2));
const markupHashes=[];
for(const file of ['app.wxss','styles/atoms.wxss',...names.flatMap(name=>[fixtures[name].page+'/index.wxml',fixtures[name].page+'/index.wxss'])]) {
 const sourceHash=sha(fs.readFileSync(path.join(appSource,file))),nativeHash=sha(fs.readFileSync(path.join(native,file)));
 if(sourceHash!==nativeHash)throw Error('Native source drift '+file);
 markupHashes.push({file,sourceSha256:sourceHash,nativeSha256:nativeHash});
}
fs.writeFileSync(path.join(evidenceDir,'native-source-hashes.json'),JSON.stringify(markupHashes,null,2)+'\n');
console.log(`PASS: ${records.length} approved viewport/state HTMLs match current production rendering after comment and CSS blank-line normalization; ${allRendered.length} existing HTML previews contain no arc. Isolated native project: ${native}`);
