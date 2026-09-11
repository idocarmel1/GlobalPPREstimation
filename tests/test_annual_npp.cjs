const {test}=require('node:test');
const assert=require('node:assert/strict');
const api=require('../PPRAtlas/atlas/time_series_metrics.js');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const annual=require('../PPRAtlas/atlas/annual_npp.js');
const years=[1950,2000,2001,2002,2003];
const state={units:['a','b'],method:'taxon',methods:['taxon'],scope:'all',mode:'ratio',npp:'vgpm'};
function fixture(){
 const unit=(npp,factor)=>({name:'Region',simple:{ppr:years.map(()=>90*factor),catch:years.map(()=>10),covered_catch:years.map(()=>10)},npp:{vgpm:npp},npp_metadata:{2000:{status:'ok',provenance:'annual source'}},models:[]});
 return {years,npp_year:null,npp_source:'NPPExtraction/output/annual_npp.csv',npp_methods:[{id:'vgpm'}],ppr_methods:[{id:'taxon',kind:'taxon',scopes:['all']}],units:{a:unit([null,100,null,200,null],1),b:unit([null,null,300,400,null],2)}};
}
test('annual NPP preserves a fixed cohort and leaves unsupported years blank',()=>{
 const db=fixture(),before=structuredClone(db),r=api.aggregate(db,state);
 assert.deepEqual(r.included,['a','b']);assert.equal(r.annual_npp,true);
 assert.deepEqual(r.points.map(p=>p.value),[null,null,null,5,null]);
 assert.equal(r.points[3].ppr,30);assert.equal(r.points[3].npp,600);
 assert.deepEqual(db,before);
});
test('optional earliest-year substitution fills only missing years before each method starts',()=>{
 const r=api.aggregate(fixture(),{...state,npp_fill:'earliest'});
 assert.deepEqual(r.points.map(p=>p.value),[7.5,7.5,null,5,null]);
 assert.equal(r.points[0].npp_estimated,true);
 assert.deepEqual(r.points[0].npp_substituted_ids,['a','b']);
 assert.deepEqual(r.points[0].npp_source_years,{a:2000,b:2001});
 assert.equal(r.points[1].npp_estimated,true);assert.deepEqual(r.points[1].npp_substituted_ids,['b']);
 assert.equal(r.points[3].npp_estimated,false);
 assert.equal(api.aggregate(fixture(),{...state,npp_fill:'earliest',years:[1950]}).points[0].value,7.5);
});
test('CSV preserves annual source, substitution policy and exact source years',()=>{
 const s={...state,npp_fill:'earliest'},r=api.aggregate(fixture(),s),csv=api.toCSV(r,s);
 assert.match(csv,/npp_fill_policy,npp_estimated,npp_substituted_ids,npp_source_years,npp_source,npp_provenance/);
 assert.match(csv,/earliest/);assert.match(csv,/annual_npp.csv/);assert.match(csv,/annual source/);
 assert.match(csv,/2000/);assert.match(csv,/2001/);
});
test('map ratio uses selected annual NPP and keeps missing years unavailable',()=>{
 const unit={years,catch:years.map(()=>[1]),models:[]};
 unit.catch=[years.map(()=>90)];unit.models=[{verified:true,scopes:{all:{methods:['m'],status:{m:'ok'},values:[[1]]}}}];
 const npp={years,values:[null,100,null,200,null]};
 const s={year:1950,scope:'all',method:'m',mode:'npp_ratio',npp_data:npp};
 assert.equal(map.evaluate(unit,0,s).value,null);
 const early=map.evaluate(unit,0,{...s,npp_fill:'earliest'});
 assert.equal(early.value,10);assert.equal(early.numerator,10);assert.equal(early.npp.source_year,2000);assert.equal(early.npp.substituted,true);
 assert.equal(map.evaluate(unit,0,{...s,year:2002}).value,5);
 assert.equal(map.evaluate(unit,0,{...s,year:2001,npp_fill:'earliest'}).value,null);
 assert.equal(map.evaluate(null,0,{...s,npp_fill:'earliest'}).value,null);
});
test('earliest-year policy never replaces a recorded zero, a later gap or an unknown year',()=>{
 for(const [year,values] of [[1950,[0,100,null,200,null]],[2001,[null,100,null,200,null]],[2003,[null,100,null,200,null]],[1949,[null,100,null,200,null]]]){
  assert.equal(annual.resolve(years,values,year,'earliest').value,null);
 }
 assert.equal(annual.resolve(years,[null,100,null,200,null],1950,'unknown').value,null);
 assert.equal(annual.resolve(years,[null,null,null,null,null],1950,'earliest').value,null);
});
test('annual method comparisons preserve common ecosystems and substitution provenance',()=>{
 const db=fixture();db.ppr_methods.push({id:'other',kind:'model',scopes:['all']});
 for(const u of Object.values(db.units)){
  u.default_model='m';u.models=[{id:'m',verified:true,scopes:{all:{methods:{other:{status:'ok',ppr:u.simple.ppr.map(v=>2*v),covered_catch:u.simple.covered_catch}}}}}];
 }
 const s={...state,methods:['taxon','other'],baseline:'taxon',npp_fill:'earliest'},r=api.compare(db,s);
 assert.deepEqual(r.included,['a','b']);
 assert.deepEqual(r.series[1].points.map(p=>p.value),[2,2,null,2,null]);
 assert.deepEqual(r.series[1].points[0].npp_source_years,{a:2000,b:2001});
 assert.equal(r.series[1].points[0].ppr,60);assert.equal(r.series[1].points[0].npp,400);
 const csv=api.comparisonToCSV(r,s);assert.match(csv,/npp_fill_policy/);assert.match(csv,/annual_npp.csv/);
});
test('ensemble support follows the substituted source year and remains in exported provenance',()=>{
 const db=fixture();
 db.units.a.npp_metadata={1950:{n_models:'0'},2000:{n_models:'1',available_models:'VGPM',ensemble_basis:'available-model median'},2002:{n_models:'2',available_models:'VGPM;CAFE'}};
 const s={...state,npp_fill:'earliest'},result=api.aggregate(db,s);
 assert.equal(result.points[0].npp_provenance.a.n_models,'1');
 assert.equal(result.points[3].npp_provenance.a.n_models,'2');
 assert.match(api.toCSV(result,s),/available-model median/);
 assert.match(api.toCSV(result,s),/VGPM;CAFE/);
});
