const {test}=require('node:test');
const assert=require('node:assert/strict');
const ranking=require('../PPRAtlas/atlas/map_ranking.js');
const metrics=require('../PPRAtlas/atlas/network_metrics.js');
const region=(id,value)=>({unit_id:id,networkResult:{value}});

test('ranking and cumulative shares use the selected ensemble before limiting display',()=>{
  const rows=[region('outside',1000),region('a',50),region('b',30),region('c',20),region('missing',null)];
  const result=ranking.rank(rows,new Set(['a','b','c','missing']));
  assert.equal(result.total,100);assert.equal(result.available,3);assert.equal(result.size,4);
  const a=rows.find(r=>r.unit_id==='a'),b=rows.find(r=>r.unit_id==='b');
  assert.equal(a.ppr_rank,1);assert.equal(a.cumulative_ppr_share,.5);
  assert.equal(b.cumulative_ppr_share,.8);
  assert.equal(a.cumulative_before_share,0);assert.equal(b.cumulative_before_share,.5);
  assert.equal(rows.find(r=>r.unit_id==='outside').ppr_rank,null);
  assert.deepEqual(rows.filter(r=>ranking.visible(r,'1')).map(r=>r.unit_id),['a']);
  assert.deepEqual(rows.filter(r=>ranking.visible(r,'all')).map(r=>r.unit_id),['a','b','c','missing']);
  assert.equal(b.cumulative_ppr_share,.8);
  ranking.rank(rows,null);
  assert.equal(rows[0].unit_id,'outside');assert.equal(a.ppr_rank,2);
});

test('ties share rank and cumulative color, while Top N displays exactly N',()=>{
  const rows=[region('c',10),region('b',20),region('a',20),region('z',0),region('missing',null)];
  ranking.rank(rows,null);
  assert.deepEqual(rows.map(r=>r.ppr_rank),[1,1,3,4,null]);
  assert.equal(rows[0].cumulative_ppr_share,.8);assert.equal(rows[1].cumulative_ppr_share,.8);
  assert.equal(rows[0].cumulative_before_share,0);assert.equal(rows[1].cumulative_before_share,0);
  assert.deepEqual(rows.filter(r=>ranking.visible(r,'1')).map(r=>r.unit_id),['a']);
  assert.equal(ranking.visible(rows[0],'custom','2.5'),false);
  assert.equal(ranking.visible(rows[0],'custom','0'),false);
  assert.equal(ranking.visible(rows[0],'custom',''),false);
  assert.equal(ranking.visible(rows[1],'custom','2'),true);
});

test('NPP works without a catch record or Ecopath model and is already carbon',()=>{
  const state={mode:'npp',year:2019,npp_data:{years:[2018,2019],values:[90,180]}};
  const result=metrics.evaluate(null,undefined,state);
  assert.equal(result.value,180);assert.equal(result.catch,null);assert.equal(result.npp.source_year,2019);
  assert.equal(metrics.evaluate(null,0,{...state,year:2017}).value,null);
});

test('NPP honors explicit historical substitution and keeps internal gaps missing',()=>{
  const state={mode:'npp',year:1995,npp_fill:'earliest',npp_data:{years:[1995,1998,1999,2000],values:[null,90,null,120]}};
  const early=metrics.evaluate(null,0,state);
  assert.equal(early.value,90);assert.equal(early.npp.substituted,true);
  assert.equal(metrics.evaluate(null,0,{...state,year:1999}).value,null);
  assert.equal(metrics.evaluate(null,0,{...state,npp_fill:'observed'}).value,null);
});

test('recorded zero NPP is ranked as zero production but cannot be a ratio denominator',()=>{
  const data={years:[1995,1998,1999],values:[null,0,90]};
  assert.equal(metrics.evaluate(null,0,{mode:'npp',year:1998,npp_data:data}).value,0);
  const historic=metrics.evaluate(null,0,{mode:'npp',year:1995,npp_fill:'earliest',npp_data:data});
  assert.equal(historic.value,0);assert.equal(historic.npp.source_year,1998);
  const denominator=require('../PPRAtlas/atlas/annual_npp.js').resolve(data.years,data.values,1998);
  assert.equal(denominator.value,null);
});
