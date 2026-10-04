const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'../../../../..'),pages=path.join(root,'interactive_map');
const map=fs.readFileSync(path.join(pages,'index.html'),'utf8'),trend=fs.readFileSync(path.join(pages,'trends.html'),'utf8');
for(const [name,page] of [['map',map],['trends',trend]])for(const match of page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))new vm.Script(match[1],{filename:name});
function payload(page,name){const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;const ends=[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0);return JSON.parse(page.slice(start,Math.min(...ends)));}
const catalog=payload(map,'DB'),series=payload(trend,'SERIES_DB');
const unit=catalog.network.units.LME_034,id='34_1_Bay_of_Bengal_(1978)',mi=unit.models.findIndex(m=>m.id===id),model=unit.models[mi];
const sm=series.units.LME_034.models.find(m=>m.id===id);assert.deepEqual(model.researcher_review,sm.researcher_review);
const review=model.researcher_review;assert.equal(review.status,'Validated by researcher');assert.equal(review.researcher_name,'Ido Carmel');assert.equal(review.review_date,'2026-10-01');
assert.equal(review.report_sha256,'3e1f329da2cb8160f8f8cd56443fcb4f62b1377689dbc4206ab9846dd6196da2');
assert.deepEqual(model.display_ppr_excluded_group_ids,[]);assert.deepEqual(sm.display_ppr_excluded_group_ids,[]);
assert(review.sections[1].rows[0].text.includes('ρ_living = 0.59'));assert(review.sections[1].rows[0].text.includes('b = 0.17'));
assert(review.sections[1].rows[1].text.includes('ρ_living = 0.63'));assert(review.sections[1].rows[1].text.includes('b = 0 (structural convention).'));
assert(review.sections[2].rows[0].text.includes('seabirds (GE<0.01%'));assert(review.note.includes('contains no matching group'));assert(review.note.includes('No model groups are excluded'));
assert.equal(review.sections[4].appendix_path,'regions/LME_034/LME034_taxon_mapping_appendix.xlsx');
const start=map.indexOf('/* Shared annual denominator lookup.'),ctx={};vm.createContext(ctx);vm.runInContext(map.slice(start,map.indexOf('/* Rank the full chosen geography;',start)),ctx);
const metrics=vm.runInContext('PPRMetrics',ctx),groups=vm.runInContext('PPRGroups',ctx);assert.equal(groups.selection(model).count,model.group_data.groups.length);
const raw=structuredClone(model);delete raw.display_ppr_excluded_group_ids;delete raw.researcher_review;
const rawUnit={...unit,models:unit.models.map((m,i)=>i===mi?raw:m)};
const close=(a,b,key)=>{if(a==null||b==null)return assert.equal(a,b,key);assert(Math.abs(a-b)<=Math.max(1e-6,Math.abs(b)*1e-12),key+': '+a+' versus '+b);};
let cases=0;for(const [scope,data] of Object.entries(model.scopes))for(const method of data.methods)for(const basis of ['landings','catch','discards']){
const state={unit_id:'LME_034',mode:'ppr',scope,method,year:2019,catch_basis:basis,unidentified:'method',simple_unit:catalog.network.simple_units.LME_034};
const a=metrics.evaluate(unit,mi,state),b=metrics.evaluate(rawUnit,mi,state);for(const key of ['value','catch','total_catch','coverage','total_catch_all','total_discards','unidentified_catch'])close(a[key],b[key],key);cases++;}
for(const mode of ['b','rho_living'])assert.deepEqual(metrics.evaluate(unit,mi,{mode,te:'GE'}),metrics.evaluate(rawUnit,mi,{mode,te:'GE'}));
assert.deepEqual(metrics.evaluate(unit,mi,{mode:'npp',year:2019,npp_data:{years:[2019],values:[100]}}),metrics.evaluate(rawUnit,mi,{mode:'npp',year:2019,npp_data:{years:[2019],values:[100]}}));
const result={map_and_trends_syntax:true,matching_review_snapshots:true,status:review.status,reviewer:review.researcher_name,report_sha256:review.report_sha256,applicable_exclusions:[],cases,unchanged_display_ppr_catch_coverage_diagnostics_and_npp:true,honest_closing_note:review.note};
fs.writeFileSync(path.join(__dirname,'html_verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
