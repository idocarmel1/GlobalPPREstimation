const {test}=require('node:test');
const assert=require('node:assert/strict');
const api=require('../PPRAtlas/atlas/time_series_metrics.js');
const band=value=>({status:'assessed',min_tC:value,max_tC:value*2,route_ppr_tC:{SC:value,SM:value*2}});
function fixture(){
  const unit=(ppr,npp)=>({name:'Region',simple:{ppr:[ppr*9,ppr*9],catch:[10,10],covered_catch:[10,10]},npp:{ens_median_tC_yr:npp,vgpm:npp.map(x=>x===null?null:x*2)},models:[{id:'model',verified:true,scopes:{all:{methods:{m:{status:'ok',ppr:[ppr*9,ppr*9],covered_catch:[10,10],sensitivity:[band(ppr),band(ppr)]},other:{status:'ok',ppr:[ppr*18,ppr*18],covered_catch:[10,10]}}}}}],default_model:'model',npp_metadata:{2000:{status:'complete',provenance:'test source'}}});
  return {years:[2000,2001],npp_year:null,npp_source:'annual.csv',sets:[],ppr_methods:[{id:'m',kind:'model',scopes:['all']},{id:'other',kind:'model',scopes:['all']}],npp_methods:[{id:'ens_median_tC_yr'},{id:'vgpm'}],units:{a:unit(100,[1000,1000]),b:unit(300,[3000,3000])},global_npp:{id:'atlas_union_v1',label:'Global atlas NPP',unit_ids:['a','b','unselected'],values:[10000,20000],ensemble_convention:'median of complete model totals on fixed atlas union',geography:'Atlas union, not world ocean',overlap_policy:'union raster cells counted once',source:'union.csv',metadata:{2000:{status:'complete',model_count:3,model_names:['A','B','C']},2001:{status:'complete',model_count:3,model_names:['A','B','C']}}}};
}
const state={units:['a','b'],methods:['m'],method:'m',mode:'ratio',scope:'all',npp:'ens_median_tC_yr',catch_basis:'landings',uncertainty:'1'};
test('NPP-only ignores unavailable PPR methods, models and catch and produces one NPP curve',()=>{
  const db=fixture();delete db.units.a.simple;db.units.a.models=[];db.units.b.simple.ppr=[null,null];
  const r=api.compare(db,{...state,mode:'npp',methods:['unknown','other'],baseline:'unknown',scope:'invalid'});
  assert.equal(r.series.length,1);assert.equal(r.normalized,false);
  assert.deepEqual(r.included,['a','b']);assert.equal(r.points[0].value,4000);
  assert.equal(r.points[0].ppr,null);assert.equal(r.points[0].npp,4000);
});
test('selected versus fixed global reference matches carbon arithmetic and subset invariance',()=>{
  const db=fixture();
  for(const [units,local,global] of [[['a','b'],10,4],[['a'],10,1]]){
    assert.equal(api.aggregate(db,{...state,units}).points[0].value,local);
    const r=api.aggregate(db,{...state,units,npp_scope:'global'});
    assert.equal(r.points[0].value,global);assert.equal(r.points[0].npp_denominator,10000);
  }
  assert.equal(api.aggregate(db,{...state,method:'other',npp_scope:'global'}).points[0].npp,10000);
  db.units.b.models=[];db.units.a.npp={};
  const r=api.aggregate(db,{...state,npp_scope:'global'});
  assert.deepEqual(r.included,['a']);assert.equal(r.points[0].value,1);
  assert.equal(r.points[0].npp,10000);
});
test('global uses fixed reference ensemble regardless of regional NPP selector',()=>{
  const db=fixture();const r=api.aggregate(db,{...state,npp_scope:'global',npp:'vgpm'});
  assert.equal(r.points[0].value,4);assert.equal(r.points[0].npp,10000);
  assert.equal(r.points[0].npp_ensemble_convention,db.global_npp.ensemble_convention);
  assert.deepEqual(r.points[0].npp_reference_ids,db.global_npp.unit_ids);
});
test('routing endpoints use exactly the chosen selected or global NPP denominator',()=>{
  const db=fixture();
  const selected=api.aggregate(db,state).points[0];
  const global=api.aggregate(db,{...state,npp_scope:'global'}).points[0];
  assert.equal(selected.sensitivity.lower,10);assert.equal(selected.sensitivity.upper,20);
  assert.equal(global.sensitivity.lower,4);assert.equal(global.sensitivity.upper,8);
});
test('fixed NPP-only cohort exposes missing regions without shrinking annual sums; real zero survives',()=>{
  const db=fixture();db.units.b.npp.ens_median_tC_yr=[null,3000];
  let r=api.compare(db,{...state,mode:'npp'});
  assert.deepEqual(r.points.map(p=>p.value),[null,4000]);
  assert.deepEqual(r.points[0].npp_missing_ids,['b']);assert.deepEqual(r.points[0].npp_available_ids,['a']);
  r=api.compare(db,{...state,mode:'npp',npp_fill:'earliest'});
  assert.equal(r.points[0].value,4000);assert.equal(r.points[0].npp_estimated,true);
  assert.equal(r.points[0].npp_source_years.b,2001);
  db.units.a.npp.ens_median_tC_yr=[0,1000];
  r=api.compare(db,{...state,mode:'npp',units:['a'],npp_fill:'earliest'});
  assert.equal(r.points[0].value,0);assert.equal(r.points[0].npp_estimated,false);
});
test('global missing years stay gaps; explicit earliest proxy preserves reference source support',()=>{
  const db=fixture();db.global_npp.values=[null,20000];db.global_npp.metadata[2000]={status:'incomplete',reason:'Missing reference support'};
  let r=api.aggregate(db,{...state,npp_scope:'global'});
  assert.equal(r.points[0].value,null);assert.equal(r.points[0].ppr,400);assert.equal(r.points[0].sensitivity.max_tC,800);
  r=api.aggregate(db,{...state,npp_scope:'global',npp_fill:'earliest'});
  assert.equal(r.points[0].value,2);assert.equal(r.points[0].npp_estimated,true);
  assert.equal(r.points[0].npp_source_years.atlas_union_v1,2001);
  assert.equal(r.points[0].npp_reference_metadata.model_count,3);
  db.global_npp.values=[10000,null];
  assert.equal(api.aggregate(db,{...state,npp_scope:'global',npp_fill:'earliest'}).points[1].value,null);
});
test('selected ratios retain a gap when a required region has zero NPP in that year',()=>{
  const db=fixture();db.units.a.npp.ens_median_tC_yr=[0,1000];
  assert.equal(api.aggregate(db,state).points[0].value,null);
  assert.equal(api.compare(db,{...state,mode:'npp'}).points[0].value,3000);
});
test('a calculated but coverage-limited global reference stays explicitly labeled in values and exports',()=>{
  const db=fixture();db.global_npp.metadata[2000]={status:'coverage_limited',complete:true,coverage_complete:false,coverage_limited:true,reason:'Source water mask excludes never-retrieved pixels.',water_area_pct_of_polygon:82};
  const s={...state,npp_scope:'global'},r=api.compare(db,s),p=r.points[0];
  assert.equal(p.value,4);assert.equal(p.npp_status,'coverage_limited');
  assert.match(p.npp_reason,/never-retrieved/);
  assert.match(api.comparisonToCSV(r,s),/coverage_limited/);
});
test('comparison normalization remains dimensionless and cannot normalize an NPP mass',()=>{
  const db=fixture();
  const r=api.compare(db,{...state,methods:['m','other'],baseline:'m',npp_scope:'global'});
  assert.deepEqual(r.series.map(s=>s.points[0].value),[1,2]);
  assert.equal(r.series[0].points[0].npp,10000);
  assert.equal(api.compare(db,{...state,mode:'npp',baseline:'m'}).points[0].value,4000);
});
test('CSV and JSON preserve numeric denominator, reference geography, ensemble and substitutions',()=>{
  const db=fixture(),s={...state,npp_scope:'global'},r=api.compare(db,s);
  const csv=api.comparisonToCSV(r,s);
  assert.match(csv,/npp_denominator_scope/);assert.match(csv,/npp_denominator_tonnes_carbon/);
  assert.match(csv,/atlas_union_v1/);assert.match(csv,/median of complete model totals/);
  const download=JSON.parse(api.comparisonToJSON(r,s));
  assert.equal(download.result.points[0].npp_denominator,10000);
  assert.deepEqual(download.result.npp_reference.unit_ids,db.global_npp.unit_ids);
  const nppState={...state,mode:'npp',methods:['m','other'],baseline:'m'};
  const nppCSV=api.comparisonToCSV(api.compare(db,nppState),nppState);
  assert.equal(nppCSV.trim().split('\n').length,3);
  assert.match(nppCSV,/"4000"/);
});
