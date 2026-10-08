/* Exercise actual checkbox/bulk actions against a signed default. */
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
  assert(start>=0&&tail>start,'Shared group dialog is available');
  vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
  vm.runInContext(fs.readFileSync(require('node:path').resolve(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),ctx);
  const model={id:'m',verified:true,display_ppr_excluded_group_ids:['Bird'],group_data:{groups:[{id:'Fish',name:'Fish'},{id:'Bird',name:'Bird'}],methods:['new_GE'],scopes:{all:[[9],[90]]},mappings:[[[0,1]],[[1,1]]]},scopes:{all:{methods:['new_GE'],status:{new_GE:'ok'},values:[[9],[90]]}}};
  const unit={name:'U',default_model:'m',models:[model],years:[2019],taxa:['fish','bird'],catch:[[9],[9]],landings:[[9],[9]]};
  const store={data:{models:{},selections:{},tables:{}},save(){},shareLinks(){},storageAvailable:true};
  ctx.PPRGroupDialog.create({units:{U:unit},store,getContext:()=>({year:2019,scope:'all',method:'new_GE',catch_basis:'landings'}),onChange(){}}).open('U');
  const nodes=()=>{const found=[];const visit=e=>{found.push(e);e.children.forEach(visit);};visit(body);return found;};
  const byId=id=>nodes().find(e=>e.id===id),row=name=>byId('groupTableBody').children.find(e=>e.dataset.groupId===name),check=name=>row(name).children[0].children[0];
  assert.equal(check('Bird').checked,false,'Signed removal sets initial unchecked state');
  assert(!check('Bird').disabled,'Researcher-excluded checkbox stays editable');
  assert.match(row('Bird').children[1].textContent,/Excluded from displayed PPR by researcher/,'Signed annotation stays visible');
  byId('groupSelectAll').onclick();
  assert.equal(check('Bird').checked,true,'Select all can restore a signed excluded group');
  assert.deepEqual(Array.from(store.data.selections['U::m']),['Fish','Bird'],'All override is persisted rather than reverting to signed default');
  check('Fish').checked=false;check('Fish').onchange();
  assert.deepEqual(Array.from(store.data.selections['U::m']),['Bird'],'Checkbox can retain only the researcher-excluded group');
  byId('groupClearAll').onclick();assert.equal(check('Bird').checked,false);assert.equal(store.data.selections['U::m'].length,0);
  byId('groupSearch').value='Bird';byId('groupSearch').oninput();byId('groupSelectMatching').onclick();
  assert.deepEqual(Array.from(store.data.selections['U::m']),['Bird'],'Matching selection honors signed-excluded groups');
  assert.deepEqual(model.display_ppr_excluded_group_ids,['Bird'],'All UI actions preserve the signed decision');
}
console.log('Group override UI passed: editable checkbox, All/None/Matching, persistent selection, retained researcher annotation.');
