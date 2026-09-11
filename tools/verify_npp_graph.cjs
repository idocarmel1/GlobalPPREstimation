/* Independent arithmetic over the actual NPP graph export and its reference. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),graph=require('../PPRAtlas/atlas/time_series_metrics.js');
const db=JSON.parse(fs.readFileSync(path.join(root,'PPRAtlas/data/time_series.json'),'utf8'));
const reference=db.global_npp;assert.ok(reference,'Global reference must be exported');
const allowPartial=process.argv.includes('--allow-partial-reference');
assert.equal(reference.unit_ids.length,84);assert.equal(new Set(reference.unit_ids).size,84);
assert.ok(reference.unit_ids.includes('LME_064'));assert.ok(reference.unit_ids.includes('HS_018'));
assert.ok(reference.unit_ids.every(id=>id.startsWith('LME_')||id.startsWith('HS_')));
assert.equal(typeof reference.ensemble_convention,'string');
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const near=(a,b,label)=>{assert.equal(a==null,b==null,label+' availability');if(a!=null)assert.ok(Math.abs(a-b)<=1e-8+Math.abs(b)*1e-12,`${label}: ${a} != ${b}`);};
const report={status:'ok',reference:reference.id,reference_regions:reference.unit_ids.length,reference_years:[],checks:0,examples:{}};
for(const [i,year]of db.years.entries()){
  const meta=reference.metadata[String(year)],value=reference.values[i];
  if(value!=null){
    const models=meta.model_names||meta.available_models;
    const totals=models.map(model=>reference.npp['npp_'+model+'_tC_yr'][i]).sort((a,b)=>a-b);
    assert.ok(totals.length&&totals.every(finite));
    const median=totals.length%2?totals[Math.floor(totals.length/2)]:(totals[totals.length/2-1]+totals[totals.length/2])/2;
    near(value,median,year+' reference ensemble order');
    assert.equal(meta.complete,true);assert.equal(meta.coverage_limited,true);assert.equal(meta.coverage_complete,false);
    report.reference_years.push(year);
  }
}
const expectedYears=Array.from({length:22},(_,i)=>1998+i);
report.missing_reference_years=expectedYears.filter(year=>!report.reference_years.includes(year));
if(allowPartial&&report.missing_reference_years.length)report.status='in_progress';
else assert.deepEqual(report.reference_years,expectedYears,'Full 1998–2019 reference must be complete');
const state={scope:'all',mode:'ratio',npp:'ens_median_tC_yr',catch_basis:'landings',uncertainty:'1'};
for(const year of [1950,1998,2007,2019])for(const ids of [['LME_034'],['LME_034','LME_028'],['HS_018']]){
  for(const method of ['new_GE','SPPR_1995_TE0.1','unknown']){
    const s={...state,units:ids,years:[year],method,methods:[method]},global=graph.compare(db,{...s,npp_scope:'global'}),point=global.points[0];
    const expected=reference.values[db.years.indexOf(year)];
    near(point.npp,expected,`${year}/${ids}/${method} fixed denominator`);
    if(finite(point.ppr)&&expected>0){
      near(point.value,100*point.ppr/expected,'global ratio');
      if(point.sensitivity?.status==='assessed'){
        near(point.sensitivity.lower,100*point.sensitivity.min_tC/expected,'global lower');
        near(point.sensitivity.upper,100*point.sensitivity.max_tC/expected,'global upper');
      }
    }else assert.equal(point.value,null);
    const selected=graph.compare(db,s),p=selected.points[0];
    const localValues=selected.included.map(id=>db.units[id].npp.ens_median_tC_yr[db.years.indexOf(year)]);
    const local=localValues.length&&localValues.every(v=>finite(v)&&v>0)?localValues.reduce((a,b)=>a+b,0):null;
    near(p.npp,local,'selected matching denominator');
    if(finite(p.ppr)&&local>0)near(p.value,100*p.ppr/local,'selected ratio');
    const json=JSON.parse(graph.comparisonToJSON(global,{...s,npp_scope:'global'}));
    near(json.result.points[0].npp_denominator,expected,'JSON denominator');
    if(year===2019&&ids.length===1&&ids[0]==='LME_034')report.examples[method]={selected:p.value,global:point.value,denominator:expected};
    report.checks++;
  }
}
// The actual Arctic identity has no catch series or verified Ecopath model.
for(const ids of [['HS_018'],['LME_034','HS_018']]){
  const s={...state,mode:'npp',units:ids,methods:['unavailable','new_GE'],baseline:'unavailable'};
  const result=graph.compare(db,s);assert.equal(result.series.length,1);assert.equal(result.normalized,false);
  assert.deepEqual(result.included,ids);
  for(const [i,p]of result.points.entries()){
    const values=ids.map(id=>db.units[id].npp.ens_median_tC_yr[i]);
    const expected=values.every(v=>finite(v)&&v>=0)?values.reduce((a,b)=>a+b,0):null;
    near(p.value,expected,'NPP-only sum');assert.equal(p.ppr,null);
    report.checks++;
  }
}
fs.writeFileSync(path.join(root,'data/npp_graph_validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
