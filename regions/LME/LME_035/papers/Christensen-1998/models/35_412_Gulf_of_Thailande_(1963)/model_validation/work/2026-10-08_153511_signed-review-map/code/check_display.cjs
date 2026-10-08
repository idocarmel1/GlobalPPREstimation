const fs=require('fs'),assert=require('assert/strict'),vm=require('vm'),path=require('path');
const root=process.cwd(),qa=path.join(__dirname,'../qa');
function payload(page,name){const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;const ends=[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0);return JSON.parse(page.slice(start,Math.min(...ends)));}
class Element{
 constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.style={};this.classes=new Set();this.classList={add:x=>this.classes.add(x),remove:(...xs)=>xs.forEach(x=>this.classes.delete(x))};}
 appendChild(x){this.children.push(x);return x;} setAttribute(k,v){this[k]=v;}
}
const document={createElement:t=>new Element(t),createTextNode:t=>new Element('#text',t)};
const results=[];
for(const [filename,variable] of [['index.html','DB'],['trends.html','SERIES_DB']]){
 const page=fs.readFileSync(path.join(root,'interactive_map',filename),'utf8'),db=payload(page,variable),units=variable==='DB'?db.network.units:db.units;
 const model=units.LME_035.models.find(m=>m.id==='35_412_Gulf_of_Thailande_(1963)');
 assert.equal(model.researcher_review.status,'Validated by researcher');assert.deepEqual(model.display_ppr_excluded_group_ids,['M. mammals']);
 const start=page.indexOf('const PPRResearcherReview='),end=page.indexOf('})();',start)+5;
 const context={document};vm.runInNewContext(page.slice(start,end)+';globalThis.review=PPRResearcherReview;',context);
 const parent=new Element('div');assert.equal(context.review.append(parent,model),true);
 const wrap=parent.children[0],headings=wrap.children.filter(c=>c.tag==='h4').map(c=>c.textContent);
 assert.deepEqual(headings,['Model extraction notes','GE diagnostics','TE diagnostics','SPPR Calculation Notes','Geographic fit','Taxon mapping confidence']);
 const name=new Element('span');context.review.decorateName(name,model);assert.equal(name.style.color,'#187344');
 const table=wrap.children.find(c=>c.tag==='table');assert.deepEqual(table.children.map(r=>r.children.map(c=>c.textContent)),model.researcher_review.sections.at(-1).table);
 const references=model.researcher_review.sections.at(-1).reference;assert(references[0].includes('2019 landings'));
 const gstart=page.indexOf('/* Retain the original catch allocations when selecting model groups. */'),gend=page.indexOf('/* Compact preferences shared by the two standalone pages.',gstart);
 const groupContext={module:{exports:{}}};vm.runInNewContext(page.slice(gstart,gend),groupContext);
 const api=groupContext.module.exports,all=model.group_data.groups.map(g=>g.id);
 for(const requested of [undefined,all,['M. mammals']])assert(!api.selection(model,requested).ids.includes('M. mammals'));
 assert(api.selection(model).requested_ids.includes('M. mammals'));
 assert(page.includes('check.disabled=(current().model?.display_ppr_excluded_group_ids||[]).includes(row.id)'));
 results.push({page:filename,green_model_name:true,six_flat_headings:true,confidence_table_exact:true,fixed_2019_reference:true,exclusion_cannot_be_restored:true,excluded_control_disabled:true});
}
fs.writeFileSync(path.join(qa,'display_behavior.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
