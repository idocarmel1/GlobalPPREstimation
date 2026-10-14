/* Exercise generated assumption panels, effective group values and downloaded provenance. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.style={};this.classList={remove(){},add(){}};this.value='';this.events={};}
  append(...items){for(const item of items){item.parentElement=this;this.children.push(item);}if(this.tag==='select'&&!this.value)this.value=this.children[0]?.value||'';}
  appendChild(item){this.append(item);return item;}
  replaceChildren(...items){this.children=[];this.value='';this.append(...items);}
  setAttribute(key,value){this[key]=value;} addEventListener(key,callback){this.events[key]=callback;} showModal(){} close(){} click(){this.events.click?.();}
  get options(){return this.children;}
  get textContent(){return (this.text||'')+this.children.map(child=>child.textContent||'').join('');}
  set textContent(value){this.text=String(value);this.children=[];}
}
for(const filename of process.argv.slice(2)){
  const html=fs.readFileSync(filename,'utf8');
  assert.ok(html.includes('/* Saved EE-floor calculation assumptions.'),'Generated page must include the calculation assumption adapter');
  const body=new Element('body'),ctx={document:{body,createElement:tag=>new Element(tag),createTextNode:text=>{const e=new Element('#text');e.textContent=text;return e;}}};
  vm.createContext(ctx);
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match=>match[1]);
  const floorStart=html.indexOf('/* Saved EE-floor calculation assumptions.'),floorEnd=html.indexOf('\n});',floorStart)+5;
  vm.runInContext(html.slice(floorStart,floorEnd),ctx);
  vm.runInContext(scripts.find(script=>script.includes('const PPRResearcherReview=')),ctx);
  const reviewView=vm.runInContext('PPRResearcherReview',ctx);
  const review={status:'Validated by researcher',researcher_name:'R',review_date:'2026-09-01',report_path:'reports/signed.docx',note:'Original exclusions',
    sections:[{heading:'GE and TE diagnostics',rows:[{label:'GE',paragraphs:[[{text:'Original FAIL diagnostic prose\nunchanged'}]]}]}]};
  const provenance={use_ee_floor:true,ee_floor:.1,affected_group_count:1,external_mortality_export_total:1.5,calculation_engine_upgrade:'ee_floor_v1',calculation_engine_sha256:'e'.repeat(64),effective_loader_flags:{constructor:{use_ee_floor:true,ee_floor:.1}}};
  const model={id:'candidate',workbook:'regions/LME/LME_001/papers/P/models/candidate/results/regional_snapshot.xlsx',source:'regions/LME/LME_001/papers/P/models/candidate/sppr_source.xlsx',calculation_provenance:provenance,researcher_review:review,health:{GE:{status:'WARN',balanced:false}},review_flags:['GE: strict SPPR balance false']};
  const before=JSON.stringify(model),panel=new Element('div');reviewView.append(panel,model);
  assert.match(panel.textContent,/EE floor ON \(0\.1\)/);
  assert.match(panel.textContent,/hypothetical.*nonfishery/i);
  assert.match(panel.textContent,/does not approve/i);
  assert.match(panel.textContent,/Current calculation diagnostics: GE: WARN/);
  assert.match(panel.textContent,/strict SPPR balance false/);
  assert.match(panel.textContent,/Original FAIL diagnostic prose\nunchanged/);
  assert.match(panel.textContent,/2026-09-01/);
  assert.equal(JSON.stringify(model),before,'Presentation never changes the signed review or provenance');
  const unsigned={...model};delete unsigned.researcher_review;
  const unsignedPanel=new Element('div');reviewView.append(unsignedPanel,unsigned);
  assert.match(unsignedPanel.textContent,/require separate researcher review/);
  assert.doesNotMatch(unsignedPanel.textContent,/The signed researcher review retains/,'An unreviewed model must not gain a claimed signature');
  const off=structuredClone(model);off.calculation_provenance.use_ee_floor=false;off.calculation_provenance.affected_group_count=0;
  const offPanel=new Element('div');reviewView.append(offPanel,off);assert.match(offPanel.textContent,/EE floor OFF/);
  const noAffected=structuredClone(model);noAffected.calculation_provenance.affected_group_count=0;noAffected.calculation_provenance.external_mortality_export_total=0;
  const noAffectedPanel=new Element('div');reviewView.append(noAffectedPanel,noAffected);assert.match(noAffectedPanel.textContent,/EE floor ON \(0\.1\)/);
  const historical={id:'historical'},historicalPanel=new Element('div');reviewView.append(historicalPanel,historical);
  assert.doesNotMatch(historicalPanel.textContent,/EE floor ON|EE floor OFF/,'Unknown historical floor must not inherit a default');
  const group={ee:.1,source_ee:.02,source_m0:null,ee_before_floor:.025,m0_before_floor:19.5,m0_effective:18,external_mortality_export:1.5};
  const tooltip=ctx.PPREeFloor.groupTooltip(group);assert.match(tooltip,/effective EE: 0\.1/i);assert.match(tooltip,/source EE: 0\.02/i);assert.match(tooltip,/source M0: unavailable/i);
  const pickerStart=html.indexOf('/* Shared annual denominator lookup.'),pickerTail=html.indexOf('  return {create,filterRows,sortRows};',pickerStart),pickerEnd=html.indexOf('});',pickerTail)+3;
  vm.runInContext(html.slice(pickerStart,pickerEnd),ctx);
  const pickerModel={...model,verified:true,group_data:{groups:[{...group,id:'fish group',name:'fish group',ge:.2,te:.02}],methods:['new_GE'],scopes:{all:[[9]],inner:[[4.5]],PP:[[1]]},mappings:[[[0,1]]]},
    scopes:{all:{methods:['new_GE'],status:{new_GE:'provisional: WARN'},values:[[9]]}}};
  const pickerUnit={default_model:'candidate',models:[pickerModel],years:[2019],taxa:['fish'],catch:[[2]],landings:[[2]],discards:[[0]],unidentified:{taxa:[]}};
  const store={data:{models:{},selections:{},tables:{}},save(){},shareLinks(){},storageAvailable:true};
  const dialog=ctx.PPRGroupDialog.create({units:{U:pickerUnit},store,getContext:()=>({year:2019,scope:'all',method:'new_GE',catch_basis:'catch',mode:'ppr'}),onChange(){}});dialog.open('U');
  const nodes=[];const visit=e=>{nodes.push(e);e.children.forEach(visit);};visit(body);
  const displayed=nodes.find(e=>e.id==='groupTableBody').children[0].children[3];
  assert.equal(displayed.textContent,'0.1','Group EE column shows the saved effective value');
  assert.match(displayed.title,/Source EE: 0\.02/,'The same displayed cell carries the original source value');
  if(filename.endsWith('trends.html')){
    const db={units:{U:{default_model:'selected',models:[{id:'selected',calculation_provenance:{use_ee_floor:false,ee_floor:.1}},model]}}};
    const result={model_ids:{U:'candidate'},series:[{model_ids:{U:'candidate'},points:[{year:2019,value:3}]}],baseline_model_ids:{U:'selected'}};
    const original=JSON.stringify(result),exported=ctx.PPREeFloor.exportResult(db,result,{mode:'ppr',units:['U']});
    assert.equal(exported.calculation_provenance.U.candidate.use_ee_floor,true);
    assert.equal(exported.calculation_provenance.U.selected.use_ee_floor,false,'Baseline retains its own calculation assumption');
    assert.equal(JSON.stringify(result),original,'Download enrichment leaves live result unchanged');
    const csv=ctx.PPREeFloor.toCSV('year,value\n2019,3\n',exported.calculation_provenance);
    assert.match(csv,/year,value,calculation_provenance/);assert.match(csv,/""use_ee_floor"":true/);
    assert.deepEqual(Object.keys(ctx.PPREeFloor.exportResult(db,result,{mode:'npp',units:['U']}).calculation_provenance),[]);
    assert.match(html,/comparisonToJSON\(PPREeFloor\.exportResult\(db,result,state\),state\)/);
  }else{
    assert.match(html,/calculation_provenance:metricState\.mode==='npp'\?null:model\?\.calculation_provenance/);
    let downloaded;
    Object.assign(ctx,{DB:{year:2019},metricState:{mode:'ppr',method:'new_GE',catch_basis:'catch',scope:'all',group_selections:{}},
      showSensitivity:()=>false,assessedSensitivity:()=>false,PPRMetrics:{finite:value=>typeof value==='number'&&Number.isFinite(value)},
      Blob:class{constructor(parts){downloaded=parts.join('');}},URL:{createObjectURL:()=>'',revokeObjectURL(){}},setTimeout(){}});
    const exportStart=html.indexOf('function appendResultDownload('),exportEnd=html.indexOf('function appendTreatment(',exportStart);
    vm.runInContext(html.slice(exportStart,exportEnd),ctx);
    const downloadPanel=new Element('div');ctx.appendResultDownload(downloadPanel,{unit_id:'U'},model,{value:3,status:'provisional: WARN'},pickerUnit);
    downloadPanel.children[0].click();assert.match(downloaded,/calculation_provenance/);assert.match(downloaded,/""use_ee_floor"":true/);
  }
}
console.log('EE-floor views passed: source/effective EE, ON/OFF/no affected groups, exact signed review, candidate and baseline export settings.');
