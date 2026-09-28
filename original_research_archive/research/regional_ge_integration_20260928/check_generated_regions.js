const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.cwd(),here=__dirname;
const report=JSON.parse(fs.readFileSync(process.argv[2]||path.join(here,'STAGED_INTEGRATION_VERIFICATION.json'),'utf8'));
const folder=process.argv[3]||'interactive_map';
const html=fs.readFileSync(path.join(root,folder,'index.html'),'utf8');
const trend=fs.readFileSync(path.join(root,folder,'trends.html'),'utf8');
function embedded(text,name){const start=text.indexOf('const '+name+'=')+('const '+name+'=').length;const end=Math.min(text.indexOf('\n',start),text.indexOf('</script>',start));return JSON.parse(text.slice(start,end).trim().replace(/;$/,''));}
const db=embedded(html,'DB'),series=embedded(trend,'SERIES_DB');
const ctx={};vm.createContext(ctx);
vm.runInContext(html.slice(html.indexOf('/* Shared annual denominator lookup.'),html.indexOf('/* Rank the full chosen geography;')),ctx);
const evaluate=vm.runInContext('PPRMetrics.evaluate',ctx);
const tctx={};vm.createContext(tctx);const ts=trend.indexOf('/* Shared annual denominator lookup.');
vm.runInContext(trend.slice(ts,trend.indexOf('</script>',ts)),tctx);
const checked=[];
function near(a,b,label){assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=Math.max(1e-7,Math.abs(b)*1e-10),`${label}: ${a} != ${b}`);}
for(const r of report.selected_regions.filter(r=>r.updated)){
 const u=db.network.units[r.unit_id],mi=u.models.findIndex(m=>m.id===r.model_id);
 assert.ok(mi>=0,r.unit_id+' selected model present');
 const state={mode:'ppr',scope:'all',method:'new_GE',year:2019,catch_basis:'catch',unidentified:'method'};
 const result=evaluate(u,mi,state);
 near(result.value,r.ge_ppr_tC_2019,r.unit_id+' map carbon PPR');
 near(result.coverage*100,r.coverage_pct,r.unit_id+' map catch coverage');
 assert.match(result.status,/^provisional:/);
 assert.ok(u.models[mi].review_flags.length>0);
 assert.ok(Object.keys(u.models[mi].health).includes('GE'),r.unit_id+' GE diagnosis metadata');
 const agg=tctx.PPRTimeSeries.aggregate(series,{...state,units:[r.unit_id]});
 const point=agg.points.find(p=>p.year===2019);
 near(point.value,r.ge_ppr_tC_2019,r.unit_id+' trend carbon PPR');
 assert.match(point.status,/provisional:/);assert.ok(agg.review_flags.length>0);
 checked.push({unit_id:r.unit_id,map_ppr_tC:result.value,coverage_pct:result.coverage*100,trend_ppr_tC:point.value,status:result.status,diagnostic_options:Object.keys(u.models[mi].health)});
}
fs.writeFileSync(path.join(here,'generated_regions_verification.json'),JSON.stringify({checked},null,2));
console.log(`${checked.length} updated regions: generated map and trends match regional GE totals, carbon conversion, catch coverage, provisional status and diagnosis flags.`);
