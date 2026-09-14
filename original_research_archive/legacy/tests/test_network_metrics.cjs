const {test} = require('node:test');
const assert = require('node:assert/strict');
const m = require('../PPRAtlas/atlas/network_metrics.js');
const unit={years:[2019],catch:[[10],[90],[0]],models:[{id:'one',verified:true,
  scopes:{all:{methods:['a','b'],values:[[2,4],[100,null],[1,0]],status:{a:'ok',b:'ok'}}},
  health:{GE:{b:1.2,rho_living:.2,status:'FAIL'}}}]};
test('ratio uses common catch and reports coverage',()=>{
 const r=m.evaluate(unit,0,{year:2019,scope:'all',mode:'ratio',method:'a',denominator:'b'});
 assert.equal(r.value,.5);assert.equal(r.coverage,.1);assert.equal(r.catch,10);
 assert.equal(r.numerator,20/9);assert.equal(r.denominator,40/9);
});
test('map PPR is carbon while catch and source coefficients retain their original units',()=>{
 const original=structuredClone(unit);
 const r=m.evaluate(unit,0,{year:2019,scope:'all',mode:'ppr',method:'a'});
 assert.equal(r.value,9020/9);assert.equal(r.numerator,9020/9);
 assert.equal(r.catch,100);assert.deepEqual(unit,original);
});
test('missing scope, denominator and failed method remain missing',()=>{
 for(const state of [{scope:'PP'},{denominator:'missing'}])
  assert.equal(m.evaluate(unit,0,{year:2019,scope:'all',mode:'ratio',method:'a',denominator:'b',...state}).value,null);
 const bad=structuredClone(unit);bad.models[0].scopes.all.status.a='DIVERGED';
 assert.equal(m.evaluate(bad,0,{year:2019,scope:'all',mode:'ppr',method:'a'}).value,null);
 const zero=structuredClone(unit);zero.models[0].scopes.all.values[0][1]=0;
 assert.equal(m.evaluate(zero,0,{year:2019,scope:'all',mode:'ratio',method:'a',denominator:'b'}).value,null);
});
test('diagnostics retain failure and zero while unselected ecosystems stay empty',()=>{
 assert.equal(m.evaluate(null,0,{mode:'b',te:'GE'}).value,null);
 const r=m.evaluate(unit,0,{mode:'b',te:'GE'});assert.equal(r.value,1.2);assert.equal(r.status,'FAIL');
 const zero=structuredClone(unit);zero.models[0].health.GE.b=0;
 assert.equal(m.evaluate(zero,0,{mode:'b',te:'GE'}).value,0);
});
