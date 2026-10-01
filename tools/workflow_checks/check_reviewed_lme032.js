const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const [mapPath,trendPath]=process.argv.slice(2);
assert(mapPath&&trendPath,'Pass generated map and trends pages');
const map=fs.readFileSync(mapPath,'utf8'),trend=fs.readFileSync(trendPath,'utf8');
function payload(page,name){
  const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;
  const ends=[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0);
  return JSON.parse(page.slice(start,Math.min(...ends)));
}
const catalog=payload(map,'DB'),series=payload(trend,'SERIES_DB');
const unit=catalog.network.units.LME_032,id='32_1_Arabian_Sea_off_Karnataka_(2000)';
const mi=unit.models.findIndex(m=>m.id===id),model=unit.models[mi];
const sm=series.units.LME_032.models.find(m=>m.id===id);
assert.deepEqual(model.researcher_review,sm.researcher_review);
const review=model.researcher_review;
assert.equal(review.status,'Validated by researcher');
assert.equal(review.researcher_name,'Ido Carmel');assert.equal(review.review_date,'2026-10-01');
assert.equal(review.report_sha256,'cea0b847d09f84b97ef403342eaa716a6fa4f328fc9983f13f6f00ccf38800ac');
assert.deepEqual(model.display_ppr_excluded_group_ids,['Marine Mammals']);
assert.deepEqual(sm.display_ppr_excluded_group_ids,['Marine Mammals']);
assert.equal(review.sections[4].appendix_path,'regions/LME_032/LME032_taxon_mapping_appendix.xlsx');
assert.deepEqual(review.sections[4].table[2],['Medium','205','48.5275%','64.2253%']);
assert(review.sections[1].rows[0].text.includes('rho_living = 0.58'));
assert(review.sections[1].rows[1].text.includes('(34) marine mammals'));
assert(review.note.includes('marine mammals are excluded from displayed PPR'));
assert(!review.note.includes('pinnipeds'));
const start=map.indexOf('/* Shared annual denominator lookup.'),ctx={};vm.createContext(ctx);
vm.runInContext(map.slice(start,map.indexOf('/* Rank the full chosen geography;',start)),ctx);
const metrics=vm.runInContext('PPRMetrics',ctx),groups=vm.runInContext('PPRGroups',ctx);
const selection=groups.selection(model);
assert.equal(selection.count,model.group_data.groups.length-1);
assert(!selection.ids.includes('Marine Mammals'));
const raw=structuredClone(model);delete raw.display_ppr_excluded_group_ids;delete raw.researcher_review;
const rawUnit={...unit,models:unit.models.map((m,i)=>i===mi?raw:m)};
const close=(a,b,key)=>{
  if(a==null||b==null)return assert.equal(a,b,key);
  assert(Math.abs(a-b)<=Math.max(1e-6,Math.abs(b)*1e-12),key+': '+a+' versus '+b);
};
let cases=0;
for(const [scope,data] of Object.entries(model.scopes))for(const method of data.methods)for(const basis of ['landings','catch','discards']){
  const state={unit_id:'LME_032',mode:'ppr',scope,method,year:2019,catch_basis:basis,unidentified:'method',simple_unit:catalog.network.simple_units.LME_032};
  const a=metrics.evaluate(unit,mi,state),b=metrics.evaluate(rawUnit,mi,state);
  for(const key of ['catch','total_catch','coverage','total_catch_all','total_discards','unidentified_catch'])close(a[key],b[key],key);
  cases++;
}
assert(cases>0);
for(const mode of ['b','rho_living'])assert.deepEqual(metrics.evaluate(unit,mi,{mode,te:'GE'}),metrics.evaluate(rawUnit,mi,{mode,te:'GE'}));
console.log(`LME032 pages passed: exact reviewed source text/identity, correct appendix, one mandatory mammal exclusion, ${cases} unchanged catch/coverage cases and unchanged diagnostics.`);
