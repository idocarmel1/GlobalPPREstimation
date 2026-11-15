const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const work=path.dirname(__dirname);
let root=work;while(!fs.existsSync(path.join(root,'Project.xlsx')))root=path.dirname(root);
const page=fs.readFileSync(path.join(root,'interactive_map/trends.html'),'utf8');
const scripts=[...page.matchAll(/<script(?:[^>]*)>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const payload=scripts.find(s=>s.startsWith('const SERIES_DB='));
const db=JSON.parse(payload.slice('const SERIES_DB='.length).trim().replace(/;$/,''));
const cx=vm.createContext({console,db});
vm.runInContext(scripts.find(s=>s.includes('const PPRRegionTable=')),cx);
const before=JSON.parse(fs.readFileSync(path.join(work,'inputs/table_2019_before.json'),'utf8'));
const inventory=JSON.parse(fs.readFileSync(path.join(work,'inputs/validated_inventory.json'),'utf8'));
cx.state={set:'validated',review_filter:'validated',units:[],methods:['SPPR_1995_TE0.1','new_GE','new_TE_EEfix'],models:{},scope:'all',mode:'ratio',npp_scope:'global',npp:'ens_median_tC_yr',npp_fill:'observed',unidentified:'method',group_selections:{},uncertainty:'0',baseline:null};
const report={passed:true,scope:'Production time-series and annual table functions, researcher-validated defaults, all sources, 2019, global atlas NPP',tables:{}};
report.source_sha256=Object.fromEntries(['Project.xlsx','interactive_map/trends.html'].map(p=>[p,require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')]));
report.annual_checks=[];
for(const basis of ['landings','catch']){
  cx.state.catch_basis=basis;
  const table=vm.runInContext('PPRTrendExtras.table(db,state,2019,PPRTimeSeries.compare,PPRTimeSeries.aggregate)',cx);
  assert.deepEqual(Array.from(table.rows,r=>r.id).sort(),inventory.pairs.map(r=>r.unit_id).sort());
  for(const row of table.rows){
    const old=before[basis].rows.find(r=>r.id===row.id);
    assert.ok(Number.isFinite(row.values[0].value),`${row.id} fixed-TE SPPR_1995 still unavailable`);
    for(const index of [1,2])assert.ok(Math.abs(row.values[index].value-old.values[index].value)<=1e-12*Math.max(1,Math.abs(old.values[index].value)),`${row.id} retained GE/TE changed`);
  }
  report.tables[basis]=table;
  for(const item of inventory.pairs){
    cx.annualState={...cx.state,set:'custom',units:[item.unit_id],mode:'ppr',years:db.years};
    const series=vm.runInContext('PPRTimeSeries.compare(db,annualState).series',cx);
    const fixed=series.find(s=>s.method==='SPPR_1995_TE0.1');
    const controls=series.filter(s=>['new_GE','new_TE_EEfix'].includes(s.method));
    let checked=0;
    for(const point of fixed.points){
      if(controls.some(s=>s.points.some(p=>p.year===point.year&&Number.isFinite(p.value)))){
        assert.ok(Number.isFinite(point.value),`${item.unit_id}/${basis}/${point.year} fixed-TE SPPR missing despite retained GE/TE`);
        checked++;
      }
    }
    report.annual_checks.push({unit_id:item.unit_id,catch_basis:basis,years_with_control_results:checked,passed:true});
  }
}
fs.writeFileSync(path.join(work,'qa/time_series_table_verification.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:true,validated_models:inventory.pairs.length,screenshot_catch_basis:'landings',four_models:report.tables.landings.rows.filter(r=>['LME_003','LME_038','EEZ_941','LME_022'].includes(r.id)).map(r=>({unit:r.id,SPPR_1995_TE01_percent:r.values[0].value,GE:r.values[1].value,TE:r.values[2].value}))},null,2));
