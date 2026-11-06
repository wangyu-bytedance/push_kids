const child={id:'synthetic',name:'合成孩子',active:true,
grade:'三年级',avatar:'合'};
module.exports={
newIdempotencyKey:()=> 'synthetic-key',
request:async function(url,options={}){
  if(options.method&&options.method!=='GET')throw Error('Synthetic copy forbids writes');
  if(url==='/me')return {state:'bound',family:{id:'synthetic'},member:{role:'manager'},children:[child]};
  if(url==='/children')return [child];
  if(url.includes('/history?'))return {items:[],pending_count:0,has_processing:false,next_cursor:null};
  if(url.includes('/report?'))return {subjects:[],overview:{learning_records:1,new_knowledge_items:1,
    review_feedback_count:0,activity_records:0},review_urgency:[],review_activity:[],activity_subjects:[]};
  if(url.includes('/review-inventory/subjects?'))return {items:[{id:'english',name:'英语',count:42}],next_cursor:null};
  if(url.includes('/review-inventory?')){
    const fixture=getApp().globalData.footerFixture;
    if(fixture){
      fixture.calls=(fixture.calls||0)+1;
      if(fixture.hold)return new Promise((resolve,reject)=>{
        fixture.release=()=>fixture.fail?reject(Error('合成读取失败')):resolve(JSON.parse(fixture.payload));
      });
      if(fixture.fail)throw Error('合成读取失败');
      return JSON.parse(fixture.payload);
    }
    return {items:[],total:0,next_cursor:null,as_of_day:'2026-11-01',child_writable:true};
  }
  return {};
}}
