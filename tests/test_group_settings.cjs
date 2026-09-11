const {test}=require('node:test');
const assert=require('node:assert/strict');
const settings=require('../PPRAtlas/atlas/group_settings.js');
const ui=require('../PPRAtlas/atlas/group_ui.js');
function env(href,storage=new Map()){
  const e={location:{href},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},addEventListener(){}};
  e.history={replaceState(_state,_title,url){e.location.href=new URL(url,e.location.href).href;}};
  return e;
}
test('table-only edits update the current URL so reload cannot restore stale preferences',()=>{
  const disk=new Map(),e=env('file:///project/index.html',disk),store=settings.create({env:e,view:'map'});
  store.data.tables['a::m']={sort:'tl',direction:'desc',query:'fish',method:'new_GE',ranges:{te:{min:'.1'}}};
  store.save();
  const reload=settings.create({env:env(e.location.href,disk),view:'map'});
  assert.deepEqual(reload.data.tables,store.data.tables);
});
test('local reopen and cross-view URLs preserve explicit empty selections and model overrides',()=>{
  const disk=new Map(),first=settings.create({env:env('file:///project/index.html',disk),view:'map'});
  first.data.selections['a::m']=[];first.data.models.a='m';first.save(new URLSearchParams('method=MC_new_GE'));
  const reopened=settings.create({env:env('file:///project/index.html',disk),view:'map'});
  assert.deepEqual(reopened.data.selections['a::m'],[]);assert.equal(reopened.params.get('method'),'MC_new_GE');
  const other=settings.create({env:env(first.link('trends.html'),new Map()),view:'trends'});
  assert.deepEqual(other.data.selections['a::m'],[]);assert.equal(other.data.models.a,'m');
  delete other.data.selections['a::m'];
  const cleared=settings.create({env:env(other.link('index.html'),disk),view:'map'});
  assert.deepEqual(cleared.data.selections,{});
});
test('malformed saved data and blocked browser storage retain working URL transfer',()=>{
  const e=env('file:///project/index.html?group_settings=invalid');
  e.localStorage={getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}};
  const store=settings.create({env:e,view:'map'});store.data.selections['a::m']=['Fish'];
  assert.doesNotThrow(()=>store.save());assert.equal(store.storageAvailable,false);
  assert.match(store.link('trends.html'),/group_settings=/);
});
test('range filters combine with names and sorting keeps unavailable values last',()=>{
  const rows=[{id:'fish',name:'Fish',te:.2,tl:4,ppr:100},{id:'bird',name:'Bird',te:null,tl:4,ppr:50},{id:'shark',name:'Shark',te:.1,tl:5,ppr:200}];
  assert.deepEqual(ui.filterRows(rows,{query:'sh',ranges:{tl:{min:4.5},ppr:{max:250}}}).map(r=>r.id),['shark']);
  assert.deepEqual(ui.sortRows(rows,'te','asc').map(r=>r.id),['shark','fish','bird']);
  assert.deepEqual(ui.sortRows(rows,'te','desc').map(r=>r.id),['fish','shark','bird']);
});
