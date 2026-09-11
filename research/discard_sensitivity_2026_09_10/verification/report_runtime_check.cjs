// Data-backed renderer smoke check with a minimal DOM stub. This is NOT browser/visual QA.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'report.html'),'utf8');
const raw=html.match(/<script id="study-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const source=html.match(/<script>\r?\n([\s\S]*?)<\/script>/)[1],nodes={};
function node(id){
  if(nodes[id])return nodes[id];
  return nodes[id]={textContent:id==='study-data'?raw:'',innerHTML:'',value:'',checked:false,
    get selectedOptions(){return [{textContent:this.value||'Result'}];},
    addEventListener(){},querySelectorAll(){return []}};
}
const context={console,document:{getElementById:node,querySelectorAll(){return [];}},setTimeout};
vm.createContext(context);new vm.Script(source).runInContext(context);
const checks=vm.runInContext(`(()=>{
 let views=0;
 for(const m of D.models)for(const method of D.methods)for(const scope of ['all','PP'])for(const route of ['SM','SR'])for(const metric of ['ppr','native_percent','standard_excess']){
   Object.assign(state,{model:m.model_id,method,scope,route,metric,fraction:.1,boundary:'H'});syncChoices();render();views++;
   if(/NaN|Infinity/.test($('curve').innerHTML))throw new Error('Nonfinite chart');
   const r=record();if(metric==='native_percent'&&r?.native_denominator_compatible===false&&value(r)!==null)throw new Error('Incompatible native ratio');
   if(!r?.valid&&value(r)!==null)throw new Error('Invalid result charted');
   if(!evidenceFor(m.model_id))throw new Error('Source evidence missing');
 }
 return {views,models:D.models.length,records:D.records.length,method_names:D.methods.every(m=>!!names[m])};
})()`,context);
const reportPath=path.join(__dirname,'report_data.json'),report=JSON.parse(fs.readFileSync(reportPath,'utf8'));
Object.assign(report,{node_syntax_verified:true,node_dom_stub_smoke:checks,browser_verified:false,browser_verification_reason:'direct_file_navigation_blocked'});
fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(__dirname,'report_script.js'),source);
console.log(JSON.stringify(report));
