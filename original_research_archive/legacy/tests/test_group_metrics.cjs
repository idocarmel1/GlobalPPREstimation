const {test}=require('node:test');
const assert=require('node:assert/strict');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const trends=require('../PPRAtlas/atlas/time_series_metrics.js');
const groups=require('../PPRAtlas/atlas/group_metrics.js');
const simple='simple trophic chain';
function fixture(){
 const methods=['network','MC_GE',simple], values=[[80,160,20],[200,400,40],[null,null,null]];
 const scope={methods,status:Object.fromEntries(methods.map(m=>[m,'ok'])),values};
 const model={id:'model',verified:true,scopes:{all:scope,inner:structuredClone(scope)},mc_diagnostics:{MC_GE:{n_samples:100,n_accepted:90}},
 group_data:{groups:[{id:'A',name:'A',te:.1,tl:2},{id:'B',name:'B',te:.2,tl:3}],methods,
 scopes:{all:[[20,40,2],[100,200,4]],inner:[[10,20,1],[50,100,2]]},mappings:[[[0,.25],[1,.75]],[[1,1]],[]]}};
 const unit={years:[2000,2001],taxa:['mixed','B taxon','unknown'],catch:[[20,40],[10,20],[5,10]],full_precision_catch:[[20,40],[10,20],[5,10]],landings:[[16,32],[8,16],[4,8]],discards:[[4,8],[2,4],[1,2]],simple_sppr:[20,40,null],models:[model],catch_basis_policy:{},unidentified:{taxa:[{name:'mixed',simple_sppr:12}]}};
 const record={status:'ok',ppr:[2880,5760],covered_catch:[24,48],catch_bases:{catch:{ppr:[3600,7200],covered_catch:[30,60]},discards:{ppr:[720,1440],covered_catch:[6,12]}}};
 const annual={...structuredClone(unit),name:'region',default_model:'model',group_inputs:structuredClone(unit),npp:{npp:[100,200]},simple:{status:'ok',ppr:[640,1280],covered_catch:[24,48],catch:[28,56],catch_bases:{catch:{ppr:[800,1600],covered_catch:[30,60],catch:[35,70]},discards:{ppr:[160,320],covered_catch:[6,12],catch:[7,14]}}}};
 annual.models=[{...structuredClone(model),taxon_scopes:structuredClone(model.scopes),scopes:{all:{methods:{network:record,MC_GE:structuredClone(record)}},inner:{methods:{network:structuredClone(record)}}}}];
 const db={years:unit.years,ppr_methods:methods.map(id=>({id,kind:id===simple?'taxon':'model',scopes:['all','inner']})),npp_methods:[{id:'npp'}],units:{u:annual}};
 return {unit,model,db};
}
const state={unit_id:'u',units:['u'],year:2000,method:'network',scope:'all',mode:'ppr',catch_basis:'catch',npp:'npp'};
const selected=ids=>({...state,group_selections:{'u::model':ids}});
test('group selections use names and all-selected identity is exact',()=>{
 const {unit,model,db}=fixture();
 assert.equal(groups.key('u',model),'u::model');assert.equal(groups.active(model,['B','A']),false);
 assert.deepEqual(map.evaluate(unit,0,selected(['A','B'])),map.evaluate(unit,0,state));
 assert.deepEqual(trends.aggregate(db,selected(['A','B'])),trends.aggregate(db,state));
});
test('mixed mappings retain weights without renormalizing and map matches trends for each catch basis',()=>{
 const {unit,db}=fixture();
 for(const [basis,c] of [['catch',20],['landings',16],['discards',4]]){
  const s={...selected(['A']),catch_basis:basis},m=map.evaluate(unit,0,s),t=trends.aggregate(db,s).points[0];
  assert.equal(m.value,c*.25*20/9);assert.equal(m.catch,c*.25);assert.equal(m.total_catch,c*.25);assert.equal(m.coverage,1);
  assert.equal(t.value,m.value);assert.equal(t.catch,m.total_catch);assert.equal(t.covered_catch,m.catch);
  if(basis==='landings')assert.match(m.sensitivity.reason,/group subset/i);
 }
});
test('empty selection yields explicit zero without fallback and leaves NPP unchanged',()=>{
 const {unit,db}=fixture(),s=selected([]);
 const m=map.evaluate(unit,0,s),t=trends.aggregate(db,s);
 assert.equal(m.value,0);assert.equal(m.catch,0);assert.match(m.status,/No groups selected/);assert.equal(t.points[0].value,0);
 const mapRatio=map.evaluate(unit,0,{...selected(['A']),mode:'npp_ratio',npp_data:{years:[2000],values:[100]}});
 const trendRatio=trends.aggregate(db,{...selected(['A']),mode:'ratio'}).points[0];
 assert.equal(mapRatio.denominator,100);assert.equal(trendRatio.npp,100);assert.equal(mapRatio.value,trendRatio.value);
});
test('MC and workbook rejection precede partial and empty selection',()=>{
 for(const ids of [['A'],[]]){
  const {unit,model,db}=fixture();model.mc_diagnostics.MC_GE.n_accepted=79;db.units.u.models[0].mc_diagnostics.MC_GE.n_accepted=79;
  const s={...selected(ids),method:'MC_GE'};
  assert.equal(map.evaluate(unit,0,s).value,null);assert.match(map.evaluate(unit,0,s).status,/80%/);assert.equal(trends.aggregate(db,s).points[0].value,null);
  model.verified=false;assert.equal(map.evaluate(unit,0,selected(ids)).value,null);
 }
 const {unit,model}=fixture();model.mc_diagnostics.MC_GE.n_accepted=79;
 assert.equal(map.evaluate(unit,0,{...state,method:'MC_GE'}).value,null);
 assert.equal(map.evaluate(unit,0,{...selected(['A','B']),method:'MC_GE'}).value,null);
});
test('simple-chain and residual reference coefficients use retained allocation fractions',()=>{
 const {unit,db}=fixture();
 const s={...selected(['A']),method:simple,simple_unit:db.units.u};
 assert.equal(map.evaluate(unit,0,s).value,20*.25*20/9);assert.equal(trends.aggregate(db,s).points[0].value,20*.25*20/9);
 for(const [treatment,expected] of [['zero',0],['simple',20*.25*12/9]]){
  const r=map.evaluate(unit,0,{...selected(['A']),unidentified:treatment});assert.equal(r.value,expected);
 }
});
test('missing method, taxon coefficient and catch data cannot be rescued by selection',()=>{
 const {unit,model}=fixture();
 model.scopes.all.status.network='unavailable';assert.equal(map.evaluate(unit,0,selected([])).value,null);
 model.scopes.all.status.network='ok';model.scopes.all.values[0][0]=null;
 assert.equal(map.evaluate(unit,0,selected(['A'])).value,null);
 unit.full_precision_catch[0][0]=null;assert.equal(map.evaluate(unit,0,selected([])).value,null);
});
test('table reports original group scope coefficients and carbon catch contribution',()=>{
 const {unit,model}=fixture(),rows=groups.rows(unit,model,state);
 assert.equal(rows[0].sppr_all,20);assert.equal(rows[0].sppr_inner,10);assert.equal(rows[0].ppr,100/9);
});
test('method ratios use selected common catch and CSV selection provenance is conditional',()=>{
 const {unit,db}=fixture();
 assert.equal(map.evaluate(unit,0,{...selected(['A']),mode:'ratio',denominator:'MC_GE'}).value,.5);
 assert.match(trends.toCSV(trends.aggregate(db,selected(['A'])),selected(['A'])),/group_selections/);
 assert.doesNotMatch(trends.toCSV(trends.aggregate(db,state),state),/group_selections/);
});
test('annual source-year alignment, gaps and empty-selection NPP status remain explicit',()=>{
 const {unit,db}=fixture();
 const s={...selected([]),mode:'npp_ratio',npp_data:{years:[2000],values:[100]}};
 assert.match(map.evaluate(unit,0,s).status,/No groups selected/);
 const source=db.units.u.group_inputs;
 source.years.reverse();for(const key of ['catch','full_precision_catch','landings','discards'])source[key].forEach(row=>row.reverse());
 assert.equal(trends.aggregate(db,selected(['A'])).points[0].value,map.evaluate(unit,0,selected(['A'])).value);
 db.units.u.models[0].scopes.all.methods.network.catch_bases.catch.ppr[0]=null;
 assert.equal(trends.aggregate(db,selected([])).points[0].value,null);
 const gap=trends.aggregate(db,{...selected([]),allow_gaps:true});
 assert.deepEqual(gap.points.map(p=>p.value),[null,0]);
});
test('subset residual scenarios agree across map and annual view and reject source decomposition',()=>{
 const {unit,db}=fixture(),r=db.units.u.models[0].scopes.all.methods.network;
 for(const treatment of ['zero','simple']){
  r['unidentified_'+treatment]=structuredClone(r);
  const s={...selected(['A']),unidentified:treatment};
  assert.equal(trends.aggregate(db,s).points[0].value,map.evaluate(unit,0,s).value);
 }
 assert.equal(map.evaluate(unit,0,{...selected(['A']),unidentified:'simple',scope:'inner'}).value,null);
});
