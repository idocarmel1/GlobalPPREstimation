const {test}=require('node:test');
const assert=require('node:assert/strict');
const api=require('../PPRAtlas/atlas/time_series_metrics.js');

function fixture() {
  const unit=x=>{
    const record=(factor,covered)=>({status:'ok',ppr:[90,180,270].map(v=>v*x*factor),covered_catch:[5,10,15].map(v=>v*x*covered)});
    const model=(id,factor)=>({id,verified:true,scopes:{
      all:{methods:{one:record(factor,1),two:record(2*factor,1.5),three:record(3*factor,1.8)}},
      inner:{methods:{one:record(factor/2,1),two:record(factor,1.5),three:record(1.5*factor,1.8)}}}});
    return {name:`Region ${x}`,simple:{ppr:[90,180,270].map(v=>v*x),catch:[10,20,30].map(v=>v*x),covered_catch:[8,16,24].map(v=>v*x)},
      npp:{vgpm:100*x},models:[model('old',1),model('new',4)],default_model:'old'};
  };
  return {years:[2000,2001,2002],npp_year:2019,npp_methods:[{id:'vgpm'}],
    ppr_methods:[{id:'taxon',kind:'taxon',scopes:['all']},...['one','two','three'].map(id=>({id,kind:'model',scopes:['all','inner']}))],
    units:{a:unit(1),b:unit(2),c:unit(3)}};
}
const state={units:['a','b','c'],methods:['one','two'],scope:'all',mode:'ppr',npp:'vgpm'};
const compare=(db,s)=>{assert.equal(typeof api.compare,'function','Multi-method comparison has not been implemented');return api.compare(db,s);};
const values=series=>series.points.map(p=>p.value);

function mcFixture() {
  const db=fixture();
  db.ppr_methods.push({id:'MC_new_GE',kind:'model',scopes:['all','inner']});
  for(const u of Object.values(db.units))for(const model of u.models){
    model.mc_diagnostics={MC_new_GE:{n_samples:100,n_accepted:100}};
    for(const scope of Object.values(model.scopes))scope.methods.MC_new_GE=structuredClone(scope.methods.three);
  }
  return db;
}

test('MC acceptance below 80% excludes an ecosystem from every curve and the NPP denominator',()=>{
  const db=mcFixture();
  db.units.a.models[0].mc_diagnostics.MC_new_GE.n_accepted=2;
  db.units.b.models[0].mc_diagnostics.MC_new_GE.n_accepted=80;
  const s={...state,methods:['one','MC_new_GE'],mode:'ratio'},r=compare(db,s);
  assert.deepEqual(r.included,['b','c']);
  assert.ok(r.series.every(series=>series.points[0].npp===500));
  assert.match(r.excluded[0].reason,/MC_new_GE.*2.*100.*80%/);
  assert.deepEqual(compare(db,{...state,methods:['one']}).included,['a','b','c']);
  assert.deepEqual(compare(db,{...s,models:{a:'new'}}).included,['a','b','c']);
  const csv=api.comparisonToCSV(r,s);
  assert.ok(csv.includes('b;c'));assert.ok(!csv.includes('a;b;c'));
});

test('MC cutoff applies to a baseline, single curve, all scopes and sensitivity treatments',()=>{
  const db=mcFixture();db.units.a.models[0].mc_diagnostics.MC_new_GE.n_accepted=79;
  assert.deepEqual(compare(db,{...state,methods:['one'],baseline:'MC_new_GE'}).included,['b','c']);
  for(const scope of ['all','inner'])for(const catch_basis of ['landings','catch','discards']){
    const r=compare(db,{...state,units:['a'],methods:['MC_new_GE'],scope,catch_basis,unidentified:'zero'});
    assert.deepEqual(r.included,[]);assert.match(r.excluded[0].reason,/79.*100.*80%/);
  }
});

test('an entirely rejected MC curve cannot silently restore ecosystems in the other curves',()=>{
  const db=mcFixture();
  for(const u of Object.values(db.units))u.models[0].mc_diagnostics.MC_new_GE.n_accepted=79;
  const r=compare(db,{...state,methods:['one','MC_new_GE']});
  assert.deepEqual(r.included,[]);assert.ok(r.series.every(s=>values(s).every(v=>v===null)));
  assert.ok(r.excluded.every(e=>/80%/.test(e.reason)));
});

test('single method without baseline preserves the exact aggregate and CSV contract',()=>{
  const db=fixture();db.units.b.simple.ppr[1]=null;
  const s={...state,methods:['taxon']},original=api.aggregate(db,{...s,method:'taxon'});
  const result=compare(db,s),{method,...series}=result.series[0];
  assert.equal(method,'taxon');assert.deepEqual(series,original);
  assert.deepEqual(result.points,original.points);assert.deepEqual(result.included,['a','c']);
  assert.equal(api.comparisonToCSV(result,s),api.toCSV(original,{...s,method:'taxon'}));
});

test('two and three curves preserve individual method masses with one carbon conversion',()=>{
  const db=fixture(),before=structuredClone(db);
  const two=compare(db,state),three=compare(db,{...state,methods:['one','two','three']});
  assert.deepEqual(two.series.map(values),[[60,120,180],[120,240,360]]);
  assert.deepEqual(three.series.map(s=>s.points[0].value),[60,120,180]);
  assert.equal(three.series[1].points[0].ppr,120);assert.equal(three.series[1].points[0].covered_catch,45);
  assert.equal(three.normalized,false);assert.equal(three.baseline,null);assert.deepEqual(db,before);
});

test('comparisons use the intersection of ecosystem cohorts and disclose method exclusions',()=>{
  const db=fixture();db.units.c.models[0].scopes.all.methods.two.status='FAILED diagnostic';
  db.units.b.models[0].scopes.all.methods.three.ppr=[null,null,null];
  const r=compare(db,{...state,methods:['one','two','three']});
  assert.deepEqual(r.included,['a']);assert.equal(r.selected,3);
  assert.deepEqual(r.series.map(s=>s.points[0].value),[10,20,30]);
  for(const s of r.series){assert.deepEqual(s.included,['a']);assert.deepEqual(s.excluded,r.excluded);assert.equal(s.selected,3);assert.deepEqual(s.model_ids,{a:'old'});}
  assert.match(r.excluded.find(e=>e.id==='b').reason,/three/);
  assert.match(r.excluded.find(e=>e.id==='c').reason,/two.*FAILED/);
});

test('a wholly unavailable selected method retains failure reasons without erasing usable curves',()=>{
  const db=fixture();for(const u of Object.values(db.units))u.models[0].scopes.all.methods.three.status='DIVERGED';
  const r=compare(db,{...state,methods:['one','three','two']});
  assert.deepEqual(r.included,['a','b','c']);assert.deepEqual(values(r.series[0]),[60,120,180]);
  assert.deepEqual(values(r.series[1]),[null,null,null]);assert.match(r.series[1].reason,/DIVERGED/);
  assert.match(r.series[1].excluded[0].reason,/DIVERGED/);assert.equal(r.series[2].points[0].value,120);
});

test('disjoint valid method cohorts produce no fabricated common sum',()=>{
  const db=fixture();
  for(const id of ['b','c'])db.units[id].models[0].scopes.all.methods.one.status='FAILED';
  db.units.a.models[0].scopes.all.methods.two.status='FAILED';
  const r=compare(db,state);
  assert.deepEqual(r.included,[]);assert.ok(r.series.every(s=>values(s).every(v=>v===null)));
  assert.match(r.reason,/common.*ecosystem/i);assert.equal(r.excluded.length,3);
});

test('an unplotted baseline joins the common cohort and selected baseline normalizes to one',()=>{
  const db=fixture();db.units.c.models[0].scopes.all.methods.one.status='FAILED';
  let r=compare(db,{...state,methods:['two','three'],baseline:'one'});
  assert.deepEqual(r.series.map(s=>s.method),['two','three']);assert.deepEqual(r.included,['a','b']);
  assert.equal(r.normalized,true);assert.equal(r.baseline,'one');
  assert.deepEqual(r.series.map(s=>s.points[0].value),[2,3]);
  assert.equal(r.series[0].points[0].unnormalized_value,60);
  assert.equal(r.series[0].points[0].baseline_value,30);assert.equal(r.series[0].points[0].baseline_ppr,30);
  assert.equal(r.series[0].points[0].baseline_covered_catch,15);assert.match(r.excluded[0].reason,/baseline.*one/i);
  r=compare(db,{...state,methods:['one','two'],baseline:'one'});
  assert.deepEqual(values(r.series[0]),[1,1,1]);assert.deepEqual(values(r.series[1]),[2,2,2]);
});

test('missing and zero baseline samples remain gaps and unknown baseline fails closed',()=>{
  const db=fixture();db.units.a.models[0].scopes.all.methods.one.ppr=[0,null,90];
  const s={...state,units:['a'],methods:['two'],baseline:'one',allow_gaps:true};
  const r=compare(db,s);assert.deepEqual(values(r.series[0]),[null,null,6]);
  assert.equal(r.series[0].points[0].baseline_value,0);assert.equal(r.series[0].points[1].baseline_value,null);
  for(const baseline of ['unknown','three']){
    if(baseline==='three')db.units.a.models[0].scopes.all.methods.three.status='FAILED';
    const failed=compare(db,{...s,baseline});assert.ok(values(failed.series[0]).every(v=>v===null));
    assert.match(failed.reason,/baseline.*unavailable/i);assert.deepEqual(failed.included,[]);
  }
});

test('normalized PPR/NPP uses the matched denominator and cancels without another carbon conversion',()=>{
  const db=fixture();db.units.c.npp.vgpm=null;
  const r=compare(db,{...state,mode:'ratio',baseline:'one'});
  assert.deepEqual(r.included,['a','b']);assert.equal(r.series[1].points[0].value,2);
  assert.equal(r.series[1].points[0].unnormalized_value,20);assert.equal(r.series[1].points[0].baseline_value,10);
  assert.equal(r.series[1].points[0].ppr,60);assert.equal(r.series[1].points[0].npp,300);
  db.units.a.npp.vgpm=[100,200,300];
  assert.equal(compare(db,{...state,mode:'ratio',baseline:'one'}).annual_npp,true);
});

test('source scopes, year subsets and model overrides also apply to the baseline',()=>{
  const r=compare(fixture(),{...state,units:['a','b'],scope:'inner',years:[2002],models:{a:'new'},baseline:'one'});
  assert.deepEqual(r.series[0].model_ids,{a:'new',b:'old'});
  assert.equal(r.series[0].points[0].baseline_ppr,90);assert.equal(r.series[1].points[0].ppr,180);
  assert.equal(r.series[1].points[0].value,2);assert.equal(r.points[0].year,2002);
});

test('empty and duplicate method choices preserve alignment and avoid duplicate curves',()=>{
  const db=fixture();let r=compare(db,{...state,methods:[]});
  assert.deepEqual(r.series,[]);assert.deepEqual(r.included,[]);assert.equal(r.points.length,3);
  assert.ok(r.points.every(p=>p.value===null));assert.match(r.reason,/method/i);
  r=compare(db,{...state,methods:['two','one','two'],units:['a','a','b']});
  assert.deepEqual(r.series.map(s=>s.method),['two','one']);assert.equal(r.selected,2);
});

function parseRow(line){return [...line.matchAll(/(?:^|,)(?:"((?:[^"]|"")*)"|([^,]*))/g)].map(m=>(m[1]??m[2]).replaceAll('""','"'));}
test('comparison CSV emits exactly the plotted curves and baseline provenance in long format',()=>{
  const s={...state,methods:['two','three'],baseline:'one'},r=compare(fixture(),s);
  const lines=api.comparisonToCSV(r,s).trim().split('\n'),header=parseRow(lines[0]);
  assert.equal(lines.length,7);
  const rows=lines.slice(1).map(line=>Object.fromEntries(parseRow(line).map((v,i)=>[header[i],v])));
  const row=rows.find(r=>r.year==='2000' && r.ppr_method==='two');
  assert.equal(row.value,'2');assert.equal(row.ppr_tonnes_carbon,'120');
  assert.equal(row.unnormalized_value,'120');assert.equal(row.baseline_method,'one');
  assert.equal(row.baseline_value,'60');assert.equal(row.baseline_ppr_tonnes_carbon,'60');
  assert.equal(row.baseline_covered_catch_tonnes,'30');assert.equal(row.included_ids,'a;b;c');
  assert.equal(row.selected_ecosystems,'3');assert.equal(JSON.parse(row.model_ids).a,'old');
});

test('an unplotted model baseline records default model identities for a taxon numerator',()=>{
  const db=fixture();db.units.a.default_model='new';
  const s={...state,units:['a','b'],methods:['taxon'],baseline:'one'},r=compare(db,s);
  assert.deepEqual(r.series[0].model_ids,{});assert.equal(r.series[0].points[0].value,.5);
  assert.deepEqual(r.baseline_model_ids,{a:'new',b:'old'});
  const lines=api.comparisonToCSV(r,s).trim().split('\n'),header=parseRow(lines[0]);
  const row=Object.fromEntries(parseRow(lines[1]).map((value,i)=>[header[i],value]));
  assert.deepEqual(JSON.parse(row.model_ids),{});assert.deepEqual(JSON.parse(row.model_overrides),{});
  assert.deepEqual(JSON.parse(row.baseline_model_ids),{a:'new',b:'old'});
});

test('zero and missing baseline gaps retain masses, model provenance and per-year CSV reasons',()=>{
  const db=fixture();db.units.a.models[0].scopes.all.methods.one.ppr=[0,null,90];
  const s={...state,units:['a'],methods:['two'],baseline:'one',allow_gaps:true},r=compare(db,s);
  const [zero,missing,valid]=r.series[0].points;
  assert.equal(zero.value,null);assert.equal(zero.unnormalized_value,20);
  assert.equal(zero.baseline_value,0);assert.equal(zero.baseline_ppr,0);assert.equal(zero.baseline_covered_catch,5);
  assert.match(zero.unavailable_reason,/baseline.*zero/i);assert.match(missing.unavailable_reason,/baseline.*unavailable/i);
  assert.equal(missing.baseline_ppr,null);assert.equal(valid.value,6);assert.equal(valid.unavailable_reason,'');
  const lines=api.comparisonToCSV(r,s).trim().split('\n'),header=parseRow(lines[0]);
  const row=Object.fromEntries(parseRow(lines[1]).map((value,i)=>[header[i],value]));
  assert.equal(row.value,'');assert.equal(row.baseline_value,'0');assert.equal(row.baseline_ppr_tonnes_carbon,'0');
  assert.equal(row.unnormalized_value,'20');assert.deepEqual(JSON.parse(row.baseline_model_ids),{a:'old'});
  assert.match(row.unavailable_reason,/baseline.*zero/i);
  db.units.a.models[0].scopes.all.methods.one.ppr=[0,0,0];
  const allZero=compare(db,s);assert.ok(allZero.series[0].points.every(p=>p.value===null));
  assert.match(allZero.reason,/baseline.*positive/i);assert.deepEqual(allZero.baseline_model_ids,{a:'old'});
});
