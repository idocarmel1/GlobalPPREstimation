// Test the exact pure calculation and export code embedded in the final page.
// This is offline application-code verification, not browser automation.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'../../..'),out=path.join(__dirname,'verification/final_trends_outputs');
fs.mkdirSync(out,{recursive:true});
const html=fs.readFileSync(path.join(root,'interactive_map/trends.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const data=scripts.find(s=>s.startsWith('const SERIES_DB='));
const db=JSON.parse(data.slice('const SERIES_DB='.length,data.lastIndexOf(';')));
const pure=scripts.find(s=>s.startsWith('/* Shared annual denominator'));
assert(pure && pure.includes('comparisonToJSON'));
const context=vm.createContext({});vm.runInContext(pure,context,{timeout:10000});
const synthesis=JSON.parse(fs.readFileSync(path.join(__dirname,'work/final_status_synthesis/final_23_region_status.json'),'utf8'));
const units=synthesis.regions.map(r=>r.unit_id),models=Object.fromEntries(synthesis.regions.map(r=>[r.unit_id,r.model_id]));
const base={units,models,set:'custom',scope:'all',mode:'ppr',npp_scope:'selected',catch_basis:'landings',uncertainty:'1',npp:'ens_median_tC_yr',npp_fill:'observed',unidentified:'method',group_selections:{},years:db.years};
const methods=['simple trophic chain','new_TE_EEfix','new_GE','new_WithEgestion'];
const scenarios=[
  {name:'four_methods_landings',state:{...base,methods},observed:[4649500000,13952000000,3293100000,952070000],included:19},
  {name:'four_methods_catch',state:{...base,methods,catch_basis:'catch'},observed:[4890300000,18247000000,3676200000,1024200000],included:19},
  {name:'GE_inner_NPP_ratio',state:{...base,methods:['new_GE'],scope:'inner',mode:'ratio'},observed:[32.266],included:22},
];
const receipt={recorded_utc:new Date().toISOString(),status:'PASS',scope:'Exact generated-page pure functions compared with observed CUA DOM; CSV/JSON serializers verified offline. The IAB download event timed out, so filesystem delivery through its download manager is not certified.',page_sha256:crypto.createHash('sha256').update(html).digest('hex'),project_sha256:html.match(/name="ppr-project-sha256" content="([a-f0-9]+)"/)[1],checks:[]};
for(const scenario of scenarios){
  const result=context.PPRTimeSeries.compare(db,scenario.state);
  assert.equal(result.included.length,scenario.included);
  const checks=result.series.map((s,i)=>{const value=s.points.find(p=>p.year===2019).value,shown=scenario.observed[i],tol=10**(Math.floor(Math.log10(Math.abs(value)))-4)/2;assert(Math.abs(value-shown)<=tol,`${scenario.name}/${s.method}: ${value} != ${shown}`);return {method:s.method,value,observed:shown,rounding_tolerance:tol};});
  const json=context.PPRTimeSeries.comparisonToJSON(result,scenario.state);
  const csv=context.PPRTimeSeries.comparisonToCSV(result,scenario.state);
  assert.deepEqual(JSON.parse(json).state,scenario.state);
  assert.equal(JSON.parse(json).result.series.length,scenario.observed.length);
  const paths={};for(const [format,content] of [['json',json],['csv',csv]]){const name=scenario.name+'.'+format+'.gz';fs.writeFileSync(path.join(out,name),zlib.gzipSync(content));paths[format]={path:path.relative(root,path.join(out,name)).replaceAll('\\','/'),sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,name))).digest('hex')};}
  receipt.checks.push({scenario:scenario.name,included:result.included,excluded:result.excluded,values:checks,exports:paths});
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({status:'PASS',scenarios:scenarios.length,values:receipt.checks.reduce((n,c)=>n+c.values.length,0),exports:6,receipt:path.join(out,'verification.json')}));
