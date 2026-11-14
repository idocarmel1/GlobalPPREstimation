const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const page=JSON.parse(fs.readFileSync(0,'utf8'));
function section(start,end){
  const a=page.indexOf(start),b=page.indexOf(end,a);
  assert.ok(a>=0&&b>a,`Missing trend section: ${start}`);
  return page.slice(a,b);
}
const reviewed=id=>({id,verified:false,researcher_review:{status:'Validated by researcher'},scopes:{all:{methods:{GE:{status:'FAIL',ppr:[null]}}}}});
const pending={id:'pending',verified:true},rejected={id:'rejected',verified:true,researcher_review:{status:'Disqualified by researcher'}};
const unit=(name,models,default_model)=>({name,type:'LME',models,default_model,simple:{status:'ok',ppr:[90],catch:[9],covered_catch:[9]},npp:{npp:[100]}});
const db={years:[2019],ppr_methods:[{id:'simple trophic chain',kind:'taxon',scopes:['all']}],npp_methods:[{id:'npp'}],units:{
  LME_022:unit('North Sea',[reviewed('ices'),pending],'ices'),
  LME_038:unit('Indonesian Sea',[reviewed('java')],'java'),
  alternative:unit('Alternative',[pending,reviewed('approved')],'pending'),
  rejected:unit('Rejected',[rejected],'rejected'),
  pending:unit('Pending',[{...pending,recorded_review_pending:{recorded_status:'Validated by researcher'}}],'pending'),
  numeric:unit('Numeric default',[reviewed('numeric-approved')],0),
}};
db.sets=[{id:'global',label:'All ecosystems',units:Object.keys(db.units)},{id:'pilot',label:'Pilot',units:['LME_022']}];
const snapshot=JSON.stringify(db);
function session(query){
  const nodes={};
  function element(tag){return {tag,value:'',children:[],listeners:{},scrollTop:0,open:false,
    set id(value){this._id=value;nodes[value]=this;},get id(){return this._id;},
    append(...children){this.children.push(...children);},appendChild(child){this.children.push(child);return child;},
    replaceChildren(...children){this.children=children;},setAttribute(key,value){this[key]=value;},
    addEventListener(event,fn){this.listeners[event]=fn;},focus(){},showModal(){this.open=true;},close(){this.open=false;}};}
  const node=id=>nodes[id]||=(element('div'));
  const address=new URL(query,'https://example.test/trends.html'),storage=new Map();
  const context={console,URL,URLSearchParams,SERIES_DB:structuredClone(db),location:{search:address.search,href:address.href},
    localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    document:{getElementById:node,createElement:element,querySelectorAll:()=>[]},history:{replaceState(_state,_title,url){context.savedURL=url;}}};
  vm.createContext(context);
  vm.runInContext(section('/* Additional trend views','</script>'),context);
  vm.runInContext(section('  const db=SERIES_DB','  function update() {'),context);
  // Exercise production selection/calculation and URL logic; chart drawing is unrelated.
  vm.runInContext(section('  function update() {','    focus=result.points.findIndex')+'    saveURL();\n  }',context);
  vm.runInContext(section('  const ordered=Object.entries(db.units)','  function download(format)'),context);
  const evaluate=code=>vm.runInContext(code,context);
  const state=()=>JSON.parse(evaluate('JSON.stringify(state)'));
  const selected=()=>JSON.parse(evaluate('JSON.stringify(PPRTrendExtras.selectedUnits(db,state))')).sort();
  const changeSet=value=>{node('ecosystemSet').value=value;node('ecosystemSet').listeners.change();};
  const changeModel=(id,value)=>{
    const row=node('ecosystemList').children.find(row=>row.children[0]?.children[0]?.value===id);
    const select=row?.children.find(child=>child.tag==='select');assert.ok(select,`Model choice remains available for ${id}`);
    select.value=value;select.listeners.change();
  };
  evaluate('update();renderPicker();');
  return {context,node,evaluate,state,selected,changeSet,changeModel};
}
const s=session('?units=&method=simple+trophic+chain&npp=npp');
assert.ok(s.node('ecosystemSet').children.some(option=>option.value==='validated'&&option.textContent==='Validated by researcher'),
  'The ecosystem-set menu offers the researcher-validated cohort');
s.changeSet('validated');
assert.deepEqual(s.state().units.sort(),['LME_022','LME_038','numeric'],
  'The preset recovers every reviewed selected model from an empty custom selection, regardless of numerical verification');
assert.equal(s.state().set,'validated');assert.equal(s.node('regionReviewFilter').value,'validated');
assert.deepEqual(s.state().models,{},'Review eligibility never switches a selected model');
assert.match(s.node('pickerNote').textContent,/currently selected model/i);
s.changeModel('LME_022','pending');
assert.deepEqual(s.selected(),['LME_038','numeric'],'Switching away from a reviewed model removes its ecosystem');
assert.deepEqual(s.state().units.sort(),['LME_038','numeric']);
const restored=session(s.context.savedURL);
assert.equal(restored.state().set,'validated');
assert.deepEqual(restored.selected(),['LME_038','numeric'],'The preset URL retains model overrides for excluded ecosystems');
s.changeModel('LME_022','ices');
s.changeModel('alternative','approved');
assert.deepEqual(s.selected(),['LME_022','LME_038','alternative','numeric'],'Changing the selected candidate changes full-preset eligibility');
const box=s.node('pick_LME_038');box.checked=false;box.listeners.change();
assert.equal(s.state().set,'custom');assert.equal(s.state().review_filter,'validated');
assert.deepEqual(s.selected(),['LME_022','alternative','numeric']);
s.changeModel('LME_022','pending');
assert.deepEqual(s.selected(),['alternative','numeric'],'A custom subset retains selected-model review eligibility');
const custom=session(s.context.savedURL);
assert.equal(custom.state().set,'custom');
assert.deepEqual(custom.selected(),['alternative','numeric'],'A custom reviewed subset and its chosen models survive URL restoration');
s.changeSet('pilot');
assert.deepEqual(s.state().units,['LME_022']);assert.deepEqual(s.selected(),[],
  'Ordinary geography presets still intersect the independently visible review filter');
s.node('regionReviewFilter').value='all';s.node('regionReviewFilter').listeners.change();
assert.deepEqual(s.selected(),['LME_022'],'The separate review filter can explicitly restore an ordinary selected geography');
s.node('clearSelection').listeners.click();assert.deepEqual(s.selected(),[]);
s.changeSet('validated');assert.deepEqual(s.selected(),['LME_038','alternative','numeric']);
assert.deepEqual(session('?set=validated&npp=npp').selected(),['LME_022','LME_038','numeric'],
  'A direct validated-preset URL initializes the full currently approved cohort');
assert.equal(JSON.stringify(s.context.SERIES_DB),snapshot,'Selection does not alter source data or review records');
console.log('Validated ecosystem preset passed: empty/custom selection, selected-model identity, review-only models, model changes, subset edits, ordinary sets and URL restoration.');
