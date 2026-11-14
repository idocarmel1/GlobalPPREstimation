const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const base=path.resolve(__dirname,'../../project_core/maps'),modulePath=path.join(base,'model_preferences.js');
let preferences;
if(fs.existsSync(modulePath))preferences=require(modulePath);
else{
  const html=fs.readFileSync(path.join(base,'original_html_layout/index.html'),'utf8');
  const context={URL,URLSearchParams};vm.createContext(context);
  vm.runInContext(html.slice(html.indexOf('/* Compact preferences'),html.indexOf('/* Shared group picker.')),context);
  preferences=context.PPRGroupSettings;
}
const legacyKey='GlobalPPR:group-settings:v1:/interactive_map/';
const key='GlobalPPR:group-settings:v2:/interactive_map/';
const units={LME_022:{default_model:1,models:[{id:'Scotland'},{id:'ICES',researcher_review:{status:'Validated by researcher'}}]},LME_038:{default_model:0,models:[{id:'Java'}]}};
function environment({data=null,view='',mapView='',url='http://localhost/interactive_map/index.html'}={}){
  const values=new Map(),listeners={};
  const sourceKey=data?.version===1?legacyKey:key;
  if(data)values.set(sourceKey,JSON.stringify(data));
  if(view)values.set(sourceKey+':trends',view);
  if(mapView)values.set(sourceKey+':map',mapView);
  const env={location:{href:url},localStorage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>values.set(k,v)},
    history:{replaceState(_a,_b,url){env.location.href=new URL(url,env.location.href).href;}},addEventListener:(type,fn)=>{listeners[type]=fn;}};
  return {env,values,listeners};
}
const plain=value=>JSON.parse(JSON.stringify(value));
const legacy={version:1,models:{LME_022:'Scotland',LME_038:'Java'},selections:{'LME_022::Scotland':['Fish']},tables:{'LME_022::Scotland':{query:'fish'}}};
let browser=environment({data:legacy}),store=preferences.create({env:browser.env,view:'map',units});
assert.deepEqual(plain(store.data.models),{},'An untouched legacy Scotland default must not override the newly published ICES default');
assert.deepEqual(plain(store.data.legacy_models),legacy.models,'Ambiguous legacy model choices must remain recoverable');
assert.deepEqual(plain(store.data.selections),legacy.selections);assert.deepEqual(plain(store.data.tables),legacy.tables);
store.save(new URLSearchParams('metric=ppr'));
assert.deepEqual(JSON.parse(browser.values.get(key)).models,{},'Saving a view must not invent explicit model choices');
browser=environment({data:legacy,mapView:'metric=ppr&models='+encodeURIComponent(JSON.stringify({LME_022:'Scotland'}))});
store=preferences.create({env:browser.env,view:'trends',units});
assert.deepEqual(plain(store.data.models),{LME_022:'Scotland'},'Recover the old map view\'s recorded explicit nondefault choice');
browser=environment({data:legacy,view:'models='+encodeURIComponent(JSON.stringify(legacy.models))});
store=preferences.create({env:browser.env,view:'trends',units});
assert.deepEqual(plain(store.data.models),{},'Legacy trends view copied defaults and cannot establish explicit model intent');
browser=environment({data:{version:2,models:{LME_022:'Scotland'}},url:'http://localhost/interactive_map/index.html?models='+encodeURIComponent(JSON.stringify({LME_022:'ICES'}))});
store=preferences.create({env:browser.env,units});
assert.deepEqual(plain(store.data.models),{},'Direct URL selection must outrank stored Scotland and follow current ICES default');
store.selectModel('LME_022','Scotland');store.save();
assert.deepEqual(plain(store.data.models),{LME_022:'Scotland'},'Deliberate unvalidated alternatives remain selectable');
store.selectModel('LME_022','ICES');store.save();assert.deepEqual(plain(store.data.models),{});
store.selectModel('LME_022','Scotland');let notifications=0;store.subscribe(()=>notifications++);store.resetModels();
assert.deepEqual(plain(store.data.models),{});assert.equal(notifications,1,'Reset must update the current page');
store.selectModel('LME_022','Scotland');
browser.listeners.storage({key,newValue:JSON.stringify({version:2,models:{},selections:{},tables:{}})});
assert.deepEqual(plain(store.data.models),{});assert.equal(notifications,2,'Cross-tab reset must replace, not merge, active model choices');
browser=environment({url:'http://localhost/interactive_map/index.html?models='+encodeURIComponent(JSON.stringify({LME_022:0,LME_038:0,missing:'fake'}))});
store=preferences.create({env:browser.env,units});
assert.deepEqual(plain(store.data.models),{LME_022:'Scotland'},'Numeric URL choices resolve to stable IDs; defaults and unknown units add no override');
browser=environment({data:{version:2,models:{LME_022:'deleted'},selections:legacy.selections,tables:legacy.tables}});
store=preferences.create({env:browser.env,units});assert.deepEqual(plain(store.data.models),{});
assert.deepEqual(plain(store.data.selections),legacy.selections);
browser=environment({data:legacy});
const untouchedLegacy=browser.values.get(legacyKey);
store=preferences.create({env:browser.env,units});
assert.equal(browser.values.get(legacyKey),untouchedLegacy,'Migration must leave the old tab\'s v1 store unchanged');
assert(browser.values.has(key),'Active preferences require an isolated v2 store');
store.selectModel('LME_022','Scotland');store.save();
browser.listeners.storage({key:legacyKey,newValue:JSON.stringify({...legacy,models:{LME_022:'ICES'}})});
assert.equal(store.data.models.LME_022,'Scotland','An old page event must not overwrite an explicit v2 choice');
store.resetModels();
browser.listeners.storage({key:legacyKey,newValue:JSON.stringify(legacy)});
assert.deepEqual(plain(store.data.models),{},'An old page cannot reinstate a retired default');
// Exercise the real frozen v1 store while it remains open, including its
// old map subscriber that saves every chosen model after storage events.
{
  const html=fs.readFileSync(path.join(base,'original_html_layout/index.html'),'utf8'),context={URL,URLSearchParams};
  vm.createContext(context);vm.runInContext(html.slice(html.indexOf('/* Compact preferences'),html.indexOf('/* Shared group picker.')),context);
  const shared=new Map([[legacyKey,JSON.stringify(legacy)],[legacyKey+':map','metric=ratio'],[legacyKey+':trends','metric=npp']]),queue=[],tabs=[];
  function tab(){const result=environment();result.env.localStorage={getItem:k=>shared.get(k)??null,setItem(k,v){const old=shared.get(k);shared.set(k,v);if(old!==v)for(const other of tabs)if(other!==result)queue.push(()=>other.listeners.storage?.({key:k,newValue:v}));}};tabs.push(result);return result;}
  const oldTab=tab(),oldStore=context.PPRGroupSettings.create({env:oldTab.env});
  oldStore.subscribe(()=>{oldStore.data.models.LME_022='Scotland';oldStore.save();});
  const oldBytes=shared.get(legacyKey),newTab=tab(),newStore=preferences.create({env:newTab.env,units});
  newStore.subscribe(()=>newStore.save());let events=0;
  function flush(){while(queue.length){assert(++events<50,'Old/new pages must not enter a storage ping-pong');queue.shift()();}}
  flush();assert.equal(shared.get(legacyKey),oldBytes);assert.deepEqual(plain(newStore.data.models),{});
  assert.equal(new URLSearchParams(shared.get(key+':map')).get('metric'),'ratio');
  assert.equal(new URLSearchParams(shared.get(key+':trends')).get('metric'),'npp');
  oldStore.data.models.LME_022='ICES';oldStore.save();flush();assert.deepEqual(plain(newStore.data.models),{});
  newStore.selectModel('LME_022','Scotland');newStore.save();flush();
  oldStore.data.models.LME_022='Scotland';oldStore.save();flush();assert.equal(newStore.data.models.LME_022,'Scotland');
  newStore.resetModels();flush();assert.deepEqual(plain(newStore.data.models),{});assert.equal(queue.length,0);
}
console.log('Model preferences: legacy migration, explicit overrides, URL precedence, reset, cross-tab replacement and protected group/table preferences passed.');
const input=fs.readFileSync(0,'utf8');
if(input.trim()){
  const layouts=JSON.parse(input);
  function section(html,start,end){const a=html.indexOf(start),b=html.indexOf(end,a);assert(a>=0&&b>a,start);return html.slice(a,b);}
  for(const [name,html] of Object.entries(layouts)){
    for(const [,script] of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))if(script.trim())new vm.Script(script);
    assert(html.includes('id="resetModelChoices"'),'Project-default recovery is visible in '+name);
    browser=environment({data:legacy});store=preferences.create({env:browser.env,view:name==='map'?'map':'trends',units});
    const context={groupStore:store,URLSearchParams,network:{units},mapParams:store.params,metricState:{},
      params:store.params,DB:{year:2019},db:{units},initialSet:{id:'global',units:Object.keys(units)},initialMethods:[],
      $:()=>null,applyYear(){},update(){},groupDialog:{refresh(){}}};
    vm.createContext(context);
    if(name==='map'){
      vm.runInContext(section(html,'const chosenModels =','const $ =')+'globalThis.choices=chosenModels;',context);
      assert.equal(context.choices.LME_022,1);assert.equal(context.choices.LME_038,0);
      context.params=new URLSearchParams();
      vm.runInContext(section(html,'  const overrides=Object.fromEntries(Object.entries(chosenModels)','  try{history.replaceState'),context);
      assert.deepEqual(plain(store.data.models),{},'Actual map save path must not persist untouched defaults');
      context.choices.LME_022=0;
    }else{
      vm.runInContext(section(html,'  const models={...groupStore?.data.models};','  let result,')+'globalThis.choices=state;',context);
      assert.deepEqual(plain(context.choices.models),{},'Actual trends bootstrap must use migrated model intent');
      context.choices.models.LME_022='Scotland';
    }
    const subscription=html.match(/groupStore\.subscribe\(\(\)=>\{[^\n]*\}\);/);
    assert(subscription,'Actual cross-tab subscription in '+name);vm.runInContext(subscription[0],context);
    store.selectModel('LME_022','Scotland');store.resetModels();
    if(name==='map')assert.equal(context.choices.LME_022,1,'Map reset returns to the published ICES default');
    else assert.deepEqual(plain(context.choices.models),{},'Trends reset removes stale overrides');
  }
  console.log('Both generated layouts: syntax, migrated bootstrap, map save, project-default control and actual reset subscriptions passed.');
}
