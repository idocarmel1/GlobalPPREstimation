/* Run the actual transformed startup with fresh, saved and linked preferences. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const page=JSON.parse(fs.readFileSync(0,'utf8'));
function section(start,end){
  const a=page.indexOf(start),b=page.indexOf(end,a);
  assert(a>=0&&b>a,`Missing trend section: ${start}`);
  return page.slice(a,b);
}
const methods=['simple trophic chain','SPPR_1995_TE0.1','new_GE','new_TE_EEfix'];
const approved=(id,excluded=[])=>({id,verified:false,researcher_review:{status:'Validated by researcher'},
  display_ppr_excluded_group_ids:excluded,group_data:{groups:[{id:'fish'},{id:'bird'},{id:'mammal'}]}});
const pending={id:'pending',verified:true};
const unit=(models,default_model)=>({models,default_model,simple:{catch:[null,9,null]}});
const db={years:[1950,2000,2019],ppr_methods:methods.map(id=>({id,kind:id===methods[0]?'taxon':'model'})),
  npp_methods:[{id:'ens_median_tC_yr'}],units:{
    A:unit([approved('selected',['bird']),pending],'selected'),
    B:unit([pending,approved('alternative')],'pending'),
    C:unit([approved('numeric',['bird','mammal'])],0),
    D:unit([{id:'rejected',researcher_review:{status:'Disqualified by researcher'}}],'rejected'),
    E:unit([{id:'stale',recorded_review_pending:{recorded_status:'Validated by researcher'}}],'stale'),
  }};
db.sets=[{id:'global',units:Object.keys(db.units)},{id:'pilot',units:['B']}];
const key='GlobalPPR:group-settings:v2:/interactive_map/';
const plain=value=>JSON.parse(JSON.stringify(value));
function session({query='',saved='',preferences,source=db,storageBlocked=false}={}){
  const nodes={},storage=new Map(),address=new URL('https://example.test/interactive_map/trends.html'+query);
  if(preferences)storage.set(key,JSON.stringify(preferences));
  if(saved)storage.set(key+':trends',saved);
  function element(){return {value:'',children:[],replaceChildren(...items){this.children=items;},appendChild(item){this.children.push(item);}};}
  const context={URL,URLSearchParams,SERIES_DB:structuredClone(source),location:{href:address.href,search:address.search},
    document:{getElementById:id=>nodes[id]??=(element()),createElement:element,querySelectorAll:()=>[]},
    localStorage:{getItem(k){if(storageBlocked)throw Error('disabled');return storage.get(k)??null;},
      setItem(k,v){if(storageBlocked)throw Error('disabled');storage.set(k,v);}},
    history:{replaceState(_a,_b,url){context.location.href=new URL(url,context.location.href).href;}}};
  vm.createContext(context);
  vm.runInContext(section('/* Additional trend views','</script>'),context);
  vm.runInContext(section('const PPRResearcherReview=','</script>'),context);
  vm.runInContext(section('  const db=SERIES_DB','  function update() {'),context);
  const evaluate=code=>vm.runInContext(code,context);
  return {state:plain(evaluate('state')),nodes,storage,evaluate,source:context.SERIES_DB};
}
let s=session();
assert.equal(s.state.set,'validated','Fresh opens must choose the dynamic researcher-validated preset');
assert.deepEqual(s.state.units,['A','C'],'Eligibility follows the project-selected model, even without numerical results');
assert.deepEqual(s.state.methods,methods,'Keep all four requested methods in their requested order');
assert.deepEqual(Object.fromEntries(['mode','scope','catch_basis','uncertainty','baseline','npp_scope','npp_fill',
  'unidentified','group_display','global_estimate','review_filter','from','to'].map(k=>[k,s.state[k]])),
  {mode:'ratio',scope:'all',catch_basis:'landings',uncertainty:'1',baseline:null,npp_scope:'global',npp_fill:'earliest',
    unidentified:'method',group_display:'total',global_estimate:false,review_filter:'validated',from:1950,to:2019});
assert.deepEqual(s.state.models,{},'Default initialization must not freeze project model choices as user overrides');
assert.deepEqual(s.state.group_selections,{},'Researcher exclusions remain live defaults, not stored user selections');
assert.match(s.evaluate('PPRResearcherReview.selectionSummary(db.units,groupStore.data,state.units)'),/^3 groups excluded/);
assert.deepEqual(plain(s.evaluate('PPRGroups.selection(db.units.A.models[0],state.group_selections["A::selected"]).ids')),['fish','mammal']);
assert.equal(s.nodes.metric.value,'ratio');assert.equal(s.nodes.nppScope.value,'global');
assert.equal(s.nodes.regionReviewFilter.value,'validated');assert.equal(s.nodes.fromYear.value,'1950');
assert.equal(s.nodes.toYear.value,'2019');assert.equal(s.nodes.groupDisplay.value,'total');
assert.deepEqual(s.source,db,'Initialization must not mutate scientific data or researcher decisions');
const changed=structuredClone(db);changed.units.B.default_model='alternative';changed.years=[1949,2021];
assert.deepEqual(session({source:changed}).state.units,['A','B','C'],'New project selections change the default cohort');
assert.equal(session({source:changed}).state.from,1949);assert.equal(session({source:changed}).state.to,2021);
const single=structuredClone(db);single.units.C.models[0].researcher_review=null;
s=session({source:single});assert.deepEqual(s.state.units,['A']);
assert.equal(s.state.from,1950);assert.equal(s.state.to,2019,'One validated ecosystem still opens with the full available year range');
assert.equal(session({storageBlocked:true}).state.set,'validated','Storage restrictions do not prevent requested defaults');
// User group edits remain the shared saved default, including All and None.
for(const ids of [['fish','bird','mammal'],[],['bird']]){
  s=session();
  s.evaluate('groupStore.data.selections["A::selected"]='+JSON.stringify(ids)+';groupStore.save();');
  const persisted=JSON.parse(s.storage.get(key));
  assert.deepEqual(persisted.selections['A::selected'],ids);
  const reopened=session({preferences:persisted});
  assert.deepEqual(plain(reopened.evaluate('PPRGroups.selection(db.units.A.models[0],state.group_selections["A::selected"]).ids')),ids);
  assert.deepEqual(plain(reopened.evaluate('PPRGroupSettings.create({view:"map",units:db.units}).data.selections["A::selected"]')),ids,
    'Map and trends reuse the same saved group choices');
}
const overrides={version:2,models:{A:'pending',B:'alternative'},selections:{'B::alternative':['bird']},tables:{}};
s=session({preferences:overrides});assert.deepEqual(s.state.units,['B','C']);
assert.deepEqual(s.state.models,overrides.models);assert.deepEqual(s.state.group_selections,overrides.selections);
s=session({saved:'method=new_GE',preferences:overrides});
assert.deepEqual(s.state.methods,['new_GE']);assert.equal(s.state.mode,'ratio');assert.equal(s.state.npp_scope,'global');
assert.equal(s.state.npp_fill,'earliest');assert.equal(s.state.from,1950);assert.equal(s.state.to,2019);
const saved='units=B&method=new_GE&metric=ppr&scope=PP&catch_basis=discards&uncertainty=0&baseline=SPPR_1995_TE0.1&npp_scope=selected&npp_fill=observed&unidentified=zero&group_display=groups&global_estimate=1&from=2000&to=2019';
s=session({saved,preferences:overrides});
assert.equal(s.state.set,'custom');assert.deepEqual(s.state.units,['B']);assert.deepEqual(s.state.methods,['new_GE']);
assert.equal(s.state.mode,'ppr');assert.equal(s.state.scope,'PP');assert.equal(s.state.catch_basis,'discards');
assert.equal(s.state.uncertainty,'0');assert.equal(s.state.baseline,'SPPR_1995_TE0.1');
assert.equal(s.state.npp_scope,'selected');assert.equal(s.state.npp_fill,'observed');assert.equal(s.state.unidentified,'zero');
assert.equal(s.state.group_display,'groups');assert.equal(s.state.global_estimate,true);assert.equal(s.state.from,2000);
const linked='?group_settings='+encodeURIComponent(JSON.stringify(overrides));
s=session({saved,preferences:overrides,query:linked});
assert.equal(s.state.set,'validated','Navigation links intentionally start a new view instead of restoring saved presentation');
assert.deepEqual(s.state.methods,methods);assert.equal(s.state.mode,'ratio');
assert.deepEqual(s.state.models,overrides.models);assert.deepEqual(s.state.group_selections,overrides.selections);
s=session({saved,preferences:overrides,query:'?set=pilot&methods=new_TE_EEfix,new_GE&metric=npp&from=1950&to=2000&models='+encodeURIComponent(JSON.stringify({B:'pending'}))});
assert.equal(s.state.set,'pilot');assert.deepEqual(s.state.units,['B']);assert.equal(s.state.mode,'npp');
assert.deepEqual(s.state.methods,['new_TE_EEfix','new_GE']);assert.equal(s.state.from,1950);assert.equal(s.state.to,2000);
assert.equal(s.state.models.B,undefined,'Explicit URL model choices outrank stored alternatives');
assert.equal(s.state.baseline,null,'An explicit view URL must not inherit an omitted baseline from a different saved view');
s=session({query:'?units=&methods=&from=2000&to=2000'});
assert.deepEqual(s.state.units,[]);assert.deepEqual(s.state.methods,[]);assert.equal(s.state.from,2000);assert.equal(s.state.to,2000);
assert.deepEqual(session({query:'?method=new_GE&method=new_TE_EEfix'}).state.methods,['new_GE','new_TE_EEfix']);
console.log('Trend startup passed: dynamic validated defaults, four methods, requested controls, data-driven years/exclusions, saved choices and URL precedence.');
