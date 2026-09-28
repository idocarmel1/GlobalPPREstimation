const {test}=require('node:test');
const assert=require('node:assert/strict');
const series=require('../PPRAtlas/atlas/time_series_metrics.js');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const metadata={classifier_version:'explicit-nei-v1',rule_description:'Explicit residual labels only',taxa:[{name:'Marine fishes not identified',reason:'explicit not identified',reference_tl:2,simple_sppr:10}],catch:[20],missing_simple_catch:[0]};
function fixture(){
 const record={status:'ok',ppr:[1080],covered_catch:[100],unidentified_zero:{status:'ok',ppr:[180],covered_catch:[100]},unidentified_simple:{status:'ok',ppr:[380],covered_catch:[100]}};
 const unit={name:'Test',simple:{...structuredClone(record),catch:[100]},models:[{id:'model',verified:true,scopes:{all:{methods:{m:record}},PP:{methods:{m:record}}}}],default_model:'model',npp:{vgpm:[100]},unidentified:structuredClone(metadata)};
 return {years:[2019],npp_year:null,ppr_methods:[{id:'m',kind:'model',scopes:['all','PP']},{id:'taxon',kind:'taxon',scopes:['all']}],npp_methods:[{id:'vgpm'}],units:{a:unit}};
}
const state={units:['a'],method:'m',methods:['m'],scope:'all',mode:'ppr',npp:'vgpm'};
test('own method remains default; sensitivity changes PPR but retains all catch and affected share',()=>{
 const db=fixture(),before=structuredClone(db);
 assert.equal(series.aggregate(db,state).points[0].ppr,120);
 for(const [unidentified,ppr]of [['zero',20],['simple',380/9]]){
  const r=series.aggregate(db,{...state,unidentified}),p=r.points[0];
  assert.equal(p.ppr,ppr);assert.equal(p.catch,100);assert.equal(p.unidentified_catch,20);assert.equal(p.unidentified_share,.2);
 }
 assert.deepEqual(db,before);
});
test('simple reference has no invented source decomposition and absent scenarios fail closed',()=>{
 const db=fixture();
 assert.equal(series.aggregate(db,{...state,scope:'PP',unidentified:'simple'}).points[0].value,null);
 delete db.units.a.models[0].scopes.all.methods.m.unidentified_zero;
 assert.equal(series.aggregate(db,{...state,unidentified:'zero'}).points[0].value,null);
});
test('sensitivity is applied to every curve and baseline with CSV audit fields',()=>{
 const db=fixture(),s={...state,methods:['m','taxon'],baseline:'taxon',unidentified:'zero',mode:'ratio'};
 const r=series.compare(db,s);
 assert.deepEqual(r.series.map(v=>v.points[0].value),[1,1]);
 assert.equal(r.series[0].points[0].ppr,20);assert.equal(r.series[0].points[0].npp,100);
 const csv=series.comparisonToCSV(r,s);assert.match(csv,/unidentified_treatment/);assert.match(csv,/explicit-nei-v1/);assert.match(csv,/Marine fishes not identified/);
});
function mapFixture(){return {years:[2019],taxa:['Named species','Marine fishes not identified','Scombridae'],catch:[[70],[20],[10]],unidentified:structuredClone(metadata),models:[{verified:true,scopes:{all:{methods:['m','n'],status:{m:'ok',n:'ok'},values:[[2,4],[45,90],[4,8]]},PP:{methods:['m'],status:{m:'ok'},values:[[2],[45],[4]]}}}]};}
test('map modifies only explicitly listed residual taxa, including both ratio methods',()=>{
 const unit=mapFixture(),before=structuredClone(unit),s={year:2019,method:'m',denominator:'n',scope:'all',mode:'ppr'};
 assert.equal(map.evaluate(unit,0,s).value,120);
 let r=map.evaluate(unit,0,{...s,unidentified:'zero'});assert.equal(r.value,20);assert.equal(r.catch,100);assert.equal(r.unidentified_share,.2);
 r=map.evaluate(unit,0,{...s,unidentified:'simple'});assert.equal(r.value,380/9);
 r=map.evaluate(unit,0,{...s,mode:'ratio',unidentified:'simple'});assert.equal(r.value,380/560);
 assert.deepEqual(unit,before);
});
test('missing reference coefficients remain uncovered; zero treatment is an explicit true zero',()=>{
 const unit=mapFixture(),s={year:2019,method:'m',scope:'all',mode:'ppr',unidentified:'simple'};
 unit.unidentified.taxa[0].simple_sppr=null;unit.unidentified.missing_simple_catch=[20];
 const r=map.evaluate(unit,0,s);assert.equal(r.value,20);assert.equal(r.coverage,.8);assert.equal(r.unidentified_missing_simple_catch,20);
 assert.equal(map.evaluate(unit,0,{...s,scope:'PP'}).value,null);
 unit.catch=[[0],[20],[0]];
 assert.equal(map.evaluate(unit,0,s).value,null);
 assert.equal(map.evaluate(unit,0,{...s,unidentified:'zero'}).value,0);
});
test('map PPR/NPP responds to treatment and denominator without changing catch or carbon conversion',()=>{
 const unit=mapFixture(),s={year:2019,method:'m',scope:'all',mode:'npp_ratio',unidentified:'simple',npp_data:{years:[2019],values:[100]}};
 assert.ok(Math.abs(map.evaluate(unit,0,s).value-380/9)<1e-10);
 assert.ok(Math.abs(map.evaluate(unit,0,{...s,npp_data:{years:[2019],values:[200]}}).value-190/9)<1e-10);
 assert.equal(map.evaluate(unit,0,{...s,unidentified:'zero'}).value,20);
 assert.ok(Math.abs(map.evaluate(unit,0,{...s,method:'n'}).value-560/9)<1e-10);
 for(const value of [0,null,-1])assert.equal(map.evaluate(unit,0,{...s,npp_data:{years:[2019],values:[value]}}).value,null);
});
test('sensitivity cannot revive a failed scientific method',()=>{
 const db=fixture(),unit=mapFixture();db.units.a.models[0].scopes.all.methods.m.status='FAILED';unit.models[0].scopes.all.status.m='FAILED';
 for(const unidentified of ['zero','simple']){
  assert.equal(series.aggregate(db,{...state,unidentified}).points[0].value,null);
  assert.equal(map.evaluate(unit,0,{year:2019,method:'m',scope:'all',mode:'ppr',unidentified}).value,null);
 }
});
