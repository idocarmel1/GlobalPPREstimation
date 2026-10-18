// Focused existing presentation/calculation checks against the generated pages.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const checks=[
  ['check_review_presentation.js'],
  ['check_map_validation_filter.js','interactive_map/index.html'],
  ['check_trend_extras.js'],
  ['check_researcher_review.js','interactive_map/index.html','interactive_map/trends.html'],
  ['check_ee_floor_views.js','interactive_map/index.html','interactive_map/trends.html'],
  ['check_available_results.js'],
];
const results=[];
for(const [name,...args] of checks){
  const input=name==='check_available_results.js'?JSON.stringify(Object.fromEntries(['index.html','trends.html'].map(f=>[f,fs.readFileSync('interactive_map/'+f,'utf8')]))):undefined;
  const result=cp.spawnSync(process.execPath,['tools/workflow_checks/maps/'+name,...args],{input,encoding:'utf8',maxBuffer:2**24});
  results.push({name,status:result.status,stdout:result.stdout,stderr:result.stderr,error:result.error?.message});
  console.log(name+': '+(result.status===0?'PASS':'FAIL'));
}
fs.writeFileSync(path.join(__dirname,'../qa/existing_view_checks.json'),JSON.stringify(results,null,2)+'\n');
if(results.some(x=>x.status!==0))process.exitCode=1;
