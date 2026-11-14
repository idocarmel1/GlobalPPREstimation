import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from 'file:///C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root=process.cwd();
const model=path.join(root,'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991');
const validation=path.join(model,'model_validation');
const run=path.join(validation,'work/2026-11-14_200000_ices_full_review');
const audit=JSON.parse(await fs.readFile(path.join(validation,'evidence/mapping/mapping_decisions.json'),'utf8'));
const isFinal=process.argv.includes('--final');
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load(isFinal?path.join(validation,'taxon_mapping.xlsx'):path.join(run,'inputs/taxon_mapping_import.xlsx')));
if(isFinal){
  const splitRow=8+audit.rows.findIndex(r=>r.taxon==='Marine fishes not identified');
  for(const [sheetName,range,name] of [['SPPR diagnostics','A1:J11','diagnostics_final'],['Taxon mapping',`A${splitRow}:G${splitRow+1}`,'mapping_largest_split_final'],['Sources','A12:D17','mapping_sources_2_final']]){
    const blob=await workbook.render({sheetName,range,scale:1,format:'png'});
    await fs.writeFile(path.join(run,'qa',name+'.png'),new Uint8Array(await blob.arrayBuffer()));
  }
  const check=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final preserved-package error scan'});
  await fs.writeFile(path.join(run,'qa/final_mapping_error_scan.ndjson'),check.ndjson);
  console.log(JSON.stringify({finalRender:true,largestSplitRow:splitRow}));
  process.exit(0);
}
if(process.argv.includes('--before')){
  for(const [sheetName,range,name] of [['Taxon mapping','A1:G13','appendix_before'],['Sources','A1:D9','sources_before'],['SPPR diagnostics','A1:J11','diagnostics_before']]){
    const blob=await workbook.render({sheetName,range,scale:1,format:'png'});
    await fs.writeFile(path.join(run,'qa',name+'.png'),new Uint8Array(await blob.arrayBuffer()));
  }
  console.log((await workbook.inspect({kind:'sheet,table',maxChars:2500,tableMaxRows:2,tableMaxCols:4})).ndjson);
  process.exit(0);
}
const sheet=workbook.worksheets.getItem('Taxon mapping');
const sources=workbook.worksheets.getItem('Sources');
sheet.getRange('A1').values=[['North Sea LME_022 proposed taxon mapping']];
sheet.getRange('A2').values=[['2019 total catch (landings plus discards). ICES_WGSAM2015_North_Sea_1991. All 384 exact catch labels, including zero-catch labels.']];
sheet.getRange('A3').values=[['Independent simple-chain PPR = catch × saved classic coefficient / 9 once (tonnes C). Sorted by unrounded PPR descending, then taxon name.']];
sheet.getRange('A4').values=[['72 labels lack a saved TL/coefficient; all have zero recorded 2019 catch and zero annual PPR. ? means unavailable. No annual contribution is unknown.']];
sheet.getRange('A5').values=[['PROPOSED FOR RESEARCHER REVIEW. No ICES mapping has been adopted into the regional workbook. Total catch: 2,717,260.698205 t. Simple-chain PPR: 188,909,420.829195 t C.']];
sheet.getRange('A5:G5').format.fill='#FFF2CC';
sheet.getRange('D6').values=[['86 Very low proposals account for 12% of catch and 4.2% of simple-chain PPR. No label remains without a proposed placement.']];
sheet.getRange('D6:G6').format.wrapText=true;
const pct=w=>w===0?'0%':w===1?'100%':`${Number((100*w).toPrecision(4))}%`;
const rows=audit.rows.map(r=>[r.taxon,r.tl??'?',r.catch_tonnes??'?',r.simple_chain_ppr_tC??'?',r.groups.map(g=>`${g.group_name} (${pct(g.weight)})`).join('; '),r.overall_confidence,r.reason]);
sheet.getRange('A8:G391').values=rows;
for(const [c,width] of Object.entries({A:33,B:8,C:20,D:25,E:62,F:15,G:86}))sheet.getRange(`${c}1:${c}391`).format.columnWidth=width;
sheet.getRange('A8:G391').format.wrapText=true;
sheet.getRange('A8:G391').format.verticalAlignment='center';
for(let i=0;i<rows.length;i++){
  const row=rows[i];
  const lines=Math.max(Math.ceil(String(row[0]).length/31),Math.ceil(String(row[4]).length/58)+1,Math.ceil(String(row[6]).length/82)+1);
  sheet.getRange(`A${i+8}:G${i+8}`).format.rowHeight=Math.max(50,Math.min(390,lines*15+10));
}
sheet.getRange('A1:G1').format.rowHeight=30;
sheet.getRange('A2:G5').format.rowHeight=31;
sheet.getRange('A6:G6').format.rowHeight=33;
sheet.getRange('B8:B391').setNumberFormat('0.00');
sheet.getRange('C8:D391').setNumberFormat('#,##0.000000');
sheet.freezePanes.freezeRows(7);sheet.freezePanes.freezeColumns(1);
// Keep the original two-sheet structure, source layout and diagnostic sheet.
for(const r of ['A14:D14','A15:D15'])sources.getRange(r).unmerge();
sources.getRange('A5:D40').clear({applyTo:'contents'});
sources.getRange('A1').values=[['Sources and assumptions for the proposed mapping']];
sources.getRange('A2').values=[['Membership uses the focal group inventory, the explicitly documented 2007 predecessor, provider reporting scope and disclosed analogues. Allocation is separately assessed. Regional adoption is pending.']];
sources.getRange('A2:D2').format.rowHeight=42;
sources.getRange('A4:D4').values=[['Source / material','What it supports and where','Link','Reviewed']];
const sourceRows=audit.sources.map(s=>[`${s.id}: ${s.title}`,`${s.locator}. ${s.supports}`,'Open source','14/11/2026']);
sources.getRange(`A5:D${4+sourceRows.length}`).values=sourceRows;
for(let i=0;i<audit.sources.length;i++){
  const s=audit.sources[i],target=s.path??s.url;
  if(s.path){await fs.access(path.resolve(validation,s.path));}
  sources.getRange(`C${5+i}`).formulas=[[`=HYPERLINK("${target.replaceAll('"','""')}","Open source")`]];
  const lines=Math.max(Math.ceil(sourceRows[i][0].length/49),Math.ceil(sourceRows[i][1].length/92));
  sources.getRange(`A${5+i}:D${5+i}`).format.rowHeight=Math.max(66,lines*15+15);
}
sources.getRange(`A5:D${4+sourceRows.length}`).format.wrapText=true;
sources.getRange(`A5:D${4+sourceRows.length}`).format.verticalAlignment='center';
sources.getRange(`A5:D${4+sourceRows.length}`).format.font={name:'Arial',size:11,color:'#202020'};
sources.getRange(`C5:C${4+sourceRows.length}`).format.font={name:'Arial',size:11,color:'#0563C1',underline:'single'};
for(const [c,width] of Object.entries({A:57,B:102,C:18,D:17}))sources.getRange(`${c}1:${c}40`).format.columnWidth=width;
sources.freezePanes.freezeRows(4);
workbook.recalculate();
const check=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final error scan'});
await fs.writeFile(path.join(run,'qa/mapping_error_scan.ndjson'),check.ndjson);
await (await SpreadsheetFile.exportXlsx(workbook)).save(path.join(run,'outputs/edited_mapping_artifact.xlsx'));
for(const [sheetName,range,name] of [['Taxon mapping','A1:G12','mapping_top'],['Taxon mapping','A60:G66','mapping_mid'],['Taxon mapping','A384:G391','mapping_bottom'],['Sources','A1:D11','mapping_sources_1'],['Sources',`A12:D${4+sourceRows.length}`,'mapping_sources_2']]){
  const blob=await workbook.render({sheetName,range,scale:1,format:'png'});
  await fs.writeFile(path.join(run,'qa',name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({rows:rows.length,sources:sourceRows.length,output:'edited_mapping_artifact.xlsx'}));
