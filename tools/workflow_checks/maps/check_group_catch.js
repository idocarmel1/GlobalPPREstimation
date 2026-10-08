/* Exercise generated group calculations and real dialog events. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.style={};this.classList={remove(){},add(){}};this.value='';}
  append(...items){for(const item of items){item.parentElement=this;this.children.push(item);}if(this.tag==='select'&&!this.value)this.value=this.children[0]?.value||'';}
  appendChild(item){this.append(item);return item;}
  replaceChildren(...items){this.children=[];this.value='';this.append(...items);}
  setAttribute(){} addEventListener(){} showModal(){this.open=true;} close(){this.open=false;}
  get options(){return this.children;}
}
for(const filename of process.argv.slice(2)){
  const html=fs.readFileSync(filename,'utf8'),body=new Element('body'),ctx={document:{body,createElement:tag=>new Element(tag)}};
  const start=html.indexOf('/* Shared annual denominator lookup.'),tail=html.indexOf('  return {create,filterRows,sortRows};',start),end=html.indexOf('});',tail)+3;
  vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
  vm.runInContext(fs.readFileSync(require('node:path').resolve(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),ctx);
  const model={id:'m',verified:true,model_catch_units:'t wet weight/km²/year',model_catch_carbon_factor:1/9,display_ppr_excluded_group_ids:['Bird'],group_data:{
    groups:[{id:'Fish',name:'Fish',model_catch:2},{id:'Bird',name:'Bird',model_catch:0},{id:'Missing',name:'Missing',model_catch:null}],
    methods:['new_GE'],scopes:{all:[[9],[90],[18]],inner:[[4.5],[45],[9]]},mappings:[[[0,.75],[1,.25]],[[1,1]],[[2,1]]]},
    scopes:{all:{methods:['new_GE'],status:{new_GE:'ok'},values:[[29.25],[90],[18]]},inner:{methods:['new_GE'],status:{new_GE:'ok'},values:[[14.625],[45],[9]]}}};
  const unit={name:'U',default_model:'m',models:[model],years:[2018,2019],taxa:['split','bird','missing'],catch:[[8,4],[4,2],[2,1]],landings:[[8,4],[4,2],[2,1]],discards:[[2,1],[1,.5],[0,0]],unidentified:{taxa:[]}};
  const state={year:2019,scope:'all',method:'new_GE',catch_basis:'landings',mode:'ppr'};
  const before=JSON.stringify(unit),groups=ctx.PPRGroups;
  assert.equal(groups.evaluate(unit,model,state).total_catch,4,'Default unchecked groups cannot contribute to total catch');
  assert.equal(groups.evaluate(unit,model,state).catch,4,'Default unchecked groups cannot contribute to covered catch');
  assert.equal(groups.evaluate(unit,model,state,['Fish']).total_catch,3,'Manual subset retains .75 of split taxon, without reallocating');
  assert.equal(groups.evaluate(unit,model,state,['Fish']).value,3);
  assert.equal(groups.evaluate(unit,model,state,['Fish']).total_discards,.75);
  assert.equal(groups.evaluate(unit,model,state,['Fish','Bird','Missing']).total_catch,7,'Explicit override still admits every original share');
  assert.equal(groups.evaluate(unit,model,state,[]).total_catch,0);
  const native=groups.rows(unit,model,{...state,catch_source:'model'});
  assert.deepEqual(Array.from(native,r=>r.ppr),[2,0,null],'Saved model catch uses group SPPR /9 and preserves missingness');
  const carbonModel=structuredClone(model);carbonModel.model_catch_units='t C/km²/year';carbonModel.model_catch_carbon_factor=1;
  assert.equal(groups.rows(unit,carbonModel,{...state,catch_source:'model'})[0].ppr,18,'Native carbon catch must not be divided by nine again');
  carbonModel.group_data.groups[0].model_catch_sppr={all:{new_GE:4.5}};
  assert.equal(groups.rows(unit,carbonModel,{...state,catch_source:'model'})[0].ppr,9,'Native carbon display uses the saved native coefficient instead of transformed regional SPPR');
  assert.equal(groups.rows(unit,carbonModel,{...state,catch_source:'model',scope:'inner'})[0].ppr,null,'Missing native scope cannot fall back to differently transformed regional coefficients');
  const unknownUnits=structuredClone(model);delete unknownUnits.model_catch_carbon_factor;
  assert.equal(groups.rows(unit,unknownUnits,{...state,catch_source:'model'})[0].ppr,null,'Unknown native catch units cannot become a carbon density');
  assert.equal(groups.rows(unit,model,{...state,catch_source:'model',scope:'inner'})[0].ppr,1);
  assert.equal(groups.rows(unit,model,{...state,catch_source:'annual',year:2018})[0].ppr,6,'Annual inspection uses selected year and original .75 allocation');
  assert.equal(groups.rows(unit,model,{...state,catch_source:'annual',year:2019})[1].ppr,30,'Rows still show values before checkbox selection');
  assert.equal(JSON.stringify(unit),before,'Inspection never changes saved input values or review evidence');
  const failed=structuredClone(model);failed.scopes.all.status.new_GE='FAIL';
  assert.equal(groups.rows(unit,failed,{...state,catch_source:'model'})[0].ppr,null,'Ordinary diagnostic failures remain unavailable');
  failed.scopes.all.status.new_GE='provisional: retained signed result';failed.group_data.scopes.all[0][0]=-9;
  assert.equal(groups.rows(unit,failed,{...state,catch_source:'model'})[0].ppr,-2,'Explicit provisional results retain signed contributions');
  const store={data:{models:{},selections:{},tables:{}},save(){},shareLinks(){},storageAvailable:true};let changed=0;
  const graphState=JSON.stringify(state),dialog=ctx.PPRGroupDialog.create({units:{U:unit},store,getContext:()=>state,onChange(){changed++;}});dialog.open('U');
  const nodes=()=>{const found=[];const visit=e=>{found.push(e);e.children.forEach(visit);};visit(body);return found;};
  const byId=id=>nodes().find(e=>e.id===id),row=name=>byId('groupTableBody').children.find(e=>e.dataset.groupId===name),ppr=name=>row(name).children.at(-1).textContent;
  assert.equal(byId('groupCatchSource').value,'annual');assert.equal(byId('groupCatchYear').value,'2019');
  assert.equal(ppr('Fish'),'3');
  byId('groupCatchYear').value='2018';byId('groupCatchYear').onchange();assert.equal(ppr('Fish'),'6');
  byId('groupCatchSource').value='model';byId('groupCatchSource').onchange();assert.equal(ppr('Fish'),'2');
  assert.equal(byId('groupCatchYear').disabled,true);assert.match(byId('groupContext').textContent,/t C\/km²\/year/);
  assert.equal(changed,0,'Inspection source/year controls do not notify or recalculate the graph');assert.equal(JSON.stringify(state),graphState);
  dialog.refresh();assert.equal(byId('groupCatchSource').value,'model','Inspection choice survives dialog refresh');
  assert.equal(store.data.tables['U::m'].catch_year,2018);assert.equal(store.data.tables['U::m'].catch_source,'model');
  byId('groupCatchSource').value='annual';byId('groupCatchSource').onchange();assert.equal(ppr('Fish'),'6');assert.equal(byId('groupCatchYear').disabled,false);
  const groupCheck=row('Fish').children[0].children[0];groupCheck.checked=false;groupCheck.onchange();assert.equal(changed,1,'Checkbox still updates graph selection');
}
console.log('Group catch inspection passed: saved density, annual weights/year, catch exclusion, missingness, persistence and graph isolation.');
