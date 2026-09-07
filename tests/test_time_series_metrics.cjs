const {test} = require('node:test');
const assert = require('node:assert/strict');
const {aggregate, toCSV} = require('../PPRAtlas/atlas/time_series_metrics.js');

function fixture() {
  const unit=(ppr,npp)=>({name:'Region',simple:{ppr,catch:[10,20],covered_catch:[8,15]},npp:{vgpm:npp},models:[],default_model:null});
  return {years:[2000,2001],npp_year:2019,ppr_methods:[{id:'simple trophic chain',kind:'taxon',scopes:['all']},{id:'network',kind:'model',scopes:['all','inner']}],npp_methods:[{id:'vgpm'}],units:{a:unit([90,180],1),b:unit([810,1620],90)}};
}
const state={units:['a','b'],method:'simple trophic chain',scope:'all',mode:'ppr',npp:'vgpm'};
test('ratio is the ratio of matched sums with wet-weight to carbon conversion',()=>{
 const r=aggregate(fixture(),{...state,mode:'ratio'});
 assert.deepEqual(r.included,['a','b']);
 assert.equal(r.points[0].ppr,900);
 assert.equal(r.points[0].npp,91);
 assert.equal(r.points[0].value,100*900/9/91);
 assert.equal(r.points[1].npp,91); // fixed 2019 baseline duplicated
 assert.equal(r.points[1].coverage,.75);
});
test('a stable cohort excludes missing years and missing NPP from both totals',()=>{
 const db=fixture();db.units.b.npp.vgpm=null;
 let r=aggregate(db,{...state,mode:'ratio'});
 assert.deepEqual(r.included,['a']);assert.equal(r.points[0].ppr,90);
 assert.match(r.excluded[0].reason,/NPP/);
 db.units.b.npp.vgpm=90;db.units.b.simple.ppr[1]=null;
 r=aggregate(db,state);assert.deepEqual(r.included,['a']);assert.equal(r.points[0].value,90);
 assert.match(r.excluded[0].reason,/annual/);
});
test('true zeros survive; empty, unknown and unsupported choices never make up zero',()=>{
 const db=fixture();db.units.a.simple.ppr=[0,0];db.units.a.npp.vgpm=0;
 assert.equal(aggregate(db,{...state,units:['a']}).points[0].value,0);
 for(const extra of [{units:[]},{units:['unknown']},{method:'unknown'},{scope:'inner'},{years:[1999]},{mode:'ratio',npp:'unknown'},{mode:'ratio',units:['a']}]) {
   const r=aggregate(db,{...state,...extra});assert.ok(r.points.every(p=>p.value===null));
 }
});
test('model overrides are independent and failures never fall back to simple',()=>{
 const db=fixture();
 const model=(id,status,ppr)=>({id,verified:true,scopes:{all:{methods:{network:{status,ppr,covered_catch:[5,10]}}}}});
 db.units.a.models=[model('old','ok',[50,100]),model('new','ok',[500,1000])];db.units.a.default_model='old';
 db.units.b.models=[model('bad','DIVERGED',[900,1800])];db.units.b.default_model='bad';
 let r=aggregate(db,{...state,method:'network'});assert.equal(r.points[0].value,50);assert.equal(r.excluded.length,1);
 assert.deepEqual(r.model_ids,{a:'old'});assert.match(toCSV(r,{...state,method:'network'}),/old/);
 r=aggregate(db,{...state,method:'network',models:{a:'new'}});assert.equal(r.points[0].value,500);
 r=aggregate(db,{...state,method:'network',models:{a:'missing'}});assert.equal(r.points[0].value,null);
 db.units.a.models[0].verified=false;assert.equal(aggregate(db,{...state,method:'network'}).points[0].value,null);
});
test('deduplicates IDs, supports explicit years and future annual NPP',()=>{
 const db=fixture();db.units.a.npp.vgpm=[1,2];
 const r=aggregate(db,{...state,mode:'ratio',units:['a','a'],years:[2001]});
 assert.deepEqual(r.included,['a']);assert.equal(r.points.length,1);assert.equal(r.points[0].npp,2);assert.equal(r.points[0].value,1000);
});
test('CSV retains the plotted values, coverage and denominator provenance',()=>{
 const r=aggregate(fixture(),{...state,mode:'ratio'});
 const csv=toCSV(r,{...state,mode:'ratio'});
 assert.match(csv,/year,value,ppr_tonnes_wet_pp,npp_tonnes_carbon/);
 assert.match(csv,/2019/);assert.match(csv,/simple trophic chain/);
 assert.equal(csv.trim().split('\n').length,3);
});
test('individual graphs can retain genuine annual gaps without drawing zero or changing a sum cohort',()=>{
 const db=fixture();db.units.a.simple.ppr[0]=null;
 let r=aggregate(db,{...state,units:['a'],allow_gaps:true});
 assert.deepEqual(r.included,['a']);assert.deepEqual(r.points.map(p=>p.value),[null,180]);
 r=aggregate(db,{...state,allow_gaps:true});assert.deepEqual(r.included,['b']);
 db.units.a.simple.ppr[0]=90;db.units.a.npp.vgpm=[null,2];
 r=aggregate(db,{...state,mode:'ratio',units:['a'],allow_gaps:true});
 assert.deepEqual(r.points.map(p=>p.value),[null,1000]);
});
