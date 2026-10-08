const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm'),path=require('node:path');
const root=process.cwd(),map=fs.readFileSync(path.join(root,'interactive_map/index.html'),'utf8'),trend=fs.readFileSync(path.join(root,'interactive_map/trends.html'),'utf8');
for(const [name,page] of [['map',map],['trends',trend]])for(const m of page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))new vm.Script(m[1],{filename:name});
function payload(page,name){const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;const end=Math.min(...[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0));return JSON.parse(page.slice(start,end));}
const db=payload(map,'DB'),series=payload(trend,'SERIES_DB'),unit=db.network.units.HS_077;
const id='077HS_1_Eastern_tropical_Pacific_(1993-1997)',mi=unit.models.findIndex(m=>m.id===id),model=unit.models[mi],sm=series.units.HS_077.models.find(m=>m.id===id);
assert.equal(model.researcher_review.status,'Validated by researcher');assert.equal(model.researcher_review.researcher_name,'Ido Carmel');assert.equal(model.researcher_review.review_date,'2026-10-08');assert.deepEqual(model.researcher_review,sm.researcher_review);
const excluded=['Grazing birds','Pursuit birds','Toothed whales','Spotted dolphin','Mesopelagic dolphins','Large sharks','Small sharks'];assert.deepEqual([...model.display_ppr_excluded_group_ids].sort(),excluded.sort());
const ctx={};vm.createContext(ctx);const start=map.indexOf('/* Shared annual denominator lookup.');vm.runInContext(map.slice(start,map.indexOf('/* Rank the full chosen geography;',start)),ctx);
const groups=ctx.PPRGroups,metrics=vm.runInContext('PPRMetrics',ctx),allIds=model.group_data.groups.map(g=>g.id);
assert.equal(groups.selection(model,allIds).count,allIds.length-7,'Select all cannot readmit researcher exclusions');
const raw=structuredClone(model);delete raw.display_ppr_excluded_group_ids;delete raw.researcher_review;const rawUnit={...unit,models:unit.models.map((m,i)=>i===mi?raw:m)};
const close=(a,b,label)=>{if(a==null||b==null)return assert.equal(a,b,label);assert(Math.abs(a-b)<=Math.max(1e-6,Math.abs(b)*1e-12),label+': '+a+' / '+b);};
let cases=0,reduced=0;
for(const [scope,data] of Object.entries(model.scopes))for(const method of data.methods)for(const basis of ['landings','catch','discards']){
 const state={unit_id:'HS_077',mode:'ppr',scope,method,year:2019,catch_basis:basis,unidentified:'method',simple_unit:db.network.simple_units.HS_077};
 const a=metrics.evaluate(unit,mi,state),b=metrics.evaluate(rawUnit,mi,state);
 for(const key of ['catch','total_catch','coverage','total_catch_all','total_discards','unidentified_catch'])close(a[key],b[key],key);
 if(a.value!=null&&b.value!=null){assert(a.value<=b.value+1e-6,'Exclusions cannot increase PPR');if(a.value<b.value-1e-6)reduced++;cases++;}
}
assert(reduced>0,'At least one mapped contribution should be omitted');
for(const mode of ['b','rho_living'])assert.deepEqual(metrics.evaluate(unit,mi,{mode,te:'GE'}),metrics.evaluate(rawUnit,mi,{mode,te:'GE'}));
class Element{constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.className='';}appendChild(c){this.children.push(c);return c;}setAttribute(k,v){this[k]=v;}}
const dc={document:{createElement:t=>new Element(t),createTextNode:t=>new Element('#text',t)}};vm.createContext(dc);vm.runInContext(fs.readFileSync(path.join(root,'tools/project_core/maps/researcher_review.js'),'utf8'),dc);const review=vm.runInContext('PPRResearcherReview',dc),rendered=new Element('div');assert(review.append(rendered,model));assert.deepEqual(rendered.children[0].children.filter(c=>c.tag==='h4').map(c=>c.textContent),['Model extraction notes','GE diagnostics','TE diagnostics','SPPR Calculation Notes','Geographic fit','Taxon mapping confidence']);const named=new Element('div');review.appendName(named,model);assert.equal(named.children[1].className,'researcher-validated-name');
console.log(JSON.stringify({syntax_verified:true,matching_signed_review:true,mandatory_exclusions:7,green_model_name:true,six_flat_review_headings:true,catch_coverage_and_diagnostics_unchanged:true,available_cases:cases,reduced_PPR_cases:reduced}));
