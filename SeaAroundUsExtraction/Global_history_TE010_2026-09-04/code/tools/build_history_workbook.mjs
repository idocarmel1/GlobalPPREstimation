import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';
import {addHistorySheets} from './history_workbook.mjs';
import {coerceCsvValue} from './eez_workbook.mjs';

const [source,historyDir,outputDir,previewDir]=process.argv.slice(2);
if(!source||!historyDir||!outputDir||!previewDir)throw new Error('Expected source workbook, history directory, output directory, preview directory');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const sourceHash=hash(await fs.readFile(source));
async function readCsv(name) {
  const text=await fs.readFile(path.join(historyDir,'tables',name),'utf8');
  const temp=await Workbook.fromCSV(text.replace(/^\uFEFF/,''),{sheetName:'Data'});
  const [headers,...rows]=temp.worksheets.getItem('Data').getUsedRange().values;
  return rows.map(r=>Object.fromEntries(headers.map((h,i)=>[h,coerceCsvValue(r[i])])));
}
const annual=JSON.parse(await fs.readFile(path.join(historyDir,'tables/annual_regions.json'),'utf8'));
let selected=await readCsv('selected_regions.csv');
const inventory=new Map(annual.map(r=>[r.unit_id,r]));
selected=selected.map(r=>({...r,region_name:inventory.get(r.unit_id)?.region_name??r.region_name,
  region_type:inventory.get(r.unit_id)?.region_type??r.region_type}));
const scenarios=await readCsv('selection_scenarios.csv');
const metrics=JSON.parse(await fs.readFile(path.join(historyDir,'tables/selection_metrics.json'),'utf8'));
const metricSummary=Object.fromEntries(Object.entries(metrics).filter(([key])=>
  !['scenarios','scenario_details','validation','created_at_utc'].includes(key)));
console.log(`Loading original summary; annual rows=${annual.length}, selected=${selected.length}`);
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const sheetSnapshot=await workbook.inspect({kind:'sheet',include:'id,name',maxChars:10000});
const originalNames=sheetSnapshot.ndjson.split('\n').filter(Boolean).map(x=>JSON.parse(x)).filter(x=>x.kind==='sheet').map(x=>x.name);
const originalSnapshots=new Map(originalNames.map(name=>{
  const range=workbook.worksheets.getItem(name).getUsedRange();
  return [name,hash(JSON.stringify({values:range.values,formulas:range.formulas}))];
}));
console.log('Adding live historical sheets');
const result=await addHistorySheets(workbook,{annual,selected,metrics:metricSummary,scenarios,progress:message=>console.log(message)});
const {summary,years}=result;
const selectedIds=new Set(selected.map(x=>x.unit_id));
const compare=(actual,expected,label)=>{
  if(typeof expected==='number')assert.ok(typeof actual==='number'&&Math.abs(actual-expected)<=Math.max(1e-7,Math.abs(expected)*1e-10),`${label}: ${actual} != ${expected}`);
  else assert.equal(actual,expected,label);
};
const checkYears=[years[0],years[Math.floor(years.length/2)],years.at(-1)];
const verification=[];
for(const year of checkYears) {
  summary.getRange('B3').values=[[year]];
  const rows=annual.filter(r=>r.year===year&&selectedIds.has(r.unit_id));
  const available=rows.filter(r=>r.source_data_status==='available');
  const expected=available.sort((a,b)=>b.ppr_species-a.ppr_species||a.unit_id.localeCompare(b.unit_id));
  const total=available.reduce((s,r)=>s+r.ppr_species,0);
  const catchTotal=available.reduce((s,r)=>s+r.total_catch_tonnes,0);
  compare(summary.getRange('B5').values[0][0],total,`${year} total PPR`);
  compare(summary.getRange('B6').values[0][0],catchTotal,`${year} total catch`);
  compare(summary.getRange('B8').values[0][0],selected.length-available.length,`${year} missing regions`);
  const actual=summary.getRange(`A11:J${selected.length+10}`).values;
  let cumulative=0;
  expected.forEach((row,i)=>{
    compare(actual[i][0],row.unit_id,`${year} row ${i} ID`);
    compare(actual[i][3],row.total_catch_tonnes,`${year} ${row.unit_id} catch`);
    compare(actual[i][4],row.ppr_species,`${year} ${row.unit_id} PPR`);
    compare(actual[i][6],i+1,`${year} ${row.unit_id} rank`);
    cumulative+=row.ppr_species;
    if(total>0){compare(actual[i][5],row.ppr_species/total,`${year} share`);compare(actual[i][7],cumulative/total,`${year} cumulative`);}
  });
  for(let i=expected.length;i<actual.length;i++)assert.equal(actual[i][4],'',`${year} unavailable row must stay blank`);
  assert.deepEqual(new Set(actual.map(r=>r[0])),selectedIds,`${year} membership`);
  verification.push({year,total_ppr:total,total_catch_tonnes:catchTotal,available_regions:available.length,selected_regions:selected.length});
  console.log(`Verified year ${year}: ${available.length}/${selected.length} regions with catch data`);
}
summary.getRange('B3').values=[[years.at(-1)+100]];
assert.equal(summary.getRange('B5').values[0][0],'');
assert.equal(summary.getRange('A11').values[0][0],'');
summary.getRange('B3').values=[[years.at(-1)]];
for(const [name,expected]of originalSnapshots) {
  const range=workbook.worksheets.getItem(name).getUsedRange();
  assert.equal(hash(JSON.stringify({values:range.values,formulas:range.formulas})),expected,`Original sheet altered: ${name}`);
}
console.log('Original sheet values/formulas preserved');
await fs.mkdir(previewDir,{recursive:true});
for(const [sheetName,range]of [['Global Estimation','A1:J22'],['Annual Regional PPR','A1:I14'],['Selected Regions','A1:E14'],
  ['Selected Year','A1:K14'],['Available Years','A1:A15'],['Spatial Coverage','A1:B18']]) {
  const image=await workbook.render({sheetName,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(previewDir,`${sheetName.replaceAll(' ','_')}.png`),new Uint8Array(await image.arrayBuffer()));
}
for(const [sheetName,range,label]of [['Annual Regional PPR','J1:Q14','Annual_PPR_and_Jensen'],['Spatial Coverage','A16:B32','Spatial_metrics']]) {
  const image=await workbook.render({sheetName,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(previewDir,`${label}.png`),new Uint8Array(await image.arrayBuffer()));
}
console.log((await workbook.inspect({kind:'table',range:"'Global Estimation'!A10:J15",include:'values,formulas',tableMaxRows:6,tableMaxCols:10,maxChars:2500})).ndjson);
const errors=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:25},maxChars:2500,summary:'Formula errors'});
console.log(errors.ndjson);
// Also inspect actual values: a compact text search alone is not a guarantee.
const spreadsheetError=/^#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/;
for(const name of [...originalNames,'Global Estimation','Annual Regional PPR','Selected Regions','Selected Year','Available Years','Spatial Coverage']) {
  for(const row of workbook.worksheets.getItem(name).getUsedRange().values)
    for(const value of row)if(typeof value==='string'&&spreadsheetError.test(value))throw new Error(`Formula error in ${name}: ${value}`);
}
await fs.mkdir(outputDir,{recursive:true});
const destination=path.join(outputDir,'PPR_global_summary.xlsx');
const exported=await SpreadsheetFile.exportXlsx(workbook);
await exported.save(destination);
assert.equal(hash(await fs.readFile(source)),sourceHash,'Source workbook changed');
const record={source_workbook_sha256:sourceHash,output_workbook_sha256:hash(await fs.readFile(destination)),
  original_sheets_preserved:originalNames,new_sheets:['Global Estimation','Annual Regional PPR','Selected Regions','Selected Year','Available Years','Spatial Coverage'],
  selected_count:selected.length,annual_rows:annual.length,years,year_selection_checks:verification,invalid_year_check:true};
await fs.writeFile(path.join(outputDir,'workbook_validation.json'),JSON.stringify(record,null,2));
console.log(`Saved ${destination}`);
