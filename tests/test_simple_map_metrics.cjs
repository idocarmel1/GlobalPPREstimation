const {test}=require('node:test');
const assert=require('node:assert/strict');
const api=require('../PPRAtlas/atlas/network_metrics.js');
const state={year:2019,method:'simple trophic chain',scope:'all',mode:'ppr',catch_basis:'landings',uncertainty:true};
const values=(ppr,catchValue=10,covered=catchValue)=>({status:'ok',ppr:[ppr],catch:[catchValue],covered_catch:[covered]});
function fixture(){return {years:[2019],simple:{...values(900),catch_bases:{catch:values(1800,20),discards:values(900)},unidentified_zero:{...values(450),catch_bases:{catch:values(900,20),discards:values(450)}},unidentified_simple:values(900)},unidentified:{catch:[5],missing_simple_catch:[0],catch_bases:{catch:{catch:[10],missing_simple_catch:[0]}}},sources:{catch_csv:'raw.csv'}};}
test('independent simple PPR needs no article and ignores model coefficients and verification',()=>{
  const simple_unit=fixture();
  for(const unit of [null,{models:[]},{models:[{verified:false}]},{models:[{verified:true,scopes:{all:{values:[[999999]]}}}]}]){
    const r=api.evaluate(unit,0,{...state,simple_unit});
    assert.equal(r.value,100);assert.equal(r.numerator,100);assert.equal(r.catch,10);assert.equal(r.coverage,1);
    assert.equal(r.independent_simple,true);assert.deepEqual(r.sources,simple_unit.sources);
    assert.equal(r.sensitivity.status,'not_assessed');
  }
});
test('independent simple selects exact catch basis and unidentified treatment',()=>{
  const simple_unit=fixture(),run=s=>api.evaluate(null,0,{...state,simple_unit,...s});
  assert.equal(run({catch_basis:'catch'}).value,200);
  assert.equal(run({catch_basis:'discards'}).value,100);
  const r=run({catch_basis:'catch',unidentified:'zero'});
  assert.equal(r.value,100);assert.equal(r.total_catch,20);assert.equal(r.unidentified_catch,10);
  assert.equal(r.total_catch_all,20);assert.equal(r.total_discards,10);
  assert.equal(run({unidentified:'simple'}).value,100);
  delete simple_unit.simple.catch_bases.discards;
  assert.equal(run({catch_basis:'discards'}).value,null);
});
test('independent simple preserves real zeros, partial TL coverage, missing catch and years',()=>{
  const simple_unit=fixture(),run=()=>api.evaluate(null,0,{...state,simple_unit});
  simple_unit.simple={...values(0,0)};assert.equal(run().value,0);
  simple_unit.simple=values(900,20,10);assert.equal(run().coverage,.5);
  simple_unit.simple=values(null,20,0);assert.equal(run().value,null);
  simple_unit.simple=null;assert.equal(run().value,null);
  assert.equal(api.evaluate(null,0,{...state,year:1900,simple_unit:fixture()}).value,null);
});
test('independent simple NPP ratio uses annual positive carbon denominator once',()=>{
  const simple_unit=fixture(),run=npp_data=>api.evaluate(null,0,{...state,mode:'npp_ratio',simple_unit,npp_data});
  const r=run({years:[2019],values:[1000]});
  assert.equal(r.value,10);assert.equal(r.numerator,100);assert.equal(r.denominator,1000);
  for(const value of [0,-1,null])assert.equal(run({years:[2019],values:[value]}).value,null);
});
test('simple bypass applies only to all-source PPR and NPP ratios',()=>{
  for(const change of [{scope:'living'},{mode:'ratio'},{mode:'b'},{method:'model method'}]){
    assert.equal(api.evaluate(null,0,{...state,simple_unit:fixture(),...change}).value,null);
  }
});
