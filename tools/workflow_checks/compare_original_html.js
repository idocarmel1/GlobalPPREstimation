const fs=require('fs'),path=require('path'),assert=require('assert');
const original=process.argv[2]||path.resolve(__dirname,'../../original_research_archive/legacy/PPRAtlas');
const current=process.argv[3]||path.resolve(__dirname,'../../interactive_map');
const modules=path.resolve(__dirname,'../original_html_layout/calculation_modules');
const metric=require(path.join(modules,'network_metrics.js'));
const times=require(path.join(modules,'time_series_metrics.js'));
function data(file,variable){const text=fs.readFileSync(file,'utf8'),marker='const '+variable+'=',start=text.indexOf(marker)+marker.length;const end=text.indexOf('</script>',start);const raw=text.slice(start,end);return JSON.parse(raw.slice(0,raw.lastIndexOf(';')));}
// The map shares a script block with additional declarations: use the next declaration boundary.
function map(file){const text=fs.readFileSync(file,'utf8'),start=text.indexOf('const DB=')+9;let depth=0,string=false,escape=false,end=start;
for(;end<text.length;end++){const c=text[end];if(string){if(escape)escape=false;else if(c==='\\')escape=true;else if(c==='"')string=false;}else if(c==='"')string=true;else if(c==='{'||c==='[')depth++;else if(c==='}'||c===']'){depth--;if(!depth){end++;break;}}}return JSON.parse(text.slice(start,end));}
const old=map(path.join(original,'index.html')).network,next=map(path.join(current,'index.html')).network;
let checks=0;
function same(a,b,label){if(a==null||b==null)assert.equal(a,b,label);else assert(Math.abs(a-b)<=1e-9+1e-12*Math.max(Math.abs(a),Math.abs(b)),label+': '+a+' != '+b);checks++;}
for(const [id,u] of Object.entries(old.units)){
 const v=next.units[id];assert(v,id);const oldm=u.models[u.default_model],newm=v.models[v.default_model];assert.equal(oldm?.id,newm?.id,id);
 for(const scope of ['all','inner','PP'])for(const method of oldm?.scopes[scope]?.methods||[])for(const year of [1950,1998,2019])for(const basis of ['landings','catch','discards'])for(const unidentified of ['method','zero','simple']){
  const state={unit_id:id,mode:'ppr',scope,method,year,catch_basis:basis,unidentified};
  const a=metric.evaluate(u,u.default_model,{...state,simple_unit:old.simple_units[id]}),b=metric.evaluate(v,v.default_model,{...state,simple_unit:next.simple_units[id]});same(a.value,b.value,[id,scope,method,year,basis,unidentified].join('/'));
 }
 if(oldm?.group_data?.groups.length){const selected=oldm.group_data.groups.slice(0,8).map(g=>g.id);const state={unit_id:id,mode:'ppr',scope:'all',method:'new_GE',year:2019,catch_basis:'landings',group_selections:{[id+'::'+oldm.id]:selected}};same(metric.evaluate(u,u.default_model,state).value,metric.evaluate(v,v.default_model,state).value,id+' group subset');}
}
const a=data(path.join(original,'trends.html'),'SERIES_DB'),b=data(path.join(current,'trends.html'),'SERIES_DB');
for(const method of a.ppr_methods)for(const scope of method.scopes)for(const mode of ['ppr','ratio']){
 const state={units:Object.keys(old.units),method:method.id,scope,mode,npp:'ens_median_tC_yr',npp_scope:'selected',npp_fill:'observed',catch_basis:'landings',years:[1998,2005,2019]};
 const x=times.aggregate(a,state),y=times.aggregate(b,state);for(let i=0;i<x.points.length;i++)same(x.points[i].value,y.points[i].value,'trend '+method.id+'/'+scope+'/'+mode+'/'+i);
}
console.log('Original JavaScript numerical parity passed: '+checks+' map, subset and trend values');
