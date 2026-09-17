/* Exercise embedded report logic and downloadable bytes; actual browser QA is separate. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'report.html'),'utf8');
const payload=html.match(/<script id="payload"[^>]*>(.*?)<\/script>/s)[1];
const script=html.match(/<script>(.*?)<\/script>/s)[1],nodes=new Map();
function element(id){if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',innerHTML:'',classList:{add(){},remove(){}},viewBox:{baseVal:{width:id==='modelChart'?660:550,height:315}},addEventListener(){},appendChild(){},click(){},querySelector(){return element(id+'-tbody')}});return nodes.get(id)}
const document={getElementById:element,createElement:()=>({click(){}}),documentElement:{dataset:{}}};
element('payload').textContent=payload;
for(const [id,value] of Object.entries({scope:'all',route:'SM',basis:'H',fraction:'20',range:'dense',metric:'change',support:'fixed'}))element(id).value=value;
const context=vm.createContext({document,console,Blob,Response,DecompressionStream,Uint8Array,atob,setTimeout,URL,window:{}});
vm.runInContext(script,context);
(async()=>{
  for(let i=0;i<200&&!document.documentElement.dataset.reportReady;i++)await new Promise(resolve=>setTimeout(resolve,50));
  assert.equal(document.documentElement.dataset.reportReady,'true',element('loading').textContent);
  const D=context.window.reportData,R=context.window.reportRows;
  assert.equal(R.length,62784);assert.equal(D.models.length,24);assert.equal(D.fractions.length,27);
  const cases=[];
  function check(label,values){
    for(const [k,v] of Object.entries(values))element(k).value=String(v);
    vm.runInContext('render()',context);const s=context.window.currentReportSelection,r=s.record;
    assert(r);assert.equal(element('fvalue').textContent,Math.round(r.fraction*100)+'%');
    const value=s.basis==='H'?r.ppr_fixed_H_tC:r.ppr_retained_L_tC;
    const expected=value==null?'Unavailable':Number(value).toLocaleString('en-US',{maximumFractionDigits:5});
    assert.equal(element('pprValue').textContent,expected);
    element('downloadJSON').onclick();const downloaded=JSON.parse(context.window.lastDownload.text),jsonCharacters=context.window.lastDownload.text.length;
    const expectedRows=R.filter(x=>x.model_id===s.model&&x.method===s.method&&x.scope===s.scope);
    assert.equal(downloaded.records.length,109);assert.equal(expectedRows.length,109);
    for(const x of downloaded.records){const source=expectedRows.find(y=>y.route===x.route&&y.fraction===x.fraction);assert(source);assert.deepStrictEqual(JSON.parse(JSON.stringify(x.coefficients)),source.vector_id==null?null:JSON.parse(JSON.stringify(D.vectors[source.vector_id])));assert.equal(x.ppr_fixed_H_tC,source.ppr_fixed_H_tC);assert.equal(x.valid,source.valid)}
    element('downloadCSV').onclick();assert.equal(context.window.lastDownload.text.trimEnd().split('\n').length,110);
    cases.push({label,model:s.model,method:s.method,scope:s.scope,route:s.route,basis:s.basis,fraction:s.f,status:r.status,displayed_PPR:expected,displayed_coefficient_change:element('changeValue').textContent,download_records:downloaded.records.length,download_csv_characters:context.window.lastDownload.text.length,download_json_characters:jsonCharacters});
  }
  check('default 20 percent',{});
  check('one percent retained footprint',{fraction:1,basis:'L'});
  check('SC invariance',{route:'SC',fraction:20,basis:'H'});
  check('unavailable source scope',{method:'SPPR_1986',scope:'PP'});
  check('zero catch endpoint undefined',{method:'SPPR_1986',scope:'all',route:'SM',fraction:26,range:'full'});
  check('standard retained endpoint',{method:'standard_fixed_baseline_TL',basis:'L'});
  check('unsupported added return',{method:'new_GE',route:'SR',fraction:10,basis:'H'});
  check('documented original return',{model:'13_2_Northern_Humboldt_Current_(1995-1998)',route:'SR'});
  check('zero-harvest reference',{model:'52_1_Sea_of_Okhotsk_NE_(1980)',route:'SM',fraction:20});
  element('downloadAll').onclick();assert.deepStrictEqual(JSON.parse(context.window.lastDownload.text),JSON.parse(fs.readFileSync(path.join(root,'results/report_data.v2.json'),'utf8')));
  element('downloadScreen').onclick();assert.equal(context.window.lastDownload.text.trimEnd().split('\n').length,253);
  element('downloadAggregate').onclick();assert.equal(context.window.lastDownload.text.trimEnd().split('\n').length,D.aggregates.length+1);
  fs.writeFileSync(path.join(root,'verification/report_runtime_checks.json'),JSON.stringify({passed:true,report_sha256:crypto.createHash('sha256').update(html).digest('hex'),scope:'Node DOM stub exercises embedded JavaScript and download bytes; actual browser verification is separately recorded',cases,complete_embedded_json_matches_verified_output:true,screening_rows:252,aggregate_rows:D.aggregates.length},null,2));
  console.log('Report runtime/download checks passed:',cases.length,'control scenarios');
})().catch(e=>{console.error(e);process.exitCode=1});
