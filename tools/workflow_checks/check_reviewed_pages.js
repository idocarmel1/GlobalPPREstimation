const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const [mapPath,trendPath]=process.argv.slice(2);assert(mapPath&&trendPath,'Pass the generated map and trends pages');
const map=fs.readFileSync(mapPath,'utf8'),trend=fs.readFileSync(trendPath,'utf8');
for(const [name,page] of [['map',map],['trends',trend]]){
  for(const match of page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))new vm.Script(match[1],{filename:name});
}
function payload(page,name){
  const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;
  const ends=[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0);
  try{return JSON.parse(page.slice(start,Math.min(...ends)));}catch(e){throw new Error('Cannot parse '+name+' embedded payload: '+e.message);}
}
const catalog=payload(map,'DB'),series=payload(trend,'SERIES_DB');
const unit=catalog.network.units.LME_036,mi=unit.models.findIndex(m=>m.id===series.units.LME_036.default_model),model=unit.models[mi];
const sm=series.units.LME_036.models.find(m=>m.id===model.id);
assert(model.researcher_review);assert.deepEqual(model.researcher_review,sm.researcher_review);
assert.equal(model.researcher_review.status,'Validated by researcher');
assert.equal(model.display_ppr_excluded_group_ids.length,4);
assert.deepEqual(model.researcher_review.sections.map(s=>s.heading),['Model extraction notes','GE and TE diagnostics','Groups excluded from displayed PPR','Geographic fit','Taxon mapping confidence']);
assert.equal(model.researcher_review.sections[4].table[1][3],'31.8829%');
assert(model.researcher_review.sections[4].reference.some(p=>p.includes('2019 landings')));
const start=map.indexOf('/* Shared annual denominator lookup.'),ctx={};vm.createContext(ctx);vm.runInContext(map.slice(start,map.indexOf('/* Rank the full chosen geography;',start)),ctx);
const metrics=vm.runInContext('PPRMetrics',ctx);
const original={...model};delete original.display_ppr_excluded_group_ids;delete original.researcher_review;
const rawUnit={...unit,models:unit.models.map((m,i)=>i===mi?original:m)};
const close=(a,b,label)=>{if(a==null||b==null)return assert.equal(a,b,label);assert(Math.abs(a-b)<=Math.max(1e-6,Math.abs(b)*1e-12),label+': '+a+' versus '+b);};
let checked=0;
for(const [scope,data] of Object.entries(model.scopes))for(const method of data.methods)for(const basis of ['landings','catch','discards']){
  const state={unit_id:'LME_036',mode:'ppr',scope,method,year:2019,catch_basis:basis,unidentified:'method',simple_unit:catalog.network.simple_units.LME_036};
  const a=metrics.evaluate(unit,mi,state),b=metrics.evaluate(rawUnit,mi,state);
  if(a.value==null||b.value==null){assert.equal(a.value,b.value);continue;}
  close(a.value,b.value,'No mapped contribution exists for the four excluded groups');
  for(const key of ['catch','total_catch','coverage','total_catch_all','total_discards','unidentified_catch'])close(a[key],b[key],key+' remains unchanged');
  checked++;
}
for(const mode of ['b','rho_living'])assert.deepEqual(metrics.evaluate(unit,mi,{mode,te:'GE'}),metrics.evaluate(rawUnit,mi,{mode,te:'GE'}));
assert.deepEqual(metrics.evaluate(unit,mi,{mode:'npp',year:2019,npp_data:{years:[2019],values:[100]}}),metrics.evaluate(rawUnit,mi,{mode:'npp',year:2019,npp_data:{years:[2019],values:[100]}}));
console.log(`Generated pages passed syntax, matching review snapshots, five headings, fixed confidence reference, ${checked} available method/scope/catch-basis cases, unchanged diagnostics/NPP.`);
